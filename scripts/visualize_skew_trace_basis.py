"""Visualize the split-algebra trace statements, with their explicit limitations.

This diagram is not a new proof or a sample of physical roots. It records the
formulas in TraceFreeBasis.lean and SplitTraceQuotient.lean. The small bars are
the exact rational specialization a=1 and a=2, not a general-field ordering.
"""
from pathlib import Path
import hashlib
import json
import re

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'formal/HodgeLab/OneReflectionSkew'
names = ['TraceFreeBasis.lean', 'SplitTraceQuotient.lean']
sources = {name: (SOURCE / name).read_text(encoding='utf-8') for name in names}
required = {
    names[0]: ['trace_basis_initial', 'trace_basis_last', 'trace_eq_coordinate', 'traceFree_finrank'],
    names[1]: ['evaluationEquiv', 'trace_transport', 'quotient_derivative_isUnit',
               'quotientTraceFreeBasis', 'quotient_traceFree_finrank'],
}
for name, declarations in required.items():
    for declaration in declarations:
        if not re.search(r'^(?:def|theorem) ' + declaration + r'\b', sources[name], re.M):
            raise ValueError(f'Missing source declaration: {name}:{declaration}')
n = int(re.search(r'abbrev SplitAlgebra.*?Fin (\d+)', sources[names[0]], re.S).group(1))
if n != 18:
    raise ValueError('This diagram is specifically for the degree-18 statements')

INK, MUTED = '#183b43', '#53676c'
BG, TEAL, TEAL_LIGHT, GOLD = '#fafaf7', '#509997', '#d7ebe8', '#d6bd89'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                     'svg.hashsalt': 'skew-trace-basis-v1'})
fig = plt.figure(figsize=(16, 10), facecolor=BG)
canvas = fig.add_axes([0, 0, 1, 1])
canvas.set_xlim(0, 1)
canvas.set_ylim(0, 1)
canvas.axis('off')

def box(x, y, width, height, color=TEAL_LIGHT):
    canvas.add_patch(FancyBboxPatch((x, y), width, height,
        boxstyle='round,pad=0.008,rounding_size=0.012',
        facecolor=color, edgecolor='none'))

fig.text(.055, .944, 'A full degree-18 algebra, a 17-dimensional trace kernel',
         fontsize=23, fontweight='bold', color=INK)
fig.text(.055, .900,
         r'Assume $K$ is a field, $a_{18}\ne0$, and all 18 roots $\rho_j\in K$ are distinct.',
         fontsize=14, color=MUTED)

box(.055, .710, .40, .135)
box(.545, .710, .40, .135)
fig.text(.075, .807, 'The whole quotient algebra', fontsize=13, fontweight='bold', color=INK)
fig.text(.075, .757, r'$A=K[Z]/(P),\quad P(Z)=a_{18}\prod_{j=0}^{17}(Z-\rho_j)$',
         fontsize=18, color=INK)
fig.text(.565, .807, 'All 18 evaluation components', fontsize=13, fontweight='bold', color=INK)
fig.text(.565, .757, r'$A\ \cong\ K^{18},\qquad [f]\longmapsto(f(\rho_j))_{j=0}^{17}$',
         fontsize=18, color=INK)
canvas.annotate('', xy=(.535, .777), xytext=(.465, .777),
                arrowprops={'arrowstyle': '<->', 'color': INK, 'lw': 2})
fig.text(.5, .729, 'trace preserved', ha='center', fontsize=10, color=MUTED)

fig.text(.055, .657, 'Derivative-weighted basis of the entire algebra',
         fontsize=15, fontweight='bold', color=INK)
fig.text(.055, .612,
         r'$b_i=Z^i/P^{\prime}(Z)\ \mathrm{in}\ A,\quad '
         r'b_i(\rho_j)=\rho_j^i/P^{\prime}(\rho_j),\qquad 0\leq i\leq17$',
         fontsize=19, color=INK)
