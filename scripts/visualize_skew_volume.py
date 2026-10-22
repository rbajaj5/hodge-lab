"""Render the actual Euler-volume matrix and its coefficient normalization."""
from fractions import Fraction
from pathlib import Path
import hashlib,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

R=Path(__file__).resolve().parents[1];O=R/'formal/results/skew-volume'
v=json.loads((O/'validation.json').read_text(encoding='utf-8'))
if v['status']!='PASS':raise RuntimeError('Passing volume receipt required')
for name,h in {**v['source_lf_sha256'],**v['reused_source_lf_sha256']}.items():
    if hashlib.sha256((R/'formal'/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest()!=h:
        raise RuntimeError('Checked proof source changed '+name)
raw=(O/'independent.json').read_bytes()
if hashlib.sha256(raw).hexdigest()!=v['independent_receipt_lf_sha256']:
    raise RuntimeError('Independent reconstruction changed')
d=json.loads(raw)

def poly(terms):
    if not terms:return '$0$'
    out=[]
    for coefficient,e in terms:
        c=Fraction(coefficient);m=''.join(s if n==1 else s+'^{'+str(n)+'}' for s,n in zip(['x','r','w','t','z'],e) if n)
        a=abs(c);number='' if a==1 and m else str(a.numerator) if a.denominator==1 else r'\frac{'+str(a.numerator)+'}{'+str(a.denominator)+'}'
        out.append(('-' if c<0 else '+' if out else '')+number+m)
    return '$'+''.join(out)+'$'

matrix=[[poly(p) for p in row] for row in d['omega_matrix']]
plt.rcParams['svg.hashsalt']='hodge-lab-skew-volume'
fig=plt.figure(figsize=(16,9),facecolor='#faf9f4')
fig.text(.04,.94,'Where the sign and the factor 1/2 come from',fontsize=23,weight='bold',color='#17333b')
fig.text(.04,.89,'one-reflection-skew  •  actual polynomial partial derivatives  •  ordered algebraic volume coefficients in Lean',fontsize=12.5,color='#53696e')
ax=fig.add_axes([.065,.38,.48,.40]);ax.axis('off')
table=ax.table(cellText=matrix,colLabels=['point',r'$\partial_x$',r'$\partial_r$',r'$\partial_w$',r'$\partial_t$',r'$\partial_z$'],
               rowLabels=['X₀','X₁','X₂','Y₀','Y₁','Y₂'],cellLoc='center',bbox=[0,0,1,1])
table.auto_set_font_size(False);table.set_fontsize(16)
for (i,j),cell in table.get_celld().items():
    cell.set_edgecolor('#bfd1cd')
    cell.set_facecolor('#e2efea' if i!=4 else '#f4e2bc')
    if i==0:
        cell.set_facecolor('#173f48');cell.set_text_props(color='white',weight='bold',fontsize=13)
    elif j==-1:cell.set_text_props(weight='bold',color='#17333b',fontsize=13)
ax.text(0,1.09,'Euler volume = determinant of this 6 × 6 matrix',fontsize=13,weight='bold',color='#17333b',transform=ax.transAxes)
fig.text(.065,.32,'Expand along the constant Y₀ row (index 3).',fontsize=14,color='#92611c',weight='bold')
fig.text(.065,.275,'Its minor is the actual affine Jacobian: det J = x².',fontsize=13,color='#17333b')
fig.text(.065,.225,'The signed coefficient is (−1)³ x² = −x².',fontsize=15,color='#14737a',weight='bold')
bx=fig.add_axes([.60,.22,.355,.57]);bx.axis('off')
boxes=[(.70,.26,'Square coordinate: U = x²',r'$\det S = 2x$'+'\nInvertible tangent map iff x ≠ 0\nThe factor 1/2 is not a trace factor.', '#ece8f5','#7762a0'),
       (.30,.29,'Retain the protected scalar source',r'$A=x^3,\quad G=F(\varphi)$'+'\n'+r'$A\Omega/F^2:\quad -x^5/G^2$'+'\n'+r'$U\mathrm{\ coefficient}:\quad -U^2/(2G^2)$','#e3f0e9','#14737a'),
       (.00,.18,'Explicit chart boundary','G ≠ 0: ambient complement, before residue.\nx ≠ 0: required for division by 2x.', '#fff0d6','#aa792b')]
for y,h,title,body,fill,edge in boxes:
    bx.add_patch(FancyBboxPatch((0,y),1,h,boxstyle='round,pad=.015',facecolor=fill,edgecolor=edge,transform=bx.transAxes))
    bx.text(.03,y+h-.05,title,fontsize=12,weight='bold',color=edge,transform=bx.transAxes)
    bx.text(.03,y+.035,body,fontsize=11.5,color='#17333b',linespacing=1.5,transform=bx.transAxes)
for y1,y2 in [(.68,.61),(.28,.20)]:
    bx.annotate('',xy=(.5,y2),xytext=(.5,y1),xycoords='axes fraction',arrowprops={'arrowstyle':'->','color':'#14737a','lw':1.5})
fig.text(.04,.13,f"{v['new_theorems']} theorem audits  •  {v['new_modules_replayed']} new-module kernel replays  •  4 true values and 4 deliberate errors checked",fontsize=13,color='#14737a',weight='bold')
fig.text(.04,.078,'Forward polynomial Jacobians allow x = 0. Recovering the coefficient by inverse Jacobian does not.',fontsize=12,color='#53696e')
fig.text(.04,.035,'Not established here: residue map, general differential-form API, global descent, trace or rational primitive.',fontsize=12,color='#53696e')
for ext in ['png','svg']:
    fig.savefig(R/'visualizations'/('skew-volume.'+ext),dpi=170,facecolor=fig.get_facecolor(),metadata={'Date':None} if ext=='svg' else None)
p=R/'visualizations/skew-volume.svg';p.write_text('\n'.join(s.rstrip() for s in p.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8',newline='\n')
(O/'visualization-data.json').write_text(json.dumps({'matrix':d['omega_matrix'],'row_order':d['protected_order'],
    'affine_det':d['affine_determinant'],'square_det':d['square_determinant'],'omega_det':d['omega_determinant'],
    'sample':d['sample'],'new_theorems':v['new_theorems'],'limits':d['limits']},indent=2)+'\n',encoding='utf-8',newline='\n')
print('PASS: actual reconstructed matrix and formal scope rendered')
