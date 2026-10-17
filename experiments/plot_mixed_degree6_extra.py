#!/usr/bin/env python3
"""Visualize checked mixed-biweight degree-six extra directions and E2 maps."""
from __future__ import annotations

from fractions import Fraction
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np

from plot_fresh_instance_degree6 import (ROOT, TEAL, CORAL, GOLD, PURPLE, INK,
    MUTED, PAPER, GRAY, NAMES, sha, load, relative, monomials, checked_map,
    style, sparse_plot, add_term)

SOURCE = ROOT / 'results' / 'mixed-degree6-extra'
OUT = ROOT / 'results' / 'mixed-degree6-extra-figures'
E1_SOURCE = ROOT / 'results' / 'fresh-instance-degree6'


def load_checked():
    path = E1_SOURCE / 'mixed-biweight' / 'degree-6.json'
    packet = load(path)
    receipt_path = E1_SOURCE / 'validation.json'
    receipt = next(r for r in load(receipt_path) if r['instance'] == 'mixed-biweight')
    assert receipt['status'] == 'PASS' and receipt['packet_sha256'] == sha(path)
    assert packet['instance'] == 'mixed-biweight' and packet['degree'] == 6
    assert receipt['dimensions'] == packet['dimensions']
    assert packet['dimensions']['denominator_kernel_dimension'] == 39
    assert receipt['jacobian_denominator_subspace_dimension'] == 36
    assert receipt['non_J6_denominator_dimension'] == 3
    for name, digest in packet['source_sha256'].items():
        assert sha(ROOT / name) == digest
    for name, digest in packet['experiment_source_sha256'].items():
        assert sha(ROOT / name) == digest
    indices = packet['non_J6_representative_kernel_indices']
    assert indices == [17, 29, 30]
    mons = monomials(6, 6)
    representatives = []
    for index in indices:
        terms = [[list(mons[c]), value] for c, value in packet['kernel_lifts'][index]['denominator']]
        assert len(terms) == 4 and all(sum(mon) == 6 and Fraction(value) != 0 for mon, value in terms)
        representatives.append({'kernel_index': index, 'terms': terms})
    result = {'schema': 'mixed-degree6-extra-plot-v1',
            'sha256_policy': 'UTF-8 bytes with CRLF normalized to LF',
            'E1_packet_path': relative(path), 'E1_packet_sha256': sha(path),
            'E1_validation_sha256': sha(receipt_path),
            'plot_helper_sha256': sha(ROOT / 'experiments' / 'plot_fresh_instance_degree6.py'),
            'representatives': representatives,
            'E1_dimensions': packet['dimensions'],
            'scope': 'Exact polynomial supports in the fixed coordinate basis. '
                     'An E1 direction need not extend to a certificate; no surface '
                     'or phase-transition interpretation is inferred.'}
    quotient_path = SOURCE / 'quotient.json'
    validation_path = SOURCE / 'quotient-validation.json'
    quotient, validation = load(quotient_path), load(validation_path)
    assert quotient['schema'] == 'mixed-degree6-extra-quotient-v1'
    assert validation['status'] == 'PASS' and validation['packet_sha256'] == sha(quotient_path)
    assert quotient['degree6_E1_sha256'] == result['E1_packet_sha256']
    assert quotient['source_sha256'] == packet['source_sha256']
    dims, pairs, steps = quotient['dimensions'], quotient['quadratic_column_pairs'], quotient['steps']
    assert dims['parameters_after_F_gauge'] == 38 and dims['quadratic_columns'] == len(pairs) == 741
    assert dims['numerator_kernel_dimension'] == validation['Koszul_fields_checked'] == 315
    assert validation['square_obstructions'] == 33
    assert quotient['remaining_parameters'] == validation['remaining_parameters'] == [0, 7, 14, 21, 28]
    assert [s['quotient_rank'] for s in steps] == [321, 25, 3]
    entries = quotient['matrix_plot']['residual_entries']
    checked_map(entries, dims['coefficient_rows'], len(pairs))
    stages = []
    for step in steps:
        allowed = step['allowed_parameters']
        columns = [c for c, (a, b) in enumerate(pairs) if a in allowed and b in allowed]
        assert step['active_columns'] == columns
        lookup = {c: j for j, c in enumerate(columns)}
        restricted = [[r, lookup[c], value] for r, c, value in entries if c in lookup]
        matrix = checked_map(restricted, dims['coefficient_rows'], len(columns))
        assert len(matrix['active_row_indices']) == step['nonzero_coefficient_rows']
        stages.append({'allowed_parameters': allowed, 'original_columns': columns,
                       'quadratic_column_pairs': [pairs[c] for c in columns],
                       'rank': step['quotient_rank'], 'matrix': matrix,
                       'forced_parameters': [w['parameter'] for w in step['forced_squares']],
                       'remaining_parameters': step['unresolved_parameters']})
    result['quotient'] = {'path': relative(quotient_path), 'sha256': sha(quotient_path),
        'validation_sha256': sha(validation_path), 'dimensions': dims,
        'parameters': quotient['parameters'], 'stages': stages,
        'degree6_excluded_at_quotient_stage': False}
    path = SOURCE / 'diagonal.json'
    receipt_path = SOURCE / 'diagonal-validation.json'
    diagonal, receipt = load(path), load(receipt_path)
    assert diagonal['schema'] == 'mixed-degree6-extra-diagonal-v1'
    assert receipt['status'] == 'PASS' and receipt['packet_sha256'] == sha(path)
    assert diagonal['quotient_sha256'] == result['quotient']['sha256']
    assert diagonal['source_sha256'] == packet['source_sha256']
    assert diagonal['dimensions']['necessary_quadratic_rank'] == 5
    assert diagonal['dimensions']['correction_columns'] == 2352
    assert diagonal['dimensions']['correction_rank'] == 1451
    pairs, equations = diagonal['gauged_column_pairs'], diagonal['gauged_equations']
    assert len(pairs) == 15 and len(equations) == 5
    eq_polys = []
    for equation in equations:
        poly = {}
        for column, value in equation:
            i, j = pairs[column]
            mon = [0]*5; mon[i] += 1; mon[j] += 1
            add_term(poly, tuple(mon), Fraction(value))
        eq_polys.append(poly)
    attempts = diagonal['multiplier_attempts']
    assert [(a['degree'], a['row_rank'], a['coefficient_columns']) for a in attempts] == [(2, 5, 15), (3, 25, 35), (4, 65, 70)]
    assert [len(a['identities']) for a in attempts] == [0, 0, 3]
    final = attempts[-1]
    mons, multipliers = monomials(4, 5), monomials(2, 5)
    lookup = {mon: i for i, mon in enumerate(mons)}
    entries, column_labels = [], []
    for equation, poly in enumerate(eq_polys):
        for multiplier in multipliers:
            column = len(column_labels); column_labels.append([equation, list(multiplier)])
            for mon, value in poly.items():
                shifted = tuple(a+b for a, b in zip(mon, multiplier))
                entries.append([lookup[shifted], column, str(value)])
    assert len(column_labels) == 75 and len(mons) == 70
    for identity in final['identities']:
        answer = {}
        for equation, multiplier, value in identity['multipliers']:
            assert 0 <= equation < 5 and len(multiplier) == 5 and sum(multiplier) == 2
            for mon, coefficient in eq_polys[equation].items():
                shifted = tuple(a+b for a, b in zip(mon, multiplier))
                add_term(answer, shifted, Fraction(value)*coefficient)
        target = {(0,)*5: Fraction(1)}
        for _ in range(identity['power']):
            product = {}
            for mon, coefficient in target.items():
                for variable, value in identity['linear_form']:
                    shifted = list(mon); shifted[variable] += 1
                    add_term(product, tuple(shifted), coefficient*Fraction(value))
            target = product
        assert identity['power'] == 4 and answer == target
    assert [w['linear_form'] for w in final['identities']] == [[[0, '1'], [4, '-1']], [[1, '1'], [4, '-1']], [[3, '1'], [4, '-1']]]
    reduction = diagonal['two_parameter_reduction']
    assert reduction['equation'] == '5*t^2-8*t*s+8*s^2=0'
    for poly, multiple in zip(eq_polys, reduction['source_equation_multiples']):
        substituted = {}
        for mon, coefficient in poly.items():
            add_term(substituted, (sum(mon)-mon[2], mon[2]), coefficient)
        assert substituted == {(2, 0): 8*Fraction(multiple), (1, 1): -8*Fraction(multiple), (0, 2): 5*Fraction(multiple)}
    result['diagonal'] = {'path': relative(path), 'sha256': sha(path),
        'validation_sha256': sha(receipt_path), 'dimensions': diagonal['dimensions'],
        'attempts': [{k: a[k] for k in ('degree', 'coefficient_columns', 'multiplier_rows', 'row_rank')}
                     | {'difference_identities': len(a['identities'])} for a in attempts],
        'quartic_matrix': checked_map(entries, 70, 75), 'quartic_row_monomials': mons,
        'multiplier_column_labels': column_labels, 'fourth_power_identities_checked_again': 3,
        'two_parameter_reduction': reduction,
        'normalized_polynomial_coefficients': ['8', '-8', '5'],
        'root_display': {'real': .8, 'imaginary_magnitude': 2*math.sqrt(6)/5,
                         'exact_roots': '(4 +/- 2*i*sqrt(6))/5'}}
    path = SOURCE / 'field-obstruction.json'
    receipt_path = SOURCE / 'field-validation.json'
    field, receipt = load(path), load(receipt_path)
    assert field['schema'] == 'mixed-degree6-quadratic-field-v1'
    assert receipt['status'] == 'PASS' and receipt['packet_sha256'] == sha(path)
    assert field['target'] == diagonal['target'] and field['source_sha256'] == packet['source_sha256']
    for name, digest in field['experiment_source_sha256'].items():
        assert sha(ROOT / name) == digest
    assert field['field']['minimal_polynomial_ascending'] == result['diagonal']['normalized_polynomial_coefficients']
    dims = field['dimensions']
    assert dims['correction_columns'] == receipt['correction_pairings'] == 777
    assert dims['correction_rank_over_quadratic_field'] == 742 and dims['augmented_rank_over_quadratic_field'] == 743
    functional = {r: (Fraction(a), Fraction(b)) for r, a, b in field['functional']}
    assert sorted(functional) == [3415, 4213, 4219] and receipt['functional_terms'] == 3
    assert functional == {3415: (Fraction(1,648), Fraction(-5,5184)),
                          4213: (Fraction(-7,180), Fraction(1,144)),
                          4219: (Fraction(7,180), Fraction(-1,144))}
    def multiply_field(x, y):
        a, b = x; c, d = y
        return (a*c-Fraction(8,5)*b*d, a*d+b*c+Fraction(8,5)*b*d)
    sums = [(Fraction(0), Fraction(0)) for _ in range(777)]
    entries = field['matrix_plot']['correction_entries']
    assert len({(r, c) for r, c, a, b in entries}) == len(entries)
    for row, column, a, b in entries:
        value = Fraction(a), Fraction(b)
        assert 0 <= row < 6188 and 0 <= column < 777 and value != (0,0)
        if row in functional:
            product = multiply_field(functional[row], value)
            sums[column] = tuple(x+y for x,y in zip(sums[column], product))
    assert all(value == (0,0) for value in sums)
    rhs = (Fraction(0), Fraction(0))
    for row, a, b in field['matrix_plot']['rhs_entries']:
        if row in functional:
            product = multiply_field(functional[row], (Fraction(a), Fraction(b)))
            rhs = tuple(x+y for x,y in zip(rhs, product))
    assert rhs == (1,0) and field['target_value'] == receipt['target_value'] == ['1', '0']
    ambient_monomials = monomials(12,6)
    assert [ambient_monomials[r] for r in sorted(functional)] == [(2,0,5,0,0,5),(3,0,0,3,0,6),(3,0,0,3,6,0)]
    result['field_obstruction'] = {'path': relative(path), 'sha256': sha(path),
        'validation_sha256': sha(receipt_path), 'dimensions': dims,
        'functional': field['functional'],
        'functional_row_monomials': [[r, ambient_monomials[r]] for r in sorted(functional)],
        'correction_pairings_checked_again': 777, 'target_pairing_checked_again': ['1', '0'],
        'both_complex_points_excluded': True}
    review_path = SOURCE / 'independent-validation.json'
    review = load(review_path)
    assert review['status'] == 'PASS' and review['degree6_E1_sha256'] == result['E1_packet_sha256']
    for audit, key in [('exact_quotient_audit', 'quotient'), ('exact_diagonal_audit', 'diagonal'),
                       ('exact_quadratic_field_audit', 'field_obstruction')]:
        assert review[audit]['status'] == 'PASS'
        assert review[audit]['packet_sha256'] == result[key]['sha256']
    result['independent_validation_sha256'] = sha(review_path)
    return result


