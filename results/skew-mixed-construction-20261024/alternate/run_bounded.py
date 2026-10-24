#!/usr/bin/env python3
"""Fresh, bounded exact-run receipts; all symbolic children have a 60s limit."""
import datetime,hashlib,json,platform,shutil,subprocess,sys,time
from pathlib import Path
target=Path(sys.argv[1]);target.mkdir(parents=True,exist_ok=False)
script=Path(sys.argv[2]).resolve();args=sys.argv[3:]
shutil.copyfile(script,target/'source.py')
cmd=[sys.executable,'-O',str(script),*args]
start=time.monotonic();utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
with (target/'stdout.log').open('wb') as out,(target/'stderr.log').open('wb') as err:
 try:
  p=subprocess.run(cmd,stdout=out,stderr=err,timeout=60,check=False)
  code=p.returncode;timed_out=False
 except subprocess.TimeoutExpired:
  code=124;timed_out=True
receipt={'command':cmd,'cwd':str(Path.cwd()),'started_utc':utc,'elapsed_seconds':time.monotonic()-start,'exit_code':code,'timeout_seconds':60,'timed_out':timed_out,'python_version':platform.python_version(),'executor':'Pro mixed_constructive AI worker','source_sha256':hashlib.sha256(script.read_bytes()).hexdigest(),'stdout_sha256':hashlib.sha256((target/'stdout.log').read_bytes()).hexdigest(),'stderr_sha256':hashlib.sha256((target/'stderr.log').read_bytes()).hexdigest()}
(target/'execution.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,indent=2));sys.exit(code)
