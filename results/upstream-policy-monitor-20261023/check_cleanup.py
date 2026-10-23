"""Read-only structural comparison; no mathematical or deployed-site replay."""
from pathlib import Path
import collections, datetime, hashlib, json, re, subprocess, sys

BASE = 'faa9df2ec6406e4eacc135f677cf3711315d0e41'
HEAD = '554757eca1aebecdd1d21f3452d3c71ffa601b19'
repo = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2]).resolve()

def git(*args):
    return subprocess.run(['git', '-C', str(repo), *args], check=True,
                          capture_output=True, text=True, encoding='utf-8',
                          timeout=30).stdout

def require(value, message):
    if not value:
        raise RuntimeError(message)

names = git('diff', '--name-only', BASE, HEAD).splitlines()
records = [p for p in names if p.endswith('/record.json')]
instances = [p for p in names if p.endswith('/instance.rec')]
require(len(records) == len(instances) == 82, 'Unexpected target count')
checks = []
render_removals = []
for path in records:
    old, new = [json.loads(git('show', rev + ':' + path)) for rev in [BASE, HEAD]]
    ca, cb = old['render']['camera'], new['render']['camera']
    require('yaw' in ca and 'pitch' in ca, path)
    require('orientation' in cb and 'yaw' not in cb and 'pitch' not in cb, path)
    del ca['yaw'], ca['pitch']
    if 'orientation' in ca:
        require(ca['orientation'] == cb['orientation'], 'Existing orientation changed: ' + path)
    else:
        del cb['orientation']
    if 'divisorProgram' in old['render'] and 'divisorProgram' not in new['render']:
        require(path == 'data/quadric-contact-broken/record.json', 'Unexpected removed renderer: ' + path)
        program = old['render'].pop('divisorProgram')
        render_removals.append({'path': path, 'field': 'render.divisorProgram',
                                'description': program['description'], 'source': program['source']})
    require(old == new, 'Change outside camera representation: ' + path)
    checks.append({'path': path, 'unchanged_except_camera_representation_and_listed_render_removals': True})
for path in instances:
    patch = git('diff', '--no-ext-diff', '--unified=0', BASE, HEAD, '--', path)
    removed = [s[1:] for s in patch.splitlines() if s.startswith('-') and not s.startswith('---')]
    added = [s[1:] for s in patch.splitlines() if s.startswith('+') and not s.startswith('+++')]
    require(len(removed) == 2 and len(added) in {0, 1}, 'Unexpected edit: ' + path)
    require(all(re.fullmatch(r'    (yaw|pitch): [-+0-9.eE]+', s) for s in removed), path)
    require(not added or re.fullmatch(r'    orientation: \[[-+0-9.eE, ]+\]', added[0]), path)
    checks.append({'path': path, 'only_two_camera_scalars_removed_and_optional_orientation_added': True})
solutions = [p for p in names if p.endswith('/solution.md')]
for path in solutions:
    old, new = [git('show', rev + ':' + path) for rev in [BASE, HEAD]]
    folder = path.rsplit('/', 1)[0] + '/'
    require(old.replace('](' + folder + 'witness.json)', '](witness.json)').replace(
        '](' + folder + 'Solution.lean)', '](Solution.lean)') == new,
        'Change outside two source links: ' + path)
proof_changes = [p for p in names if p.endswith('.lean') or p.startswith('formal/') or
                 p.rsplit('/', 1)[-1] in {'acceptance.json', 'proof.json', 'provenance.json', 'why.md', 'witness.json'}]
require(not proof_changes, 'Protected proof/context changed: ' + repr(proof_changes))
result = {'status': 'PASS', 'checked_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'base': BASE, 'head': HEAD, 'complete_git_diff_files': len(names),
          'file_groups': dict(collections.Counter(p.split('/')[0] for p in names)),
          'target_record_checks': checks, 'proof_or_acceptance_changes': proof_changes,
          'render_removals': render_removals,
          'solution_explanations_only_two_link_targets_changed': solutions,
          'python_version': sys.version, 'git_version': git('--version').strip(),
          'command_timeout_seconds': 30, 'checker_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'limits': ['Structural data comparison only; camera rotations not independently compared',
                     'No Lean build, mathematical replay, backend tests, or deployed-service verification',
                     'GitHub compare response capped at 300 files; complete local Git diff used instead']}
out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps({k: v for k, v in result.items() if k != 'target_record_checks'}, indent=2))
