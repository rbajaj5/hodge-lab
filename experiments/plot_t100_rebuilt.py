"""Render and validate the exact T100 rebuilt-multiplier experiment."""
from pathlib import Path
import argparse
import hashlib
import json

import typed_rewrite_families as h
import t100_rebuilt_multipliers as multipliers
import t100_rebuilt_blocks as blocks
import t100_rebuilt_closure as closure


OUT = multipliers.OUT


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True,
        separators=(',', ':')).encode()).hexdigest()


def data():
    primary = read(OUT / 'validation.json')
    independent = read(OUT / 'independent-validation.json')
    block_primary = read(blocks.OUT / 'validation.json')
    block_independent = read(blocks.OUT / 'independent-validation.json')
    close_primary = read(closure.OUT / 'validation.json')
    close_independent = read(closure.OUT / 'independent-validation.json')
    clean = lambda row: {k: v for k, v in row.items()
                         if k not in ['seconds', 'independent_physical_polynomials']}
    assert clean(primary) == clean(independent)
    assert clean(block_primary) == clean(block_independent)
    assert clean(close_primary) == clean(close_independent)
    assert primary['status'] == block_primary['status'] == close_primary['status'] == 'PASS'
    assert close_primary['excluded'] and close_primary['ending'] == 'x0_y1_dependency'
    packet = h.q.load(OUT / 'relations.json.gz')
    block_packet = h.q.load(blocks.OUT / 'blocks.json.gz')
    close_packet = h.q.load(closure.OUT / 'closure.json.gz')
    assert packet['completed'] and block_packet['completed'] and close_packet['completed']
    strands = []
    for block in block_packet['blocks']:
        for strand in block['strands']:
            strands.append({
                'character': block['character'],
                'raw_ids': block['raw_ids'],
                'degree': strand['degree'],
                'rank_Q': strand['rank_Q'],
                'codomain': strand['codomain'],
                'quotient_dimension_Q': strand['quotient_dimension_Q'],
                'rank_mod_p': strand['rank_mod_p'],
                'forced_raw_ids': [packet['system']['basis_indices'][p['coordinate']]
                                   for p in strand['powers']],
            })
    result = {
        'family': 'T100',
        'global_family': packet['global_family'],
        'old_directions': 13,
        'rebuilt_directions': primary['denominator_directions'],
        'physical_equations': primary['physical_equations'],
        'relations': primary['relations'],
        'additional_relations': primary['additional_relations'],
        'completed_multiplier_blocks': primary['completed_blocks'],
        'strands': strands,
        'forced_raw_ids': block_primary['forced_raw_ids'],
        'closure_cycles': close_primary['cycles'],
        'ending': close_primary['ending'],
        'excluded': close_primary['excluded'],
        'checks': close_primary['checks'],
        'hashes': {
            'relations.json.gz': h.digest(OUT / 'relations.json.gz'),
            'blocks.json.gz': h.digest(blocks.OUT / 'blocks.json.gz'),
            'closure.json.gz': h.digest(closure.OUT / 'closure.json.gz'),
            'validation': sha(clean(primary)),
            'blocks-validation': sha(clean(block_primary)),
            'closure-validation': sha(clean(close_primary)),
        },
        'scope': ('Exact Q-ranks and identities; ranks modulo 1009, 1013, and 1019 '
                  'are consistency screens, not p-adic Hodge-theory proofs.'),
    }
    return result


def render(payload):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch
    plt.rcParams.update({'font.size': 10.5, 'svg.fonttype': 'none',
                         'svg.hashsalt': 't100-rebuilt'})
    blue, gold, green, red, gray = '#276b9b', '#b97b2b', '#2f8375', '#a7455c', '#d9dde0'
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 6.7), layout='constrained',
                             gridspec_kw={'width_ratios': [1.25, 1]})
    ax = axes[0]
    groups = [([0, 0, 1], 'X0', blue), ([4, 2, 3], 'added', gold), ([5, 3, 0], 'Y1', green)]
    for character, label, color in groups:
        rows = sorted([r for r in payload['strands'] if r['character'] == character],
                      key=lambda r: r['degree'])
        degrees = [r['degree'] for r in rows]
        ratios = [r['rank_Q'] / r['codomain'] for r in rows]
        ax.plot(degrees, ratios, marker='o', linewidth=2, color=color, label=label)
        for row, x, y in zip(rows, degrees, ratios):
            if row['forced_raw_ids']:
                ax.scatter([x], [y], s=95, facecolors='none', edgecolors=red,
                           linewidths=2, zorder=4)
    ax.set(xlabel='Total degree', ylabel='Exact rank / monomial-space dimension',
           xticks=[3, 4, 5, 6], ylim=(0, 1.05),
           title='Pure-character graded maps after rebuilding')
    ax.grid(axis='y', color=gray, linewidth=.8)
    ax.spines[['top', 'right']].set_visible(False)
    ax.legend(frameon=False, loc='lower right')
    ax.text(0.02, 0.03,
            'Open red ring: at least one exact coordinate-power witness.\n'
            'All 36 displayed modular ranks equal the rational rank.',
            transform=ax.transAxes, fontsize=9, va='bottom')

    ax = axes[1]
    ax.axis('off')
    stages = [
        (0.90, '13 directions', 'original T100'),
        (0.70, '12 directions', 'earlier exact $a_{56}=0$'),
        (0.48, '7 directions', 'five exact Y1 vanishings'),
        (0.26, '5 X0 directions', 'charts 6 and 211 contradict'),
        (0.07, 'excluded', 'replayed anchor dependency'),
    ]
    for i, (y, title, subtitle) in enumerate(stages):
        color = green if i == len(stages) - 1 else blue if i < 2 else gold
        ax.text(.5, y, title, ha='center', va='center', fontsize=14,
                color='white', bbox={'boxstyle': 'round,pad=.42', 'fc': color, 'ec': 'none'})
        ax.text(.5, y - .075, subtitle, ha='center', va='top', fontsize=9, color='#444444')
        if i < len(stages) - 1:
            next_y = stages[i + 1][0]
            ax.add_patch(FancyArrowPatch((.5, y - .105), (.5, next_y + .07),
                         arrowstyle='-|>', mutation_scale=13, color='#777777', linewidth=1.2))
    ax.text(.02, .43, 'Failed rebuilt charts retained:\n42, 88, 102, 111, 114',
            fontsize=9, color=red, va='center')
    ax.set_title('Exact reduction and closure', pad=12)
    fig.suptitle('T100: rebuilt multipliers turn a failed continuation into an exact exclusion', fontsize=15)
    fig.supxlabel('Finite-field calculations screen ranks; every vanishing and chart contradiction is replayed over Q in two physical polynomial constructions.', fontsize=9.5)
    for suffix in ['png', 'svg']:
        fig.savefig(OUT / f't100-rebuilt.{suffix}', dpi=190 if suffix == 'png' else None,
                    metadata={'Date': None} if suffix == 'svg' else None)
    plt.close(fig)
    svg = OUT / 't100-rebuilt.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines()) + '\n', encoding='utf-8')


def main(check=False):
    payload = data()
    path = OUT / 'visual-data.json'
    if check:
        assert read(path) == payload
        assert (OUT / 't100-rebuilt.png').exists() and (OUT / 't100-rebuilt.svg').exists()
        print(json.dumps({'status': 'PASS', 'excluded': payload['excluded'],
                          'strands': len(payload['strands']),
                          'finite_field_rank_comparisons': payload['checks']['finite_field_rank_comparisons'],
                          'scope': payload['scope']}, indent=2))
    else:
        path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
        render(payload)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    main(args.check)
