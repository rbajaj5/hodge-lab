"""Reproduce the receipt lifecycle and conditional polynomial-binding figure.

Reads completed receipts and the independent exact coefficient table. It does
not sample physical roots, establish distinctness, or perform a proof replay.
Requires Matplotlib; run `python3 -B scripts/visualize_skew_physical_cover.py`.
"""
from pathlib import Path
import hashlib
import json
import os
import tempfile

os.environ.setdefault('MPLCONFIGDIR', str(Path(tempfile.gettempdir()) / 'hodge-cover-mpl'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / 'results/ci-receipt-physical-cover-20261023'
INPUTS = {
    'sequence': BATCH / 'sequence-executed/sequence.json',
    'forms': BATCH / 'sequence-executed/forms/validation.json',
    'trace': BATCH / 'sequence-executed/trace/validation.json',
    'physical': BATCH / 'lean-development/checker-01/validation.json',
    'source': BATCH / 'physical-source/validation.json',
    'derivation': BATCH / 'math-review/derivation-review.json',
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    records = {key: json.loads(path.read_text(encoding='utf-8')) for key, path in INPUTS.items()}
    for key in ['sequence', 'forms', 'trace', 'physical', 'source']:
        if records[key]['status'] != 'PASS':
            raise RuntimeError('A completed PASS receipt is required: ' + key)
    if records['sequence']['historical_files_changed']:
        raise RuntimeError('Historical evidence was changed')
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'svg.hashsalt': 'hodge-physical-cover-20261023',
                         'mathtext.fontset': 'dejavusans'})
    navy, blue, green, amber, gray = '#172f4a', '#286ea6', '#28745f', '#aa6c11', '#63778b'
    fig = plt.figure(figsize=(14, 11), facecolor='#f7f9fc')
    grid = fig.add_gridspec(3, 2, height_ratios=[0.95, 1.5, 1.1], hspace=0.36, wspace=0.13,
                          left=0.055, right=0.97, top=0.88, bottom=0.12)
    fig.text(0.055, 0.955, 'One literal cover, one conditional link', fontsize=25, color=navy, weight='bold')
    fig.text(0.055, 0.917, 'Hodge Lab · 23 October 2026 · reviewed local handoff; remote publication belongs to coordinator',
             fontsize=11, color=gray)

    ax = fig.add_subplot(grid[0, :]); ax.set_axis_off()
    ax.text(0, 1.02, 'A  Exact polynomial and coefficient support', color=navy, weight='bold', transform=ax.transAxes)
    ax.text(0.5, 0.79, r'$f(r)=r^{18}+r^{12}+(vr-1)^6-ar^{15}$', ha='center', fontsize=24, color=navy,
            transform=ax.transAxes)
    table = records['derivation']['results']['coefficient_table']
    labels = {0: '$1$', 1: '$-6v$', 2: '$15v^2$', 3: '$-20v^3$', 4: '$15v^4$',
              5: '$-6v^5$', 6: '$v^6$', 12: '$1$', 15: '$-a$', 18: '$1$'}
    for degree in range(19):
        x, width = degree / 19, 0.047
        nonzero = table[str(degree)] != '0'
        color = '#e3edf7' if nonzero else '#edf0f4'
        if degree == 18: color = '#cfebe2'
        box = FancyBboxPatch((x, 0.20), width, 0.29, boxstyle='round,pad=0.002,rounding_size=0.012',
                             facecolor=color, edgecolor='white', transform=ax.transAxes)
        ax.add_patch(box)
        ax.text(x + width / 2, 0.35, labels.get(degree, '$0$'), ha='center', va='center', fontsize=10,
                color=navy if nonzero else '#a0aab6', transform=ax.transAxes)
        ax.text(x + width / 2, 0.09, str(degree), ha='center', color=gray, fontsize=9, transform=ax.transAxes)
    ax.text(0, -0.08, 'Power of r. All lower terms have degree ≤15; leading coefficient is 1 for every a,v.',
            color=gray, fontsize=10, transform=ax.transAxes)

    def panel(axis, title):
        axis.set_axis_off()
        axis.text(0, 1.04, title, transform=axis.transAxes, color=navy, weight='bold', fontsize=12)
    def box(axis, x, y, w, h, heading, detail, fill='#ffffff', color=navy):
        axis.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.012,rounding_size=0.02',
                       transform=axis.transAxes, facecolor=fill, edgecolor='#d5dde7', linewidth=1))
        axis.text(x + 0.025, y + h - 0.055, heading, transform=axis.transAxes, va='top',
                  fontsize=11, weight='bold', color=color)
        axis.text(x + 0.025, y + h - 0.135, detail, transform=axis.transAxes, va='top',
                  fontsize=9.5, color=gray, linespacing=1.45)
    left = fig.add_subplot(grid[1, 0]); panel(left, 'B  Historical evidence and fresh executions')
    box(left, 0, 0.66, 0.96, 0.29, 'Immutable historical forms receipt',
        'SHA256 29cc594f52a4…1b1a1c4c\nOriginal trace input pin retained; no replacement.', '#f1f5fa')
    left.annotate('', xy=(0.755, 0.57), xytext=(0.755, 0.65), xycoords='axes fraction',
                   arrowprops={'arrowstyle': '->', 'color': gray, 'lw': 1.6})
    box(left, 0, 0.30, 0.45, 0.27, 'Fresh forms: PASS',
        f"{records['forms']['new_theorems']} audits · 1 replay\n{records['forms']['elapsed_seconds']:.1f} s · separate output", '#e9f5ef', green)
    box(left, 0.51, 0.30, 0.45, 0.27, 'Fresh trace: PASS',
        f"{records['trace']['new_declarations_audited']} audits · 3 replays\n{records['trace']['elapsed_seconds']:.1f} s · separate output", '#e9f5ef', green)
    left.annotate('', xy=(0.505, 0.44), xytext=(0.455, 0.44), xycoords='axes fraction',
                   arrowprops={'arrowstyle': '->', 'color': green, 'lw': 1.6})
    left.text(0.02, 0.18, f"{records['sequence']['historical_files_checked']:,} tracked result files unchanged", color=green,
              weight='bold', transform=left.transAxes, fontsize=12)
    left.text(0.02, 0.07, 'Original CI failure is retained. The affected sequence\npassed locally; no fresh remote CI result is claimed.',
              color=gray, transform=left.transAxes, fontsize=10)

    right = fig.add_subplot(grid[1, 1]); panel(right, 'C  The single new mathematical bridge')
    box(right, 0, 0.68, 0.96, 0.27, 'ASSUMED: eighteen distinct roots in K',
        r'$\rho:\mathrm{Fin}(18)\to K$ injective; $f(\rho_j)=0$ for all $j$.' + '\nK is a field; a,v are arbitrary.', '#fff5de', amber)
    right.annotate('', xy=(0.49, 0.59), xytext=(0.49, 0.67), xycoords='axes fraction',
                   arrowprops={'arrowstyle': '->', 'color': gray, 'lw': 1.6})
    box(right, 0, 0.31, 0.96, 0.28, 'PROVED: literal polynomial equals split cover',
        r'$f(r)=(r-\rho_0)\cdots(r-\rho_{17})$' + '\nDistinct factors divide f; both sides are monic degree 18.', '#e9f5ef', green)
    right.text(0.02, 0.20, f"{records['physical']['new_declarations_audited']} declaration audits · 1 module replay · {records['physical']['elapsed_seconds']:.1f} s",
               color=green, weight='bold', transform=right.transAxes, fontsize=11)
    right.text(0.02, 0.08, 'One approach used. Helpers and two trace corollaries\nreuse the completed basis; no separability or descent proof.',
               color=gray, transform=right.transAxes, fontsize=10)

    trace = fig.add_subplot(grid[2, 0])
    trace.set_facecolor('#ffffff')
    trace.set_title('D  Exact split trace after binding', loc='left', fontsize=12, color=navy, weight='bold', pad=16)
    trace.plot(range(18), [0] * 17 + [1], 'o', ms=6, color=blue)
    trace.vlines(17, 0, 1, color=green, lw=2)
    trace.axhline(0, lw=1, color='#b9c6d4')
    trace.set_ylim(-0.18, 1.3); trace.set_xlim(-0.6, 17.8)
    trace.set_xticks([0, 5, 11, 16, 17]); trace.set_yticks([0, 1]); trace.tick_params(colors=gray, labelsize=9)
    trace.set_xlabel(r'Index $i$ in $b_i=r^i/f\,\prime(r)$', color=gray, fontsize=10)
    trace.set_ylabel(r'$\operatorname{Tr}(b_i)$', color=gray, fontsize=11)
    trace.text(1, 0.79, 'First 17 vectors: trace 0\nLast vector: trace 1', color=navy, fontsize=11)
    for spine in ['top', 'right']: trace.spines[spine].set_visible(False)
    trace.spines['left'].set_color('#d5dde7'); trace.spines['bottom'].set_color('#d5dde7')
    trace.text(0, -0.31, 'All 18 components retained. Trace zero does not mean zero or exact.',
               color=gray, fontsize=9, transform=trace.transAxes)

    control = fig.add_subplot(grid[2, 1]); panel(control, 'E  Why the root hypotheses remain explicit')
    box(control, 0, 0.05, 0.96, 0.90, 'At a=2, v=1: a repeated-root control',
        r'$f(r)=r^{12}(r^3-1)^2+(r-1)^6$' + '\n\n' +
        r'$f(1)=f\,\prime(1)=0,\quad f\,\prime\prime(1)=18$ over $\mathbb{Q}$.' + '\n\n' +
        'Taking every listed root as 1 satisfies root membership,\nbut f(2)=200705 while (2−1)¹⁸=1.\nDistinctness cannot be dropped.', '#fff5de', amber)
    fig.text(0.055, 0.022, 'Encodes pinned receipts, exact coefficients, conditional proof dependencies and trace values. '
             'It neither plots physical roots nor establishes the missing physical hypotheses.', fontsize=9, color=gray)
    out = ROOT / 'visualizations'; out.mkdir(exist_ok=True)
    png, svg = out / 'skew-physical-cover-binding.png', out / 'skew-physical-cover-binding.svg'
    fig.savefig(png, dpi=160, facecolor=fig.get_facecolor(), metadata={'Software': 'Hodge Lab / Matplotlib'})
    fig.savefig(svg, facecolor=fig.get_facecolor(), metadata={'Date': None, 'Creator': 'Hodge Lab / Matplotlib'})
    plt.close(fig)
    receipt = {'status': 'GENERATED', 'generator': 'scripts/visualize_skew_physical_cover.py',
               'generator_sha256': digest(Path(__file__).resolve()), 'matplotlib': matplotlib.__version__,
               'input_sha256': {str(p.relative_to(ROOT)): digest(p) for p in INPUTS.values()},
               'output_sha256': {str(p.relative_to(ROOT)): digest(p) for p in [png, svg]},
               'scope': 'Receipt separation, exact coefficient support, conditional binding, split traces and repeated-root control; not independent proof evidence.'}
    (BATCH / 'visualization.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
