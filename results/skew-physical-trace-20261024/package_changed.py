#!/usr/bin/env python3
"""Changed-file-only handoff; raw index bytes, no commit or push."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,subprocess,time,zipfile
ROOT=Path(__file__).resolve().parents[2]
BASE='2bbbaa312642822c28483ba85cbbccf0af97d6dc'
BATCH=ROOT/'results/skew-physical-trace-20261024'
OUT=ROOT.parent/'handoff-physical-trace-20261024'
START=time.monotonic()
def sha(data):return hashlib.sha256(data).hexdigest()
def git(*args,input=None):return subprocess.check_output(['git',*args],cwd=ROOT,input=input)
def js(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser();p.add_argument('--receipt',required=True);a=p.parse_args()
 receipt_path=ROOT/a.receipt;receipt=json.loads(receipt_path.read_text(encoding='utf-8'))
 if receipt['status']!='PASS':raise RuntimeError('Final checker must pass')
 if git('rev-parse','HEAD').decode().strip()!=BASE:raise RuntimeError('Unexpected parent')
 OUT.mkdir(exist_ok=False)
 old=git('show',BASE+':LEDGER.md');cur=(ROOT/'LEDGER.md').read_bytes()
 if not cur.startswith(old) or len(old)!=440921 or sha(old)!='1da42f452082925e8d6983c37276a062f336fb4e0a0ca02920403e377fa2ec9f':raise RuntimeError('Parent ledger prefix changed')
 names=['.github/workflows/lean.yml','README.md','LEDGER.md','formal/AuditSkewPhysicalTrace.lean','formal/ReplaySkewPhysicalTrace.lean','formal/HodgeLab/OneReflectionSkew/PhysicalTraceBridge.lean','formal/check_skew_physical_trace.py','formal/results/skew-physical-trace/inputs.json','notes/skew-physical-trace-bridge.md','scripts/visualize_skew_physical_trace.py']
 selected=[ROOT/n for n in names]+sorted(p for p in BATCH.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc')
 if len(selected)!=len(set(selected)):raise RuntimeError('Duplicate selection')
 text_count=0;binary=[];index=[]
 for p in selected:
  rel=p.relative_to(ROOT).as_posix();data=p.read_bytes()
  if p.suffix.lower() in {'.png','.zip'}:binary.append(rel)
  else:data.decode('utf-8');text_count+=1
  blob=git('hash-object','-w','--stdin',input=data).decode().strip()
  mode='100755' if os.access(p,os.X_OK) else '100644';index.append(f'{mode} {blob}\t{rel}\0'.encode())
 git('update-index','-z','--index-info',input=b''.join(index))
 changed=[x for x in git('diff','--cached','--name-only','-z',BASE).decode().split('\0') if x]
 expected={p.relative_to(ROOT).as_posix() for p in selected}
 if set(changed)!=expected:raise RuntimeError('Unexpected staged selection: '+repr(set(changed)^expected))
 parent_paths={x.decode() for x in git('ls-tree','-r','--name-only','-z',BASE).split(b'\0') if x}
 modified_old=set(changed)&parent_paths
 if modified_old!={'.github/workflows/lean.yml','README.md','LEDGER.md'}:raise RuntimeError('Historical source/receipt modified: '+repr(modified_old))
 for p in selected:
  if git('show',':'+p.relative_to(ROOT).as_posix())!=p.read_bytes():raise RuntimeError('Staged bytes differ: '+str(p))
 tree=git('write-tree').decode().strip()
 patch=git('diff','--cached','--binary','--full-index','--no-ext-diff',BASE)
 patch_path=OUT/'physical-trace-bridge.patch';patch_path.write_bytes(patch)
 payload=OUT/'payload';payload.mkdir()
 for rel in changed:
  dest=payload/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(git('show',':'+rel))
 all_ws=subprocess.run(['git','diff','--cached','--check',BASE],cwd=ROOT,capture_output=True)
 (OUT/'staged-whitespace-check.log').write_bytes(all_ws.stdout+all_ws.stderr)
 clean_names=[n for n in changed if '/lean-development/' not in n and '/bootstrap/' not in n]
 code_ws=subprocess.run(['git','diff','--cached','--check',BASE,'--',*clean_names],cwd=ROOT,capture_output=True)
 (OUT/'source-documentation-whitespace-check.log').write_bytes(code_ws.stdout+code_ws.stderr)
 if code_ws.returncode:raise RuntimeError('Current code/documentation whitespace check failed')
 submodules=[]
 for line in git('ls-tree','-r',BASE).decode().splitlines():
  if line.startswith('160000 '):
   m,path=line.split('\t',1);submodules.append({'path':path,'sha':m.split()[2],'mode':'160000'})
 limits=json.loads((BATCH/'execution-summary.json').read_text(encoding='utf-8'))
 meta={'parent':BASE,'upstream':'e96be434bd55d6013d7a5854732cb317ca0e43e7','expected_staged_tree':tree,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'changed_file_count':len(changed),'changed_paths':changed,'modified_parent_paths':sorted(modified_old),'unchanged_gitlinks':submodules,'utf8_text_files':text_count,'binary_files':binary,'parent_ledger_bytes':len(old),'parent_ledger_sha256':sha(old),'final_focused_receipt_path':a.receipt,'final_focused_receipt_sha256':sha(receipt_path.read_bytes()),'module_sha256':sha((ROOT/'formal/HodgeLab/OneReflectionSkew/PhysicalTraceBridge.lean').read_bytes()),'patch_sha256':sha(patch),'worker_publication':'No commit, push, upstream post or PR; coordinator owns publication','scope':'Actual physical coefficient embedding, Q compatibility, quotient/derivative/source evaluation, exhaustive18 roots and finite-algebra tensor/trace bridge','remaining':'Compatible all-sheet allowed-domain physical differential-form/source-class maps; no exactness/primitive/certificate claim','remote_ci':'No new remote CI; prior40084595344 reused only','math_stop_utc':limits['math_stop_utc'],'packaging_limit_seconds':300,'all_whitespace_exit_code':all_ws.returncode,'source_documentation_whitespace_exit_code':code_ws.returncode,'exclusions':['unchanged repository','Git databases','caches','expanded submodules'],'coordinator_apply_validation':'Coordinator has exact parent and independently applies/checks tree; no full-parent archive'}
 js(OUT/'handoff.json',meta)
 handoff=f'''# Physical trace bridge handoff

24 October 2026 EDT. The Goal-enabled coordinator owns integration,
publication and full remote CI. This worker made no commit, push or
upstream post/reply/PR.

- Exact parent: `{BASE}`
- Upstream: `e96be434bd55d6013d7a5854732cb317ca0e43e7`
- Expected staged tree: `{tree}`
- Changed/added files: {len(changed)}
- Patch SHA256: `{sha(patch)}`

## Apply

```bash
git apply --check physical-trace-bridge.patch
git apply --index physical-trace-bridge.patch
git write-tree
```

The tree must equal the value above. The payload is raw staged bytes;
the binary-safe patch includes the scientific PNG. MANIFEST.sha256 covers
every archive member except itself. External SHA256SUMS.txt hashes the ZIP,
patch, manifest, this handoff and handoff.json. Only changed/added files
are delivered. No unchanged repository, Git databases, cache or expanded
submodule is included; gitlinks remain references. The coordinator has
the exact parent and performs the full apply/tree validation.

## Proved bridge

The existing K=Q(v)(t)(a) injects into the existing physical Curve, with
a=(1+r^6+w^6)/r^3, v=1/r+rw, t=t. Physical base independence and the
existing rational-algebra compatibility are proved. The actual quotient
evaluation E=AdjoinRoot f -> Curve sends theta to r, derivative to f_r,
inverse derivative to 1/f_r and sourceScalar to nonzero r^11/(12*f_r).
No irreducibility/field/injectivity assertion is made for E evaluation.

The existing full splitting field embeds compatibly into Curve. Its18
roots remain distinct and exhaustive; a proved matching sheet evaluates
at physical r. Slot11 is a power index, not that sheet index. The actual
left Curve-algebra T=Curve tensor_K E is finite free rank18 and isomorphic
to Curve^18, with beta(l tensor e)_j=l*sigma_j(e). Trace base change and
all-sheet sums hold for arbitrary e; trace transport holds for arbitrary
z:T. The scalar source has full trace0, while its physical value is nonzero.
Controls distinguish evaluation1=1, trace1=18 and trace(2 tensor1)=36.

This does not construct compatible physical-form maps on all sheets.
The smallest next dependency is a valid regular-domain sheet construction
fixing compact V=rU and z, with U_j=V/r_j, and proved curve/form compatibility.
Scalar trace zero is separate from full two-row source exactness. The
checkpoint142 P[z^-1] boundary remains: no ambient field map killing G
and no G^-1 evaluation. Four-form nonvanishing, whole/minimal function-field
identity, cohomology/GM, primitive, clearing, certificate and solve remain
outside this unit.

## Executed evidence

Final writer receipt: `{a.receipt}`; SHA256
`{meta['final_focused_receipt_sha256']}`.
98 declarations/instances audited, one new-module kernel replay,39 positive
and10 intended mathematical False-goal controls; {receipt['elapsed_seconds']:.3f}s.
Allowed axioms: propext, Classical.choice, Quot.sound. Cached imports reused,
not counted as new kernel replays. Union-of-actual-local-imports manifest
pins31 historical inputs. Lean4.31.0, Mathlib
fabf563a7c95a166b8d7b6efca11c8b4dc9d911f. Exact Python version and every
command/start/elapsed/exit/stdout/stderr are in receipts.

All development attempts and failed checker runs are preserved. Attempts04,
10 and12 compiled successive stages; other attempts record path/import/API/
instance/search failures. Checker01 failed caller Q-instance elaboration;
checker02 failed because the explicit local instance header needed
noncomputable marking. These are not counted as passing focused checks.
Read-only mathematical/API and adversarial evidence AI reviews are separate
from writer execution and from human review. Reviewer hash/log audit and
source-inspection receipts have their own executor labels. Prior successful
CI40084595344 is reused only; no new remote CI is claimed.

```bash
cd formal
timeout 600 python3 -O check_skew_physical_trace.py \\
  --output-dir results/runs/physical-trace-reproduction
```

Use a fresh output directory and pinned toolchain. A fresh-output focused
CI step is included. Reproduce the diagram from repository root:

```bash
python3 scripts/visualize_skew_physical_trace.py \\
  --receipt {a.receipt} \\
  --output-dir results/skew-physical-trace-20261024/visualization-reproduction
```

The PNG/SVG, generator and all input/output hashes are in visualization-01.
The final PNG was inspected. The diagram has permanent theorem boundaries,
not a transient CI label.

Checkpoint143 preserves all440921 parent ledger bytes, SHA256
1da42f452082925e8d6983c37276a062f336fb4e0a0ca02920403e377fa2ec9f.
Only README,LEDGER and the CI workflow change among parent-tracked files;
all old proof/result bytes remain unchanged in the staged tree. Posts1–29
and tally29 discussions/one closed maintenance PR/zero accepted authored
solves are unchanged. Raw failed-source/log bytes retain their original
whitespace; current source/documentation check passes.

One mathematical approach. Start10:28:47UTC; stop{limits['math_stop_utc']}.
45-minute mathematical bound;120s per Lean process,600s checker,45s network;
no interrupted calculation counted. Five-minute changed-file packaging
limit recorded separately. No publication/authentication retry was attempted.
'''
 (OUT/'HANDOFF.md').write_text(handoff,encoding='utf-8')
 files=sorted(p for p in OUT.rglob('*') if p.is_file())
 (OUT/'MANIFEST.sha256').write_text(''.join(f'{sha(p.read_bytes())}  {p.relative_to(OUT).as_posix()}\n' for p in files),encoding='utf-8')
 zip_path=OUT/'physical-trace-bridge.zip'
 with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(OUT.rglob('*')):
   if p.is_file() and p!=zip_path:z.write(p,p.relative_to(OUT).as_posix())
 with zipfile.ZipFile(zip_path) as z:
  if z.testzip() is not None:raise RuntimeError('ZIP CRC failure')
  for line in (OUT/'MANIFEST.sha256').read_text(encoding='utf-8').splitlines():
   expected,member=line.split('  ',1)
   if sha(z.read(member))!=expected:raise RuntimeError('ZIP member hash mismatch: '+member)
 (OUT/'SHA256SUMS.txt').write_text(''.join(f'{sha(p.read_bytes())}  {p.name}\n' for p in [zip_path,patch_path,OUT/'MANIFEST.sha256',OUT/'HANDOFF.md',OUT/'handoff.json']),encoding='utf-8')
 print(json.dumps({'status':'PASS','out':str(OUT),'expected_staged_tree':tree,'changed_files':len(changed),'zip_bytes':zip_path.stat().st_size,'zip_sha256':sha(zip_path.read_bytes()),'patch_sha256':sha(patch),'manifest_sha256':sha((OUT/'MANIFEST.sha256').read_bytes()),'packaging_script_seconds':time.monotonic()-START,'all_whitespace_exit_code':all_ws.returncode,'source_documentation_whitespace_exit_code':code_ws.returncode},indent=2))
if __name__=='__main__':
 try:main()
 except Exception as e:
  OUT.mkdir(exist_ok=True);js(OUT/'packaging-failure.json',{'error':repr(e),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-START});raise
