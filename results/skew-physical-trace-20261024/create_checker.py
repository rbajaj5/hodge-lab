from pathlib import Path
import hashlib,json,re
R=Path(__file__).resolve().parents[2]; F=R/'formal'; B=R/'results/skew-physical-trace-20261024'
M='HodgeLab.OneReflectionSkew.PhysicalTraceBridge'; P=F/(M.replace('.','/')+'.lean')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def js(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
names=re.findall(r'^(?:@\[[^\n]*\]\s*)?(?:(?:noncomputable|local|private)\s+)*(?:def|abbrev|theorem|lemma|instance)\s+(\w+)',P.read_text(encoding='utf-8'),re.M)
(F/'AuditSkewPhysicalTrace.lean').write_text('import '+M+'\n\n'+''.join('#print axioms '+M+'.'+n+'\n' for n in names),encoding='utf-8')
(F/'ReplaySkewPhysicalTrace.lean').write_text((F/'ReplaySkewPhysicalCurve.lean').read_text(encoding='utf-8').replace('PhysicalCurveRealization','PhysicalTraceBridge'),encoding='utf-8')
old=(F/'check_skew_physical_curve.py').read_text(encoding='utf-8')
s=old.replace('physical curve and allowed common-domain differential pullbacks','physical coefficient-field, quotient evaluation and all-sheet trace bridge').replace('skew-physical-curve','skew-physical-trace').replace('PhysicalCurveRealization','PhysicalTraceBridge').replace('SkewPhysicalCurve','SkewPhysicalTrace').replace('check_skew_physical_curve','check_skew_physical_trace')
a=s.index('DECLARATIONS = ');b=s.index('\nNAMES =',a);s=s[:a]+'DECLARATIONS = '+repr(names)+s[b:]
s=s.replace("ROOT.parent/'results/skew-physical-trace-20261024/inputs'","ROOT.parent/'results/skew-physical-curve-20261024',\n       ROOT.parent/'results/skew-physical-trace-20261024/inputs'")
a=s.index('    header=');b=s.index('    scratch_parent=',a)
header='''import HodgeLab.OneReflectionSkew.PhysicalTraceBridge
open HodgeLab.OneReflectionSkew
open GenericDistinctRoots ScalarExtensionTrace PhysicalSourceNormalization
open PhysicalCurveRealization PhysicalTraceBridge TraceFreeBasis SplitTraceQuotient
open scoped TensorProduct BigOperators
noncomputable section
local instance : Algebra ℚ VField := PhysicalTraceBridge.vRationalAlgebra
local instance : Algebra ℚ CoeffField := PhysicalTraceBridge.coeffRationalAlgebra
local instance : Algebra ℚ BaseField := PhysicalTraceBridge.baseRationalAlgebra
'''
positive='''
example : AlgebraicIndependent ℚ physicalBaseCoords := physical_base_independent
example : IsTranscendenceBasis ℚ transformed := transformed_basis
example : Function.Injective baseToCurve := baseToCurve_injective
example (i:Fin 3) : baseToCurve (genericBaseCoords i)=physicalBaseCoords i := baseToCurve_coordinates i
example : baseToCurve genericA=aChart r w := baseToCurve_a
example : baseToCurve genericV=vChart r w := baseToCurve_v
example : baseToCurve genericT=t := baseToCurve_t
example (q:ℚ) : baseToCurve (algebraMap ℚ BaseField q)=algebraMap ℚ L q := baseToCurve_rational q
example (q:ℚ) : algebraMap BaseField L (algebraMap ℚ BaseField q)=algebraMap ℚ L q := curve_scalar_tower q
example : genericPolynomial.map baseToCurve.toRingHom=PhysicalCoverBinding.physicalPolynomial physicalA physicalV := mapped_polynomial
example : Polynomial.aeval r genericPolynomial=0 := physical_r_aeval
example : physicalEval theta=r := physicalEval_theta
example : physicalEval derivativeElement=fR r w := physicalEval_derivative
example : physicalEval derivativeInverse=(fR r w)⁻¹ := physicalEval_inverseDerivative
example : physicalEval sourceScalar=r^11/(12*fR r w) := physicalEval_sourceScalar
example : physicalEval sourceScalar≠0 := physical_sourceScalar_ne_zero
example : physicalEval sourceScalar=r^11/fR r w/12 := physical_source_factor
example : Function.Injective splitToCurve := splitToCurve_injective
example (k:BaseField) : splitToCurve (baseToSplit k)=baseToCurve k := split_base_compatibility k
example : Function.Injective curveRoots := curveRoots_injective
example (j:Fin 18) : Polynomial.aeval (curveRoots j) genericPolynomial=0 := curveRoots_aeval j
example : PhysicalCoverBinding.physicalPolynomial physicalA physicalV=coverPolynomial 1 curveRoots := physical_eq_full_split
example (y:L) (h:Polynomial.aeval y genericPolynomial=0) : ∃j:Fin 18,curveRoots j=y := curveRoots_exhaust y h
example : curveRoots physicalSheet=r := physicalSheet_root
example : physicalEval=curveSigma physicalSheet := physicalEval_eq_sheet
example : Module.Finite L CurveTensor := inferInstance
example : Module.Free L CurveTensor := inferInstance
example : Module.finrank L CurveTensor=18 := curveTensor_finrank
example (l:L) (e:E) (j:Fin 18) : curveBeta (l⊗ₜ[BaseField]e) j=l*curveSigma j e := curveBeta_tmul l e j
example (l:L) : curveBeta (l⊗ₜ[BaseField](1:E))=fun _=>l := curveBeta_scalar l
example (e:E) : baseToCurve (Algebra.trace BaseField E e)=Algebra.trace L CurveTensor (1⊗ₜ[BaseField]e) := trace_curve_baseChange e
example (z:CurveTensor) : Algebra.trace L CurveTensor z=Algebra.trace L (SplitAlgebra L) (curveBeta z) := trace_curveBeta z
example (z:CurveTensor) : Algebra.trace L CurveTensor z=∑j,curveBeta z j := trace_curve_sum z
example (e:E) : baseToCurve (Algebra.trace BaseField E e)=∑j,curveSigma j e := trace_allSheets e
example (l:L) (e:E) : Algebra.trace L CurveTensor (l⊗ₜ[BaseField]e)=l*baseToCurve (Algebra.trace BaseField E e) := trace_curve_tmul l e
example : Algebra.trace L CurveTensor (1⊗ₜ[BaseField]sourceScalar)=0 := trace_curve_sourceScalar
example : Algebra.trace L CurveTensor ((2:L)⊗ₜ[BaseField](1:E))=36 := trace_curve_two
example : physicalEval (1:E)≠baseToCurve (Algebra.trace BaseField E 1) := physical_evaluation_not_trace
example : ¬IsUnit (algebraMap P Regular (NormalChart.chartPolynomial (K:=ℚ))) := regular_relation_not_unit
'''
negative={
'collapsed-base-parameter-rejected':'''example : physicalA=0 := by
  have h : physicalA≠0 := transformed_independent.ne_zero 1
  simp only [h]
''',
'coefficient-image-zero-rejected':'''example : baseToCurve genericA=0 := by
  rw [baseToCurve_a]
  have h : physicalA≠0 := transformed_independent.ne_zero 1
  simp only [h]
''',
'evaluation-as-trace-rejected':'''example : physicalEval (1:E)=baseToCurve (Algebra.trace BaseField E 1) := by
  simp only [physical_evaluation_not_trace]
''',
'scalar-zero-on-sheet-rejected':'''example : physicalEval sourceScalar=0 := by
  simp only [physical_sourceScalar_ne_zero]
''',
'scalar-sign-mutation-rejected':'''example : physicalEval sourceScalar= -physicalEval sourceScalar := by
  have h : physicalEval sourceScalar≠ -physicalEval sourceScalar := by
    intro h
    have hh : (2:L)*physicalEval sourceScalar=0 := by linear_combination h
    exact (mul_ne_zero (by norm_num : (2:L)≠0) physical_sourceScalar_ne_zero) hh
  simp only [h]
''',
'dropped-twelfth-rejected':'''example : (12:L)*physicalEval sourceScalar=physicalEval sourceScalar := by
  have h : (12:L)*physicalEval sourceScalar≠physicalEval sourceScalar := by
    intro h
    have hh : (11:L)*physicalEval sourceScalar=0 := by linear_combination h
    exact (mul_ne_zero (by norm_num : (11:L)≠0) physical_sourceScalar_ne_zero) hh
  simp only [h]
''',
'normalized-trace-rejected':'''example : Algebra.trace L CurveTensor ((2:L)⊗ₜ[BaseField](1:E))=1 := by
  rw [trace_curve_two]
  norm_num
''',
'dropped-tensor-scalar-rejected':'''example : Algebra.trace L CurveTensor ((2:L)⊗ₜ[BaseField](1:E))=18 := by
  rw [trace_curve_two]
  norm_num
''',
'single-sheet-constant-trace-rejected':'''example : (∑j:Fin 18,curveSigma j (1:E))=physicalEval (1:E) := by
  simp only [map_one,Finset.sum_const,Finset.card_univ,Fintype.card_fin,nsmul_eq_mul,mul_one]
  norm_num
''',
'forbidden-relation-inversion-rejected':'''example : IsUnit (algebraMap P Regular (NormalChart.chartPolynomial (K:=ℚ))) := by
  simp only [regular_relation_not_unit]
'''}
s=s[:a]+'    header='+repr(header)+'\n    positive='+repr(positive)+'\n    negatives='+repr(negative)+'\n'+s[b:]
s=s.replace("['New module only kernel replay; imports restored because previous cache expired','Prior successful CI is reused evidence, not new remote CI','No irreducibility, trace-tower comparison, residue/cohomology or primitive claim']","['New module only kernel replay; cached imports reused','Prior successful CI is reused evidence, not new remote CI','No irreducibility, all-sheet physical form, cohomology, primitive or certificate claim']")
(F/'check_skew_physical_trace.py').write_text(s,encoding='utf-8')
files=set(); imports={}; seen=set()
def walk(m):
 if m in seen:return
 seen.add(m);p=F/(m.replace('.','/')+'.lean')
 text=p.read_text(encoding='utf-8');children=re.findall(r'^import\s+(\S+)',text,re.M);imports[m]=children
 if m!=M:files.add(p.relative_to(R).as_posix())
 for child in children:
  if child.startswith('HodgeLab.'):walk(child)
walk(M)
prior='results/skew-physical-curve-20261024/remote-ci-40084595344/focused-receipt/validation.json'
files.update(['AGENTS.md','formal/lean-toolchain','formal/lakefile.toml','formal/lake-manifest.json','formal/fresh_receipts.py',
'results/skew-physical-curve-20261024/inputs/upstream/data/one-reflection-skew/instance.rec',
'results/skew-physical-curve-20261024/inputs/upstream/AGENTS.md',prior,
'results/skew-physical-curve-20261024/remote-ci-40084595344/ci-receipt-review.json',
'notes/skew-physical-curve-realization.md','notes/skew-scalar-extension-trace.md'])
manifest={'parent':'2bbbaa312642822c28483ba85cbbccf0af97d6dc','upstream':'e96be434bd55d6013d7a5854732cb317ca0e43e7','entry_module':M,'actual_notebook_import_graph':imports,'mathlib_commit':'fabf563a7c95a166b8d7b6efca11c8b4dc9d911f','files':{n:{'sha256':sha(R/n),'bytes':(R/n).stat().st_size} for n in sorted(files)},'protected_source':{'path':'results/skew-physical-curve-20261024/inputs/upstream/data/one-reflection-skew/instance.rec','sha256':'c6621c8845addf857ed30726f86449d5ea3310c7609641db9e326f9b85f10fbd','q':'1','A':'X0**3*Y0**3'},'reuse':'Prior proof modules and source bytes are immutable inputs; no prior focused checker rerun.'}
js(B/'source-pins.json',manifest)
h=F/'results/skew-physical-trace';h.mkdir(exist_ok=True)
js(h/'inputs.json',{'notebook_parent':manifest['parent'],'upstream_commit':manifest['upstream'],'source_pins_manifest':{'path':(B/'source-pins.json').relative_to(R).as_posix(),'sha256':sha(B/'source-pins.json')},'pinned_file_count':len(files),'reused_source_receipt':prior,'mathematical_scope':{'base':'Existing K=Q(v)(t)(a) injectively maps to existing Curve=AlgebraicClosure(Q(U,r,w,t)); exact a,v,t images and Q compatibility proved','quotient':'E=AdjoinRoot f, monic finite free rank18 algebra; no field or irreducibility assumption','evaluation':'Actual evaluation theta->r; derivative inverse and sourceScalar r^11/(12 f_r), nonzero on physical sheet','split':'Existing full splitting field embeds into Curve; all18 roots injective and exhaustive; physicalSheet matched by proof','tensor':'Curve tensor_K E, left Curve-algebra, finite free rank18, actual beta equivalence with Curve^18','trace':'Arbitrary-element base change, beta conjugacy and full18-sheet sums; scalar source trace0 distinct from its nonzero single-sheet image','unchanged_boundary':'Regular P[z^-1] maps from142 retained; no whole ambient fraction field specialization killing G','limits':['No quotient evaluation injectivity/irreducibility claim','No all-sheet physical differential-form/source-class identification','No four-form nonvanishing, minimal/whole hypersurface field, cohomology/GM, primitive, clearing, certificate or solve']}})
print(json.dumps({'declarations':len(names),'positive_controls':len(re.findall(r'^example',positive,re.M)),'negative_controls':len(negative),'pinned_files':len(files),'module_sha256':sha(P)},indent=2))
