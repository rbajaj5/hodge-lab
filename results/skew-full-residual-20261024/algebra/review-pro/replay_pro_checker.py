"""Replay unmodified Pro recurrence-checker bytes in an owned minimal mirror."""
import argparse,datetime,hashlib,json,pathlib,shutil,subprocess,sys,time
p=argparse.ArgumentParser();p.add_argument('--pro-root',required=True,type=pathlib.Path);p.add_argument('--connection',required=True,type=pathlib.Path);args=p.parse_args()
root=pathlib.Path(__file__).resolve().parent;mirror=root/'replay-inputs';mirror.mkdir(exist_ok=False)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
relcode=pathlib.Path('results/skew-mixed-construction-20261024/checker/check_first_jet_system.py')
relsystem=pathlib.Path('results/skew-mixed-construction-20261024/alternate/first-jet-result-01/system.json')
relconn=pathlib.Path('results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json')
bindings=[]
for source,rel in [(args.pro_root/relcode,relcode),(args.pro_root/relsystem,relsystem),(args.connection,relconn)]:
 dest=mirror/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
 if sha(source)!=sha(dest):raise ValueError('copy mismatch')
 bindings.append({'source':str(source),'snapshot':str(dest.relative_to(root)),'sha256':sha(dest),'bytes':dest.stat().st_size})
if sha(mirror/relconn)!='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d':raise ValueError('connection pin mismatch')
(root/'input-bindings.json').write_text(json.dumps(bindings,indent=2)+'\n',encoding='utf-8')
run=root/'replay-01';run.mkdir(exist_ok=False);shutil.copyfile(__file__,run/'replay-wrapper-source.py')
cmd=[sys.executable,'-O',str(mirror/relcode),str(run/'result/validation.json')]
start=time.monotonic();utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
try:
 proc=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',timeout=60)
 code=proc.returncode;stdout=proc.stdout;stderr=proc.stderr;status='completed'
except subprocess.TimeoutExpired as ex:
 code=None;status='timeout'
 def txt(x):return x.decode('utf-8',errors='replace') if isinstance(x,bytes) else (x or '')
 stdout=txt(ex.stdout);stderr=txt(ex.stderr)
for name,val in [('stdout.log',stdout),('stderr.log',stderr)]: (run/name).write_text(val,encoding='utf-8')
record={'attribution':'This is an independently executed replay of UNMODIFIED Pro checker code, not newly authored independent mathematical reconstruction. Internal executor label is inherited from that code.',
 'command':cmd,'start_utc':utc,'end_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seconds':time.monotonic()-start,'timeout_seconds':60,'status':status,'exit_code':code,
 'checker_sha256':sha(mirror/relcode),'wrapper_sha256':sha(pathlib.Path(__file__)),'input_bindings':'../input-bindings.json'}
(run/'execution.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print(json.dumps(record,indent=2));print(stdout);print(stderr);sys.exit(0 if code==0 else 1)
