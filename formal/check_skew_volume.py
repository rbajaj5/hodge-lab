"""Bounded algebraic coordinate-volume proof check, reusing checkpoint124.

python3 -O check_skew_volume.py; cached Lean dependencies, no network.
120 seconds per command and 600 seconds total. Standard-library exact arithmetic.
"""
from fractions import Fraction as Q
from itertools import permutations
from pathlib import Path
import datetime, hashlib, json, re, sys, time
import check_skew_extension as util

ROOT = Path(__file__).resolve().parent
OUT = ROOT/'results/skew-volume'
PREFIX = 'HodgeLab.OneReflectionSkew.'
MODULES = [PREFIX+'CoordinateVolume', PREFIX+'VolumeDensity']
VOLUME_NAMES = ['physicalCoordinates_eval','physicalJacobian_entries','affineJacobian_entries',
                'affineJacobian_det','squareCoordinates_eval','squareJacobian_entries',
                'squareJacobian_det','omegaMatrix_entries','omegaMatrix_minor','omegaMatrix_det']
DENSITY_NAMES = ['xCoefficient_eq','square_pullback','affine_nonsingular_iff',
                 'square_nonsingular_iff','coefficient_recovery','protected_pole_condition']
NAMES = [PREFIX+'CoordinateVolume.'+n for n in VOLUME_NAMES]+[PREFIX+'VolumeDensity.'+n for n in DENSITY_NAMES]
SOURCES = ['lean-toolchain','lakefile.toml','lake-manifest.json','check_skew_extension.py',
           'check_skew_volume.py','AuditSkewVolume.lean','ReplaySkewVolume.lean']+[m.replace('.','/')+'.lean' for m in MODULES]
require, digest = util.require, util.digest

def write(name, value):
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')

ZERO = (0,)*5
ONE = {ZERO:Q(1)}

def add(a,b):
    r=dict(a)
    for e,c in b.items(): r[e]=r.get(e,Q(0))+c
    return {e:c for e,c in r.items() if c}

def scale(a,c): return {e:Q(c)*v for e,v in a.items() if c*v}

def mul(a,b):
    r={}
    for e,c in a.items():
        for f,d in b.items():
            k=tuple(x+y for x,y in zip(e,f));r[k]=r.get(k,Q(0))+c*d
    return {e:c for e,c in r.items() if c}

def power(a,n):
    r=ONE
    for _ in range(n):r=mul(r,a)
    return r

def deriv(a,j):
    r={}
    for e,c in a.items():
        if e[j]:
            f=list(e);f[j]-=1;r[tuple(f)]=c*e[j]
    return r

def det(m):
    total={};n=len(m)
    for p in permutations(range(n)):
        term=ONE
        for i,j in enumerate(p):term=mul(term,m[i][j])
        sign=(-1)**sum(p[i]>p[j] for i in range(n) for j in range(i+1,n))
        total=add(total,scale(term,sign))
    return total

def value(a,point):
    total=Q(0)
    for e,c in a.items():
        term=c
        for x,n in zip(point,e):term*=Q(x)**n
        total+=term
    return total

def terms(a):return [[str(c),list(e)] for e,c in sorted(a.items())]

