#!/usr/bin/env python3
"""Reproduce the physical coefficient and finite-algebra trace map diagram."""
from pathlib import Path
import argparse, datetime, hashlib, json, os, re, shutil, sys, tempfile, time
os.environ.setdefault('MPLCONFIGDIR', tempfile.mkdtemp(prefix='physical-trace-mpl-'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
ROOT=Path(__file__).resolve().parents[1]
MODULE='formal/HodgeLab/OneReflectionSkew/PhysicalTraceBridge.lean'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--receipt',required=True); p.add_argument('--output-dir',required=True)
    a=p.parse_args(); start=time.monotonic(); receipt=ROOT/a.receipt
    data=json.loads(receipt.read_text(encoding='utf-8'))
    if data['status']!='PASS': raise RuntimeError('Passing focused receipt required')
    if data['source_sha256'][MODULE.removeprefix('formal/')]!=sha(ROOT/MODULE): raise RuntimeError('Proof source mismatch')
    required=['physical_base_independent','baseToCurve_injective','curve_scalar_tower','physicalEval_sourceScalar','physicalSheet_root','curveBeta_tmul','trace_curve_baseChange','trace_curve_sum','trace_curve_sourceScalar','physical_evaluation_not_trace']
    text=(ROOT/MODULE).read_text(encoding='utf-8')
    if not all(re.search(r'^theorem '+n+r'\b',text,re.M) for n in required): raise RuntimeError('Missing theorem')
    out=(ROOT/a.output_dir).resolve()
    if not out.is_relative_to(ROOT): raise RuntimeError('Output escapes repository')
    out.mkdir(parents=True,exist_ok=False); shutil.copyfile(__file__,out/'generator.py')
    navy,teal,gray,amber='#17334e','#007d83','#506475','#98600c'
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':13,'svg.hashsalt':'hodge-physical-trace-v1'})
    fig=plt.figure(figsize=(16,13),facecolor='white'); ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')
    def panel(x,y,w,h,title,face='#eef5f8',edge='#bfd1dc'):
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.009',facecolor=face,edgecolor=edge,linewidth=1.4))
        ax.text(x+.013,y+h-.026,title,fontsize=16,fontweight='bold',color=navy,va='center')
    def arrow(p,q): ax.add_patch(FancyArrowPatch(p,q,arrowstyle='-|>',mutation_scale=18,color=teal,linewidth=2))
    ax.text(.045,.958,'Physical curve to the full eighteen-sheet trace algebra',fontsize=23,fontweight='bold',color=navy)
    ax.text(.045,.921,'Proved coefficient embedding, quotient evaluation and scalar extension; the physical form boundary remains explicit.',fontsize=14,color=gray)
    panel(.045,.763,.265,.116,'Existing generic base')
    ax.text(.1775,.814,r'$K=\mathbb{Q}(v)(t)(a)$',ha='center',fontsize=22,color=navy)
    ax.text(.1775,.782,r'$f=X^{18}+X^{12}+(vX-1)^6-aX^{15}$',ha='center',fontsize=12,color=gray)
    panel(.3675,.763,.265,.116,'Existing full splitting field')
    ax.text(.5,.814,r'$S=f.\mathrm{SplittingField}$',ha='center',fontsize=20,color=navy)
    ax.text(.5,.782,'All 18 distinct roots are retained.',ha='center',fontsize=12,color=gray)
    panel(.690,.763,.265,.116,'Existing physical realization')
    ax.text(.8225,.814,r'$L=\overline{\mathbb{Q}(U,r,w,t)}$',ha='center',fontsize=20,color=navy)
    ax.text(.8225,.782,'Its original Q-algebra is preserved.',ha='center',fontsize=12,color=gray)
    arrow((.322,.823),(.355,.823)); arrow((.645,.823),(.678,.823))
    ax.text(.5,.724,r'Compatible injections $K\to S\to L$: $a\mapsto(1+r^6+w^6)/r^3$, $v\mapsto r^{-1}+rw$, $t\mapsto t$.',ha='center',fontsize=15,color=teal)
    ax.text(.5,.689,'Actual independence: U,a,v,t form a transcendence basis; the Q-scalar commuting diagram is proved.',ha='center',fontsize=14,color=gray)
    panel(.045,.503,.425,.128,'One physical evaluation')
    ax.text(.2575,.566,r'$\varepsilon:E=K[X]/(f)\longrightarrow L,\quad\theta\mapsto r$',ha='center',fontsize=20,color=navy)
    ax.text(.2575,.531,r'$\varepsilon(\mathrm{sourceScalar})=\frac{r^{11}}{12f_r}\ne0$',ha='center',fontsize=21,color=teal)
    panel(.530,.503,.425,.128,'All-sheet scalar extension')
    ax.text(.7425,.566,r'$T=L\otimes_K E\ \overset{\beta}{\simeq}_L\ L^{18}$',ha='center',fontsize=22,color=navy)
    ax.text(.7425,.531,r'$\beta(\ell\otimes e)_j=\ell\,\sigma_j(e)$',ha='center',fontsize=21,color=teal)
    ax.text(.2575,.470,'E is finite free of rank 18; no field assumption.',ha='center',fontsize=13,color=gray)
    ax.text(.7425,.470,'T has the standard left L-algebra structure.',ha='center',fontsize=13,color=gray)
    ax.text(.5,.431,r'Exhaustion proves $r=r_{\mathrm{physicalSheet}}$ and $\varepsilon=\sigma_{\mathrm{physicalSheet}}$; power slot 11 is not sheet 11.',ha='center',fontsize=14,color=gray)
    panel(.045,.268,.91,.116,'Trace compatibility for arbitrary elements',face='#e8f5f0',edge='#9bcab5')
    ax.text(.5,.326,r'$\iota(\mathrm{Tr}_{E/K}(e))=\mathrm{Tr}_{T/L}(1\otimes e)=\sum_{j=0}^{17}\sigma_j(e),\qquad \mathrm{Tr}_{T/L}(z)=\sum_{j=0}^{17}\beta(z)_j$',ha='center',fontsize=20,color=teal)
    ax.text(.5,.287,r'$\mathrm{Tr}_{T/L}(1\otimes\mathrm{sourceScalar})=0;\qquad\varepsilon(1)=1,\quad\mathrm{Tr}_{E/K}(1)=18,\quad\mathrm{Tr}_{T/L}(2\otimes1)=36.$',ha='center',fontsize=17,color=navy)
    ax.text(.045,.226,'This is the trace of the degree-18 finite algebra, not a field trace of the algebraic closure L over K.',fontsize=14,color=gray)
    panel(.045,.077,.91,.109,'Remaining physical-form dependency',face='#fff7e8',edge='#ddc59a')
    ax.text(.062,.132,r'Construct compatible allowed-domain sheet maps fixing $V=rU$ and $z$, with $U_j=V/r_j$, then prove form/source compatibility.',fontsize=14,color=amber)
    ax.text(.062,.099,r'The existing common localization $P[z^{-1}]$ remains valid. No ambient-field specialization killing $G$, and no evaluation of $G^{-1}$.',fontsize=13,color=gray)
    ax.text(.045,.034,'Scalar trace zero is separate from the full two-row source, its exactness, a primitive, a certificate or a solve.',fontsize=14,color=gray)
    png=out/'physical-trace-bridge.png'; svg=out/'physical-trace-bridge.svg'
    fig.savefig(png,dpi=160,metadata={'Software':'Hodge Lab reproducible Matplotlib figure'})
    fig.savefig(svg,metadata={'Date':None,'Creator':'Hodge Lab reproducible Matplotlib figure'}); plt.close(fig)
    svg.write_text('\n'.join(s.rstrip() for s in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
    m={'executor':'Pro root integration','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'inputs':{MODULE:sha(ROOT/MODULE),a.receipt:sha(receipt),'scripts/visualize_skew_physical_trace.py':sha(Path(__file__))},'outputs':{p.name:sha(p) for p in [png,svg,out/'generator.py']},'required_declarations':required,'python_version':sys.version,'matplotlib_version':matplotlib.__version__,'elapsed_seconds':time.monotonic()-start,'scope':'Actual coefficient/tensor maps and scalar traces; unproved physical-form comparison explicitly delimited; visualization is not proof evidence'}
    (out/'visualization.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8'); print(json.dumps(m))
if __name__=='__main__': main()
