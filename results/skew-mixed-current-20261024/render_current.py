"""Render the checked remainder from the saved independent-check receipts.

Run in any directory: python render_current.py
Plots illustrate a single ordinary cover point; they are not solvability tests.
"""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import sympy as s

HERE = Path(__file__).resolve().parent
RAW = HERE / 'checker/check-current.json'
CENTERED = HERE / 'checker/check-regular-current.json'
raw = json.loads(RAW.read_text(encoding='utf-8'))
centered = json.loads(CENTERED.read_text(encoding='utf-8'))
a, v, t, g, k = s.symbols('a v t g k')
loc = {str(x): x for x in (a, v, t, g, k)}
rows = [s.sympify(x, locals=loc).subs({a: 3, v: 2, g: 38, k: -s.Rational(55, 3)})
        for x in raw['residual_regular_rows']]
grid = np.linspace(0, 1, 401)
ys = [s.lambdify(t, q, 'numpy')(grid) for q in rows]
fig = plt.figure(figsize=(12, 7.2), facecolor='#f7f9fc')
fig.suptitle('A regular current with a nonzero remainder', fontsize=20, x=.065, ha='left', y=.96)
fig.text(.065, .895, r'One-reflection-skew  |  $B=\mathrm{Div}_N(Q)+R_2$  |  centered $\chi=r^{-3}-v^3/3$', fontsize=13)
ax = fig.add_axes([.08, .32, .52, .48], facecolor='white')
for y, color, label in zip(ys, ['#176b98', '#b45632'], [r'$R_{2,0}$', r'$R_{2,1}$']):
    ax.plot(grid, y, color=color, linewidth=2.5, label=label)
ax.axhline(0, color='#7b8796', linewidth=.8)
ax.scatter([0, 0], [float(s.Rational(x)) for x in centered['t_zero_centered_residual']],
           color=['#176b98', '#b45632'], s=42, zorder=4)
ax.set(xlabel=r'$t$', ylabel='Remainder coefficient', title=r'One cover point: $r=1,\ v=2,\ a=3$')
ax.grid(alpha=.18)
ax.legend(frameon=False)
fig.text(.655, .76, 'Exact endpoint values', fontsize=14, weight='bold')
fig.text(.655, .67, r'$t=0:\quad (19/15876,\ 19/1134)$', fontsize=13)
fig.text(.655, .57, r'$t=1:\quad (105778/440559,$', fontsize=13)
fig.text(.71, .52, r'$-52889/97902)$', fontsize=13)
fig.text(.655, .40, 'Both source rows retained.\nAll six current coefficients are\nregular at generic t = 0.', fontsize=12, linespacing=1.6)
fig.text(.08, .22, 'What changed: the artificial t-poles cancel in the current and remainder.', fontsize=13, weight='bold')
fig.text(.08, .145, 'What remains: a nonzero trace-free source. Rank 34 and the cover are retained.\nNo full rational primitive or certificate is supplied by this identity.', fontsize=12, linespacing=1.6)
fig.text(.08, .055, 'Exact identities and endpoint values come from the saved independent checks.\nThe sampled curves are an illustration, not a proof of global regularity or rational solvability.', fontsize=10, color='#4b5563')
for ext in ['png', 'svg']:
    fig.savefig(HERE / ('regular-current.'+ext), dpi=160, facecolor=fig.get_facecolor())
manifest = {
    'inputs': {str(p.relative_to(HERE)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (RAW, CENTERED)},
    'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'scope': 'Illustration of a single cover point and the exact saved endpoints; no new mathematical verification.',
    'outputs': {('regular-current.'+e): hashlib.sha256((HERE/('regular-current.'+e)).read_bytes()).hexdigest() for e in ['png','svg']}
}
(HERE/'visualization.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
print('Rendered regular-current.png and .svg from bound receipts.')
