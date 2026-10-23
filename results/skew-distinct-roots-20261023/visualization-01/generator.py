"""Render the exact eliminant, field tower and scope of generic distinctness.

Reads completed evidence; does not approximate roots or replay proofs.
Run from the notebook root with a fresh --output-dir (relative to formal,
or absolute). Matplotlib is the only non-standard Python dependency.
"""
from pathlib import Path
import hashlib
import json
import os
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / 'results/skew-distinct-roots-20261023'
sys.path.insert(0, str(ROOT / 'formal'))
from fresh_receipts import fresh_output_dir

os.environ.setdefault('MPLCONFIGDIR', str(Path(tempfile.gettempdir()) / 'hodge-distinct-mpl'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

INPUTS = {
    'lean': BATCH / 'lean-development/checker-01/validation.json',
    'exact': BATCH / 'math-review/exact-01/stdout.json',
    'source': BATCH / 'source-check/validation.json',
    'pins': BATCH / 'source-pins.json',
    'old_control': ROOT / 'results/ci-receipt-physical-cover-20261023/math-review/derivation-review.json',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def render(records, out):
    exact, lean = records['exact'], records['lean']
    require(lean['status'] == 'PASS', 'A completed focused Lean PASS receipt is required')
    require(records['source']['status'] == 'PASS', 'A completed source comparison is required')
    require(exact['status'] == 'PASS_EXACT_IDENTITY_AND_THREE_MUTATION_CONTROLS',
            'The exact eliminant computation and controls must have passed')
    require(exact['a_eliminated'] and exact['D_constant_term'] == -15 and
            exact['f_constant_term'] == 1, 'Unexpected eliminant data')
    require(all(term['a_power'] == 0 for term in exact['D_terms']), 'a was not eliminated')
    old = records['old_control']['results']['specialization']
    require((old['a'], old['v'], old['f_at_1'], old['derivative_at_1'],
             old['second_derivative_at_1']) == ('2', '1', '0', '0', '18'),
            'Historical specialization control differs')

    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'mathtext.fontset': 'dejavusans',
                         'svg.hashsalt': 'hodge-generic-distinct-roots-20261023'})
    navy, green, blue, amber, gray = '#19324d', '#25705a', '#286ea6', '#9a6013', '#5c6c80'
    fig = plt.figure(figsize=(15, 12), facecolor='#f7f9fc')
    grid = fig.add_gridspec(3, 2, height_ratios=[1.05, 1.65, 1.10],
                           left=0.055, right=0.975, top=0.88, bottom=0.10,
                           hspace=0.34, wspace=0.13)
    fig.text(0.055, 0.953, 'Generic cover: eighteen distinct roots',
             fontsize=25, weight='bold', color=navy)
    fig.text(0.055, 0.918, 'One elimination argument · explicit rational-function tower · full splitting field',
             fontsize=13, color=gray)

    def panel(ax, title):
        ax.set_axis_off()
        ax.text(0, 1.04, title, transform=ax.transAxes, fontsize=12, weight='bold', color=navy)

    def box(ax, x, y, w, h, title, detail, fill='#ffffff', color=navy):
        ax.add_patch(FancyBboxPatch((x, y), w, h,
            boxstyle='round,pad=0.012,rounding_size=0.018',
            facecolor=fill, edgecolor='#d4dce7', linewidth=1, transform=ax.transAxes))
        ax.text(x + 0.025, y + h - 0.04, title, va='top', fontsize=11,
                weight='bold', color=color, transform=ax.transAxes)
        ax.text(x + 0.025, y + h - 0.115, detail, va='top', fontsize=10,
                linespacing=1.4, color=gray, transform=ax.transAxes)

    def arrow(ax, x, upper, lower):
        ax.annotate('', xy=(x, lower), xytext=(x, upper), xycoords='axes fraction',
                    arrowprops={'arrowstyle': '->', 'color': gray, 'lw': 1.4})

    exact_ax = fig.add_subplot(grid[0, :]); panel(exact_ax, 'A  Eliminate the transcendental parameter a')
    exact_ax.text(0.5, 0.84, r'$f(X)=X^{18}+X^{12}+(vX-1)^6-aX^{15}$',
                  ha='center', fontsize=20, color=navy, transform=exact_ax.transAxes)
    exact_ax.text(0.5, 0.61,
        r'$D(X)=Xf\,\prime(X)-15f(X)=3X^{18}-3X^{12}+(vX-1)^5(15-9vX)$',
        ha='center', fontsize=17, color=blue, transform=exact_ax.transAxes)
    terms = exact['D_terms']
    for idx, term in enumerate(terms):
        x = idx / len(terms)
        w = 0.104
        exact_ax.add_patch(FancyBboxPatch((x, 0.12), w, 0.25,
            boxstyle='round,pad=0.002,rounding_size=0.014',
            facecolor='#e1efe9' if term['x_power'] == 0 else '#e4edf7',
            edgecolor='white', transform=exact_ax.transAxes))
        c, vp, xp = term['coefficient'], term['v_power'], term['x_power']
        coefficient = str(c) + (('v' if vp == 1 else 'v^{' + str(vp) + '}') if vp else '')
        exact_ax.text(x + w/2, 0.265, '$' + coefficient + '$', ha='center', va='center',
                      fontsize=12, color=navy, transform=exact_ax.transAxes)
        exact_ax.text(x + w/2, 0.17, '$X^{' + str(xp) + '}$', ha='center', va='center',
                      fontsize=10, color=gray, transform=exact_ax.transAxes)
    exact_ax.text(0, -0.02,
        'All nonzero coefficients of D, read from the exact sparse computation. No a term; D(0) = −15 ≠ 0 in characteristic zero.',
        fontsize=10, color=gray, transform=exact_ax.transAxes)

    tower = fig.add_subplot(grid[1, 0]); panel(tower, 'B  Specified generic fields and embeddings')
    box(tower, 0, 0.78, 0.96, 0.19, r'$V=\mathbb{Q}(v)$',
        'v is the first formal indeterminate.', '#edf3fb')
    arrow(tower, 0.49, 0.765, 0.72)
    box(tower, 0, 0.51, 0.96, 0.19, r'$k=V(t),\qquad K=k(a)$',
        't is transcendental over V; a is transcendental over k.', '#edf3fb')
    arrow(tower, 0.49, 0.495, 0.45)
    box(tower, 0, 0.24, 0.96, 0.19, r'$L=\mathrm{SplittingField}(f/K)$',
        'The entire polynomial splits in this field.', '#e5f2eb', green)
    tower.text(0.02, 0.115, 'Constants maps and the K → L field map are injective.\n'
               'Compatible scalar towers preserve the meaning of a,v,t.\n'
               'The concrete base is the iterated field Q(v)(t)(a).',
               transform=tower.transAxes, fontsize=10, color=gray, linespacing=1.45)

    proof = fig.add_subplot(grid[1, 1]); panel(proof, 'C  Why a repeated generic root is impossible')
    box(proof, 0, 0.78, 0.96, 0.19, r'Assume $f(r)=f\,\prime(r)=0$',
        'Then D(r)=0. Since D is nonzero over k, r is algebraic over k.')
    arrow(proof, 0.49, 0.765, 0.72)
    box(proof, 0, 0.51, 0.96, 0.19, r'$f(0)=1\quad\Longrightarrow\quad r\ne 0$',
        r'$r^{15}a=r^{18}+r^{12}+(vr-1)^6$' + '\nThe right-hand side is algebraic over k.')
    arrow(proof, 0.49, 0.495, 0.45)
    box(proof, 0, 0.24, 0.96, 0.19, 'Therefore a is algebraic over k: contradiction',
        'Lean uses the algebraicity-of-a-product lemma and r¹⁵ ≠ 0.', '#e5f2eb', green)
    proof.text(0.02, 0.115,
        'Injectivity transports the contradiction back to K.\n'
        'Thus f and its derivative are coprime: f is separable.\n'
        'No specialization transfer or expanded discriminant is used.',
        transform=proof.transAxes, fontsize=10, color=gray, linespacing=1.45)

    roots = fig.add_subplot(grid[2, 0]); panel(roots, 'D  All eighteen roots, then the existing split traces')
    roots.text(0.02, 0.91, 'Degree 18 + separability + splitting ⇒ 18-element root set',
               transform=roots.transAxes, color=green, weight='bold', fontsize=11)
    for i in range(18):
        x = 0.04 + i * 0.052
        roots.plot([x], [0.69], 'o', ms=6, color=green, transform=roots.transAxes)
        if i in (0, 5, 11, 17):
            roots.text(x, 0.57, str(i), ha='center', color=gray, fontsize=9,
                       transform=roots.transAxes)
    roots.text(0.02, 0.43, r'$\rho:\mathrm{Fin}(18)\to L$ injective; $f_L(\rho_j)=0$',
               transform=roots.transAxes, fontsize=13, color=navy)
    roots.text(0.02, 0.23, r'$f_L=\prod_{j=0}^{17}(X-\rho_j)$' + '\n'
               r'Existing split trace: last vector $1$; slot eleven $0$.',
               transform=roots.transAxes, fontsize=11, color=navy, linespacing=1.65)
    roots.text(0.02, 0.01, 'Dots denote tuple indices, not numerical root locations.',
               transform=roots.transAxes, fontsize=9.5, color=gray)

    scope = fig.add_subplot(grid[2, 1]); panel(scope, 'E  The preserved specialization control')
    box(scope, 0, 0.08, 0.96, 0.88, 'At a = 2, v = 1: generic hypotheses fail',
        r'$f(X)=X^{12}(X^3-1)^2+(X-1)^6$' + '\n\n'
        r'$f(1)=f\,\prime(1)=0,\qquad f\,\prime\prime(1)=18.$' + '\n\n'
        'Exactly double root at 1 over Q: reused historical receipt.\n'
        'No field embedding K → k can send the indeterminate a to 2.\n'
        'Generic distinctness does not apply to every specialization.', '#fff2d9', amber)

    fig.text(0.055, 0.044,
        'Evidence: new focused Lean PASS; separate exact integer controls; source pins; preserved double-root control. '
        'The figure records proof dependencies, not independent proof.', color=gray, fontsize=9)
    fig.text(0.055, 0.023,
        'Scope: split L-algebra only. No unsplit descent, source normalization, primitive, certificate or target solve. '
        'New remote CI awaits coordinator publication.', color=gray, fontsize=9)
    png, svg = out / 'generic-distinct-roots.png', out / 'generic-distinct-roots.svg'
    fig.savefig(png, dpi=160, facecolor=fig.get_facecolor(),
                metadata={'Software': 'Hodge Lab / Matplotlib'})
    fig.savefig(svg, facecolor=fig.get_facecolor(),
                metadata={'Date': None, 'Creator': 'Hodge Lab / Matplotlib'})
    plt.close(fig)
    return png, svg


def main():
    out = fresh_output_dir(ROOT / 'formal', 'skew-distinct-roots-figure', [
        ROOT / 'formal/results/skew-distinct-roots', BATCH / 'inputs',
        ROOT / 'results/ci-receipt-physical-cover-20261023'])
    before = {str(path.relative_to(ROOT)): sha(path) for path in INPUTS.values()}
    try:
        records = {key: json.loads(path.read_text(encoding='utf-8'))
                   for key, path in INPUTS.items()}
        outputs = render(records, out)
        require(before == {str(path.relative_to(ROOT)): sha(path) for path in INPUTS.values()},
                'An input changed during figure generation')
        receipt = {
            'status': 'GENERATED', 'generator': str(Path(__file__).resolve().relative_to(ROOT)),
            'generator_sha256': sha(Path(__file__)), 'matplotlib': matplotlib.__version__,
            'python': sys.version, 'input_sha256': before,
            'output_sha256': {path.name: sha(path) for path in outputs},
            'scope': 'Exact eliminant, compatible generic field tower, proof dependencies, all-root enumeration and specialization limit; not independent proof evidence.',
            'historical_control': 'The historical exact double-root receipt is read by hash; the new Lean module additionally proves this specialization is not separable.',
            'new_remote_ci': 'Not executed; coordinator owns publication.',
        }
    except Exception as exc:
        receipt = {'status': 'FAIL', 'error': repr(exc), 'input_sha256': before}
        (out / 'visualization.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
        raise
    (out / 'visualization.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
