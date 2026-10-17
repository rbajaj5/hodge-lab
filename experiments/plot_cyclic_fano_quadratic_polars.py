#!/usr/bin/env python3
"""Plot checked quadratic-polar subfamilies and their actual coefficient maps.

The five component exclusions are conditional, separate statements. The full
75-parameter family is not excluded. Large maps use explicitly specified
any-nonzero bins; their colors encode occupancy, never a numerical spectrum.
"""
from __future__ import annotations

from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import FancyBboxPatch
import numpy as np

import cyclic_fano_quadratic_polars as producer

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'results/cyclic-fano-quadratic-polars'
OUT = ROOT / 'results/cyclic-fano-quadratic-polars-figures'
INK, MUTED, PAPER = '#17323B', '#53666D', '#FAFAF5'
TEAL, PURPLE, CORAL = '#166A70', '#7967AA', '#B94D42'
BASE = (0, 1, 3, 4, 5)
NAMES = ('X0', 'X1', 'Y0', 'Y1', 'Y2')


def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sparse(terms):
    return {tuple(t['powers']): Q(t['coefficient']) for t in terms}


def dot(a, b):
    return sum((c * b.get(m, 0) for m, c in a.items()), Q(0))


def display_map(data, indices, row_bin, col_bin):
    """Keep the exact row/column order and record all occupied display bins."""
    indices = sorted(indices)
    columns = [data['columns'][j] for j in indices]
    rows = sorted({m for p in columns for m, c in p.items() if c})
    lookup = {m: i for i, m in enumerate(rows)}
    bins = set()
    nonzero = 0
    for j, p in enumerate(columns):
        for m, c in p.items():
            if c:
                nonzero += 1
                bins.add((lookup[m] // row_bin, j // col_bin))
    shape = [len(rows), len(indices)]
    return {
        'shape': shape,
        'global_column_indices': indices,
        'physical_row_monomials_lexicographic': [list(m) for m in rows],
        'nonzero_coefficients': nonzero,
        'bin_size_rows_columns': [row_bin, col_bin],
        'bin_rule': 'Occupied iff at least one exact nonzero coefficient lies in the bin.',
        'binned_shape': [(shape[0] + row_bin - 1) // row_bin,
                         (shape[1] + col_bin - 1) // col_bin],
        'occupied_bins': [list(p) for p in sorted(bins)],
        'pure_columns': sum(data['labels'][j]['kind'] == 'a*a' for j in indices),
    }


def check_data():
    packet_path = INPUT / 'packet.json'
    primary_path = INPUT / 'validation.json'
    review_path = INPUT / 'independent-validation.json'
    packet, primary, review = map(load, (packet_path, primary_path, review_path))
    source = ROOT / 'results/cyclic-fano-curve/source/instance.rec'
    producer_path = ROOT / 'experiments/cyclic_fano_quadratic_polars.py'
    checker_path = ROOT / 'experiments/check_cyclic_fano_quadratic_polars.py'
    assert packet['schema'] == 'cyclic-fano-quadratic-polars-v1'
    assert primary['schema'] == 'cyclic-fano-quadratic-polars-validation-v1'
    assert review['schema'] == 'cyclic-fano-quadratic-polars-independent-v1'
    assert packet['status'] == primary['status'] == review['status'] == 'PASS'
    assert packet['instance'] == 'cyclic-triple-fano' and packet['degree'] == 7 and packet['q'] == 1
    assert packet['producer_sha256'] == primary['producer_sha256'] == sha(producer_path)
    assert primary['packet_sha256'] == review['packet_lf_sha256'] == sha(packet_path)
    assert review['primary_validation_lf_sha256'] == sha(primary_path)
    assert review['checker_lf_sha256'] == sha(checker_path)
    assert packet['source_instance_sha256'] == review['source_instance_lf_sha256'] == sha(source)
    bindings = {p.relative_to(ROOT).as_posix(): sha(p) for p in
                (packet_path, primary_path, review_path, producer_path, checker_path, source)}
    for dependencies in (packet['dependencies'], review['independent_arithmetic_dependencies']):
        for name, digest in dependencies.items():
            path = ROOT / 'experiments' / name
            assert sha(path) == digest
            bindings[path.relative_to(ROOT).as_posix()] = digest

    exact = producer.system()
    assert producer.map_digest(exact) == packet['full_map']['coefficient_sha256'] == review['coefficient_sha256']
    assert exact['basis'] == packet['parameter_basis']
    assert exact['correction_labels'] == packet['projection']['compact_generators']
    assert len(exact['basis']) == 75 and len(exact['residuals']) == 2850 and len(exact['mixed']) == 4125
    assert len(exact['columns']) == packet['full_map']['columns'] == 6975
    assert len(exact['rows']) == packet['full_map']['active_rows'] == 1799
    assert packet['full_map']['potential_rows'] == 1820
    projection = packet['projection']
    assert projection['raw_field_count'] == len(projection['raw_field_labels']) == 230
    assert projection['compact_generator_count'] == len(projection['compact_generators']) == 55
    assert sum(c['kind'] == 'linear_base_pair' for c in projection['compact_generators']) == 50
    assert sum(c['kind'] == 't_mixed' for c in projection['compact_generators']) == 5
    assert projection['quotient_projection_identities'] == len(projection['quotient_monomials']) == 246

    monomials = [p['quadratic_powers'] for p in packet['parameter_basis'][:15]]
    pure_indices = [i for i, m in enumerate(monomials) if 2 in m]
    assert pure_indices == [0, 5, 9, 12, 14]
    expected_stats = dict(exact_E1_and_upstairs_Piola_lifts=75,
                          parameter_quadratic_coefficients_reconstructed=2850,
                          compact_mixed_columns_reconstructed=4125,
                          full_Koszul_projection_checks=17250,
                          complete_raw_Koszul_fields=230,
                          surviving_correction_types=55, quotient_columns=246,
                          component_family_count=5, component_parameter_dimension=15,
                          square_duals=75, dual_nonzero_terms=296,
                          dual_coefficient_pairings=53875,
                          component_residual_rescaling_identities=600,
                          negative_controls_rejected=9)
    for key, value in expected_stats.items():
        assert review[key] == value, (key, review[key], value)
    families, chosen_maps = [], []
    pairings = terms = 0
    for component, family in enumerate(packet['component_family_exclusions']):
        assert family['component'] == BASE[component] and family['base_name'] == NAMES[component]
        active = set(range(15 * component, 15 * (component + 1)))
        rounds = [0] * 15
        stage_stats = []
        for stage_index, stage in enumerate(family['stages']):
            assert set(stage['active_parameters']) == active
            physical_rows, kept = producer.restricted_rows(exact, active)
            indices = sorted(kept)
            assert len(physical_rows) == stage['active_rows']
            assert len(indices) == stage['columns'] == (945 if stage_index == 0 else 605)
            expected_forced = {15 * component + i for i in pure_indices} if stage_index == 0 else active.copy()
            assert {w['parameter_index'] for w in stage['square_duals']} == expected_forced
            for witness in stage['square_duals']:
                k = witness['parameter_index']
                dual = sparse(witness['dual'])
                terms += len(dual)
                for j in indices:
                    label = exact['labels'][j]
                    target = label['kind'] == 'a*a' and label['indices'] == [k, k]
                    assert dot(dual, exact['columns'][j]) == int(target)
                    pairings += 1
                rounds[k - 15 * component] = stage_index + 1
            independent_stage = review['exact_component_stages'][component]['stages'][stage_index]
            assert independent_stage['exact_rank'] == stage['rank']
            assert independent_stage['rows'] == stage['active_rows']
            assert independent_stage['columns'] == stage['columns']
            assert independent_stage['forced_square_indices'] == sorted(expected_forced)
            stage_stats.append({k: stage[k] for k in ('active_parameters', 'active_rows', 'columns', 'rank')})
            if component == 0:
                chosen_maps.append(display_map(exact, indices, 3, 2))
            active -= expected_forced
        assert not active and not family['remaining_parameters'] and sorted(rounds) == [1] * 5 + [2] * 10
        families.append({'component': family['component'], 'base_name': family['base_name'],
                         'elimination_rounds': rounds, 'stages': stage_stats,
                         'assumption': 'The other four components of v are zero.'})
    assert pairings == 53875 and terms == 296

    full_screen = packet['full_modular_screen']
    sub_screen = packet['coordinate_divisible_modular_screen']
    assert full_screen['prime'] == sub_screen['prime'] == 1009
    assert full_screen['isolated_square_indices_mod_prime'] == sub_screen['isolated_square_indices_mod_prime'] == []
    assert full_screen['rank_mod_prime'] == 1759 and sub_screen['rank_mod_prime'] == 833
    for screen, key in ((full_screen, 'full75'), (sub_screen, 'coordinate_divisible25')):
        checked = review['modular_only_unresolved_screens'][key]
        assert checked['rank'] == screen['rank_mod_prime'] and checked['square_indices'] == []
        assert checked['rows'] == screen['active_rows'] and checked['columns'] == screen['columns']
    assert [(a['id'], a['status']) for a in packet['attempts']] == [
        ('full75', 'unresolved'), ('coordinate_divisible25', 'unresolved'),
        ('five_single_component_families', 'exactly_excluded')]

    comparison = []
    for old_dir, params, raw, compact, quotient, degree in (
        ('cyclic-fano-polar-family', 5, 25, 0, 15, 5),
        ('cyclic-fano-linear-polars', 25, 85, 10, 75, 6)):
        old_path = ROOT / 'results' / old_dir / 'packet.json'
        old_review_path = old_path.parent / 'independent-validation.json'
        old, old_review = load(old_path), load(old_review_path)
        assert old['status'] == old_review['status'] == 'PASS'
        assert old_review['packet_lf_sha256'] == sha(old_path)
        assert old['degree'] == degree and len(old['basis']) == params
        if degree == 5:
            assert old['complete_corrections_per_E'] == raw and old['quotient_dimension'] == quotient
            assert old_review['all_corrections_have_zero_even_projection']
        else:
            assert old_review['complete_Koszul_fields'] == raw
            assert old_review['surviving_correction_generator_types'] == compact
            assert old_review['quotient_columns'] == quotient
        for path in (old_path, old_review_path):
            bindings[path.relative_to(ROOT).as_posix()] = sha(path)
        comparison.append(dict(degree=degree, parameters=params, raw_Koszul=raw,
                               surviving_types=compact, quotient_directions=quotient))
    comparison.append(dict(degree=7, parameters=75, raw_Koszul=230,
                           surviving_types=55, quotient_directions=246))
    return dict(schema='cyclic-fano-quadratic-polars-plot-v1',
                instance='cyclic-triple-fano', discussion_number=112,
                sha256_policy='File bytes with CRLF normalized to LF',
                source_sha256=bindings, plot_source_sha256=sha(Path(__file__)),
                exact_coefficient_digest=packet['full_map']['coefficient_sha256'],
                full_map=display_map(exact, range(6975), 4, 7),
                X0_stage_maps=chosen_maps, families=families,
                monomial_powers=monomials, comparison=comparison,
                full_modular_screen=full_screen, coordinate_divisible_modular_screen=sub_screen,
                attempts=packet['attempts'], checked_square_pairings=pairings,
                checked_dual_terms=terms, limits=packet['limits'])


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    fig.savefig(path.with_suffix('.png'), dpi=160, facecolor=PAPER)
    svg = path.with_suffix('.svg')
    fig.savefig(svg, facecolor=PAPER, metadata={'Date': None})
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines()) + '\n',
                   encoding='utf-8', newline='\n')
    plt.close(fig)


def monomial_label(powers):
    names = ('X_0', 'X_1', 'Z', 'Y_0', 'Y_1', 'Y_2')
    return '$' + ''.join(names[i] + ('^{' + str(p) + '}' if p != 1 else '')
                         for i, p in enumerate(powers) if p) + '$'


def box(fig, x, y, w, h, title, body, color):
    fig.add_artist(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.010',
                                 transform=fig.transFigure, facecolor='#F0F1EA',
                                 edgecolor='#CED6D2', linewidth=1))
    fig.text(x + .012, y + h - .040, title, fontsize=16, color=color, weight='bold')
    fig.text(x + .012, y + h - .075, body, fontsize=13, color=INK, va='top', linespacing=1.5)


