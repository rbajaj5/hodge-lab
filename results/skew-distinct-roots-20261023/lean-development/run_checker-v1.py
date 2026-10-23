#!/usr/bin/env python3
"""Run the focused checker with an overall 600 second wall bound and fresh logs."""
from pathlib import Path
import datetime,json,os,subprocess,sys,time
R=Path(__file__).resolve().parents[3]; F=R/'formal'
sys.path.insert(0,str(F))
from fresh_receipts import fresh_output_dir
label=sys.argv[1]
base=R/'results/skew-distinct-roots-20261023/lean-development'
out=fresh_output_dir(F,'checker-launch',[F/'results/skew-distinct-roots'],['--output-dir',str(base/(label+'-launch'))])
command=[sys.executable,'-O','check_skew_distinct_roots.py','--output-dir',str(base/label)]
env=os.environ.copy();env['ELAN_HOME']='/workspace/scratch/b8974c152662/lean-environment';env['PATH']=env['ELAN_HOME']+'/bin:'+env['PATH']
start=time.monotonic();stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
try:
 p=subprocess.run(command,cwd=F,env=env,capture_output=True,encoding='utf-8',timeout=600)
 stdout,stderr,code=p.stdout,p.stderr,p.returncode
except subprocess.TimeoutExpired as e:
 stdout=e.stdout or '';stderr=e.stderr or '';code=124
 if isinstance(stdout,bytes):stdout=stdout.decode('utf-8',errors='replace')
 if isinstance(stderr,bytes):stderr=stderr.decode('utf-8',errors='replace')
(out/'stdout.log').write_text(stdout,encoding='utf-8');(out/'stderr.log').write_text(stderr,encoding='utf-8')
meta={'label':label,'command':command,'cwd':str(F),'started_utc':stamp,'elapsed_seconds':time.monotonic()-start,'exit_code':code,'timeout_seconds':600,'worker':'distinct_lean'}
(out/'attempt.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
print(json.dumps(meta));print(stdout);print(stderr,file=sys.stderr)
sys.exit(code)
