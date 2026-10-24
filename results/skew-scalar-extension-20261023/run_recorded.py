#!/usr/bin/env python3
"""Record one bounded integration command without replacing an old run."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import subprocess
import time


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', required=True)
    p.add_argument('--timeout', type=int, default=120)
    p.add_argument('--executor', default='Pro root integration')
    p.add_argument('command', nargs=argparse.REMAINDER)
    a = p.parse_args()
    if not 0 < a.timeout <= 600:
        raise ValueError('Timeout outside declared bound')
    command = a.command[1:] if a.command[:1] == ['--'] else a.command
    if not command:
        raise ValueError('Missing command')
    out = Path(a.out); out.mkdir(parents=True, exist_ok=False)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    start = time.monotonic()
    try:
        r = subprocess.run(command, capture_output=True, timeout=a.timeout)
        code, stdout, stderr = r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired as e:
        code, stdout, stderr = 124, e.stdout or b'', e.stderr or b''
    (out/'stdout.log').write_bytes(stdout)
    (out/'stderr.log').write_bytes(stderr)
    receipt = {'executor':a.executor, 'command':command, 'cwd':str(Path.cwd()),
               'started_utc':started, 'elapsed_seconds':time.monotonic()-start,
               'timeout_seconds':a.timeout, 'exit_code':code,
               'stdout_sha256':hashlib.sha256(stdout).hexdigest(),
               'stderr_sha256':hashlib.sha256(stderr).hexdigest()}
    (out/'execution.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt))
    print(stdout.decode('utf-8',errors='replace'),end='')
    print(stderr.decode('utf-8',errors='replace'),end='')
    raise SystemExit(code)


if __name__ == '__main__':
    main()
