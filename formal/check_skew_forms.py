"""Bounded actual differential-form check: 120 seconds/process, 600 total.

Run python3 -O check_skew_forms.py from formal after fetching pinned Mathlib
dependencies. Reuses checkpoint 128; does not rewrite or replay its receipts.
Historical inputs remain in results/skew-forms. Every invocation writes to a
fresh results/runs directory (or a new directory selected by --output-dir).
Every required check raises on failure, including under Python -O.
"""
from pathlib import Path
import datetime, hashlib, json, os, re, shlex, subprocess, sys, time
import check_skew_extension as util
from fresh_receipts import fresh_output_dir

ROOT = Path(__file__).resolve().parent
HISTORY = ROOT/'results/skew-forms'
OUT = None
MODULE = 'HodgeLab.OneReflectionSkew.DifferentialForms'
DECLARATIONS = ['base_wedge_zero', 'coordinate_swap', 'normal_first_orientation', 'wedgeDerivation_apply', 'normalDerivation_apply', 'polynomial_derivations_eq', 'derivations_eq', 'differential_wedge', 'differentialBasis_apply', 'volume_eq_multi', 'topCoefficient_volume', 'volume_ne_zero', 'actual_form_reduction']
NAMES = [MODULE+'.'+name for name in DECLARATIONS]
SOURCES = ['lean-toolchain','lakefile.toml','lake-manifest.json','check_skew_extension.py',
           'check_skew_forms.py','fresh_receipts.py','AuditSkewForms.lean','ReplaySkewForms.lean',
           MODULE.replace('.','/')+'.lean']
require, digest = util.require, util.digest
START = time.monotonic()
RECORDS = []
if hasattr(sys.stdout,'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')

def write(name,value):
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')

def run(label,command,reject=False):
    remaining=600-(time.monotonic()-START)
    require(remaining>1,'600-second budget exhausted')
    bound=min(120,int(remaining))
    execution=command
    if os.name=='nt':
        wroot='/mnt/'+ROOT.drive[0].lower()+ROOT.as_posix()[2:]
        execution=['wsl.exe','--cd',wroot,'-e','sh','-lc','exec timeout '+str(bound)+' '+shlex.join(command)]
    began=time.monotonic()
    try:
        result=subprocess.run(execution,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=bound+10)
        code=result.returncode;log=result.stdout+result.stderr
    except subprocess.TimeoutExpired as error:
        def txt(value):return value.decode('utf-8',errors='replace') if isinstance(value,bytes) else value or ''
        code=124;log=txt(error.stdout)+txt(error.stderr)
    (OUT/(label+'.log')).write_text(log,encoding='utf-8',newline='\n')
    RECORDS.append({'label':label,'command':command,'execution_command':execution,
                    'bound_seconds':bound,'exit_code':code,'elapsed_seconds':time.monotonic()-began,
                    'expected_failure':reject,'log':label+'.log','log_lf_sha256':digest(OUT/(label+'.log'))})
    write('commands.json',RECORDS)
    print(json.dumps({'label':label,'exit_code':code,'seconds':RECORDS[-1]['elapsed_seconds']}),flush=True)
    require(code!=124,label+' timed out; no mathematical result')
    if reject:
        require(code!=0 and log.count('error:')==1 and 'unsolved goals' in log and '⊢ False' in log,
                label+' did not fail at the expected false mathematical goal: '+log[:1800])
        require('failed to synthesize' not in log and 'unknown' not in log.lower(), 'Unrelated control error')
    else:
        require(code==0,label+' failed: '+log[:1800])
    return log

