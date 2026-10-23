"""Record one bounded Lean development attempt, including source snapshot."""
from pathlib import Path
import datetime, hashlib, json, os, subprocess, sys, time

root = Path(__file__).resolve().parents[3]
formal = root / 'formal'
out = Path(__file__).resolve().parent
label, source = sys.argv[1:]
path = formal / source
raw = path.read_bytes()
(out / (label + '.lean.txt')).write_bytes(raw)
command = ['lake', 'env', 'lean', source]
env = dict(os.environ)
env['ELAN_HOME'] = '/workspace/scratch/b8974c152662/lean-environment'
env['PATH'] = env['ELAN_HOME'] + '/bin:' + env['PATH']
started = time.monotonic()
try:
    p = subprocess.run(command, cwd=formal, env=env, capture_output=True,
                       encoding='utf-8', timeout=120)
    code, log = p.returncode, p.stdout + p.stderr
except subprocess.TimeoutExpired as error:
    code = 124
    def text(value):
        return value.decode('utf-8', errors='replace') if isinstance(value, bytes) else value or ''
    log = text(error.stdout) + text(error.stderr)
(out / (label + '.log')).write_text(log, encoding='utf-8')
record = dict(command=command, cwd='formal', exit_code=code,
              elapsed_seconds=time.monotonic()-started, timeout_seconds=120,
              completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              source=source, source_sha256=hashlib.sha256(raw).hexdigest(),
              source_snapshot=label+'.lean.txt', log=label+'.log',
              log_sha256=hashlib.sha256(log.encode('utf-8')).hexdigest(),
              scope='Development compile only; interruption or failure is not a mathematical result')
(out / (label + '.json')).write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record))
print(log)
sys.exit(code)