def fraction_tex(value):
    value = Fraction(value)
    sign = '-' if value < 0 else ''
    value = abs(value)
    if value.denominator == 1:
        return sign + str(value.numerator)
    return sign + rf'\frac{{{value.numerator}}}{{{value.denominator}}}'


def render_support(data):
    fig, axes = plt.subplots(1, 3, figsize=(16, 8.5), facecolor=PAPER)
    fig.subplots_adjust(left=.075, right=.925, top=.57, bottom=.255, wspace=.50)
    fig.text(.075, .94, 'Mixed biweights: three extra degree-six directions', fontsize=23, weight='bold')
    fig.text(.075, .885, r'$D=(MZ)(F)+c_0R_0+c_1R_1+c_2R_2$', fontsize=20, color=TEAL)
    fig.text(.075, .838, 'The 39-dimensional E1 kernel contains J(F)₆ plus these three independent quotient representatives.',
             fontsize=12, color=MUTED)
    fig.text(.075, .778, '35 directions in J(F)₆ / ⟨F⟩', fontsize=16, weight='bold')
    fig.text(.395, .778, '+ 3 additional directions', fontsize=16, weight='bold', color=PURPLE)
    fig.text(.715, .778, '= 38 after the F gauge', fontsize=16, weight='bold')
    fig.text(.075, .708, 'Each row below is one monomial. The cells are its six exponents; the number at right is its exact coefficient.',
             fontsize=11, color=MUTED)
    for i, (ax, rep) in enumerate(zip(axes, data['representatives'])):
        style(ax)
        exponents = np.array([mon for mon, value in rep['terms']])
        image = ax.imshow(exponents, vmin=0, vmax=6, cmap='viridis', aspect='auto')
        for row in range(4):
            for col in range(6):
                value = exponents[row, col]
                ax.text(col, row, str(value), ha='center', va='center', fontsize=13,
                        color='white' if value <= 3 else INK)
            value = rep['terms'][row][1]
            ax.text(1.05, 1-(row+.5)/4, '$'+fraction_tex(value)+'$', transform=ax.transAxes,
                    ha='left', va='center', fontsize=13, color=CORAL if Fraction(value) < 0 else TEAL)
        ax.set_xticks(range(6), NAMES)
        ax.set_yticks(range(4), [f'term {j+1}' for j in range(4)])
        ax.set_xticks(np.arange(-.5, 6, 1), minor=True)
        ax.set_yticks(np.arange(-.5, 4, 1), minor=True)
        ax.grid(which='minor', color=PAPER, linewidth=2)
        ax.tick_params(which='minor', bottom=False, left=False)
        ax.set_title(rf'$R_{i}$: kernel representative {rep["kernel_index"]}',
                     loc='left', fontsize=13, weight='bold', pad=20)
        ax.set_xlabel('Fixed polynomial coordinates')
        ax.text(1.04, 1.035, 'coefficient', transform=ax.transAxes, fontsize=9, color=MUTED)
    cax = fig.add_axes([.335, .153, .30, .021])
    cb = fig.colorbar(image, cax=cax, orientation='horizontal', ticks=range(7))
    cb.set_label('Exponent (each monomial has total degree 6)', fontsize=10)
    cb.ax.tick_params(labelsize=9)
    fig.text(.075, .07, 'All three representatives satisfy the complete E1 condition with checked numerator lifts.', fontsize=12, color=TEAL)
    fig.text(.075, .03, 'These pictures describe a polynomial basis; they do not establish E2, coprimality, a certificate, or a geometric phase transition.',
             fontsize=10, color=MUTED)
    fig.savefig(OUT / 'mixed-extra-support.png', dpi=100, facecolor=PAPER)
    fig.savefig(OUT / 'mixed-extra-support.svg', facecolor=PAPER, metadata={'Date': None})
    plt.close(fig)


