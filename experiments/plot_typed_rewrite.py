"""Actual typed Macaulay operator, matched cache comparison, and search history.

Matrix sorting is only a visual permutation. Both timed modes use the same
original input order. --check reconstructs exact data without plotting packages.
"""
from collections import Counter
from fractions import Fraction as Q
import argparse
import hashlib
import json
import typed_rewrite_search as s

h = s.h
OUT = h.OUT


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def check_goal_geometry(g, eq, meta, record, projected_only=False):
    """Replay plotted maps and powers; ranks were checked in both source reports.

    Avoid repeating the full quartic elimination merely to draw row counts.
    Every displayed positive membership has its own coefficientwise identity.
    """
    weights = meta['weights']
    degree = record['degree']
    labels, rows, types, selected = g.maps(eq, weights, len(weights), degree,
                                         record['target_character'])
    assert record['full_rows'] == len(rows)
    assert record['typed_rows'] == len(selected)
    assert record['full_nonzeros'] == sum(map(len, rows))
    assert record['typed_nonzeros'] == sum(len(rows[i]) for i in selected)
    assert record['selected_indices'] == selected
    assert record['type_counts'] == [[list(t), n] for t, n in sorted(Counter(types).items())]
    assert record['matrix_sha256'] == s.sha({'labels': [[j, list(m)] for j, m in labels],
                                           'rows': [h.cert.encode(p) for p in rows]})
    all_labels = set(labels)
    typed_labels = {labels[i] for i in selected}
    negative_member = None
    for answer in record['queries']:
        local = answer['local']
        assert local in meta['target_local_indices']
        assert answer['raw'] == meta['system']['basis_indices'][local]
        assert answer['power'] == degree
        target = {(local,) * degree: Q(1)}
        fields = [('products', typed_labels)] if projected_only else [
            ('full_products', all_labels), ('typed_products', typed_labels)]
        if answer['found']:
            for field, allowed in fields:
                assert all((j, tuple(mon)) in allowed for j, mon, _ in answer[field])
                assert h.e.expand_products(eq, answer[field]) == target
        else:
            assert all(answer[field] is None for field, _ in fields)
            if negative_member is None:
                negative_member, _, _ = h.cert.reduce_span([rows[i] for i in selected])
            assert negative_member(target) is None


