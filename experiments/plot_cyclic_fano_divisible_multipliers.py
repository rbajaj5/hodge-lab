#!/usr/bin/env python3
"""Draw the checked multiplier search on coordinate-divisible quadratic polars.

Every displayed elimination must be backed by an exact checked identity.
Modular screens are displayed as discovery records, not characteristic-zero
proofs. Dense occupancy arrays are saved as compact coordinates.
"""
from __future__ import annotations

from fractions import Fraction as Q
import hashlib
from itertools import combinations_with_replacement
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
import cyclic_fano_quadratic_polars as source

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'results/cyclic-fano-divisible-multipliers'
OUT = ROOT / 'results/cyclic-fano-divisible-multipliers-figures'
INK, MUTED, PAPER = '#17323B', '#53666D', '#FAFAF5'
TEAL, PURPLE, CORAL = '#166A70', '#7967AA', '#B94D42'
NAMES = ('X0', 'X1', 'Y0', 'Y1', 'Y2')


def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sparse(terms):
    return {tuple(t['powers']): Q(t['coefficient']) for t in terms}


def dot(a, b):
    return sum((c * b.get(m, 0) for m, c in a.items()), Q(0))


def monomials(n, degree):
    out = []
    for indices in combinations_with_replacement(range(n), degree):
        powers = [0] * n
        for i in indices:
            powers[i] += 1
        out.append(tuple(powers))
    return sorted(out)


def add_scaled(result, polynomial, scalar):
    for m, c in polynomial.items():
        value = result.get(m, Q(0)) + scalar*c
        if value:
            result[m] = value
        else:
            result.pop(m, None)


def linear_multiple(polynomial, variable):
    result = {}
    for m, c in polynomial.items():
        p = list(m)
        p[variable] += 1
        result[tuple(p)] = c
    return result


def independent_indices(polynomials, pivots=None):
    pivots = {} if pivots is None else {m: p.copy() for m, p in pivots.items()}
    selected = []
    for i, polynomial in enumerate(polynomials):
        row = polynomial.copy()
        while row:
            key = min(row)
            if key not in pivots:
                scale = row[key]
                pivots[key] = {m: c/scale for m, c in row.items()}
                selected.append(i)
                break
            add_scaled(row, pivots[key], -row[key])
    return selected, pivots


def check_stage(exact, stage, expected_dimension):
    active = stage['active_raw_parameter_indices']
    assert len(active) == expected_dimension and len(set(active)) == len(active)
    rows, kept = source.restricted_rows(exact, set(active))
    indices = sorted(kept)
    pure = [j for j in indices if exact['labels'][j]['kind'] == 'a*a']
    mixed = [j for j in indices if exact['labels'][j]['kind'] == 'a*c']
    assert stage['rows'] == len(rows) and stage['columns'] == len(indices)
    assert stage['pure_columns'] == len(pure) == expected_dimension*(expected_dimension+1)//2
    assert stage['mixed_columns'] == len(mixed) == expected_dimension*55
    monomial_for_column = {}
    for j in pure:
        a, b = exact['labels'][j]['indices']
        monomial_for_column[j] = tuple(int(k == a) + int(k == b) for k in active)
    equations = []
    checked_products = 0
    for entry in stage['equations']:
        polynomial, dual = sparse(entry['polynomial']), sparse(entry['dual'])
        combined = {}
        for m, c in dual.items():
            assert m in rows
            add_scaled(combined, rows[m], c)
            checked_products += len(rows[m])
        expected = {j: polynomial[p] for j, p in monomial_for_column.items() if polynomial.get(p)}
        assert combined == expected
        equations.append(polynomial)
    assert len(equations) == stage['rank'] - stage['mixed_rank']
    return equations, [exact['columns'][j] for j in indices], indices, checked_products


