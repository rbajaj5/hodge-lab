"""Render the actual rebuilt 49x15 operator and its proven dependency chain."""
from pathlib import Path
from fractions import Fraction
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/one-reflection-skew-hessian-source'


def main():
    report = json.loads((OUT / 'reconstruction.json').read_text(encoding='utf-8'))
    if report['status'] != 'PASS':
        raise ValueError('A passing reconstruction is required')
    rows = report['row_labels']
    lookup = {r: i for i, r in enumerate(rows)}
    matrix = np.zeros((len(rows), len(report['quadratic_pairs'])))
    for j, col in enumerate(report['residual_columns']):
        for r, c in col:
            x = float(Fraction(c))
            matrix[lookup[r], j] = np.sign(x) * np.log10(1 + abs(x))
    paper, ink, teal, slate = '#FAFAF5', '#17323B', '#166A70', '#53666D'
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'text.color': ink,
                         'axes.labelcolor': ink, 'xtick.color': slate, 'ytick.color': slate})
    fig = plt.figure(figsize=(14, 9), facecolor=paper)
    fig.text(.055, .946, 'From the protected sextic to the corrected Hessian ideal',
             fontsize=22, weight='bold')
    fig.text(.055, .908, 'one-reflection-skew  /  degree 6  /  exact rational reconstruction', color=slate)
    chain = fig.add_axes([.05, .24, .39, .61]); chain.set_xlim(0, 1); chain.set_ylim(0, 1); chain.axis('off')
    boxes = [('$F, A, q=1$', 'Protected source; all six partial derivatives'),
             ('15 Hessian coefficient columns', r'$H_{ij}=(2-\delta_{ij})A Z_i Z_j F_{ij}$'),
             ('Exact quotient by $J_{12}$', '882 rows / 684 columns / rank 636\nFull source-character block; six components'),
             ('49 rows / rank 4', '567 saved coefficients match exactly\nTwo-way identities recover the corrected ideal')]
    for k, (title, body) in enumerate(boxes):
        y = .81 - k * .235
        chain.add_patch(FancyBboxPatch((.025, y), .92, .17, boxstyle='round,pad=0.012',
                                      facecolor='white', edgecolor=teal, linewidth=1.5))
        chain.text(.065, y + .125, title, weight='bold', fontsize=13, va='center')
        chain.text(.065, y + .057, body, fontsize=10.3, color=slate, va='center')
        if k < 3:
            chain.annotate('', xy=(.48, y-.054), xytext=(.48, y-.015),
                           arrowprops={'arrowstyle':'->', 'color':teal, 'lw':1.5})
    ax = fig.add_axes([.54, .28, .36, .56])
    lim = np.max(np.abs(matrix))
    im = ax.imshow(matrix, aspect='auto', interpolation='nearest', cmap='PuOr', vmin=-lim, vmax=lim)
    ax.set_title('Rebuilt residual coefficient matrix', fontsize=13, pad=13)
    ax.set_xticks(range(15), [f'{i}{j}' for i, j in report['quadratic_pairs']], fontsize=9)
    ax.set_xlabel(r'Column $ij$ represents $a_i a_j$')
    ticks = list(range(0, len(rows), 6))
    ax.set_yticks(ticks, [str(rows[i]) for i in ticks], fontsize=9)
    ax.set_ylabel('Global degree-12 monomial row')
    cb = fig.colorbar(im, ax=ax, fraction=.045, pad=.03)
    cb.set_label(r'$\mathrm{sign}(c)\log_{10}(1+|c|)$', fontsize=10)
    fig.text(.055, .188, 'Q_anchor belongs to this rebuilt space. Historical Q3 does not.',
             color=teal, fontsize=15, weight='bold')
    fig.text(.055, .148, 'At a = (1,1,1,1,1): every rebuilt row = 0, while Q3 = 5/4. '
             'Changed source and residual controls fail.', fontsize=11)
    fig.text(.055, .103, 'Reused height certificate: regular sequence; Hilbert series (1+t)^4 / (1-t); '
             'projective scheme length 16.', color=slate, fontsize=10.5)
    fig.text(.055, .060, 'A necessary Hessian quotient, not the full E2 system or a rational primitive. '
             'Color encodes coefficients, not geometry.', color=slate, fontsize=10.5)
    fig.savefig(OUT / 'source-map.png', dpi=150, facecolor=paper)
    fig.savefig(OUT / 'source-map.svg', facecolor=paper)
    svg = OUT / 'source-map.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines()) + '\n',
                   encoding='utf-8', newline='\n')
    plt.close(fig)


if __name__ == '__main__':
    main()
