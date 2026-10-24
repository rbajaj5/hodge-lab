"""Presentation only: renders two frozen receipts without recomputing mathematics."""
import argparse,datetime,hashlib,json,pathlib,sys,time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
p=argparse.ArgumentParser();p.add_argument('--algebra',required=True,type=pathlib.Path);p.add_argument('--checker',required=True,type=pathlib.Path);p.add_argument('--output',required=True,type=pathlib.Path);args=p.parse_args()
start=time.monotonic()
if args.output.exists():raise SystemExit('fresh output directory required')
args.output.mkdir(parents=True)
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
a=json.loads(args.algebra.read_text(encoding='utf-8'));c=json.loads(args.checker.read_text(encoding='utf-8'))
if a['source_sha256']!=c['connection_sha256']:raise ValueError('receipts use different source pins')
if not c['all_lower_coefficients_preserved'] or c['lower_A2_projection_used']:raise ValueError('figure scope disagrees with receipt')
if a['dimensions']['joint_necessary']!=c['coefficient_columns']:raise ValueError('receipt dimension mismatch')
for name,src in [('algebra-validation.json',args.algebra),('checker-A3-minor.json',args.checker)]:
    (args.output/name).write_bytes(src.read_bytes())
(args.output/'generator-source.py').write_bytes(pathlib.Path(__file__).read_bytes())
plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'none'})
fig,ax=plt.subplots(figsize=(14,9),dpi=160)
fig.patch.set_facecolor('#f5f7fa');ax.set_facecolor('#f5f7fa');ax.set_xlim(0,1);ax.set_ylim(0,1);ax.axis('off')
fig.subplots_adjust(left=0,right=1,bottom=0,top=1)
ink='#182c43';muted='#506478';blue='#2369a1';teal='#0e766e';line='#9fb0bf'
def txt(x,y,text,size=14,color=ink,weight='normal',ha='left',va='center'):
    return ax.text(x,y,text,fontsize=size,color=color,weight=weight,ha=ha,va=va,linespacing=1.4)
def box(x,y,w,h,face='#ffffff',edge='#d2dce5',lw=1.2):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.008,rounding_size=0.012',facecolor=face,edgecolor=edge,linewidth=lw))
def arrow(x0,y0,x1,y1):
    ax.add_patch(FancyArrowPatch((x0,y0),(x1,y1),arrowstyle='-|>',mutation_scale=16,linewidth=1.5,color=line))
txt(.035,.955,'The A⁻³ search: a bounded family excluded',24,weight='bold')
txt(.035,.908,'Frozen-receipt visualization • fixed source r⁻⁴ M_b e₀ /12 • both rows • all r, v, t derivatives',13,color=muted)
txt(.035,.866,'Each scalar numerator lies in B: r exponents −10…2; v and t exponents 0…2.',14,color=muted)
cards=[(.035,'P₀',False),(.275,'P₁ / A',False),(.515,'P₂ / A²',False),(.755,'P₃ / A³',True)]
for x,label,top in cards:
    box(x,.675,.21,.145,face='#e7f3f1' if top else '#ffffff',edge='#82b5ae' if top else '#d2dce5')
    txt(x+.105,.783,label,20,teal if top else blue,'bold',ha='center')
    txt(x+.105,.738,'702 → 294' if top else '702 retained',18,teal if top else ink,'bold',ha='center')
    txt(x+.105,.701,'highest pole: tangent' if top else 'unrestricted lower level',11.5,muted,ha='center')
for x in (.14,.38,.62):arrow(x,.663,x,.613)
arrow(.86,.663,.86,.613)
box(.035,.515,.69,.09,face='#edf2f7')
txt(.38,.566,f"{a['dimensions']['unrestricted_lower']:,} lower coefficients remain free",20,ink,'bold',ha='center')
txt(.38,.531,'No separate lower-level tangency or A⁻² projection is imposed.',12,muted,ha='center')
box(.755,.515,.21,.09,face='#e7f3f1',edge='#82b5ae')
txt(.86,.568,'294 top coefficients',16,teal,'bold',ha='center')
txt(.86,.531,'60 in h₃ + 234 in k₃',12,muted,ha='center')
arrow(.38,.505,.46,.451);arrow(.86,.505,.64,.451)
box(.25,.335,.50,.11,face=ink,edge=ink)
txt(.50,.402,f"{c['coefficient_columns']:,} necessary coefficients",23,'white','bold',ha='center')
txt(.50,.358,'Contains every solution in the declared 2,808-generator family',12.5,'#d7e5f2',ha='center')
arrow(.50,.325,.35,.293)
box(.035,.145,.62,.14,face='#ffffff',edge='#88aea2',lw=1.5)
txt(.055,.257,f"{c['minor_shape'][0]:,} × {c['minor_shape'][1]:,} augmented minor",17,ink,'bold')
txt(.055,.211,f"det = {c['determinant']:,} mod {c['prime']:,} ≠ 0",23,teal,'bold')
txt(.055,.168,'Recorded conclusion: this finite four-sector family is excluded.',12.5,muted)
box(.69,.145,.275,.14,face='#fff3df',edge='#d8b978')
txt(.71,.254,'Full target remains open',16,'#795119','bold')
txt(.71,.201,'General rational currents\nare not excluded.',15,'#795119')
txt(.035,.093,'Allowed physical open: r · A · Δ ≠ 0. The necessary restriction uses the generic A = 0 boundary.',12.5,muted)
txt(.035,.048,'This diagram displays saved receipts; the algebra and exact minor certificate supply the evidence.',12,muted)
paths=[]
for ext in ('svg','png'):
    path=args.output/('A3-receipt-summary.'+ext);fig.savefig(path,dpi=160,facecolor=fig.get_facecolor(),metadata={'Date':None} if ext=='svg' else None);paths.append(path)
plt.close(fig)
report={'status':'RENDERED_FROM_FROZEN_RECEIPTS_NO_MATH_RECOMPUTATION','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'command':[sys.executable,*sys.argv],'elapsed_seconds':time.monotonic()-start,'matplotlib':matplotlib.__version__,
 'generator_sha256':sha(pathlib.Path(__file__)),'inputs':[{'path':str(q),'sha256':sha(q)} for q in (args.algebra,args.checker)],
 'outputs':[{'path':q.name,'sha256':sha(q),'bytes':q.stat().st_size} for q in paths],
 'scope':'Presentation-only fallback. Independent checker receipt is used; delivered Pro CSV equality was not performed in that receipt. No mathematical replay or new inference from visual size.'}
(args.output/'visualization.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
