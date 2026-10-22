"""Bounded algebraic residue coefficient proof check, reusing checkpoints124/125.

python3 -O check_skew_residue.py; cached Lean dependencies, no network.
120 seconds per command and 600 seconds total. Standard-library exact arithmetic.
"""
from fractions import Fraction as Q
from itertools import permutations
from pathlib import Path
import datetime, hashlib, json, re, sys, time
import check_skew_extension as util
import skew_residue_algebra as algebra

ROOT = Path(__file__).resolve().parent
OUT = ROOT/'results/skew-residue'
PREFIX = 'HodgeLab.OneReflectionSkew.'
MODULES = [PREFIX+'NormalChart', PREFIX+'ResidueNormalization']
NORMAL_NAMES = ['chartPolynomial_eval', 'chartPolynomial_pderiv', 'normalDerivative_eq', 'coefficientMatrix_det', 'gradient_volume_coefficient', 'coefficientMatrix_scaled', 'base_covector_vanishes', 'normalJacobian_entries', 'normalJacobian_det', 'normalDerivative_ne_zero_iff', 'normalJacobian_ne_zero_iff']
RESIDUE_NAMES = ['cubic_derivative_zero', 'chartDenominator_derivative', 'beta_denominator_derivative', 'beta_derivative', 'ambient_reduction', 'normalizedPoleCoefficient_eq', 'simple_pole_factorization', 'ambient_normal_factorization']
NAMES = [PREFIX+'NormalChart.'+n for n in NORMAL_NAMES]+[PREFIX+'ResidueNormalization.'+n for n in RESIDUE_NAMES]
SOURCES = ['lean-toolchain','lakefile.toml','lake-manifest.json','check_skew_extension.py',
           'check_skew_residue.py','AuditSkewResidue.lean','ReplaySkewResidue.lean','check_skew_volume.py','skew_residue_algebra.py']+[m.replace('.','/')+'.lean' for m in MODULES]
require, digest = util.require, util.digest

def write(name, value):
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')