fig.text(.055, .574, r'$P^{\prime}(Z)$ is a unit in $A$ under the stated assumptions.',
         fontsize=11, color=MUTED)

left, right, bottom, height = .055, .945, .442, .080
width = (right-left)/n
for i in range(n):
    canvas.add_patch(Rectangle((left+i*width, bottom), width-.003, height,
                              facecolor=TEAL_LIGHT if i<n-1 else GOLD,
                              edgecolor=BG, linewidth=1))
    fig.text(left+(i+.47)*width, bottom+.052, rf'$b_{{{i}}}$',
             ha='center', fontsize=12, color=INK)
    fig.text(left+(i+.47)*width, bottom+.014, '0' if i<n-1 else r'$1/a_{18}$',
             ha='center', fontsize=12, fontweight='bold', color=INK)
fig.text(.055, .536, 'Basis vector / algebra trace', fontsize=10, color=MUTED)
fig.text(.055, .413, r'$b_0,\ldots,b_{16}$ form a basis of $\ker(\operatorname{Tr})$',
         fontsize=14, color=INK)
fig.text(.945, .413, 'last slot carries the trace', ha='right', fontsize=11, color=MUTED)

box(.055, .216, .535, .144, color='#edf1ef')
fig.text(.075, .321, 'The last coordinate determines the trace',
         fontsize=13, fontweight='bold', color=INK)
fig.text(.075, .277,
         r'$x=\sum_i c_i b_i\quad\Longrightarrow\quad '
         r'\operatorname{Tr}(x)=c_{17}/a_{18}$', fontsize=20, color=INK)
fig.text(.075, .235, 'The leading coefficient is retained; no monic normalization is hidden.',
         fontsize=11, color=MUTED)

ax = fig.add_axes([.665, .225, .27, .115], facecolor=BG)
ax.barh([1, 0], [1, .5], color=[TEAL, GOLD], height=.48)
ax.set_xlim(0, 1.18)
ax.set_yticks([1, 0], [r'$a_{18}=1$', r'$a_{18}=2$'], fontsize=12)
ax.set_xticks([])
ax.tick_params(axis='y', length=0)
ax.spines[:].set_visible(False)
ax.text(1.03, 1, '1', va='center', color=INK, fontsize=13)
ax.text(.53, 0, '1/2', va='center', color=INK, fontsize=13)
fig.text(.665, .361, r'Exact rational examples: $\operatorname{Tr}(b_{17})$',
         fontsize=12, fontweight='bold', color=INK)

canvas.plot([.055, .945], [.18, .18], color='#c4cecb', linewidth=1)
fig.text(.055, .143, 'Trace zero does not establish exactness or a primitive.',
         fontsize=15, fontweight='bold', color=INK)
fig.text(.055, .105, 'Split distinct roots are assumed. Unsplit descent and the literal physical source are not checked here.',
         fontsize=12, color=MUTED)
fig.text(.055, .065, 'Statement map: TraceFreeBasis.lean + SplitTraceQuotient.lean · the quotient is an algebra, not assumed to be a field.',
         fontsize=10, color=MUTED)
fig.text(.055, .035, 'No sampled roots, numerical rank estimate, certificate, or new acceptance result is represented.',
         fontsize=10, color=MUTED)

out = ROOT / 'visualizations'
out.mkdir(exist_ok=True)
fig.savefig(out / 'skew-trace-basis.png', dpi=150)
fig.savefig(out / 'skew-trace-basis.svg', metadata={'Date': None})
svg = out / 'skew-trace-basis.svg'
svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',
               encoding='utf-8', newline='\n')
plt.close(fig)
print(json.dumps({'outputs': ['visualizations/skew-trace-basis.png', 'visualizations/skew-trace-basis.svg'],
                  'matplotlib': matplotlib.__version__,
                  'source_sha256': {name: hashlib.sha256((SOURCE/name).read_bytes()).hexdigest()
                                    for name in names}}, indent=2))
