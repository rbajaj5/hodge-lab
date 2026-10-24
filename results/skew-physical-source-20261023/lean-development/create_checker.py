from pathlib import Path
import hashlib,json,re
R=Path(__file__).resolve().parents[3]
F=R/'formal'
module='HodgeLab.OneReflectionSkew.PhysicalSourceNormalization'
source=F/(module.replace('.','/')+'.lean')
decls=re.findall(r'^(?:def|abbrev|theorem|lemma|instance) (\w+)',source.read_text(),re.M)
(F/'AuditSkewPhysicalSource.lean').write_text('import '+module+'\n\n'+'\n'.join('#print axioms '+module+'.'+n for n in decls)+'\n',encoding='utf-8')
(F/'ReplaySkewPhysicalSource.lean').write_text('''import LeanChecker

-- Replay only the new source-normalization module; all imported modules are reused.
#eval do
  Lean.initSearchPath (← Lean.findSysroot)
  replayFromImports `HodgeLab.OneReflectionSkew.PhysicalSourceNormalization
  IO.println "PASS HodgeLab.OneReflectionSkew.PhysicalSourceNormalization"
  (← IO.getStdout).flush
''',encoding='utf-8')
s=(F/'check_skew_scalar_extension.py').read_text()
s=s.replace('scalar-extension/trace bridge','physical-source normalization and actual four-form reduction')
s=s.replace('Historical distinct-root/binding/basis receipts','Historical scalar-extension/binding/basis receipts')
s=s.replace('skew-scalar-extension','skew-physical-source')
s=s.replace('ScalarExtensionTrace','PhysicalSourceNormalization')
s=s.replace('check_skew_scalar_extension.py','check_skew_physical_source_normalization.py')
s=s.replace('AuditSkewScalarExtension','AuditSkewPhysicalSource').replace('ReplaySkewScalarExtension','ReplaySkewPhysicalSource')
s=re.sub(r'DECLARATIONS = \[.*?\]\n', 'DECLARATIONS = '+repr(decls)+'\n',s,count=1)
s=s.replace("pins['reused_files']","pins['files']").replace("'reused_files':pins['files']","'pinned_files':pins['files']").replace("reused_files=pins['files']","pinned_files=pins['files']")
s=s.replace("len(pins['files']) >= 14", "len(pins['files']) == 44")
s=s.replace('Missing reused source/receipt pins','Missing pinned source/receipt inputs')
s=s.replace('Reused source or historical receipt changed:','Pinned source or historical receipt changed:')
s=s.replace("inputs['reused_distinct_root_receipt']","inputs['reused_scalar_extension_receipt']")
s=s.replace('Reused distinct-root receipt is not PASS','Reused scalar-extension receipt is not PASS')
s=s.replace("ROOT.parent/'results/ci-receipt-physical-cover-20261023'])", "ROOT.parent/'results/ci-receipt-physical-cover-20261023',\n        ROOT.parent/'results/skew-physical-source-20261023/inputs',\n        ROOT.parent/'results/skew-scalar-extension-20261023'])")
a=s.index('    header = """');b=s.index('    scratch_parent=',a)
controls='''    header = """import HodgeLab.OneReflectionSkew.PhysicalSourceNormalization
open Polynomial HodgeLab.OneReflectionSkew.ChartSubstitution
open HodgeLab.OneReflectionSkew.PhysicalCoverBinding
open HodgeLab.OneReflectionSkew.PhysicalSourceNormalization
open HodgeLab.OneReflectionSkew.GenericDistinctRoots
open HodgeLab.OneReflectionSkew.ScalarExtensionTrace
"""
    positive = """
section
variable {K : Type*} [Field K] [CharZero K] [Algebra ℚ K]
example (r w : K) (hr:r≠0) : (vChart r w*r-1)/r^2=w := vChart_inverse r w hr
example (r w : K) (hr:r≠0) : (physicalPolynomial (aChart r w) (vChart r w)).eval r=0 :=
  physical_cover_equation r w hr
example (V r w t:K) (hr:r≠0) : cubic (V/r) r w t=
    aChart r w*V^3+(t*vChart r w)*V^2+(t*(1-t^2)/7)*V+(1+t^6) :=
  cubic_coordinate_change V r w t hr
example (r w:K) (hr:r≠0) : jacobian r w=fR r w/r^14 := jacobian_eq r w hr
example (r w:K) (hr:r≠0) : d (aChart r w)*d (vChart r w)=jacobian r w•(d r*d w) :=
  two_form_change r w hr
example (U r w t:K) (hr:r≠0) : newFourForm (r*U) (aChart r w) (vChart r w) t=
    (fR r w/r^13)•oldFourForm U r w t := four_form_jacobian U r w t hr
example (V a v t:K) : newFourForm V a v t=-(d a*(d v*(d t*d V))) := fibre_last_orientation V a v t
example (U r w t z:K) (hr:r≠0) (hz:z≠0) (hf:fR r w≠0) :
    HodgeLab.OneReflectionSkew.ResidueNormalization.normalizedPoleCoefficient U r w t z • oldFourForm U r w t=
    ((5/72:K)*(r^11/fR r w)*((r*U)^2/z^11))•newFourForm (r*U) (aChart r w) (vChart r w) t :=
  normalized_source_form_transport U r w t z hr hz hf
example (a b c d0 V:K) (hΔ:delta a b c d0≠0) :
    (5/6:K)*V^2= -fibreP a b c d0 V*(bColumn0 a b c d0+bColumn1 a b c d0*V)-
      fibreP a b c d0 V*correctionPrime a b c d0 V+(5/6:K)*fibrePPrime a b c V*correction a b c d0 V :=
  b_column_rational a b c d0 V hΔ
example (D:Derivation ℚ K K) (a b c d0 V z:K) (ha:D a=0) (hb:D b=1) (hc:D c=0)
    (hd:D d0=0) (hV:D V=0) (hz:z≠0) (hcurve:z^6+fibreP a b c d0 V=0) :
    D (z⁻¹^5)=(5/6:K)*V^2/z^11 := b_variation D a b c d0 V z ha hb hc hd hV hz hcurve
example (D:Derivation ℚ K K) (a b c d0 V z:K) (ha:D a=0) (hb:D b=0) (hc:D c=0)
    (hd:D d0=0) (hV:D V=1) (hz:z≠0) (hΔ:delta a b c d0≠0) (hcurve:z^6+fibreP a b c d0 V=0) :
    (5/6:K)*V^2/z^11=(bColumn0 a b c d0+bColumn1 a b c d0*V)/z^5+D(correction a b c d0 V/z^5) :=
  b_column_relative_reduction D a b c d0 V z ha hb hc hd hV hz hΔ hcurve
example (r w t:K) (hr:r≠0) : baseWedge (aChart r w) (vChart r w) t (r^11/fR r w/12)=0 :=
  baseWedge_factor r w t hr
example (U r w t z:K) (hr:r≠0) (hz:z≠0) (hf:fR r w≠0)
    (hΔ:delta (aChart r w) (t*vChart r w) (t*(1-t^2)/7) (1+t^6)≠0)
    (hcurve:z^6+cubic U r w t=0) :
    HodgeLab.OneReflectionSkew.ResidueNormalization.normalizedPoleCoefficient U r w t z • oldFourForm U r w t=
      ((r^11/fR r w/12)*((bColumn0 (aChart r w) (t*vChart r w) (t*(1-t^2)/7) (1+t^6)+
      bColumn1 (aChart r w) (t*vChart r w) (t*(1-t^2)/7) (1+t^6)*(r*U))/z^5))•
      newFourForm (r*U) (aChart r w) (vChart r w) t+
      baseWedge (aChart r w) (vChart r w) t ((r^11/fR r w/12)*
      (correction (aChart r w) (t*vChart r w) (t*(1-t^2)/7) (1+t^6) (r*U)/z^5)) :=
  source_four_form_reduction U r w t z hr hz hf hΔ hcurve
example (a v r:K) (hr:r≠0) (hroot:(physicalPolynomial a v).eval r=0) :
    aChart r (recoverW r v)=a ∧ vChart r (recoverW r v)=v ∧
    fR r (recoverW r v)=(physicalPolynomial a v).derivative.eval r :=
  ⟨aChart_recover a v r hr hroot,vChart_recover r v hr,fR_recover a v r hr hroot⟩
end
example (j:Fin 18) : fR (roots j) (rootW j)≠0 := root_fR_ne_zero j
example (j:Fin 18) : sigma j sourceScalar=(roots j)^11/(12*fR (roots j) (rootW j)) := sourceScalar_image j
example : Algebra.trace BaseField E sourceScalar=0 := sourceScalar_trace
example : fR (2:ℚ) 1≠0 := by norm_num [fR_expanded,vChart,aChart,aCoeff]
example : delta (1:ℚ) 0 0 (-2)≠0 := by norm_num [delta]
"""
    negatives={
      'missing-r-nonzero-rejected':"""example : (vChart (0:ℚ) 1*0-1)/0^2=1 := by norm_num [vChart]
""",
      'missing-fr-nonzero-rejected':"""example : (5/72:ℚ)=((5/72:ℚ)*(1^11/fR 1 0)*(1^2/1^11))*(fR 1 0/1^13) := by
  norm_num [fR_expanded,vChart,aChart,aCoeff]
""",
      'orientation-sign-rejected':"""example : (5/72:ℚ)= -((5/72:ℚ)*(2^11/fR 2 1)*(2^2/1^11))*(fR 2 1/2^13) := by
  norm_num [fR_expanded,vChart,aChart,aCoeff]
""",
      'wrong-twelve-factor-rejected':"""example : (5/72:ℚ)=(1/6:ℚ)*(5/6:ℚ) := by norm_num
""",
      'missing-delta-nonzero-rejected':"""example : (5/6:ℚ)= -fibreP 0 0 0 0 1*(bColumn0 0 0 0 0+bColumn1 0 0 0 0*1)-
    fibreP 0 0 0 0 1*correctionPrime 0 0 0 0 1+(5/6:ℚ)*fibrePPrime 0 0 0 1*correction 0 0 0 0 1 := by
  norm_num [fibreP,fibrePPrime,bColumn0,bColumn1,correction,correctionPrime,delta,n0,n1,rNumerator,rNumeratorPrime]
""",
      'dropped-exact-correction-rejected':"""example : (5/6:ℚ)=(bColumn0 1 0 0 (-2)+bColumn1 1 0 0 (-2))/1^5 := by
  norm_num [bColumn0,bColumn1,n0,n1,delta]
""",
      'scalar-trace-one-rejected':"""example : Algebra.trace BaseField E sourceScalar=1 := by rw [sourceScalar_trace]; norm_num
"""}
'''
s=s[:a]+controls+s[b:]
s=s.replace("'Source hashes do not prove physical differential-source normalization'", "'The conditional curve-field four-form reduction is not a constructed residue/cohomology/connection comparison'")
s=s.replace("scope=inputs['mathematical_scope'],", "scope=inputs['mathematical_scope'],\n        physical_source_pins=pins['protected_source'],packet_pins=pins['benediamond_packet'],")
(F/'check_skew_physical_source_normalization.py').write_text(s,encoding='utf-8')
inputs={'notebook_parent':'bbb8aa406cd2a8b5ddb06d6e14358781b9c215e9','upstream_commit':'b790130d43b49ec0ddc6865d0bdc949eeeee2319',
'source_pins_manifest':{'path':'results/skew-physical-source-20261023/source-pins.json','sha256':'3b3fbbbcbb49a999d34638f2ddac47e16b5043554b88e43545e96b65df9d1a21'},
'reused_scalar_extension_receipt':'results/skew-scalar-extension-20261023/lean-development/checker-02/validation.json',
'mathematical_scope':{
'coefficient_field':'Any characteristic-zero field K with explicit Q-algebra; generic quotient specialization uses K=Q(v)(t)(a), L=f.SplittingField',
'chart':'r,z,f_r nonzero; V=rU, v=r^-1+rw, a=(1+r^6+w^6)/r^3; selected b-column requires Delta nonzero',
'curve_hypothesis':'z^6+cubic(U,r,w,t)=0 is explicit; no ambient-to-hypersurface residue map is constructed',
'new_result':'Exact coordinate/Jacobian/exterior-form normalization, explicit fibre-last sign, b variation, one packet b-column reduction, actual four-form representative plus d(H) wedge da wedge dv wedge dt, recovered roots and quotient source scalar image/trace zero',
'orientation':'Existing positive5/72 coefficient is fibre-first; moving fibre last changes sign. Packet global normal-last convention is separately pinned.',
'quotient_element':'sourceScalar=(1/12)*quotientWeight11 in E=AdjoinRoot f, not a full rank-two vector source',
'remaining':['Ambient residue source to hypersurface/cohomology realization','Connection/cohomology identification and source-class realization','Primitive','Global clearing','Certificate','Solve'],
'specialization_limit':'Chart nonzero and curve hypotheses are explicit. Generic root results are reused; singular/zero-denominator controls reject universal-specialization claims.'}}
(F/'results/skew-physical-source').mkdir(exist_ok=True)
(F/'results/skew-physical-source/inputs.json').write_text(json.dumps(inputs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(len(decls),'declarations')
print('module',hashlib.sha256(source.read_bytes()).hexdigest())
print('checker',hashlib.sha256((F/'check_skew_physical_source_normalization.py').read_bytes()).hexdigest())
