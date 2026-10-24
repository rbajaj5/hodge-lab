"""Research diagram from frozen A4 receipts; no mathematical recomputation."""
from pathlib import Path
import hashlib, json, os, sys
os.environ.setdefault('MPLCONFIGDIR', '/tmp/hodge-A4-denominator-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=False)
base = Path(__file__).resolve().parent
author = base / 'lead/matrix-01/result/validation.json'
checker = base / 'checker/reconstruction-01/result/validation.json'
reported = base / 'coordinator-reported.json'
a, c, r = [json.loads(p.read_text(encoding='utf-8')) for p in (author, checker, reported)]
if a['matrix_shape'] != [3160, 3103] or c['entries_reconstructed'] != 9805480:
    raise RuntimeError('Unexpected matrix inputs')
if r['minor']['determinant'] != 28764 or r['minor']['prime'] != 65521:
    raise RuntimeError('Unexpected imported minor report')
plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':11, 'svg.hashsalt':'A4-20261024'})
fig = plt.figure(figsize=(13.8, 8), facecolor='#f6f8fb')
gs = fig.add_gridspec(1, 2, width_ratios=[1,1.15], left=.07, right=.96,
                      bottom=.26, top=.79, wspace=.23)
ax = fig.add_subplot(gs[0,0]); ax.set_facecolor('#f6f8fb')
y = np.arange(5)
ax.barh(y+.16, [702]*5, height=.29, color='#c6d0db')
ax.barh(y-.16, [702,702,702,702,294], height=.29,
        color=['#246781']*4+['#cf663e'])
ax.set_yticks(y, ['P₀','P₁ / A','P₂ / A²','P₃ / A³','P₄ / A⁴'])
ax.invert_yaxis(); ax.set_xlim(0,840)
ax.set_xlabel('Scalar parameters across all six flux components')
ax.set_title('All four lower sectors remain free', loc='left', fontweight='bold', pad=18)
for i,n in enumerate([702,702,702,702,294]):
    ax.text(n+12, i-.16, str(n), va='center', fontweight='bold')
ax.text(714, 4+.16, '702', va='center', color='#617182')
for s in ['top','right','left']: ax.spines[s].set_visible(False)
ax.tick_params(axis='y',length=0); ax.grid(axis='x',alpha=.15); ax.set_axisbelow(True)
bx = fig.add_subplot(gs[0,1]); bx.axis('off')
bx.text(0,1.02,'Top-pole rule and decisive finite-family minor', fontweight='bold', fontsize=12.5)
bx.text(0,.85,r'$(R_a-4I)Q_4=0$,  $\det(R_a-4I)=52/3$',fontsize=13)
bx.text(0,.69,r'$P_4=(T_rh_4,T_vh_4,k_4)$',fontsize=17,color='#a94b2b')
bx.text(0,.55,r'$\tau_4=-2r^7+15r$',fontsize=15)
bx.text(0,.40,'60 + 234 + 4 × 702 = 3102 parameters',fontsize=12.5)
bx.text(0,.22,'3103 × 3103 augmented minor',fontsize=16,fontweight='bold')
bx.text(0,.07,'det = 28764 (mod 65521) ≠ 0',fontsize=16,fontweight='bold',color='#195e78')
bx.text(0,-.07,'Exact determinant: coordinator’s separate FLINT execution',fontsize=10.1,color='#455566')
fig.text(.07,.935,'A to the fourth: the declared sum family is excluded',fontsize=22,fontweight='bold',color='#17344b')
fig.text(.07,.875,'Full physical source: both rows, every r / v / t derivative, positive packet orientation.',fontsize=12,color='#455566')
fig.text(.07,.190,'Gray: original 3510 parameters. Blue / orange: the 3102-parameter necessary family.',fontsize=11,color='#455566')
fig.text(.07,.146,'Pro: direct quotient columns and separate reconstruction of 9,805,480 entries; imported top-pole / support theorem.',fontsize=10.5,color='#455566')
fig.text(.07,.102,'Scope: B + B/A + B/A² + B/A³ + B/A⁴, with r exponents −10…2 and v,t degrees ≤2.',fontsize=11,color='#455566')
fig.text(.07,.058,'No rational primitive or general obstruction. Other supports, pole divisors and unbounded currents remain open.',fontsize=11,color='#455566')
svg=out/'A4-denominator-certificate.svg'; png=out/'A4-denominator-certificate.png'
fig.savefig(svg,metadata={'Date':None});fig.savefig(png,dpi=180);plt.close(fig)
svg.write_text('\n'.join(x.rstrip() for x in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
receipt={'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'matplotlib':matplotlib.__version__,
         'inputs':{str(p.relative_to(base)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (author,checker,reported)},
         'outputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (svg,png)},
         'claim_boundary':'Finite-family exclusion from separately reported coordinator determinant and imported top-pole theorem; Pro directly reconstructed matrix. Delivery IO binding is separate. No primitive or general obstruction.'}
(out/'visualization.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,indent=2))
