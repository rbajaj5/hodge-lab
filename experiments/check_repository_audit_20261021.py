"""Reproduce the focused October21 audit corrections and refresh their figures.

Does not rebuild Lean, repeat low-degree elimination, or contact GitHub.
Run with repository plotting dependencies installed, without Python -O.
"""
from pathlib import Path
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/repository-audit-20261021'
REPORT={'schema':'hodge-lab-focused-audit-v1','status':'RUNNING','commands':[],
        'audit_base':'09539bb5151f918f73ec9fd4b9faba781959c436',
        'upstream_observed_head':'dda4c5e72eeea8cfd52dd6e731e90031884f32fc',
        'not_executed':['Fresh Lean compilation/replay','Full degree0–6 elimination','Full degree7 added-block reconstruction'],
        'python':sys.version,'platform':platform.platform()}

def sha(p):return hashlib.sha256(p.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
def checkpoint():
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'validation.json').write_text(json.dumps(REPORT,indent=2)+'\n',encoding='utf-8',newline='\n')
def run(label,command,bound=180,expected_failure=False):
    rec={'label':label,'command':command,'bound_seconds':bound,'expected_failure':expected_failure}
    REPORT['commands'].append(rec);start=time.perf_counter();text=''
    try:
        p=subprocess.run(command,cwd=ROOT,text=True,encoding='utf-8',capture_output=True,timeout=bound)
        text=p.stdout+p.stderr;rec['exit_code']=p.returncode
        if expected_failure:
            assert p.returncode!=0 and 'ValueError:' in text,text
        else:assert p.returncode==0,text
        rec['status']='PASS'
    except subprocess.TimeoutExpired:
        rec['status']='TIMEOUT';raise
    except BaseException:
        rec.setdefault('status','FAIL');raise
    finally:
        path=OUT/(label+'.log');path.write_text(text,encoding='utf-8',newline='\n')
        rec.update(elapsed_seconds=round(time.perf_counter()-start,3),log=path.name,log_lf_sha256=sha(path))
        checkpoint()
    print(json.dumps(rec),flush=True)

def main():
    if not __debug__:
        raise RuntimeError('Run without -O.')
    import matplotlib,numpy,sympy
    REPORT['packages']={'matplotlib':matplotlib.__version__,'numpy':numpy.__version__,'sympy':sympy.__version__}
    files=['experiments/check_one_reflection_skew_hessian.py','experiments/check_one_reflection_skew_line.py',
           'experiments/one_reflection_skew_koszul_homology.py','experiments/one_reflection_skew_pilot.py',
           'experiments/check_repository_audit_20261021.py','experiments/necessary_koszul_complex.py',
           'experiments/one_reflection_skew_degree6.py','experiments/fresh_instance_e1.py',
           'experiments/fresh_instance_degree6.py','experiments/one_reflection_skew_degree7.py',
           'results/one-reflection-skew-degree6/one-reflection-skew/degree-6-e2.json']
    REPORT['source_lf_sha256']={f:sha(ROOT/f) for f in files};checkpoint()
    run('corrected-hessian',[sys.executable,'-S','experiments/check_one_reflection_skew_hessian.py'],30)
    run('line-valid',[sys.executable,'experiments/check_one_reflection_skew_line.py'],30)
    source=(ROOT/'experiments/check_one_reflection_skew_line.py').read_text(encoding='utf-8')
    for label,before,after in [('line','6*s + 2*t','5*s + 2*t'),('source','\nA = X0**3 * Y0**3','\nA = 2 * X0**3 * Y0**3')]:
        assert source.count(before)==1
        changed=source.replace(before,after)
        with tempfile.TemporaryDirectory(prefix='hodge-audit-') as folder:
            p=Path(folder)/'changed.py';p.write_text(changed,encoding='utf-8',newline='\n')
            run('reject-'+label,[sys.executable,'-O',str(p)],30,True)
    run('koszul-strands',[sys.executable,'experiments/one_reflection_skew_koszul_homology.py'],180)
    from fractions import Fraction
    from itertools import combinations_with_replacement
    import necessary_koszul_complex as kh
    all_quadrics=[{pair:Fraction(1)} for pair in combinations_with_replacement(range(7),2)]
    model=kh.complex_at(all_quadrics,list(range(7)),3)
    assert model['homology'][1]==112
    REPORT['added_block_figure_control']={'model':'All 28 quadrics in seven variables',
        'degree':3,'H1':112,'scope':'Abstract full quadratic ideal; not a replay of the physical added block'}
    import one_reflection_skew_pilot as pilot
    path=ROOT/'results/one-reflection-skew-pilot/report.json'
    report=json.loads(path.read_text(encoding='utf-8'))
    baseline_hash=hashlib.sha256(json.dumps(report['lowDegreeBaseline'],sort_keys=True).encode()).hexdigest()
    assert baseline_hash=='5d8a46eea9a52028c52a387368af207ac65fd153abed82c0ebc2fd62293baa74', 'Inherited elimination changed from audited09539bb'
    vars6,base,skew,F,A=pilot.make_one_reflection_skew()
    symbolic=pilot.check_symmetries_and_cubic_obstruction(vars6,base,skew,F,A)
    report['symmetryAndBinaryCubicAudit']=symbolic
    report['audit20261021']={'rerun':'Symbolic exchange/Cramer/Cayley/Hessian identities and boundary counterexample; figure redraw',
        'not_rerun':'Curation/smoothness and full low-degree elimination; inherited unchanged from original receipt',
        'inherited_low_degree_sorted_json_sha256':baseline_hash}
    path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    pilot.render_figures(report)
    REPORT['symbolic_pilot']={'status':'PASS','hessian_det_scale':4,'exchange_order':2,'disc_h_boundary':81,
                               'inherited_low_degree_sorted_json_sha256':baseline_hash}
    outputs=['results/one-reflection-skew-koszul/summary.json','results/one-reflection-skew-pilot/report.json',
             'results/repository-audit-20261021/corrected-hessian-validation.json']
    REPORT['output_lf_sha256']={f:sha(ROOT/f) for f in outputs}
    REPORT['figure_raw_sha256']={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
        for folder,stem in [('one-reflection-skew-koszul','one-reflection-skew-koszul-homology'),('one-reflection-skew-pilot','one-reflection-skew-audit')]
        for p in [ROOT/'results'/folder/(stem+suffix) for suffix in ['.png','.svg']]}
    assert all(sha(ROOT/f)==h for f,h in REPORT['source_lf_sha256'].items())
    REPORT['status']='PASS';checkpoint()
    print('PASS: focused audit corrections; no fresh Lean or full elimination replay')

if __name__=='__main__':
    try:main()
    except BaseException as error:
        REPORT.update(status='FAIL',error=type(error).__name__+': '+str(error));checkpoint();raise