def main():
    global START, OUT
    START=time.monotonic()
    OUT=fresh_output_dir(ROOT, 'skew-forms', [HISTORY,
        ROOT/'results/skew-trace-basis', ROOT/'results/skew-ambient',
        ROOT.parent/'results/chi-target-source'])
    print('Fresh receipts: '+str(OUT),flush=True)
    write('validation.json',{'status':'IN_PROGRESS'})
    hashes={p:digest(ROOT/p) for p in SOURCES}
    prior_path=ROOT/'results/skew-ambient/validation.json'
    prior_hash=digest(prior_path)
    prior=json.loads(prior_path.read_text(encoding='utf-8'))
    require(prior['status']=='PASS','Completed ambient derivation receipt required')
    reused=dict(prior['reused_source_lf_sha256'])
    reused.update({p:h for p,h in prior['source_lf_sha256'].items() if p.startswith('HodgeLab/') and p.endswith('.lean')})
    for p,h in reused.items(): require(digest(ROOT/p)==h,'Reused proof changed '+p)
    pins=json.loads((HISTORY/'inputs.json').read_text(encoding='utf-8'))
    input_hashes={'inputs.json':digest(HISTORY/'inputs.json')}
    for pin in pins['pins']:
        raw=(ROOT.parent/pin['path']).read_bytes().replace(b'\r\n',b'\n')
        require(hashlib.sha256(raw).hexdigest()==pin['sha256'],'Target hash mismatch')
        require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==pin['git_blob'],'Target Git blob mismatch')
        input_hashes[pin['path']]=digest(ROOT.parent/pin['path'])
    for p in SOURCES:
        if p.endswith('.lean'):
            require(not re.search(r'\b(sorry|admit|axiom|native_decide)\b',(ROOT/p).read_text(encoding='utf-8')),'Unproved token '+p)
    version=run('version',['lake','env','lean','--version'])
    require('version 4.31.0,' in version,'Unexpected Lean version')
    manifest=json.loads((ROOT/'lake-manifest.json').read_text(encoding='utf-8'))
    rev=next(p['rev'] for p in manifest['packages'] if p['name']=='mathlib')
    require(run('mathlib-head',['git','-C','.lake/packages/mathlib','rev-parse','HEAD']).strip()==rev,'Mathlib mismatch')
    run('build',['lake','build',MODULE])
    audit=run('axioms',['lake','env','lean','AuditSkewForms.lean'])
    axioms={n:[a.strip() for a in values.split(',') if a.strip()] for n,values in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]",audit)}
    for n in re.findall(r"'([^']+)' does not depend on any axioms",audit): axioms[n]=[]
    require(set(axioms)==set(NAMES),'Missing or unexpected theorem audits')
    require(all(set(a)<={'propext','Classical.choice','Quot.sound'} for a in axioms.values()),'Unexpected axiom')
    replay=run('kernel-replay',['lake','env','lean','ReplaySkewForms.lean'])
    require('PASS '+MODULE in replay,'Missing module replay marker')
    header='import '+MODULE+'\nopen '+MODULE+' HodgeLab.OneReflectionSkew.AmbientDerivation\n'
    scratch=ROOT/'.lake/skew-forms-controls';scratch.mkdir(parents=True,exist_ok=True)
    positive=header+"""
example : topCoefficient volume = 1 := topCoefficient_volume
example : volume ≠ 0 := volume_ne_zero
example : topCoefficient (oneForm (coord 4)*alpha) = 1 := by
  rw [normal_first_orientation, topCoefficient_volume]
example : topCoefficient (oneForm (coord 0)*alpha) = 0 := by
  have h := base_wedge_zero 0
  change oneForm (coord 0)*alpha = 0 at h
  rw [h,map_zero]
example : (coord 4)^2 * topCoefficient (oneForm ((coord 4)⁻¹)*alpha) = -1 := by
  rw [differential_wedge, map_smul, topCoefficient_volume]
  simpa using scaled_reciprocal_derivative
"""
    p=scratch/'positive.lean';p.write_text(positive,encoding='utf-8',newline='\n')
    (OUT/'positive.lean.txt').write_bytes(p.read_bytes())
    run('positive-controls',['lake','env','lean',p.relative_to(ROOT).as_posix()])
    negatives={
        'wrong-orientation':"""example : topCoefficient (oneForm (coord 4)*alpha) = -1 := by
  rw [normal_first_orientation, topCoefficient_volume]
  norm_num
""",
        'wrong-repeated-wedge':"""example : topCoefficient (oneForm (coord 0)*alpha) = 1 := by
  have h := base_wedge_zero 0
  change oneForm (coord 0)*alpha = 0 at h
  rw [h,map_zero]
  norm_num
""",
        'wrong-reciprocal-sign':"""example : (coord 4)^2 * topCoefficient (oneForm ((coord 4)⁻¹)*alpha) = 1 := by
  rw [differential_wedge, map_smul, topCoefficient_volume]
  change (coord 4)^2 * (ambientD ((coord 4)⁻¹) * 1) = 1
  rw [mul_one,scaled_reciprocal_derivative]
  norm_num
"""}
    for label,body in negatives.items():
        p=scratch/(label+'.lean');p.write_text(header+body,encoding='utf-8',newline='\n')
        (OUT/(label+'.lean.txt')).write_bytes(p.read_bytes())
        run(label,['lake','env','lean',p.relative_to(ROOT).as_posix()],True)
    require(hashes=={p:digest(ROOT/p) for p in SOURCES},'New sources changed during verification')
    for p,h in reused.items(): require(digest(ROOT/p)==h,'Reused sources changed during verification')
    for p,h in input_hashes.items(): require(digest(HISTORY/p if p=='inputs.json' else ROOT.parent/p)==h,'Input changed during verification')
    require(digest(prior_path)==prior_hash,'Prior receipt changed')
    write('validation.json',{'status':'PASS','completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'lean_version':version.strip(),'python_version':sys.version,'mathlib_commit':rev,
        'source_lf_sha256':hashes,'reused_source_lf_sha256':reused,'input_lf_sha256':input_hashes,
        'prior_receipt_lf_sha256':prior_hash,
        'artifact_sha256':{MODULE:hashlib.sha256((ROOT/'.lake/build/lib/lean'/(MODULE.replace('.','/')+'.olean')).read_bytes()).hexdigest()},
        'theorem_axioms':axioms,'commands':RECORDS,'elapsed_seconds':time.monotonic()-START,
        'total_budget_seconds':600,'new_theorems':len(NAMES),'new_modules_replayed':1,
        'positive_controls':5,'negative_controls':len(negatives),
        'scope':'Actual Kahler differentials and exterior products over Frac(Q[U,r,w,t,z]); df wedge alpha equals the constructed normal derivative times a proved nonzero volume; exact +5/72 logarithmic reduction.',
        'limits':['Independent ambient variables over Q; G and z are nonzero rational functions',
                  'betaDifferential is d(betaScalar) wedge alpha, not a general exterior differential',
                  'No de Rham complex, general residue operator or restriction of the ambient equation to G=0',
                  'No physical square-cover pullback, primitive, trace, clearing or HasCertificate',
                  'Prior proofs and Mathlib are reused imports, not newly kernel-replayed',
                  'No increased bounded-exclusion coverage or accepted solve']})
    print('PASS: 13 theorem audits, one kernel replay, five positive and three negative controls')

if __name__=='__main__':
    try: main()
    except Exception as error:
        if OUT is not None:
            write('validation.json',{'status':'FAIL','error':str(error),'commands':RECORDS})
        raise