def render_quotient(data):
    fig, axes = plt.subplots(1, 3, figsize=(16, 10), facecolor=PAPER)
    fig.subplots_adjust(left=.075, right=.96, top=.62, bottom=.27, wspace=.36)
    fig.text(.075, .947, 'All three extra directions vanish in the next exact test', fontsize=23, weight='bold')
    fig.text(.075, .897, r'$B_D(N_0)=D\,\mathrm{div}(N_0)-N_0(D)$ modulo the Jacobian ideal $J(F)$',
             fontsize=17, color=TEAL)
    fig.text(.075, .85, 'mixed-biweight  |  Complete 38-parameter E1 family after the F gauge  |  All 315 Koszul corrections accounted for',
             fontsize=11, color=MUTED)
    milestones = [(.075, '38 parameters', '28 exact squares force the first vanishings'),
                  (.402, '10 parameters', '5 further squares remove the last off-diagonal terms'),
                  (.727, '5 diagonal parameters', 'a stronger test is still needed at this stage')]
    for x, title, detail in milestones:
        fig.text(x, .77, title, fontsize=16, weight='bold',
                 bbox={'boxstyle': 'round,pad=.45', 'facecolor': '#E4EDEA', 'edgecolor': 'none'})
        fig.text(x, .725, detail, fontsize=9, color=MUTED)
    fig.text(.347, .77, '→', fontsize=25, color=TEAL)
    fig.text(.675, .77, '→', fontsize=25, color=TEAL)
    names = ['All three extra directions included', 'Last extra direction still included', 'Only the five diagonal terms']
    for i, (ax, stage) in enumerate(zip(axes, data['quotient']['stages'])):
        style(ax)
        matrix = stage['matrix']
        sparse_plot(ax, matrix, 6 if i == 0 else (22 if i == 1 else 45))
        ax.set_title(names[i], loc='left', fontsize=12, weight='bold', pad=30)
        ax.text(0, 1.035, f"{len(matrix['active_row_indices'])} active rows × {matrix['full_shape'][1]} columns  |  rank {stage['rank']}",
                transform=ax.transAxes, fontsize=10, color=MUTED)
        ax.set_ylabel('Active coefficient rows (original order)')
        if i < 2:
            ax.set_xlabel('All active quadratic columns')
        else:
            label = []
            for a, b in stage['quadratic_column_pairs']:
                first, second = a//7, b//7
                label.append(fr'$b_{first}^2$' if first == second else fr'$b_{first}b_{second}$')
            ax.set_xticks(range(15), label, rotation=90, fontsize=9)
            ax.set_yticks(range(len(matrix['active_row_indices'])), [str(r) for r in matrix['active_row_indices']])
            ax.set_ylabel('Original coefficient-row index')
            ax.set_xlabel('The 15 remaining quadratic monomials')
        if i == 0:
            text = r'$c_0^2=c_1^2=0$ here, among 28 isolated squares.'
        elif i == 1:
            text = r'$c_2^2=0$ here, among 5 additional isolated squares.'
        else:
            text = 'No individual square is isolated at this stage.'
        ax.text(0, -.30, text, transform=ax.transAxes, fontsize=10, color=TEAL)
    fig.legend(handles=[Patch(color=TEAL, label='Positive coefficient'),
                        Patch(color=CORAL, label='Negative coefficient')],
               loc='lower left', bbox_to_anchor=(.07, .114), ncol=2, frameon=False, fontsize=10)
    fig.text(.075, .09, '33 exact square identities remove 30 off-diagonal matrix entries and all three extra E1 parameters.', fontsize=12, color=TEAL)
    fig.text(.075, .055, 'Zero coefficient rows are omitted; column order follows the packet. The complete ambient coefficient space has 6,188 rows.',
             fontsize=10, color=MUTED)
    fig.text(.075, .023, 'This figure records an intermediate necessary test. The five remaining parameters are not candidates certified to solve the target.',
             fontsize=10, color=MUTED)
    fig.savefig(OUT / 'mixed-extra-quotient.png', dpi=100, facecolor=PAPER)
    fig.savefig(OUT / 'mixed-extra-quotient.svg', facecolor=PAPER, metadata={'Date': None})
    plt.close(fig)


