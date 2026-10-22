"""Bounded ambient derivation check: 120 seconds/process, 600 total.

Run python3 -O check_skew_ambient.py from formal after fetching pinned Mathlib
dependencies. Reuses checkpoint 126; does not rewrite or replay its receipts.
Every required check raises on failure, including under Python -O.
"""
from pathlib import Path
import datetime, hashlib, json, os, re, shlex, subprocess, sys, time
import check_skew_extension as util

ROOT = Path(__file__).resolve().parent
OUT = ROOT/'results/skew-ambient'
MODULE = 'HodgeLab.OneReflectionSkew.AmbientDerivation'
DECLARATIONS = ['ambientD_algebraMap','ambientD_coord','coord_ne_zero',
                'ambientD_quotient','reciprocal_derivative','scaled_reciprocal_derivative',
                'G_eq_algebraMap','ambientD_G','G_ne_zero','concrete_ambient_reduction',
                'concrete_normal_factorization','no_unchanged_derivation_on_divisor']
NAMES = [MODULE+'.'+name for name in DECLARATIONS]
SOURCES = ['lean-toolchain','lakefile.toml','lake-manifest.json','check_skew_extension.py',
           'check_skew_ambient.py','AuditSkewAmbient.lean','ReplaySkewAmbient.lean',
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
    global START
    START=time.monotonic()
    OUT.mkdir(parents=True,exist_ok=True)
    write('validation.json',{'status':'IN_PROGRESS'})
    hashes={p:digest(ROOT/p) for p in SOURCES}
    prior_path=ROOT/'results/skew-residue/validation.json'
    prior_hash=digest(prior_path)
    prior=json.loads(prior_path.read_text(encoding='utf-8'))
    require(prior['status']=='PASS','Completed residue receipt required')
    reused=dict(prior['reused_source_lf_sha256'])
    reused.update({p:h for p,h in prior['source_lf_sha256'].items() if p.startswith('HodgeLab/') and p.endswith('.lean')})
    for p,h in reused.items(): require(digest(ROOT/p)==h,'Reused proof changed '+p)
    pins=json.loads((OUT/'inputs.json').read_text(encoding='utf-8'))
    input_hashes={'inputs.json':digest(OUT/'inputs.json')}
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
    audit=run('axioms',['lake','env','lean','AuditSkewAmbient.lean'])
    axioms={n:[a.strip() for a in values.split(',') if a.strip()] for n,values in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]",audit)}
    for n in re.findall(r"'([^']+)' does not depend on any axioms",audit): axioms[n]=[]
    require(set(axioms)==set(NAMES),'Missing or unexpected theorem audits')
    require(all(set(a)<={'propext','Classical.choice','Quot.sound'} for a in axioms.values()),'Unexpected axiom')
    replay=run('kernel-replay',['lake','env','lean','ReplaySkewAmbient.lean'])
    require('PASS '+MODULE in replay,'Missing module replay marker')
    header='import '+MODULE+'\nopen '+MODULE+'\n'
    scratch=ROOT/'.lake/skew-ambient-controls';scratch.mkdir(parents=True,exist_ok=True)
    positive=header
    for i in range(5):
        positive+=f'example : ambientD (coord {i}) = {int(i==4)} := by simp [ambientD_coord]\n'
    positive+='example : (coord 4)^2 * ambientD ((coord 4)⁻¹) = -1 := scaled_reciprocal_derivative\n'
    positive+='example : G ≠ 0 := G_ne_zero\n'
    p=scratch/'positive.lean';p.write_text(positive,encoding='utf-8',newline='\n')
    (OUT/'positive.lean.txt').write_bytes(p.read_bytes())
    run('positive-controls',['lake','env','lean',p.relative_to(ROOT).as_posix()])
    negatives={
        'wrong-base-derivative':'example : ambientD (coord 0) = 1 := by\n  simp [ambientD_coord]\n',
        'wrong-normal-sign':'example : ambientD (coord 4) = -1 := by\n  simp [ambientD_coord]\n  norm_num\n',
        'wrong-quotient-sign':'example : (coord 4)^2 * ambientD ((coord 4)⁻¹) = 1 := by\n  rw [scaled_reciprocal_derivative]\n  norm_num\n'}
    for label,body in negatives.items():
        p=scratch/(label+'.lean');p.write_text(header+body,encoding='utf-8',newline='\n')
        (OUT/(label+'.lean.txt')).write_bytes(p.read_bytes())
        run(label,['lake','env','lean',p.relative_to(ROOT).as_posix()],True)
    require(hashes=={p:digest(ROOT/p) for p in SOURCES},'New sources changed during verification')
    for p,h in reused.items(): require(digest(ROOT/p)==h,'Reused sources changed during verification')
    for p,h in input_hashes.items(): require(digest(OUT/p if p=='inputs.json' else ROOT.parent/p)==h,'Input changed during verification')
    require(digest(prior_path)==prior_hash,'Prior receipt changed')
    write('validation.json',{'status':'PASS','completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'lean_version':version.strip(),'python_version':sys.version,'mathlib_commit':rev,
        'source_lf_sha256':hashes,'reused_source_lf_sha256':reused,'input_lf_sha256':input_hashes,
        'prior_receipt_lf_sha256':prior_hash,
        'artifact_sha256':{MODULE:hashlib.sha256((ROOT/'.lake/build/lib/lean'/(MODULE.replace('.','/')+'.olean')).read_bytes()).hexdigest()},
        'theorem_axioms':axioms,'commands':RECORDS,'elapsed_seconds':time.monotonic()-START,
        'total_budget_seconds':600,'new_theorems':len(NAMES),'new_modules_replayed':1,
        'positive_controls':7,'negative_controls':len(negatives),
        'scope':'Constructed rational ambient derivation, exact polynomial embedding, nonzero chart denominators, instantiated local pole reduction and explicit non-descent to G=0.',
        'limits':['K is Frac(Q[U,r,w,t,z]); coordinates are independent ambient variables',
                  'No derivation on the hypersurface quotient or global primitive',
                  'Quotient identity uses Lean total division; ordinary fraction interpretation requires nonzero denominator',
                  'No general exterior-derivative/residue operator, physical square-cover lift, trace or clearing',
                  'Prior proofs and Mathlib are reused imports, not newly kernel-replayed',
                  'No increased bounded-exclusion coverage or accepted solve']})
    print('PASS: 12 theorem audits, one kernel replay, seven positive and three negative controls')

if __name__=='__main__':
    try: main()
    except Exception as error:
        OUT.mkdir(parents=True,exist_ok=True)
        write('validation.json',{'status':'FAIL','error':str(error),'commands':RECORDS})
        raise
