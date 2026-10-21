"""Bounded mutation checks and figure generation; preserve completed searches."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'results/skew-base-derivatives'


def main():
    start=time.perf_counter();deadline=start+300
    receipt={'status':'running','total_budget_seconds':300,'operations':[],
             'positive_verification':'first-independent-run.json',
             'searches':'initial-run.json and remaining-runs.json; reused without rerun'}
    env={**os.environ,'PYTHONIOENCODING':'utf-8'}
    jobs=[('drop-base','FAIL: base-only positive control r'),
          ('drop-denominator-derivative','FAIL: denominator differentiation required'),
          ('drop-dual-term','FAIL: dual annihilates full column')]
    try:
        for mutation,message in jobs:
            cmd=[sys.executable,'-O','scripts/check_skew_base_derivatives.py','--mutation',mutation]
            before=time.perf_counter();timeout=min(120,deadline-before)
            if timeout<=0:raise TimeoutError('Total validation budget exceeded')
            p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',env=env,timeout=timeout)
            receipt['operations'].append({'command':cmd,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'seconds':time.perf_counter()-before,'timeout_seconds':timeout})
            if p.returncode!=1 or message not in p.stdout:raise ValueError('Mutation did not fail as required: '+mutation)
        cmd=[sys.executable,'scripts/visualize_skew_base_derivatives.py']
        before=time.perf_counter();timeout=min(60,deadline-before)
        if timeout<=0:raise TimeoutError('Total validation budget exceeded')
        p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',env=env,timeout=timeout)
        receipt['operations'].append({'command':cmd,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'seconds':time.perf_counter()-before,'timeout_seconds':timeout})
        if p.returncode:raise ValueError('Visualization failed')
        receipt['status']='PASS'
    except Exception as error:
        receipt['status']='FAIL';receipt['error']=str(error)
        raise
    finally:
        receipt['seconds']=time.perf_counter()-start
        receipt['script_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'scripts').glob('*skew_base_derivatives.py'))}
        (OUT/'validation.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':receipt['status'],'seconds':receipt['seconds']}))


if __name__=='__main__':main()
