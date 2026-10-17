#!/usr/bin/env python3
"""Render exact checked fresh-instance E1 maps; no ranks are inferred from pixels.

Run after fresh_instance_e1.py verify. Requires matplotlib and numpy. Source
packets and their Fraction-verifier receipts are bound by SHA-256 before plotting.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'results' / 'fresh-instance-e1'
OUT = ROOT / 'results' / 'fresh-instance-e1-figures'
INSTANCES = ('cycle-three', 'mixed-biweight')
TITLES = {'cycle-three': 'Cyclic coupling', 'mixed-biweight': 'Mixed biweights'}
TEAL, CORAL, GOLD = '#166A70', '#CA584C', '#D5AB3E'
INK, MUTED, PAPER = '#17323B', '#53666D', '#FAFAF5'


def sha(path):
    # Match mathematical packets across core.autocrlf checkouts.
    return hashlib.sha256(path.read_text(encoding='utf-8').encode('utf-8')).hexdigest()


def relative(path):
    return path.relative_to(ROOT).as_posix()


def load_checked():
    receipt_path = SOURCE / 'validation.json'
    receipts = {(r['instance'], r['degree']): r
                for r in json.loads(receipt_path.read_text(encoding='utf-8'))}
    result = {'schema': 'fresh-instance-e1-plot-v1',
              'sha256_policy': 'UTF-8 bytes with CRLF normalized to LF',
              'validation_sha256': sha(receipt_path), 'instances': {},
              'interpretation': 'Exact Fraction-checked E1 rank and kernel dimensions. '
              'An E1 survivor is not a certificate. Degree-four maps use only active '
              'rows, sorted by original coefficient-row index; all 126 columns remain.'}
    for instance in INSTANCES:
        packets, records = [], []
        for degree in range(6):
            path = SOURCE / instance / f'degree-{degree}.json'
            data = json.loads(path.read_text(encoding='utf-8'))
            receipt = receipts[(instance, degree)]
            assert receipt['status'] == 'PASS'
            assert receipt['packet_sha256'] == sha(path)
            assert data['dimensions'] == receipt['dimensions']
            assert data['instance'] == instance and data['degree'] == degree
            for name, digest in data['source_sha256'].items():
                assert sha(ROOT / name) == digest, name
            dims = data['dimensions']
            assert dims['denominator_image_rank'] + dims['denominator_kernel_dimension'] == dims['denominator_columns']
            assert data['jacobian_denominator_subspace_dimension'] == receipt['jacobian_denominator_subspace_dimension']
            packets.append(data)
            records.append({'degree': degree, 'path': relative(path),
                            'sha256': sha(path), **dims,
                            'jacobian_denominator_subspace_dimension': data['jacobian_denominator_subspace_dimension']})
        data = packets[4]
        entries = data['matrix_plot']['residual_entries']
        dims = data['dimensions']
        assert dims['denominator_columns'] == 126
        assert len(entries) == data['sparsity']['reduced_AD_nonzeros']
        positions = set()
        for row, col, coefficient in entries:
            assert 0 <= row < dims['coefficient_rows']
            assert 0 <= col < dims['denominator_columns']
            assert Fraction(coefficient) != 0
            assert (row, col) not in positions
            positions.add((row, col))
        active_rows = sorted({row for row, _, _ in entries})
        result['instances'][instance] = {
            'degrees': records,
            'degree_four': {'full_shape': [dims['coefficient_rows'], dims['denominator_columns']],
                            'active_row_indices': active_rows,
                            'residual_entries': entries,
                            'sign_encoding': 'teal positive; coral negative; dot size is constant; no amplitude encoding'}}
    e2_receipt_path = SOURCE / 'e2-validation.json'
    e2_receipts = {r['instance']: r for r in json.loads(e2_receipt_path.read_text(encoding='utf-8'))}
    result['e2_validation_sha256'] = sha(e2_receipt_path)
    for instance in INSTANCES:
        path = SOURCE / instance / 'degree-5-e2.json'
        packet = json.loads(path.read_text(encoding='utf-8'))
        receipt = e2_receipts[instance]
        assert receipt['status'] == 'PASS'
        assert receipt['packet_sha256'] == sha(path)
        assert packet['degree5_e1_sha256'] == result['instances'][instance]['degrees'][5]['sha256']
        assert packet['degree5_excluded'] is True
        assert packet['dimensions']['quotient_quadratic_rank'] == 21
        assert packet['dimensions']['quadratic_columns'] == 21
        assert len(packet['square_obstructions']) == 6
        for name, digest in packet['source_sha256'].items():
            assert sha(ROOT / name) == digest
        entries = packet['matrix_plot']['residual_entries']
        assert len({(r, c) for r, c, v in entries}) == len(entries)
        assert all(0 <= r < 3003 and 0 <= c < 21 and Fraction(v) != 0 for r, c, v in entries)
        result['instances'][instance]['degree_five_e2'] = {
            'path': relative(path), 'sha256': sha(path),
            'dimensions': packet['dimensions'],
            'quadratic_column_pairs': packet['quadratic_column_pairs'],
            'square_columns': [r['quadratic_column'] for r in packet['square_obstructions']],
            'active_row_indices': sorted({r for r, c, v in entries}),
            'residual_entries': entries,
            'degree5_excluded': True}
    return result


def style_axis(ax):
    ax.set_facecolor(PAPER)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('left', 'bottom'):
        ax.spines[side].set_color('#B8C2C0')
    ax.tick_params(colors=MUTED, labelsize=10)
    ax.xaxis.label.set_color(INK)
    ax.yaxis.label.set_color(INK)


def render(data):
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'text.color': INK, 'axes.labelcolor': INK,
                         'svg.fonttype': 'none'})
    fig, axes = plt.subplots(2, 2, figsize=(16, 10.8),
                             gridspec_kw={'height_ratios': [1, 1.2]})
    fig.patch.set_facecolor(PAPER)
    fig.subplots_adjust(left=.075, right=.965, bottom=.145, top=.83,
                        wspace=.26, hspace=.54)
    fig.text(.075, .955, 'Two fresh instances: the first exact denominator filter',
             fontsize=23, weight='bold')
    fig.text(.075, .918, r'$D \mapsto [AD]$ in the Jacobian quotient $S/J(F)$',
             fontsize=16, color=TEAL)
    fig.text(.075, .884, 'Fixed targets, q = 1  |  Entire homogeneous denominator spaces  |  Rational arithmetic',
             fontsize=11, color=MUTED)
    for col, instance in enumerate(INSTANCES):
        info = data['instances'][instance]
        degrees = info['degrees']
        ax = axes[0, col]
        style_axis(ax)
        x = np.arange(6)
        eliminated = np.array([r['denominator_image_rank'] for r in degrees])
        retained = np.array([r['denominator_kernel_dimension'] for r in degrees])
        total = eliminated + retained
        ax.bar(x, eliminated, color=TEAL, width=.65)
        ax.bar(x, retained, bottom=eliminated, color=GOLD, width=.65)
        for i, n in enumerate(total):
            ax.text(i, n + 7, str(n), ha='center', fontsize=11, weight='bold')
        ax.annotate('6 retained\n= the Jacobian degree-five subspace',
                    xy=(5, 249), xytext=(2.25, 206), fontsize=10,
                    color=INK, arrowprops={'arrowstyle': '-', 'color': MUTED},
                    ha='center', va='center')
        ax.set_title(TITLES[instance] + '  |  ' + instance,
                     loc='left', fontsize=14, weight='bold', pad=14)
        ax.set_xticks(x)
        ax.set_xlabel('Denominator degree d')
        ax.set_ylabel('Independent denominator directions')
        ax.set_ylim(0, 285)
        ax.set_xlim(-.55, 5.55)
        ax.yaxis.grid(True, color='#DDE3DF', linewidth=.6)
        ax.set_axisbelow(True)
        ax.legend(handles=[Patch(color=TEAL, label='Eliminated by E1'),
                           Patch(color=GOLD, label='Retained by E1')],
                  loc='upper left', frameon=False, fontsize=10)

        ax = axes[1, col]
        style_axis(ax)
        matrix = info['degree_four']
        rows = matrix['active_row_indices']
        lookup = {r: i for i, r in enumerate(rows)}
        entries = matrix['residual_entries']
        for positive, color in ((True, TEAL), (False, CORAL)):
            points = [(c, lookup[r]) for r, c, v in entries
                      if (Fraction(v) > 0) == positive]
            if points:
                xx, yy = zip(*points)
                ax.scatter(xx, yy, s=12, color=color, linewidths=0, marker='s',
                           label='Positive' if positive else 'Negative')
        ax.set_xlim(-1, 126)
        ax.set_ylim(len(rows), -1)
        ax.set_xlabel('Denominator monomial column (0–125; all 126 shown)')
        ax.set_ylabel('Active coefficient rows only\n(sorted by original row index)')
        ax.set_title(f'Degree 4: {len(entries)} nonzeros in {len(rows)} active rows',
                     loc='left', fontsize=13, weight='bold', pad=15)
        ax.text(.0, 1.015, f'Full map: 3,003 × 126  |  rank 126  |  kernel 0',
                transform=ax.transAxes, fontsize=10, color=MUTED)
    fig.legend(handles=[Patch(color=TEAL, label='Positive map coefficient'),
                        Patch(color=CORAL, label='Negative map coefficient')],
               loc='center', bbox_to_anchor=(.52, .497), ncol=2,
               frameon=False, fontsize=10)
    fig.text(.075, .08, 'Degrees 0–4: every denominator direction is excluded. Degree 5: six E1 directions remain.',
             fontsize=12, weight='bold')
    fig.text(.075, .052, 'E1 survivors ≠ certificates. The companion E2 figure applies a further necessary condition and excludes these six directions.',
             fontsize=11, color=MUTED)
    fig.text(.075, .025, 'Exact ranks come from Fraction-checked packets, not pixel estimates. Map dots encode coefficient sign only; zero rows are omitted.',
             fontsize=10, color=MUTED)
    fig.savefig(OUT / 'fresh-instance-e1.png', dpi=100, facecolor=PAPER)
    fig.savefig(OUT / 'fresh-instance-e1.svg', facecolor=PAPER)
    plt.close(fig)


def render_e2(data):
    fig, axes = plt.subplots(1, 2, figsize=(16, 9.5))
    fig.patch.set_facecolor(PAPER)
    fig.subplots_adjust(left=.075, right=.965, bottom=.245, top=.65, wspace=.26)
    fig.text(.075, .947, 'The degree-five survivors fail the next exact filter',
             fontsize=23, weight='bold')
    fig.text(.075, .903, r'$D=\sum_i a_i F_i$: quadratic coefficients in the necessary E2 quotient',
             fontsize=16, color=TEAL)
    boxes = [(.075, '6 E1 directions', 'the span of the six partial derivatives'),
             (.38, '21 independent quadratics', 'exact quotient-map rank = 21 of 21'),
             (.705, 'All six squares vanish', r'$a_i^2=0\ (i=0,\ldots,5)$, hence $D=0$')]
    for x, title, detail in boxes:
        fig.text(x, .824, title, fontsize=15, weight='bold',
                 bbox={'boxstyle': 'round,pad=.45', 'facecolor': '#E4EDEA', 'edgecolor': 'none'})
        fig.text(x, .782, detail, fontsize=10, color=MUTED)
    fig.text(.337, .824, '→', fontsize=23, color=TEAL)
    fig.text(.662, .824, '→', fontsize=23, color=TEAL)
    for col, instance in enumerate(INSTANCES):
        matrix = data['instances'][instance]['degree_five_e2']
        ax = axes[col]
        style_axis(ax)
        rows = matrix['active_row_indices']
        lookup = {r: i for i, r in enumerate(rows)}
        entries = matrix['residual_entries']
        for c in matrix['square_columns']:
            ax.axvspan(c - .45, c + .45, color=GOLD, alpha=.20, linewidth=0, zorder=0)
        for positive, color in ((True, TEAL), (False, CORAL)):
            points = [(c, lookup[r]) for r, c, v in entries if (Fraction(v) > 0) == positive]
            if points:
                xx, yy = zip(*points)
                ax.scatter(xx, yy, s=36, color=color, linewidths=0, marker='s', zorder=2)
        ax.set_xlim(-.65, 20.65)
        ax.set_ylim(len(rows) - .4, -.6)
        ax.set_title(f'{TITLES[instance]}: {len(entries)} nonzeros, {len(rows)} active rows',
                     loc='left', fontsize=13, weight='bold', pad=35)
        ax.text(0, 1.025, 'Full map: 3,003 × 21  |  rank 21  |  kernel 0',
                transform=ax.transAxes, fontsize=11, color=MUTED)
        ax.set_ylabel('Active coefficient rows only\n(sorted by original row index)')
        ax.set_xticks(range(21))
        labels = []
        for first, second in matrix['quadratic_column_pairs']:
            label = fr'$a_{{{first}}}^2$' if first == second else fr'$a_{{{first}}}a_{{{second}}}$'
            labels.append(label)
        ax.set_xticklabels(labels, rotation=90, fontsize=9)
        ax.set_xlabel('Quadratic parameter monomials (all 21 columns)', labelpad=9)
    fig.legend(handles=[Patch(color=TEAL, label='Positive coefficient'),
                        Patch(color=CORAL, label='Negative coefficient'),
                        Patch(color=GOLD, alpha=.3, label='Square parameter column')],
               loc='lower left', bbox_to_anchor=(.069, .116), ncol=3, frameon=False, fontsize=11)
    fig.text(.075, .092, 'Both targets: exact degree-five exclusion. Together with E1, this excludes every denominator degree 0–5.',
             fontsize=12, weight='bold')
    fig.text(.075, .057, 'Each of the six square obstructions has an exact dual functional. Complete degree-six Koszul correction space: dimension 90.',
             fontsize=11, color=MUTED)
    fig.text(.075, .026, 'Necessary quotient only: higher-degree denominators remain open. This is not a certificate, Lean proof, or complete solve.',
             fontsize=11, color=MUTED)
    fig.savefig(OUT / 'fresh-instance-e2.png', dpi=100, facecolor=PAPER)
    fig.savefig(OUT / 'fresh-instance-e2.svg', facecolor=PAPER)
    plt.close(fig)


def main():
    if not __debug__:
        raise RuntimeError('Run without -O: input bindings use assertions')
    data = load_checked()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'plot-data.json').write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8', newline='\n')
    render(data)
    render_e2(data)
    for name in ('fresh-instance-e1.svg', 'fresh-instance-e2.svg'):
        path = OUT / name
        path.write_text('\n'.join(line.rstrip() for line in path.read_text(encoding='utf-8').splitlines()) + '\n',
                        encoding='utf-8', newline='\n')
    print(json.dumps({'status': 'PASS', 'packet_bindings_checked': 14,
                      'source_bindings_checked': 42,
                      'output': relative(OUT),
                      'readout': {name: {'degree_four_nonzeros': len(info['degree_four']['residual_entries']),
                                         'degree_four_active_rows': len(info['degree_four']['active_row_indices']),
                                         'degree_five_kernel_dimension': info['degrees'][5]['denominator_kernel_dimension']}
                                  for name, info in data['instances'].items()}}, indent=2))


if __name__ == '__main__':
    main()
