"""Visualize checked added-character scores, actual Koszul maps, and attempts.

The --check path uses only the standard library and the exact local checkers.
It reconstructs the mathematical data and checks the saved source hashes; it
does not treat rasterized pictures as algebraic certificates.
"""
from fractions import Fraction as Q
from itertools import combinations, combinations_with_replacement
import argparse
import hashlib
import json
import added_character_homology as h


def read(name):
    return json.loads((h.OUT / name).read_text(encoding='utf-8'))


def exact_maps(number, block):
    """Build the exterior differentials directly, including their signs."""
    stage = h.q.load(h.OUT / f'baseline-{number:03d}.json.gz')['stages'][-1]
    eq = [h.cert.decode(stage['necessary'][i]['polynomial'])
          for i in block['equation_indices']]
    ids = block['ids']
    bases = [[(I, mon) for I in combinations(range(len(eq)), k)
              for mon in combinations_with_replacement(ids, 4 - 2 * k)]
             for k in range(3)]
    maps = []
    for k in (1, 2):
        index = {item: i for i, item in enumerate(bases[k - 1])}
        columns = []
        for I, mon in bases[k]:
            column = {}
            for position, generator in enumerate(I):
                for term, value in eq[generator].items():
                    key = (I[:position] + I[position + 1:], tuple(sorted(mon + term)))
                    at = index[key]
                    column[at] = column.get(at, Q(0)) + (-1) ** position * value
            columns.append({i: c for i, c in column.items() if c})
        maps.append(columns)
    result = h.kh.complex_at(eq, ids, 4)
    assert result == block['homology'][1]
    assert [len(b) for b in bases] == result['dimensions'][:3]
    assert [len(h.kh.image(m).rows) for m in maps] == result['differential_ranks'][:2]
    for column in maps[1]:
        assert not h.kh.apply(maps[0], column)
    representative = {i: Q(c) for i, c in result['h1_representatives'][0]}
    assert not h.kh.apply(maps[0], representative)
    assert h.kh.image(maps[1]).reduce(representative)
    terms = [{'generator': bases[1][i][0][0], 'monomial': list(bases[1][i][1]),
              'coefficient': str(c)} for i, c in sorted(representative.items())]
    return {'number': number, 'character': block['character'], 'ids': ids,
            'equations': [h.cert.encode(p) for p in eq],
            'dimensions': [len(b) for b in bases],
            'ranks': result['differential_ranks'][:2],
            'homology': result['homology'][:3], 'kernel_d1': result['kernel_d1'],
            'boundaries': result['boundaries_d2'],
            'representative': result['h1_representatives'][0], 'cycle_terms': terms,
            'maps': [[[[i, str(c)] for i, c in sorted(column.items())]
                      for column in columns] for columns in maps]}