def feature(data):
    fig = plt.figure(figsize=(14, 9.3), facecolor=PAPER)
    fig.text(.055, .947, 'Quadratic polars: five subfamilies excluded', fontsize=25, weight='bold')
    fig.text(.055, .906, r'cyclic-triple-fano · discussion #112   |   degree 7 denominators $E=f\,\partial_i\Delta$', fontsize=14, color=MUTED)
    fig.text(.055, .850, r'Each row is a separate problem: $v=f\,\partial_i$; the other four components are zero.',
             fontsize=16, weight='bold')
    ax = fig.add_axes([.182, .438, .61, .326])
    rounds = np.array([f['elimination_rounds'] for f in data['families']])
    ax.imshow(rounds, cmap=ListedColormap(['#C5E0DA', '#DFD5ED']), vmin=1, vmax=2, aspect='auto')
    for i in range(5):
        for j in range(15):
            ax.text(j, i, str(rounds[i, j]), ha='center', va='center', fontsize=16,
                    color=TEAL if rounds[i, j] == 1 else PURPLE, weight='bold')
    ax.set_yticks(range(5), [r'$v=f\,\partial_{' + name[0] + '_' + name[1] + '}$' for name in NAMES], fontsize=17)
    ax.set_xticks(range(15), [monomial_label(m) for m in data['monomial_powers']], rotation=40,
                  ha='right', fontsize=13)
    ax.set_xticks(np.arange(-.5, 15, 1), minor=True)
    ax.set_yticks(np.arange(-.5, 5, 1), minor=True)
    ax.grid(which='minor', color=PAPER, linewidth=2)
    ax.tick_params(which='both', length=0)
    ax.set_title('Coefficient of each monomial in f: elimination round', loc='left', fontsize=15, pad=17)
    for spine in ax.spines.values():
        spine.set_visible(False)
    for i in range(5):
        fig.text(.816, .729 - .0652 * i, '15 → 10 → 0', fontsize=17, color=TEAL, weight='bold')
    fig.text(.812, .789, 'Parameters left', fontsize=13, color=MUTED)
    fig.text(.055, .357, '1  Five square-monomial coefficients vanish.', fontsize=15, color=TEAL)
    fig.text(.510, .357, '2  Rebuild; ten cross-term coefficients vanish.', fontsize=15, color=PURPLE)
    fig.text(.055, .314, r'75 exact identities of the form $a_k^2=\ell_k(\mathrm{equations})$ across these five separate families.',
             fontsize=14, color=INK)
    box(fig, .065, .133, .410, .130, 'Full mixed-component family: OPEN',
        '75 parameters. No individual squares found modulo 1009.\nThis modular screen does not exclude the family.', CORAL)
    box(fig, .515, .133, .410, .130, 'Coordinate-divisible family: OPEN',
        r'$v_i=x_i\ell_i$: 25 parameters; same unresolved screen.' + '\nBoth searches retained their recorded 120 s bounds.', CORAL)
    fig.text(.055, .082, 'Every component proof retains 55 correction types and all 246 quotient directions.',
             fontsize=14, weight='bold')
    fig.text(.055, .045, 'Separate exclusions do not exclude sums, unions of supports, or all degree 7 denominators. No certificate is claimed.',
             fontsize=12, color=MUTED)
    save(fig, 'cyclic-fano-quadratic-polars')


