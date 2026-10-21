"""Bounded positive and deliberately invalid executions, with receipts."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/chi-target-source'


def main():
    started=time.monotonic()
    deadline=started+300
    receipt={'status':'running','total_budget_seconds':300,'operations':[]}
    env={**os.environ,'PYTHONIOENCODING':'utf-8'}
    cases=[([],0,'"status": "PASS"'),(['--mutation','drop-skew'],1,'FAIL: protected coefficient c'),
           (['--mutation','drop-connection'],1,'FAIL: weighted derivative operator'),
           (['--mutation','primitive-sign'],1,'FAIL: constant candidate residual')]
    try:
        for arguments,code,message in cases:
            cmd=[sys.executable,'-O','scripts/check_chi_target_source.py',*arguments]
            t=time.monotonic();timeout=min(120,deadline-t)
            if timeout<=0:raise TimeoutError('Total 300-second budget exhausted')
            p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',env=env,timeout=timeout)
            receipt['operations'].append({'command':cmd,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'seconds':round(time.monotonic()-t,3),'timeout_seconds':timeout})
            if p.returncode!=code or message not in p.stdout:raise RuntimeError('Unexpected outcome: '+repr(arguments))
        cmd=[sys.executable,'scripts/visualize_chi_target_source.py']
        t=time.monotonic();timeout=min(60,deadline-t)
        if timeout<=0:raise TimeoutError('Total 300-second budget exhausted')
        p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',env=env,timeout=timeout)
        receipt['operations'].append({'command':cmd,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'seconds':round(time.monotonic()-t,3),'timeout_seconds':timeout})
        if p.returncode:raise RuntimeError('Visualization failed')
        receipt['status']='PASS'
    except Exception as error:
        receipt['status']='FAIL';receipt['error']=type(error).__name__+': '+str(error)
        raise
    finally:
        receipt['seconds']=round(time.monotonic()-started,3)
        receipt['script_sha256']={name:hashlib.sha256((ROOT/'scripts'/name).read_bytes()).hexdigest() for name in ['check_chi_target_source.py','validate_chi_target_source.py','visualize_chi_target_source.py']}
        (OUT/'validation.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':receipt['status'],'seconds':receipt['seconds'],'operations':len(receipt['operations'])}))


if __name__=='__main__': main()
