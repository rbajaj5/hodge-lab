"""Render the actual bounded operator and exact dual support from the receipt."""
from pathlib import Path
import hashlib
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sympy as s
from search_skew_base_derivatives import source, denominator, build

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/skew-base-derivatives'
receipt = json.loads((OUT/'verification.json').read_text(encoding='utf-8'))
if receipt['status'] != 'PASS':
    raise ValueError('Successful independent verification required')
for name, digest in receipt['certificate_sha256'].items():
    if hashlib.sha256((OUT/name).read_bytes()).hexdigest() != digest:
        raise ValueError('Certificate changed: '+name)
P = source()
columns, rhs, labels = build(P, denominator('a', P), 4)
rows = sorted(set(rhs).union(*(set(c) for c in columns)))
lookup = {m:i for i,m in enumerate(rows)}
cert = json.loads((OUT/'search-a-degree4.json').read_text(encoding='utf-8'))
colors = ['#176d7b', '#c2942b', '#7361a5', '#d66450']
plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':11, 'svg.fonttype':'none'})
fig = plt.figure(figsize=(15, 9), facecolor='#fafaf6')
fig.text(.05,.94,'The full base-derivative equation: a bounded test',fontsize=23,weight='bold',color='#17343d')
fig.text(.05,.895,r'$\Gamma=z^{-5}\iota_{N/D}(dU\wedge dr\wedge dw\wedge dt),\qquad d\Gamma=\frac{5U^2}{72z^{11}}\,dU\wedge dr\wedge dw\wedge dt$',fontsize=17)
ax = fig.add_axes([.07,.20,.48,.60], facecolor='white')
for block in range(4):
    xx, yy = [], []
    for j, column in enumerate(columns):
        if labels[j][0] == block:
            xx.extend([j]*len(column)); yy.extend(lookup[e] for e in column)
    ax.scatter(xx,yy,s=2,color=colors[block],linewidths=0,alpha=.8,rasterized=False)
for item in cert['dual']:
    ax.axhline(lookup[tuple(item['exponent'])],color='#d32840',lw=1,alpha=.85)
for x in [69.5,139.5,209.5]: ax.axvline(x,color='#c7d1d0',lw=.8)
ax.set_xlim(-.5,279.5);ax.set_ylim(len(rows)-.5,-.5)
ax.set_xticks([34.5,104.5,174.5,244.5],['$N_U$','$N_r$','$N_w$','$N_t$'])
ax.set_ylabel('Coefficient rows (lexicographic monomials)')
ax.set_xlabel('70 monomials in each of four components')
ax.set_title('D = a = 1 + r⁶ + w⁶, numerator degree ≤ 4\n2,068 rows × 280 columns; colored dots = nonzero entries',fontsize=12,pad=12)
ax.text(.01,-.16,'Red lines locate the three coefficients used by the exact dual.',transform=ax.transAxes,fontsize=10,color='#8f2635')
right = fig.add_axes([.61,.51,.34,.29]);right.axis('off')
right.set_title('Four fixed denominators; every component included',loc='left',fontsize=13,pad=13)
data=[]
for name in ['1','r','t','a']:
    case=next(c for c in receipt['cases'] if c['denominator']==name and c['degree_bound']==4)
    data.append([name,str(case['rows']),str(case['columns_checked']),str(case['dual_terms'])])
table=right.table(cellText=data,colLabels=['D','Rows','Columns','Dual terms'],loc='upper left',cellLoc='center',bbox=[0,.12,1,.85])
table.auto_set_font_size(False);table.set_fontsize(11)
for (i,j),cell in table.get_celld().items():
    cell.set_edgecolor('#d7dfdd');cell.set_facecolor('#e8f1ed' if i==0 else '#ffffff')
right.text(0,-.02,'All four degree-4 spaces excluded over ℚ (also ℂ).\nBounds 0 and 2 are nested checks, not new families.',fontsize=10,va='top')
fig.text(.61,.405,'A three-coefficient certificate',fontsize=14,weight='bold',color='#17343d')
fig.text(.61,.355,r'$\lambda=\frac{3}{5}[rt^3]+\frac{1}{35}[U^2w^{12}]-\frac{1}{35}[U^2w^{12}t^2]$',fontsize=13)
fig.text(.61,.305,r'$\lambda^{T}M=0,\qquad\lambda^{T}(35U^2a^2)=1$',fontsize=16,color='#176d7b')
fig.text(.61,.235,'M is the denominator-cleared operator scaled by 84.\nThe independent checker rebuilds every column.\nThis is an inconsistency certificate, not a rank estimate.',fontsize=10,linespacing=1.6)
fig.text(.05,.065,'No target primitive found. Other denominators, higher numerator degrees and unrestricted rational coefficients remain open.',fontsize=12,weight='bold',color='#8f2635')
fig.text(.05,.027,'one-reflection-skew · protected source pinned at a6b4cc49 · finite matrix support is not a geometric phase transition',fontsize=10,color='#566b71')
for ext in ['png','svg']:
    fig.savefig(ROOT/f'visualizations/skew-base-derivatives.{ext}',dpi=160,facecolor=fig.get_facecolor())
svg = ROOT/'visualizations/skew-base-derivatives.svg'
svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n', encoding='utf-8', newline='\n')
print(json.dumps({'status':'PASS','matrix_rows':len(rows),'matrix_columns':len(columns),'certificate_terms':len(cert['dual'])}))
