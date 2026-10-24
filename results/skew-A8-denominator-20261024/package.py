"""Create the changed-file A8 delivery; byte binding only, no mathematics.

Usage from any directory: python package.py FRESH_DELIVERY_DIRECTORY
"""
from pathlib import Path
import datetime, hashlib, json, shutil, sys, time, zipfile

start=time.monotonic(); batch=Path(__file__).resolve().parent
root=batch.parents[1]; dest=Path(sys.argv[1]).resolve()
dest.mkdir(parents=True,exist_ok=False); payload=dest/'payload'; payload.mkdir()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dumps(v): return json.dumps(v,indent=2,ensure_ascii=False)+'\n'
def write(p,s): p.write_text(s,encoding='utf-8')
files=[root/'notes/skew-A8-denominator-20261024.md']
files+=sorted(p for p in batch.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
if any(p.is_symlink() for p in files): raise RuntimeError('Unexpected payload symlink')
text_count=0; entries={}
for p in files:
    rel=p.relative_to(root); data=p.read_bytes()
    if p.suffix not in ['.png','.bin']:
        data.decode('utf-8'); text_count+=1
    target=payload/rel;target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(data)
    if target.read_bytes()!=data:raise RuntimeError('Payload copy mismatch')
    entries['payload/'+rel.as_posix()]={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
raw='payload/results/skew-A8-denominator-20261024/lead/matrix-01/result/augmented-matrix.u16.bin'
if entries[raw] != {'bytes':70932000,'sha256':'760a3e5cc7c7e0e941a482f2f554cf372f5145371ebf48ff5498300af20da9b3'}:
    raise RuntimeError('Pinned matrix changed during packaging')
manifest=''.join(f"{v['sha256']}  {k}\n" for k,v in sorted(entries.items()))
write(dest/'MANIFEST.sha256',manifest)
write(dest/'ADDED-FILES.txt',''.join(k.removeprefix('payload/')+'\n' for k in sorted(entries)))
handoff='A8 full-current handoff — mathematics frozen; integration only\n24 October2026, America/New_York. Math close:14:29:12EDT /18:29:12UTC.\nIntegration deadline:14:44:12EDT /18:44:12UTC.\n\nIntegration parent:c6e2e54f957eeeaa97cabc7a26df6d81ffd759ee\nCached execution checkout:fc4f38a338b47addf62d1bf699783302285378fe\nUpstream coordinator pin:27f4bb9ad8757e5841f884d9d30124a3c97a847d\nCurrent-parent AGENTS,board and connection read via connector; Git blobs and\nsource bytes match. No fresh full parent or combined Git tree is claimed.\nConnectionSHA256:a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d\n\nOWNED ADDITIONS ONLY:notes/skew-A8-denominator-20261024.md and\nresults/skew-A8-denominator-20261024/. No shared-file edits,Lean,commit,push\nor upstream actions. Coordinator owns integration and Hodge Lab publication.\n\nRESULT:finite rational-CONSTANT family(B+B/A+...+B/A^8)^6 excluded,where\nB spans r^m v^n t^k,-10<=m<=2,0<=n,k<=2. Original6318 parameters;\nonly P8 tangent:top294 plus ALL5616 lower parameters free=5910.\nBothrows,allphysical derivatives,fullNt,positive r^-4 Mb e0/12 retained.\nImported det(Ra-8I)=200/3,tau8=-14r^7+27r; lower pole coupling retained.\n\nFixed prime65521,seed2026102508,3000admissible points; full6000x5911 matrix.\nFirst5911rows decisive. Coordinator independently reports determinant30337\nmod65521,34,939,921 entries at2956points,26.781s,3controls,exactFLINT0.9.0.\nPro did NOT execute a determinant or install a backend.\nPro author:34.721790s,exit0. Separate AI reconstruction:32.314968s,exit0;\nall35,466,000entries,3000domains,basis/rejections match;25controls detected.\nNo mathematical failures,timeouts or repairs. One orchestration call aborted\nbefore dispatch; no code ran,and its operations were reissued.\nCoordinator algebra:7checks+3controls,2.235s process/0.219s algebra,imported.\nExact6318x5910 injectionSHA32dcdb1291e8ee2cc2703978f95a2b62d8e9a6d5295b8db48c6c37e5a10040a2.\n\nMATRIX:headerless row-major little-endian uint16(<u2),shape(6000,5911),\n70,932,000bytes. Final column positive source.\nSHA256:760a3e5cc7c7e0e941a482f2f554cf372f5145371ebf48ff5498300af20da9b3\ninputs.jsonSHA256:1e635a3e0c6e5be593ce954e638bd37f2453b882110d7da41ce268709772d9c4\nExactdomains,basislabels and sourcepins included. No rejected samples.\nCoordinator frozenNPYSHA256:1c41301ad2a113d530bbd3b13c4ee004ac22fb55219b8bab99ae9850d46ac9e6\nOptional binder checks these exact matrix hashes and every decisive entry.\nIt is IO-only and was NOT executed in Pro; coordinator NPY is not present.\n\nREMAINING:coordinator IO-only decisive-entry/domain/basis matching,then\nshared integration and normal Hodge Lab push. No extra mathematical replay,\nreview or setup needed. No primitive,source exactness,general rational-current\nobstruction,cohomology theorem,global clearing,certificate or solve claimed.\n\nARCHIVE:payload/<repository-relative-path>,MANIFEST.sha256,HANDOFF.txt.\nFull root manifest paths start payload/; verify from unpacked root,then\napply payload contents only. ADDED-FILES.txt is an inventory,not a Git tree.\nReview ZIP retains all non-matrix payload bytes with its own root manifest.\nOriginal full manifest/handoff under original-delivery/; omitted-artifacts.json\nidentifies only the bulky matrix. Full ZIP and slices retain that matrix.\nPARTS.sha256 paths start parts/. Concatenate part001 onward numerically as\nraw bytes without separators. Everypart<=2,000,000bytes. DELIVERY.json and\nSHA256SUMS.txt contain exact archive,manifest,handoff and slice hashes/sizes.\nNo repository/cache/submodule dump. Original bytes immutable after creation.\n\nRUN.md supplies fresh-directory <=60s -O reproduction commands. No old proof\nor receipt rewritten. Reproducible scientific PNG/SVG and generator/input/output\nhashes included; PNG inspected. Credit fqlx,benediamond,hodge.computer framework.\n'
write(dest/'HANDOFF.txt',handoff)
archive=dest/'A8-denominator.zip'
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for name in sorted(entries):z.write(dest/name,name)
    z.write(dest/'MANIFEST.sha256','MANIFEST.sha256');z.write(dest/'HANDOFF.txt','HANDOFF.txt')
with zipfile.ZipFile(archive) as z:
    if z.testzip() is not None:raise RuntimeError('Full ZIP CRC failure')
    if set(z.namelist())!=set(entries)|{'MANIFEST.sha256','HANDOFF.txt'}:raise RuntimeError('Full ZIP member inventory mismatch')
    for name,value in entries.items():
        if hashlib.sha256(z.read(name)).hexdigest()!=value['sha256']:raise RuntimeError('Full ZIP member binding failed')
omitted={'omitted_only_from_review_zip':[{'archive_path':raw,**entries[raw],'format':'headerless C-order <u2','shape':[6000,5911]}],
         'original_zip_retains_every_payload_byte':True,'new_mathematics':False}
write(dest/'omitted-artifacts.json',dumps(omitted))
review_members={k:(dest/k).read_bytes() for k in entries if k!=raw}
review_members['original-delivery/MANIFEST.sha256']=manifest.encode('utf-8')
review_members['original-delivery/HANDOFF.txt']=handoff.encode('utf-8')
review_members['omitted-artifacts.json']=(dest/'omitted-artifacts.json').read_bytes()
review_handoff='''A8 REVIEW ZIP:all non-matrix original payload bytes unchanged.
Only the bulky raw matrix is omitted; exact hash/size/shape are recorded in
omitted-artifacts.json. Full original archive and numbered parts retain it.
The root MANIFEST.sha256 covers THIS review ZIP. The full original manifest
and handoff are preserved under original-delivery/. Verify from unpacked root.
No new mathematics; coordinator determinant and IO-only delivery binding remain
separate. For complete scope/pins/commands see original-delivery/HANDOFF.txt
and payload/results/skew-A8-denominator-20261024/RUN.md.
'''
review_members['HANDOFF.txt']=review_handoff.encode('utf-8')
review_manifest=''.join(hashlib.sha256(v).hexdigest()+'  '+k+'\n' for k,v in sorted(review_members.items()))
write(dest/'A8-review-MANIFEST.sha256',review_manifest)
review=dest/'A8-review.zip'
with zipfile.ZipFile(review,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for name,data in sorted(review_members.items()):z.writestr(name,data)
    z.writestr('MANIFEST.sha256',review_manifest.encode('utf-8'))
with zipfile.ZipFile(review) as z:
    if z.testzip() is not None:raise RuntimeError('Review ZIP CRC failure')
    for name,data in review_members.items():
        if z.read(name)!=data:raise RuntimeError('Review byte preservation failed')
parts=dest/'parts';parts.mkdir();records=[];h=hashlib.sha256();total=0
with archive.open('rb') as f:
    i=1
    while True:
        chunk=f.read(2000000)
        if not chunk:break
        part=parts/f'A8-denominator.zip.part{i:03d}';part.write_bytes(chunk)
        records.append({'path':part.relative_to(dest).as_posix(),'bytes':len(chunk),'sha256':sha(part)})
        i+=1
for rec in records:
    data=(dest/rec['path']).read_bytes();h.update(data);total+=len(data)
if h.hexdigest()!=sha(archive) or total!=archive.stat().st_size:raise RuntimeError('Slice concatenation mismatch')
write(dest/'PARTS.sha256',''.join(v['sha256']+'  '+v['path']+'\n' for v in records))
artifact_paths=['A8-denominator.zip','A8-review.zip','MANIFEST.sha256','A8-review-MANIFEST.sha256','HANDOFF.txt','ADDED-FILES.txt','omitted-artifacts.json','PARTS.sha256']
artifacts={p:{'bytes':(dest/p).stat().st_size,'sha256':sha(dest/p)} for p in artifact_paths}
delivery={'status':'COMPLETE_IMMUTABLE_A8_CHANGED_FILE_DELIVERY','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'integration_parent':'c6e2e54f957eeeaa97cabc7a26df6d81ffd759ee','cached_execution_checkout':'fc4f38a338b47addf62d1bf699783302285378fe',
          'full_parent_materialized':False,'expected_combined_git_tree_claimed':False,
          'payload_files':len(entries),'review_retained_original_payload_files':len(entries)-1,
          'artifacts':artifacts,'matrix':entries[raw]|{'path':raw,'shape':[6000,5911],'dtype':'<u2','order':'C','header':False},
          'inputs_sha256':'1e635a3e0c6e5be593ce954e638bd37f2453b882110d7da41ce268709772d9c4',
          'parts':records,'reconstruction_order':'Concatenate part001 through part%03d in numeric order, raw bytes, no separators.'%len(records),
          'manifest_layout':{'full':'Root MANIFEST.sha256 uses payload/ prefixes.','review':'Own root manifest; original full manifest/handoff under original-delivery/.','parts':'PARTS.sha256 uses parts/ prefixes relative to this delivery directory.'},
          'remaining':'Coordinator IO-only minor/domain/basis binding and Hodge Lab integration/publication.',
          'new_mathematics_during_packaging':False}
write(dest/'DELIVERY.json',dumps(delivery))
verification={'status':'PASS_BYTE_PACKAGING_ONLY','payload_files':len(entries),'utf8_text_files':text_count,
              'full_zip_crc_and_member_hashes':True,'review_retained_original_bytes_equal':True,'slice_reconstruction_exact':True,
              'parts_max_bytes':max(v['bytes'] for v in records),'source_mutations':False,'new_math':False,
              'packager_sha256':sha(Path(__file__)),'elapsed_seconds':time.monotonic()-start,
              'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
write(dest/'packaging-verification.json',dumps(verification))
sums=artifact_paths+['DELIVERY.json','packaging-verification.json']
write(dest/'SHA256SUMS.txt',''.join(sha(dest/p)+'  '+p+'\n' for p in sums))
print(dumps({'delivery':str(dest),'artifacts':artifacts,'parts':records,'verification':verification}))