def occupancy(ax, data, title, fontsize=15):
    grid = np.zeros(data['binned_shape'], dtype=np.uint8)
    bins = np.asarray(data['occupied_bins'])
    grid[bins[:, 0], bins[:, 1]] = 1
    nr, nc = data['shape']
    br, bc = data['bin_size_rows_columns']
    ax.imshow(grid, cmap=ListedColormap([PAPER, TEAL]), interpolation='nearest',
              aspect='auto', extent=(-.5, grid.shape[1]*bc-.5, grid.shape[0]*br-.5, -.5), rasterized=True)
    ax.set(xlim=(-.5, nc-.5), ylim=(nr-.5, -.5))
    ax.axvline(data['pure_columns'] - .5, color=CORAL, linewidth=1.2)
    ax.set_title(title, loc='left', fontsize=fontsize, pad=12, weight='bold')
    ax.tick_params(labelsize=10, colors=MUTED)
    ax.set(xlabel='ordered coefficient-map columns', ylabel='active coefficient rows')
    for spine in ax.spines.values():
        spine.set_color('#CED6D2')


def maps(data):
    fig = plt.figure(figsize=(16, 10), facecolor=PAPER)
    fig.text(.055, .946, 'The actual maps: more corrections, conditional progress', fontsize=25, weight='bold')
    fig.text(.055, .904, 'cyclic-triple-fano · discussion #112   |   exact rational coefficients; occupancy colors carry no spectral meaning',
             fontsize=14, color=MUTED)
    ax = fig.add_axes([.065, .460, .470, .355])
    occupancy(ax, data['full_map'], 'Full map: 1,799 × 6,975; unresolved')
    ax.set_xticks([0, 2850, 5000, 6974])
    fig.text(.065, .394, '2,850 parameter quadratics  |  4,125 parameter × correction terms', fontsize=12)
    fig.text(.065, .364, '21 all-zero rows omitted from 1,820. Each pixel-bin covers 4 rows × 7 columns.', fontsize=12, color=MUTED)
    fig.text(.065, .334, 'Rank 1,759 is modulo 1009 only; no characteristic-zero rank is asserted.', fontsize=12, color=CORAL)
    for i, (x, stage_map, title) in enumerate(zip(
            (.610, .815), data['X0_stage_maps'], ('X₀ component: round 1', 'X₀ component: rebuilt'))):
        stage_ax = fig.add_axes([x, .577, .145, .236])
        occupancy(stage_ax, stage_map, title, fontsize=13)
        stage_ax.set_ylabel('active rows' if i == 0 else '')
        stage_ax.set_xlabel('columns', fontsize=11)
        s = data['families'][0]['stages'][i]
        fig.text(x, .518, f"{s['active_rows']:,} × {s['columns']}; exact rank {s['rank']}", fontsize=11)
        fig.text(x, .488, '3-row × 2-column bins', fontsize=11, color=MUTED)
    fig.text(.610, .433, 'These maps assume all other components are zero.', fontsize=13, weight='bold')
    fig.text(.610, .397, 'Round 1: 120 pure + 825 mixed columns.', fontsize=12)
    fig.text(.610, .366, 'Round 2: 55 pure + 550 mixed columns; all 55 types retained.', fontsize=12)
    fig.text(.610, .335, 'Coral lines separate pure quadratic and mixed columns.', fontsize=12, color=CORAL)

    table_ax = fig.add_axes([.055, .103, .500, .170])
    table_ax.axis('off')
    headers = ['Denominator degree', 'Parameters', 'Raw Koszul', 'Surviving types', 'Quotients']
    cells = [[str(row[key]) for key in ('degree', 'parameters', 'raw_Koszul', 'surviving_types', 'quotient_directions')]
             for row in data['comparison']]
    table = table_ax.table(cellText=cells, colLabels=headers, loc='center', cellLoc='center',
                           colWidths=[.26, .17, .18, .22, .17])
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 1.8)
    for (i, j), cell in table.get_celld().items():
        cell.set_edgecolor(PAPER)
        cell.set_facecolor('#C5E0DA' if i == 0 else '#EDF1EA')
        cell.get_text().set_color(INK)
        if i == 0:
            cell.get_text().set_fontweight('bold')
    fig.text(.610, .247, 'Degree 7 adds five new correction types.', fontsize=16, weight='bold')
    fig.text(.610, .218, '55 = 50 linear multiples of earlier base-pair types\n       + 5 mixed types involving the reflected coordinate.',
             fontsize=13, linespacing=1.5, va='top')
    fig.text(.610, .120, 'Counts describe complete spaces, not ranks.\nFull-family exclusion is still unresolved at degree 7.',
             fontsize=13, color=CORAL, linespacing=1.4)
    fig.text(.055, .044, 'Every bin is occupied iff it contains an exact nonzero. Row/column order, bin coordinates, source hashes and all 75 dual checks are saved in plot-data.json.',
             fontsize=11, color=MUTED)
    save(fig, 'cyclic-fano-quadratic-polars-maps')


def main():
    assert __debug__, 'Run without -O.'
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'text.color': INK,
                         'axes.labelcolor': INK, 'axes.titlecolor': INK,
                         'svg.hashsalt': 'cyclic-fano-quadratic-polars-v1'})
    data = check_data()
    feature(data)
    maps(data)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'plot-data.json').write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8', newline='\n')
    assert all(sha(ROOT / name) == digest for name, digest in data['source_sha256'].items())
    print(json.dumps({'status': 'PASS', 'source_bindings': len(data['source_sha256']),
                      'square_dual_pairings': data['checked_square_pairings'],
                      'full_map_nonzero_coefficients': data['full_map']['nonzero_coefficients'],
                      'excluded_separate_component_families': 5,
                      'full_75_parameter_family': 'unresolved',
                      'figures': ['cyclic-fano-quadratic-polars.png', 'cyclic-fano-quadratic-polars-maps.png']}))


if __name__ == '__main__':
    main()
