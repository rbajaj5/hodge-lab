from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[2]
FORMAL=ROOT/'formal';BATCH=Path(__file__).resolve().parent
module='HodgeLab.OneReflectionSkew.PhysicalCurveRealization'
source=(FORMAL/(module.replace('.','/')+'.lean')).read_text(encoding='utf-8')
pattern=r'^(?:@\[[^\n]*\]\s*)?(?:(?:noncomputable|local|private)\s+)*(?:def|abbrev|theorem|lemma|instance)\s+(\w+)'
names=re.findall(pattern,source,re.M)
if len(names)!=len(set(names)):raise RuntimeError('Duplicate declaration names')
(FORMAL/'AuditSkewPhysicalCurve.lean').write_text('import '+module+'\n\n'+''.join('#print axioms '+module+'.'+n+'\n' for n in names),encoding='utf-8')
(FORMAL/'ReplaySkewPhysicalCurve.lean').write_text('''import LeanChecker

-- Replay only the new module; imported modules are dependency evidence.
#eval do
  Lean.initSearchPath (← Lean.findSysroot)
  replayFromImports `HodgeLab.OneReflectionSkew.PhysicalCurveRealization
  IO.println "PASS HodgeLab.OneReflectionSkew.PhysicalCurveRealization"
  (← IO.getStdout).flush
''',encoding='utf-8')
# Pin transitive local imported sources, without rerunning any old checker.
pinned=set();todo=re.findall(r'^import (HodgeLab\.[\w.]+)',source,re.M)
while todo:
 name=todo.pop();path='formal/'+name.replace('.','/')+'.lean'
 if path in pinned:continue
 pinned.add(path);todo+=re.findall(r'^import (HodgeLab\.[\w.]+)',(ROOT/path).read_text(encoding='utf-8'),re.M)