def independent_check():
    pins=json.loads((OUT/'inputs.json').read_text(encoding='utf-8'))['pins'];saved={}
    for pin in pins:
        raw=(ROOT.parent/pin['path']).read_bytes().replace(b'\r\n',b'\n')
        require(hashlib.sha256(raw).hexdigest()==pin['sha256'],'Input SHA256 mismatch')
        require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==pin['git_blob'],'Input Git blob mismatch')
        saved[Path(pin['upstream_path']).name]=json.loads(raw) if pin['upstream_path'].endswith('.json') else raw.decode('utf-8')
    require(saved['provenance.json']['variables']==['X0','X1','X2','Y0','Y1','Y2'],'Protected order changed')
    require(saved['record.json']['q']==1,'Wrong protected pole order')
    variables=[{tuple(int(i==j) for i in range(5)):Q(1)} for j in range(5)]
    x,r,w,t,z=variables
    coordinates=[x,mul(r,x),mul(w,x),ONE,t,z]
    square=[power(x,2),r,w,t,z]
    J=[[deriv(p,j) for j in range(5)] for p in coordinates]
    S=[[deriv(p,j) for j in range(5)] for p in square]
    expectedJ=[[ONE,{},{},{},{}],[r,x,{},{},{}],[w,{},x,{},{}],[{},{},{},{},{}],
               [{},{},{},ONE,{}],[{},{},{},{},ONE]]
    expectedS=[[scale(x,2) if i==j==0 else ONE if i==j else {} for j in range(5)] for i in range(5)]
    require(J==expectedJ,'Physical polynomial derivative matrix mismatch')
    require(S==expectedS,'Square polynomial derivative matrix mismatch')
    affine=[J[i] for i in [0,1,2,4,5]]
    M=[[coordinates[i],*J[i]] for i in range(6)]
    da,ds,om=det(affine),det(S),det(M)
    require(da==power(x,2),'Affine Jacobian determinant failed')
    require(ds==scale(x,2),'Square Jacobian determinant failed')
    require(om==scale(power(x,2),-1),'Projective volume orientation failed')
    cofactor=[]
    for i in range(6):
        minor=[J[k] for k in range(6) if k!=i]
        summand=scale(mul(coordinates[i],det(minor)),(-1)**i)
        require(summand==(om if i==3 else {}),'Unexpected Euler-volume summand')
        cofactor.append(summand)
    def substitute(protected_terms):
        result={}
        for c,e in protected_terms:
            term=scale(ONE,Q(c))
            for p,n in zip(coordinates,e):term=mul(term,power(p,n))
            result=add(result,term)
        return result
    A=substitute(saved['record.json']['A']['terms'])
    F=substitute(saved['record.json']['F']['terms'])
    source_numerator=mul(A,om)
    normalized_numerator=scale(power(x,4),Q(-1,2))
    require(A==power(x,3),'Protected source substitution mismatch')
    require(source_numerator==scale(power(x,5),-1),'Source-volume numerator mismatch')
    require(mul(normalized_numerator,ds)==source_numerator,'Forward coefficient numerator identity failed')
    point=[2,0,0,0,0];g=value(F,point)
    require(g==65,'Protected control denominator mismatch')
    sample={'point':point,'G':str(g),'affine_det':str(value(da,point)),'square_det':str(value(ds,point)),
            'omega_det':str(value(om,point)),'x_coefficient':str(value(source_numerator,point)/g**2),
            'u_coefficient':str(value(normalized_numerator,point)/g**2)}
    require(Q(sample['u_coefficient'])*4225==-8,'Density control mismatch')
    require(value(ds,[0,0,0,0,0])==0,'Degenerate chart control mismatch')
    result={'status':'PASS','method':'independent exact sparse rational arithmetic and permutation determinants',
            'protected_order':saved['provenance.json']['variables'],'parameter_order':['x','r','w','t','z'],
            'affine_output_order':['X0','X1','X2','Y1','Y2'],'square_output_order':['U','r','w','t','z'],
            'physical_derivative_entries':30,'square_derivative_entries':25,
            'physical_jacobian':[[terms(p) for p in row] for row in J],
            'square_jacobian':[[terms(p) for p in row] for row in S],
            'omega_matrix':[[terms(p) for p in row] for row in M],
            'affine_determinant':terms(da),'square_determinant':terms(ds),'omega_determinant':terms(om),
            'euler_volume_summands':[terms(p) for p in cofactor], 'source_numerator':terms(source_numerator),
            'normalized_numerator_after_U=x^2':terms(normalized_numerator),'sample':sample,
            'limits':'Algebraic coefficient model of ordered top volumes; no general differential-form API, residue, global descent or trace replay.'}
    write('independent.json',result)

