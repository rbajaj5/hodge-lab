"""Research diagram from frozen A7 receipts; no mathematical recomputation."""
from pathlib import Path
import hashlib, json, os, sys
os.environ.setdefault('MPLCONFIGDIR', '/tmp/hodge-A7-denominator-mpl')
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
if a['matrix_shape'] != [5280, 5209] or c['entries_reconstructed'] != 27503520:
    raise RuntimeError('Unexpected matrix inputs')
if r['minor']['determinant'] != 56940 or r['minor']['prime'] != 65519:
    raise RuntimeError('Unexpected imported minor report')
plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':11, 'svg.hashsalt':'A7-20261024'})
fig = plt.figure(figsize=(13.8, 8.4), facecolor='#f6f8fb')
gs = fig.add_gridspec(1, 2, width_ratios=[1,1.15], left=.07, right=.96,
                      bottom=.30, top=.79, wspace=.23)
ax = fig.add_subplot(gs[0,0]); ax.set_facecolor('#f6f8fb')
y = np.arange(8)
ax.barh(y+.16, [702]*8, height=.29, color='#c6d0db')
ax.barh(y-.16, [702,702,702,702,702,702,702,294], height=.29,
        color=['#246781']*7+['#cf663e'])
ax.set_yticks(y, ['P₀','P₁ / A','P₂ / A²','P₃ / A³','P₄ / A⁴','P₅ / A⁵','P₆ / A⁶','P₇ / A⁷'])
ax.invert_yaxis(); ax.set_xlim(0,840)
ax.set_xlabel('Scalar parameters across all six flux components')
ax.set_title('All seven lower sectors remain free', loc='left', fontweight='bold', pad=18)
for i,n in enumerate([702,702,702,702,702,702,702,294]):
    ax.text(n+12, i-.16, str(n), va='center', fontweight='bold')
ax.text(714, 7+.16, '702', va='center', color='#617182')
for s in ['top','right','left']: ax.spines[s].set_visible(False)
ax.tick_params(axis='y',length=0); ax.grid(axis='x',alpha=.15); ax.set_axisbelow(True)
bx = fig.add_subplot(gs[0,1]); bx.axis('off')
bx.text(0,1.02,'Top-pole rule and decisive finite-family minor', fontweight='bold', fontsize=12.5)
bx.text(0,.85,r'$(R_a-7I)Q_7=0$,  $\det(R_a-7I)=154/3$',fontsize=13)
bx.text(0,.69,r'$P_7=(T_rh_7,T_vh_7,k_7)$',fontsize=17,color='#a94b2b')
bx.text(0,.55,r'$\tau_7=-11r^7+24r$',fontsize=15)
bx.text(0,.40,'60 + 234 + 7 × 702 = 5208 parameters',fontsize=12.5)
bx.text(0,.22,'5209 × 5209 augmented minor',fontsize=16,fontweight='bold')
bx.text(0,.07,'det = 56940 (mod 65519) ≠ 0',fontsize=16,fontweight='bold',color='#195e78')
bx.text(0,-.07,'Exact determinant: coordinator’s separate FLINT execution',fontsize=10.1,color='#455566')
fig.text(.07,.935,'A to the seventh: the declared sum family is excluded',fontsize=22,fontweight='bold',color='#17344b')
fig.text(.07,.875,'Full physical source: both rows, every r / v / t derivative, positive packet orientation.',fontsize=12,color='#455566')
fig.text(.07,.190,'Gray: original 5616 parameters. Blue / orange: the 5208-parameter necessary family.',fontsize=11,color='#455566')
fig.text(.07,.146,'Pro: direct quotient columns and separate reconstruction of 27,503,520 entries; imported top-pole / support theorem.',fontsize=10.5,color='#455566')
fig.text(.07,.102,'Scope: B + B/A + B/A² + B/A³ + B/A⁴ + B/A⁵ + B/A⁶ + B/A⁷, with r exponents −10…2 and v,t degrees ≤2.',fontsize=11,color='#455566')
fig.text(.07,.058,'No rational primitive or general obstruction. Other supports, pole divisors and unbounded currents remain open.',fontsize=11,color='#455566')
svg=out/'A7-denominator-certificate.svg'; png=out/'A7-denominator-certificate.png'
fig.savefig(svg,metadata={'Date':None});fig.savefig(png,dpi=180);plt.close(fig)
svg.write_text('\n'.join(x.rstrip() for x in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
receipt={'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'matplotlib':matplotlib.__version__,
         'inputs':{str(p.relative_to(base)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (author,checker,reported)},
         'outputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (svg,png)},
         'claim_boundary':'Finite-family exclusion from separately reported coordinator determinant and imported top-pole theorem; Pro directly reconstructed matrix. Delivery IO binding is separate. No primitive or general obstruction.'}
(out/'visualization.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,indent=2))