pinned.update(['AGENTS.md','formal/lean-toolchain','formal/lakefile.toml','formal/lake-manifest.json','formal/fresh_receipts.py',
 'results/skew-physical-source-20261023/source-pins.json',
 'results/skew-physical-source-20261023/coordinator-ci/40051515847/focused/validation.json',
 'results/skew-physical-source-20261023/coordinator-ci/40051515847/ci-receipt-review.json',
 'results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json',
 'results/skew-physical-curve-20261024/inputs/upstream/data/one-reflection-skew/instance.rec',
 'results/skew-physical-curve-20261024/inputs/upstream/AGENTS.md'])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins={'parent':'e2182223a0395cfb758a2ee09e304eb940b7a67a','upstream':'e96be434bd55d6013d7a5854732cb317ca0e43e7',
'files':{p:{'sha256':sha(ROOT/p),'bytes':(ROOT/p).stat().st_size} for p in sorted(pinned)},
'protected_source':{'path':'results/skew-physical-curve-20261024/inputs/upstream/data/one-reflection-skew/instance.rec','q':'1','A':'X0**3*Y0**3','sha256':'c6621c8845addf857ed30726f86449d5ea3310c7609641db9e326f9b85f10fbd'},
'reuse':'Imported mathematical sources and prior full CI are immutable evidence; no historical focused checker rerun'}
(BATCH/'source-pins.json').write_text(json.dumps(pins,indent=2)+'\n',encoding='utf-8')
history=FORMAL/'results/skew-physical-curve';history.mkdir(exist_ok=True)
inputs={'notebook_parent':pins['parent'],'upstream_commit':pins['upstream'],
'source_pins_manifest':{'path':'results/skew-physical-curve-20261024/source-pins.json','sha256':sha(BATCH/'source-pins.json')},
'pinned_file_count':len(pinned),'reused_source_receipt':'results/skew-physical-source-20261023/coordinator-ci/40051515847/focused/validation.json',
'mathematical_scope':{'base':'FractionRing(MvPolynomial(Fin4,Q)), four coordinates algebraically independent',
'curve':'AlgebraicClosure Base, constructed z^6=-cubic and x^2=U; actual protected F=0 and A=x^3',
'allowed_domain':'Regular=P[z^-1], P=Q[U,r,w,t,z]; two compatible Q-algebra maps to old Ambient.K and Curve',
'forms':'Universal Kaehler/exterior pullbacks, all five coordinate differentials, common normalized four-form, curve and square differential relations',
'nonzero':'r,z,f_r,Delta proved nonzero in this generic realization; no claim for every specialization',
'new_result':'Concrete realized_source_reduction without residual curve/chart hypotheses',
'forbidden':'No whole ambient fraction field map killing nonzeroG; G not a unit of Regular; no unchanged normal derivation',
'limits':['Not identified with whole irreducible hypersurface function field or minimal root field','No comparison with prior Q(v)(t)(a) splitting-field tower','No general residue map, deRham/cohomology connection, primitive, certificate or solve']}}
(history/'inputs.json').write_text(json.dumps(inputs,indent=2)+'\n',encoding='utf-8')
old=(FORMAL/'check_skew_physical_source_normalization.py').read_text(encoding='utf-8')
head=old[:old.index('\ndef checked_inputs():')]
head=head.replace('physical-source normalization and actual four-form reduction','physical curve and allowed common-domain differential pullbacks').replace("HISTORY = ROOT/'results/skew-physical-source'","HISTORY = ROOT/'results/skew-physical-curve'").replace("MODULE = 'HodgeLab.OneReflectionSkew.PhysicalSourceNormalization'","MODULE = '"+module+"'")
head=re.sub(r'^DECLARATIONS = .*$', 'DECLARATIONS = '+repr(names),head,flags=re.M)
head=head.replace('check_skew_physical_source_normalization.py','check_skew_physical_curve.py').replace('AuditSkewPhysicalSource','AuditSkewPhysicalCurve').replace('ReplaySkewPhysicalSource','ReplaySkewPhysicalCurve')
body=r'''
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
    OUT=fresh_output_dir(ROOT,'skew-physical-curve',[HISTORY,
       ROOT.parent/'results/skew-physical-source-20261023',
       ROOT.parent/'results/skew-scalar-extension-20261023',
       ROOT.parent/'results/skew-distinct-roots-20261023',
       ROOT.parent/'results/ci-receipt-physical-cover-20261023',
       ROOT.parent/'results/skew-physical-curve-20261024/inputs'])
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
    audit=run('axioms',['lake','env','lean','AuditSkewPhysicalCurve.lean'])
    axioms={n:[a.strip() for a in values.split(',') if a.strip()] for n,values in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]",audit)}
    for name in re.findall(r"'([^']+)' does not depend on any axioms",audit):axioms[name]=[]
    require(set(axioms)==set(NAMES),'Missing/new declaration audit')
    require(all(set(v)<={'propext','Classical.choice','Quot.sound'} for v in axioms.values()),'Unexpected axioms')
    replay=run('kernel-replay',['lake','env','lean','ReplaySkewPhysicalCurve.lean'])
    require('PASS '+MODULE in replay,'Kernel replay marker missing')
    header="""import HodgeLab.OneReflectionSkew.PhysicalCurveRealization
open MvPolynomial HodgeLab.OneReflectionSkew
open PhysicalCurveRealization PhysicalSourceNormalization ChartSubstitution NormalChart
open ResidueNormalization
"""
    positive="""
example : Function.Injective (algebraMap BasePoly Curve) := polynomial_embedding_injective
example : AlgebraicIndependent ℚ param := parameters_independent
example : x^2=U := x_square
example : x≠0 := x_ne_zero
example : z≠0 := z_ne_zero
example : z^6+cubic U r w t=0 := curve_equation
example : CoordinateComparison.skewF (physicalPoint x r w t z)=0 := protected_F_zero
example : CoordinateComparison.skewA (physicalPoint x r w t z)=x^3 := protected_A_image
example (i:Fin 6) : physicalMap (X i)=physicalPoint x r w t z i := physicalMap_X i
example (i:Fin 5) : chartMap (X i)=coords i := chartMap_X i
example : chartMap (chartPolynomial (K:=ℚ))=0 := chartMap_relation
example (i:Fin 5) : regularToCurve (algebraMap P Regular (X i))=coords i := regularToCurve_coord i
example (i:Fin 5) : regularToAmbient (algebraMap P Regular (X i))=AmbientDerivation.coord i := regularToAmbient_coord i
example (i:Fin 5) : kaehlerPull regularToCurve
    (KaehlerDifferential.D ℚ Regular (algebraMap P Regular (X i)))=
    KaehlerDifferential.D ℚ Curve (coords i) := curve_differentials i
example (i:Fin 5) : curveExterior (regularD (algebraMap P Regular (X i)))=d (coords i) := curve_exterior_coordinates i
example : ambientExterior regularSource=DifferentialForms.residueScalar•DifferentialForms.alpha := ambient_source
example : curveExterior regularSource=normalizedPoleCoefficient U r w t z•oldFourForm U r w t := curve_source
example : (6*z^5)•KaehlerDifferential.D ℚ Curve z+KaehlerDifferential.D ℚ Curve (cubic U r w t)=0 := curve_differential_relation
example : (2*x)•KaehlerDifferential.D ℚ Curve x=KaehlerDifferential.D ℚ Curve U := square_cover_differential
example : fR r w≠0 := cover_derivative_ne_zero
example : delta (aChart r w) (t*vChart r w) (t*(1-t^2)/7) (1+t^6)≠0 := physical_delta_ne_zero
example : curveExterior regularSource=
    ((r^11/fR r w/12)*((bColumn0 (aChart r w) (t*vChart r w) (t*(1-t^2)/7) (1+t^6)+
    bColumn1 (aChart r w) (t*vChart r w) (t*(1-t^2)/7) (1+t^6)*(r*U))/z^5))•
    newFourForm (r*U) (aChart r w) (vChart r w) t+
    baseWedge (aChart r w) (vChart r w) t ((r^11/fR r w/12)*
      (correction (aChart r w) (t*vChart r w) (t*(1-t^2)/7) (1+t^6) (r*U)/z^5)) := realized_source_reduction
example (f:AmbientDerivation.K→+*Curve) (h:f AmbientDerivation.G=0) : False := no_ambient_field_specialization f h
example : ¬IsUnit (algebraMap P Regular (chartPolynomial (K:=ℚ))) := regular_relation_not_unit
example (D:Derivation ℚ Curve Curve) (hU:D U=0) (hr:D r=0) (hw:D w=0) (ht:D t=0) (hz:D z=1) : False := no_unchanged_normal_derivation D hU hr hw ht hz
"""
    negatives={
      'parameter-collapse-rejected':"example : U=0 := by simp only [param_ne_zero 0]\n",
      'zero-sixth-root-rejected':"example : z=0 := by simp only [z_ne_zero]\n",
      'relation-not-killed-rejected':"example : chartMap (chartPolynomial (K:=ℚ))≠0 := by rw [chartMap_relation]; norm_num\n",
      'ambient-field-specialization-rejected':"""example : ∃f:AmbientDerivation.K→+*Curve, f AmbientDerivation.G=0 := by
  have h : ¬∃f:AmbientDerivation.K→+*Curve, f AmbientDerivation.G=0 := by
    rintro ⟨f,hf⟩;exact no_ambient_field_specialization f hf
  simp only [h]
""",
      'inverted-curve-equation-rejected':"example : IsUnit (algebraMap P Regular (chartPolynomial (K:=ℚ))) := by simp only [regular_relation_not_unit]\n",
      'coefficient-sign-rejected':"example : (5/72:ℚ)= -(5/72:ℚ) := by norm_num\n",
      'fr-sign-mutation-rejected':"example : MvPolynomial.eval (fun _:Fin 4=>(1:ℚ)) frPolynomial=3 := by norm_num [frPolynomial,map_ofNat]\n",
      'delta-clearing-zero-mutation-rejected':"example : MvPolynomial.eval (fun _:Fin 4=>(0:ℚ)) deltaPolynomial=0 := by norm_num [deltaPolynomial,map_ofNat]\n"}
    scratch_parent=ROOT/'.lake/skew-physical-curve-controls';scratch_parent.mkdir(parents=True,exist_ok=True)
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
      execution_limits=['New module only kernel replay; imports restored because previous cache expired','Prior successful CI is reused evidence, not new remote CI','No irreducibility, trace-tower comparison, residue/cohomology or primitive claim']))
    print('PASS: '+str(len(NAMES))+' declarations, one new-module replay, '+str(count)+' positive, '+str(len(negatives))+' intended failures')

if __name__=='__main__':
    try:main()
    except Exception as error:
        if OUT is not None:write('validation.json',{'status':'FAIL','error':str(error),'commands':RECORDS,'worker':EXECUTOR})
        raise
'''
(FORMAL/'check_skew_physical_curve.py').write_text(head+body,encoding='utf-8')
print(json.dumps({'declarations':len(names),'pinned_inputs':len(pinned),'names':names}))
