"""Reproduce the audited transport-factor and correction dependency diagram."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT/'results/physical-source-transport-audit/replay.json').read_text(encoding='utf-8'))
if receipt['status'] != 'PASS' or receipt['residue_density'] != '-144*R*v^3':
    raise ValueError('A passing transport receipt with the stated density is required')
plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'none',
                     'svg.hashsalt':'physical-source-transport-audit'})
fig, ax = plt.subplots(figsize=(14,9), dpi=160)
fig.patch.set_facecolor('#f7f8f5'); ax.set(xlim=(0,14),ylim=(0,9)); ax.axis('off')
ink, teal, purple = '#17333d','#167575','#7759a7'

def box(x,y,w,h,title,body,color=teal):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.12',
                               facecolor='white',edgecolor=color,linewidth=1.5))
    ax.text(x+.15,y+h-.25,title,fontsize=13,color=color,weight='bold',va='top')
    ax.text(x+.15,y+h-.68,body,fontsize=12.5,color=ink,va='top',linespacing=1.35)

ax.text(.3,8.65,'Where the 144 comes from',fontsize=25,weight='bold',color=ink)
ax.text(.3,8.25,'holdout-moving-branch · exact local transport audit · 21 October 2026',fontsize=12,color=ink)
box(.4,6.1,3.8,1.65,'Coordinate determinant',
    '$F_0\\det M=-48R^4 W(\\xi)$\n$W(\\xi)=v^3G D\\xi$')
box(5.0,6.1,3.5,1.65,'Relative differential',
    '$G D\\xi=6\\eta$\nFactor 3: prior exact audit')
box(9.3,6.1,4.1,1.65,'Weierstrass normal',
    '$V_Y=2Y=2R^3\\eta$\n$\\rho=F_0\\det M/(2Y)$')
for left,right in [(4.25,4.85),(8.6,9.15)]:
    ax.annotate('',xy=(right,6.95),xytext=(left,6.95),arrowprops={'arrowstyle':'->','color':teal,'lw':2})
ax.text(7,5.52,'$\\rho=(-48)(6)/(2)\\;R^{4-3}v^3=-144Rv^3$',
        ha='center',fontsize=24,color=teal)
ax.text(7,5.07,'Residue-volume identity on F = 0; not an ambient six-dimensional Jacobian.',
        ha='center',fontsize=12,color=ink)
box(.4,2.8,6.0,1.75,'Source normalization',
    '$P=-V_\\alpha/(144R)$\n$P\\circ\\phi=R^5(\\dot a\\xi+\\dot b)/144$\n$\\operatorname{Div}(w_{\\rm pulled})=-v^3(\\dot a\\xi+\\dot b)/(2\\eta^2)$')
box(7.0,2.8,6.4,1.75,'Both corrections are needed',
    '$S=v^3\\dot G/G+\\operatorname{Div}(C e_2)$\n$w=w_{\\rm pulled}+[\\dot\\xi/(6\\eta)]W-Ce_2$\n$\\operatorname{Div}(w)=-S$')
box(.4,.65,13,1.65,'Verification boundary',
    f"{receipt['checks_passed']} exact identities, including all 25 matrix entries. Three deliberate errors must fail.\n"
    'Moving-map algebra assumes the curve and differential first variations.\n'
    'Full covariant jets, field/trace/clearing proofs and Lean compilation were not replayed.',purple)
ax.text(.4,.28,'A dependency diagram, not a new solve. Current packet pins inputs and records all conditional steps.',
        fontsize=11,color=ink)
for suffix in ['png','svg']:
    output = ROOT/f'visualizations/physical-source-transport-audit.{suffix}'
    fig.savefig(output,bbox_inches='tight',metadata={'Date':None} if suffix=='svg' else None)
    if suffix == 'svg':
        output.write_text('\n'.join(line.rstrip() for line in
                          output.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
print('Wrote physical-source-transport-audit.png and .svg')
