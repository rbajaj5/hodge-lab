import argparse,datetime,hashlib,json,pathlib,shutil,subprocess,sys,time
p=argparse.ArgumentParser();p.add_argument('run');p.add_argument('--connection',required=True,type=pathlib.Path);p.add_argument('--prior-residue',required=True,type=pathlib.Path);args=p.parse_args()
root=pathlib.Path(__file__).resolve().parent;out=root/args.run;out.mkdir(exist_ok=False)
script=root/'check_v_local.py';shutil.copyfile(script,out/'checker-source.py');shutil.copyfile(__file__,out/'runner-source.py')
cmd=[sys.executable,'-O',str(script),'--connection',str(args.connection),'--prior-residue',str(args.prior_residue),'--output',str(out/'validation.json')]
start=time.monotonic();utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
try:
 p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',timeout=60);code=p.returncode;stdout=p.stdout;stderr=p.stderr;status='completed'
except subprocess.TimeoutExpired as ex:
 code=None;status='timeout'
 def text(x):return x.decode('utf-8',errors='replace') if isinstance(x,bytes) else (x or '')
 stdout=text(ex.stdout);stderr=text(ex.stderr)
for name,value in [('stdout.log',stdout),('stderr.log',stderr)]: (out/name).write_text(value,encoding='utf-8')
record={'command':cmd,'start_utc':utc,'end_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seconds':time.monotonic()-start,'timeout_seconds':60,'status':status,'exit_code':code,'checker_sha256':hashlib.sha256((out/'checker-source.py').read_bytes()).hexdigest()}
(out/'execution.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print(json.dumps(record,indent=2));print(stdout);print(stderr);sys.exit(0 if code==0 else 1)
