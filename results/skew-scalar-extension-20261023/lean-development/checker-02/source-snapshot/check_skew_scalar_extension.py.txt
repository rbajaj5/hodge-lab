"""Verify the new scalar-extension/trace bridge with fresh receipts.

120 seconds per Lean command, 600 seconds per checker. Only the new module is
kernel-replayed. Historical distinct-root/binding/basis receipts are inputs.
"""
from pathlib import Path
import datetime, hashlib, json, os, re, shlex, subprocess, sys, tempfile, time
from check_skew_extension import require, digest
from fresh_receipts import fresh_output_dir

ROOT = Path(__file__).resolve().parent
HISTORY = ROOT/'results/skew-scalar-extension'
OUT = None
MODULE = 'HodgeLab.OneReflectionSkew.ScalarExtensionTrace'
DECLARATIONS = ['E', 'T', 'Q', 'theta', 'iota', 'iota_apply', 'mapped_polynomial_eq', 'generic_monic', 'finiteE', 'freeE', 'finiteT', 'freeT', 'quotientBasis', 'tensorBasis', 'finrankE', 'finrankT', 'sigma', 'sigma_theta', 'allEvaluations', 'betaHom', 'betaHom_tmul', 'betaHom_theta', 'betaHom_surjective', 'betaHom_bijective', 'beta', 'beta_tmul', 'beta_theta', 'beta_scalar', 'quotientComparison', 'quotientComparison_evaluation', 'quotientComparison_theta', 'quotientComparison_scalar', 'trace_baseChange', 'trace_beta', 'trace_quotientComparison', 'trace_eq_sum', 'trace_evaluations', 'trace_tmul', 'trace_one', 'trace_two_tmul_one', 'derivativeElement', 'derivative_isUnit', 'derivativeInverse', 'derivative_mul_inverse', 'sigma_derivative', 'sigma_derivativeInverse', 'quotientWeight', 'beta_quotientWeight', 'trace_quotientWeight', 'trace_slot_seventeen', 'trace_slot_eleven']
NAMES = [MODULE+'.'+n for n in DECLARATIONS]
SOURCES = ['lean-toolchain','lakefile.toml','lake-manifest.json',
    'check_skew_extension.py','fresh_receipts.py','check_skew_scalar_extension.py',
    'AuditSkewScalarExtension.lean','ReplaySkewScalarExtension.lean',
    MODULE.replace('.','/')+'.lean']
RECORDS = []
START = time.monotonic()
EXECUTOR = os.environ.get('HODGE_CHECK_EXECUTOR') or (
    'GitHub Actions' if os.environ.get('GITHUB_ACTIONS') == 'true' else 'unspecified local invoker')
