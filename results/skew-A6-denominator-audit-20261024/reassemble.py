"""Verify downloaded binary slices and reconstruct the exact original ZIP."""
from pathlib import Path, PurePosixPath
import argparse, datetime, hashlib, json, re
p=argparse.ArgumentParser();p.add_argument('--archive-sha256',required=True)
p.add_argument('--archive-bytes',type=int,required=True);p.add_argument('--review-sha256',required=True)
p.add_argument('--parts-prefix',choices=['parts/',''],required=True)
args=p.parse_args();base=Path(__file__).resolve().parent
files={x['name']:Path(x['path']) for x in json.loads((base/'downloads.json').read_text(encoding='utf-8'))}
pins={}
for line in files['PARTS.sha256'].read_text(encoding='utf-8').splitlines():
 if not line.strip():continue
 digest,name=line.split();assert re.fullmatch('[0-9a-f]{64}',digest)
 if args.parts_prefix:assert name.startswith(args.parts_prefix);name=name.removeprefix(args.parts_prefix)
 assert re.fullmatch(r'A6-denominator\.zip\.part\d{3}',name),name
 assert name not in pins; pins[name]=digest
names=['A6-denominator.zip.part'+str(i).zfill(3) for i in range(1,len(pins)+1)]
assert set(names)==set(pins)
chunks=[];records=[]
for name in names:
 raw=files[name].read_bytes();h=hashlib.sha256(raw).hexdigest()
 assert h==pins[name] and len(raw)<=2_000_000,name
 records.append({'file':name,'sha256':h,'bytes':len(raw)});chunks.append(raw)
raw=b''.join(chunks);h=hashlib.sha256(raw).hexdigest()
assert len(raw)==args.archive_bytes and h==args.archive_sha256
review_hash=hashlib.sha256(files['A6-review.zip'].read_bytes()).hexdigest()
assert review_hash==args.review_sha256
(base/'A6-denominator-reassembled.zip').write_bytes(raw)
record={'status':'PASS: original ZIP reconstructed from all verified slices',
 'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'archive_sha256':h,'archive_bytes':len(raw),
 'parts':records,'parts_prefix':args.parts_prefix,'review_sha256':review_hash,'download_failures':0,
 'download_repair':None,
 'mathematical_replay':False,'manifest_note':'Explicit paths checked before basename mapping; no manifest-layout assumption inherited from previous batch.'}
(base/'transfer-receipt.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in record.items() if k!='parts'},indent=2))
