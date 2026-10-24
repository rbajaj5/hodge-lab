"""Reproducible scientific diagram; frozen new receipts are its inputs."""
from pathlib import Path
import hashlib,json,os,sys
os.environ.setdefault('MPLCONFIGDIR','/tmp/hodge-A3-denominator-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
base=Path(__file__).resolve().parent
author=base/'lead/sum-01/result/validation.json'
checker=base/'checker/determinant-01/result/validation.json'
a=json.loads(author.read_text());c=json.loads(checker.read_text())
if (a['rank_coefficient'],a['rank_augmented'],c['independent_augmented_minor_det_mod_prime'])!=(2400,2401,13752):
    raise RuntimeError('Unexpected certificate inputs')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'svg.hashsalt':'A3-20261024'})
fig=plt.figure(figsize=(13,7.4),facecolor='#f6f8fb')
gs=fig.add_gridspec(1,2,width_ratios=[1,1.12],left=.07,right=.96,bottom=.23,top=.79,wspace=.22)
ax=fig.add_subplot(gs[0,0]);ax.set_facecolor('#f6f8fb')
y=np.arange(4)
ax.barh(y+.16,[702,702,702,702],height=.29,color='#c6d0db',label='Original parameters')
ax.barh(y-.16,[702,702,702,294],height=.29,color=['#246781','#246781','#246781','#cf663e'],label='Necessary family tested')
ax.set_yticks(y,['P₀','P₁ / A','P₂ / A²','P₃ / A³']);ax.invert_yaxis();ax.set_xlim(0,840)
ax.set_xlabel('Independent scalar parameters across all six fluxes')
ax.set_title('Only the top sector is restricted',loc='left',fontweight='bold',pad=18)
for i,n in enumerate([702,702,702,294]):ax.text(n+12,i-.16,str(n),va='center',fontweight='bold')
ax.text(714,3+.16,'702',va='center',color='#617182')
for s in ['top','right','left']:ax.spines[s].set_visible(False)
ax.tick_params(axis='y',length=0);ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True)
fig.text(.07,.145,'Gray: original parameters. Blue / orange: necessary family tested. P₂, P₁ and P₀ remain unrestricted.',fontsize=10.3,color='#455566')
bx=fig.add_subplot(gs[0,1]);bx.axis('off')
bx.text(0,1.02,'Pole condition → full two-row certificate',fontweight='bold',fontsize=13)
bx.text(0,.83,r'Highest pole: $(R_a-3I)Q_3=0$,  $\det(R_a-3I)=10$',fontsize=11)
bx.text(0,.67,r'$P_3=(T_rh_3,T_vh_3,k_3)$',fontsize=16,color='#a94b2b')
bx.text(0,.53,'60 h₃ + 234 k₃ + 3 × 702 lower = 2400',fontsize=12)
bx.text(0,.34,'Coefficient rank 2400  |  augmented rank 2401',fontsize=11.5,color='#195e78')
bx.text(0,.15,'2401 × 2401 minor',fontsize=17,fontweight='bold')
bx.text(0,-.015,'det = 13752 (mod 32003) ≠ 0',fontsize=16,fontweight='bold',color='#195e78')
fig.text(.07,.935,'A cubed: the declared combined family is excluded',fontsize=22,fontweight='bold',color='#17344b')
fig.text(.07,.875,'Full physical current: both compact rows, all r / v / t derivatives, positive packet orientation.',fontsize=11.5,color='#455566')
fig.text(.07,.105,'Top-pole / support theorem: imported structural evidence. Matrix and minor: new, separately reconstructed computations.',fontsize=10.3,color='#455566')
fig.text(.07,.060,'Scope: B + B/A + B/A² + B/A³,  r exponents −10…2, v and t degrees ≤2. Other supports, divisors and pole orders remain open.',fontsize=10.3,color='#455566')
svg=out/'A3-denominator-certificate.svg';png=out/'A3-denominator-certificate.png'
fig.savefig(svg,metadata={'Date':None});fig.savefig(png,dpi=180);plt.close(fig)
svg.write_text('\n'.join(x.rstrip() for x in svg.read_text().splitlines())+'\n',encoding='utf-8')
receipt={'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'matplotlib':matplotlib.__version__,'inputs':{str(p.relative_to(base)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [author,checker]},'outputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [svg,png]},'claim_boundary':'Imported highest-pole reduction plus new exact finite-family exclusion. No primitive or general obstruction.'}
(out/'visualization.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt,indent=2))
