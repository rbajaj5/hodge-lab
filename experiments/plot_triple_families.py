"""Render a coverage atlas of complete X0/Y0 three-character extensions."""
from pathlib import Path
import gzip, json, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'algebra'))
import degree7_triples as triples
import degree7_triple_shared as shared


def run():
    out = triples.OUT
    with gzip.open(out / 'certificates.json.gz', 'rt') as f: packet = json.load(f)
    validation = json.loads((out / 'shared-validation.json').read_text(encoding='utf-8-sig'))
    independent = json.loads((out / 'shared-independent-validation.json').read_text(encoding='utf-8-sig'))
    assert validation['status'] == independent['status'] == 'PASS'
    assert validation['families'] == independent['families']
    covered = {r['family'] for r in validation['families'] if r['covered']}
    rows = []; atlas = {}
    coordinate_chars = {tuple(w[i] for w in triples.e1.WEIGHTS) for i in range(6)}
    for family in packet['families']:
        chars = {tuple(c) for c in family['characters']}
        status = ('excluded_by_relaxed_duals' if family['status'] == 'reduced_to_at_most_two_characters'
                  else 'excluded_by_shared_charts' if family['number'] in covered else 'unresolved')
        row = {'number': family['number'], 'characters': family['characters'], 'status': status,
               'initial_dimension': len(family['basis_indices']),
               'anchor_extension': shared.ANCHOR <= chars, 'coordinate_triple': chars <= coordinate_chars}
        rows.append(row)
        if row['anchor_extension']:
            third, = chars - shared.ANCHOR
            atlas[third] = status
    assert len(atlas) == 136
    summary = {'tested_families': len(rows), 'excluded_families': sum(r['status'] != 'unresolved' for r in rows),
               'unresolved_families': sum(r['status'] == 'unresolved' for r in rows),
               'anchor_extensions': 136, 'excluded_anchor_extensions': sum(s != 'unresolved' for s in atlas.values()),
               'remaining_third_characters': [list(c) for c, s in sorted(atlas.items()) if s == 'unresolved'],
               'coordinate_triples_tested': 20, 'total_possible_three_character_families': 428536,
               'closure_dependency': 'The archived complete X0/Y0 exclusion; no new proof of that pair is claimed.',
               'families': rows}
    (out / 'coverage.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    bg = '#101b29'; muted = '#aab8c8'; ink = '#e9f1fa'
    colors = {'excluded_by_relaxed_duals': '#44c4b0', 'excluded_by_shared_charts': '#6f99fa',
              'unresolved': '#f5bb62', 'absent': '#283546', 'anchor': '#f4f5f6'}
    fig, axes = plt.subplots(2, 3, figsize=(12, 9), facecolor=bg)
    for k, ax in enumerate(axes.flat):
        ax.set_facecolor(bg)
        for y in range(6):
            for z in range(6):
                char = (k, y, z)
                status = 'anchor' if char in shared.ANCHOR else atlas.get(char, 'absent')
                ax.add_patch(Rectangle((y-.44, z-.44), .88, .88, color=colors[status], lw=0))
                if status == 'unresolved': ax.text(y, z, '?', ha='center', va='center', color=bg, fontsize=16, weight='bold')
                if status == 'anchor': ax.text(y, z, 'A', ha='center', va='center', color=bg, fontsize=13, weight='bold')
        ax.set(xlim=(-.6,5.6), ylim=(5.6,-.6), xticks=range(6), yticks=range(6), aspect='equal')
        ax.set_title(f'Third character ({k}, b, c)', color=ink, pad=10, fontsize=12)
        ax.set_xlabel('b', color=muted); ax.set_ylabel('c', color=muted, rotation=0, labelpad=12)
        ax.tick_params(colors=muted, length=0)
        for spine in ax.spines.values(): spine.set_visible(False)
    fig.text(.06,.96, 'Holdout: a systematic three-character slice', color=ink, fontsize=23, weight='bold')
    total = len(atlas); excluded = summary['excluded_anchor_extensions']
    fig.text(.06,.922, f'Fixed pair X₀ / Y₀  ·  {total} possible third characters  ·  {excluded} excluded, {total-excluded} unresolved', color=muted, fontsize=12)
    count = lambda status: sum(s == status for s in atlas.values())
    legend = [('excluded_by_relaxed_duals',f"{count('excluded_by_relaxed_duals')}: exact necessary conditions"),
              ('excluded_by_shared_charts',f"{count('excluded_by_shared_charts')}: full shared-numerator charts"),
              ('unresolved',f"{count('unresolved')}: unresolved"), ('anchor','Fixed pair'), ('absent','No retained E1 sector')]
    fig.legend(handles=[Patch(color=colors[k], label=v) for k,v in legend], loc='lower center',
               bbox_to_anchor=(.5,.045), ncol=3, frameon=False, labelcolor=ink, fontsize=10)
    fig.text(.06,.02,'Whole complex coefficient families, modulo F·S₁. This slice is not the full degree-seven problem.',color=muted,fontsize=10)
    fig.subplots_adjust(left=.06,right=.97,top=.87,bottom=.15,hspace=.33,wspace=.2)
    fig.savefig(out / 'character-atlas.png', dpi=180, facecolor=bg)
    print(json.dumps({k:v for k,v in summary.items() if k != 'families'}, indent=2))


if __name__ == '__main__': run()
