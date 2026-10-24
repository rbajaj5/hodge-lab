"""Verify the new physical coefficient-field, quotient evaluation and all-sheet trace bridge with fresh receipts.

120 seconds per Lean command, 600 seconds per checker. Only the new module is
kernel-replayed. Historical scalar-extension/binding/basis receipts are inputs.
"""
from pathlib import Path
import datetime, hashlib, importlib.util, json, os, re, shlex, subprocess, sys, tempfile, time
from check_skew_extension import require, digest
from fresh_receipts import fresh_output_dir

ROOT = Path(__file__).resolve().parent
HISTORY = ROOT/'results/skew-physical-trace'
OUT = None
MODULE = 'HodgeLab.OneReflectionSkew.PhysicalTraceBridge'
DECLARATIONS = ['L', 'physicalA', 'physicalV', 'transformed', 'ChartField', 'original_basis', 'transformed_mem', 'chartA', 'chartV', 'physical_r_root', 'r_algebraic_chart', 'w_algebraic_chart', 'parameters_algebraic_chart', 'transformed_basis', 'transformed_independent', 'physicalBaseCoords', 'physical_base_independent', 'vRationalAlgebra', 'coeffRationalAlgebra', 'baseRationalAlgebra', 'qVCoeffTower', 'qCoeffBaseTower', 'qVBaseTower', 'genericBaseCoords', 'coordinateIndex', 'coordinateIndex_injective', 'generic_base_independent', 'ratfunc_image_mem', 'GenericCoordinateField', 'generic_coordinate_mem', 'generic_vfield_mem', 'generic_coefffield_mem', 'generic_coordinate_field_top', 'CoordinateFractions', 'coordinateFractionRationalAlgebra', 'genericCoordinateRationalAlgebra', 'topBaseRationalAlgebra', 'physicalCoordinateRationalAlgebra', 'genericCoordinateEquiv', 'genericCoordinateEquiv_X', 'baseToCurveRing', 'baseToCurve', 'baseToCurve_coordinates', 'baseToCurve_a', 'baseToCurve_v', 'baseToCurve_t', 'field_map_injective', 'baseToCurve_injective', 'curveBaseAlgebra', 'curveQBaseTower', 'baseToCurve_rational', 'curve_scalar_tower', 'mapped_polynomial', 'physical_r_aeval', 'physicalEval', 'physicalEval_theta', 'physicalEval_derivative', 'physicalEval_inverseDerivative', 'physicalEval_sourceScalar', 'physical_sourceScalar_ne_zero', 'physical_source_factor', 'splitToCurve', 'splitToCurve_injective', 'split_base_compatibility', 'curveRoots', 'curveRoots_injective', 'curveRoots_aeval', 'curveRoots_eval', 'physical_eq_full_split', 'curveRoots_exhaust', 'physicalSheet', 'physicalSheet_root', 'curveSigma', 'curveSigma_theta', 'physicalEval_eq_sheet', 'CurveTensor', 'finiteCurveTensor', 'freeCurveTensor', 'curveTensorBasis', 'curveTensor_finrank', 'curveSplitScalarTower', 'curveAllEvaluations', 'curveBetaHom', 'curveBetaHom_tmul', 'curveBetaHom_theta', 'curveBetaHom_surjective', 'curveBetaHom_bijective', 'curveBeta', 'curveBeta_tmul', 'curveBeta_scalar', 'trace_curve_baseChange', 'trace_curveBeta', 'trace_curve_sum', 'trace_allSheets', 'trace_curve_tmul', 'trace_curve_sourceScalar', 'trace_curve_two', 'physical_evaluation_not_trace']
NAMES = [MODULE+'.'+n for n in DECLARATIONS]
SOURCES = ['lean-toolchain','lakefile.toml','lake-manifest.json',
    'check_skew_extension.py','fresh_receipts.py','check_skew_physical_trace.py',
    'AuditSkewPhysicalTrace.lean','ReplaySkewPhysicalTrace.lean',
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
    inputs=json.loads((HISTORY/'inputs.json').read_text(encoding='utf-8'))
    ref=inputs['source_pins_manifest'];path=(ROOT.parent/ref['path']).resolve()
    require(path.is_relative_to(ROOT.parent.resolve()),'Manifest path escapes repository')
    require(raw_digest(path)==ref['sha256'],'Source-pin manifest changed')
    pins=json.loads(path.read_text(encoding='utf-8'))
    require(pins['parent']==inputs['notebook_parent'] and pins['upstream']==inputs['upstream_commit'],'Source commit mismatch')
    require(len(pins['files'])==inputs['pinned_file_count'],'Missing pinned source input')
    for name,pin in pins['files'].items():
        p=(ROOT.parent/name).resolve()
        require(p.is_relative_to(ROOT.parent.resolve()),'Pinned path escapes repository')
        require(raw_digest(p)==pin['sha256'] and p.stat().st_size==pin['bytes'],'Historical/source bytes changed: '+name)
    prior=json.loads((ROOT.parent/inputs['reused_source_receipt']).read_text(encoding='utf-8'))
    require(prior['status']=='PASS','Reused source-normalization receipt is not PASS')
    return inputs,pins

def main():
    global OUT,START
    START=time.monotonic()
    OUT=fresh_output_dir(ROOT,'skew-physical-trace',[HISTORY,
       ROOT.parent/'results/skew-physical-source-20261023',
       ROOT.parent/'results/skew-scalar-extension-20261023',
       ROOT.parent/'results/skew-distinct-roots-20261023',
       ROOT.parent/'results/ci-receipt-physical-cover-20261023',
       ROOT.parent/'results/skew-physical-curve-20261024',
       ROOT.parent/'results/skew-physical-trace-20261024/inputs'])
    print('Fresh receipts: '+str(OUT),flush=True)
    write('validation.json',{'status':'IN_PROGRESS'})
    inputs,pins=checked_inputs();input_hash=raw_digest(HISTORY/'inputs.json')
    hashes={p:raw_digest(ROOT/p) for p in SOURCES}
    snap=OUT/'source-snapshot';snap.mkdir()
    for name in SOURCES:
        p=snap/(name+'.txt');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/name).read_bytes())
    (snap/'inputs.json.txt').write_bytes((HISTORY/'inputs.json').read_bytes())
    write('source-inputs.json',{'source_sha256':hashes,'inputs_sha256':input_hash,'pinned_files':pins['files']})
    for name in SOURCES:
        if name.endswith('.lean'):
            require(not re.search(r'\b(sorry|admit|axiom|native_decide)\b',(ROOT/name).read_text(encoding='utf-8')),'Unproved token: '+name)
    actual=re.findall(r'^(?:@\[[^\n]*\]\s*)?(?:(?:noncomputable|local|private)\s+)*(?:def|abbrev|theorem|lemma|instance)\s+(\w+)',(ROOT/(MODULE.replace('.','/')+'.lean')).read_text(encoding='utf-8'),re.M)
    require(actual==DECLARATIONS,'Declaration inventory including local instances differs')
    version=run('version',['lake','env','lean','--version'])
    require('version 4.31.0,' in version,'Unexpected Lean version')
    revision=next(p['rev'] for p in json.loads((ROOT/'lake-manifest.json').read_text(encoding='utf-8'))['packages'] if p['name']=='mathlib')
    require(run('mathlib-head',['git','-C','.lake/packages/mathlib','rev-parse','HEAD']).strip()==revision,'Mathlib mismatch')
    run('build',['lake','build',MODULE])
    audit=run('axioms',['lake','env','lean','AuditSkewPhysicalTrace.lean'])
    axioms={n:[a.strip() for a in values.split(',') if a.strip()] for n,values in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]",audit)}
    for name in re.findall(r"'([^']+)' does not depend on any axioms",audit):axioms[name]=[]
    require(set(axioms)==set(NAMES),'Missing/new declaration audit')
    require(all(set(v)<={'propext','Classical.choice','Quot.sound'} for v in axioms.values()),'Unexpected axioms')
    replay=run('kernel-replay',['lake','env','lean','ReplaySkewPhysicalTrace.lean'])
    require('PASS '+MODULE in replay,'Kernel replay marker missing')
    header='import HodgeLab.OneReflectionSkew.PhysicalTraceBridge\nopen HodgeLab.OneReflectionSkew\nopen GenericDistinctRoots ScalarExtensionTrace PhysicalSourceNormalization\nopen PhysicalCurveRealization PhysicalTraceBridge TraceFreeBasis SplitTraceQuotient\nopen scoped TensorProduct BigOperators\nnoncomputable section\nlocal instance : Algebra ℚ VField := PhysicalTraceBridge.vRationalAlgebra\nlocal instance : Algebra ℚ CoeffField := PhysicalTraceBridge.coeffRationalAlgebra\nlocal instance : Algebra ℚ BaseField := PhysicalTraceBridge.baseRationalAlgebra\n'
    positive='\nexample : AlgebraicIndependent ℚ physicalBaseCoords := physical_base_independent\nexample : IsTranscendenceBasis ℚ transformed := transformed_basis\nexample : Function.Injective baseToCurve := baseToCurve_injective\nexample (i:Fin 3) : baseToCurve (genericBaseCoords i)=physicalBaseCoords i := baseToCurve_coordinates i\nexample : baseToCurve genericA=aChart r w := baseToCurve_a\nexample : baseToCurve genericV=vChart r w := baseToCurve_v\nexample : baseToCurve genericT=t := baseToCurve_t\nexample (q:ℚ) : baseToCurve (algebraMap ℚ BaseField q)=algebraMap ℚ L q := baseToCurve_rational q\nexample (q:ℚ) : algebraMap BaseField L (algebraMap ℚ BaseField q)=algebraMap ℚ L q := curve_scalar_tower q\nexample : genericPolynomial.map baseToCurve.toRingHom=PhysicalCoverBinding.physicalPolynomial physicalA physicalV := mapped_polynomial\nexample : Polynomial.aeval r genericPolynomial=0 := physical_r_aeval\nexample : physicalEval theta=r := physicalEval_theta\nexample : physicalEval derivativeElement=fR r w := physicalEval_derivative\nexample : physicalEval derivativeInverse=(fR r w)⁻¹ := physicalEval_inverseDerivative\nexample : physicalEval sourceScalar=r^11/(12*fR r w) := physicalEval_sourceScalar\nexample : physicalEval sourceScalar≠0 := physical_sourceScalar_ne_zero\nexample : physicalEval sourceScalar=r^11/fR r w/12 := physical_source_factor\nexample : Function.Injective splitToCurve := splitToCurve_injective\nexample (k:BaseField) : splitToCurve (baseToSplit k)=baseToCurve k := split_base_compatibility k\nexample : Function.Injective curveRoots := curveRoots_injective\nexample (j:Fin 18) : Polynomial.aeval (curveRoots j) genericPolynomial=0 := curveRoots_aeval j\nexample : PhysicalCoverBinding.physicalPolynomial physicalA physicalV=coverPolynomial 1 curveRoots := physical_eq_full_split\nexample (y:L) (h:Polynomial.aeval y genericPolynomial=0) : ∃j:Fin 18,curveRoots j=y := curveRoots_exhaust y h\nexample : curveRoots physicalSheet=r := physicalSheet_root\nexample : physicalEval=curveSigma physicalSheet := physicalEval_eq_sheet\nexample : Module.Finite L CurveTensor := inferInstance\nexample : Module.Free L CurveTensor := inferInstance\nexample : Module.finrank L CurveTensor=18 := curveTensor_finrank\nexample (l:L) (e:E) (j:Fin 18) : curveBeta (l⊗ₜ[BaseField]e) j=l*curveSigma j e := curveBeta_tmul l e j\nexample (l:L) : curveBeta (l⊗ₜ[BaseField](1:E))=fun _=>l := curveBeta_scalar l\nexample (e:E) : baseToCurve (Algebra.trace BaseField E e)=Algebra.trace L CurveTensor (1⊗ₜ[BaseField]e) := trace_curve_baseChange e\nexample (z:CurveTensor) : Algebra.trace L CurveTensor z=Algebra.trace L (SplitAlgebra L) (curveBeta z) := trace_curveBeta z\nexample (z:CurveTensor) : Algebra.trace L CurveTensor z=∑j,curveBeta z j := trace_curve_sum z\nexample (e:E) : baseToCurve (Algebra.trace BaseField E e)=∑j,curveSigma j e := trace_allSheets e\nexample (l:L) (e:E) : Algebra.trace L CurveTensor (l⊗ₜ[BaseField]e)=l*baseToCurve (Algebra.trace BaseField E e) := trace_curve_tmul l e\nexample : Algebra.trace L CurveTensor (1⊗ₜ[BaseField]sourceScalar)=0 := trace_curve_sourceScalar\nexample : Algebra.trace L CurveTensor ((2:L)⊗ₜ[BaseField](1:E))=36 := trace_curve_two\nexample : physicalEval (1:E)≠baseToCurve (Algebra.trace BaseField E 1) := physical_evaluation_not_trace\nexample : ¬IsUnit (algebraMap P Regular (NormalChart.chartPolynomial (K:=ℚ))) := regular_relation_not_unit\n'
    negatives={'collapsed-base-parameter-rejected': 'example : physicalA=0 := by\n  have h : physicalA≠0 := transformed_independent.ne_zero 1\n  simp only [h]\n', 'coefficient-image-zero-rejected': 'example : baseToCurve genericA=0 := by\n  rw [baseToCurve_a]\n  have h : physicalA≠0 := transformed_independent.ne_zero 1\n  simp only [h]\n', 'evaluation-as-trace-rejected': 'example : physicalEval (1:E)=baseToCurve (Algebra.trace BaseField E 1) := by\n  simp only [physical_evaluation_not_trace]\n', 'scalar-zero-on-sheet-rejected': 'example : physicalEval sourceScalar=0 := by\n  simp only [physical_sourceScalar_ne_zero]\n', 'scalar-sign-mutation-rejected': 'example : physicalEval sourceScalar= -physicalEval sourceScalar := by\n  have h : physicalEval sourceScalar≠ -physicalEval sourceScalar := by\n    intro h\n    have hh : (2:L)*physicalEval sourceScalar=0 := by linear_combination h\n    exact (mul_ne_zero (by norm_num : (2:L)≠0) physical_sourceScalar_ne_zero) hh\n  simp only [h]\n', 'dropped-twelfth-rejected': 'example : (12:L)*physicalEval sourceScalar=physicalEval sourceScalar := by\n  have h : (12:L)*physicalEval sourceScalar≠physicalEval sourceScalar := by\n    intro h\n    have hh : (11:L)*physicalEval sourceScalar=0 := by linear_combination h\n    exact (mul_ne_zero (by norm_num : (11:L)≠0) physical_sourceScalar_ne_zero) hh\n  simp only [h]\n', 'normalized-trace-rejected': 'example : Algebra.trace L CurveTensor ((2:L)⊗ₜ[BaseField](1:E))=1 := by\n  rw [trace_curve_two]\n  norm_num\n', 'dropped-tensor-scalar-rejected': 'example : Algebra.trace L CurveTensor ((2:L)⊗ₜ[BaseField](1:E))=18 := by\n  rw [trace_curve_two]\n  norm_num\n', 'single-sheet-constant-trace-rejected': 'example : (∑j:Fin 18,curveSigma j (1:E))=physicalEval (1:E) := by\n  simp only [map_one,Finset.sum_const,Finset.card_univ,Fintype.card_fin,nsmul_eq_mul,mul_one]\n  norm_num\n', 'forbidden-relation-inversion-rejected': 'example : IsUnit (algebraMap P Regular (NormalChart.chartPolynomial (K:=ℚ))) := by\n  simp only [regular_relation_not_unit]\n'}
    scratch_parent=ROOT/'.lake/skew-physical-trace-controls';scratch_parent.mkdir(parents=True,exist_ok=True)
    scratch=Path(tempfile.mkdtemp(prefix='controls-',dir=scratch_parent))
    for label,body,reject in [('positive-controls',positive,False)]+[(label,body,True) for label,body in negatives.items()]:
        p=scratch/(label+'.lean');p.write_text(header+body,encoding='utf-8',newline='\n')
        (OUT/(label+'.lean.txt')).write_bytes(p.read_bytes());run(label,['lake','env','lean',p.relative_to(ROOT).as_posix()],reject)
    require(hashes=={p:raw_digest(ROOT/p) for p in SOURCES},'Sources changed during check')
    require(input_hash==raw_digest(HISTORY/'inputs.json'),'Input manifest changed during check');checked_inputs()
    count=len(re.findall(r'^example',positive,re.M))
    write('validation.json',dict(status='PASS',completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
      worker=EXECUTOR,lean_version=version.strip(),python_version=sys.version,mathlib_commit=revision,
      source_sha256=hashes,inputs_sha256=input_hash,pinned_files=pins['files'],source_pins_manifest=inputs['source_pins_manifest'],
      declaration_axioms=axioms,commands=RECORDS,elapsed_seconds=time.monotonic()-START,total_budget_seconds=600,
      new_public_declarations_audited=len(NAMES),new_modules_replayed=1,positive_controls=count,negative_controls=len(negatives),
      artifact_sha256={MODULE:raw_digest(ROOT/'.lake/build/lib/lean'/(MODULE.replace('.','/')+'.olean'))},
      scope=inputs['mathematical_scope'],physical_source_pins=pins['protected_source'],
      execution_limits=['New module only kernel replay; cached imports reused','Prior successful CI is reused evidence, not new remote CI','No irreducibility, all-sheet physical form, cohomology, primitive or certificate claim']))
    print('PASS: '+str(len(NAMES))+' declarations, one new-module replay, '+str(count)+' positive, '+str(len(negatives))+' intended failures')

if __name__=='__main__':
    try:main()
    except Exception as error:
        if OUT is not None:write('validation.json',{'status':'FAIL','error':str(error),'commands':RECORDS,'worker':EXECUTOR})
        raise