def render_diagonal(data):
    info = data['diagonal']
    fig, axes = plt.subplots(1, 3, figsize=(16, 10), facecolor=PAPER)
    fig.subplots_adjust(left=.075, right=.96, top=.65, bottom=.27, wspace=.35)
    fig.text(.075, .945, 'Five diagonal parameters reduce to two complex points', fontsize=23, weight='bold')
    fig.text(.075, .895, 'mixed-biweight  |  Exact polynomial multipliers retain the unsuccessful lower-degree attempts',
             fontsize=14, color=TEAL)
    fig.text(.075, .825, r'$(b_0-b_4)^4=(b_1-b_4)^4=(b_3-b_4)^4=0$ follows from the five necessary quadrics.',
             fontsize=17)
    fig.text(.075, .768, r'Therefore $(b_0,b_1,b_2,b_3,b_4,b_5)=(s,s,t,s,s,0)$, with $5t^2-8ts+8s^2=0$.',
             fontsize=17, color=TEAL)

    ax = axes[0]; style(ax)
    attempts = info['attempts']; x = np.arange(3)
    rank = [a['row_rank'] for a in attempts]
    missing = [a['coefficient_columns']-a['row_rank'] for a in attempts]
    ax.bar(x, rank, color=TEAL, width=.65)
    ax.bar(x, missing, bottom=rank, color=GRAY, width=.65)
    for i, attempt in enumerate(attempts):
        ax.text(i, attempt['coefficient_columns']+2, f"{attempt['row_rank']}/{attempt['coefficient_columns']}", ha='center', fontsize=11)
    ax.set_xticks(x, [str(a['degree']) for a in attempts]); ax.set_ylim(0, 80)
    ax.set_xlabel('Total degree of multiplier identity')
    ax.set_ylabel('Dimension of homogeneous coefficient space')
    ax.set_title('Failed searches remain visible', loc='left', fontsize=12, weight='bold', pad=24)
    ax.text(0, 1.025, 'Degree 2: none  |  Degree 3: none  |  Degree 4: 3 identities',
            transform=ax.transAxes, fontsize=9, color=MUTED)
    ax.legend(handles=[Patch(color=TEAL, label='Multiplier-image rank'), Patch(color=GRAY, label='Quotient dimension')],
              loc='upper left', frameon=False, fontsize=9)

    ax = axes[1]; style(ax)
    sparse_plot(ax, info['quartic_matrix'], 8)
    for i in range(1, 5):
        ax.axvline(15*i-.5, color=GRAY, linewidth=.6)
    ax.set_title('Actual degree-four multiplication map', loc='left', fontsize=12, weight='bold', pad=24)
    ax.text(0, 1.025, '70 rows × 75 columns  |  rank 65; not full rank', transform=ax.transAxes, fontsize=10, color=MUTED)
    ax.set_xticks([7+15*i for i in range(5)], [f'P{i}' for i in range(5)])
    ax.set_xlabel('15 quadratic multiples of each necessary equation')
    ax.set_ylabel('All 70 quartic monomials (lexicographic order)')

    ax = axes[2]; style(ax)
    ax.axhline(0, color=GRAY, linewidth=1); ax.axvline(0, color=GRAY, linewidth=1)
    root = info['root_display']
    im = root['imaginary_magnitude']
    ax.scatter([root['real']]*2, [-im, im], s=130, color=PURPLE, edgecolor=PAPER, linewidth=1.5, zorder=3)
    ax.plot([root['real']]*2, [-im, im], linestyle=':', color=PURPLE, linewidth=1)
    for sign, label in ((1, r'$\theta_+$'), (-1, r'$\theta_-$')):
        ax.annotate(label, (root['real'], sign*im), xytext=(12, 2), textcoords='offset points', fontsize=15, color=PURPLE)
    ax.set(xlim=(-.2, 1.7), ylim=(-1.35, 1.35), aspect='equal')
    ax.set_xticks([0, .8, 1.6]); ax.set_yticks([-1, 0, 1])
    ax.set_xlabel(r'Re$(t/s)$'); ax.set_ylabel(r'Im$(t/s)$')
    ax.set_title('Two projective points remain here', loc='left', fontsize=12, weight='bold', pad=24)
    ax.text(0, 1.025, r'$s\ne0$; normalize $s=1$', transform=ax.transAxes, fontsize=11, color=MUTED)
    ax.text(0, -.27, r'$\theta_\pm=(4\pm2i\sqrt{6})/5$', transform=ax.transAxes, fontsize=15, color=PURPLE)

    fig.legend(handles=[Patch(color=TEAL, label='Positive map coefficient'),
                        Patch(color=CORAL, label='Negative map coefficient')],
               loc='lower left', bbox_to_anchor=(.07, .145), ncol=2, frameon=False, fontsize=10)
    fig.text(.075, .112, 'Degree four does not eliminate all five variables: it proves three exact linear differences vanish.', fontsize=12, color=TEAL)
    fig.text(.075, .072, 'The two complex points are the survivors of this necessary relaxation. Their displayed locations are approximate; the defining equation is exact.',
             fontsize=10, color=MUTED)
    fig.text(.075, .035, 'The original numerator correction coefficients must still satisfy the full certificate equation at each point. Neither point is a solution claim.',
             fontsize=10, color=MUTED)
    fig.savefig(OUT / 'mixed-extra-diagonal.png', dpi=100, facecolor=PAPER)
    fig.savefig(OUT / 'mixed-extra-diagonal.svg', facecolor=PAPER, metadata={'Date': None})
    plt.close(fig)