def data():
    comparison = read(s.OUT / 'validation.json')
    other = read(s.OUT / 'independent-validation.json')
    assert comparison['status'] == other['status'] == 'PASS'
    assert comparison['records'] == other['records'] and comparison['matches'] == other['matches']
    assert comparison.get('cache_selftest') == other.get('cache_selftest')
    plan = read(s.OUT / 'plan.json')
    number = plan['cases'][0]['number']
    matrix = s.matrix_data(h.Model(), number)
    from check_degree7_triples import IndependentModel
    independent = s.matrix_data(IndependentModel(), number)
    assert matrix == independent
    rows, columns = matrix['row_types'], matrix['column_types']
    row_order = sorted(range(len(rows)), key=lambda i: (rows[i], i))
    column_order = sorted(range(len(columns)), key=lambda i: (columns[i], i))
    ri, ci = {j: i for i, j in enumerate(row_order)}, {j: i for i, j in enumerate(column_order)}
    transformed = [[ri[i], ci[j], value] for i, j, value in matrix['entries']]
    assert all(rows[i] == columns[j] for i, j, _ in matrix['entries'])
    assert sorted([[row_order[i], column_order[j], c] for i, j, c in transformed]) == sorted(matrix['entries'])
    blocks = []
    for typ in sorted({tuple(t) for t in rows}):
        rr = [ri[i] for i, t in enumerate(rows) if tuple(t) == typ]
        cc = [ci[j] for j, t in enumerate(columns) if tuple(t) == typ]
        assert rr and cc
        assert max(rr) - min(rr) + 1 == len(rr) and max(cc) - min(cc) + 1 == len(cc)
        blocks.append({'type': list(typ), 'row_start': min(rr), 'row_count': len(rr),
                       'column_start': min(cc), 'column_count': len(cc)})
    records = []
    attempts = read(s.OUT / 'attempts.json')
    for report, attempt in zip(comparison['records'], attempts):
        job = {k: attempt[k] for k in ['number', 'mode', 'replicate']}
        assert all(report['job'][k] == job[k] for k in job)
        packet_path = s.OUT / (s.basename(**job) + '.json.gz')
        packet = h.q.load(packet_path) if packet_path.exists() else None
        if packet is not None and report.get('rows', 0):
            assert packet['statistics'] == report['statistics']
            assert packet['basis_sha256'] == report['basis_sha256']
            assert packet['elimination_seconds'] == report['elimination_seconds']
            assert packet['rows_processed'] == report['rows']
            assert packet['completed'] == report['completed']
            if job['mode'] == 'typed':
                assert len(packet['applications']) == report['statistics'].get('cache_hits', 0)
        if 'wall_seconds' in report:
            assert report['wall_seconds'] == attempt['wall_seconds']
        records.append({**report, 'wall_seconds': attempt['wall_seconds'],
                        'attempt_status': attempt['status']})
    phase = 'follow' if (OUT / 'follow-validation.json').exists() else 'baseline'
    report_path = OUT / f'{phase}-validation.json'
    report = read(report_path)
    independent_report = read(OUT / f'{phase}-independent-validation.json')
    assert report['status'] == independent_report['status'] == 'PASS'
    assert report['families'] == independent_report['families']
    baseline = read(OUT / 'baseline-validation.json')
    survivors = [r for r in baseline['families'] if not r['excluded']]
    by_number = {r['batch_number']: r for r in report['families']}
    families = []
    for r in survivors:
        f = by_number[r['batch_number']]
        charts = [c for cycle in f.get('cycles', []) for c in cycle['charts']]
        families.append({'number': r['batch_number'], 'initial': len(r['basis_indices']),
                         'after_squares': len(r['remaining']), 'remaining': len(f['remaining']),
                         'excluded': f['excluded'], 'charts': charts,
                         'attempt': f.get('attempt')})
    excluded = sum(r['excluded'] for r in report['families'])
    goal_cases = None
    goal_sources = []
    goal_root = OUT / 'goal-powers'
    goal_attempts = []
    goal_setups = {}
    if (goal_root / 'validation.json').exists():
        import typed_goal_powers as g
        goals = read(goal_root / 'validation.json')
        independent_goals = read(goal_root / 'independent-validation.json')
        assert goals['status'] == independent_goals['status'] == 'PASS'
        assert goals['cases'] == independent_goals['cases']
        assert goals['checks'] == independent_goals['checks']
        goal_cases = goals['cases']
        goal_attempts = read(goal_root / 'attempts.json')
        for case in goal_cases:
            if case.get('no_packet'):
                continue
            _, meta, eq, _ = g.setup(h.Model(), case['family'])
            goal_setups[case['family']] = (meta, eq)
            goal_sources.append(meta)
            packet = h.q.load(goal_root / f"family-{case['family']:03d}.json.gz")
            assert case['records'] == packet['records']
            for record in case['records']:
                check_goal_geometry(g, eq, meta, record)
    quartic_root = OUT / 'goal-quartics'
    quartic_records = None
    if (quartic_root / 'validation.json').exists():
        import typed_goal_quartics as gq
        quartics = read(quartic_root / 'validation.json')
        independent_quartics = read(quartic_root / 'independent-validation.json')
        assert quartics['status'] == independent_quartics['status'] == 'PASS'
        assert quartics['records'] == independent_quartics['records']
        assert quartics['checks'] == independent_quartics['checks']
        quartic_records = quartics['records']
        for record in quartic_records:
            if record.get('no_packet'):
                continue
            if record['family'] not in goal_setups:
                _, meta, eq, _ = gq.g.setup(h.Model(), record['family'])
                goal_setups[record['family']] = (meta, eq)
            meta, eq = goal_setups[record['family']]
            assert meta == record['metadata']
            packet = h.q.load(quartic_root / f"family-{record['family']:03d}.json.gz")
            assert packet['record'] == record
            check_goal_geometry(gq.g, eq, meta, record, projected_only=True)
            assert record['full_rank'] is None and record['full_elimination_performed'] is False
    supplement = None
    supplement_root = OUT / 't100'
    hashes = {}
    if (supplement_root / 'independent-closure-validation.json').exists():
        supplement = {}
        for name in ['validation', 'blocks-validation', 'closure-validation']:
            a = read(supplement_root / (name + '.json'))
            b = read(supplement_root / ('independent-' + name + '.json'))
            clean = lambda r: {k: v for k, v in r.items() if k not in ['seconds', 'independent_physical_polynomials']}
            assert a['status'] == b['status'] == 'PASS'
            assert clean(a) == clean(b)
            supplement[name] = clean(a)
            for prefix, value in [('', a), ('independent-', b)]:
                hashes['t100/' + prefix + name + '.json'] = s.sha(clean(value))
        packet = h.q.load(supplement_root / 'global.json.gz')
        supplement['initial_directions'] = len(packet['system']['basis_indices'])
        assert len(packet['baseline']) == supplement['validation']['baseline_relations']
        assert len(packet['selected_new']) == supplement['validation']['additional_relations']
        assert packet['completed'] == supplement['validation']['completed']
        assert len(packet['completed_multipliers']) == supplement['validation']['multiplier_blocks']
        closure = h.q.load(supplement_root / 'closure.json.gz')
        assert closure['remaining'] == supplement['closure-validation']['remaining']
        supplement['attempt'] = read(supplement_root / 'attempt.json')
        supplement['closure_attempt'] = read(supplement_root / 'closure-attempt.json')
    for root in [OUT, s.OUT, goal_root, quartic_root, supplement_root]:
        for path in sorted(root.glob('*.json.gz')):
            hashes[path.relative_to(OUT).as_posix()] = h.digest(path)
        for path in sorted(root.glob('*.json')):
            if ('plan' in path.stem or 'attempt' in path.stem) and 'validation' not in path.stem:
                hashes[path.relative_to(OUT).as_posix()] = s.sha(read(path))
    visual = {'matrix': {'family': number, 'rows': len(rows), 'columns': len(columns),
        'nonzero_entries': len(matrix['entries']), 'matrix_sha256': matrix['matrix_sha256'],
        'permuted_entries_sha256': s.sha(sorted(transformed)), 'types': blocks,
        'row_permutation': row_order, 'column_permutation': column_order},
        'records': records, 'matches': comparison['matches'], 'comparison_plan': plan,
        'cache_selftest': comparison.get('cache_selftest'),
        'baseline_excluded': sum(r['excluded'] for r in baseline['families']),
        'excluded': excluded, 'selected_union': 680 + excluded,
        'families': families, 'goal_cases': goal_cases, 'goal_sources': goal_sources,
        'goal_attempts': goal_attempts, 'quartic_records': quartic_records, 't100': supplement,
        'source_hashes': hashes,
        'hash_format': 'SHA256: gzip bytes; sorted compact canonical JSON plans and attempts.',
        'scope': 'Actual coefficient operator and exact visual permutation. Cache telemetry is exploratory; no grammar reduction or speed theorem.'}
    return visual, matrix, transformed


