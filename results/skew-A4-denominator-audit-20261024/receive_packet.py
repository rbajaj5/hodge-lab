"""Bounded artifact verification only; does not execute received code."""
import argparse, hashlib, json, pathlib, zipfile, datetime
p=argparse.ArgumentParser()
p.add_argument('archive',type=pathlib.Path)
p.add_argument('--sha256',required=True)
p.add_argument('--destination',type=pathlib.Path,required=True)
p.add_argument('--verify-existing',action='store_true')
args=p.parse_args()
raw=args.archive.read_bytes()
sha=hashlib.sha256(raw).hexdigest()
assert sha==args.sha256,(sha,args.sha256)
dest=args.destination.resolve()
assert not dest.exists() or args.verify_existing,'fresh extraction destination required'
with zipfile.ZipFile(args.archive) as z:
    infos=z.infolist()
    assert len(infos)<=500 and sum(x.file_size for x in infos)<=120_000_000
    assert len({i.filename for i in infos})==len(infos)
    for info in infos:
        q=(dest/info.filename).resolve()
        assert q.is_relative_to(dest),info.filename
        assert (info.external_attr>>16)&0o170000 != 0o120000,'symlink rejected'
    dest.mkdir(parents=True,exist_ok=args.verify_existing)
    for info in infos:
        q=(dest/info.filename).resolve()
        if info.is_dir():q.mkdir(parents=True,exist_ok=True)
        else:
            q.parent.mkdir(parents=True,exist_ok=True)
            content=z.read(info)
            if q.exists():assert args.verify_existing and q.read_bytes()==content,info.filename
            else:q.write_bytes(content)
manifests=list(dest.rglob('MANIFEST.sha256'))
assert len(manifests)==1,[str(x) for x in manifests]
manifest=manifests[0];root=manifest.parent/'payload'
assert root.is_dir(),'this packet explicitly contains payload/'
entries={}
for line in manifest.read_text(encoding='utf-8').splitlines():
    if not line.strip():continue
    h,name=line.split('  ',1)
    name=name.removeprefix('*')
    assert name.startswith('payload/'), 'A4 manifest explicitly prefixes payload/'
    name=name.removeprefix('payload/')
    f=(root/name).resolve()
    assert f.is_relative_to(root.resolve()) and f.is_file(),name
    assert hashlib.sha256(f.read_bytes()).hexdigest()==h,name
    assert name not in entries,name
    entries[name]=h
receipt={'status':'PASS archive SHA256, safe extraction and manifest bytes; not mathematical replay',
 'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'archive_sha256':sha,'archive_bytes':len(raw),'manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),
 'payload_root':str(root),'metadata_root':str(manifest.parent),'files':entries,'file_count':len(entries),
 'integration_note':'Original payload bytes verified at the explicitly declared archive layout. No mathematical replay.'}
(dest.parent/'packet-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='files'},indent=2))