def render_field(data):
    info = data['field_obstruction']
    fig = plt.figure(figsize=(16, 9.5), facecolor=PAPER)
    fig.text(.075, .945, 'Three coefficients exclude both remaining complex points', fontsize=23, weight='bold')
    fig.text(.075, .89, r'Work exactly in $\mathbb{Q}(\theta)$, where $5\theta^2-8\theta+8=0$. The same identity applies to both embeddings.',
             fontsize=15, color=TEAL)
    ax = fig.add_axes([.075, .31, .24, .45]); style(ax)
    root = data['diagonal']['root_display']; im = root['imaginary_magnitude']
    ax.axhline(0, color=GRAY, linewidth=1); ax.axvline(0, color=GRAY, linewidth=1)
    ax.scatter([root['real']]*2, [-im,im], s=170, color=CORAL, marker='x', linewidth=3)
    for sign, label in ((1,r'$\theta_+$'),(-1,r'$\theta_-$')):
        ax.annotate(label+' excluded', (root['real'],sign*im), xytext=(13,1),textcoords='offset points',fontsize=12,color=CORAL)
    ax.set(xlim=(-.2,2.0),ylim=(-1.4,1.4),aspect='equal')
    ax.set_xlabel(r'Re$(\theta)$');ax.set_ylabel(r'Im$(\theta)$')
    ax.set_xticks([0,.8,1.6]);ax.set_yticks([-1,0,1])
    ax.set_title('Neither survivor extends to a certificate',loc='left',fontsize=12,weight='bold',pad=22)

    ax = fig.add_axes([.40,.31,.55,.45]); ax.axis('off')
    ax.text(0,1.08,r'A linear functional $\ell$ reads only three polynomial coefficients:',fontsize=14,weight='bold')
    cells = [
        [r'$3415$',r'$X_0^2X_2^5Y_2^5$',r'$(8-5\theta)/5184$'],
        [r'$4213$',r'$X_0^3Y_0^3Y_2^6$',r'$(-28+5\theta)/720$'],
        [r'$4219$',r'$X_0^3Y_0^3Y_1^6$',r'$(28-5\theta)/720$']]
    table=ax.table(cellText=cells,colLabels=['Coefficient row','Monomial','Exact weight'],cellLoc='center',
                   colLoc='center',bbox=[0,.43,1,.52],colWidths=[.23,.35,.42])
    table.auto_set_font_size(False);table.set_fontsize(14)
    for (row,col),cell in table.get_celld().items():
        cell.set_edgecolor(PAPER);cell.set_linewidth(3)
        cell.set_facecolor('#E4EDEA' if row==0 else '#F0F3ED')
        cell.get_text().set_color(INK)
        if row==0:cell.get_text().set_fontsize(12)
    ax.text(0,.24,r'$\ell(C_j)=0$ for all 777 correction columns',fontsize=17,color=TEAL)
    ax.text(0,.08,r'$\ell(R)=1$ for the required right-hand side',fontsize=17,color=CORAL)
    ax.text(.72,.16,r'$0\ne1$',fontsize=28,color=CORAL,
            bbox={'boxstyle':'round,pad=.45','facecolor':'#F8E6E0','edgecolor':'none'})

    fig.text(.075,.226,'The full correction matrix has rank 742; adjoining the target raises the rank to 743.',fontsize=14,color=TEAL)
    fig.text(.075,.175,'Its 777 columns include 462 unrestricted quotient terms and all 315 shared Koszul correction directions.',fontsize=12,color=MUTED)
    fig.text(.075,.115,'Both degree-six candidates are excluded by exact arithmetic. Combined with the preceding reductions, the complete mixed-biweight degree-six family is excluded.',
             fontsize=11,color=TEAL)
    fig.text(.075,.066,'The complex-point coordinates are drawn approximately, but the field arithmetic and every functional pairing use rational coefficients exactly.',
             fontsize=10,color=MUTED)
    fig.text(.075,.027,'Higher degrees remain open. This is an obstruction, not a certificate of existence, Lean proof, or accepted solution.',fontsize=10,color=MUTED)
    fig.savefig(OUT/'mixed-extra-field.png',dpi=100,facecolor=PAPER)
    fig.savefig(OUT/'mixed-extra-field.svg',facecolor=PAPER,metadata={'Date':None})
    plt.close(fig)


def main():
    if not __debug__:
        raise RuntimeError('Run without -O: packet bindings use assertions')
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'text.color': INK, 'axes.labelcolor': INK, 'svg.fonttype': 'none',
                         'svg.hashsalt': 'mixed-degree6-extra-v1'})
    data = load_checked()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'plot-data.json').write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8', newline='\n')
    render_support(data)
    render_quotient(data)
    render_diagonal(data)
    render_field(data)
    for path in OUT.glob('*.svg'):
        path.write_text('\n'.join(line.rstrip() for line in path.read_text(encoding='utf-8').splitlines())+'\n',
                        encoding='utf-8', newline='\n')
    print(json.dumps({'status': 'PASS', 'output': relative(OUT), 'extra_denominator_monomials': 12,
                      'packet_bindings_checked': 4, 'fourth_power_identities_rechecked': 3,
                      'quadratic_field_correction_pairings_rechecked': 777,
                      'quadratic_field_rhs_rechecked': ['1', '0'],
                      'independent_review_bound': True}, indent=2))


if __name__ == '__main__':
    main()