def main():
    OUT.mkdir(parents=True,exist_ok=True);util.OUT,util.START,util.RECORDS=OUT,time.monotonic(),[]
    write('validation.json',{'status':'IN_PROGRESS'})
    hashes={s:digest(ROOT/s) for s in SOURCES}
    prior_path=ROOT/'results/skew-volume/validation.json'
    prior_hash=digest(prior_path);prior=json.loads(prior_path.read_text(encoding='utf-8'))
    require(prior['status']=='PASS','Completed volume proof receipt missing')
    reused=dict(prior['reused_source_lf_sha256'])
    reused.update({n:h for n,h in prior['source_lf_sha256'].items() if n.startswith('HodgeLab/') and n.endswith('.lean')})
    for n,h in reused.items():require(digest(ROOT/n)==h,'Reused proof changed '+n)
    input_hashes={'inputs.json':digest(OUT/'inputs.json')}
    for p in json.loads((OUT/'inputs.json').read_text(encoding='utf-8'))['pins']:
        input_hashes[p['path']]=digest(ROOT.parent/p['path'])
        if p['path'] in prior['input_lf_sha256']:
            require(input_hashes[p['path']]==prior['input_lf_sha256'][p['path']],'Target changed since volume proof')
    for n in SOURCES:
        if n.endswith('.lean'):require(not re.search(r'\b(sorry|admit|axiom|native_decide)\b',(ROOT/n).read_text(encoding='utf-8')),'Unproved token '+n)
    algebra.reconstruct(OUT)
    version=util.run('version',['lake','env','lean','--version']);require('version 4.31.0,' in version,'Wrong Lean')
    manifest=json.loads((ROOT/'lake-manifest.json').read_text(encoding='utf-8'));rev=next(p['rev'] for p in manifest['packages'] if p['name']=='mathlib')
    require(util.run('mathlib-head',['git','-C','.lake/packages/mathlib','rev-parse','HEAD']).strip()==rev,'Mathlib mismatch')
    util.run('build',['lake','build',*MODULES])
    audit=util.run('axioms',['lake','env','lean','AuditSkewResidue.lean'])
    axioms={n:[x.strip() for x in a.split(',') if x.strip()] for n,a in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]",audit)}
    for n in re.findall(r"'([^']+)' does not depend on any axioms",audit):axioms[n]=[]
    require(set(axioms)==set(NAMES),'Missing/unexpected theorem audits')
    require(all(set(a)<={'propext','Classical.choice','Quot.sound'} for a in axioms.values()),'Unexpected axiom')
    replay=util.run('kernel-replay',['lake','env','lean','ReplaySkewResidue.lean'])
    require(all('PASS '+m in replay for m in MODULES),'Missing replay marker')
    controls={
        'wrong-wedge-sign': ('(coefficientMatrix (![0,0,0,0,1] : Fin 5 → ℚ)).det','1','-1','rw [coefficientMatrix_det]\n    rfl'),
        'wrong-residue-sign': ('72 * normalizedPoleCoefficient (1 : ℚ) 0 0 0 1','5','-5','rw [normalizedPoleCoefficient_eq _ _ _ _ _ (by norm_num)]\n    norm_num'),
        'missing-normal-factor-six': ('72 * normalizedPoleCoefficient (1 : ℚ) 0 0 0 1','5','30','rw [normalizedPoleCoefficient_eq _ _ _ _ _ (by norm_num)]\n    norm_num'),
        'omitted-z-power-derivative': ('36 * (uCoefficient (1 : ℚ) 0 0 0 1 - poleNumerator 1 1 / chartDenominator 1 0 0 0 1)','-7','-2','norm_num [uCoefficient, poleNumerator, chartDenominator, cubic, aCoeff, bCoeff, cCoeff, dCoeff]'),
        'invalid-normal-chart': ('normalDerivative (1 : ℚ) 0 0 0 0','0',None,'rw [normalDerivative_eq]\n    norm_num')}
    header=('import HodgeLab.OneReflectionSkew.ResidueNormalization\nopen HodgeLab.OneReflectionSkew.ChartSubstitution\n'
            'open HodgeLab.OneReflectionSkew.NormalChart\nopen HodgeLab.OneReflectionSkew.VolumeDensity\n'
            'open HodgeLab.OneReflectionSkew.ResidueNormalization\n')
    scratch=ROOT/'.lake/skew-residue-controls';scratch.mkdir(parents=True,exist_ok=True)
    positive=header+'\n'.join('example : '+e+' = '+c+' := by\n    '+proof+'\n' for e,c,_,proof in controls.values())
    positive += ('example : chartDenominator (-1 : ℚ) 1 0 0 1 = 0 := by\n'
                 '  norm_num [chartDenominator, cubic, aCoeff, bCoeff, cCoeff, dCoeff]\n'
                 'example : normalDerivative (-1 : ℚ) 1 0 0 1 = 6 := by\n'
                 '  rw [normalDerivative_eq]; norm_num\n'
                 'example : 72 * normalizedPoleCoefficient (-1 : ℚ) 1 0 0 1 = 5 := by\n'
                 '  rw [normalizedPoleCoefficient_eq _ _ _ _ _ (by norm_num)]; norm_num\n')
    p=scratch/'positive.lean';p.write_text(positive,encoding='utf-8',newline='\n');(OUT/'positive.lean.txt').write_bytes(p.read_bytes())
    util.run('positive-controls',['lake','env','lean',p.relative_to(ROOT).as_posix()])
    for name,(e,c,w,proof) in controls.items():
        statement=e+(' ≠ 0' if w is None else ' = '+w)
        body=header+'example : '+statement+' := by\n  have checked : '+e+' = '+c+' := by\n    '+proof+'\n  rw [checked]\n  decide +kernel\n'
        p=scratch/(name+'.lean');p.write_text(body,encoding='utf-8',newline='\n');(OUT/(name+'.lean.txt')).write_bytes(p.read_bytes())
        log=util.run(name,['lake','env','lean',p.relative_to(ROOT).as_posix()],True)
        require(log.count('error:')==1 and 'unsolved goals' not in log and 'did not reduce' not in log,'Unrelated control error '+name)
    require(hashes=={s:digest(ROOT/s) for s in SOURCES},'Proof sources changed during run')
    for n,h in reused.items():require(digest(ROOT/n)==h,'Reused source changed during run')
    for n,h in input_hashes.items():require(digest(OUT/n if n=='inputs.json' else ROOT.parent/n)==h,'Input changed during run')
    require(digest(prior_path)==prior_hash,'Prior receipt changed during run')
    write('validation.json',{'status':'PASS','completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'lean_version':version.strip(),'python_version':sys.version,'mathlib_commit':rev,
        'source_lf_sha256':hashes,'reused_source_lf_sha256':reused,'input_lf_sha256':input_hashes,
        'prior_receipt_lf_sha256':prior_hash,'independent_receipt_lf_sha256':digest(OUT/'independent.json'),
        'artifact_sha256':{m:hashlib.sha256((ROOT/'.lake/build/lib/lean'/(m.replace('.','/')+'.olean')).read_bytes()).hexdigest() for m in MODULES},
        'theorem_axioms':axioms,'commands':util.RECORDS,'elapsed_seconds':time.monotonic()-util.START,'total_budget_seconds':600,
        'new_theorems':len(NAMES),'new_modules_replayed':len(MODULES),'positive_controls':len(controls)+3,'negative_controls':len(controls),
        'scope':'Actual normal polynomial derivative, arbitrary-covector orientation and conditional coordinate-derivation pole reduction; local normal coefficient 5/72.',
        'limits':['No general exterior-derivative or residue operator instantiated',
                  'Ambient reduction assumes a coordinate derivation; its existence on the chosen function field is not constructed',
                  'Ambient z and G nonzero; final normal coefficient only z nonzero and may be restricted to G=0',
                  'No global descent, trace, primitive, clearing or HasCertificate',
                  'Prior proofs and mathlib reused; only two new modules kernel-replayed',
                  'No expanded denominator family or accepted solve']})
    print('PASS: 19 theorem audits, two kernel replays, eight positive and five negative controls')

if __name__=='__main__':
    try:main()
    except Exception as error:
        OUT.mkdir(parents=True,exist_ok=True);write('validation.json',{'status':'FAIL','error':str(error),'commands':util.RECORDS});raise
