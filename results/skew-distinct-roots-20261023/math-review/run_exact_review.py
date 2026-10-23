#!/usr/bin/env python3
"""Run the bounded exact derivation check into a required fresh directory."""

import argparse
import datetime
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time


parser = argparse.ArgumentParser()
parser.add_argument("--output-dir", required=True)
args = parser.parse_args()
output = Path(args.output_dir).resolve()
output.mkdir(parents=True, exist_ok=False)
source = Path(__file__).resolve().with_name("check_elimination.py")
command = [sys.executable, "-O", str(source)]
started = datetime.datetime.now(datetime.timezone.utc)
tick = time.monotonic()
status = "EXECUTION_ERROR"
exit_code = None
try:
    proc = subprocess.run(command, capture_output=True, timeout=30, check=False)
    stdout, stderr = proc.stdout, proc.stderr
    exit_code = proc.returncode
    status = "PASS" if exit_code == 0 else "FAIL"
except subprocess.TimeoutExpired as exc:
    stdout, stderr = exc.stdout or b"", exc.stderr or b""
    status = "TIMEOUT_NOT_A_RESULT"
elapsed = time.monotonic() - tick
(output / "stdout.json").write_bytes(stdout)
(output / "stderr.log").write_bytes(stderr)
receipt = {
    "worker": "distinct_derivation, AI mathematical derivation specialist",
    "status": status,
    "started_utc": started.isoformat(),
    "completed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "command": command,
    "python_version": sys.version,
    "platform": platform.platform(),
    "working_directory": str(Path.cwd()),
    "process_bound_seconds": 30,
    "elapsed_seconds": elapsed,
    "exit_code": exit_code,
    "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
    "stderr_sha256": hashlib.sha256(stderr).hexdigest(),
    "proof_claim": "Exact eliminant identity and three mutation controls only; generic field reasoning is reviewed separately",
}
(output / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(receipt, indent=2, sort_keys=True))
raise SystemExit(0 if status == "PASS" else 1)