def check_cubic(equations, proof, dimension):
    columns = [linear_multiple(q, j) for q in equations for j in range(dimension)]
    ambient = monomials(dimension, 3)
    assert proof['rows'] == len(ambient) and proof['columns'] == len(columns) and proof['degree'] == 3
    seen = set()
    terms = products = 0
    for identity in proof['identities']:
        k = identity['parameter_index']
        assert 0 <= k < dimension and k not in seen and identity['power'] == 3
        seen.add(k)
        total = {}
        for term in identity['multipliers']:
            q, j = term['equation_index'], term['linear_variable']
            assert 0 <= q < len(equations) and 0 <= j < dimension
            column = columns[q*dimension+j]
            add_scaled(total, column, Q(term['coefficient']))
            terms += 1
            products += len(column)
        assert total == {tuple(3*int(i == k) for i in range(dimension)): Q(1)}
    assert sorted(set(range(dimension)) - seen) == proof['remaining_parameter_indices']
    return columns, ambient, dict(identities=len(seen), multiplier_terms=terms, coefficient_products=products)


def physical_digest(exact, indices):
    digest = hashlib.sha256()
    for j in indices:
        entry = {'label': exact['labels'][j], 'polynomial': source.encode(exact['columns'][j])}
        digest.update((json.dumps(entry, sort_keys=True, separators=(',', ':'))+'\n').encode())
    return digest.hexdigest()


