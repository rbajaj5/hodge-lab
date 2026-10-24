"""Create the changed-file A7 delivery; byte binding only, no mathematics.

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
files=[root/'notes/skew-A7-denominator-20261024.md']
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
raw='payload/results/skew-A7-denominator-20261024/lead/matrix-01/result/augmented-matrix.u16.bin'
if entries[raw] != {'bytes':55007040,'sha256':'7ab80831f8757663bc208ecb4a391509ab18080b0a6f776d0a4b57695c9e2230'}:
    raise RuntimeError('Pinned matrix changed during packaging')
manifest=''.join(f"{v['sha256']}  {k}\n" for k,v in sorted(entries.items()))
write(dest/'MANIFEST.sha256',manifest)
write(dest/'ADDED-FILES.txt',''.join(k.removeprefix('payload/')+'\n' for k in sorted(entries)))
handoff='''A7 full-current handoff — mathematics frozen; integration only
Date:24 October2026, America/New_York. Mathematical close:14:13:01EDT /18:13:01UTC.
Integration deadline:14:28:01EDT /18:28:01UTC.

Integration parent:030d13b75270f6ad1a774e9c11321038fe6305e9
Cached execution checkout:fc4f38a338b47addf62d1bf699783302285378fe
Upstream coordinator pin:27f4bb9ad8757e5841f884d9d30124a3c97a847d
No fresh full parent or combined Git tree is claimed. Current-parent AGENTS,
board and connection were read via connector; Git blobs and source bytes match.
SourceSHA256:a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d

OWNED ADDITIONS ONLY:notes/skew-A7-denominator-20261024.md and
results/skew-A7-denominator-20261024/. No shared edits, Lean, commit, push or
upstream actions. Coordinator owns integration and Hodge Lab publication.

RESULT:finite rational-CONSTANT family(B+B/A+...+B/A^7)^6 excluded, where
B spans r^m v^n t^k,-10<=m<=2,0<=n,k<=2. Original5616 parameters;
only P7 tangent:top294 plus ALL4914 lower parameters free=5208.
Both rows/full physical derivatives/fullNt/positive r^-4 Mb e0/12 retained.
Imported det(Ra-7I)=154/3,tau7=-11r^7+24r; lower pole coupling retained.

Fixed prime65519,seed2026102497,2640 admissible points; full5280x5209 matrix.
First5209 rows are decisive; coordinator independently reports determinant
56940 mod65519,27,133,681 entries at2605points,18.563s,3controls.
Pro did NOT execute a determinant or install a backend.
Pro author:25.995578s,exit0. Separate AI reconstruction:26.800365s,exit0;
all27,503,520 entries,2640domains,basis/rejections match;23controls detected.
No math failures,timeouts or repairs. Coordinator algebra:7checks+3controls,
2.297s process,0.187s algebra,10byte bindings,imported only.

MATRIX:row-major little-endian uint16(<u2),no header,shape(5280,5209),
55,007,040bytes. Final column positive source.
SHA256:7ab80831f8757663bc208ecb4a391509ab18080b0a6f776d0a4b57695c9e2230
inputs.jsonSHA256:4d67271f1607894a72afab28a39d3ee0e2e1752da414f3e85b6b32f418ee4ded
Exact domains,basis labels and source pins are included. No rejected samples.
Coordinator frozen arraySHA256:8f4a48490018861c4599e08ae1e6da0e279b874c260e96d6350af74110f81b28
Its container was not specified in relay; the optional IO-only binder accepts
the exact pinned array as NPY or raw. Not executed in Pro.

REMAINING:coordinator IO-only decisive-entry/domain/basis comparison to its
frozen independent data, then shared-file integration and normal Hodge Lab push.
No extra math/review/backend setup is needed. No primitive,source exactness,
global rational-current obstruction,cohomology theorem,certificate or solve.

ARCHIVE LAYOUT:payload/<repository-relative-path>,MANIFEST.sha256,HANDOFF.txt.
Full root manifest entries start payload/; verify from unpacked archive root,
then apply contents of payload/ only. ADDED-FILES.txt is an added-file inventory,
not a combined Git tree. No repository/cache/submodule dump.
Review ZIP retains every non-matrix payload byte, with its own root manifest.
Original manifest/handoff under original-delivery/; omitted-artifacts.json
identifies only the bulky matrix. Full ZIP and slices contain that matrix.
PARTS.sha256 paths start parts/. Concatenate part001 onward in numeric order
as raw bytes without separators. Parts<=2,000,000bytes each. DELIVERY.json
and SHA256SUMS.txt give exact original/review archive hashes and sizes.

RUN.md provides fresh-directory <=60s -O reproduction commands. No old run
or historical receipt rewritten. Scientific PNG/SVG and generator/input/output
hashes included; PNG inspected. Credit fqlx,benediamond,hodge.computer framework.
'''
write(dest/'HANDOFF.txt',handoff)
archive=dest/'A7-denominator.zip'
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for name in sorted(entries):z.write(dest/name,name)
    z.write(dest/'MANIFEST.sha256','MANIFEST.sha256');z.write(dest/'HANDOFF.txt','HANDOFF.txt')
with zipfile.ZipFile(archive) as z:
    if z.testzip() is not None:raise RuntimeError('Full ZIP CRC failure')
    if set(z.namelist())!=set(entries)|{'MANIFEST.sha256','HANDOFF.txt'}:raise RuntimeError('Full ZIP member inventory mismatch')
    for name,value in entries.items():
        if hashlib.sha256(z.read(name)).hexdigest()!=value['sha256']:raise RuntimeError('Full ZIP member binding failed')
omitted={'omitted_only_from_review_zip':[{'archive_path':raw,**entries[raw],'format':'headerless C-order <u2','shape':[5280,5209]}],
         'original_zip_retains_every_payload_byte':True,'new_mathematics':False}
write(dest/'omitted-artifacts.json',dumps(omitted))
review_members={k:(dest/k).read_bytes() for k in entries if k!=raw}
review_members['original-delivery/MANIFEST.sha256']=manifest.encode('utf-8')
review_members['original-delivery/HANDOFF.txt']=handoff.encode('utf-8')
review_members['omitted-artifacts.json']=(dest/'omitted-artifacts.json').read_bytes()
review_handoff='''A7 REVIEW ZIP:all non-matrix original payload bytes unchanged.
Only the bulky raw matrix is omitted; exact hash/size/shape are recorded in
omitted-artifacts.json. Full original archive and numbered parts retain it.
The root MANIFEST.sha256 covers THIS review ZIP. The full original manifest
and handoff are preserved under original-delivery/. Verify from unpacked root.
No new mathematics; coordinator determinant and IO-only delivery binding remain
separate. For complete scope/pins/commands see original-delivery/HANDOFF.txt
and payload/results/skew-A7-denominator-20261024/RUN.md.
'''
review_members['HANDOFF.txt']=review_handoff.encode('utf-8')
review_manifest=''.join(hashlib.sha256(v).hexdigest()+'  '+k+'\n' for k,v in sorted(review_members.items()))
write(dest/'A7-review-MANIFEST.sha256',review_manifest)
review=dest/'A7-review.zip'
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
        part=parts/f'A7-denominator.zip.part{i:03d}';part.write_bytes(chunk)
        records.append({'path':part.relative_to(dest).as_posix(),'bytes':len(chunk),'sha256':sha(part)})
        i+=1
for rec in records:
    data=(dest/rec['path']).read_bytes();h.update(data);total+=len(data)
if h.hexdigest()!=sha(archive) or total!=archive.stat().st_size:raise RuntimeError('Slice concatenation mismatch')
write(dest/'PARTS.sha256',''.join(v['sha256']+'  '+v['path']+'\n' for v in records))
artifact_paths=['A7-denominator.zip','A7-review.zip','MANIFEST.sha256','A7-review-MANIFEST.sha256','HANDOFF.txt','ADDED-FILES.txt','omitted-artifacts.json','PARTS.sha256']
artifacts={p:{'bytes':(dest/p).stat().st_size,'sha256':sha(dest/p)} for p in artifact_paths}
delivery={'status':'COMPLETE_IMMUTABLE_A7_CHANGED_FILE_DELIVERY','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'integration_parent':'030d13b75270f6ad1a774e9c11321038fe6305e9','cached_execution_checkout':'fc4f38a338b47addf62d1bf699783302285378fe',
          'full_parent_materialized':False,'expected_combined_git_tree_claimed':False,
          'payload_files':len(entries),'review_retained_original_payload_files':len(entries)-1,
          'artifacts':artifacts,'matrix':entries[raw]|{'path':raw,'shape':[5280,5209],'dtype':'<u2','order':'C','header':False},
          'inputs_sha256':'4d67271f1607894a72afab28a39d3ee0e2e1752da414f3e85b6b32f418ee4ded',
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
