"""Fresh 60-second checker receipt; no mathematics in the wrapper."""
from pathlib import Path
import datetime, hashlib, json, os, shutil, subprocess, sys, time
base=Path(__file__).resolve().parent; script=Path(sys.argv[1]).resolve(); run=base/sys.argv[2]
if run.exists(): raise RuntimeError('Fresh run directory required')
run.mkdir(parents=True); shutil.copyfile(script,run/'source.py'); shutil.copyfile(__file__,run/'runner.py')
start=time.monotonic(); stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
command=[sys.executable,'-O',str(script),str(run/'result')]+sys.argv[3:]
with (run/'stdout.log').open('w',encoding='utf-8') as out, (run/'stderr.log').open('w',encoding='utf-8') as err:
    try:
        done=subprocess.run(command,stdout=out,stderr=err,timeout=60,check=False)
        code=done.returncode; timed_out=False
    except subprocess.TimeoutExpired:
        code=124; timed_out=True
receipt={'executor':'a6_denominator_checker AI worker','command':command,'cwd':str(Path.cwd()),'started_utc':stamp,'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'wall_seconds':time.monotonic()-start,'timeout_seconds':60,'exit':code,'timed_out':timed_out,'python':sys.version,'PYTHONPATH':os.environ.get('PYTHONPATH'),'files':{p.relative_to(run).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in run.rglob('*') if p.is_file()}}
(run/'execution.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,indent=2));sys.exit(code)
