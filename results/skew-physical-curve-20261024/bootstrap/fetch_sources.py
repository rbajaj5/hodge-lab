from pathlib import Path
import datetime,hashlib,json,time,urllib.request
out=Path('results/skew-physical-curve-20261024/inputs/upstream');out.mkdir(parents=True,exist_ok=True)
sha='e96be434bd55d6013d7a5854732cb317ca0e43e7';records=[]
for name in ['data/one-reflection-skew/instance.rec','AGENTS.md']:
 url='https://raw.githubusercontent.com/hodge-computer/sextics/'+sha+'/'+name
 start=time.monotonic();p=out/name;p.parent.mkdir(parents=True,exist_ok=True)
 with urllib.request.urlopen(url,timeout=45) as r:data=r.read()
 p.write_bytes(data);records.append({'url':url,'path':str(p),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'elapsed_seconds':time.monotonic()-start})
(out/'fetch.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commit':sha,'files':records},indent=2)+'\n',encoding='utf-8');print(json.dumps(records))
