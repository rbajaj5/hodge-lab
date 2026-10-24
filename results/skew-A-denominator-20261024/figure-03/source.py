"""Scientific diagram of the declared supports, necessary map and exact minor.
Reads frozen new receipts. It does not run a new mathematical search.
"""
from pathlib import Path
import datetime,hashlib,json,sys,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/hodge-A-denominator-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
base=Path(__file__).resolve().parent;out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
author=base/'lead/sum-01/result/validation.json';checker=base/'checker/reduced-sum-01/result/validation.json'
a=json.loads(author.read_text(encoding='utf-8'));c=json.loads(checker.read_text(encoding='utf-8'))
if a['rank_coefficient']!=996 or a['rank_augmented']!=997 or c['independent_augmented_minor_det_mod_prime']!=26947:raise RuntimeError('Unexpected receipt values')
fig,(ax,bx)=plt.subplots(1,2,figsize=(12,6.8),gridspec_kw={'width_ratios':[1,1.35]})
fig.subplots_adjust(left=.07,right=.98,top=.82,bottom=.23,wspace=.25)
fig.suptitle('A-denominator search: forced tangency, incompatible full source',fontsize=16,fontweight='bold',y=.97)
fig.text(.07,.89,r'$F_i=L_i+P_i/A$, with both compact rows and all three flux directions independent initially.',fontsize=12)
for m in range(-10,3):
    for n in range(3):ax.scatter(m,n,s=80,color='#BDC8CF',zorder=1)
for m in range(-10,-5):
    for n in range(2):ax.scatter(m,n,s=55,color='#176B80',zorder=2)
ax.scatter([],[],s=80,color='#BDC8CF',label=r'$B$: 117 monomials per row')
ax.scatter([],[],s=55,color='#176B80',label=r'$h$: 30 monomials per row')
ax.set_xticks(range(-10,3,2));ax.set_yticks([0,1,2]);ax.set_xlim(-10.8,2.8);ax.set_ylim(-.5,2.6)
ax.set_xlabel(r'Exponent of $r$');ax.set_ylabel(r'Exponent of $v$')
ax.set_title('Necessary numerator support',fontsize=13)
ax.grid(alpha=.15)
ax.text(.02,.97,r'Each plotted point has $t$ powers 0, 1, 2.',transform=ax.transAxes,va='top',fontsize=10)
bx.axis('off')
texts=[(.96,'Double-pole equation forces the coupled numerators',12,'bold'),
(.85,r'$P_r=T_rh,\quad P_v=T_vh,\quad P_t\in B$',15,'normal'),
(.73,r'$T_r=r^2(r^6+1)$',13,'normal'),
(.63,r'$T_v=r(2r^6+1)v-(3r^6+2)$',13,'normal'),
(.50,r'$T(A)=3r(r^6-1)A$',13,'normal'),
(.36,'Necessary joint parameters: 60 + 234 + 702 = 996',11,'bold'),
(.23,'Augmented minor: 997 × 997',13,'normal'),
(.10,'det = 26947 (mod 32003) ≠ 0',17,'bold')]
for y,text,size,weight in texts:bx.text(0,y,text,transform=bx.transAxes,va='top',fontsize=size,fontweight=weight)
fig.text(.07,.145,'Light gray: B, 117 monomials per row.   Blue: h, 30 monomials per row.',fontsize=10)
fig.text(.07,.09,r'Conclusion: no solution in $(B\oplus A^{-1}B)^6$. Other supports, pole divisors and powers remain open.',fontsize=11)
fig.text(.07,.045,'Structural necessity: imported checked theorem. New evidence: direct quotient-rule matrix and separate exact minor.',fontsize=10)
svg=out/'A-denominator-certificate.svg';png=out/'A-denominator-certificate.png'
fig.savefig(svg,metadata={'Date':None});fig.savefig(png,dpi=160,metadata={'Software':'Matplotlib'});plt.close(fig)
# Normalize only this new generated SVG before recording its hash.
svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
record={'purpose':'Display support restriction and scoped exact obstruction, not a general nonexistence proof','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'matplotlib':matplotlib.__version__,'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'inputs':{p.relative_to(base).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [author,checker]},'outputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [svg,png]}}
(out/'visualization.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print(json.dumps(record,indent=2))
