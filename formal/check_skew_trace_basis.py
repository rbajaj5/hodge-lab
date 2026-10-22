"""Full split degree-18 trace-kernel audit; 120 seconds/command, 600 total.
Run python3 -O check_skew_trace_basis.py. No network, old proof replay, or
literal physical-cover instantiation. Required checks raise under Python -O.
"""
from pathlib import Path
import datetime, hashlib, json, os, re, shlex, subprocess, sys, time
import check_skew_extension as util
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results/skew-trace-basis'
require,digest=util.require,util.digest
START=time.monotonic(); RECORDS=[]
if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
def write(name,value):
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
MODULES=['HodgeLab.OneReflectionSkew.TraceKernel', 'HodgeLab.OneReflectionSkew.TraceFreeBasis', 'HodgeLab.OneReflectionSkew.SplitTraceQuotient']
NAMES=['HodgeLab.OneReflectionSkew.TraceKernel.trace_eq_last_coefficient', 'HodgeLab.OneReflectionSkew.TraceKernel.mem_ker_iff_last_coefficient_eq_zero', 'HodgeLab.OneReflectionSkew.TraceKernel.kernelCoordinates', 'HodgeLab.OneReflectionSkew.TraceKernel.kernelCoordinates_injective', 'HodgeLab.OneReflectionSkew.TraceKernel.kernelCoordinates_surjective', 'HodgeLab.OneReflectionSkew.TraceKernel.kernelEquiv', 'HodgeLab.OneReflectionSkew.TraceKernel.kernelBasis', 'HodgeLab.OneReflectionSkew.TraceKernel.kernelBasis_repr', 'HodgeLab.OneReflectionSkew.TraceKernel.kernelBasis_apply', 'HodgeLab.OneReflectionSkew.TraceKernel.kernelBasisSeventeen', 'HodgeLab.OneReflectionSkew.TraceKernel.slot_eleven_mem_ker', 'HodgeLab.OneReflectionSkew.TraceFreeBasis.coverPolynomial', 'HodgeLab.OneReflectionSkew.TraceFreeBasis.derivativeValue', 'HodgeLab.OneReflectionSkew.TraceFreeBasis.codifferent', 'HodgeLab.OneReflectionSkew.TraceFreeBasis.leading_coefficient', 'HodgeLab.OneReflectionSkew.TraceFreeBasis.cover_degree', 'HodgeLab.OneReflectionSkew.TraceFreeBasis.derivative_value', 'HodgeLab.OneReflectionSkew.TraceFreeBasis.derivative_value_ne_zero', 'HodgeLab.OneReflectionSkew.TraceFreeBasis.algebra_trace_eq_sum', 'HodgeLab.OneReflectionSkew.TraceFreeBasis.monomial_weight_sum', 'HodgeLab.OneReflectionSkew.TraceFreeBasis.trace_codifferent', 'HodgeLab.OneReflectionSkew.TraceFreeBasis.evaluationMatrix', 'HodgeLab.OneReflectionSkew.TraceFreeBasis.evaluation_matrix_det_ne_zero', 'HodgeLab.OneReflectionSkew.TraceFreeBasis.codifferentBasis', 'HodgeLab.OneReflectionSkew.TraceFreeBasis.codifferentBasis_apply', 'HodgeLab.OneReflectionSkew.TraceFreeBasis.trace_basis_initial', 'HodgeLab.OneReflectionSkew.TraceFreeBasis.trace_basis_last', 'HodgeLab.OneReflectionSkew.TraceFreeBasis.traceFreeBasis', 'HodgeLab.OneReflectionSkew.TraceFreeBasis.traceFreeBasis_apply', 'HodgeLab.OneReflectionSkew.TraceFreeBasis.trace_eq_coordinate', 'HodgeLab.OneReflectionSkew.TraceFreeBasis.slot_eleven_trace_zero', 'HodgeLab.OneReflectionSkew.TraceFreeBasis.traceFree_finrank', 'HodgeLab.OneReflectionSkew.TraceFreeBasis.trace_one', 'HodgeLab.OneReflectionSkew.TraceFreeBasis.remove_scalar_trace', 'HodgeLab.OneReflectionSkew.SplitTraceQuotient.cover_eval_root', 'HodgeLab.OneReflectionSkew.SplitTraceQuotient.evaluation', 'HodgeLab.OneReflectionSkew.SplitTraceQuotient.evaluation_mk', 'HodgeLab.OneReflectionSkew.SplitTraceQuotient.evaluation_root', 'HodgeLab.OneReflectionSkew.SplitTraceQuotient.evaluation_surjective', 'HodgeLab.OneReflectionSkew.SplitTraceQuotient.cover_ne_zero', 'HodgeLab.OneReflectionSkew.SplitTraceQuotient.evaluation_bijective', 'HodgeLab.OneReflectionSkew.SplitTraceQuotient.evaluationEquiv', 'HodgeLab.OneReflectionSkew.SplitTraceQuotient.evaluationEquiv_apply', 'HodgeLab.OneReflectionSkew.SplitTraceQuotient.evaluationEquiv_root', 'HodgeLab.OneReflectionSkew.SplitTraceQuotient.trace_transport', 'HodgeLab.OneReflectionSkew.SplitTraceQuotient.quotientCodifferent', 'HodgeLab.OneReflectionSkew.SplitTraceQuotient.quotientCodifferentBasis', 'HodgeLab.OneReflectionSkew.SplitTraceQuotient.quotientCodifferentBasis_apply', 'HodgeLab.OneReflectionSkew.SplitTraceQuotient.trace_quotientCodifferent', 'HodgeLab.OneReflectionSkew.SplitTraceQuotient.derivative_mul_quotientCodifferent', 'HodgeLab.OneReflectionSkew.SplitTraceQuotient.quotient_derivative_isUnit', 'HodgeLab.OneReflectionSkew.SplitTraceQuotient.trace_quotient_basis_initial', 'HodgeLab.OneReflectionSkew.SplitTraceQuotient.trace_quotient_basis_last', 'HodgeLab.OneReflectionSkew.SplitTraceQuotient.quotientTraceFreeBasis', 'HodgeLab.OneReflectionSkew.SplitTraceQuotient.quotientTraceFreeBasis_apply', 'HodgeLab.OneReflectionSkew.SplitTraceQuotient.quotient_traceFree_finrank']
SOURCES=['lean-toolchain','lakefile.toml','lake-manifest.json','check_skew_extension.py','check_skew_trace_basis.py','AuditSkewTraceBasis.lean','ReplaySkewTraceBasis.lean']+[m.replace('.','/')+'.lean' for m in MODULES]
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
    START=time.monotonic();OUT.mkdir(parents=True,exist_ok=True)
    write('validation.json',{'status':'IN_PROGRESS'})
    hashes={p:digest(ROOT/p) for p in SOURCES}
    pins=json.loads((OUT/'inputs.json').read_text(encoding='utf-8'))
    for p,h in pins['context_receipt_lf_sha256'].items():
        require(digest(ROOT.parent/p)==h,'Historical context receipt changed: '+p)
    for p in SOURCES:
        if p.endswith('.lean'):
            require(not re.search(r'\b(sorry|admit|axiom|native_decide)\b',(ROOT/p).read_text(encoding='utf-8')),'Unproved token '+p)
    version=run('version',['lake','env','lean','--version'])
    require('version 4.31.0,' in version,'Unexpected Lean version')
    manifest=json.loads((ROOT/'lake-manifest.json').read_text(encoding='utf-8'))
    rev=next(p['rev'] for p in manifest['packages'] if p['name']=='mathlib')
    require(run('mathlib-head',['git','-C','.lake/packages/mathlib','rev-parse','HEAD']).strip()==rev,'Mathlib mismatch')
    run('build',['lake','build',MODULES[-1]])
    audit=run('axioms',['lake','env','lean','AuditSkewTraceBasis.lean'])
    axioms={n:[a.strip() for a in values.split(',') if a.strip()] for n,values in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]",audit)}
    for n in re.findall(r"'([^']+)' does not depend on any axioms",audit):axioms[n]=[]
    require(set(axioms)==set(NAMES),'Missing or unexpected declaration audits')
    require(all(set(a)<={'propext','Classical.choice','Quot.sound'} for a in axioms.values()),'Unexpected axiom')
    replay=run('kernel-replay',['lake','env','lean','ReplaySkewTraceBasis.lean'])
    for mod in MODULES:require('PASS '+mod in replay,'Missing replay '+mod)
    header="""import HodgeLab.OneReflectionSkew.SplitTraceQuotient
open HodgeLab.OneReflectionSkew.TraceFreeBasis HodgeLab.OneReflectionSkew.SplitTraceQuotient
def rootsQ (j : Fin 18) : ℚ := (j.val : ℚ)
theorem rootsQ_injective : Function.Injective rootsQ := by
  intro i j h
  apply Fin.ext
  change (i.val : ℚ) = (j.val : ℚ) at h
  exact_mod_cast h
"""
    scratch=ROOT/'.lake/skew-trace-basis-controls';scratch.mkdir(parents=True,exist_ok=True)
    positive="""
example : (coverPolynomial (2 : ℚ) rootsQ).leadingCoeff = 2 := leading_coefficient 2 rootsQ
example : (coverPolynomial (2 : ℚ) rootsQ).natDegree = 18 := cover_degree 2 (by norm_num) rootsQ
example : Algebra.trace ℚ (SplitAlgebra ℚ) (codifferent 2 rootsQ 17) = 1/2 := by
  rw [trace_codifferent 2 rootsQ rootsQ_injective]; norm_num
example : Algebra.trace ℚ (SplitAlgebra ℚ) (codifferent 2 rootsQ 11) = 0 :=
  slot_eleven_trace_zero 2 rootsQ rootsQ_injective
example : codifferent (2 : ℚ) rootsQ 11 ≠ 0 := by
  rw [← codifferentBasis_apply 2 (by norm_num) rootsQ rootsQ_injective]
  exact (codifferentBasis 2 (by norm_num) rootsQ rootsQ_injective).ne_zero 11
example : Module.finrank ℚ (LinearMap.ker (Algebra.trace ℚ (CoverAlgebra 2 rootsQ))) = 17 :=
  quotient_traceFree_finrank 2 (by norm_num) rootsQ rootsQ_injective
example : Algebra.trace ℚ (CoverAlgebra 2 rootsQ)
    (quotientCodifferent 2 (by norm_num) rootsQ rootsQ_injective 17) = 1/2 := by
  rw [trace_quotientCodifferent]; norm_num
"""
    p=scratch/'positive.lean';p.write_text(header+positive,encoding='utf-8',newline='\n')
    (OUT/'positive.lean.txt').write_bytes(p.read_bytes())
    run('positive-controls',['lake','env','lean',p.relative_to(ROOT).as_posix()])
    negatives={
      'missing-leading-coefficient':"""example : Algebra.trace ℚ (CoverAlgebra 2 rootsQ)
    (quotientCodifferent 2 (by norm_num) rootsQ rootsQ_injective 17) = 1 := by
  rw [trace_quotientCodifferent]; norm_num
""",
      'wrong-kernel-dimension':"""example : Module.finrank ℚ (LinearMap.ker (Algebra.trace ℚ (CoverAlgebra 2 rootsQ))) = 18 := by
  rw [quotient_traceFree_finrank 2 (by norm_num) rootsQ rootsQ_injective]; norm_num
""",
      'trace-zero-means-zero':"""example : codifferent (2 : ℚ) rootsQ 11 = 0 := by
  have h : codifferent (2 : ℚ) rootsQ 11 ≠ 0 := by
    rw [← codifferentBasis_apply 2 (by norm_num) rootsQ rootsQ_injective]
    exact (codifferentBasis 2 (by norm_num) rootsQ rootsQ_injective).ne_zero 11
  simp only [h]
"""}
    for label,body in negatives.items():
        p=scratch/(label+'.lean');p.write_text(header+body,encoding='utf-8',newline='\n')
        (OUT/(label+'.lean.txt')).write_bytes(p.read_bytes())
        run(label,['lake','env','lean',p.relative_to(ROOT).as_posix()],True)
    require(hashes=={p:digest(ROOT/p) for p in SOURCES},'Sources changed during verification')
    for p,h in pins['context_receipt_lf_sha256'].items():require(digest(ROOT.parent/p)==h,'Prior receipt changed')
    write('validation.json',{'status':'PASS','completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'lean_version':version.strip(),'python_version':sys.version,'mathlib_commit':rev,
      'source_lf_sha256':hashes,'inputs_lf_sha256':digest(OUT/'inputs.json'),
      'declaration_axioms':axioms,'commands':RECORDS,'elapsed_seconds':time.monotonic()-START,
      'total_budget_seconds':600,'new_declarations_audited':len(NAMES),'new_modules_replayed':len(MODULES),
      'positive_controls':7,'negative_controls':3,
      'artifact_sha256':{m:hashlib.sha256((ROOT/'.lake/build/lib/lean'/(m.replace('.','/')+'.olean')).read_bytes()).hexdigest() for m in MODULES},
      'scope':'Full split degree-18 algebra and quotient; actual algebra trace; derivative-weighted basis; first17 vectors form trace kernel; last trace 1/a18.',
      'limits':['Field K, nonzero leading coefficient, 18 explicitly distinct roots required',
        'No irreducibility assumed; all18 split components retained',
        'Characteristic zero required only for scalar trace/18 removal',
        'No descent over the unsplit physical coefficient field or literal physical-polynomial/source binding',
        'No connection, primitive, homogeneous certificate, trace-and-clearing replay or HasCertificate',
        'Mathlib imports and previous proofs not newly kernel-replayed; context receipt hashes are provenance only']})
    print('PASS: '+str(len(NAMES))+' declaration audits, three module kernel replays, seven positive and three negative controls')

if __name__=='__main__':
    try:main()
    except Exception as error:
        OUT.mkdir(parents=True,exist_ok=True)
        write('validation.json',{'status':'FAIL','error':str(error),'commands':RECORDS})
        raise
