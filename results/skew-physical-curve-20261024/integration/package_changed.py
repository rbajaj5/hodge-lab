#!/usr/bin/env python3
"""Package only this unit's explicit changed files; preserve raw staged bytes."""
from pathlib import Path
import datetime,hashlib,json,os,subprocess,sys,time,zipfile
ROOT=Path(__file__).resolve().parents[3]
BASE='e2182223a0395cfb758a2ee09e304eb940b7a67a'
BATCH=ROOT/'results/skew-physical-curve-20261024'
OUT=ROOT.parent/'handoff-physical-curve-20261024'
START=time.monotonic()
def sha(data): return hashlib.sha256(data).hexdigest()
def git(*args,input=None):
 return subprocess.check_output(['git',*args],cwd=ROOT,input=input)
def write_json(path,value): path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 if git('rev-parse','HEAD').decode().strip()!=BASE: raise RuntimeError('Unexpected parent')
 OUT.mkdir(exist_ok=False)
 receipt=json.loads((BATCH/'lean-development/checker-02/validation.json').read_text(encoding='utf-8'))
 if receipt['status']!='PASS': raise RuntimeError('Final checker did not pass')
 old=git('show',BASE+':LEDGER.md');current=(ROOT/'LEDGER.md').read_bytes()
 if not current.startswith(old) or len(old)!=430885: raise RuntimeError('Parent ledger changed')
 selected=[ROOT/p for p in ['.github/workflows/lean.yml','README.md','LEDGER.md',
   'formal/AuditSkewPhysicalCurve.lean','formal/ReplaySkewPhysicalCurve.lean',
   'formal/HodgeLab/OneReflectionSkew/PhysicalCurveRealization.lean',
   'formal/check_skew_physical_curve.py',
   'formal/results/skew-physical-curve/inputs.json',
   'notes/skew-physical-curve-realization.md','scripts/visualize_skew_physical_curve.py']]
 selected+=sorted(p for p in BATCH.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc')
 if len(selected)!=len(set(selected)): raise RuntimeError('Duplicate selected path')
 text_count=0;binary=[];index_lines=[]
 for p in selected:
  rel=p.relative_to(ROOT).as_posix();data=p.read_bytes()
  if p.suffix.lower() in {'.png','.zip'}: binary.append(rel)
  else: data.decode('utf-8');text_count+=1
  # Raw blob insertion avoids changing protected packet or failed-attempt bytes through attributes.
  blob=git('hash-object','-w','--stdin',input=data).decode().strip()
  mode='100755' if os.access(p,os.X_OK) else '100644'
  index_lines.append(f'{mode} {blob}\t{rel}\0'.encode())
 git('update-index','-z','--index-info',input=b''.join(index_lines))
 changed=git('diff','--cached','--name-only','-z',BASE).decode().strip('\0').split('\0')
 expected={p.relative_to(ROOT).as_posix() for p in selected}
 if set(changed)!=expected: raise RuntimeError('Unexpected staged paths: '+repr(set(changed)^expected))
 old_paths={p.decode() for p in git('ls-tree','-r','--name-only','-z',BASE).split(b'\0') if p}
 modified_old=set(changed)&old_paths
 if modified_old!={'.github/workflows/lean.yml','README.md','LEDGER.md'}: raise RuntimeError('Historical file modification: '+repr(modified_old))
 for p in selected:
  rel=p.relative_to(ROOT).as_posix()
  if git('show',':'+rel)!=p.read_bytes(): raise RuntimeError('Staged/worktree byte mismatch: '+rel)
 tree=git('write-tree').decode().strip()
 patch=git('diff','--cached','--binary','--full-index','--no-ext-diff',BASE)
 patch_path=OUT/'physical-curve-realization.patch';patch_path.write_bytes(patch)
 payload=OUT/'payload';payload.mkdir()
 for rel in changed:
  dest=payload/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(git('show',':'+rel))
 check=subprocess.run(['git','diff','--cached','--check',BASE],cwd=ROOT,capture_output=True)
 (OUT/'staged-whitespace-check.log').write_bytes(check.stdout+check.stderr)
 submodules=[]
 for line in git('ls-tree','-r',BASE).decode().splitlines():
  if line.startswith('160000 '):
   m,path=line.split('\t',1);submodules.append({'path':path,'sha':m.split()[2],'mode':'160000'})
 final_review=json.loads((BATCH/'source-review/final-review.json').read_text(encoding='utf-8'))
 meta={'parent':BASE,'upstream':'e96be434bd55d6013d7a5854732cb317ca0e43e7','expected_staged_tree':tree,
  'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'changed_file_count':len(changed),
  'changed_paths':changed,'modified_parent_paths':sorted(modified_old),'unchanged_gitlinks':submodules,
  'utf8_text_files':text_count,'binary_files':binary,'parent_ledger_bytes':len(old),'parent_ledger_sha256':sha(old),
  'final_focused_receipt_sha256':sha((BATCH/'lean-development/checker-02/validation.json').read_bytes()),
  'module_sha256':sha((ROOT/'formal/HodgeLab/OneReflectionSkew/PhysicalCurveRealization.lean').read_bytes()),
  'patch_sha256':sha(patch),'worker_publication':'No commit, push, upstream post or PR; coordinator owns publication',
  'scope':'Concrete physical curve realization, compatible polynomial-localization Kaehler/exterior pullbacks, proved generic nonzeros and instantiated source theorem',
  'remaining':'Transformed base and prior trace-tower comparison; whole hypersurface function-field identification; residue/cohomology source-class realization',
  'ci':'Prior run40051515847 succeeded on a4a253e; reused receipt only, no new remote CI execution',
  'math_stop_utc':receipt['completed_utc'],'packaging_limit_seconds':300,
  'whitespace_check_exit_code':check.returncode,
  'exclusions':['unchanged parent content','Git databases','caches','expanded submodules'],
  'no_full_parent_archive':True,'coordinator_apply_validation':'Not repeated here; coordinator has exact parent and validates applied tree'}
 write_json(OUT/'handoff.json',meta)
 handoff=f'''# Physical curve realization handoff

24 October 2026 EDT. No worker commit, push or upstream publication.
The Goal-enabled coordinator owns integration and publication.

- Exact parent: `{BASE}`
- Upstream: `e96be434bd55d6013d7a5854732cb317ca0e43e7`
- Expected staged tree: `{tree}`
- Changed files: {len(changed)}.
- Binary patch SHA256: `{sha(patch)}`

## Apply and verify

```bash
git apply --check physical-curve-realization.patch
git apply --index physical-curve-realization.patch
git write-tree
```

The final command must equal the tree above. Payload files are raw index
bytes. MANIFEST.sha256 covers every archive member except itself; external
SHA256SUMS.txt hashes the ZIP, patch, manifest, handoff and metadata.
Only changed/added files are included. Unchanged repository content, Git
databases, caches and expanded submodules are excluded. Gitlinks are
recorded as references. Coordinator owns full-parent apply validation.

## Proved result and limits

B=Frac(Q[U,r,w,t]) embeds injectively into L=AlgebraicClosure B, preserving
all four independent parameters. Constructed roots satisfy z^6=-cubic
and x^2=U. The original protected point (x,rx,wx,1,t,z) has F=0 and A=x^3.
The common allowed domain S=Q[U,r,w,t,z][z^-1] has actual Q-algebra maps
to the old ambient field and L, with universal Kaehler/exterior maps and
all coordinate differential images. Its regular source maps to both
the old residueScalar • alpha and the curve normalized representative.
The curve/square differential relations and r,z,f_r,Delta nonzero are
proved. realized_source_reduction has no residual curve/chart hypotheses.

No whole ambient-field specialization or evaluation of G^-1 is permitted;
the corresponding obstruction is proved. No whole irreducible function
field/minimal-component identification, comparison with the prior
Q(v)(t)(a) trace tower, residue/cohomology realization, primitive, global
clearing, certificate or solve is claimed. Both compact rows remain.
The smallest next dependency is transformed-base independence and the
comparison maps to the earlier trace construction.

## Actual checks

Final writer checker-02: 81 audited declarations, one new-module kernel
replay, 25 positive controls, eight intended False-goal controls;
{receipt['elapsed_seconds']:.3f}s. Receipt SHA256:
`{meta['final_focused_receipt_sha256']}`.
All negative controls reject mathematical mutations rather than API errors.
Five development attempts (four failures then PASS) and two passing
focused checks are retained. Checker-02 follows explicit UTF-8 fixes.
Expired-cache restoration rebuilt dependencies but did not rerun old
focused mathematics. Initial sandbox network failure and tar ownership
warnings/extraction exit are preserved. Lean4.31.0; pinned Mathlib
fabf563a7c95a166b8d7b6efca11c8b4dc9d911f; Python3.12.14.

Read-only AI math/API and adversarial reviewers ran no Lean or symbolic
mathematics. The evidence reviewer ran a 0.05445s hash/log audit:37
source/context hashes,42 command streams,81 declarations and saved controls.
These are AI reviews, not independent human review. Prior successful
CI40051515847 is reused evidence. No new remote CI is claimed.

```bash
cd formal
timeout 600 python3 -O check_skew_physical_curve.py \
  --output-dir results/runs/physical-curve-reproduction
```

Use the pinned Lean/Mathlib toolchain and a fresh output directory. The new
CI step follows that lifecycle. The final scientific PNG/SVG, generator
and input/output hash manifest are under visualization-02. From repo root:

```bash
python3 scripts/visualize_skew_physical_curve.py \
  --receipt results/skew-physical-curve-20261024/lean-development/checker-02/validation.json \
  --output-dir results/skew-physical-curve-20261024/visualization-reproduction
```

Checkpoint142 appends to the exact430885-byte parent ledger, SHA256
f4e1e853360368889cd83be8536d4f0c509a73464d391311c91639c326abbc66.
Only README,LEDGER and the CI workflow differ among parent-tracked files.
Posts1–29 and tally29/1/0 are unchanged. Historical receipts remain intact.

One implementation approach,09:39:45–09:58:13UTC, within45minutes.
Lean120s/checker600s/network45s process limits; no timeout counted as result.
Five minutes allotted separately to packaging. No full-parent archive or
coordinator apply audit is repeated. Raw failure logs are retained even
when their whitespace does not meet source formatting conventions.
'''
 (OUT/'HANDOFF.md').write_text(handoff,encoding='utf-8')
 files=sorted(p for p in OUT.rglob('*') if p.is_file())
 (OUT/'MANIFEST.sha256').write_text(''.join(f'{sha(p.read_bytes())}  {p.relative_to(OUT).as_posix()}\n' for p in files),encoding='utf-8')
 zip_path=OUT/'physical-curve-realization.zip'
 with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(OUT.rglob('*')):
   if p.is_file() and p!=zip_path:z.write(p,p.relative_to(OUT).as_posix())
 with zipfile.ZipFile(zip_path) as z:
  if z.testzip() is not None: raise RuntimeError('ZIP CRC check failed')
  for line in (OUT/'MANIFEST.sha256').read_text(encoding='utf-8').splitlines():
   expected,member=line.split('  ',1)
   if sha(z.read(member))!=expected: raise RuntimeError('Archive member hash mismatch: '+member)
 elapsed=time.monotonic()-START
 (OUT/'SHA256SUMS.txt').write_text(''.join(f'{sha(p.read_bytes())}  {p.name}\n' for p in [zip_path,patch_path,OUT/'MANIFEST.sha256',OUT/'HANDOFF.md',OUT/'handoff.json']),encoding='utf-8')
 print(json.dumps({'status':'PASS','out':str(OUT),'expected_staged_tree':tree,'changed_files':len(changed),
   'zip_bytes':zip_path.stat().st_size,'zip_sha256':sha(zip_path.read_bytes()),'patch_sha256':sha(patch),
   'manifest_sha256':sha((OUT/'MANIFEST.sha256').read_bytes()),'packaging_seconds':elapsed,
   'whitespace_check_exit_code':check.returncode},indent=2))
if __name__=='__main__':
 try: main()
 except Exception as e:
  OUT.mkdir(exist_ok=True)
  write_json(OUT/'packaging-failure.json',{'error':repr(e),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-START})
  raise
