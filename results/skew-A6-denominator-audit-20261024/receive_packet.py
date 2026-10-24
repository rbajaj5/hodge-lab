"""Verify and safely extract a received archive; never executes received code."""
import argparse, datetime, hashlib, json, pathlib, zipfile
p=argparse.ArgumentParser(); p.add_argument('archive',type=pathlib.Path)
p.add_argument('--sha256',required=True);p.add_argument('--manifest-sha256',required=True)
p.add_argument('--destination',type=pathlib.Path,required=True)
p.add_argument('--manifest-prefix',choices=['payload/',''],required=True)
args=p.parse_args();raw=args.archive.read_bytes()
assert hashlib.sha256(raw).hexdigest()==args.sha256
dest=args.destination.resolve();assert not dest.exists(),'fresh destination required'
with zipfile.ZipFile(args.archive) as z:
 infos=z.infolist();assert len(infos)<=500 and sum(x.file_size for x in infos)<=150_000_000
 assert len({i.filename for i in infos})==len(infos)
 for info in infos:
  q=(dest/info.filename).resolve();assert q.is_relative_to(dest),info.filename
  assert (info.external_attr>>16)&0o170000!=0o120000,'symlink rejected'
 dest.mkdir(parents=True)
 for info in infos:
  q=(dest/info.filename).resolve()
  if info.is_dir():q.mkdir(parents=True,exist_ok=True)
  else:q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(z.read(info))
manifests=list(dest.rglob('MANIFEST.sha256'));assert len(manifests)==1
manifest=manifests[0];assert hashlib.sha256(manifest.read_bytes()).hexdigest()==args.manifest_sha256
root=manifest.parent/'payload';assert root.is_dir()
entries={}
for line in manifest.read_text(encoding='utf-8').splitlines():
 if not line.strip():continue
 h,name=line.split('  ',1);name=name.removeprefix('*')
 if args.manifest_prefix:assert name.startswith(args.manifest_prefix);name=name.removeprefix(args.manifest_prefix)
 f=(root/name).resolve();assert f.is_relative_to(root.resolve()) and f.is_file(),name
 assert hashlib.sha256(f.read_bytes()).hexdigest()==h,name
 assert name not in entries,name
 entries[name]=h
assert set(entries)=={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()},'manifest coverage'
record={'status':'PASS archive hash, safe extraction and complete manifest; not mathematical replay',
 'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'archive_sha256':args.sha256,
 'archive_bytes':len(raw),'manifest_sha256':args.manifest_sha256,'manifest_prefix':args.manifest_prefix,
 'payload_root':str(root),'metadata_root':str(manifest.parent),'files':entries,'file_count':len(entries)}
(dest.parent/'packet-receipt.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in record.items() if k!='files'},indent=2))