def data():
    report = read('validation.json')
    other = read('independent-validation.json')
    assert report['status'] == other['status'] == 'PASS'
    assert report['families'] == other['families']
    assert report['checks'] == other['checks']
    assert report['comparison'] == other['comparison']
    assert report['excluded'] == sum(r['excluded'] for r in report['families'])
    plan = read('ranking-plan.json')
    by_number = {r['batch_number']: r for r in report['families']}
    rows, informative = [], []
    for row in plan['all_profiles']:
        number = row['number']
        p = h.q.load(h.OUT / f'profile-{number:03d}.json.gz')
        assert p['completed'] and len(p['blocks']) == 1
        b = p['blocks'][0]
        f = by_number[number]
        assert b['character'] == f['third_character']
        assert tuple(b['character']) not in h.ANCHOR
        score = b['homology'][1]['homology'][1] if b['homology'] else 0
        degree3 = b['homology'][0]['homology'][1] if b['homology'] else 0
        assert score == row['score'] == p['score'] == f['score']
        assert degree3 == p['score_degree3']
        assert bool(b['homology']) == bool(b['equation_indices'])
        group = ('high' if number in report['comparison']['high']['families'] else
                 'control' if number in report['comparison']['low_control']['families'] else 'later')
        histories = [{'before': len(c['before']), 'after_blocks': len(c['after_blocks']),
                      'charts': c['charts'], 'after': len(c['after'])} for c in f['cycles']]
        charts = [c for cycle in histories for c in cycle['charts']]
        rows.append({'number': number, 'score': score, 'degree3': degree3, 'group': group,
                     'character': b['character'], 'block_variables': len(b['ids']),
                     'block_equations': len(b['equation_indices']),
                     'empty_block': not b['equation_indices'],
                     'H0_degree3': b['homology'][0]['homology'][0] if b['homology'] else None,
                     'H0_degree4': b['homology'][1]['homology'][0] if b['homology'] else None,
                     'initial': len(f['basis_indices']), 'after_squares': len(f['baseline_remaining']),
                     'final': len(f['remaining']), 'excluded': f['excluded'],
                     'attempt': f['attempt'], 'history': histories,
                     'contradicted_charts': sum(c['excluded'] for c in charts),
                     'unresolved_charts': sum(not c['excluded'] for c in charts)})
        if score:
            informative.append((number, b))
    chosen = exact_maps(*informative[0]) if informative else None
    contrast = []
    if chosen is not None:
        first = next(r for r in rows if r['number'] == chosen['number'])
        candidates = [first]
        same_h1 = [r for r in rows if r['score'] == first['score']
                   and r['H0_degree4'] != first['H0_degree4'] and not r['empty_block']]
        zero_h1 = [r for r in rows if r['score'] == 0 and r['H0_degree4'] == 0
                   and not r['empty_block']]
        if same_h1:
            candidates.append(same_h1[0])
        if zero_h1:
            candidates.append(zero_h1[0])
        contrast = [{key: r[key] for key in ('number', 'score', 'H0_degree3', 'H0_degree4')}
                    for r in candidates]
    hashes = {p.name: h.digest(p) for p in sorted(h.OUT.glob('*.json.gz'))}
    for pattern in ('*-plan.json', '*-attempts.json'):
        for p in sorted(h.OUT.glob(pattern)):
            value = json.loads(p.read_text(encoding='utf-8'))
            hashes[p.name] = hashlib.sha256(json.dumps(value, sort_keys=True,
                separators=(',', ':')).encode('utf-8')).hexdigest()
    return {'block_scope': 'Subideal generated by the selected pure-character necessary rows; not asserted to be the full pure elimination ideal.',
            'excluded': report['excluded'], 'baseline_excluded': report['baseline_excluded'],
            'selected_union': 548 + report['excluded'], 'selection_size': len(report['families']),
            'comparison': report['comparison'],
            'comparison_checkpoint_excluded': report['comparison_checkpoint_excluded'],
            'comparison_is_informative': report['comparison_is_informative'],
            'families': rows, 'actual_complex': chosen, 'H0_contrast': contrast,
            'hash_format': 'SHA256: gzip files as bytes; JSON plans and attempts as sorted compact JSON.',
            'hashes': hashes}


def save(fig, name, plt):
    fig.savefig(h.OUT / (name + '.png'), dpi=180)
    fig.savefig(h.OUT / (name + '.svg'), metadata={'Date': None})
    plt.close(fig)
    path = h.OUT / (name + '.svg')
    path.write_text('\n'.join(line.rstrip() for line in path.read_text(encoding='utf-8').splitlines())
                    + '\n', encoding='utf-8')


