"""Fresh-output 60-second checker execution; no symbolic work in this wrapper."""
from pathlib import Path
import datetime, hashlib, json, os, shutil, subprocess, sys, time
base=Path(__file__).resolve().parent
script=Path(sys.argv[1]).resolve(); run=base/sys.argv[2]
if run.exists():raise RuntimeError('Fresh run name required')
run.mkdir(parents=True);shutil.copyfile(script,run/'source.py')
start=time.monotonic();utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
command=[sys.executable,'-O',str(script),str(run/'result'/'validation.json')]
with (run/'stdout.log').open('w',encoding='utf-8') as out,(run/'stderr.log').open('w',encoding='utf-8') as err:
    try:
        proc=subprocess.run(command,stdout=out,stderr=err,timeout=60,check=False)
        code=proc.returncode;timed_out=False
    except subprocess.TimeoutExpired:
        code=124;timed_out=True
receipt={'executor':'mixed_checker AI worker','command':command,'cwd':str(Path.cwd()),'started_utc':utc,'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'wall_seconds':time.monotonic()-start,'timeout_seconds':60,'exit':code,'timed_out':timed_out,'python':sys.version,'source_sha256':hashlib.sha256(script.read_bytes()).hexdigest(),'PYTHONPATH':os.environ.get('PYTHONPATH'),'files':{str(p.relative_to(run)):hashlib.sha256(p.read_bytes()).hexdigest() for p in run.rglob('*') if p.is_file()}}
(run/'execution.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,indent=2));sys.exit(code)
