#!/usr/bin/env python3
"""Package only this unit's explicit changed files; preserve raw staged bytes."""
from pathlib import Path
import datetime,hashlib,json,os,subprocess,sys,time,zipfile
ROOT=Path(__file__).resolve().parents[3]
BASE='bbb8aa406cd2a8b5ddb06d6e14358781b9c215e9'
BATCH=ROOT/'results/skew-physical-source-20261023'
OUT=ROOT.parent/'handoff-physical-source-20261023'
START=time.monotonic()
def sha(data): return hashlib.sha256(data).hexdigest()
def git(*args,input=None):
 return subprocess.check_output(['git',*args],cwd=ROOT,input=input)
def write_json(path,value): path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 if git('rev-parse','HEAD').decode().strip()!=BASE: raise RuntimeError('Unexpected parent')
 OUT.mkdir(exist_ok=False)
 receipt=json.loads((BATCH/'lean-development/checker-04/validation.json').read_text())
 if receipt['status']!='PASS': raise RuntimeError('Final checker did not pass')
 old=git('show',BASE+':LEDGER.md');current=(ROOT/'LEDGER.md').read_bytes()
 if not current.startswith(old) or len(old)!=418118: raise RuntimeError('Parent ledger changed')
 selected=[ROOT/p for p in ['.github/workflows/lean.yml','README.md','LEDGER.md',
   'formal/AuditSkewPhysicalSource.lean','formal/ReplaySkewPhysicalSource.lean',
   'formal/HodgeLab/OneReflectionSkew/PhysicalSourceNormalization.lean',
   'formal/check_skew_physical_source_normalization.py',
   'formal/results/skew-physical-source/inputs.json',
   'notes/skew-physical-source-normalization.md','scripts/visualize_skew_physical_source.py']]
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
 patch_path=OUT/'physical-source-normalization.patch';patch_path.write_bytes(patch)
 payload=OUT/'payload';payload.mkdir()
 for rel in changed:
  dest=payload/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(git('show',':'+rel))
 check=subprocess.run(['git','diff','--cached','--check',BASE],cwd=ROOT,capture_output=True)
 (OUT/'staged-whitespace-check.log').write_bytes(check.stdout+check.stderr)
 submodules=[]
 for line in git('ls-tree','-r',BASE).decode().splitlines():
  if line.startswith('160000 '):
   m,path=line.split('\t',1);submodules.append({'path':path,'sha':m.split()[2],'mode':'160000'})
 final_review=json.loads((BATCH/'source-review/final-review.json').read_text())
 meta={'parent':BASE,'upstream':'b790130d43b49ec0ddc6865d0bdc949eeeee2319','expected_staged_tree':tree,
  'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'changed_file_count':len(changed),
  'changed_paths':changed,'modified_parent_paths':sorted(modified_old),'unchanged_gitlinks':submodules,
  'utf8_text_files':text_count,'binary_files':binary,'parent_ledger_bytes':len(old),'parent_ledger_sha256':sha(old),
  'final_focused_receipt_sha256':sha((BATCH/'lean-development/checker-04/validation.json').read_bytes()),
  'module_sha256':sha((ROOT/'formal/HodgeLab/OneReflectionSkew/PhysicalSourceNormalization.lean').read_bytes()),
  'patch_sha256':sha(patch),'worker_publication':'No commit, push, upstream post or PR; coordinator owns publication',
  'scope':'Conditional actual Kaehler four-form normalization and selected correction; exact quotient scalar trace link',
  'remaining':'Physical curve-field realization and compatible Kaehler pullback; Delta nonzero domain; cohomology/connection source-class comparison',
  'ci':'Prior run40046576101 succeeded on9cf1e71; no new remote CI execution',
  'math_stop_utc':receipt['completed_utc'],'packaging_limit_seconds':300,
  'whitespace_check_exit_code':check.returncode,
  'exclusions':['unchanged parent content','Git databases','caches','expanded submodules'],
  'no_full_parent_archive':True,'coordinator_apply_validation':'Not repeated here; coordinator has exact parent and validates applied tree'}
 write_json(OUT/'handoff.json',meta)
 handoff=f'''# Physical-source normalization handoff\n\n23 October 2026 EDT. Coordinator-owned publication; no worker commit or push.\n\n- Parent: `{BASE}`\n- Upstream: `b790130d43b49ec0ddc6865d0bdc949eeeee2319`\n- Expected staged tree: `{tree}`\n- Changed files: {len(changed)}; UTF-8 text files: {text_count}.\n- Binary-safe patch SHA256: `{sha(patch)}`\n\n## Apply on the exact parent\n\n```bash\ngit apply --check physical-source-normalization.patch\ngit apply --index physical-source-normalization.patch\ngit write-tree\n```\n\nThe last command should print the expected tree above. This worker does not\nrepeat a full-parent archive or coordinator apply audit. Payload files are\nraw index bytes. `MANIFEST.sha256` hashes each delivered member except itself;\nthe external `SHA256SUMS.txt` hashes the ZIP, patch and manifest. Submodule\ngitlinks are references in handoff.json, with no expanded submodules.\n\n## Proved result\n\n`source_four_form_reduction` derives the existing normalized pole coefficient\ntimes the actual old four-form as the literal packet's b-input column 0\nrepresentative with scalar r^11/(12 f_r), plus d(H) wedge da wedge dv wedge dt.\nIt proves the factor's fibre-wedge constancy and the curve differential\nrelation, keeps both compact rows and explicit orientation, and assumes\nr,z,f_r,Delta nonzero with the curve equation over a characteristic-zero\nQ-algebra field. `sourceScalar_image` identifies the scalar with\n(1/12)*quotientWeight11 in the actual quotient; its trace is zero.\n\nThe physical curve field and compatible ambient Kaehler pullback, a residue\nmap, a general exterior differential and cohomology/connection realization\nare not constructed. Physical Delta nonvanishing is assumed. The optional\nold concrete Ambient wrapper encountered saved instance errors. No primitive,\nclearing, certificate or solve is claimed. See the complete scoped note.\n\n## Executions and review\n\nFinal writer checker-04: 68 declaration audits, one new-module kernel replay,\n19 positive and seven intended mathematical failures; 11 literal packet\nbindings and three mutations; {receipt['elapsed_seconds']:.3f}s. Receipt SHA256\n`{meta['final_focused_receipt_sha256']}`.\n\nSeparate math AI: 10 exact identities/5 mutations (1.725s process), then\n11 formula bindings/3 mutations (0.035s), no Lean. Separate adversarial AI:\nread-only final evidence audit0.063s; no Lean or mathematical execution.\nCoordinator-reported9 identities/6 mutations remain reported, not worker\ncounts. Fourteen Lean development attempts and four focused checker runs,\nincluding failures and prior passing receipts, are preserved. The first\nfigure syntax failure and stale-receipt review rejection are preserved.\n\n```bash\ncd formal\ntimeout 600 python3 -O check_skew_physical_source_normalization.py \\\n  --output-dir results/runs/physical-source-reproduction\n```\n\nUse a new output directory and the pinned Lean4.31.0/Mathlib cache.\nThe new CI step invokes only the new focused checker. Full remote CI is\nthe coordinator's next integration action; no new remote result is claimed.\n\n## Visualization and ledger\n\nThe reproducible PNG/SVG and generator are in\n`results/skew-physical-source-20261023/visualization-02`; its manifest binds\nall inputs and outputs. The PNG was visually inspected. Reproduction:\n\n```bash\npython3 scripts/visualize_skew_physical_source.py \\\n  --receipt results/skew-physical-source-20261023/lean-development/checker-03/validation.json \\\n  --output-dir results/skew-physical-source-20261023/visualization-reproduction\n```\n\nThe figure uses the same frozen mathematical source as checker-04.\nCheckpoint141 is appended after the exact418118-byte parent ledger.\nPosts1–29 and tally29 discussions/1 closed maintenance PR/0 accepted authored\nsolves are unchanged. Only README, LEDGER and the focused CI workflow differ\namong parent-tracked files. Raw historical result files are unchanged in the\nstaged tree. Git's old discussion127 CRLF normalization-only working-tree\nstatus was excluded from staging; no old bytes were normalized.\n'''
 (OUT/'HANDOFF.md').write_text(handoff,encoding='utf-8')
 files=sorted(p for p in OUT.rglob('*') if p.is_file())
 (OUT/'MANIFEST.sha256').write_text(''.join(f'{sha(p.read_bytes())}  {p.relative_to(OUT).as_posix()}\n' for p in files),encoding='utf-8')
 zip_path=OUT/'physical-source-normalization.zip'
 with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(OUT.rglob('*')):
   if p.is_file() and p!=zip_path:z.write(p,p.relative_to(OUT).as_posix())
 with zipfile.ZipFile(zip_path) as z:
  if z.testzip() is not None: raise RuntimeError('ZIP CRC check failed')
  for line in (OUT/'MANIFEST.sha256').read_text().splitlines():
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