def figures(d):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap, BoundaryNorm
    import numpy as np
    plt.rcParams.update({'font.size': 11, 'svg.fonttype': 'none',
                         'svg.hashsalt': 'added-character-homology'})
    rows = d['families']
    colors = {'high': '#286b9b', 'control': '#b87827', 'later': '#7b638c'}
    fig, axes = plt.subplots(1, 2, figsize=(13, 7.2), layout='constrained',
                             gridspec_kw={'width_ratios': [1.3, 1]})
    ax = axes[0]
    ax.barh(range(len(rows)), [r['score'] for r in rows],
            color=[colors[r['group']] for r in rows], height=.68)
    max_score = max([r['score'] for r in rows] + [1])
    for i, r in enumerate(rows):
        label = str(r['score']) + ('  (no equations)' if r['empty_block'] else '')
        ax.text(r['score'] + .025 * max_score, i, label, va='center', fontsize=9)
        if r['empty_block']:
            ax.plot(0, i, marker='o', markersize=6, markerfacecolor='white',
                    markeredgecolor=colors[r['group']], clip_on=False)
    ax.set(yticks=range(len(rows)), yticklabels=[f"A{r['number']}  [{r['group']}; {r['block_variables']}/{r['block_equations']}]" for r in rows],
           xlabel='Added-character H1 dimension at total degree four',
           title='Only the added character contributes to the score', xlim=(0, max_score * 1.32))
    ax.invert_yaxis()
    ax.spines[['top', 'right']].set_visible(False)
    ax = axes[1]
    groups = [d['comparison']['high'], d['comparison']['low_control']]
    counts = [len(g['families']) for g in groups]
    excluded = [g['excluded'] for g in groups]
    upper = max(counts + [1])
    ax.bar(['High H1', 'Low H1\ncontrol'], counts, width=.55, color='#e7e7e5')
    ax.bar(['High H1', 'Low H1\ncontrol'], excluded, width=.55,
           color=[colors['high'], colors['control']])
    for i, (n, success) in enumerate(zip(counts, excluded)):
        ax.text(i, n + .13, f'{success} / {n} excluded', ha='center')
    ax.set(ylim=(0, upper * 1.8), yticks=range(upper + 1),
           ylabel='Checked family exclusions', title='The prospective comparison is preserved')
    if excluded[0] == excluded[1] and counts[0] == counts[1]:
        comparison = 'Equal exclusion counts in the two groups.\nNo demonstrated ranking advantage.'
    else:
        comparison = 'These are observed counts in a small,\nnonrandomized comparison.'
    ax.text(.5, .86, comparison, transform=ax.transAxes, ha='center', va='center', fontsize=11)
    ax.text(.5, .25, f"{d['baseline_excluded']} / {d['selection_size']} excluded after squares\n"
            f"{d['excluded']} / {d['selection_size']} excluded after follow-up\n"
            f"{sum(r['empty_block'] for r in rows)} of {len(rows)} profiles have no added-block equations",
            transform=ax.transAxes, ha='center', va='center', fontsize=11,
            bbox={'facecolor': 'white', 'alpha': .96, 'edgecolor': '#dddddd', 'pad': 9})
    ax.spines[['top', 'right']].set_visible(False)
    fig.suptitle('Added-character homology: separating the new direction from the anchors', fontsize=15)
    fig.supxlabel('Labels show group; variables/generators. Empty blocks score zero by convention. These necessary subideals and nonrandomized groups are not matched. Holdout remains unsolved.', fontsize=9.5)
    save(fig, 'added-character-ranking', plt)

    c = d['actual_complex']
    if c is not None:
        fig, axes = plt.subplots(1, 4, figsize=(15.3, 5.6), layout='constrained',
                                 gridspec_kw={'width_ratios': [1.45, .65, 1.05, 1.03]})
        cmap = ListedColormap(['#286b9b', '#fbfbf7', '#b87827'])
        norm = BoundaryNorm([-1.5, -.5, .5, 1.5], 3)
        for k, ax in enumerate(axes[:2]):
            matrix = np.zeros((c['dimensions'][k], c['dimensions'][k + 1]))
            for j, column in enumerate(c['maps'][k]):
                for i, value in column:
                    matrix[i, j] = 1 if Q(value) > 0 else -1
            ax.imshow(matrix, cmap=cmap, norm=norm, aspect='auto', interpolation='nearest')
            ax.set(title=f"d{k + 1}: {matrix.shape[0]} × {matrix.shape[1]}\nexact rank {c['ranks'][k]}",
                   xlabel=f'K{k + 1} basis index', ylabel=f'K{k} basis index')
        ax = axes[2]
        ax.axis('off')
        k0, k1, k2 = c['dimensions']
        ax.text(0, .98, f"A{c['number']} added-character block", weight='bold', fontsize=12, va='top')
        ax.text(0, .88, f"{len(c['equations'])} quadratics in {len(c['ids'])} variables\n"
                f"Character {tuple(c['character'])}\nTotal degree four", linespacing=1.6, va='top')
        ax.text(0, .65, f'K2 ({k2}) → K1 ({k1}) → K0 ({k0})\n\nd1 d2 = 0 exactly\n\n'
                f"{c['kernel_d1']} cycles − {c['boundaries']} boundaries\n= {c['homology'][1]} homology classes",
                linespacing=1.5, va='top')
        ax.text(0, .23, 'Blue: negative   Gold: positive\nWhite: zero; magnitude hidden\nPatterns depend on basis order.',
                fontsize=10, linespacing=1.6, va='top')
        ax = axes[3]
        ax.axis('off')
        ax.text(0, .98, 'Compare H1 with the quotient H0', weight='bold', fontsize=11, va='top')
        ax.text(0, .89, 'Same H1 can hide different images', fontsize=10, va='top')
        cells = [[f"A{r['number']}", r['score'], r['H0_degree3'], r['H0_degree4']]
                 for r in d['H0_contrast']]
        table = ax.table(cellText=cells, colLabels=['Family', 'H1 d4', 'H0 d3', 'H0 d4'],
                         loc='upper center', cellLoc='center', bbox=[0, .56, 1, .25])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        for key, cell in table.get_celld().items():
            cell.set_edgecolor('#d9dcdf')
            if key[0] == 0:
                cell.set_facecolor('#edf2f6')
        ax.text(0, .47, 'H0 = 0 means the differential\nspans every monomial at that\ndegree, including coordinate\npowers.', fontsize=10, linespacing=1.5, va='top')
        ax.text(0, .23, 'Thus a block can be excluded\nwhen H1 = 0. The H1 score\nalone does not detect this.',
                fontsize=10, linespacing=1.5, va='top')
        fig.suptitle('Actual Koszul differentials of an added-character ideal', fontsize=15)
        fig.supxlabel('Selected necessary subideal; not asserted to be the full pure elimination ideal. A nonboundary cycle is checked. Its relation supplies no new denominator constraint.', fontsize=9.5)
        save(fig, 'added-character-koszul-map', plt)

    fig, axes = plt.subplots(1, 2, figsize=(13, 7.4), layout='constrained',
                             gridspec_kw={'width_ratios': [1.3, 1]})
    order = sorted(rows, key=lambda r: r['number'])
    ax = axes[0]
    for i, r in enumerate(order):
        ax.plot([r['initial'], r['after_squares'], r['final']], [i, i, i], color='#b9b9b6', linewidth=2)
        ax.scatter(r['initial'], i, marker='|', s=160, color='#8a8d92', zorder=3)
        ax.scatter(r['after_squares'], i, marker='o', s=45, color=colors[r['group']], zorder=3)
        ax.scatter(r['final'], i, marker='D', s=38,
                   color='#2e8175' if r['excluded'] else '#a7435c', zorder=4)
    ax.set(yticks=range(len(order)), yticklabels=[f"A{r['number']}" for r in order],
           xlabel='Retained denominator directions',
           title='Rebuilding can reduce a family to a checked dependency',
           xlim=(max(r['initial'] for r in order) + 1, 0))
    ax.invert_yaxis()
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([], [], marker='|', color='#8a8d92', linestyle='', label='Initial'),
                       Line2D([], [], marker='o', color='#286b9b', linestyle='', label='After squares'),
                       Line2D([], [], marker='D', color='#2e8175', linestyle='', label='Final, excluded family'),
                       Line2D([], [], marker='D', color='#a7435c', linestyle='', label='Final, unresolved family')],
              loc='lower right', frameon=True, fontsize=9)
    ax.spines[['top', 'right']].set_visible(False)
    ax = axes[1]
    solved = [r['contradicted_charts'] for r in order]
    failed = [r['unresolved_charts'] for r in order]
    ax.barh(range(len(order)), solved, color='#2e8175', label='Contradicted chart')
    ax.barh(range(len(order)), failed, left=solved, color='#a7435c', label='Unresolved chart attempt')
    for i, r in enumerate(order):
        if not solved[i] and not failed[i]:
            label = 'blocks only' if r['attempt'] is not None else 'not attempted'
            ax.text(.15, i, label, va='center', fontsize=9, color='#626469')
        elif failed[i]:
            ax.text(solved[i] + failed[i] + .15, i,
                    'family later excluded' if r['excluded'] else 'family unresolved', va='center', fontsize=9)
    ax.set(yticks=range(len(order)), yticklabels=[f"A{r['number']}" for r in order],
           xlabel='Normalized shared-numerator chart attempts', title='Keep unsuccessful attempts in the record',
           xlim=(0, max([a + b for a, b in zip(solved, failed)] + [1]) * 1.55 + 1))
    ax.invert_yaxis()
    ax.legend(loc='lower right', frameon=True, fontsize=9)
    ax.spines[['top', 'right']].set_visible(False)
    fig.suptitle('Proof routes and bounded attempts for the surviving triples', fontsize=15)
    fig.supxlabel('A final nonzero direction count can mean reduction to an already checked pair or single character. An unresolved chart is never counted as an exclusion.', fontsize=10)
    save(fig, 'added-character-search-history', plt)


def run(check=False):
    d = data()
    path = h.OUT / 'visual-data.json'
    if check:
        assert read(path.name) == d
    else:
        path.write_text(json.dumps(d, indent=2) + '\n', encoding='utf-8')
        figures(d)
    receipt = {'status': 'PASS', 'profiles': len(d['families']), 'excluded': d['excluded'],
               'added_character_only': True, 'empty_blocks': sum(r['empty_block'] for r in d['families']),
               'source_hashes': d['hashes']}
    if d['actual_complex'] is not None:
        c = d['actual_complex']
        receipt.update(complex_family=c['number'], dimensions=c['dimensions'],
                       zero_compositions_checked=len(c['maps'][1]),
                       nonboundary_representative_checked=True)
    (h.OUT / 'figure-validation.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print('PASS: added-only scores, comparison outcomes, histories, exact differentials, and source hashes')


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('Run without -O.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    run(parser.parse_args().check)
