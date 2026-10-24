#!/usr/bin/env python3
"""Read-only final source/receipt audit; executes no Lean or mathematics."""
from pathlib import Path
import argparse,datetime,hashlib,json,re,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[3]
MODULE='formal/HodgeLab/OneReflectionSkew/PhysicalTraceBridge.lean'
PREFIX='HodgeLab.OneReflectionSkew.PhysicalTraceBridge.'
PARENT='2bbbaa312642822c28483ba85cbbccf0af97d6dc'
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
 input_path=ROOT/'formal/results/skew-physical-trace/inputs.json'
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
  snapshot=receipt.parent/'source-snapshot'/(name+'.txt')
  require(snapshot.is_file() and sha(snapshot)==expected,'Missing or changed source snapshot: '+name)
 for name,entry in data.get('pinned_files',{}).items():
  expected=entry['sha256'] if isinstance(entry,dict) else entry
  target=path_for(name);require(sha(target)==expected,'Pinned input differs: '+name);checked[target.relative_to(ROOT).as_posix()]=expected
 replay_source=ROOT/'formal/ReplaySkewPhysicalTrace.lean'
 replay_text=replay_source.read_text(encoding='utf-8')
 require(re.findall(r'replayFromImports\s+`([A-Za-z0-9_.]+)',replay_text)==[PREFIX[:-1]],'Kernel replay source does not exclusively replay the new module')
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
 records=data.get('commands') or json.loads((receipt.parent/'commands.json').read_text(encoding='utf-8'))
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
 require('PASS '+PREFIX[:-1] in (receipt.parent/replay[0]['log']).read_text(encoding='utf-8'),'Replay marker missing')
 parent=subprocess.check_output(['git','show',PARENT+':LEDGER.md'],cwd=ROOT)
 current=(ROOT/'LEDGER.md').read_bytes()
 require(current.startswith(parent),'Parent ledger prefix changed')
 require(len(parent)==440921 and hashlib.sha256(parent).hexdigest()=='1da42f452082925e8d6983c37276a062f336fb4e0a0ca02920403e377fa2ec9f','Wrong parent ledger')
 positive_source=receipt.parent/'positive-controls.lean.txt'
 require(positive_source.is_file(),'Missing positive control source')
 positive_count=len(re.findall(r'^example',positive_source.read_text(encoding='utf-8'),re.M))
 require(data.get('positive_controls')==positive_count,'Positive count differs from actual saved examples')
 for label in negatives:
  require((receipt.parent/(label+'.lean.txt')).is_file(),'Missing intended-failure source: '+label)
 require(data.get('negative_controls')==len(negatives),'Negative count differs')
 public_count=data.get('new_public_declarations_audited')
 require(public_count==len(names),'Public declaration count differs')
 development=[]
 devroot=ROOT/'results/skew-physical-trace-20261024/lean-development'
 failure_notes={}
 for note in [devroot/'initial-path-error.json',ROOT/'results/skew-physical-trace-20261024/bootstrap/environment-interruption.json']:
  require(note.is_file(),'Missing infrastructure failure note: '+str(note))
  json.loads(note.read_text(encoding='utf-8'))
  failure_notes[note.relative_to(ROOT).as_posix()]=sha(note)
 for execution in sorted(devroot.glob('attempt-*/run/execution.json')):
  attempt=execution.parent.parent.name
  d=json.loads(execution.read_text(encoding='utf-8'))
  require(d['timeout_seconds']<=120,'Development Lean bound exceeded: '+attempt)
  stream_hashes={}
  for stream in ['stdout','stderr']:
   target=execution.parent/(stream+'.log')
   require(sha(target)==d[stream+'_sha256'],'Development stream differs: '+str(target))
   stream_hashes[stream]=sha(target)
  snapshot=execution.parent.parent/'source.lean.txt'
  if attempt=='attempt-01':
   require(not snapshot.exists(),'Path-failure attempt unexpectedly has a mathematical source snapshot')
   snapshot_hash=None
  else:
   require(snapshot.is_file(),'Missing development source: '+attempt)
   snapshot.read_text(encoding='utf-8')
   snapshot_hash=sha(snapshot)
  development.append({'attempt':attempt,'execution':execution.relative_to(ROOT).as_posix(),'execution_sha256':sha(execution),'source_sha256':snapshot_hash,'stream_sha256':stream_hashes,'exit_code':d['exit_code'],'elapsed_seconds':d['elapsed_seconds'],'timeout_seconds':d['timeout_seconds']})
 require(len(development)==12,'Expected all12 frozen development attempts')
 require(development[-1]['source_sha256']==sha(ROOT/MODULE) and development[-1]['exit_code']==0,'Frozen final attempt differs from current source')
 earlier_checks=[]
 for earlier in sorted(devroot.glob('checker-*/validation.json')):
  if earlier.resolve()==receipt.resolve():continue
  d=json.loads(earlier.read_text(encoding='utf-8'))
  old_count=0
  for rec in d.get('commands',[]):
   for key,hkey in [('stdout','stdout_sha256'),('stderr','stderr_sha256')]:
    require(sha(earlier.parent/rec[key])==rec[hkey],'Earlier checker stream differs: '+rec['label'])
    old_count+=1
   log=(earlier.parent/rec['log']).read_bytes().replace(b'\r\n',b'\n')
   require(hashlib.sha256(log).hexdigest()==rec['log_lf_sha256'],'Earlier combined log differs: '+rec['label'])
   old_count+=1
  prior_inputs=earlier.parent/'source-inputs.json'
  prior_source_count=0
  if prior_inputs.exists():
   prior_data=json.loads(prior_inputs.read_text(encoding='utf-8'))
   for name,expected in prior_data['source_sha256'].items():
    require(sha(earlier.parent/'source-snapshot'/(name+'.txt'))==expected,'Earlier checker source snapshot differs: '+name)
    prior_source_count+=1
  earlier_checks.append({'receipt':earlier.relative_to(ROOT).as_posix(),'sha256':sha(earlier),'status':d['status'],'error':d.get('error'),'command_stream_hashes_checked':old_count,'source_snapshot_hashes_checked':prior_source_count})
 result={'status':'PASS_SAVED_EVIDENCE_AUDIT','executor':'Pro curve_evidence_review read-only AI reviewer','started_utc':began,'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-start,'receipt':a.receipt,'receipt_sha256':sha(receipt),'module':MODULE,'module_sha256':sha(ROOT/MODULE),'source_context_hashes':len(checked),'command_stream_hashes':count,'public_declarations':len(names),'positive_controls':data.get('positive_controls'),'intended_false_goals':len(negatives),'negative_labels':negatives,'new_modules_replayed':1,'parent_ledger_bytes':len(parent),'parent_ledger_prefix_exact':True,'reviewer_Lean_commands':0,'reviewer_symbolic_mathematics':0,'scope':'Saved execution evidence and current source bindings; not an independent Lean or mathematical rerun','checked_source_sha256':checked,'development_attempts':development,'infrastructure_failure_notes_sha256':failure_notes,'earlier_checker_evidence':earlier_checks}
 (out/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
