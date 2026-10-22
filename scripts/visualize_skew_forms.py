"""Render the checked exterior-product bridge; require the source-bound receipt."""
from pathlib import Path
import hashlib, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'formal/results/skew-forms'
v=json.loads((OUT/'validation.json').read_text(encoding='utf-8'))
if v['status']!='PASS':raise RuntimeError('Passing receipt required')
for p,h in {**v['source_lf_sha256'],**v['reused_source_lf_sha256']}.items():
    if hashlib.sha256((ROOT/'formal'/p).read_bytes().replace(b'\r\n',b'\n')).hexdigest()!=h:
        raise RuntimeError('Checked source changed: '+p)
required=['differential_wedge','normal_first_orientation','topCoefficient_volume',
          'volume_ne_zero','actual_form_reduction']
if not all('HodgeLab.OneReflectionSkew.DifferentialForms.'+n in v['theorem_axioms'] for n in required):
    raise RuntimeError('Missing diagram dependency')
plt.rcParams['svg.hashsalt']='skew-actual-differential-forms'
fig=plt.figure(figsize=(16,11),facecolor='#faf9f4')
fig.text(.045,.949,'From coefficients to actual differential forms',fontsize=26,weight='bold',color='#17333b')
fig.text(.045,.908,r'$K=\mathrm{Frac}(\mathbb{Q}[U,r,w,t,z])$  •  Kähler differentials over Q  •  exterior products over K',fontsize=14,color='#53696e')
ax=fig.add_axes([.045,.625,.91,.225]);ax.axis('off')
cards=[(0,'The actual 1-forms',r'$df\in\Omega_{K/\mathbb{Q}}$',r'$\alpha=dU\wedge dr\wedge dw\wedge dt$','Universal derivation, not symbols'),
       (.35,'The normal derivative',r'$Df=\partial_z f$',r'$df\wedge\alpha=Df\;\mathrm{vol}$','Generators, then the quotient rule'),
       (.70,'A nonzero volume',r'$\mathrm{vol}=\alpha\wedge dz$',r'$\lambda(\mathrm{vol})=1$','Localized basis + determinant')]
for x,title,a,b,c in cards:
    ax.add_patch(FancyBboxPatch((x,.03),.29,.93,boxstyle='round,pad=.008',facecolor='#e3efe9',edgecolor='#14737a',clip_on=False))
    for y,text,size,bold in [(.76,title,14,True),(.53,a,18,False),(.30,b,15,False),(.10,c,10.5,False)]:
        ax.text(x+.015,y,text,fontsize=size,weight='bold' if bold else 'normal',color='#17333b')
for x in [.30,.65]:ax.annotate('',xy=(x+.04,.5),xytext=(x,.5),arrowprops={'arrowstyle':'->','color':'#14737a','lw':2})
fig.text(.045,.566,'Orientation and repeated factors',fontsize=15,weight='bold',color='#14737a')
fig.text(.045,.517,r'$dz\wedge\alpha=(-1)^4\alpha\wedge dz=\mathrm{vol}$',fontsize=19,color='#17333b')
fig.text(.54,.517,r'$dU\wedge\alpha=dr\wedge\alpha=dw\wedge\alpha=dt\wedge\alpha=0$',fontsize=15,color='#17333b')
fig.text(.045,.447,'The checked reduction in the exterior algebra',fontsize=16,weight='bold',color='#14737a')
fig.text(.045,.375,r'$-\frac{U^2}{2G^2}\,\mathrm{vol}=d\!\left(\frac{U^2}{12z^5G}\right)\wedge\alpha+\frac{5U^2}{72z^{11}}\,\frac{dG}{G}\wedge\alpha$',fontsize=23,color='#17333b')
fig.text(.045,.314,'G = z⁶ + P(U,r,w,t), with the protected chart polynomial reused; z and G are nonzero in K.',fontsize=13,color='#53696e')
fig.text(.045,.237,'Precisely what this adds',fontsize=15,weight='bold',color='#14737a')
fig.text(.045,.193,'A genuine equality of exterior products, with a nonzero top form.\nThe expression d(f) ∧ α is the standard differential expression for the specific four-form fα.',fontsize=13,color='#17333b',linespacing=1.5)
fig.text(.045,.126,f"{v['new_theorems']} theorem audits  •  {v['new_modules_replayed']} new-module kernel replay  •  {v['positive_controls']} positive / {v['negative_controls']} negative proof controls",fontsize=13,weight='bold',color='#14737a')
fig.text(.045,.073,'Separate obligations: a general exterior derivative, residue transport, the physical U = x² pullback, trace and clearing.',fontsize=12,color='#996529')
fig.text(.045,.036,'Proof dependency diagram. No hypersurface primitive or accepted solve is claimed.',fontsize=11,color='#53696e')
for ext in ['png','svg']:
    fig.savefig(ROOT/'visualizations'/('skew-forms.'+ext),dpi=160,facecolor=fig.get_facecolor(),metadata={'Date':None} if ext=='svg' else None)
p=ROOT/'visualizations/skew-forms.svg'
p.write_text('\n'.join(s.rstrip() for s in p.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8',newline='\n')
(OUT/'visualization-data.json').write_text(json.dumps({'coordinate_order':['U','r','w','t','z'],
    'normal_first_swap_count':4,'normal_first_sign':1,'top_coefficient_of_volume':1,
    'base_wedge_coefficients':[0,0,0,0],'required_theorems':required,
    'scope':'Actual Kahler/exterior identity, not a general exterior differential or a residue map.'},indent=2)+'\n',encoding='utf-8',newline='\n')
print('PASS: actual differential-form bridge and limits rendered')
