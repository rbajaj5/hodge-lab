from pathlib import Path
import datetime, hashlib, json, subprocess, time

OUT = Path(__file__).resolve().parent
START = time.monotonic()
FIELDS = 'id url createdAt updatedAt author {login ... on User {name}} body'
INFO = 'pageInfo {hasNextPage endCursor} totalCount'

def api(query, variables):
    if time.monotonic() - START > 120:
        raise TimeoutError('120-second collection budget')
    p = subprocess.run(['gh','api','graphql','--input','-'],
        input=json.dumps({'query':query,'variables':variables}), capture_output=True,
        text=True, encoding='utf-8', timeout=45)
    if p.returncode:
        raise RuntimeError(p.stderr[:1000])
    data = json.loads(p.stdout)
    if data.get('errors'):
        raise RuntimeError(str(data['errors']))
    return data['data']

q = 'query($after:String){repository(owner:"hodge-computer",name:"sextics"){discussion(number:127){id number title url body updatedAt locked answer{id url} comments(first:100,after:$after){'+INFO+' nodes{'+FIELDS+' replies(first:100){'+INFO+' nodes{'+FIELDS+'}}}}}}}'
comments=[]
after=None
while True:
    d=api(q,{'after':after})['repository']['discussion']
    page=d['comments']; comments+=page['nodes']
    if not page['pageInfo']['hasNextPage']: break
    after=page['pageInfo']['endCursor']
if len(comments)!=page['totalCount']: raise ValueError('comment count mismatch')
for c in comments:
    r=c['replies']; nodes=r['nodes']; pi=r['pageInfo']
    while pi['hasNextPage']:
        r=api('query($id:ID!,$after:String){node(id:$id){... on DiscussionComment{replies(first:100,after:$after){'+INFO+' nodes{'+FIELDS+'}}}}}',{'id':c['id'],'after':pi['endCursor']})['node']['replies']
        nodes+=r['nodes']; pi=r['pageInfo']
    if len(nodes)!=r['totalCount']: raise ValueError('reply count mismatch')
    c['replies']={'nodes':nodes,'totalCount':len(nodes),'all_pages_fetched':True}
d['comments']={'nodes':comments,'totalCount':len(comments),'all_pages_fetched':True}
d['retrieved_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
(OUT/'discussion-127.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=[d['url'],d['body']]; summaries=[]
for c in comments:
    for x in [c]+c['replies']['nodes']:
        lines.extend([x['url'],json.dumps({k:x[k] for k in ('id','author','createdAt','updatedAt')},ensure_ascii=False),x['body']])
        s={k:x[k] for k in ('id','url','author','createdAt','updatedAt')}
        s['body_sha256']=hashlib.sha256(x['body'].encode()).hexdigest(); summaries.append(s)
        if x['url'].endswith('19129985'):
            (OUT/'comment-19129985.json').write_text(json.dumps({**x,'body_sha256':s['body_sha256']},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            print(json.dumps({**s,'body':x['body']},ensure_ascii=False))
(OUT/'discussion-127.md').write_text('\n\n'.join(lines)+'\n',encoding='utf-8')
(OUT/'manifest.json').write_text(json.dumps({'retrieved_utc':d['retrieved_utc'],'per_request_seconds':45,'total_budget_seconds':120,'comments':len(comments),'replies':sum(c['replies']['totalCount'] for c in comments),'all_pages_fetched':True,'records':summaries},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'comments':len(comments),'replies':sum(c['replies']['totalCount'] for c in comments),'seconds':time.monotonic()-START,'out':str(OUT)}))
