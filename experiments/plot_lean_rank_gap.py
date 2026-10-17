#!/usr/bin/env python3
"""Draw the actual RankGap.lean proof and its explicit experimental boundary.

The compiler receipt establishes compilation of the generic theorem.  The
Python receipt establishes the separate concrete matrix checks.  This renderer
checks those bindings; it neither runs Lean nor formalizes the matrix data.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/lean-rank-gap'
INK, MUTED, PAPER = '#17323B', '#53666D', '#FAFAF5'
TEAL, PURPLE, CORAL = '#166A70', '#7967AA', '#B94D42'
THEOREMS = ['not_mem_of_finrank_gap', 'not_mem_of_finrank_150_151',
            'no_correction_solution_of_finrank_gap']


def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def evidence():
    sources={}
    def bind(name):
        path=ROOT/name
        sources[name]=sha(path)
        return path
    formal=load(bind('formal/results/rank-gap-validation.json'))
    assert formal['schema']=='hodge-lab-rank-gap-lean-v1'
    assert formal['status']=='PASS'
    assert 'version 4.31.0,' in formal['lean_version']
    assert formal['mathlib_commit']=='fabf563a7c95a166b8d7b6efca11c8b4dc9d911f'
    for name,digest in formal['source_lf_sha256'].items():
        assert sha(bind('formal/'+name))==digest
    expected=[['lake','env','lean','--version'],['lake','build'],
              ['lake','env','lean','Audit.lean'],['lake','env','leanchecker','HodgeLab.RankGap']]
    assert [record['command'] for record in formal['commands']]==expected
    for record in formal['commands']:
        assert record['exit_code']==0
        assert sha(bind('formal/results/'+record['log']))==record['log_lf_sha256']
    assert set(formal['theorem_axioms'])=={'HodgeLab.'+name for name in THEOREMS}
    for axioms in formal['theorem_axioms'].values():
        assert set(axioms)<={'propext','Classical.choice','Quot.sound'}
    source=(ROOT/'formal/HodgeLab/RankGap.lean').read_text(encoding='utf-8')
    assert re.findall(r'^theorem (\w+)',source,re.M)==THEOREMS
    assert not re.search(r'\b(sorry|admit|axiom)\b',source)
    required=['intro member','Submodule.span_insert_eq_span member',
              'rw [sameSpan] at lower',
              'exact (Nat.not_succ_le_self n) (le_trans lower upper)',
              'not_mem_of_finrank_gap corrections target 150 upper lower',
              'candidate_mem : ∀ i, candidate i ∈ Submodule.span K corrections',
              '¬ ∃ i, candidate i = target']
    assert all(fragment in source for fragment in required)
    theorem_lines={name:next(i for i,line in enumerate(source.splitlines(),1)
                             if line.startswith('theorem '+name+' ')) for name in THEOREMS}
    review=load(bind('results/cyclic-fano-cubic-polars/independent-validation.json'))
    assert review['status']=='PASS'
    assert sha(bind('experiments/check_cyclic_fano_cubic_polars.py'))==review['checker_sha256']
    assert sha(bind('results/cyclic-fano-cubic-polars/packet.json'))==review['primary_packet_sha256']
    assert sha(bind('results/cyclic-fano-cubic-gpu/report.json'))==review['gpu_report_lf_sha256']
    assert review['source_projection']['universal_correction_relations']==25
    assert review['source_projection']['exact_correction_rank_upper_bound']==150
    fixed=review['fixed_direction_minor_audit']
    assert fixed['status']=='PASS' and fixed['prime']==65521 and len(fixed['cases'])==16
    for case in fixed['cases']:
        assert case['exact_column_relations']==25
        assert case['rational_rank_upper_bound']==150
        assert case['augmented_minor_size']==151
        assert 0<case['nonzero_determinant_mod_prime']<65521
    return {'schema':'lean-rank-gap-figure-v1','status':'PASS','source_sha256':sources,
            'lean_version_short':'Lean 4.31.0 · compiled + kernel replay',
            'theorems':[{'name':'HodgeLab.'+name,'source_line':theorem_lines[name],
                         'axioms':formal['theorem_axioms']['HodgeLab.'+name]} for name in THEOREMS],
            'proof_steps':['Explicit upper/lower finrank inequalities.',
                           'Assume target membership.',
                           'Submodule.span_insert_eq_span gives equality of spans.',
                           'Rewrite lower and compose inequalities with le_trans.',
                           'Nat.not_succ_le_self contradicts n+1 <= n.',
                           'Target nonmembership; specialization and correction corollary.'],
            'python_only':{'fixed_cases':16,'relations':25,'upper_bound':150,
                           'augmented_minor_size':151,'prime':65521},
            'scope':'Generic implication compiled; concrete matrices and modular-to-rational transfer remain Python-verified, not Lean-formalized.'}


def box(fig, x, y, w, h, color, edge=None):
    fig.add_artist(FancyBboxPatch((x, y), w, h, transform=fig.transFigure,
                   boxstyle='round,pad=.008,rounding_size=.008',
                   facecolor=color, edgecolor=edge or '#D2DBD3', linewidth=1))


def arrow(fig, start, end, color=TEAL, dashed=False):
    fig.add_artist(FancyArrowPatch(start, end, transform=fig.transFigure,
                   arrowstyle='-|>', mutation_scale=17, linewidth=1.5,
                   color=color, linestyle='--' if dashed else '-'))


def draw(data):
    fig = plt.figure(figsize=(17, 11.5), facecolor=PAPER)
    fig.text(.05, .947, 'What Lean proves in the rank-gap test',
             fontsize=30, weight='bold')
    fig.text(.05, .906, 'cyclic-triple-fano · discussion #112  |  '
             'formal/HodgeLab/RankGap.lean  |  ' + data['lean_version_short'],
             fontsize=13.5, color=MUTED)

    box(fig, .05, .690, .40, .165, '#EEF2EC')
    fig.text(.065, .825, 'CONCRETE INPUTS · PYTHON CHECKED',
             fontsize=14, color=TEAL, weight='bold')
    fig.text(.065, .785, r'25 exact column relations: $\mathrm{rank}(M)\leq150$',
             fontsize=15)
    fig.text(.065, .747, r'Nonzero 151-minor: $\mathrm{rank}([M\mid b])\geq151$',
             fontsize=15)
    fig.text(.065, .712, '16 fixed cases independently checked; these data are not encoded in Lean.',
             fontsize=10.5, color=MUTED)

    box(fig, .55, .690, .40, .165, '#EEEBF4')
    fig.text(.565, .825, 'EXPLICIT HYPOTHESES · LEAN ACCEPTS',
             fontsize=14, color=PURPLE, weight='bold')
    fig.text(.565, .780, r'upper: $d(S)\leq n$     lower: $n+1\leq d(S_b)$',
             fontsize=16)
    fig.text(.565, .741, r'$d=\mathrm{Module.finrank}_K$; any field $K$, module $V$, and $n\in\mathbb{N}$.',
             fontsize=12)
    fig.text(.565, .708, 'The generic theorem does not compute either bound.',
             fontsize=11.5, color=MUTED)
    arrow(fig, (.46, .773), (.54, .773), PURPLE, True)
    fig.text(.50, .733, 'intended\ninputs', ha='center', va='top',
             fontsize=10.5, color=MUTED)

    box(fig, .05, .270, .90, .360, '#F3F5F0')
    fig.text(.065, .600, 'COMPILED IMPLICATION', fontsize=14,
             color=TEAL, weight='bold')
    fig.text(.285, .600, 'HodgeLab.not_mem_of_finrank_gap',
             fontsize=14, family='DejaVu Sans Mono')
    fig.text(.065, .562, r'$S=\mathrm{span}_K(\mathrm{corrections})$'
             r'     and     $S_b=\mathrm{span}_K(\{b\}\cup\mathrm{corrections})$',
             fontsize=14, color=MUTED)

    panels = [
        (.065, '1  Assume membership', r'$b\in S$',
         ['intro member'], '#FFFFFF', INK),
        (.295, '2  Adding b changes nothing', r'$S_b=S$',
         ['Submodule.', 'span_insert_eq_span member'], '#FFFFFF', PURPLE),
        (.525, '3  Rewrite and combine', r'$n+1\leq n$',
         ['rw [sameSpan] at lower', 'le_trans lower upper', 'Nat.not_succ_le_self n'], '#F8E9E5', CORAL),
        (.755, '4  Conclude', r'$b\notin S$',
         ['The assumed membership', 'is impossible.'], '#E0EFEB', TEAL),
    ]
    for x, title, formula, lines, color, accent in panels:
        box(fig, x, .329, .180, .185, color)
        fig.text(x+.010, .486, title, fontsize=11.3, weight='bold', color=accent)
        fig.text(x+.090, .432, formula, fontsize=25, ha='center', color=accent)
        fig.text(x+.010, .391, '\n'.join(lines), fontsize=9.3,
                 family='DejaVu Sans Mono' if x<.75 else 'DejaVu Sans',
                 color=MUTED, va='top', linespacing=1.6)
    for x in [.25, .48, .71]:
        arrow(fig, (x, .423), (x+.038, .423))
    fig.text(.065, .290, 'The contradiction is arithmetic: a natural number cannot be at least its own successor.',
             fontsize=12, color=MUTED)

    box(fig, .05, .120, .440, .108, '#EEEBF4')
    fig.text(.065, .201, 'The current numerical specialization', fontsize=13.5,
             weight='bold', color=PURPLE)
    fig.text(.065, .171, r'$n=150:\quad 151\leq150$ is impossible, hence $b\notin S$.',
             fontsize=14)
    fig.text(.065, .138, 'HodgeLab.not_mem_of_finrank_150_151',
             fontsize=10.5, family='DejaVu Sans Mono', color=MUTED)

    box(fig, .51, .120, .440, .108, '#E0EFEB')
    fig.text(.525, .201, 'The correction-system corollary', fontsize=13.5,
             weight='bold', color=TEAL)
    fig.text(.525, .171, r'If every candidate lies in $S$, no candidate equals $b$.',
             fontsize=13.5)
    fig.text(.525, .138, 'HodgeLab.no_correction_solution_of_finrank_gap',
             fontsize=10.1, family='DejaVu Sans Mono', color=MUTED)

    fig.text(.05, .077, 'Three generic lemmas compiled. Python verifies the concrete matrices, rational relations, and modular minors.',
             fontsize=12.5, weight='bold')
    fig.text(.05, .040, 'This is not a Lean verification of the 16 matrices, a HodgeComputer.HasCertificate proof, or a solution of the instance.',
             fontsize=12, color=CORAL)
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT/'lean-rank-gap.png', dpi=160, facecolor=PAPER)
    svg=OUT/'lean-rank-gap.svg'
    fig.savefig(svg, metadata={'Date':None}, facecolor=PAPER)
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',
                   encoding='utf-8', newline='\n')
    plt.close(fig)


def main():
    assert __debug__, 'Run without -O so source checks remain enabled.'
    plt.rcParams.update({'font.family':'DejaVu Sans', 'text.color':INK,
                         'svg.fonttype':'none', 'svg.hashsalt':'lean-rank-gap-v1'})
    data=evidence()
    draw(data)
    data['renderer_lf_sha256']=sha(Path(__file__))
    (OUT/'plot-data.json').write_text(json.dumps(data,separators=(',',':'))+'\n',
                                     encoding='utf-8', newline='\n')
    assert all(sha(ROOT/name)==digest for name,digest in data['source_sha256'].items())
    print(json.dumps({'status':'PASS','source_bindings':len(data['source_sha256']),
                      'compiled_theorems':len(data['theorems']),
                      'concrete_cases_python_only':16,'concrete_cases_in_Lean':0,
                      'plot_data_bytes':(OUT/'plot-data.json').stat().st_size}))


if __name__=='__main__':
    main()
