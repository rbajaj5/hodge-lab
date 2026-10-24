from pathlib import Path
import argparse,datetime,hashlib,json,os,subprocess,time
p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--timeout',type=int,required=True);p.add_argument('cmd',nargs=argparse.REMAINDER);a=p.parse_args()
out=Path(a.out);out.mkdir(parents=True,exist_ok=False);cmd=a.cmd[1:] if a.cmd[:1]==['--'] else a.cmd
start=time.monotonic();utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
try:
 r=subprocess.run(cmd,capture_output=True,timeout=a.timeout);code,stdout,stderr=r.returncode,r.stdout,r.stderr
except subprocess.TimeoutExpired as e:code,stdout,stderr=124,e.stdout or b'',e.stderr or b''
for n,b in [('stdout.log',stdout),('stderr.log',stderr)]: (out/n).write_bytes(b)
j={'executor':'Pro root sole Lean writer','command':cmd,'cwd':os.getcwd(),'started_utc':utc,'elapsed_seconds':time.monotonic()-start,'timeout_seconds':a.timeout,'exit_code':code,'stdout_sha256':hashlib.sha256(stdout).hexdigest(),'stderr_sha256':hashlib.sha256(stderr).hexdigest()}
(out/'execution.json').write_text(json.dumps(j,indent=2)+'\n',encoding='utf-8');print(json.dumps(j));print(stdout.decode('utf-8',errors='replace')[-6000:]);print(stderr.decode('utf-8',errors='replace')[-4000:]);raise SystemExit(code)
