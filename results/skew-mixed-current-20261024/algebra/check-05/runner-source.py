import datetime, hashlib, json, pathlib, shutil, subprocess, sys, time
root=pathlib.Path(__file__).parent
run=root/sys.argv[1]
run.mkdir(exist_ok=False)
if len(sys.argv)!=3:
    raise SystemExit('usage: python run_bounded.py FRESH_RUN_NAME CONNECTION_JSON')
command=[sys.executable,'-O',str(root/'check_sheet_and_t_current.py'),str(run/'validation.json'),'--connection',sys.argv[2]]
shutil.copyfile(root/'check_sheet_and_t_current.py',run/'checker-source.py')
shutil.copyfile(root/'run_bounded.py',run/'runner-source.py')
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
tic=time.monotonic()
try:
    p=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',timeout=60)
    code=p.returncode; stdout=p.stdout; stderr=p.stderr; status='completed'
except subprocess.TimeoutExpired as e:
    code=None; stdout=e.stdout or ''; stderr=e.stderr or ''; status='timeout'
    if isinstance(stdout,bytes):stdout=stdout.decode(errors='replace')
    if isinstance(stderr,bytes):stderr=stderr.decode(errors='replace')
(run/'stdout.log').write_text(stdout,encoding='utf-8')
(run/'stderr.log').write_text(stderr,encoding='utf-8')
record={'command':command,'cwd':str(pathlib.Path.cwd()),'start_utc':start,'end_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seconds':time.monotonic()-tic,'timeout_seconds':60,'exit_code':code,'status':status,'checker_sha256':hashlib.sha256((run/'checker-source.py').read_bytes()).hexdigest(),'runner_sha256':hashlib.sha256((run/'runner-source.py').read_bytes()).hexdigest()}
(run/'execution.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,indent=2));print(stdout);print(stderr)
sys.exit(0 if code==0 else 1)
