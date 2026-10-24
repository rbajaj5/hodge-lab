#!/usr/bin/env python3
"""Read-only final source/receipt audit; executes no Lean or mathematics."""
from pathlib import Path
import argparse,datetime,hashlib,json,re,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[3]
MODULE='formal/HodgeLab/OneReflectionSkew/PhysicalCurveRealization.lean'
PREFIX='HodgeLab.OneReflectionSkew.PhysicalCurveRealization.'
PARENT='e2182223a0395cfb758a2ee09e304eb940b7a67a'
def require(ok,message):
 if not ok: raise RuntimeError(message)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def path_for(name):
 p=ROOT/name
 if not p.is_file():p=ROOT/'formal'/name
 require(p.is_file(),'Missing named source: '+name)
 require(p.resolve().is_relative_to(ROOT.resolve()),'Escaping source path: '+name)
 return p

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--receipt',required=True);p.add_argument('--output-dir',required=True);a=p.parse_args()
 out=ROOT/a.output_dir;out.mkdir(parents=True,exist_ok=False)
 start=time.monotonic();began=datetime.datetime.now(datetime.timezone.utc).isoformat()
 receipt=ROOT/a.receipt;data=json.loads(receipt.read_text(encoding='utf-8'))
 require(data['status']=='PASS','Final receipt is not PASS')
 checked={}
 input_path=ROOT/'formal/results/skew-physical-curve/inputs.json'
 require(sha(input_path)==data['inputs_sha256'],'Current input manifest differs from receipt')
 checked[input_path.relative_to(ROOT).as_posix()]=sha(input_path)
 ref=data['source_pins_manifest'];manifest_path=path_for(ref['path'])
 require(sha(manifest_path)==ref['sha256'],'Source-pin manifest differs from receipt')
 checked[manifest_path.relative_to(ROOT).as_posix()]=sha(manifest_path)
 manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
 require(manifest['parent']==PARENT,'Source-pin parent differs')
 require(manifest['upstream']=='e96be434bd55d6013d7a5854732cb317ca0e43e7','Source-pin upstream differs')
 require(manifest['files']==data['pinned_files'],'Receipt pinned inventory differs from manifest')
 for name,expected in data['source_sha256'].items():
  target=path_for(name);require(sha(target)==expected,'Current source differs from saved receipt: '+name);checked[target.relative_to(ROOT).as_posix()]=expected
 for name,entry in data.get('pinned_files',{}).items():
  expected=entry['sha256'] if isinstance(entry,dict) else entry
  target=path_for(name);require(sha(target)==expected,'Pinned input differs: '+name);checked[target.relative_to(ROOT).as_posix()]=expected
 source=(ROOT/MODULE).read_text(encoding='utf-8')
 require(not re.search(r'\b(sorry|admit|axiom|native_decide)\b',source),'Forbidden proof token in new source')
 names=re.findall(r'^(?:@\[[^\n]*\]\s*)?(?:(?:noncomputable|local|private)\s+)*(?:def|abbrev|theorem|lemma|instance)\s+(\w+)',source,re.M)
 names=[PREFIX+n for n in names]
 require(len(names)==len(set(names)),'Duplicate declared names')
 axioms=data.get('declaration_axioms',data.get('axioms'))
 require(isinstance(axioms,dict),'Missing per-declaration axiom inventory')
 require(set(names)==set(axioms),'Source declarations differ from audited names: '+repr(set(names)^set(axioms)))
 require(all(set(v)<={'propext','Classical.choice','Quot.sound'} for v in axioms.values()),'Disallowed axiom dependency')
 require(data.get('new_modules_replayed')==1,'Expected exactly one new-module replay')
 records=data.get('commands') or json.loads((receipt.parent/'commands.json').read_text())
 count=0;negatives=[];positives=[]
 for rec in records:
  for key,hashkey in [('stdout','stdout_sha256'),('stderr','stderr_sha256')]:
   if key in rec:
    f=receipt.parent/rec[key];require(sha(f)==rec[hashkey],'Command stream hash mismatch: '+str(f));count+=1
  if 'log' in rec and 'log_lf_sha256' in rec:
   f=receipt.parent/rec['log'];value=f.read_bytes().replace(b'\r\n',b'\n')
   require(hashlib.sha256(value).hexdigest()==rec['log_lf_sha256'],'Combined log hash mismatch: '+str(f));count+=1
  require(rec['exit_code']!=124,'Timeout incorrectly included in passing checker')
  if rec.get('expected_failure'):
   log=(receipt.parent/rec['log']).read_text(encoding='utf-8')
   require(rec['exit_code']!=0 and log.count('error:')==1 and 'unsolved goals' in log and '⊢ False' in log,'Unintended negative control failure: '+rec['label'])
   require('failed to synthesize' not in log and 'unknown' not in log.lower(),'Negative failed for API/type error')
   negatives.append(rec['label'])
  else:require(rec['exit_code']==0,'Unexpected command failure: '+rec['label']);positives.append(rec['label'])
  require(rec.get('bound_seconds',120)<=120,'Lean/command bound exceeds declared limit')
 for module,expected in data.get('artifact_sha256',{}).items():
  artifact=ROOT/'formal/.lake/build/lib/lean'/(module.replace('.','/')+'.olean')
  require(sha(artifact)==expected,'Compiled artifact differs from receipt: '+module)
 replay=[rec for rec in records if rec['label']=='kernel-replay']
 require(len(replay)==1,'Expected one kernel replay record')
 require('PASS '+PREFIX[:-1] in (receipt.parent/replay[0]['log']).read_text(),'Replay marker missing')
 parent=subprocess.check_output(['git','show',PARENT+':LEDGER.md'],cwd=ROOT)
 current=(ROOT/'LEDGER.md').read_bytes()
 require(current.startswith(parent),'Parent ledger prefix changed')
 require(len(parent)==430885 and hashlib.sha256(parent).hexdigest()=='f4e1e853360368889cd83be8536d4f0c509a73464d391311c91639c326abbc66','Wrong parent ledger')
 require(data.get('negative_controls')==len(negatives),'Negative count differs')
 public_count=data.get('new_public_declarations_audited')
 require(public_count==len(names),'Public declaration count differs')
 result={'status':'PASS_SAVED_EVIDENCE_AUDIT','executor':'Pro curve_evidence_review read-only AI reviewer','started_utc':began,'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-start,'receipt':a.receipt,'receipt_sha256':sha(receipt),'module':MODULE,'module_sha256':sha(ROOT/MODULE),'source_context_hashes':len(checked),'command_stream_hashes':count,'public_declarations':len(names),'positive_controls':data.get('positive_controls'),'intended_false_goals':len(negatives),'negative_labels':negatives,'new_modules_replayed':1,'parent_ledger_bytes':len(parent),'parent_ledger_prefix_exact':True,'reviewer_Lean_commands':0,'reviewer_symbolic_mathematics':0,'scope':'Saved execution evidence and current source bindings; not an independent Lean or mathematical rerun','checked_source_sha256':checked}
 (out/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
