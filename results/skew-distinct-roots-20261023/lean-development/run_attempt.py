#!/usr/bin/env python3
"""Snapshot and run one bounded Lean development attempt; never overwrite receipts."""
from pathlib import Path
import datetime, hashlib, json, os, subprocess, sys, time
REPO=Path(__file__).resolve().parents[3]
FORMAL=REPO/'formal'
sys.path.insert(0,str(FORMAL))
from fresh_receipts import fresh_output_dir
label=sys.argv[1]
command=sys.argv[2:]
base=REPO/'results/skew-distinct-roots-20261023/lean-development'
out=fresh_output_dir(FORMAL, label, [FORMAL/'results/skew-distinct-roots'], ['--output-dir',str(base/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'-'+label))])
source=FORMAL/'HodgeLab/OneReflectionSkew/GenericDistinctRoots.lean'
if source.exists():
 data=source.read_bytes(); (out/source.name).write_bytes(data)
else: data=b''
env=os.environ.copy(); env['ELAN_HOME']='/workspace/scratch/b8974c152662/lean-environment'; env['PATH']=env['ELAN_HOME']+'/bin:'+env['PATH']
start=time.monotonic(); wall=datetime.datetime.now(datetime.timezone.utc).isoformat(); code=None
try:
 p=subprocess.run(command,cwd=FORMAL,env=env,text=True,encoding='utf-8',capture_output=True,timeout=120)
 stdout,stderr,code=p.stdout,p.stderr,p.returncode
except subprocess.TimeoutExpired as e:
 stdout=e.stdout or ''; stderr=e.stderr or ''
 if isinstance(stdout,bytes): stdout=stdout.decode('utf-8',errors='replace')
 if isinstance(stderr,bytes): stderr=stderr.decode('utf-8',errors='replace')
 code=124
(out/'stdout.log').write_text(stdout,encoding='utf-8'); (out/'stderr.log').write_text(stderr,encoding='utf-8')
meta={'label':label,'command':command,'cwd':str(FORMAL),'started_utc':wall,'elapsed_seconds':time.monotonic()-start,'exit_code':code,'timeout_seconds':120,'source_sha256':hashlib.sha256(data).hexdigest(),'worker':'distinct_lean','ELAN_HOME':env['ELAN_HOME']}
(out/'attempt.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
print(str(out)); print(json.dumps(meta)); print(stdout); print(stderr,file=sys.stderr)
sys.exit(code)
