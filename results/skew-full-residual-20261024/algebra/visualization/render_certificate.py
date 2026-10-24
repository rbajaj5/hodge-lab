"""Render a frozen exact receipt. No symbolic calculation or checker replay."""
import argparse, datetime, hashlib, json, math, pathlib, shutil, subprocess, sys, time

p=argparse.ArgumentParser()
p.add_argument('--receipt',required=True,type=pathlib.Path)
p.add_argument('--execution',required=True,type=pathlib.Path)
p.add_argument('--output-dir',required=True,type=pathlib.Path)
p.add_argument('--child',action='store_true')
args=p.parse_args()
out=args.output_dir
script=pathlib.Path(__file__).resolve()
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
if not args.child:
    out.mkdir(parents=True,exist_ok=False)
    shutil.copyfile(args.receipt,out/'input-validation.json')
    shutil.copyfile(args.execution,out/'input-execution.json')
    shutil.copyfile(script,out/'generator.py')
    command=[sys.executable,str(script),'--child','--receipt',str(out/'input-validation.json'),'--execution',str(out/'input-execution.json'),'--output-dir',str(out)]
    start=time.monotonic();utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        run=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',timeout=60)
        code=run.returncode;stdout=run.stdout;stderr=run.stderr;status='completed'
    except subprocess.TimeoutExpired as ex:
        code=None;status='timeout'
        def decode(x):return x.decode('utf-8',errors='replace') if isinstance(x,bytes) else (x or '')
        stdout=decode(ex.stdout);stderr=decode(ex.stderr)
    (out/'stdout.log').write_text(stdout,encoding='utf-8')
    (out/'stderr.log').write_text(stderr,encoding='utf-8')
    record={'command':command,'start_utc':utc,'end_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seconds':time.monotonic()-start,'timeout_seconds':60,'status':status,'exit_code':code,'generator_sha256':sha(script)}
    (out/'render-execution.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(record,indent=2));print(stdout);print(stderr)
    raise SystemExit(0 if code==0 else 1)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

receipt=json.loads(args.receipt.read_text(encoding='utf-8'))
execution=json.loads(args.execution.read_text(encoding='utf-8'))
if execution['exit_code']!=0 or not receipt['status'].startswith('PASS'):
    raise ValueError('a successful frozen receipt is required')
w=receipt['boundary_witness']
# Parsing already-saved coefficients is data extraction, not polynomial algebra.
coeff={}
for term in w['residue_numerator_remainder'].replace(' - ',' + -').split(' + '):
    if '*r**' in term:
        val,power=term.split('*r**');power=int(power)
    elif '*r' in term:
        val=term.removesuffix('*r');power=1
    else:
        val=term;power=0
    if power in coeff:raise ValueError('unexpected duplicate monomial in frozen polynomial')
    coeff[power]=int(val)
if sorted(coeff)!=list(range(18)):raise ValueError('unexpected frozen coefficient support')
plotdata=[{'power':k,'coefficient':str(coeff[k]),'signed_log10_abs':math.copysign(math.log10(abs(coeff[k])),coeff[k])} for k in sorted(coeff)]
(out/'coefficient-display-data.json').write_text(json.dumps(plotdata,indent=2)+'\n',encoding='utf-8')

plt.rcParams.update({'font.family':'DejaVu Sans','mathtext.fontset':'dejavusans','svg.fonttype':'none','font.size':12})
navy='#17324d';teal='#146f86';orange='#bb5a36';slate='#526477';muted='#66778a'
fig=plt.figure(figsize=(16,13),facecolor='#f7f9fc')
def box(x,y,width,height,face='#ffffff',edge='#d4dee9'):
    patch=FancyBboxPatch((x,y),width,height,boxstyle='round,pad=0.008,rounding_size=0.009',transform=fig.transFigure,linewidth=1,edgecolor=edge,facecolor=face,zorder=-1)
    fig.add_artist(patch)
def txt(x,y,s,size=12,color=navy,weight='normal',**kw):
    return fig.text(x,y,s,fontsize=size,color=color,fontweight=weight,va='top',**kw)

txt(.045,.968,'A fixed mixed-current family is excluded',25,weight='bold')
txt(.045,.929,'Exact certificate from a frozen receipt  |  Two compact rows retained  |  Other currents remain open',12,color=muted)

box(.045,.620,.545,.270)
txt(.060,.874,'COMPLETE CURRENT AND OPERATOR',12,color=teal,weight='bold')
txt(.060,.842,r'$Z=h\,\beta\wedge L,\qquad L=-7dJ\,da-3aU\,dt$',17)
txt(.060,.805,r'$Z_a=h(0,\widetilde W_a),\quad Z_v=h(-1,\widetilde W_v),\quad Z_t=h(0,\widetilde W_t)$',13)
txt(.060,.765,'Row 0',11,color=teal,weight='bold')
txt(.132,.768,r'$(\operatorname{Div}_N Z)_0=-D_vh$',17)
txt(.060,.723,'Row 1',11,color=teal,weight='bold')
txt(.132,.725,r'$(\operatorname{Div}_N Z)_1=$',15)
txt(.132,.698,r'$\widetilde W_aD_ah+\widetilde W_vD_vh+\widetilde W_t\partial_t h+\widetilde qh$',15)
txt(.060,.650,r'$D_a,D_v$ retain all moving-root terms; $\partial_t r=0$.',11,color=slate)

box(.615,.620,.340,.270)
txt(.630,.874,'POLYNOMIAL COEFFICIENTS',12,color=teal,weight='bold')
txt(.630,.843,r'$d=1+t^6,\quad J=(4-5t^2)/4$',12)
txt(.630,.815,r'$U=7t(17+2t^2+14t^4-5t^6)/4$',12)
txt(.630,.777,r'$\widetilde W_a=-3atU$',13)
txt(.630,.748,r'$\widetilde W_v=-v[7J(d-td^{\prime}/3)+2tU]$',12)
txt(.630,.719,r'$\widetilde W_t=7tdJ$',13)
txt(.630,.690,r'$\widetilde q=t[-3U+(49/6)d^{\prime}J+7dJ^{\prime}]$',12)
txt(.630,.650,'No new divisor in this current family.',11,color=slate)

box(.045,.440,.910,.145,face='#fff6ee',edge='#e2b792')
txt(.060,.569,'DISCRIMINANT BOUNDARY — A RESIDUE TEST, NOT AN ORDINARY EVALUATION',12,color='#914d2f',weight='bold')
txt(.060,.536,rf'$(a,v,t)=({w["a"]},{w["v"]},{w["t"]}),\qquad \Delta=0,\quad \Delta_v={w["Delta_v"]}\ne0$',16)
txt(.060,.496,r'$\operatorname{Res}(R_{2,0}\,dv)=\gamma/756-\kappa/2592=N(r)/D_{\mathrm{res}}(r)$',16)
txt(.060,.462,r'$\gamma=D_v^2\chi,\quad \kappa=vD_v\chi-\chi,\quad \chi=r^{-3}-v^3/3$',11,color=slate)

ax=fig.add_axes([.085,.150,.465,.230],facecolor='#ffffff')
xs=[d['power'] for d in plotdata];ys=[d['signed_log10_abs'] for d in plotdata]
colors=[teal if y>0 else orange for y in ys]
ax.bar(xs,ys,color=colors,width=.69)
ax.axhline(0,color=navy,linewidth=.8)
ax.set_xticks(xs);ax.tick_params(axis='x',labelsize=9)
ax.set_yticks([-25,-20,0,20,25]);ax.tick_params(axis='y',labelsize=10)
ax.set_ylim(-29,29);ax.set_xlim(-.8,17.8)
ax.set_xlabel(r'Power $k$ in the saved remainder $N(r)\ \mathrm{mod}\ F(r)$',fontsize=11,labelpad=8)
ax.set_ylabel(r'$\operatorname{sign}(n_k)\,\log_{10}|n_k|$',fontsize=12)
ax.set_title('Saved degree-17 residue numerator coefficients',loc='left',fontsize=13,color=navy,pad=12)
ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
for side in ('top','right'):ax.spines[side].set_visible(False)
txt(.085,.105,'Coefficient sizes are descriptive. They do not prove the obstruction.',10,color=muted)

box(.615,.143,.340,.245)
txt(.630,.372,'EXACT CERTIFICATE IN THE RECEIPT',12,color=teal,weight='bold')
txt(.630,.341,r'$F(r)=r^{18}-4r^{15}+r^{12}+(6r+1)^6$',12)
for y,label,key in [(.305,r'$\deg\gcd(F,F^{\prime})$', 'gcd_f_fr_degree'),(.273,r'$\deg\gcd(F,N)$','gcd_f_residue_numerator_degree'),(.241,r'$\deg\gcd(F,D_{\mathrm{res}})$','gcd_f_residue_denominator_degree')]:
    txt(.630,y,label,15)
    txt(.923,y,str(w[key]),17,color=teal,weight='bold',ha='right')
txt(.630,.202,'All 18 sheets: unramified; residue defined\nand nonzero. Exact derivatives have zero residue.',11,color=slate,linespacing=1.4)

box(.045,.025,.910,.058,face='#eaf2f7',edge='#b9cdda')
txt(.060,.068,'SCOPE',11,color=teal,weight='bold')
txt(.120,.068,r'No rational $h$ solves $\operatorname{Div}_N(h\beta\wedge L)=R_2$ for this fixed $L$.',13,weight='bold')
txt(.120,.044,'Arbitrary other two-row currents remain open. This diagram is not a full-source nonexistence claim.',11,color=slate)

fig.savefig(out/'mixed-beta-residue-certificate.svg',format='svg',facecolor=fig.get_facecolor())
fig.savefig(out/'mixed-beta-residue-certificate.png',format='png',dpi=175,facecolor=fig.get_facecolor())
plt.close(fig)
manifest={'status':'rendered; awaiting visual inspection','kind':'static exact-certificate diagram','no_mathematical_rerun':True,
 'rendered_claims_source':'frozen check-01 validation.json; gcd degrees read verbatim, not recomputed',
 'coefficient_display':'signed base-10 log magnitudes parsed from the saved reduced numerator; descriptive only',
 'inputs':{args.receipt.name:sha(args.receipt),args.execution.name:sha(args.execution)},
 'generator_sha256':sha(script),'matplotlib':matplotlib.__version__,
 'outputs':{name:sha(out/name) for name in ('mixed-beta-residue-certificate.svg','mixed-beta-residue-certificate.png','coefficient-display-data.json')},
 'receipt_checks':len(receipt['checks']),'receipt_mutations':len(receipt['mutations'])}
(out/'visualization.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'rendered','outputs':list(manifest['outputs']),'no_mathematical_rerun':True},indent=2))
