"""One bounded reconstruction, elimination-free replay, and scientific figure."""
from pathlib import Path
import datetime
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/one-reflection-skew-hessian-source'


def main():
    if not __debug__:
        raise RuntimeError('Run without -O; arithmetic helpers require assertions')
    report = {'status': 'RUNNING', 'python': sys.version, 'platform': platform.platform(),
              'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'time_limit_seconds_per_command': 60, 'memory_limit': 'No additional process cap',
              'executions': [], 'versions': {n: importlib.metadata.version(n)
                                            for n in ('numpy', 'matplotlib')}}
    env = dict(os.environ); env.pop('PYTHONOPTIMIZE', None)
    for script, standard_library in [('hessian_source.py', True), ('hessian_source_replay.py', True),
                                     ('plot_hessian_source.py', False)]:
        relative = 'experiments/skew_audit/' + script
        cmd = [sys.executable, '-B'] + (['-S'] if standard_library else []) + [relative]
        start = time.perf_counter()
        item = {'command': cmd, 'script_lf_sha256': hashlib.sha256(
            (ROOT / relative).read_bytes().replace(b'\r\n', b'\n')).hexdigest()}
        try:
            p = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True,
                               encoding='utf-8', timeout=60)
            item.update(exit_code=p.returncode, stdout=p.stdout, stderr=p.stderr,
                        status='PASS' if p.returncode == 0 else 'FAIL')
        except subprocess.TimeoutExpired as error:
            item.update(status='TIMEOUT', stdout=str(error.stdout), stderr=str(error.stderr))
        item['elapsed_seconds'] = time.perf_counter() - start
        report['executions'].append(item)
        if item['status'] != 'PASS':
            report['status'] = item['status']
            (OUT / 'validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
            raise RuntimeError('Bounded stage failed: ' + script)
    report['status'] = 'PASS'
    report['completed_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    report['output_lf_sha256'] = {name: hashlib.sha256((OUT / name).read_bytes().replace(b'\r\n', b'\n')).hexdigest()
                                  for name in ('inputs.json', 'reconstruction.json', 'replay.json')}
    (OUT / 'validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'status': 'PASS', 'commands': len(report['executions']),
                      'receipt': str(OUT / 'validation.json')}))


if __name__ == '__main__':
    main()
