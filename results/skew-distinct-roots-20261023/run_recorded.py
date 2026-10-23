"""Run one bounded command, retaining exact stdout, stderr and metadata.

This runner is for local integration/visualization checks. Lean development
and the focused Lean checker retain their own independent execution logs.
Usage: python3 run_recorded.py NEW_DIRECTORY SECONDS COMMAND [ARG ...]
"""
from pathlib import Path
import datetime
import hashlib
import json
import platform
import subprocess
import sys
import time


def main():
    output = Path(sys.argv[1]).resolve()
    limit = float(sys.argv[2])
    command = sys.argv[3:]
    if not command or not 0 < limit <= 600:
        raise ValueError('A command and a bound in (0,600] seconds are required')
    output.mkdir(parents=True, exist_ok=False)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    before = time.monotonic()
    timed_out = False
    try:
        result = subprocess.run(command, capture_output=True, timeout=limit)
        stdout, stderr, code = result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired as exc:
        stdout, stderr, code = exc.stdout or b'', exc.stderr or b'', None
        timed_out = True
    elapsed = time.monotonic() - before
    (output / 'stdout.log').write_bytes(stdout)
    (output / 'stderr.log').write_bytes(stderr)
    receipt = {
        'executor': 'Pro chat root', 'command': command,
        'cwd': str(Path.cwd()), 'started_utc': started,
        'elapsed_seconds': elapsed, 'timeout_seconds': limit,
        'timed_out': timed_out, 'exit_code': code,
        'python': sys.version, 'platform': platform.platform(),
        'stdout_sha256': hashlib.sha256(stdout).hexdigest(),
        'stderr_sha256': hashlib.sha256(stderr).hexdigest(),
        'runner_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (output / 'execution.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'output': str(output), 'exit_code': code, 'elapsed_seconds': elapsed,
                      'timed_out': timed_out}))
    return 124 if timed_out else code


if __name__ == '__main__':
    raise SystemExit(main())
