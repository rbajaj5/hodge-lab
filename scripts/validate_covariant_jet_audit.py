"""Bounded replay plus three nonvacuous failure tests and independent review."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
PACKET=ROOT/'results/covariant-jet-audit'


def main():
    started=time.monotonic()
    records=[]
    expected=[(None,0,'"status": "PASS"'),
              ('cubic-path',1,'actual cubic jet tangent failed'),
              ('j-coefficient',1,'actual full_syzygy RHS failed'),
              ('omit-gdot',1,'differential_first_variation remainder failed')]
    env={**os.environ,'PYTHONIOENCODING':'utf-8'}
    for perturb,code,message in expected:
        argv=[sys.executable,'-O','scripts/audit_covariant_jets.py']
        if perturb: argv+=['--perturb',perturb]
        before=time.monotonic()
        try:
            process=subprocess.run(argv,cwd=ROOT,env=env,capture_output=True,
                text=True,encoding='utf-8',timeout=min(120,600-(before-started)))
        except subprocess.TimeoutExpired as error:
            (PACKET/'interrupted.json').write_text(json.dumps({
                'command':argv,'reason':'timeout','stdout':str(error.stdout),'stderr':str(error.stderr),
                'mathematical_result':None},indent=2)+'\n',encoding='utf-8',newline='\n')
            raise
        rec={'command':argv,'timeout_seconds':120,'returncode':process.returncode,
             'elapsed_seconds':round(time.monotonic()-before,6),
             'stdout':process.stdout,'stderr':process.stderr,'expected_returncode':code,
             'expected_message':message}
        records.append(rec)
        if process.returncode!=code or message not in process.stdout:
            (PACKET/'failed-validation.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8',newline='\n')
            raise RuntimeError('Unexpected replay outcome: '+str(perturb))

    argv=[sys.executable,'-O','scripts/review_covariant_jet_denominators.py']
    before=time.monotonic()
    process=subprocess.run(argv,cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf-8',timeout=60)
    if process.returncode: raise RuntimeError(process.stderr)
    review=json.loads(process.stdout)
    if review['status']!='PASS': raise RuntimeError('Independent review failed')
    (PACKET/'denominator-review.json').write_text(process.stdout,encoding='utf-8',newline='\n')
    records.append({'command':argv,'timeout_seconds':60,'returncode':process.returncode,
        'elapsed_seconds':round(time.monotonic()-before,6),'stdout_file':'denominator-review.json',
        'stderr':process.stderr,'script_sha256':review['script_sha256']})
    (PACKET/'validation.json').write_text(json.dumps({'status':'PASS','cwd':str(ROOT),
        'commands':records,'elapsed_seconds':round(time.monotonic()-started,6),
        'computation_ceiling_seconds':600,'timeouts':0,
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'development_attempts':[{'outcome':'implementation failure before receipt serialization',
          'output':'FAIL: Object of type fmpz is not JSON serializable',
          'correction':'Convert exact monomial exponents to Python integers before JSON output; no mathematical formula changed.',
          'claimed_mathematical_result':None},
         {'outcome':'staging validation detected CRLF/LF byte mismatch',
          'correction':'Use explicit LF for generated receipts and source-checker files, then regenerate affected hash-bound receipts.',
          'claimed_mathematical_result':None}]},indent=2)+'\n',encoding='utf-8',newline='\n')
    print('PASS: baseline, three expected nonzero exits, independent denominator review')


if __name__=='__main__':
    main()
