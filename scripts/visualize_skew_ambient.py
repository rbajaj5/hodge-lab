"""Render the checked ambient-derivation dependency map from its receipt."""
from pathlib import Path
import hashlib, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'formal/results/skew-ambient'
v=json.loads((OUT/'validation.json').read_text(encoding='utf-8'))
if v['status']!='PASS': raise RuntimeError('Passing receipt required')
for path,h in {**v['source_lf_sha256'],**v['reused_source_lf_sha256']}.items():
    raw=(ROOT/'formal'/path).read_bytes().replace(b'\r\n',b'\n')
    if hashlib.sha256(raw).hexdigest()!=h: raise RuntimeError('Checked source changed: '+path)
required=['ambientD_algebraMap','ambientD_coord','G_ne_zero','concrete_normal_factorization',
          'no_unchanged_derivation_on_divisor']
if not all('HodgeLab.OneReflectionSkew.AmbientDerivation.'+n in v['theorem_axioms'] for n in required):
    raise RuntimeError('Missing diagram dependency')

plt.rcParams['svg.hashsalt']='skew-ambient-derivation'
fig=plt.figure(figsize=(16,10),facecolor='#faf9f4')
fig.text(.045,.945,'An actual ambient derivation',fontsize=28,weight='bold',color='#17333b')
fig.text(.045,.903,'one-reflection-skew  •  characteristic zero  •  independent coordinates (U, r, w, t, z)',fontsize=13,color='#53696e')
ax=fig.add_axes([.045,.60,.91,.245]);ax.axis('off')
cards=[(0,'Polynomial ring',r'$P=\mathbb{Q}[U,r,w,t,z]$',r'$\partial_z:P\to P$','Previously checked chart polynomial'),
       (.35,'Localize differentials',r'$K=\mathrm{Frac}(P)$',r'$K\otimes_P\Omega_{P/\mathbb{Q}}\simeq\Omega_{K/\mathbb{Q}}$','Mathlib localization theorem'),
       (.70,'Construct the derivative',r'$D:K\to K$',r'$D(\iota p)=\iota(\partial_zp)$','Q-linear; Leibniz rule built in')]
for x,title,line1,line2,footer in cards:
    ax.add_patch(FancyBboxPatch((x,.04),.29,.92,boxstyle='round,pad=.008',facecolor='#e3efe9',edgecolor='#14737a',clip_on=False))
    ax.text(x+.015,.77,title,fontsize=14,weight='bold',color='#14737a')
    ax.text(x+.015,.53,line1,fontsize=18,color='#17333b')
    ax.text(x+.015,.32,line2,fontsize=15,color='#17333b')
    ax.text(x+.015,.12,footer,fontsize=10.5,color='#53696e')
for x in [.30,.65]:ax.annotate('',xy=(x+.04,.50),xytext=(x,.50),arrowprops={'arrowstyle':'->','color':'#14737a','lw':2})

table=fig.add_axes([.045,.405,.42,.125]);table.axis('off')
cells=table.table(cellText=[['U','r','w','t','z'],['0','0','0','0','1']],
                  rowLabels=['input','D'],cellLoc='center',loc='center',bbox=[.16,0,.84,1])
cells.auto_set_font_size(False);cells.set_fontsize(16)
for (row,col),cell in cells.get_celld().items():
    cell.set_edgecolor('#d2ded9');cell.set_facecolor('#e3efe9' if row==1 else '#ffffff')
    if col==-1:cell.set_fontsize(11)
fig.text(.045,.555,'Derived coordinate values',fontsize=15,weight='bold',color='#17333b')
fig.text(.54,.555,'Nonzero denominators proved in K',fontsize=15,weight='bold',color='#17333b')
fig.text(.54,.493,r'$z\ne0,\qquad DG=6z^5\ne0\quad\Longrightarrow\quad G\ne0$',fontsize=18,color='#14737a')
fig.text(.54,.44,'If G were zero, its derivative would be zero.\nThe existing coefficient theorem now has concrete inputs.',fontsize=12,color='#53696e',linespacing=1.5)

fig.text(.045,.335,'Instantiated coefficient identity',fontsize=16,weight='bold',color='#14737a')
fig.text(.045,.265,r'$-\frac{U^2}{2G^2}=D\!\left(\frac{U^2}{12z^5G}\right)+\frac{6z^5}{G}\,\frac{5U^2}{72z^{11}}$',fontsize=23,color='#17333b')
fig.text(.045,.185,'The domain boundary is also proved',fontsize=15,weight='bold',color='#996529')
fig.text(.045,.142,'On G = 0 with z ≠ 0, these same coordinate-derivative values would imply 0 = 6z⁵.\nThe normal derivative does not descend unchanged to the hypersurface.',fontsize=12.5,color='#17333b',linespacing=1.5)
fig.text(.045,.073,f"{v['new_theorems']} theorem audits  •  {v['new_modules_replayed']} new-module kernel replay  •  {v['positive_controls']} positive / {v['negative_controls']} negative proof controls",fontsize=13,color='#14737a',weight='bold')
fig.text(.045,.031,'Proof dependency map, not a geometric embedding. General differential forms, residue transport and a rational primitive remain separate.',fontsize=11,color='#53696e')
for extension in ['png','svg']:
    fig.savefig(ROOT/'visualizations'/('skew-ambient.'+extension),dpi=160,facecolor=fig.get_facecolor(),metadata={'Date':None} if extension=='svg' else None)
p=ROOT/'visualizations/skew-ambient.svg'
p.write_text('\n'.join(line.rstrip() for line in p.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8',newline='\n')
(OUT/'visualization-data.json').write_text(json.dumps({'coordinate_order':['U','r','w','t','z'],
 'proved_D_values':[0,0,0,0,1],'required_theorems':required,'ambient_field':'Frac(Q[U,r,w,t,z])',
 'scope':'Proof dependencies and coordinate values; no hypersurface primitive.'},indent=2)+'\n',encoding='utf-8',newline='\n')
print('PASS: checked ambient derivation and domain boundary rendered')
