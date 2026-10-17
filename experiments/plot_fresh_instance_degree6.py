#!/usr/bin/env python3
"""Plot checked degree-six maps and parameter restrictions, not sampled geometry.

Run fresh_instance_degree6.py verifiers first.  Every depicted coefficient is
bound to a checked rational packet; plotting never estimates a matrix rank.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'results' / 'fresh-instance-degree6'
OUT = ROOT / 'results' / 'fresh-instance-degree6-figures'
INSTANCES = ('cycle-three', 'mixed-biweight')
TEAL, CORAL, GOLD, PURPLE = '#166A70', '#CA584C', '#D5AB3E', '#7967AA'
INK, MUTED, PAPER, GRAY = '#17323B', '#53666D', '#FAFAF5', '#CBD3D0'
NAMES = ('X0', 'X1', 'X2', 'Y0', 'Y1', 'Y2')


def sha(path):
    return hashlib.sha256(path.read_text(encoding='utf-8').encode('utf-8')).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def relative(path):
    return path.relative_to(ROOT).as_posix()


def checked_map(entries, rows, cols):
    assert len({(r, c) for r, c, value in entries}) == len(entries)
    assert all(0 <= r < rows and 0 <= c < cols and Fraction(value) != 0
               for r, c, value in entries)
    return {'full_shape': [rows, cols],
            'active_row_indices': sorted({r for r, c, value in entries}),
            'residual_entries': entries,
            'encoding': 'Constant-size signs: teal positive, coral negative. '
                        'Zero rows omitted; original row order preserved. All listed columns retained.'}


def monomials(degree, variables):
    if variables == 1:
        return [(degree,)]
    return [(first,) + rest for first in range(degree + 1)
            for rest in monomials(degree-first, variables-1)]


def add_term(poly, monomial, coefficient):
    poly[monomial] = poly.get(monomial, Fraction(0)) + coefficient
    if not poly[monomial]:
        del poly[monomial]


def load_checked():
    receipts = {r['instance']: r for r in load(SOURCE / 'validation.json')}
    result = {'schema': 'fresh-instance-degree6-plot-v1',
              'sha256_policy': 'UTF-8 bytes with CRLF normalized to LF',
              'validation_sha256': sha(SOURCE / 'validation.json'),
              'instances': {},
              'scope': 'Intermediate exact necessary conditions. A retained parameter '
                       'is not a certificate. Ranks are supplied by checked exact packets; '
                       'no phase transition or topological geometry is inferred.'}
    for instance in INSTANCES:
        path = SOURCE / instance / 'degree-6.json'
        packet, receipt = load(path), receipts[instance]
        assert receipt['status'] == 'PASS' and receipt['packet_sha256'] == sha(path)
        assert packet['instance'] == instance and packet['degree'] == 6
        assert receipt['dimensions'] == packet['dimensions']
        for name, digest in packet['source_sha256'].items():
            assert sha(ROOT / name) == digest
        for name, digest in packet['experiment_source_sha256'].items():
            assert sha(ROOT / name) == digest
        dims = packet['dimensions']
        assert dims['denominator_columns'] == 462
        assert dims['denominator_image_rank'] + dims['denominator_kernel_dimension'] == 462
        assert receipt['F_gauge_dimension'] == 1
        assert receipt['jacobian_denominator_subspace_dimension'] == 36
        assert receipt['denominator_kernel_mod_F_dimension'] == dims['denominator_kernel_dimension'] - 1
        assert receipt['non_J6_denominator_dimension'] == dims['denominator_kernel_dimension'] - 36
        result['instances'][instance] = {'path': relative(path), 'sha256': sha(path),
            'dimensions': dims, 'J6_dimension': 36, 'F_gauge_dimension': 1,
            'kernel_mod_F_dimension': receipt['denominator_kernel_mod_F_dimension'],
            'non_J6_dimension': receipt['non_J6_denominator_dimension']}
    path = SOURCE / 'cycle-three' / 'degree-6-e2.json'
    receipt_path = SOURCE / 'cycle-three' / 'e2-validation.json'
    packet, receipt = load(path), load(receipt_path)
    assert receipt['status'] == 'PASS' and receipt['packet_sha256'] == sha(path)
    assert packet['degree6_E1_sha256'] == result['instances']['cycle-three']['sha256']
    assert packet['schema'] == 'fresh-instance-degree6-hessian-v1'
    for name, digest in packet['source_sha256'].items():
        assert sha(ROOT / name) == digest
    dims, pairs, steps = packet['dimensions'], packet['quadratic_column_pairs'], packet['steps']
    assert dims['parameters_after_F_gauge'] == 35 and dims['quadratic_columns'] == len(pairs) == 630
    assert dims['Koszul_rank'] == dims['Koszul_fields'] == dims['numerator_kernel_dimension'] == 315
    assert len(steps) == 2 and steps[0]['quotient_rank'] == 291 and steps[1]['quotient_rank'] == 3
    forced = [w['parameter'] for w in steps[0]['forced_squares']]
    retained = packet['remaining_parameters']
    assert len(forced) == receipt['square_obstructions'] == 30
    assert retained == receipt['remaining_parameters'] == [0, 7, 14, 21, 28]
    assert all(packet['parameters'][a][0] != packet['parameters'][a][1] for a in forced)
    assert all(packet['parameters'][a][0] == packet['parameters'][a][1] for a in retained)
    entries = packet['matrix_plot']['residual_entries']
    matrix = checked_map(entries, dims['coefficient_rows'], len(pairs))
    active_cols = steps[1]['active_columns']
    assert len(active_cols) == 15
    col_lookup = {c: j for j, c in enumerate(active_cols)}
    restricted = [[r, col_lookup[c], v] for r, c, v in entries if c in col_lookup]
    restricted_map = checked_map(restricted, dims['coefficient_rows'], len(active_cols))
    assert len(restricted_map['active_row_indices']) == 3
    result['cycle_three_hessian'] = {'path': relative(path), 'sha256': sha(path),
        'validation_sha256': sha(receipt_path), 'dimensions': dims,
        'parameters': packet['parameters'], 'quadratic_column_pairs': pairs,
        'rank': steps[0]['quotient_rank'], 'forced_parameters': forced,
        'retained_parameters': retained, 'matrix': matrix,
        'restricted_columns': active_cols, 'restricted_rank': steps[1]['quotient_rank'],
        'restricted_matrix': restricted_map}
    path = SOURCE / 'cycle-three' / 'degree-6-diagonal.json'
    receipt_path = SOURCE / 'cycle-three' / 'diagonal-validation.json'
    packet, receipt = load(path), load(receipt_path)
    assert receipt['status'] == 'PASS' and receipt['packet_sha256'] == sha(path)
    assert receipt['degree6_excluded'] and packet['degree6_excluded']
    assert packet['hessian_packet_sha256'] == result['cycle_three_hessian']['sha256']
    assert packet['schema'] == 'fresh-instance-degree6-diagonal-v1'
    for name, digest in packet['source_sha256'].items():
        assert sha(ROOT / name) == digest
    dims, search = packet['dimensions'], packet['quartic_search']
    assert dims['correction_columns'] == 2352 and dims['correction_rank'] == 1451
    assert dims['necessary_quadratic_rank'] == 7
    assert search['degree'] == 4 and search['row_rank'] == search['coefficient_columns'] == 70
    assert search['multiplier_rows'] == 105 and search['unresolved_parameters'] == []
    pairs, equations = packet['gauged_column_pairs'], packet['gauged_equations']
    assert len(pairs) == 15 and len(equations) == 7
    equation_map = checked_map([[i, c, v] for i, eq in enumerate(equations) for c, v in eq], 7, 15)
    equation_polys = []
    for equation in equations:
        poly = {}
        for column, value in equation:
            i, j = pairs[column]
            exponent = [0]*5; exponent[i] += 1; exponent[j] += 1
            add_term(poly, tuple(exponent), Fraction(value))
        equation_polys.append(poly)
    quartics, multipliers = monomials(4, 5), monomials(2, 5)
    lookup = {mon: i for i, mon in enumerate(quartics)}
    entries, labels = [], []
    for i, equation in enumerate(equation_polys):
        for multiplier in multipliers:
            column = len(labels)
            labels.append([i, list(multiplier)])
            for mon, coefficient in equation.items():
                target = tuple(a+b for a, b in zip(mon, multiplier))
                entries.append([lookup[target], column, str(coefficient)])
    assert len(labels) == 105 and len(quartics) == 70
    quartic_map = checked_map(entries, 70, 105)
    identities = search['identities']
    assert sorted(w['parameter'] for w in identities) == list(range(5))
    for identity in identities:
        assert identity['power'] == 4
        answer = {}
        for equation, multiplier, value in identity['multipliers']:
            assert 0 <= equation < 7 and len(multiplier) == 5 and sum(multiplier) == 2
            for mon, coefficient in equation_polys[equation].items():
                shifted = tuple(a+b for a, b in zip(mon, multiplier))
                add_term(answer, shifted, Fraction(value)*coefficient)
        target = tuple(4 if i == identity['parameter'] else 0 for i in range(5))
        assert answer == {target: Fraction(1)}, identity['parameter']
    result['cycle_three_diagonal'] = {'path': relative(path), 'sha256': sha(path),
        'validation_sha256': sha(receipt_path), 'dimensions': dims,
        'equation_matrix': equation_map, 'quadratic_column_pairs': pairs,
        'quartic_matrix': quartic_map, 'quartic_row_monomials': quartics,
        'multiplier_columns': labels, 'quartic_rank': search['row_rank'],
        'fourth_power_identities_checked_again': 5,
        'identity_multiplier_counts': [len(w['multipliers']) for w in identities],
        'degree6_excluded': True}
    return result


def style(ax):
    ax.set_facecolor(PAPER)
    for name in ('top', 'right'):
        ax.spines[name].set_visible(False)
    for name in ('left', 'bottom'):
        ax.spines[name].set_color('#B8C2C0')
    ax.tick_params(colors=MUTED, labelsize=10)


def sparse_plot(ax, matrix, size):
    rows = matrix['active_row_indices']
    lookup = {row: i for i, row in enumerate(rows)}
    for positive, color in ((True, TEAL), (False, CORAL)):
        points = [(c, lookup[r]) for r, c, v in matrix['residual_entries']
                  if (Fraction(v) > 0) == positive]
        if points:
            x, y = zip(*points)
            ax.scatter(x, y, color=color, s=size, marker='s', linewidths=0)
    ax.set_xlim(-.7, matrix['full_shape'][1]-.3)
    ax.set_ylim(len(rows)-.3, -.7)
    return rows


def render(data):
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'text.color': INK, 'axes.labelcolor': INK, 'svg.fonttype': 'none',
                         'svg.hashsalt': 'fresh-instance-degree6-v1'})
    fig = plt.figure(figsize=(16, 12), facecolor=PAPER)
    grid = fig.add_gridspec(2, 2, left=.105, right=.96, top=.82, bottom=.17,
                           hspace=.69, wspace=.32, height_ratios=[1, 1.05])
    fig.text(.075, .955, 'Degree six: the surviving directions acquire structure', fontsize=23, weight='bold')
    fig.text(.075, .919, r'$D\mapsto[AD]$ first; then $[A\,L^T\mathrm{Hess}(F)L]$ for $L=MZ$',
             fontsize=17, color=TEAL)
    fig.text(.075, .885, 'Exact rational maps  |  Fixed targets, q = 1  |  Necessary conditions, not an existence certificate',
             fontsize=11, color=MUTED)

    ax = fig.add_subplot(grid[0, 0]); style(ax)
    ax.set_title('1  Complete degree-six E1 kernels', loc='left', fontsize=14, weight='bold', pad=22)
    names = ('cycle-three', 'mixed-biweight')
    x = np.array([0, 1])
    eliminated = np.array([data['instances'][n]['dimensions']['denominator_image_rank'] for n in names])
    ax.barh(x, eliminated, color=TEAL, height=.38)
    ax.barh(x, [36, 36], left=eliminated, color=GOLD, height=.38)
    ax.barh(x, [0, 3], left=eliminated+36, color=PURPLE, height=.38)
    for i, name in enumerate(names):
        info = data['instances'][name]
        ax.text(5, i, f"{info['dimensions']['denominator_image_rank']} eliminated", va='center', color='white', fontsize=11)
        ax.text(465, i, str(info['dimensions']['denominator_kernel_dimension']), va='center', weight='bold')
        ax.text(0, i+.27, f"Retained: J(F)₆ = 36" + ('; plus 3 extra directions' if i else '; no extra directions'),
                fontsize=10, color=MUTED, va='center')
    ax.set_yticks(x, names); ax.invert_yaxis()
    ax.set_xlim(0, 492); ax.set_ylim(1.55, -.45)
    ax.set_xticks([0, 100, 200, 300, 400, 462])
    ax.set_xlabel('All 462 homogeneous denominator coefficients')
    ax.text(0, -.31, 'Each kernel contains the one-dimensional F gauge.', transform=ax.transAxes, fontsize=10, color=MUTED)
    ax.legend(handles=[Patch(color=TEAL, label='Eliminated'), Patch(color=GOLD, label='J(F)₆'),
                       Patch(color=PURPLE, label='Outside J(F)₆')], loc='upper left',
              bbox_to_anchor=(-.02, -.36), ncol=3, frameon=False, fontsize=10)

    hessian = data['cycle_three_hessian']
    ax = fig.add_subplot(grid[0, 1]); style(ax)
    ax.set_title('2  Cyclic coupling: the matrix M becomes diagonal', loc='left', fontsize=14, weight='bold', pad=22)
    grid_values = np.zeros((6, 6), dtype=int)
    grid_values[:] = 0
    for a in hessian['retained_parameters']:
        first, second = hessian['parameters'][a]
        grid_values[NAMES.index(first), NAMES.index(second)] = 1
    grid_values[5, 5] = 2
    colors = [TEAL, GOLD, GRAY]
    for i in range(6):
        for j in range(6):
            value = grid_values[i, j]
            ax.add_patch(Rectangle((j-.5, i-.5), 1, 1, color=colors[value], ec=PAPER, linewidth=2))
            label = '0' if value == 0 else (f'b{i}' if value == 1 else 'gauge')
            ax.text(j, i, label, ha='center', va='center', color='white' if value == 0 else INK,
                    fontsize=11 if value != 2 else 9, weight='bold')
    ax.set(xlim=(-.5, 5.5), ylim=(5.5, -.5), aspect='equal')
    ax.set_anchor('W')
    ax.set_xticks(range(6), NAMES); ax.set_yticks(range(6), NAMES)
    ax.set_xlabel('Coordinate multiplying each matrix entry'); ax.set_ylabel('Component of L = MZ')
    ax.text(1.04, .91, '30 off-diagonal\nentries vanish', transform=ax.transAxes, fontsize=11, weight='bold')
    ax.text(1.04, .66, 'Exact duals isolate\neach entry squared.', transform=ax.transAxes, fontsize=10, color=MUTED)
    ax.text(1.04, .35, '5 diagonal\nparameters remain\nat this stage.', transform=ax.transAxes, fontsize=11, color=INK)
    ax.text(1.04, .05, 'M₅₅ = 0 uses\nthe F gauge.', transform=ax.transAxes, fontsize=10, color=MUTED)

    ax = fig.add_subplot(grid[1, 0]); style(ax)
    matrix = hessian['matrix']
    sparse_plot(ax, matrix, 7)
    ax.set_title('3  Actual Hessian quotient coefficients', loc='left', fontsize=14, weight='bold', pad=29)
    ax.text(0, 1.035, f"6,188 × 630 full map  |  rank {hessian['rank']}  |  {len(matrix['residual_entries']):,} nonzeros",
            transform=ax.transAxes, color=MUTED, fontsize=10)
    ax.set_xlabel('Quadratic monomial column in 35 parameters (all 630)')
    ax.set_ylabel(f"{len(matrix['active_row_indices'])} active coefficient rows\n(zero rows omitted, original order preserved)")

    ax = fig.add_subplot(grid[1, 1]); style(ax)
    matrix = hessian['restricted_matrix']
    sparse_plot(ax, matrix, 100)
    ax.set_title('4  Restriction to the five diagonal parameters', loc='left', fontsize=14, weight='bold', pad=29)
    ax.text(0, 1.035, '3 active rows × 15 quadratic monomials  |  exact rank 3',
            transform=ax.transAxes, color=MUTED, fontsize=10)
    labels = []
    for c in hessian['restricted_columns']:
        a, b = hessian['quadratic_column_pairs'][c]
        i = hessian['retained_parameters'].index(a)
        j = hessian['retained_parameters'].index(b)
        labels.append(fr'$b_{i}^2$' if i == j else fr'$b_{i}b_{j}$')
    ax.set_xticks(range(15), labels, rotation=90, fontsize=10)
    ax.set_yticks(range(3), [str(r) for r in matrix['active_row_indices']])
    ax.set_xlabel('All 15 remaining quadratic monomials')
    ax.set_ylabel('Original coefficient-row index')

    fig.legend(handles=[Patch(color=TEAL, label='Positive map coefficient'),
                        Patch(color=CORAL, label='Negative map coefficient')],
               loc='lower left', bbox_to_anchor=(.07, .092), ncol=2, frameon=False, fontsize=10)
    fig.text(.075, .070, 'All 315 Koszul correction directions are included; the Hessian quotient removes their contribution.',
             fontsize=12, color=TEAL)
    fig.text(.075, .041, 'Panels 2–4 concern cycle-three only. Mixed biweights has three additional E1 directions; its full degree-six search remains open.',
             fontsize=10, color=MUTED)
    fig.text(.075, .018, 'The sparse patterns encode a chosen algebraic basis. They do not identify a surface, phase transition, or a solution of the target equations.',
             fontsize=10, color=MUTED)
    fig.savefig(OUT / 'degree-six-maps.png', dpi=100, facecolor=PAPER)
    fig.savefig(OUT / 'degree-six-maps.svg', facecolor=PAPER, metadata={'Date': None})
    plt.close(fig)


def render_diagonal(data):
    info = data['cycle_three_diagonal']
    fig, axes = plt.subplots(1, 2, figsize=(16, 10), facecolor=PAPER)
    fig.subplots_adjust(left=.075, right=.96, top=.67, bottom=.28, wspace=.33)
    fig.text(.075, .95, 'The five diagonal directions are also excluded', fontsize=23, weight='bold')
    fig.text(.075, .907, 'cycle-three  |  Full E2 correction span, followed by degree-four polynomial multipliers',
             fontsize=15, color=TEAL)
    milestones = [(.075, '35 parameters', 'after removing the F gauge'),
                  (.385, '5 diagonal parameters', '30 exact square obstructions'),
                  (.735, '0 admissible directions', 'five exact fourth-power identities')]
    for x, title, detail in milestones:
        fig.text(x, .829, title, fontsize=15, weight='bold',
                 bbox={'boxstyle': 'round,pad=.45', 'facecolor': '#E4EDEA', 'edgecolor': 'none'})
        fig.text(x, .787, detail, fontsize=10, color=MUTED)
    fig.text(.335, .83, '→', color=TEAL, fontsize=25)
    fig.text(.685, .83, '→', color=TEAL, fontsize=25)

    ax = axes[0]; style(ax)
    sparse_plot(ax, info['equation_matrix'], 80)
    ax.set_title('Seven exact quadratic consequences', loc='left', fontsize=14, weight='bold', pad=23)
    ax.text(0, 1.02, 'Quotient out all 2,352 relaxed correction columns (rank 1,451)',
            transform=ax.transAxes, color=MUTED, fontsize=10)
    ax.set_yticks(range(7), [f'P{i}' for i in range(7)])
    labels = [fr'$b_{i}^2$' if i == j else fr'$b_{i}b_{j}$' for i, j in info['quadratic_column_pairs']]
    ax.set_xticks(range(15), labels, rotation=90, fontsize=10)
    ax.set_xlabel('Quadratic monomials after the gauge b₅ = 0')
    ax.set_ylabel('Checked equations Pᵢ(b) = 0')

    ax = axes[1]; style(ax)
    sparse_plot(ax, info['quartic_matrix'], 10)
    for i in range(1, 7):
        ax.axvline(15*i-.5, color=GRAY, linewidth=.6)
    pure_rows = [i for i, mon in enumerate(info['quartic_row_monomials']) if 4 in mon]
    for r in pure_rows:
        ax.axhspan(r-.45, r+.45, color=GOLD, alpha=.20, linewidth=0, zorder=0)
    ax.set_title('Every quartic monomial lies in their ideal', loc='left', fontsize=14, weight='bold', pad=23)
    ax.text(0, 1.02, '70 × 105 multiplication map  |  exact rank 70',
            transform=ax.transAxes, color=MUTED, fontsize=10)
    ax.set_xticks([7+15*i for i in range(7)], [f'P{i}' for i in range(7)])
    ax.set_xlabel('Each block: 15 degree-two monomial multiples of Pᵢ')
    ax.set_ylabel('All 70 degree-four monomials (original lexicographic order)')

    fig.text(.075, .157, r'$b_i^4=\sum_{r=0}^{6} C_{ir}(b)P_r(b)$ for $i=0,\ldots,4$; '
             r'$\deg C_{ir}=2$. Hence all $b_i=0$ over $\mathbb{C}$.', fontsize=15, weight='bold')
    fig.legend(handles=[Patch(color=TEAL, label='Positive coefficient'),
                        Patch(color=CORAL, label='Negative coefficient'),
                        Patch(color=GOLD, alpha=.3, label='Pure fourth-power row')],
               loc='lower left', bbox_to_anchor=(.07, .095), ncol=3, frameon=False, fontsize=10)
    fig.text(.075, .077, 'Cycle-three: no degree-six denominator survives; the remaining multiples of F are inadmissible.',
             fontsize=12, color=TEAL)
    fig.text(.075, .046, 'All 315 Koszul directions and an unrestricted quotient are included before relaxation; the seven consequences remain necessary.',
             fontsize=10, color=MUTED)
    fig.text(.075, .02, 'Higher degrees remain open. This is an exact obstruction, not a certificate of existence, Lean proof, or accepted solution.',
             fontsize=10, color=MUTED)
    fig.savefig(OUT / 'degree-six-exclusion.png', dpi=100, facecolor=PAPER)
    fig.savefig(OUT / 'degree-six-exclusion.svg', facecolor=PAPER, metadata={'Date': None})
    plt.close(fig)


def main():
    if not __debug__:
        raise RuntimeError('Run without -O: packet bindings use assertions')
    data = load_checked()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'plot-data.json').write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8', newline='\n')
    render(data)
    render_diagonal(data)
    for name in ('degree-six-maps.svg', 'degree-six-exclusion.svg'):
        path = OUT / name
        path.write_text('\n'.join(line.rstrip() for line in path.read_text(encoding='utf-8').splitlines())+'\n',
                        encoding='utf-8', newline='\n')
    print(json.dumps({'status': 'PASS', 'packet_bindings_checked': 4,
                      'output': relative(OUT),
                      'map_nonzeros': len(data['cycle_three_hessian']['matrix']['residual_entries']),
                      'map_active_rows': len(data['cycle_three_hessian']['matrix']['active_row_indices'])}, indent=2))


if __name__ == '__main__':
    main()
