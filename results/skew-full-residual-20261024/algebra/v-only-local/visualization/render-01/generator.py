"""Visualize the frozen local-coupling receipt without mathematical reruns."""
import argparse,datetime,hashlib,json,pathlib,shutil,subprocess,sys,time
p=argparse.ArgumentParser();p.add_argument('--receipt',required=True,type=pathlib.Path);p.add_argument('--execution',required=True,type=pathlib.Path);p.add_argument('--output-dir',required=True,type=pathlib.Path);p.add_argument('--child',action='store_true');args=p.parse_args()
out=args.output_dir;script=pathlib.Path(__file__).resolve();sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
if not args.child:
 out.mkdir(parents=True,exist_ok=False)
 shutil.copyfile(args.receipt,out/'input-validation.json');shutil.copyfile(args.execution,out/'input-execution.json');shutil.copyfile(script,out/'generator.py')
 cmd=[sys.executable,str(script),'--child','--receipt',str(out/'input-validation.json'),'--execution',str(out/'input-execution.json'),'--output-dir',str(out)]
 start=time.monotonic();utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
 try:
  r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',timeout=60);code=r.returncode;stdout=r.stdout;stderr=r.stderr;status='completed'
 except subprocess.TimeoutExpired as ex:
  code=None;status='timeout'
  def text(x):return x.decode('utf-8',errors='replace') if isinstance(x,bytes) else (x or '')
  stdout=text(ex.stdout);stderr=text(ex.stderr)
 for name,val in [('stdout.log',stdout),('stderr.log',stderr)]: (out/name).write_text(val,encoding='utf-8')
 record={'command':cmd,'start_utc':utc,'end_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seconds':time.monotonic()-start,'timeout_seconds':60,'status':status,'exit_code':code,'generator_sha256':sha(script)}
 (out/'render-execution.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print(json.dumps(record,indent=2));print(stdout);print(stderr);raise SystemExit(0 if code==0 else 1)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.lines import Line2D
receipt=json.loads(args.receipt.read_text(encoding='utf-8'));execution=json.loads(args.execution.read_text(encoding='utf-8'))
if execution['exit_code']!=0 or not receipt['status'].startswith('PASS'):raise ValueError('successful frozen receipt required')
point=receipt['point'];witness=receipt['reused_nonzero_scalar_certificate']['boundary_witness']
if point['projection']!='0':raise ValueError('unexpected receipt projection')
plt.rcParams.update({'font.family':'DejaVu Sans','mathtext.fontset':'dejavusans','svg.fonttype':'none','svg.hashsalt':'frozen-local-coupling-20261024'})
fig=plt.figure(figsize=(14,10),facecolor='#f7f9fc')
navy='#15334e';muted='#5c6e80';teal='#146c79';orange='#a54f2e'
def box(x,y,w,h,face='#ffffff',edge='#cfdae5'):
 fig.add_artist(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.008,rounding_size=0.010',facecolor=face,edgecolor=edge,linewidth=1,transform=fig.transFigure,zorder=-1))
def txt(x,y,text,size=12,color=navy,weight='normal',**kw):
 fig.text(x,y,text,fontsize=size,color=color,fontweight=weight,va='top',**kw)
txt(.045,.965,'Full two-row coupling removes the scalar residue obstruction',22,weight='bold')
txt(.045,.918,'Local compatibility; global rational primitive unresolved',19,color=teal,weight='bold')

box(.045,.795,.910,.075,face='#fff6ef',edge='#ddb896')
txt(.060,.854,'SAME DISCRIMINANT BOUNDARY',11,color=orange,weight='bold')
txt(.060,.824,rf'$(a,v,t)=({point["a"]},{point["v"]},{point["t"]}),\quad\Delta=0,\quad\Delta_v={witness["Delta_v"]}\ne0$',14)
txt(.520,.853,r'$\rho=\operatorname{Res}(R_2\,dv),\quad s=\gamma/756-\kappa/2592$',14)
txt(.520,.823,'A residue test at the boundary, not an ordinary matrix evaluation.',10,color=muted)

box(.045,.425,.435,.325,face='#fffdfb')
txt(.060,.731,'FIXED L FAMILY',12,color=orange,weight='bold')
txt(.060,.695,r'$Z=h\,\beta\wedge L$',18)
txt(.060,.650,r'$(\operatorname{Div}_N Z)_0=-D_vh$',18)
txt(.060,.600,r'$\operatorname{Res}(-D_vh\,dv)=0$',17)
txt(.060,.552,r'$\rho_0=s\ne0$',18,color=orange)
txt(.060,.501,'This scalar equation cannot match the source.',12)
txt(.060,.466,'Only the prescribed fixed L family is excluded.',11,color=muted)

box(.520,.425,.435,.325,face='#fbfefd')
txt(.535,.731,'FULL TWO-ROW v-ONLY EQUATION',12,color=teal,weight='bold')
txt(.535,.695,r'$(D_v+N_v)Z=R_2$',17)
txt(.535,.648,r'$C=\operatorname{Res}(N_v\,dv)=-\frac16$',16)
# Draw the saved 2x2 all-ones matrix without unsupported TeX environments.
mx=.795;my=.644;gap=.027
for dx in [0,.042]:
 for dy in [0,-.041]:txt(mx+dx,my+dy,'1',16,ha='center')
for x,sgn in [(mx-.023,1),(mx+.065,-1)]:
 fig.add_artist(Line2D([x+sgn*.008,x,x,x+sgn*.008],[my+.006,my+.006,my-.061,my-.061],transform=fig.transFigure,color=navy,linewidth=1.1))
txt(.535,.570,r'$\operatorname{spec}(C)=\{0,-1/3\},\qquad\rho=s(1,1)^T$',15)
txt(.535,.526,r'$(1,-1)\rho=0\quad\Longrightarrow\quad\rho\in\operatorname{im}C$',16,color=teal)
txt(.535,.479,r'$Z_0=-3\rho+u,\quad Cu=0$',17)
txt(.535,.446,'Compatible boundary value; no global flux is constructed.',10,color=muted)

box(.045,.185,.910,.195)
txt(.060,.364,'GENERIC ADJUGATE CERTIFICATE — NOT INFERRED FROM THE SINGLE POINT',12,color=teal,weight='bold')
txt(.060,.330,r'$B=\Delta M_b,\qquad C=B/\Delta_b\ \mathrm{on}\ \Delta=0$',15)
txt(.060,.291,r'$\operatorname{adj}(B)(\Delta M_j)e_1\ \mathrm{is\ divisible\ by}\ \Delta,\quad j=b,c,d$',15)
txt(.060,.255,r'$\operatorname{adj}(B)(\Delta M_b)e_0\ \mathrm{is\ divisible\ by}\ \Delta\quad\Longrightarrow\quad\rho\in\operatorname{im}C$',15)
txt(.060,.215,r'Domain: characteristic zero; $\Delta=0$, $\Delta_v f_r\ne0$, $ar\ne0$; source scalars regular along this divisor.',11,color=muted)

box(.045,.045,.910,.095,face='#eaf3f5',edge='#b8d0d5')
txt(.060,.122,'WHAT THIS CHANGES',11,color=teal,weight='bold')
txt(.240,.123,'The fixed-family failure does not exclude a full coupled correction.',14,weight='bold')
txt(.240,.092,'Generic local boundary compatibility holds. Other divisors, infinity, and global rationality remain untested.',11,color=muted)
txt(.240,.067,r'$Z_0$ is boundary data, not an explicit rational global current.',11,color=muted)
txt(.045,.020,'Frozen receipt only: no checker replay, no new gcd, and no mathematical computation in this render.',9,color=muted)

names=['two-row-local-compatibility.svg','two-row-local-compatibility.png']
fig.savefig(out/names[0],format='svg',metadata={'Date':receipt['utc']},facecolor=fig.get_facecolor())
fig.savefig(out/names[1],format='png',dpi=175,facecolor=fig.get_facecolor());plt.close(fig)
manifest={'status':'rendered; awaiting visual inspection','no_mathematical_rerun':True,'matplotlib':matplotlib.__version__,
 'inputs':{args.receipt.name:sha(args.receipt),args.execution.name:sha(args.execution)},'generator_sha256':sha(script),
 'outputs':{name:sha(out/name) for name in names},'data_policy':'Matrix, eigenvalues, zero projection and generic divisibility read from frozen receipt; prior nonzero scalar certificate reused verbatim.',
 'scope':'Fixed-L family excluded; generic full two-row local compatibility; global rational primitive unresolved.'}
(out/'visualization.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'rendered','outputs':names,'no_mathematical_rerun':True},indent=2))
