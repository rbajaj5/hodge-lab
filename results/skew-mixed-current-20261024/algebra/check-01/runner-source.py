import datetime, json, pathlib, subprocess, sys, time
root=pathlib.Path(__file__).parent
run=root/sys.argv[1]
run.mkdir(exist_ok=False)
command=[sys.executable,'-O',str(root/'check_sheet_and_t_current.py'),str(run/'validation.json')]
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
tic=time.monotonic()
try:
    p=subprocess.run(command,capture_output=True,text=True,timeout=60)
    code=p.returncode; stdout=p.stdout; stderr=p.stderr; status='completed'
except subprocess.TimeoutExpired as e:
    code=None; stdout=e.stdout or ''; stderr=e.stderr or ''; status='timeout'
    if isinstance(stdout,bytes):stdout=stdout.decode(errors='replace')
    if isinstance(stderr,bytes):stderr=stderr.decode(errors='replace')
(run/'stdout.log').write_text(stdout)
(run/'stderr.log').write_text(stderr)
record={'command':command,'cwd':str(pathlib.Path.cwd()),'start_utc':start,'end_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seconds':time.monotonic()-tic,'timeout_seconds':60,'exit_code':code,'status':status}
(run/'execution.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2));print(stdout);print(stderr)
sys.exit(0 if code==0 else 1)