def main():
    OUT.mkdir(parents=True,exist_ok=True);util.OUT,util.START,util.RECORDS=OUT,time.monotonic(),[]
    write('validation.json',{'status':'IN_PROGRESS'})
    hashes={s:digest(ROOT/s) for s in SOURCES}
    prior_path=ROOT/'results/skew-chart/validation.json'
    prior_hash=digest(prior_path);prior=json.loads(prior_path.read_text(encoding='utf-8'))
    require(prior['status']=='PASS','Completed chart proof receipt missing')
    reused=dict(prior['reused_source_lf_sha256'])
    reused.update({n:h for n,h in prior['source_lf_sha256'].items() if n.startswith('HodgeLab/') and n.endswith('.lean')})
    for n,h in reused.items():require(digest(ROOT/n)==h,'Reused proof changed '+n)
    input_hashes={'inputs.json':digest(OUT/'inputs.json')}
    for p in json.loads((OUT/'inputs.json').read_text(encoding='utf-8'))['pins']:
        input_hashes[p['path']]=digest(ROOT.parent/p['path'])
        if p['path'] in prior['input_lf_sha256']:
            require(input_hashes[p['path']]==prior['input_lf_sha256'][p['path']],'Target changed since chart proof')
    for n in SOURCES:
        if n.endswith('.lean'):require(not re.search(r'\b(sorry|admit|axiom|native_decide)\b',(ROOT/n).read_text(encoding='utf-8')),'Unproved token '+n)
    independent_check()
    version=util.run('version',['lake','env','lean','--version']);require('version 4.31.0,' in version,'Wrong Lean')
    manifest=json.loads((ROOT/'lake-manifest.json').read_text(encoding='utf-8'));rev=next(p['rev'] for p in manifest['packages'] if p['name']=='mathlib')
    require(util.run('mathlib-head',['git','-C','.lake/packages/mathlib','rev-parse','HEAD']).strip()==rev,'Mathlib mismatch')
    util.run('build',['lake','build',*MODULES])
    audit=util.run('axioms',['lake','env','lean','AuditSkewVolume.lean'])
    axioms={n:[x.strip() for x in a.split(',') if x.strip()] for n,a in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]",audit)}
    for n in re.findall(r"'([^']+)' does not depend on any axioms",audit):axioms[n]=[]
    require(set(axioms)==set(NAMES),'Missing/unexpected theorem audits')
    require(all(set(a)<={'propext','Classical.choice','Quot.sound'} for a in axioms.values()),'Unexpected axiom')
    replay=util.run('kernel-replay',['lake','env','lean','ReplaySkewVolume.lean'])
    require(all('PASS '+m in replay for m in MODULES),'Missing replay marker')
    controls={
        'wrong-orientation': ('(omegaMatrix (2 : ℚ) 0 0 0 0).det','-4','4','rw [omegaMatrix_det]\n    norm_num'),
        'missing-affine-factor': ('(affineJacobian (2 : ℚ) 0 0 0 0).det','4','2','rw [affineJacobian_det]\n    norm_num'),
        'missing-square-factor-two': ('4225 * uCoefficient (4 : ℚ) 0 0 0 0','-8','-16','norm_num [uCoefficient, chartDenominator, cubic, aCoeff, bCoeff, cCoeff, dCoeff]'),
        'invalid-nonzero-chart': ('(squareJacobian (0 : ℚ) 0 0 0 0).det','0',None,'rw [squareJacobian_det]\n    norm_num')}
    header=('import HodgeLab.OneReflectionSkew.VolumeDensity\nopen HodgeLab.OneReflectionSkew.ChartSubstitution\n'
            'open HodgeLab.OneReflectionSkew.CoordinateVolume\nopen HodgeLab.OneReflectionSkew.VolumeDensity\n')
    scratch=ROOT/'.lake/skew-volume-controls';scratch.mkdir(parents=True,exist_ok=True)
    positive=header+'\n'.join('example : '+e+' = '+c+' := by\n    '+proof+'\n' for e,c,_,proof in controls.values())
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
        'new_theorems':len(NAMES),'new_modules_replayed':len(MODULES),'positive_controls':len(controls),'negative_controls':len(controls),
        'scope':'Actual polynomial Jacobians, signed Euler-volume coefficient and ambient rational coefficient transport.',
        'limits':['Algebraic coefficient model; no general differential-form pullback API',
                  'G nonzero describes the complement before residue, not a point on G=0',
                  'No residue, trace, global descent, primitive, clearing or HasCertificate',
                  'Prior chart/obstruction proofs and mathlib reused; only two new modules kernel-replayed',
                  'No expanded denominator family or accepted solve']})
    print('PASS: 16 theorem audits, two kernel replays, four positive and four negative controls')

if __name__=='__main__':
    try:main()
    except Exception as error:
        OUT.mkdir(parents=True,exist_ok=True);write('validation.json',{'status':'FAIL','error':str(error),'commands':util.RECORDS});raise
