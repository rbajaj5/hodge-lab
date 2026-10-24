from pathlib import Path
import os,sys,json,hashlib,datetime,subprocess,time
root=Path(__file__).resolve().parents[3]
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
command=sys.argv[2:]
p=root/'formal/HodgeLab/OneReflectionSkew/ScalarExtensionTrace.lean'
if p.exists(): (out/'ScalarExtensionTrace.lean.txt').write_bytes(p.read_bytes())
start=time.monotonic(); started=datetime.datetime.now(datetime.timezone.utc).isoformat()
env=dict(os.environ); env['ELAN_HOME']='/workspace/scratch/b8974c152662/lean-environment';env['PATH']=env['ELAN_HOME']+'/bin:'+env['PATH']
try:
 c=subprocess.run(command,cwd=root/'formal',env=env,capture_output=True,timeout=120)
 code,stdout,stderr=c.returncode,c.stdout,c.stderr
except subprocess.TimeoutExpired as e: code,stdout,stderr=124,e.stdout or b'',e.stderr or b''
(out/'stdout.log').write_bytes(stdout);(out/'stderr.log').write_bytes(stderr)
receipt={'executor':'Pro scalar_lean AI worker','command':command,'cwd':'formal','started_utc':started,'elapsed_seconds':time.monotonic()-start,'timeout_seconds':120,'exit_code':code,'files_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}}
(out/'execution.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(stdout.decode(errors='replace'));print(stderr.decode(errors='replace'));print(json.dumps(receipt))
sys.exit(code)
