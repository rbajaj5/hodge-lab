"""Reproduce the target symmetry comparison and degree-four proof coverage."""
from pathlib import Path
from fractions import Fraction
import hashlib,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

R=Path(__file__).resolve().parents[1];O=R/'formal/results/skew-extension'
receipt=json.loads((O/'validation.json').read_text(encoding='utf-8'))
if receipt['status']!='PASS':raise RuntimeError('Passing Lean receipt required')
for name,h in receipt['source_lf_sha256'].items():
 if hashlib.sha256((R/'formal'/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest()!=h:
  raise RuntimeError('Checked source changed: '+name)
inputs=json.loads((O/'inputs.json').read_text(encoding='utf-8'))
def poly(target,key):
 p=next(x for x in inputs['pins'] if x['upstream_path']==f'data/{target}/record.json')
 raw=(R/p['path']).read_bytes().replace(b'\r\n',b'\n')
 if hashlib.sha256(raw).hexdigest()!=p['sha256']:raise RuntimeError('Input changed')
 return {tuple(e):Fraction(c) for c,e in json.loads(raw)[key]['terms']}
def defect(p,i):return {e:((-1)**(e[i]+e[i+3])-1)*c for e,c in p.items() if (e[i]+e[i+3])%2}
mixed=poly('mixed-polar','F');skew=poly('one-reflection-skew','F')
expected={(0,3,1,1,1,0):Fraction(-2)}
if [defect(mixed,i) for i in range(3)]!=[{}, {}, {}]:raise RuntimeError('Mixed symmetry mismatch')
if [defect(skew,i) for i in range(3)]!=[expected,{},expected]:raise RuntimeError('Skew defect mismatch')
for t in ['mixed-polar','one-reflection-skew']:
 if any(defect(poly(t,'A'),i) for i in range(3)):raise RuntimeError('Source character mismatch')
monomials=[(u,r,w,t) for u in range(5) for r in range(5) for w in range(5) for t in range(5) if u+r+w+t<=4]
if len(monomials)!=70:raise RuntimeError('Coverage mismatch')
data={'symmetry_defect_coefficients':{'mixed-polar':[0,0,0],'one-reflection-skew':[-2,0,-2]},
      'defect_monomial':[0,3,1,1,1,0],'source_defects_both':[0,0,0],
      'monomials':70,'components':4,'columns':280,'dual':[21,1,-1],'source_pairing':35,
      'new_theorems':receipt['new_theorems'],'new_modules_replayed':receipt['new_modules_replayed'],
      'limits':'No new searched family, direct mixed-polar transfer, or target primitive'}
(O/'visualization-data.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
plt.rcParams['svg.hashsalt']='hodge-lab-skew-extension'
fig=plt.figure(figsize=(15,8),facecolor='#faf9f4')
fig.text(.045,.935,'One-reflection-skew: what transfers, and what still needs proof',fontsize=20,color='#17333b',weight='bold')
fig.text(.045,.89,'Mixed-polar comparison + a completed Lean bridge for the existing degree-four exclusion',fontsize=12,color='#53696e')
ax=fig.add_axes([.045,.25,.44,.56]);ax.axis('off')
ax.text(0,1,'1  Check the actual target equation',fontsize=15,weight='bold',color='#17333b')
labels=['paired flip 0','paired flip 1','paired flip 2']
table=ax.table(cellText=[['mixed-polar','0','0','0'],['one-reflection-skew','−2T','0','−2T'],['both sources A','0','0','0']],
 colLabels=['F(σp) − F(p)',*labels],cellLoc='center',colWidths=[.34,.22,.22,.22],bbox=[0,.43,1,.42])
table.auto_set_font_size(False);table.set_fontsize(12)
for (i,j),cell in table.get_celld().items():
 cell.set_edgecolor('#c3d4d0');cell.set_facecolor('#e5f0eb' if i!=2 or j not in [1,3] else '#f5dfb8')
 if i==0:cell.set_facecolor('#173f48');cell.set_text_props(color='white',weight='bold',fontsize=11)
ax.text(0,.32,'T = X₁³ X₂ Y₀ Y₁.  Flip i negates (Xᵢ, Yᵢ).',fontsize=12,color='#17333b')
ax.text(0,.19,'The accepted ratio/square coordinates forget a sign\nthat the skew equation still needs.',fontsize=13,color='#8f5a22',linespacing=1.5)
ax.text(0,.01,'This blocks the same coordinate formula.\nIt does not exclude other covers or correspondences.',fontsize=11,color='#53696e',linespacing=1.5)
bx=fig.add_axes([.54,.25,.415,.56]);bx.axis('off')
bx.text(0,1,'2  Close a formal coverage gap',fontsize=15,weight='bold',color='#17333b')
boxes=[(.69,'Arbitrary numerator polynomials','Four components; total degree ≤ 4; fifth variable absent'),
       (.40,'Exact expansion and differentiation','70 monomials each → all 280 existing operator columns'),
       (.11,'Existing contradiction applies','Dual (21, 1, −1); source pairing 35 ≠ 0')]
for y,title,body in boxes:
 bx.add_patch(FancyBboxPatch((0,y),.99,.19,boxstyle='round,pad=.015',facecolor='#e4f1ec',edgecolor='#14737a',transform=bx.transAxes))
 bx.text(.025,y+.125,title,fontsize=12.5,weight='bold',color='#17333b',transform=bx.transAxes)
 bx.text(.025,y+.052,body,fontsize=10.3,color='#17333b',transform=bx.transAxes)
 if y>.2:bx.annotate('',xy=(.5,y-.07),xytext=(.5,y-.025),xycoords='axes fraction',arrowprops={'arrowstyle':'->','color':'#14737a','lw':1.5})
fig.text(.045,.135,'Checked: 23 theorem audits · 2 new-module kernel replays · 3 deliberate-error controls',fontsize=13,color='#14737a',weight='bold')
fig.text(.045,.087,'Same denominator a = 1 + r⁶ + w⁶; same bounded exclusion. Formal assurance increased; search coverage did not.',fontsize=11.5,color='#53696e')
fig.text(.045,.045,'Still open: target primitive, other denominator/degree families, source transport in Lean, and the 45-versus-504 comparison.',fontsize=11.5,color='#53696e')
for ext in ['svg','png']:
 fig.savefig(R/'visualizations'/('skew-extension.'+ext),dpi=170,facecolor=fig.get_facecolor(),metadata={'Date':None} if ext=='svg' else None)
p=R/'visualizations/skew-extension.svg'
p.write_text('\n'.join(x.rstrip() for x in p.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8',newline='\n')
print('PASS: visualization values reconstructed from pinned polynomials; Lean receipt bound')
