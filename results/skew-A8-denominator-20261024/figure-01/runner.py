"""Fresh bounded process receipts. No symbolic work occurs in this wrapper."""
from pathlib import Path
import datetime, hashlib, json, os, shutil, subprocess, sys, time
script=Path(sys.argv[1]).resolve(); run=Path(sys.argv[2]).resolve()
if run.exists(): raise RuntimeError('Fresh output directory required')
run.mkdir(parents=True); shutil.copyfile(script,run/'source.py')
shutil.copyfile(__file__,run/'runner.py')
start=time.monotonic(); utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
command=[sys.executable,'-O',str(script),str(run/'result')]+sys.argv[3:]
with (run/'stdout.log').open('w',encoding='utf-8') as out,(run/'stderr.log').open('w',encoding='utf-8') as err:
    try:
        process=subprocess.run(command,stdout=out,stderr=err,timeout=60,check=False)
        code=process.returncode; timeout=False
    except subprocess.TimeoutExpired:
        code=124; timeout=True
receipt={'executor':'Pro root constructive lead','command':command,'cwd':str(Path.cwd()),'started_utc':utc,'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'wall_seconds':time.monotonic()-start,'timeout_seconds':60,'exit':code,'timed_out':timeout,'python':sys.version,'PYTHONPATH':os.environ.get('PYTHONPATH'),'files':{p.relative_to(run).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in run.rglob('*') if p.is_file()}}
(run/'execution.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,indent=2)); sys.exit(code)
