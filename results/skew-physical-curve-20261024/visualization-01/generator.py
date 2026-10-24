#!/usr/bin/env python3
"""Reproduce the actual common-domain maps and proved/unproved boundaries."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,re,shutil,sys,tempfile,time
os.environ.setdefault('MPLCONFIGDIR',tempfile.mkdtemp(prefix='physical-curve-mpl-'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
ROOT=Path(__file__).resolve().parents[1]
MODULE='formal/HodgeLab/OneReflectionSkew/PhysicalCurveRealization.lean'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--receipt',required=True);p.add_argument('--output-dir',required=True);a=p.parse_args()
 start=time.monotonic();receipt=ROOT/a.receipt;data=json.loads(receipt.read_text(encoding='utf-8'))
 if data['status']!='PASS':raise RuntimeError('Passing focused receipt required')
 if data['source_sha256'][MODULE.removeprefix('formal/')]!=sha(ROOT/MODULE):raise RuntimeError('Proof source mismatch')
 required=['parameters_independent','protected_F_zero','x_square','kaehlerPull_D','exteriorPull_D','ambient_source','curve_source','physical_delta_ne_zero','realized_source_reduction','no_ambient_field_specialization']
 text=(ROOT/MODULE).read_text(encoding='utf-8')
 if not all(re.search(r'^theorem '+n+r'\b',text,re.M) for n in required):raise RuntimeError('Missing proved map/boundary declaration')
 out=(ROOT/a.output_dir).resolve()
 if not out.is_relative_to(ROOT):raise RuntimeError('Output escapes repository')
 out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'generator.py')
 navy,teal,gray,red,amber='#17334e','#007d83','#506475','#a63434','#98600c'
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':13,'svg.hashsalt':'hodge-physical-curve-v1'})
 fig=plt.figure(figsize=(16,13),facecolor='white');ax=fig.add_axes([0,0,1,1]);ax.set_xlim(0,1);ax.set_ylim(0,1);ax.axis('off')
 def panel(x,y,w,h,title,face='#eef5f8',edge='#bfd1dc'):
  ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.011',facecolor=face,edgecolor=edge,linewidth=1.4))
  ax.text(x+.015,y+h-.025,title,fontsize=16,fontweight='bold',color=navy,va='center')
 def arrow(p,q):ax.add_patch(FancyArrowPatch(p,q,arrowstyle='-|>',mutation_scale=18,color=teal,linewidth=2))
 ax.text(.045,.96,'Physical curve realization: one regular source, two valid pullbacks',fontsize=23,fontweight='bold',color=navy)
 ax.text(.045,.923,r'Protected $q=1,\ A=X_0^3Y_0^3$; original point $(x,rx,wx,1,t,z)$ has $F=0$ and $A=x^3$.',fontsize=15,color=gray)
 panel(.045,.788,.265,.095,'Independent polynomial base')
 ax.text(.1775,.813,r'$B_0=\mathbb{Q}[U,r,w,t]$',ha='center',fontsize=20,color=navy)
 panel(.3675,.788,.265,.095,'Rational parameter field')
 ax.text(.5,.813,r'$B=\operatorname{Frac}(B_0)$',ha='center',fontsize=20,color=navy)
 panel(.690,.788,.265,.095,'Constructed realization')
 ax.text(.8225,.813,r'$L=\overline{B}$',ha='center',fontsize=22,color=navy)
 arrow((.322,.835),(.355,.835));arrow((.645,.835),(.678,.835))
 ax.text(.5,.750,r'Both maps are injective; $U,r,w,t$ remain algebraically independent over $\mathbb{Q}$.',ha='center',fontsize=15,color=teal)
 ax.text(.5,.717,r'Chosen roots: $z^6=-p(U,r,w,t)$ and $x^2=U$; $x\ne0$ and $z\ne0$ are proved.',ha='center',fontsize=15,color=navy)
 panel(.210,.535,.58,.132,'Allowed common domain and normalized source',face='#e8f5f0',edge='#9bcab5')
 ax.text(.5,.612,r'$P=\mathbb{Q}[U,r,w,t,z],\qquad S=P[z^{-1}]$',ha='center',fontsize=20,color=navy)
 ax.text(.5,.568,r'$S_4=\frac{5}{72}U^2(z^{-1})^{11}\,d_SU\wedge d_Sr\wedge d_Sw\wedge d_St$',ha='center',fontsize=20,color=teal)
 arrow((.34,.523),(.257,.468));arrow((.66,.523),(.742,.468))
 ax.text(.253,.504,'Universal Kähler + exterior map',ha='center',fontsize=12,color=teal)
 ax.text(.747,.504,'Universal Kähler + exterior map',ha='center',fontsize=12,color=teal)
 panel(.045,.300,.425,.155,'Old ambient field: polynomial variables')
 ax.text(.2575,.391,r'$K_0=\operatorname{Frac}(P)$',ha='center',fontsize=20,color=navy)
 ax.text(.2575,.353,r'$S_4\longmapsto\mathrm{residueScalar}\,\alpha$',ha='center',fontsize=18,color=teal)
 ax.text(.2575,.318,'The prior normalized representative, through S.',ha='center',fontsize=12,color=gray)
 panel(.530,.300,.425,.155,'Curve field: actual source theorem')
 ax.text(.7425,.391,r'$L=\overline{\mathbb{Q}(U,r,w,t)},\quad z^6+p=0$',ha='center',fontsize=18,color=navy)
 ax.text(.7425,.353,r'$S_4\longmapsto\mathrm{normalizedPoleCoefficient}\,dU\wedge dr\wedge dw\wedge dt$',ha='center',fontsize=13.5,color=teal)
 ax.text(.7425,.318,r'$r,z,f_r,\Delta\ne0$ are all proved in this realization.',ha='center',fontsize=13,color=gray)
 panel(.045,.173,.91,.080,'Actual differential relations and concrete reduction',face='#e8f5f0',edge='#9bcab5')
 ax.text(.5,.190,r'$6z^5\,dz+dp=0,\quad 2x\,dx=dU;\qquad S_4=\frac{\phi}{12}\frac{M_0+M_1V}{z^5}\,dV\wedge B+d\!\left(\frac{\phi R}{12z^5}\right)\wedge B$',ha='center',fontsize=17,color=teal)
 ax.text(.045,.131,r'$\phi=r^{11}/f_r,\ B=da\wedge dv\wedge dt$. Nonzero-polynomial certificates: $f_r\mapsto-3$, cleared $\Delta\mapsto9261$.',fontsize=13,color=gray)
 ax.text(.045,.103,'The cleared-polynomial evaluation at zero is a certificate, not a physical chart specialization.',fontsize=13,color=gray)
 ax.text(.045,.073,r'Forbidden: $K_0\to L$ killing $G\ne0$, evaluating $G^{-1}$ on the curve, or descending the old normal derivation.',fontsize=13,color=red)
 ax.text(.045,.043,'Unproved: whole-hypersurface function-field identification; comparison with the earlier trace field; residue/cohomology realization.',fontsize=12.5,color=amber)
 ax.text(.045,.016,'Both compact rows remain; no primitive, global clearing, certificate or solve is claimed.',fontsize=12.5,color=gray)
 png=out/'physical-curve-pullback.png';svg=out/'physical-curve-pullback.svg'
 fig.savefig(png,dpi=160,metadata={'Software':'Hodge Lab reproducible Matplotlib figure'})
 fig.savefig(svg,metadata={'Date':None,'Creator':'Hodge Lab reproducible Matplotlib figure'});plt.close(fig)
 svg.write_text('\n'.join(s.rstrip() for s in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
 m={'executor':'Pro root integration','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'inputs':{MODULE:sha(ROOT/MODULE),a.receipt:sha(receipt),'scripts/visualize_skew_physical_curve.py':sha(Path(__file__))},'outputs':{p.name:sha(p) for p in [png,svg,out/'generator.py']},'required_declarations':required,'python_version':sys.version,'matplotlib_version':matplotlib.__version__,'elapsed_seconds':time.monotonic()-start,'scope':'Actual allowed maps, proved generic nonzeros and normalization; precise unproved boundaries; image is not proof evidence'}
 (out/'visualization.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8');print(json.dumps(m))
if __name__=='__main__':main()
