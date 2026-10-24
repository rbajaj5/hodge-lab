import argparse,datetime,hashlib,json,pathlib,shutil,subprocess,sys,time
p=argparse.ArgumentParser();p.add_argument('run');p.add_argument('--repo',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parents[3]);args=p.parse_args()
root=pathlib.Path(__file__).resolve().parent;out=root/args.run;out.mkdir(exist_ok=False)
script=root/'check_order5.py'
shutil.copyfile(script,out/'checker-source.py');shutil.copyfile(__file__,out/'runner-source.py')
command=[sys.executable,'-O',str(script),'--repo',str(args.repo),'--output',str(out/'result')]
begin=datetime.datetime.now(datetime.timezone.utc).isoformat();start=time.monotonic()
try:
    run=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',timeout=60)
    status='completed';code=run.returncode;stdout=run.stdout;stderr=run.stderr
except subprocess.TimeoutExpired as ex:
    status='timeout';code=None
    def decode(x):return x.decode('utf-8',errors='replace') if isinstance(x,bytes) else (x or '')
    stdout=decode(ex.stdout);stderr=decode(ex.stderr)
for name,data in [('stdout.log',stdout),('stderr.log',stderr)]: (out/name).write_text(data,encoding='utf-8')
record={'command':command,'start_utc':begin,'end_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seconds':time.monotonic()-start,'timeout_seconds':60,'status':status,'exit_code':code,'checker_sha256':hashlib.sha256((out/'checker-source.py').read_bytes()).hexdigest(),'runner_sha256':hashlib.sha256((out/'runner-source.py').read_bytes()).hexdigest()}
(out/'execution.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,indent=2));print(stdout);print(stderr);sys.exit(0 if code==0 else 1)
