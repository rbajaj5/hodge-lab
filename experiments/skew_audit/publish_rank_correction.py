"""One authorized edit of post25, guarded by its audited prior body hash.

Run only after pushing the corresponding ledger audit. No retries or new posts.
"""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/one-reflection-skew-rank-correction'


def sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def main():
    audit_commit = sys.argv[1]
    audit = json.loads((OUT / 'prepublication-audit.json').read_text(encoding='utf-8'))
    draft = (OUT / 'comment-draft.md').read_text(encoding='utf-8')
    if sha(draft) != audit['draft_body_sha256']:
        raise ValueError('Draft changed since ledger audit')
    log = {'status': 'NOT_EDITED', 'ledger_audit_commit': audit_commit,
           'url': audit['url'], 'operations': [], 'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    def command(label, cmd, data=None):
        try:
            p = subprocess.run(cmd, input=data, cwd=ROOT, capture_output=True,
                               text=True, encoding='utf-8', timeout=30)
        except subprocess.TimeoutExpired as e:
            log['operations'].append({'operation': label, 'status': 'TIMEOUT', 'error': str(e)})
            raise RuntimeError('Timed out: ' + label) from e
        if p.returncode:
            log['operations'].append({'operation': label, 'exit_code': p.returncode,
                                      'stderr': p.stderr, 'stdout': p.stdout})
            raise RuntimeError('Failed operation: ' + label + ': ' + p.stderr)
        log['operations'].append({'operation': label, 'exit_code': 0})
        return p.stdout
    def graphql(label, query, variables):
        obj = json.loads(command(label, ['gh', 'api', 'graphql', '--input', '-'],
                                 json.dumps({'query': query, 'variables': variables})))
        if obj.get('errors'):
            log['operations'][-1]['graphql_errors'] = obj['errors']
            raise RuntimeError('GraphQL error: ' + json.dumps(obj['errors']))
        return obj['data']
    query = 'query($id:ID!){node(id:$id){... on DiscussionComment{id url body updatedAt author{login}}}}'
    try:
        # Both local history and the remote branch must contain the ledger audit.
        command('audit commit exists locally', ['git', 'merge-base', '--is-ancestor', audit_commit, 'HEAD'])
        remote = command('audit published on Hodge Lab main', ['git', 'ls-remote', 'origin', 'refs/heads/main']).split()[0]
        if remote != audit_commit:
            raise RuntimeError('Remote main changed; reconcile before editing')
        author = command('authenticated contributor', ['gh', 'api', 'user', '--jq', '.login']).strip()
        if author != audit['author']:
            raise RuntimeError('Authenticated account differs from comment author')
        before = graphql('pre-edit body guard', query, {'id': audit['comment_id']})['node']
        if before is None or before['author']['login'] != author or sha(before['body']) != audit['before_body_sha256']:
            raise RuntimeError('Comment changed since audit; no edit attempted')
        mutation = 'mutation($id:ID!,$body:String!){updateDiscussionComment(input:{commentId:$id,body:$body}){comment{id url body updatedAt}}}'
        result = graphql('authorized correction', mutation, {'id': audit['comment_id'], 'body': draft})
        log['status'] = 'EDIT_RETURNED_NOT_YET_VERIFIED'
        (OUT / 'mutation-response.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
        after = graphql('independent readback', query, {'id': audit['comment_id']})['node']
        (OUT / 'comment-after.json').write_text(json.dumps(after, indent=2) + '\n', encoding='utf-8', newline='\n')
        if after['body'] != draft or after['url'] != audit['url']:
            raise RuntimeError('Readback differs from audited draft or permalink')
        log.update(status='PUBLISHED_AND_VERIFIED', updated_at=after['updatedAt'],
                   before_body_sha256=audit['before_body_sha256'],
                   after_body_sha256=sha(after['body']), author=author)
    except Exception as error:
        log['error'] = str(error)
        raise
    finally:
        log['completed_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        (OUT / 'publication-outcome.json').write_text(json.dumps(log, indent=2) + '\n', encoding='utf-8', newline='\n')
        print(json.dumps(log, indent=2))


if __name__ == '__main__':
    main()