def check_data():
    packet_path, primary_path, review_path = [INPUT / n for n in ('packet.json', 'validation.json', 'independent-validation.json')]
    packet, primary, review = map(load, (packet_path, primary_path, review_path))
    producer_path = ROOT / 'experiments/cyclic_fano_divisible_multipliers.py'
    checker_path = ROOT / 'experiments/check_cyclic_fano_divisible_multipliers.py'
    raw = ROOT / 'results/cyclic-fano-curve/source/instance.rec'
    assert packet['schema'] == 'cyclic-fano-divisible-multipliers-v1'
    assert primary['schema'] == 'cyclic-fano-divisible-multipliers-validation-v1'
    assert review['schema'] == 'cyclic-fano-divisible-multipliers-independent-v1'
    assert packet['status'] == primary['status'] == review['status'] == 'PASS'
    assert packet['instance'] == 'cyclic-triple-fano' and packet['degree'] == 7 and packet['q'] == 1
    assert packet['producer_sha256'] == primary['producer_sha256'] == sha(producer_path)
    assert primary['packet_sha256'] == review['packet_lf_sha256'] == sha(packet_path)
    assert review['checker_lf_sha256'] == sha(checker_path)
    assert review['primary_validation_lf_sha256'] == sha(primary_path)
    assert packet['source_instance_sha256'] == review['source_instance_lf_sha256'] == sha(raw)
    paths = (packet_path, primary_path, review_path, producer_path, checker_path, raw)
    bindings = {p.relative_to(ROOT).as_posix(): sha(p) for p in paths}
    for dependencies in (packet['dependencies'], review['independent_arithmetic_dependencies']):
        for name, digest in dependencies.items():
            path = ROOT / 'experiments' / name
            assert sha(path) == digest
            bindings[path.relative_to(ROOT).as_posix()] = digest
    prior_ref = packet['prior_projection_proof']
    prior_path = ROOT / prior_ref['packet']
    prior_primary_path = prior_path.parent / 'validation.json'
    prior_review_path = prior_path.parent / 'independent-validation.json'
    assert sha(prior_path) == prior_ref['packet_sha256']
    assert sha(prior_primary_path) == prior_ref['primary_receipt_sha256']
    assert sha(prior_review_path) == prior_ref['independent_receipt_sha256']
    prior, prior_primary, prior_review = map(load, (prior_path, prior_primary_path, prior_review_path))
    assert prior['status'] == prior_primary['status'] == prior_review['status'] == 'PASS'
    assert prior_primary['packet_sha256'] == prior_review['packet_lf_sha256'] == sha(prior_path)
    assert prior_ref['raw_Koszul_fields'] == 230
    assert prior_ref['compact_correction_types'] == 55 and prior_ref['quotient_directions'] == 246
    for p in (prior_path, prior_primary_path, prior_review_path):
        bindings[p.relative_to(ROOT).as_posix()] = sha(p)

    exact = source.system()
    assert source.map_digest(exact) == prior['full_map']['coefficient_sha256']
    labels = packet['parameter_order']
    assert [(p['matrix_row'], p['matrix_column']) for p in labels] == [(i,j) for i in range(5) for j in range(5)]
    for label in labels:
        raw_index = label['raw_parameter_index']
        basis = exact['basis'][raw_index]
        i, j = label['matrix_row'], label['matrix_column']
        assert basis['component'] == source.BASE[i]
        expected = [0] * 6
        expected[source.BASE[i]] += 1
        expected[source.BASE[j]] += 1
        assert basis['quadratic_powers'] == label['quadratic_powers'] == expected
    initial, rebuilt = packet['initial_stage'], packet['rebuild_stage']
    assert initial['active_raw_parameter_indices'] == [p['raw_parameter_index'] for p in labels]
    assert (initial['rows'], initial['columns'], initial['rank'], initial['mixed_rank']) == (1228,1700,833,678)
    assert (rebuilt['rows'], rebuilt['columns'], rebuilt['rank'], rebuilt['mixed_rank']) == (851,290,232,220)
    qs, physical_columns, physical_indices, products1 = check_stage(exact, initial, 25)
    small_qs, rebuilt_columns, rebuilt_indices, products2 = check_stage(exact, rebuilt, 5)
    assert len(qs) == 155 and len(small_qs) == 12
    cubic, small_cubic = packet['cubic_stage'], packet['final_cubic_stage']
    cubic_columns, cubic_rows, first_checks = check_cubic(qs, cubic, 25)
    small_columns, small_rows, final_checks = check_cubic(small_qs, small_cubic, 5)
    remaining = cubic['remaining_parameter_indices']
    assert remaining == [2,7,12,17,22]
    assert rebuilt['active_raw_parameter_indices'] == [initial['active_raw_parameter_indices'][k] for k in remaining]
    assert not small_cubic['remaining_parameter_indices']
    assert cubic['rank'] == 2892 and small_cubic['rank'] == 35
    assert first_checks['identities'] == 20 and first_checks['multiplier_terms'] == 588
    assert final_checks['identities'] == 5
    restricted_old = [{tuple(m[k] for k in remaining): c for m, c in q.items()
                       if all(not exponent or k in remaining for k, exponent in enumerate(m))} for q in qs]
    old_basis_indices, pivots = independent_indices(restricted_old)
    new_basis_indices, combined_pivots = independent_indices(small_qs, pivots)
    small_basis_indices, small_pivots = independent_indices(small_qs)
    assert len(old_basis_indices) == 9 and len(new_basis_indices) == 3
    assert len(combined_pivots) == len(small_basis_indices) == 12
    _, inclusion_pivots = independent_indices(restricted_old, small_pivots)
    assert len(inclusion_pivots) == 12
    assert packet['rebuild_diagnostic'] == dict(initial_quadrics_after_restriction_rank=9,
                fresh_rebuilt_quadrics_rank=12, additional_independent_quadrics=3,
                restricted_initial_span_contained_in_rebuilt_span=True)
    arranged_quadrics = [restricted_old[j] for j in old_basis_indices] + [small_qs[j] for j in new_basis_indices]
    assert primary['initial_physical_duals'] == 155 and primary['rebuild_physical_duals'] == 12
    assert primary['initial_cube_identities'] == 20 and primary['final_cube_identities'] == 5
    assert primary['compact_corrections_retained'] == 55 and primary['negative_controls_rejected'] == 8
    assert prior['coordinate_divisible_modular_screen']['isolated_square_indices_mod_prime'] == []
    for stage, proof, indices in ((initial, review['initial_physical_map'], physical_indices),
                                   (rebuilt, review['rebuilt_physical_map'], rebuilt_indices)):
        for key in ('rows','columns','rank','mixed_rank','pure_columns','mixed_columns'):
            assert stage[key] == proof[key]
        assert proof['coefficient_sha256'] == physical_digest(exact, indices)
        assert proof['necessary_quadrics'] == len(stage['equations'])
    for proof, audit in ((cubic, review['initial_cubic_map']), (small_cubic, review['final_cubic_map'])):
        for key in ('rows','columns','rank','remaining_parameter_indices'):
            assert proof[key] == audit[key]
        assert audit['isolated_squares'] == []
    assert review['rebuilding_gain'] == dict(restricted_old_rank=9, rebuilt_rank=12,
                                            added_independent_constraints=3, span_inclusion=True)
    assert review['necessary_quadric_identities'] == 167 and review['physical_coefficient_pairings'] == 266980
    assert review['initial_multiplier_terms'] == first_checks['multiplier_terms'] == 588
    assert review['final_multiplier_terms'] == final_checks['multiplier_terms'] == 112
    assert review['exact_failed_square_queries'] == 30 and review['negative_controls_rejected'] == 13
    return dict(schema='cyclic-fano-divisible-multipliers-plot-v1', instance='cyclic-triple-fano', discussion_number=112,
                source_sha256=bindings, sha256_policy='File bytes with CRLF normalized to LF',
                plot_source_sha256=sha(Path(__file__)), parameter_order=labels,
                physical_map=display_map(physical_columns, 3, 3),
                physical_column_indices_in_prior_map=physical_indices,
                physical_zero_rows_omitted=1820-len({m for p in physical_columns for m in p}),
                quadric_map=display_map(qs, rows=monomials(25,2)),
                cubic_map=display_map(cubic_columns, 4, 5, cubic_rows),
                rebuilt_physical_map=display_map(rebuilt_columns, 2, 1),
                rebuilt_column_indices_in_prior_map=rebuilt_indices,
                rebuilt_zero_rows_omitted=1820-len({m for p in rebuilt_columns for m in p}),
                final_quadric_map=display_map(small_qs, rows=monomials(5,2)),
                arranged_rebuilt_quadric_map=display_map(arranged_quadrics, rows=monomials(5,2)),
                rebuilt_basis_order=[{'restricted_initial_equation': j} for j in old_basis_indices]
                                    + [{'new_rebuilt_equation': j} for j in new_basis_indices],
                rebuilding_gain=packet['rebuild_diagnostic'],
                final_cubic_map=display_map(small_columns, rows=small_rows),
                exact_physical_dual_count=167, physical_dual_coefficient_products=products1+products2,
                independent_physical_pairings=review['physical_coefficient_pairings'],
                independent_exact_failed_square_queries=review['exact_failed_square_queries'],
                cubic_identity_checks=[first_checks,final_checks], remaining_after_first_round=remaining,
                attempts=packet['attempts'], limits=packet['limits'])


