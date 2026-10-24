"""Reproducible research figure from exact saved point residuals, no new search."""
from pathlib import Path
import datetime,hashlib,json,sys
from fractions import Fraction
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
base=Path(__file__).resolve().parent; out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
p=base/'checker/translation-current-02/result/validation.json'
q=base/'alternate/first-jet-cert-02/validation.json'
rp=json.loads(p.read_text(encoding='utf-8'));rq=json.loads(q.read_text(encoding='utf-8'))
pt=rp['exact_points'][0]
vectors=[pt['full_source_R2'],pt['residual'],[str(-Fraction(x)) for x in rq['Div_J_minus_R0_at_K_zero']]]
labels=['Original residual $R_2$','Corrected triangular current','First-jet current, $K=0$']
fig,ax=plt.subplots(figsize=(11,6.5));fig.subplots_adjust(left=.12,right=.98,top=.81,bottom=.24)
colors=['#16697A','#D66B2D'];xs=list(range(3));width=.31
for j in range(2):
    vals=[float(Fraction(x[j])) for x in vectors]
    ax.bar([x+(j-.5)*width for x in xs],vals,width,label=f'Compact row {j}',color=colors[j])
ax.axhline(0,color='#202B33',lw=1);ax.set_yscale('symlog',linthresh=.0001)
ax.set_ylim(-30,30)
ax.set_xticks(xs,labels);ax.set_ylabel('Exact residual evaluated at the stated point\n(symmetric logarithmic display)')
ax.grid(axis='y',alpha=.25);ax.legend(loc='upper left',frameon=False)
fig.suptitle('Two compact rows remain after the tested currents',fontsize=17,fontweight='bold',y=.96)
fig.text(.12,.87,r'Allowed physical point: $(r,v,t,a)=(1,2,1,3)$; $A_r=-3$, $\Delta=1036$.',fontsize=12)
fig.text(.12,.12,r'All bars use the same target: $R_2-\mathrm{Div}_N(Z)$. For the first-jet current, $Z=J-Y$.',fontsize=10)
fig.text(.12,.075,'Point witnesses reject these candidates; bar sizes are not generic error estimates or an optimization score.',fontsize=10)
fig.text(.12,.035,'The separate 702-coefficient physical-family exclusion uses an exact nonzero minor, not this plot.',fontsize=10)
svg=out/'full-residuals.svg';png=out/'full-residuals.png'
fig.savefig(svg,metadata={'Date':None});fig.savefig(png,dpi=160,metadata={'Software':'Matplotlib'});plt.close(fig)
record={'purpose':'illustrate exact full two-row nonzero witnesses, not certify generic solvability','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'matplotlib':matplotlib.__version__,'inputs':{p.relative_to(base).as_posix():hashlib.sha256(p.read_bytes()).hexdigest(),q.relative_to(base).as_posix():hashlib.sha256(q.read_bytes()).hexdigest()},'exact_vectors':vectors,'labels':labels,'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'outputs':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in [svg,png]}}
(out/'visualization.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,indent=2))
