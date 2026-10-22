"""Reproduce the protected monomial substitution table and proof boundary."""
from fractions import Fraction
from pathlib import Path
import hashlib, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

R = Path(__file__).resolve().parents[1]
O = R / 'formal/results/skew-chart'
v = json.loads((O / 'validation.json').read_text(encoding='utf-8'))
if v['status'] != 'PASS':
    raise RuntimeError('Passing Lean receipt required')
for name, h in {**v['source_lf_sha256'], **v['reused_source_lf_sha256']}.items():
    if hashlib.sha256((R/'formal'/name).read_bytes().replace(b'\r\n', b'\n')).hexdigest() != h:
        raise RuntimeError('Checked proof source changed: ' + name)
binding = json.loads((O/'source-binding.json').read_text(encoding='utf-8'))
if hashlib.sha256((O/'source-binding.json').read_bytes()).hexdigest() != v['binding_receipt_lf_sha256']:
    raise RuntimeError('Source-binding receipt changed')
pins = json.loads((O/'inputs.json').read_text(encoding='utf-8'))['pins']
pin = next(p for p in pins if p['upstream_path'].endswith('/record.json'))
raw = (R/pin['path']).read_bytes().replace(b'\r\n', b'\n')
if hashlib.sha256(raw).hexdigest() != pin['sha256']:
    raise RuntimeError('Protected record changed')
record = json.loads(raw)

def monomial(c, e, variables):
    c = Fraction(c)
    body = ''.join(s if n == 1 else s+'^{'+str(n)+'}' for s, n in zip(variables, e) if n)
    sign = '-' if c < 0 else ''
    c = abs(c)
    coef = (str(c.numerator) if c.denominator == 1 else r'\frac{'+str(c.numerator)+'}{'+str(c.denominator)+'}')
    if c == 1 and body:
        coef = ''
    return '$'+sign+coef+body+'$'

rows, data = [], []
for c, e in record['F']['terms']:
    chart = [e[0]+e[1]+e[2], e[1], e[2], e[4], e[5]]
    if e[5] == 6:
        target = '$7z^6$'; power = -1
    else:
        if chart[0] % 2 or chart[4]:
            raise RuntimeError('Unexpected chart monomial')
        pexp = [chart[0]//2, *chart[1:4], 0]
        target = monomial(7*Fraction(c), pexp, ['U', 'r', 'w', 't', 'z'])
        power = pexp[0]
    rows.append([monomial(c, e, ['X_0','X_1','X_2','Y_0','Y_1','Y_2']),
                 monomial(c, chart, ['x','r','w','t','z']), target])
    data.append({'coefficient': c, 'protected_exponents': e, 'chart_exponents': chart, 'U_power': power})
if len(rows) != binding['F_terms_checked'] or len(rows) != 10:
    raise RuntimeError('Term count mismatch')
(O/'visualization-data.json').write_text(json.dumps({'terms': data, 'source': 'A -> x^3',
    'theorems': v['new_theorems'], 'negative_controls': v['negative_controls'],
    'limits': 'Polynomial identity only; the source differential is not normalized in Lean.'}, indent=2)+'\n', encoding='utf-8', newline='\n')

plt.rcParams['svg.hashsalt'] = 'hodge-lab-skew-chart'
fig = plt.figure(figsize=(16,9), facecolor='#faf9f4')
fig.text(.04,.94,'From the protected sextic to the actual Lean chart polynomial',fontsize=20,weight='bold',color='#17333b')
fig.text(.04,.89,'one-reflection-skew  •  (X₀, X₁, X₂, Y₀, Y₁, Y₂) = (x, rx, wx, 1, t, z)  •  U = x²',fontsize=13,color='#53696e')
ax = fig.add_axes([.04,.25,.55,.57]);ax.axis('off')
table = ax.table(cellText=rows,colLabels=['Protected term in F','Substitute chart','Contribution to 7F'],
                 cellLoc='center',colWidths=[.34,.33,.33],bbox=[0,0,1,1])
table.auto_set_font_size(False);table.set_fontsize(14)
colors = {3:'#d5e9e4',2:'#e5efda',1:'#f3e5c9',0:'#e8e2f2',-1:'#dde8f1'}
for (i,j),cell in table.get_celld().items():
    cell.set_edgecolor('#c3d4d0')
    cell.set_facecolor('#173f48' if i == 0 else colors[data[i-1]['U_power']])
    if i == 0:cell.set_text_props(color='white',weight='bold',fontsize=12)
fig.text(.04,.205,'All 10 terms reconstructed from the pinned protected record; 9 give p7 and 1 gives 7z⁶.',fontsize=11.5,color='#53696e')
bx = fig.add_axes([.64,.24,.32,.59]);bx.axis('off')
boxes = [( .67, .29, 'NEW: exact polynomial binding',
           '$F = z^6 + P(x^2)$\n$7F = 7z^6 + \\operatorname{eval}(p7)$\n$A = x^3$', '#e4f1ec', '#14737a'),
         (.29, .25, 'Remaining formal dependency',
          'Volume / Jacobian / residue factors\nTransport the prescribed differential\ninto the four-component operator', '#fff0d6', '#aa792b'),
         ( .00, .18, 'PREVIOUS: bounded Lean exclusion',
           'Numerators of total degree ≤ 4\nFixed denominator a = 1 + r⁶ + w⁶', '#ece9f6', '#7b68a5')]
for y,h,title,body,fill,edge in boxes:
    bx.add_patch(FancyBboxPatch((0,y),1,h,boxstyle='round,pad=.018',facecolor=fill,edgecolor=edge,transform=bx.transAxes))
    bx.text(.035,y+h-.055,title,fontsize=12,weight='bold',color=edge,transform=bx.transAxes)
    bx.text(.035,y+.04,body,fontsize=12,color='#17333b',linespacing=1.5,transform=bx.transAxes)
for top,bottom in [(.65,.56),(.27,.20)]:
    bx.annotate('',xy=(.5,bottom),xytext=(.5,top),xycoords='axes fraction',arrowprops={'arrowstyle':'->','linestyle':'--','color':'#aa792b','lw':1.8})
fig.text(.04,.13,f"{v['new_theorems']} theorem audits  •  1 new-module kernel replay  •  3 deliberate errors rejected",fontsize=14,color='#14737a',weight='bold')
fig.text(.04,.077,'No nonvanishing is needed for the polynomial identities. Chart inversion and the square cover need separate hypotheses.',fontsize=11.7,color='#53696e')
fig.text(.04,.035,'This closes the polynomial-binding step. No primitive, new exclusion family or accepted solve is established.',fontsize=12,color='#53696e')
for ext in ['svg','png']:
    fig.savefig(R/'visualizations'/('skew-chart.'+ext),dpi=170,facecolor=fig.get_facecolor(),metadata={'Date':None} if ext=='svg' else None)
p = R/'visualizations/skew-chart.svg'
p.write_text('\n'.join(s.rstrip() for s in p.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8',newline='\n')
print('PASS: protected-term diagram generated from pinned inputs and checked receipt')