def save(fig, name, plt):
    fig.savefig(OUT / (name + '.png'), dpi=190)
    fig.savefig(OUT / (name + '.svg'), metadata={'Date': None})
    plt.close(fig)
    path = OUT / (name + '.svg')
    path.write_text('\n'.join(line.rstrip() for line in path.read_text(encoding='utf-8').splitlines()) + '\n', encoding='utf-8')


def figures(d, matrix, transformed):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    plt.rcParams.update({'font.size': 11, 'svg.fonttype': 'none', 'svg.hashsalt': 'typed-rewrite'})
    blue, gold, green, red = '#286b9b', '#b87827', '#2e8175', '#a7435c'
    info = d['matrix']
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 7.2), layout='constrained')
    for ax, entries, title in zip(axes, [matrix['entries'], transformed],
                                   ['Original input and monomial order', 'Rows and columns ordered by degree and character']):
        for positive, color in [(False, blue), (True, gold)]:
            points = [(j, i) for i, j, c in entries if (Q(c) > 0) == positive]
            if points:
                xx, yy = zip(*points)
                ax.scatter(xx, yy, s=.7, marker='s', color=color, linewidths=0, rasterized=True)
        ax.set(xlim=(-.5, info['columns'] - .5), ylim=(info['rows'] - .5, -.5),
               xlabel='Coefficient-monomial column', ylabel='Equation × allowed multiplier row', title=title)
    for block in info['types']:
        axes[1].add_patch(Rectangle((block['column_start'] - .5, block['row_start'] - .5),
            block['column_count'], block['row_count'], facecolor='none', edgecolor='#888888', linewidth=.6))
    fig.suptitle(f"T{info['family']}: the same exact Macaulay operator, viewed through its conserved types", fontsize=14)
    fig.supxlabel(f"{info['rows']} rows × {info['columns']} columns; {info['nonzero_entries']} nonzero coefficients. Blue negative, gold positive. Every cross-type entry is zero. Sorting is visual only.", fontsize=10)
    save(fig, 'typed-operator', plt)

    records = d['records']
    fig, axes = plt.subplots(1, 3, figsize=(14.5, 7.2), layout='constrained',
                             gridspec_kw={'width_ratios': [1.2, 1.2, 1]})
    labels = [f"T{r['job']['number']} {r['job']['mode']} #{r['job']['replicate'] + 1}\n"
              f"{r.get('rows', 0)}/{r.get('requested_rows', '?')} rows · {r['attempt_status']}" for r in records]
    colors = [blue if r['job']['mode'] == 'untyped' else gold for r in records]
    for k, (field, label) in enumerate([('wall_seconds', 'Total process time (seconds)'),
                                        ('elimination_steps', 'Recorded elimination steps')]):
        values = [r.get('statistics', {}).get(field, 0) if k else r.get(field, 0) for r in records]
        axes[k].barh(range(len(records)), values, color=colors, height=.65)
        axes[k].set(yticks=range(len(records)), yticklabels=labels if k == 0 else [], xlabel=label,
                    title='Every alternating run is shown' if k == 0 else 'Arithmetic work and overhead are distinct')
        axes[k].invert_yaxis()
        axes[k].tick_params(axis='y', labelsize=9)
        axes[k].spines[['top', 'right']].set_visible(False)
        if k == 0:
            measured = [(r['elimination_seconds'], i) for i, r in enumerate(records)
                        if 'elimination_seconds' in r]
            if measured:
                xx, yy = zip(*measured)
                axes[k].scatter(xx, yy, color='#242424', s=18, marker='o',
                                label='Elimination timer only', zorder=3)
                axes[k].legend(loc='upper right', fontsize=8, frameon=True)
        for i, r in enumerate(records):
            if k and field not in r.get('statistics', {}):
                axes[k].text(0, i, ' not recorded', va='center', color=red, fontsize=9)
            elif not r.get('completed', False):
                axes[k].text(values[i], i, ' incomplete', va='center', color=red, fontsize=9)
    ax = axes[2]
    ax.axis('off')
    typed = [r for r in records if r['job']['mode'] == 'typed']
    cells = [[f"T{r['job']['number']} #{r['job']['replicate'] + 1}" + ('' if r.get('completed') else '*'),
              r['statistics'].get('cache_hits', 0) if 'statistics' in r else '—',
              r['statistics'].get('peak_cache_terms', 0) if 'statistics' in r else '—'] for r in typed]
    ax.set_title('Bounded certified-residual cache')
    table = ax.table(cellText=cells, colLabels=['Run', 'Hits', 'Peak terms'],
                     cellLoc='center', bbox=[0, .49, 1, .4])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    for key, cell in table.get_celld().items():
        cell.set_edgecolor('#d9dcdf')
        if key[0] == 0:
            cell.set_facecolor('#edf2f6')
    matches = d['matches']
    checked = sum(m.get('equal_coefficient_basis', False) for m in matches)
    ax.text(0, .37, f"{checked}/{len(matches)} families: all four completed\ncoefficient bases match exactly.\n\n* Partial run; counts refer to its prefix.\nUnequal completed work has no\nmatched runtime comparison.\n\nCap: 256 entries / 50,000 terms.\nCached identities add no constraints.",
            va='top', fontsize=10, linespacing=1.5)
    fig.suptitle('Typed zero rewrites versus direct sparse elimination', fontsize=15)
    fig.supxlabel('Two deterministic families, two alternating repetitions per mode. Blue: control. Gold: typed cache. Partial runs are not equal-work timing comparisons; no speed theorem is claimed.', fontsize=9.5)
    save(fig, 'typed-comparison', plt)

    rows = d['families']
    fig, axes = plt.subplots(1, 2, figsize=(13, 6.8), layout='constrained')
    ax = axes[0]
    for i, r in enumerate(rows):
        ax.plot([r['initial'], r['after_squares'], r['remaining']], [i, i, i], color='#c0c0bc', linewidth=2)
        ax.scatter(r['initial'], i, marker='|', s=150, color='#888888')
        ax.scatter(r['after_squares'], i, s=45, color=blue)
        ax.scatter(r['remaining'], i, marker='D', s=36, color=green if r['excluded'] else red, zorder=3)
    ax.set(yticks=range(len(rows)), yticklabels=[f"T{r['number']}" for r in rows],
           xlim=(max(r['initial'] for r in rows) + 1, 0), xlabel='Retained denominator directions',
           title='Baseline survivors and subsequent exact reductions')
    ax.invert_yaxis()
    ax.spines[['top', 'right']].set_visible(False)
    ax = axes[1]
    for i, r in enumerate(rows):
        success = sum(c['excluded'] for c in r['charts'])
        failure = len(r['charts']) - success
        ax.barh(i, success, color=green)
        ax.barh(i, failure, left=success, color=red)
        if not r['charts']:
            ax.text(.1, i, 'no chart attempted', va='center', fontsize=9, color='#666666')
    ax.set(yticks=range(len(rows)), yticklabels=[f"T{r['number']}" for r in rows],
           xlabel='Shared-numerator chart attempts', title='Green: contradicted; red: unresolved attempt')
    ax.invert_yaxis()
    ax.spines[['top', 'right']].set_visible(False)
    fig.suptitle(f"Fresh X0/Y1 batch: {d['baseline_excluded']}/132 after squares; {d['excluded']}/132 after follow-up", fontsize=14)
    fig.supxlabel('Left: gray initial, blue after squares, diamond final (green excluded; red unresolved). Later family exclusions do not establish a cache advantage. Holdout remains unsolved.', fontsize=9.5)
    save(fig, 'typed-family-search', plt)

    if d['goal_cases'] is not None:
        queries = [(case['family'], record, 'both') for case in d['goal_cases']
                   for record in case.get('records', [])]
        queries += [(record['family'], record, 'projected') for record in d['quartic_records'] or []
                    if not record.get('no_packet')]
        queries.sort(key=lambda item: (item[0], item[1]['degree'], item[2]))
        fig, axes = plt.subplots(1, 2, figsize=(13, 6), layout='constrained',
                                 gridspec_kw={'width_ratios': [1.2, 1]})
        ax = axes[0]
        for i, (number, record, kind) in enumerate(queries):
            ax.barh(i, record['full_rows'], color='#dce0e3', height=.6)
            ax.barh(i, record['typed_rows'], color=gold, height=.6)
            ax.text(record['full_rows'] + 2, i,
                    f"{record['typed_rows']} / {record['full_rows']} rows", va='center', fontsize=10)
        largest = max([r['full_rows'] for _, r, _ in queries] + [1])
        ax.set(yticks=range(len(queries)),
               yticklabels=[f"T{n}, degree {r['degree']}" + (' *' if kind == 'projected' else '')
                            for n, r, kind in queries],
               xlim=(0, largest * 1.45), xlabel='Macaulay generator-multiple rows',
               title='Keep only rows of the target degree and character')
        ax.invert_yaxis()
        ax.spines[['top', 'right']].set_visible(False)
        ax = axes[1]
        ax.axis('off')
        cells = [[f'T{n}', str(r['degree']), str(answer['raw']),
                  ('Found in both' if answer['found'] else 'In neither span') if kind == 'both' else
                  ('Found (projected only)' if answer['found'] else 'Not found (projected only)')]
                 for n, r, kind in queries for answer in r['queries']]
        if not cells:
            cells = [['—', '—', '—', 'No completed query']]
        table = ax.table(cellText=cells, colLabels=['Family', 'Power', 'Raw index', 'Exact membership'],
                         cellLoc='center', colWidths=[.14, .14, .19, .53], bbox=[0, .43, 1, .43])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        for key, cell in table.get_celld().items():
            cell.set_edgecolor('#d9dcdf')
            if key[0] == 0:
                cell.set_facecolor('#edf2f6')
        ax.set_title('The same finite membership questions, exactly')
        incomplete = [a['family'] for a in d['goal_attempts'] if a['status'] != 'completed']
        incomplete_label = ', '.join('T' + str(n) for n in incomplete) or 'none'
        ax.text(.02, .29, 'Gray: all rows. Gold: target-type rows.\nEvery omitted row has zero target component.\n'
                '* Projected-only continuation; no full rank.\n'
                f'Incomplete original full comparisons: {incomplete_label}.\n\n'
                'This separate projection is justified by grading;\nits later timing is not a prospective comparison.',
                va='top', fontsize=10, linespacing=1.5)
        fig.suptitle('Typed coordinate-power queries reduce the relevant operator', fontsize=15)
        fig.supxlabel('Same necessary subideal from the retained first typed run, possibly a partial prefix. No anchor parameters are set to zero. Fewer rows alone do not establish a runtime speedup.', fontsize=9.5)
        save(fig, 'typed-goal-powers', plt)

    if d['t100'] is not None:
        t = d['t100']
        relation, blocks, closure = (t[k] for k in ['validation', 'blocks-validation', 'closure-validation'])
        fig, axes = plt.subplots(1, 3, figsize=(14, 5.7), layout='constrained',
                                 gridspec_kw={'width_ratios': [1, 1.3, 1.2]})
        ax = axes[0]
        ax.bar([0, 1], [relation['baseline_relations'], relation['baseline_relations'] + relation['additional_relations']],
               color=[blue, gold], width=.6)
        for x, value in enumerate([relation['baseline_relations'], relation['baseline_relations'] + relation['additional_relations']]):
            ax.text(x, value + .5, str(value), ha='center')
        ax.set(xticks=[0, 1], xticklabels=['Baseline', 'With new\nmultiplier relations'],
               ylim=(0, 34), ylabel='Selected necessary relations', title='A partial multiplier search adds relations')
        ax.spines[['top', 'right']].set_visible(False)
        ax.text(.02, .94, f"{relation['multiplier_blocks']}/{relation['requested_blocks']} blocks retained\n180-second search timed out",
                transform=ax.transAxes, va='top', fontsize=10, color=red)
        ax = axes[1]
        labels = []
        for i, block in enumerate(blocks['blocks']):
            for j, m in enumerate(block['maps']):
                k = 2 * i + j
                ax.barh(k, m['rank'], color=green)
                ax.barh(k, m['quotient_dimension'], left=m['rank'], color='#dce0e3')
                ax.text(m['codomain'] + 1, k, f"{m['rank']}/{m['codomain']}", va='center', fontsize=9)
                labels.append(f"{tuple(block['character'])}, d={m['degree']}")
                assert m['rank'] + m['quotient_dimension'] == m['codomain']
        ax.set(yticks=range(len(labels)), yticklabels=labels, xlim=(0, 153),
               xlabel='Homogeneous coefficient dimension', title='Selected pure-block maps retain cokernels')
        ax.invert_yaxis()
        ax.tick_params(axis='y', labelsize=9)
        ax.spines[['top', 'right']].set_visible(False)
        ax = axes[2]
        ax.axis('off')
        ax.set_title('One new vanishing; the family stays open')
        forced = ', '.join(str(x) for x in closure['forced_raw_ids'])
        attempts = [a for cycle in closure['cycles'] for a in cycle['charts']]
        failed = [a['raw'] for a in attempts if not a['excluded']]
        ax.text(.03, .9, f"Raw denominator coefficient {forced} vanishes.\n\n"
                f"{t['initial_directions']} → {len(closure['remaining'])} retained directions.\n\n"
                'Rebuilding gives no further pure-block zeros.\n\n'
                f"Charts {', '.join(map(str, failed))}: unresolved.\n\n"
                f"Primary batch remains {d['excluded']}/132 excluded.\nT100 remains unresolved.",
                va='top', fontsize=11, linespacing=1.5)
        fig.suptitle('T100 continuation: checked local progress without an exclusion', fontsize=15)
        fig.supxlabel('Green is map rank, gray is cokernel dimension for the selected necessary subideal. All retained identities were checked in two physical reconstructions; failed searches remain recorded.', fontsize=9.5)
        save(fig, 'typed100-continuation', plt)


def run(check=False):
    d, matrix, transformed = data()
    path = OUT / 'visual-data.json'
    if check:
        assert read(path) == d
    else:
        path.write_text(json.dumps(d, indent=2) + '\n', encoding='utf-8')
        figures(d, matrix, transformed)
    receipt = {'status': 'PASS', 'matrix_sha256': d['matrix']['matrix_sha256'],
               'exact_permutation_checked': True, 'cross_type_nonzero_entries': 0,
               'independent_physical_matrix_equal': True, 'runs': len(d['records']),
               'family_exclusions': d['excluded'], 'source_hashes': d['source_hashes']}
    (OUT / 'figure-validation.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print('PASS: exact operator permutation, type partition, matched telemetry, search histories, and source hashes')


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('Run without -O.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    run(parser.parse_args().check)