def display_map(columns, row_bin=1, col_bin=1, rows=None):
    rows = sorted({m for p in columns for m, c in p.items() if c}) if rows is None else rows
    lookup = {m: i for i, m in enumerate(rows)}
    bins = set()
    nonzero = 0
    for j, p in enumerate(columns):
        for m, c in p.items():
            if c:
                nonzero += 1
                bins.add((lookup[m] // row_bin, j // col_bin))
    shape = [len(rows), len(columns)]
    return dict(shape=shape, row_monomials=[list(m) for m in rows],
                nonzero_coefficients=nonzero, bin_size=[row_bin, col_bin],
                binned_shape=[(shape[0]+row_bin-1)//row_bin, (shape[1]+col_bin-1)//col_bin],
                occupied_bins=[list(p) for p in sorted(bins)],
                bin_rule='Occupied iff at least one exact nonzero coefficient lies in the bin.')


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    fig.savefig(path.with_suffix('.png'), dpi=160, facecolor=PAPER)
    svg = path.with_suffix('.svg')
    fig.savefig(svg, facecolor=PAPER, metadata={'Date': None})
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',
                   encoding='utf-8', newline='\n')
    plt.close(fig)


def occupancy(ax, matrix, color=TEAL):
    grid = np.zeros(matrix['binned_shape'], dtype=np.uint8)
    if matrix['occupied_bins']:
        positions = np.asarray(matrix['occupied_bins'])
        grid[positions[:, 0], positions[:, 1]] = 1
    nr, nc = matrix['shape']
    br, bc = matrix['bin_size']
    ax.imshow(grid, cmap=ListedColormap([PAPER, color]), interpolation='nearest',
              aspect='auto', extent=(-.5, grid.shape[1]*bc-.5, grid.shape[0]*br-.5, -.5), rasterized=True)
    ax.set(xlim=(-.5, nc-.5), ylim=(nr-.5, -.5))
    ax.tick_params(labelsize=11, colors=MUTED)
    for spine in ax.spines.values():
        spine.set_color('#CED6D2')


def feature(data):
    fig = plt.figure(figsize=(14, 8.8), facecolor=PAPER)
    fig.text(.055, .944, 'A quadratic-polar subfamily is excluded', fontsize=27, weight='bold')
    fig.text(.055, .894, r'cyclic-triple-fano · #112   |   $v_i=x_i\sum_j M_{ij}x_j$, with all 25 entries of M variable',
             fontsize=14, color=MUTED)
    ax1 = fig.add_axes([.065, .393, .245, .355])
    ax2 = fig.add_axes([.385, .393, .270, .355])
    ax3 = fig.add_axes([.740, .393, .210, .355])
    grid = np.ones((5, 5), dtype=int)
    for k in data['remaining_after_first_round']:
        grid[k//5, k%5] = 2
    ax1.imshow(grid, cmap=ListedColormap(['#C5E0DA', '#DFD5ED']), vmin=1, vmax=2, aspect='auto')
    for i in range(5):
        for j in range(5):
            ax1.text(j, i, str(grid[i,j]), ha='center', va='center', fontsize=20,
                     weight='bold', color=TEAL if grid[i,j] == 1 else PURPLE)
    names = ['$'+n[0]+'_'+n[1]+'$' for n in NAMES]
    ax1.set_xticks(range(5), names, fontsize=13)
    ax1.set_yticks(range(5), names, fontsize=13)
    ax1.set(xlabel='column j of M', ylabel='component i of v')
    ax1.set_xticks(np.arange(-.5, 5, 1), minor=True)
    ax1.set_yticks(np.arange(-.5, 5, 1), minor=True)
    ax1.grid(which='minor', color=PAPER, linewidth=2)
    ax1.tick_params(which='minor', length=0)
    ax1.set_title('Round when forced zero', loc='left', fontsize=17, pad=17)
    occupancy(ax2, data['cubic_map'])
    ax2.set_title('1  Twenty exact cubes', loc='left', fontsize=17, color=TEAL, pad=17)
    ax2.set(xlabel='3,875 linear multiples of quadrics', ylabel='2,925 cubic monomials')
    occupancy(ax3, data['final_cubic_map'], PURPLE)
    ax3.set_title('2  Five final cubes', loc='left', fontsize=17, color=PURPLE, pad=17)
    ax3.set(xlabel='60 linear multiples', ylabel='35 cubic monomials')
    fig.text(.065, .322, '1: 20 entries   ·   2: five Y₀-column entries', fontsize=12, color=MUTED)
    fig.text(.385, .322, 'Exact rank 2,892; 20 coordinate cubes isolated.', fontsize=12, color=TEAL)
    fig.text(.740, .322, 'Exact rank 35; all cubics spanned.', fontsize=12, color=PURPLE)
    fig.text(.385, .284, 'Display bins: 4 rows × 5 columns; any exact nonzero.', fontsize=11, color=MUTED)
    fig.text(.055, .245, r'Exact identities: $M_{ij}^{3}=\sum_{r,k}c_{ijrk}M_kQ_r(M)$; rebuild on the five surviving entries.',
             fontsize=17)
    fig.text(.055, .190, 'All 25 parameters vanish. This entire coordinate-divisible subfamily has no certificate.',
             fontsize=16, weight='bold', color=TEAL)
    fig.text(.055, .137, 'The full 75-parameter quadratic-direction family remains open; the restriction here is essential.',
             fontsize=14, color=CORAL)
    fig.text(.055, .087, '55 correction types and all 246 quotient directions retained. Modular screening was followed by exact rational identities.',
             fontsize=12, color=MUTED)
    fig.text(.055, .044, 'Maps show exact coefficient occupancy, with documented bins in the large map. No solved instance or Lean certificate is claimed.',
             fontsize=12, color=MUTED)
    save(fig, 'cyclic-fano-divisible-multipliers')


def detail(data):
    fig = plt.figure(figsize=(16, 9.5), facecolor=PAPER)
    fig.text(.055, .942, 'Eliminate correction variables, then use polynomial multipliers', fontsize=24, weight='bold')
    fig.text(.055, .895, 'cyclic-triple-fano · discussion #112   |   actual maps for the 25-parameter coordinate-divisible family',
             fontsize=14, color=MUTED)
    axes = [fig.add_axes([.065, .390, .350, .380]),
            fig.add_axes([.495, .390, .200, .380]),
            fig.add_axes([.775, .390, .175, .380])]
    specs = [('physical_map', 'Full physical coefficient map', TEAL),
             ('quadric_map', '155 necessary quadrics', TEAL),
             ('arranged_rebuilt_quadric_map', 'Rebuild adds 3 constraints', PURPLE)]
    for ax, (key, title, color) in zip(axes, specs):
        occupancy(ax, data[key], color)
        ax.set_title(title, loc='left', fontsize=17, pad=18)
        ax.set(xlabel='column index', ylabel='coefficient-row index')
    axes[0].axvline(325-.5, color=CORAL, linewidth=1.2)
    axes[2].axvline(9-.5, color=CORAL, linewidth=1.5)
    captions = [('1,228 × 1,700; exact rank 833', '325 parameter quadratics + 1,375 mixed terms'),
                ('325 monomials × 155 quadrics', 'Exact duals eliminate correction variables'),
                ('15 monomials × (9 + 3) quadrics', '9 old restrictions + 3 new constraints')]
    for x, (first, second) in zip((.065, .495, .775), captions):
        fig.text(x, .315, first, fontsize=13)
        fig.text(x, .271, second, fontsize=11.5, color=MUTED)
    fig.text(.065, .240, '592 zero rows omitted; 3-row × 3-column bins.', fontsize=11, color=MUTED)
    fig.text(.055, .207, 'Rebuilding gives three independent constraints beyond restriction alone; all 55 correction types remain allowed.',
             fontsize=14, weight='bold')
    fig.text(.055, .153, 'Earlier square queries modulo 1009 found no isolated coordinate squares; degree-three multipliers made progress.',
             fontsize=13, color=MUTED)
    fig.text(.055, .103, 'The first-stage cubic map has codimension 33. It need not span every cubic to prove that 20 parameters vanish.',
             fontsize=13, color=CORAL)
    fig.text(.055, .050, 'Row/column order, all-zero rows, bin sizes, source hashes, failed screens and exact witness checks are recorded in compact plot-data.json.',
             fontsize=11.5, color=MUTED)
    save(fig, 'cyclic-fano-divisible-multipliers-maps')


def main():
    assert __debug__, 'Run without -O so the exact checks stay enabled.'
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'text.color': INK,
                         'axes.labelcolor': INK, 'axes.titlecolor': INK,
                         'svg.fonttype': 'none', 'svg.hashsalt': 'cyclic-fano-divisible-multipliers-v1'})
    data = check_data()
    feature(data)
    detail(data)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'plot-data.json').write_text(json.dumps(data, separators=(',', ':'))+'\n', encoding='utf-8', newline='\n')
    assert all(sha(ROOT/name) == digest for name, digest in data['source_sha256'].items())
    print(json.dumps({'status': 'PASS', 'source_bindings': len(data['source_sha256']),
                      'physical_duals': data['exact_physical_dual_count'],
                      'physical_dual_products': data['physical_dual_coefficient_products'],
                      'cube_identity_checks': data['cubic_identity_checks'],
                      'excluded_parameter_family_dimension': 25,
                      'full_75_parameter_family': 'unresolved',
                      'plot_data_bytes': (OUT/'plot-data.json').stat().st_size,
                      'figures': ['cyclic-fano-divisible-multipliers.png', 'cyclic-fano-divisible-multipliers-maps.png']}))


if __name__ == '__main__':
    main()