if hasattr(sys.stdout,'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def write(name, value):
    (OUT/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n',
                          encoding='utf-8', newline='\n')


def raw_digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(label, command, reject=False):
    remaining = 600 - (time.monotonic()-START)
    require(remaining > 1, '600-second budget exhausted')
    bound = min(120, int(remaining))
    execution = command
    if os.name == 'nt':
        wroot = '/mnt/'+ROOT.drive[0].lower()+ROOT.as_posix()[2:]
        execution = ['wsl.exe', '--cd', wroot, '-e', 'sh', '-lc',
                     'exec timeout '+str(bound)+' '+shlex.join(command)]
    began = time.monotonic()
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        completed = subprocess.run(execution, cwd=ROOT, capture_output=True,
                                   encoding='utf-8', timeout=bound)
        code, stdout, stderr = completed.returncode, completed.stdout, completed.stderr
    except subprocess.TimeoutExpired as error:
        def text(value):
            return value.decode('utf-8', errors='replace') if isinstance(value, bytes) else value or ''
        code, stdout, stderr = 124, text(error.stdout), text(error.stderr)
    log = stdout+stderr
    for suffix, value in [('stdout.log', stdout), ('stderr.log', stderr), ('log', log)]:
        (OUT/(label+'.'+suffix)).write_text(value, encoding='utf-8', newline='\n')
    RECORDS.append(dict(label=label, command=command, execution_command=execution,
        cwd='formal', started_utc=started, bound_seconds=bound, exit_code=code,
        elapsed_seconds=time.monotonic()-began, expected_failure=reject,
        log=label+'.log', log_lf_sha256=digest(OUT/(label+'.log')),
        stdout=label+'.stdout.log', stdout_sha256=raw_digest(OUT/(label+'.stdout.log')),
        stderr=label+'.stderr.log', stderr_sha256=raw_digest(OUT/(label+'.stderr.log'))))
    write('commands.json', RECORDS)
    print(json.dumps({'label':label, 'exit_code':code,
                      'seconds':RECORDS[-1]['elapsed_seconds']}), flush=True)
    require(code != 124, label+' timed out; interrupted calculations are not results')
    if reject:
        require(code != 0 and log.count('error:') == 1 and 'unsolved goals' in log and '⊢ False' in log,
                label+' did not fail at the intended false mathematical goal: '+log[:2500])
        require('failed to synthesize' not in log and 'unknown' not in log.lower(),
                'Unrelated control error: '+label)
    else:
        require(code == 0, label+' failed: '+log[:2500])
    return log


def checked_inputs():
    inputs = json.loads((HISTORY/'inputs.json').read_text(encoding='utf-8'))
    ref = inputs['source_pins_manifest']
    source_manifest = (ROOT.parent/ref['path']).resolve()
    require(source_manifest.is_relative_to(ROOT.parent.resolve()), 'Source manifest path escapes repository')
    require(raw_digest(source_manifest) == ref['sha256'], 'Source-pin manifest changed')
    pins = json.loads(source_manifest.read_text(encoding='utf-8'))
    require(pins['parent'] == inputs['notebook_parent'], 'Notebook parent mismatch')
    require(pins['upstream'] == inputs['upstream_commit'], 'Upstream pin mismatch')
    require(len(pins['reused_files']) >= 14, 'Missing reused source/receipt pins')
    for name, pin in pins['reused_files'].items():
        path = (ROOT.parent/name).resolve()
        require(path.is_relative_to(ROOT.parent.resolve()), 'Pinned path escapes repository')
        require(raw_digest(path) == pin['sha256'], 'Reused source or historical receipt changed: '+name)
        require(path.stat().st_size == pin['bytes'], 'Pinned byte count changed: '+name)
    prior = json.loads((ROOT.parent/inputs['reused_distinct_root_receipt']).read_text(encoding='utf-8'))
    require(prior['status'] == 'PASS', 'Reused distinct-root receipt is not PASS')
    return inputs, pins


def main():
    global OUT, START
    START=time.monotonic()
    OUT=fresh_output_dir(ROOT,'skew-scalar-extension',[HISTORY,
        ROOT/'results/skew-trace-basis',ROOT/'results/skew-physical-cover',
        ROOT/'results/skew-distinct-roots',
        ROOT.parent/'results/skew-distinct-roots-20261023',
        ROOT.parent/'results/ci-receipt-physical-cover-20261023'])
    print('Fresh receipts: '+str(OUT),flush=True)
    write('validation.json',{'status':'IN_PROGRESS'})
    input_hash=raw_digest(HISTORY/'inputs.json')
    inputs,pins=checked_inputs()
    hashes={p:raw_digest(ROOT/p) for p in SOURCES}
    snapshot=OUT/'source-snapshot';snapshot.mkdir()
    for name in SOURCES:
        target=snapshot/(name+'.txt');target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes((ROOT/name).read_bytes())
    (snapshot/'inputs.json.txt').write_bytes((HISTORY/'inputs.json').read_bytes())
    write('source-inputs.json',{'source_sha256':hashes,'inputs_sha256':input_hash,
        'reused_files':pins['reused_files'],'source_pins_manifest':inputs['source_pins_manifest']})
    for name in SOURCES:
        if name.endswith('.lean'):
            require(not re.search(r'\b(sorry|admit|axiom|native_decide)\b',
                (ROOT/name).read_text(encoding='utf-8')),'Unproved token: '+name)
    actual=re.findall(r'^(?:def|abbrev|theorem|lemma|instance) (\w+)',
        (ROOT/(MODULE.replace('.','/')+'.lean')).read_text(encoding='utf-8'),re.M)
    require(actual==DECLARATIONS,'Declaration/instance audit list does not match source')
    version=run('version',['lake','env','lean','--version'])
    require('version 4.31.0,' in version,'Unexpected Lean version')
    manifest=json.loads((ROOT/'lake-manifest.json').read_text(encoding='utf-8'))
    revision=next(p['rev'] for p in manifest['packages'] if p['name']=='mathlib')
    require(run('mathlib-head',['git','-C','.lake/packages/mathlib','rev-parse','HEAD']).strip()
        ==revision,'Mathlib mismatch')
    run('build',['lake','build',MODULE])
    audit=run('axioms',['lake','env','lean','AuditSkewScalarExtension.lean'])
    axioms={n:[a.strip() for a in values.split(',') if a.strip()]
        for n,values in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]",audit)}
    for name in re.findall(r"'([^']+)' does not depend on any axioms",audit): axioms[name]=[]
    require(set(axioms)==set(NAMES),'Missing or unexpected declaration/instance audit')
    require(all(set(a)<={'propext','Classical.choice','Quot.sound'} for a in axioms.values()),
        'Unexpected axiom')
    replay=run('kernel-replay',['lake','env','lean','ReplaySkewScalarExtension.lean'])
    require('PASS '+MODULE in replay,'Missing kernel replay marker')
    header = """import HodgeLab.OneReflectionSkew.ScalarExtensionTrace
open scoped TensorProduct BigOperators
open Polynomial HodgeLab.OneReflectionSkew.GenericDistinctRoots
open HodgeLab.OneReflectionSkew.ScalarExtensionTrace
open HodgeLab.OneReflectionSkew.TraceFreeBasis HodgeLab.OneReflectionSkew.SplitTraceQuotient
"""
    positive = """
example : Module.Finite BaseField E ∧ Module.Free BaseField E ∧
    Module.Finite SplitField T ∧ Module.Free SplitField T :=
  ⟨finiteE,freeE,finiteT,freeT⟩
example : Module.finrank BaseField E=18 ∧ Module.finrank SplitField T=18 := ⟨finrankE,finrankT⟩
example : genericPolynomial.map baseToSplit=coverPolynomial (1:SplitField) roots :=
  mapped_polynomial_eq
example (l:SplitField) (e:E) (j:Fin18) : beta (l⊗ₜ[BaseField]e) j=l*sigma j e := beta_tmul l e j
example : beta (1⊗ₜ[BaseField]theta)=roots := beta_theta
example (l:SplitField) : beta (l⊗ₜ[BaseField](1:E))=(fun _=>l) := beta_scalar l
example (e:E) : iota e=1⊗ₜ[BaseField]e := iota_apply e
example (z:T) : evaluationEquiv 1 one_ne_zero roots roots_injective (quotientComparison z)=beta z :=
  quotientComparison_evaluation z
example : quotientComparison (1⊗ₜ[BaseField]theta)=
    AdjoinRoot.root (coverPolynomial (1:SplitField) roots) := quotientComparison_theta
example (l:SplitField) : quotientComparison (l⊗ₜ[BaseField](1:E))=algebraMap SplitField Q l :=
  quotientComparison_scalar l
example (e:E) : baseToSplit (Algebra.trace BaseField E e)=Algebra.trace SplitField T (1⊗ₜ[BaseField]e) :=
  trace_baseChange e
example (e:E) : baseToSplit (Algebra.trace BaseField E e)=∑j,sigma j e := trace_evaluations e
example (z:T) : Algebra.trace SplitField T z=Algebra.trace SplitField (SplitAlgebra SplitField) (beta z) ∧
    Algebra.trace SplitField T z=Algebra.trace SplitField Q (quotientComparison z) :=
  ⟨trace_beta z,trace_quotientComparison z⟩
example (l:SplitField) (e:E) : Algebra.trace SplitField T (l⊗ₜ[BaseField]e)=
    l*baseToSplit (Algebra.trace BaseField E e) := trace_tmul l e
example : Algebra.trace BaseField E 1=18 ∧
    Algebra.trace SplitField T ((2:SplitField)⊗ₜ[BaseField](1:E))=36 := ⟨trace_one,trace_two_tmul_one⟩
example : IsUnit derivativeElement ∧ derivativeElement*derivativeInverse=1 :=
  ⟨derivative_isUnit,derivative_mul_inverse⟩
example (i:Fin18) : beta (iota (quotientWeight i))=codifferent 1 roots i := beta_quotientWeight i
example (i:Fin18) : Algebra.trace BaseField E (quotientWeight i)=if (i:ℕ)=17 then 1 else 0 :=
  trace_quotientWeight i
example : Algebra.trace BaseField E (quotientWeight 17)=1 ∧
    Algebra.trace BaseField E (quotientWeight 11)=0 := ⟨trace_slot_seventeen,trace_slot_eleven⟩
""".replace('Fin18','Fin 18')
    negatives={
      'normalized-trace-rejected':"""example : Algebra.trace BaseField E 1=1 := by
  rw [trace_one]
  norm_num
""",
      'dropped-scalar-rejected':"""example : Algebra.trace SplitField T ((2:SplitField)⊗ₜ[BaseField](1:E))=18 := by
  rw [trace_two_tmul_one]
  norm_num
""",
      'slot-eleven-trace-one-rejected':"""example : Algebra.trace BaseField E (quotientWeight 11)=1 := by
  rw [trace_slot_eleven]
  norm_num
"""}
    scratch_parent=ROOT/'.lake/skew-scalar-extension-controls';scratch_parent.mkdir(parents=True,exist_ok=True)
    scratch=Path(tempfile.mkdtemp(prefix='controls-',dir=scratch_parent))
    for label,body,reject in [('positive-controls',positive,False)]+[
        (label,body,True) for label,body in negatives.items()]:
        path=scratch/(label+'.lean');path.write_text(header+body,encoding='utf-8',newline='\n')
        (OUT/(label+'.lean.txt')).write_bytes(path.read_bytes())
        run(label,['lake','env','lean',path.relative_to(ROOT).as_posix()],reject)
    require(hashes=={p:raw_digest(ROOT/p) for p in SOURCES},'Source changed during verification')
    require(input_hash==raw_digest(HISTORY/'inputs.json'),'Input manifest changed during verification')
    checked_inputs()
    positive_count=len(re.findall(r'^example',positive,re.M))
    write('validation.json',dict(status='PASS',completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        worker=EXECUTOR,lean_version=version.strip(),python_version=sys.version,mathlib_commit=revision,
        source_sha256=hashes,inputs_sha256=input_hash,reused_files=pins['reused_files'],
        source_pins_manifest=inputs['source_pins_manifest'],declaration_axioms=axioms,commands=RECORDS,
        elapsed_seconds=time.monotonic()-START,total_budget_seconds=600,
        new_public_declarations_audited=len(NAMES),new_modules_replayed=1,
        positive_controls=positive_count,negative_controls=len(negatives),
        artifact_sha256={MODULE:raw_digest(ROOT/'.lake/build/lib/lean'/(MODULE.replace('.','/')+'.olean'))},
        scope=inputs['mathematical_scope'],
        execution_limits=['Only ScalarExtensionTrace is kernel-replayed; imported proofs are reused',
          'Historical CI receipt is reused evidence, not a current remote CI execution',
          'Source hashes do not prove physical differential-source normalization']))
    print('PASS: '+str(len(NAMES))+' declaration/instance audits, one new-module replay, '+
        str(positive_count)+' positive and '+str(len(negatives))+' intended negative controls')

if __name__=='__main__':
    try: main()
    except Exception as error:
        if OUT is not None:
            write('validation.json',{'status':'FAIL','error':str(error),'commands':RECORDS,'worker':EXECUTOR})
        raise
