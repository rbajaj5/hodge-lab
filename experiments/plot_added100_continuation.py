"""Checked relation-space growth and the separate A100 continuation.

The original 131/132 visualization is a preserved bounded-search checkpoint.
This figure binds the later multiplier, pure-block, rebuilding, and chart
packets.  The --check path requires no plotting packages.
"""
from collections import Counter
import argparse
import hashlib
import json
import added100_multipliers as a
from check_x1y1_extensions import replay_stages

h = a.h
OUT = a.OUT


def read(name):
    return json.loads((OUT / name).read_text(encoding='utf-8'))


def paired_reports(name):
    report = read(name)
    other = read('independent-' + name)
    assert report['status'] == other['status'] == 'PASS'
    ignore = {'seconds', 'independent_physical_polynomials'}
    assert {k: v for k, v in report.items() if k not in ignore} == {
        k: v for k, v in other.items() if k not in ignore}
    return report


def data():
    report = paired_reports('validation.json')
    blocks_report = paired_reports('blocks-validation.json')
    closure_report = paired_reports('closure-validation.json')
    model = h.t.Model()
    desc, physical, source_hash = a.build(model)
    packet = h.q.load(OUT / 'global.json.gz')
    assert packet['system'] == desc and packet['source_sha256'] == source_hash
    nvars = len(desc['basis_indices'])
    assert packet['multiplier_degree_bound'] == 1 and packet['completed']
    assert packet['completed_multipliers'] == [[]] + [[i] for i in range(nvars)]
    products = sum(a.syz.verify_relation(physical, nvars, list(range(nvars)), relation)
                   for relation in packet['relations'] + packet['baseline'])
    old, selected, total = a.syz.select_new(packet['baseline'], packet['relations'], list(range(nvars)))
    assert selected == packet['selected_new']
    assert old == packet['checkpoints'][-1]['baseline_multiple_rank']
    assert total == packet['checkpoints'][-1]['combined_rank'] == old + len(selected)
    assert len(selected) == report['additional_relations']
    assert products == report['coefficient_products']
    degrees = Counter()
    for i in selected:
        p = h.cert.decode(packet['relations'][i]['polynomial'])
        degree_set = {len(m) for m in p}
        assert len(degree_set) == 1
        degrees[degree_set.pop()] += 1

    block_desc, forced, block_counts, blocks, complete = a.replay_blocks(model)
    assert block_desc == desc and complete
    assert blocks == blocks_report['blocks'] and forced == blocks_report['forced_raw_ids']
    assert dict(block_counts) == blocks_report['checks']
    closure = h.q.load(OUT / 'closure.json.gz')
    assert closure['source_sha256'] == h.digest(OUT / 'pure-blocks.json.gz')
    assert closure['forced'] == forced and closure['completed']
    ids = [i for i in desc['basis_indices'] if i not in forced]
    stages = [{'name': 'Before continuation', 'ids': desc['basis_indices'], 'cause': ''},
              {'name': 'New coordinate powers', 'ids': ids[:], 'cause': ', '.join(map(str, forced))}]
    cycles = []
    for cycle, record in enumerate(closure['cycles']):
        assert record['before'] == ids
        path = OUT / record['block_file']
        assert record['block_file'] == f'power-rebuilt-{cycle}.json.gz'
        assert record['block_sha256'] == h.digest(path)
        rebuilt = h.q.load(path)
        ids, zeros, _, _ = replay_stages(model, rebuilt, ids, finish=h.terminal)
        detail = {'before': record['before'], 'block_zeros': zeros,
                  'after_blocks': ids[:], 'charts': []}
        if zeros:
            stages.append({'name': 'Rebuilt necessary equations', 'ids': ids[:],
                           'cause': ', '.join(map(str, zeros))})
        if 'system' in record:
            system, eq = h.build(model, h.selection(model)[99], ids)
            assert system == record['system']
            assert [c['pivot'] for c in record['charts']] == system['pivots']
            removed = []
            for chart in record['charts']:
                h.cert.verify_chart(eq, len(ids) + len(system['Koszul_indices']), chart)
                raw = ids[chart['pivot']]
                detail['charts'].append({'raw': raw, 'excluded': chart['excluded']})
                if chart['excluded']:
                    removed.append(raw)
            assert removed == record['removed']
            ids = [i for i in ids if i not in removed]
            stages.append({'name': 'Rebuilt shared-numerator charts', 'ids': ids[:],
                           'cause': ', '.join(map(str, removed))})
        detail['after'] = ids[:]
        cycles.append(detail)
    assert cycles == closure_report['cycles']
    assert ids == closure['remaining'] == closure_report['remaining']
    assert forced == closure_report['forced_raw_ids']
    ending = h.terminal(model, ids)
    assert closure['status'] == ending and closure_report['excluded'] == (ending is not None)
    if ending == 'x0_x1_dependency':
        from added_homology_pair import replay
        dependency, _ = replay(model)
        assert dependency == closure_report['dependency']
    elif ending == 'single_character_dependency':
        from check_quartic_exclusions import single_character
        assert single_character(model, model.dc[ids[0]], ids) == closure_report['dependency']
    previous = json.loads((h.OUT / 'validation.json').read_text(encoding='utf-8'))
    old_row = next(r for r in previous['families'] if r['batch_number'] == 100)
    assert previous['status'] == 'PASS' and not old_row['excluded']
    assert old_row['remaining'] == desc['basis_indices']
    original_charts = [c for cycle in old_row['cycles'] for c in cycle['charts']]
    charts = [c for cycle in cycles for c in cycle['charts']]
    hashes = {p.name: h.digest(p) for p in sorted(OUT.glob('*.json.gz'))}
    for p in sorted(OUT.glob('*.json')):
        if p.name.endswith(('-plan.json', '-attempt.json')) or p.name in ('plan.json', 'attempt.json'):
            hashes[p.name] = hashlib.sha256(json.dumps(json.loads(p.read_text(encoding='utf-8')),
                sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()
    return {'family': 100, 'multiplier_blocks': len(packet['completed_multipliers']),
            'baseline_generators': len(packet['baseline']), 'baseline_multiple_rank': old,
            'combined_rank': total, 'additional_generators': len(selected),
            'new_generator_degrees': {str(k): v for k, v in sorted(degrees.items())},
            'relation_products_checked': products, 'blocks': blocks, 'forced_raw_ids': forced,
            'stages': stages, 'original_unresolved_charts': sum(not c['excluded'] for c in original_charts),
            'continuation_charts': charts, 'excluded': closure_report['excluded'],
            'terminal_kind': ending, 'remaining_characters': sorted(map(list, {model.dc[i] for i in ids})),
            'original_batch_excluded': previous['excluded'],
            'combined_batch_excluded': previous['excluded'] + int(closure_report['excluded']),
            'source_hashes': hashes,
            'hash_format': 'SHA256: gzip as bytes; JSON plans and attempts as sorted compact JSON.',
            'scope': 'Selected necessary relations and a separate checked A100 continuation; no full elimination ideal or holdout solution.'}


def figure(d):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 11, 'svg.fonttype': 'none', 'svg.hashsalt': 'added100-continuation'})
    fig, axes = plt.subplots(1, 3, figsize=(15, 6.3), layout='constrained',
                             gridspec_kw={'width_ratios': [1, 1.12, 1.4]})
    blue, gold, green, red = '#286b9b', '#b87827', '#2e8175', '#a7435c'
    ax = axes[0]
    old, total = d['baseline_multiple_rank'], d['combined_rank']
    ax.barh([1, 0], [old, old], color=blue, height=.48)
    ax.barh([0], [total - old], left=[old], color=gold, height=.48)
    ax.text(old + 3, 1, str(old), va='center')
    ax.text(total + 3, 0, str(total), va='center')
    ax.set(yticks=[1, 0], yticklabels=['Baseline\nclosure', 'With new\nrelations'],
           xlim=(0, total * 1.18), ylim=(-1.4, 1.75), xlabel='Exact denominator-relation rank',
           title='Multipliers add independent cubics')
    ax.text(.02, .24, f"{d['baseline_generators']} baseline quadratics\n"
            f"+ {d['additional_generators']} independent cubics\n"
            f"{d['multiplier_blocks']} completed multiplier blocks", transform=ax.transAxes,
            linespacing=1.6, va='top', fontsize=10)
    ax.text(.02, .025, 'Baseline closure includes constants\nand all linear denominator multiples.',
            transform=ax.transAxes, linespacing=1.5, fontsize=9)
    ax.spines[['top', 'right']].set_visible(False)

    ax = axes[1]
    blocks = d['blocks']
    quartics = [next(m for m in block['maps'] if m['degree'] == 4) for block in blocks]
    labels = ['X0', 'X1', 'Added character']
    for i, (block, record) in enumerate(zip(blocks, quartics)):
        ax.barh(i, record['rank'], color=blue, height=.45)
        ax.barh(i, record['quotient_dimension'], left=record['rank'], color='#e4e5e3', height=.45)
        ax.text(record['codomain'] + 2, i, f"{record['rank']}/{record['codomain']}", va='center', fontsize=10)
        zeros = ', '.join(map(str, block['forced_raw_ids'])) or 'none'
        ax.text(0, i + .34, 'Coordinates forced to zero: ' + zeros, fontsize=9, color=green if block['forced_raw_ids'] else '#626469')
    ax.set(yticks=range(len(blocks)), yticklabels=labels, ylim=(3.8, -.75),
           xlim=(0, max(m['codomain'] for m in quartics) * 1.32),
           xlabel='Degree-four image rank / monomial count', title='Partial images already force coordinate powers')
    ax.text(.02, .08, 'Blue = image; gray = remaining quotient.\nFull rank is unnecessary for a specific\ncoordinate power to lie in the image.',
            transform=ax.transAxes, fontsize=10, linespacing=1.5)
    ax.spines[['top', 'right']].set_visible(False)

    ax = axes[2]
    ax.axis('off')
    ax.set_title('Rebuild after each verified vanishing')
    for i, stage in enumerate(d['stages']):
        y = .89 - i * .18
        ax.text(.04, y, str(len(stage['ids'])), ha='center', va='center', fontsize=15, color=blue,
                bbox={'boxstyle': 'round,pad=.3', 'facecolor': '#edf2f6', 'edgecolor': '#c8d2da'})
        ax.text(.16, y + .02, stage['name'], fontsize=10.5, va='center')
        if stage['cause']:
            ax.text(.16, y - .035, 'Remove raw directions ' + stage['cause'], fontsize=9, va='center', color='#626469')
        if i < len(d['stages']) - 1:
            ax.annotate('', xy=(.04, y - .12), xytext=(.04, y - .055),
                        arrowprops={'arrowstyle': '->', 'color': '#888888'})
    excluded = d['excluded']
    status = 'A100 excluded via the checked pair dependency' if excluded else 'A100 remains unresolved'
    ax.text(.02, .225, status, color=green if excluded else red, weight='bold', fontsize=10, va='top')
    failed = sum(not c['excluded'] for c in d['continuation_charts'])
    successful = sum(c['excluded'] for c in d['continuation_charts'])
    ax.text(.02, .15, f"Original bounded search: {d['original_unresolved_charts']} unresolved charts.\n"
            f"Continuation: {successful} contradicted charts, {failed} unresolved.\n"
            'Every failed attempt remains in its original packet.', fontsize=9.5, linespacing=1.5, va='top')
    fig.suptitle('A100: added relations become useful after coordinate powers and rebuilding', fontsize=15)
    fig.supxlabel(f"Separate continuation: {d['original_batch_excluded']}/132 checkpoint → {d['combined_batch_excluded']}/132 combined exclusions. Selected pure subideals only. Holdout remains unsolved.", fontsize=10)
    fig.savefig(OUT / 'added100-continuation.png', dpi=180)
    fig.savefig(OUT / 'added100-continuation.svg', metadata={'Date': None})
    plt.close(fig)
    path = OUT / 'added100-continuation.svg'
    path.write_text('\n'.join(line.rstrip() for line in path.read_text(encoding='utf-8').splitlines()) + '\n', encoding='utf-8')


def run(check=False):
    d = data()
    if check:
        assert read('visual-data.json') == d
    else:
        (OUT / 'visual-data.json').write_text(json.dumps(d, indent=2) + '\n', encoding='utf-8')
        figure(d)
    receipt = {'status': 'PASS', 'family': 100, 'excluded': d['excluded'],
               'relation_products_checked': d['relation_products_checked'],
               'exact_maps_checked': sum(len(b['maps']) for b in d['blocks']),
               'forced_raw_ids': d['forced_raw_ids'], 'source_hashes': d['source_hashes']}
    (OUT / 'figure-validation.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print('PASS: relation rank, pure-block powers, rebuilt charts, dependency, and source hashes')


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('Run without -O.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    run(parser.parse_args().check)
