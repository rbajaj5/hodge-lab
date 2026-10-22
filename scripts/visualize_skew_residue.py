"""Visualize checked normal-coefficient reduction; consumes exact receipts."""
from pathlib import Path
from fractions import Fraction
import hashlib,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

R=Path(__file__).resolve().parents[1];O=R/'formal/results/skew-residue'
v=json.loads((O/'validation.json').read_text(encoding='utf-8'))
if v['status']!='PASS':raise RuntimeError('Passing verification required')
for name,h in {**v['source_lf_sha256'],**v['reused_source_lf_sha256']}.items():
    if hashlib.sha256((R/'formal'/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest()!=h:
        raise RuntimeError('Checked source changed: '+name)
raw=(O/'independent.json').read_bytes()
if hashlib.sha256(raw).hexdigest()!=v['independent_receipt_lf_sha256']:raise RuntimeError('Reconstruction receipt changed')
d=json.loads(raw);values=d['control_values']
plt.rcParams['svg.hashsalt']='hodge-lab-skew-residue'
fig=plt.figure(figsize=(16,9),facecolor='#faf9f4')
fig.text(.04,.94,'Residue normalization: why the coefficient is +5/72',fontsize=23,weight='bold',color='#17333b')
fig.text(.04,.89,'one-reflection-skew  •  ordered local coefficient calculus  •  signs and chart assumptions retained',fontsize=12.5,color='#53696e')
ax=fig.add_axes([.04,.55,.92,.26]);ax.axis('off')
panels=[(.00,'Double pole',r'$-U^2/(2G^2)$','Coefficient from the checked\ncoordinate-volume step.'),
        (.34,'Subtract the actual derivative',r'$f=U^2/(12z^5G),\quad \beta=f\alpha$',r'$\partial_z f=-U^2/(2G^2)-5U^2/(12z^6G)$'),
        (.68,'Normalize the simple pole',r'$\frac{5U^2}{12z^6}\ /\ (6z^5)=\frac{5U^2}{72z^{11}}$','Normal derivative: ∂G/∂z = 6z⁵')]
for x,title,formula,body in panels:
    ax.add_patch(FancyBboxPatch((x,.02),.31,.96,boxstyle='round,pad=.008',facecolor='#e3efe9',edgecolor='#14737a',transform=ax.transAxes))
    ax.text(x+.014,.80,title,fontsize=13,weight='bold',color='#14737a',transform=ax.transAxes)
    ax.text(x+.014,.51,formula,fontsize=14 if x!=.68 else 13,color='#17333b',transform=ax.transAxes)
    ax.text(x+.014,.18,body,fontsize=10.7,color='#17333b',linespacing=1.6,transform=ax.transAxes)
for x in [.317,.657]:ax.annotate('',xy=(x+.02,.52),xytext=(x,.52),xycoords='axes fraction',arrowprops={'arrowstyle':'->','color':'#14737a'})

bx=fig.add_axes([.075,.22,.40,.23],facecolor='#faf9f4')
labels=['original','derivative','remainder']
keys=['psi','beta_z','simple_pole']
nums=[float(Fraction(values[k])) for k in keys]
bx.barh(labels,nums,color=['#7762a0','#ba7853','#14737a'],height=.58)
bx.axvline(0,color='#9db2ae',lw=1)
for i,k in enumerate(keys):bx.text(nums[i]+(.006 if nums[i]>=0 else -.006),i,values[k],va='center',ha='left' if nums[i]>=0 else 'right',fontsize=12,color='#17333b')
bx.set_xlim(-.26,.20);bx.invert_yaxis();bx.set_xticks([])
for spine in bx.spines.values():spine.set_visible(False)
bx.set_title('Exact control: −1/18 = −7/36 + 5/36',loc='left',fontsize=13,weight='bold',color='#17333b',pad=15)
fig.text(.075,.18,'At (U,r,w,t,z) = (1,0,0,0,1), G = 3.',fontsize=11,color='#53696e')

cx=fig.add_axes([.56,.18,.40,.29]);cx.axis('off')
cx.text(0,.92,'Two different domains',fontsize=15,weight='bold',color='#92611c')
cx.text(0,.69,'Ambient reduction: z ≠ 0 and G ≠ 0.\nA coordinate derivation is an explicit hypothesis.',fontsize=12,color='#17333b',linespacing=1.5)
cx.text(0,.40,'Residue coefficient: restrict to G = 0, with z ≠ 0.\nDo not restrict the ambient derivation itself.',fontsize=12,color='#17333b',linespacing=1.5)
cx.text(0,.12,'Base derivatives cancel by alternation.\nThey need not vanish: one checked r-partial is −1/32.',fontsize=12,color='#17333b',linespacing=1.5)
fig.text(.04,.105,f"{v['new_theorems']} theorem audits  •  2 new-module kernel replays  •  8 true evaluations  •  5 deliberate errors rejected",fontsize=13,color='#14737a',weight='bold')
fig.text(.04,.055,'Convention: Res((dG/G) ∧ θ) = θ. The determinant model verifies the local coefficient +5U²/(72z¹¹).',fontsize=12,color='#53696e')
fig.text(.04,.018,'Still separate: constructing the coordinate derivation, a general residue operator, global transport and a rational primitive.',fontsize=11.5,color='#53696e')
for ext in ['png','svg']:
    fig.savefig(R/'visualizations'/('skew-residue.'+ext),dpi=170,facecolor=fig.get_facecolor(),metadata={'Date':None} if ext=='svg' else None)
p=R/'visualizations/skew-residue.svg'
p.write_text('\n'.join(s.rstrip() for s in p.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8',newline='\n')
(O/'visualization-data.json').write_text(json.dumps({'control_values':values,'divisor_control':d['divisor_control'],
    'nonzero_base_partial':d['nonzero_base_partial'],'polynomial':d['protected_chart_polynomial'],
    'normal':d['all_five_G_partials'][4],'scope':d['scope']},indent=2)+'\n',encoding='utf-8',newline='\n')
print('PASS: exact coefficient reduction and chart boundaries rendered')
