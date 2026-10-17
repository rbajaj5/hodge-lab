#!/usr/bin/env python3
"""An evidence-labelled map of Hodge Lab's research interests.

Connectors mean recorded motivation or a research route, never a theorem
implication. Numerical claims and exact results retain their distinct scopes.
This is an index into checked notebook artifacts, not a new proof checker.
"""
from __future__ import annotations

import hashlib
import json
from math import comb
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/idea-atlas'
INK,MUTED,PAPER='#17323B','#53666D','#FAFAF5'
TEAL,PURPLE,GOLD,CORAL='#166A70','#7967AA','#9B712A','#B94D42'


def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def evidence():
    sources={}
    def read(name):
        path=ROOT/name
        sources[name]=sha(path)
        return load(path)
    for name in ['high-genus-flow','dubedat-cycles','denominator-ranking','why-yang',
                 'typed-rewrite-search','syzygy-rebuild','cyclic-fano-spectrum',
                 'cyclic-fano-blowup-audit','cyclic-fano-remaining66-multipliers']:
        path=ROOT/'notes'/f'{name}.md'
        sources[path.relative_to(ROOT).as_posix()]=sha(path)
    topology=read('results/high-genus-flow/topology.json')
    flow=read('results/high-genus-flow/cpu-validation.json')
    assert topology['topology']['genus']==flow['genus']==48
    assert topology['expected_real_harmonic_one_form_dimension']==96
    assert flow['connected_closed_orientable_manifold_checked']
    dimers=read('results/dubedat-cycle/report.json')
    assert dimers['distinct_D_directions_mod_gauge']==dimers['rejected']==45
    assert dimers['solvable_E2']==0 and dimers['Koszul_corrections_per_case']==840
    gram=read('results/denominator-gram/report.json')
    trials=[gram]+gram['replications']
    finalists=set()
    for trial in trials:
        for candidate in trial['exact_checks']:
            assert candidate['status']=='rejected'
            finalists.add(tuple(tuple(pair) for pair in candidate['denominator_coordinates']))
    assert len(finalists)==254 and len(trials)==5
    anisotropic=sum(t['selections']['anisotropic']['mean_E2_residual'] for t in trials)/5
    uniform=sum(t['selections']['uniform']['mean_E2_residual'] for t in trials)/5
    assert round(anisotropic,5)==.31257 and round(uniform,5)==.31222
    bridges=read('results/source-bridges/report.json')
    refinements=bridges['ginibre']['refinement_history']
    assert len(refinements)==5
    assert all(abs(p['winding']+11)<1e-10 for p in refinements)
    homology=read('results/added-character-homology/visual-data.json')
    families={f['number']:f for f in homology['families']}
    assert families[19]['score']==families[30]['score']==3
    assert families[19]['H0_degree4']==11 and families[30]['H0_degree4']==0
    spectrum=read('results/cyclic-fano-spectrum/spectrum-101.json')
    spectrum_review=read('results/cyclic-fano-spectrum/independent-validation.json')
    assert spectrum_review['status']=='PASS'
    counts=spectrum['characteristic_zero_inference']
    assert spectrum['dimension']==120
    assert [counts[k] for k in ['geometric_points_over_C','one_point_length','remaining_simple_points']]==[118,3,117]
    blowup=read('results/cyclic-fano-blowup-audit/independent-validation.json')
    assert blowup['status']=='PASS'
    assert blowup['axis_scalar_pole_orders']==[1,5]
    packet=read('results/cyclic-fano-remaining66-multipliers/packet.json')
    review=read('results/cyclic-fano-remaining66-multipliers/independent-validation.json')
    assert packet['status']=='full_quadratic_direction_family_excluded' and review['status']=='PASS'
    assert review['packet_lf_sha256']==sources['results/cyclic-fano-remaining66-multipliers/packet.json']
    assert review['new_power_identities']==56 and review['coordinate_divisible_closure']['status']=='PASS'
    old=packet['prior_proof']['prior_forced_raw_parameters']
    new=review['newly_forced_raw_parameter_indices']
    closure=[item['raw_parameter_index'] for item in packet['coordinate_divisible_closure']['embedding']]
    assert [len(old),len(new),len(closure)]==[9,56,10]
    assert len(set(old+new+closure))==75
    grid=np.zeros(75,dtype=int)
    grid[new]=1;grid[closure]=2
    route_data=[
        dict(id='fields',title='High-genus Hodge / GFF',status='tested model',
             fact='Genus 48; 96 harmonic directions. A broad finite-model crossover.',
             limit='No phase transition or certificate.',note='notes/high-genus-flow.md'),
        dict(id='dimers',title='Dubédat / dimers',status='exact finite rejections',
             fact='Determinant-based candidate construction: 45 distinct directions rejected exactly.',
             limit='This polynomial adaptation is not a dimer theorem about the target.',note='notes/dubedat-cycles.md'),
        dict(id='grams',title='Anisotropic Gram ranking',status='tested heuristic',
             fact='254 distinct finalists rejected; anisotropy showed no clear advantage over uniform weighting.',
             limit='Better residual scores did not establish a solution.',note='notes/denominator-ranking.md'),
        dict(id='braids',title='Braids / random matrices',status='tested model and proposed connection',
             fact='Ginibre discriminant winding -11 at five sampling resolutions.',
             limit='Numerical winding is not full braid information; no certificate-map monodromy was constructed.',note='notes/syzygy-rebuild.md'),
        dict(id='yang',title='Yang / typed relations',status='organizing perspective',
             fact='A19 and A30 have equal H1 but different H0 in the selected graded complexes.',
             limit='Yang sheaf theorems are not instantiated; no typed-cache advantage is inferred.',note='notes/why-yang.md'),
        dict(id='geometry',title='Bourbaki / Dolgachev / Shafarevich',status='exact local and fiber results',
             fact='Fixed fiber: length120, with117 simple points and one length3 point. Scalar pole orders1 and5 on specified arcs.',
             limit='These are scoped fiber/slice calculations, not a global support or solution.',note='notes/cyclic-fano-spectrum.md'),
        dict(id='koszul',title='Eisenbud / Koszul',status='exact family exclusion',
             fact='All75 homogeneous quadratic-direction polar parameters excluded for cyclic-triple-fano.',
             limit='Arbitrary degree7 denominators and the instance remain open.',note='notes/cyclic-fano-remaining66-multipliers.md')]
    return dict(schema='hodge-lab-idea-atlas-v1',source_sha256=sources,
                routes=route_data,connections=[dict(source=r['id'],target='koszul',meaning='research motivation or proposed route; not a theorem implication')
                                             for r in route_data if r['id']!='koszul'],
                exact_parameter_partition=grid.reshape(5,15).tolist(),
                parameter_partition_legend=['nine prior zeros','56 new powers','ten closed by earlier subfamily proof'],
                gram_mean_scores=dict(anisotropic=anisotropic,uniform=uniform),
                next_search=dict(direction_degree=3,denominator_degree=8,parameters=5*comb(7,3),
                                 full_family_status='ongoing; no full-family solve asserted'),
                meaning='Evidence-labelled research map, not a theorem-dependency graph.',
                verification='Source facts and result statuses checked; full arithmetic proofs remain in linked notebooks.')


def card(ax,x,y,w,h,number,title,tag,lines,color,limit):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.009,rounding_size=0.010',
                              facecolor='white',edgecolor='#D8E0DA',linewidth=1.2))
    ax.plot([x+.014,x+.014],[y+.022,y+h-.022],color=color,lw=3,solid_capstyle='round')
    ax.text(x+.035,y+h-.028,f'{number}  {tag.upper()}',fontsize=9.5,color=color,weight='bold',va='top')
    ax.text(x+.035,y+h-.054,title,fontsize=16,weight='bold',va='top',linespacing=1.2)
    ax.text(x+.035,y+h-.097,'\n'.join(lines),fontsize=12.3,va='top',linespacing=1.45)
    ax.text(x+.035,y+.009,limit,fontsize=10.3,color=MUTED,va='bottom')


def draw(data):
    fig=plt.figure(figsize=(16,11),facecolor=PAPER)
    ax=fig.add_axes([0,0,1,1]);ax.set_xlim(0,1);ax.set_ylim(0,1);ax.axis('off')
    ax.text(.045,.965,'Hodge Lab',fontsize=31,weight='bold',va='top')
    ax.text(.045,.901,'A research notebook where mathematical interests become testable questions',fontsize=17,color=MUTED)
    for x,color,label in [(.045,PURPLE,'Perspective / analogy'),(.270,GOLD,'Tested model / heuristic'),(.525,TEAL,'Exact result with stated scope')]:
        ax.scatter([x+.004],[.866],s=45,color=color)
        ax.text(x+.018,.866,label,fontsize=11.5,va='center',color=MUTED)
    ax.text(.045,.831,'Dotted links connect research routes. They do not assert mathematical implications.',fontsize=11.5,color=MUTED)
    for sy,ty in [(.713,.690),(.483,.545),(.253,.397)]:
        for sx,tx in [(.306,.365),(.694,.635)]:
            ax.add_patch(FancyArrowPatch((sx,sy),(tx,ty),connectionstyle='arc3,rad=0',
                         arrowstyle='-|>',mutation_scale=9,color='#A7B7AF',lw=1.2,linestyle=(0,(2,3)),zorder=0))
    card(ax,.045,.625,.252,.175,'01','High-genus Hodge / GFF','tested model',
         ['48 handles · 96 harmonic directions','A broad coherence crossover.'],GOLD,'Finite simulation; no phase transition.')
    card(ax,.045,.395,.252,.175,'02','Dubédat / dimers','exact finite rejection',
         ['Determinants generate candidates.','45 directions rejected exactly.'],TEAL,'Adaptation of an idea, not a dimer proof.')
    card(ax,.045,.165,.252,.175,'03','Anisotropic Gram ranking','tested heuristic',
         ['254 distinct finalists rejected.','No clear anisotropy advantage.'],GOLD,'A smaller numerical score is not a solve.')
    card(ax,.703,.625,.252,.175,'04','Braids / random matrices','tested model + analogy',
         ['Ginibre discriminant winding −11.','Stable at five sampling resolutions.'],GOLD,'Scalar winding is not a full braid.')
    card(ax,.703,.395,.252,.175,'05','Yang / typed relations','organizing perspective',
         [r'Equal $H_1$ can hide different $H_0$.','Relations are not new equations.'],PURPLE,'No geometric sheaf theorem instantiated.')
    card(ax,.703,.165,.252,.175,'07','Bourbaki / geometry','exact geometry',
         ['Dolgachev polars; Shafarevich slices.','Fiber length 120: 117 simple + 1 triple.'],TEAL,'No supporting divisor constructed.')
    x,y,w,h=.365,.322,.270,.478
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.009,rounding_size=0.012',
                              facecolor='#ECF3ED',edgecolor=TEAL,linewidth=1.5))
    ax.text(x+.021,y+h-.029,'06  EXACT FAMILY EXCLUSION',fontsize=10,color=TEAL,weight='bold',va='top')
    ax.text(x+.021,y+h-.065,'Eisenbud / Koszul',fontsize=21,weight='bold',va='top')
    ax.text(x+.021,y+h-.116,'Build the full correction map.\nProve identities. Rebuild. Replay.',fontsize=14,linespacing=1.55,va='top')
    ax.text(x+.021,y+h-.199,'75',fontsize=42,weight='bold',color=TEAL,va='top')
    ax.text(x+.097,y+h-.205,'quadratic-direction\npolar parameters\nexcluded jointly',fontsize=13.5,va='top',linespacing=1.3)
    gridax=fig.add_axes([x+.022,y+.115,w-.044,.075])
    gridax.imshow(data['exact_parameter_partition'],aspect='auto',cmap=ListedColormap(['#D7DCD7','#6BA49A','#D6B574']),vmin=0,vmax=2)
    gridax.set_xticks(np.arange(-.5,15,1),minor=True);gridax.set_yticks(np.arange(-.5,5,1),minor=True)
    gridax.grid(which='minor',color='#ECF3ED',lw=1.1);gridax.set_xticks([]);gridax.set_yticks([]);gridax.tick_params(which='both',length=0)
    for spine in gridax.spines.values():spine.set_visible(False)
    ax.text(x+.021,y+.093,'9 prior · 56 new · 10 inherited closure',fontsize=10.2,color=MUTED,va='top')
    ax.text(x+.021,y+.057,'cyclic-triple-fano · degree 7',fontsize=12,weight='bold',va='top')
    ax.text(x+.021,y+.020,'Family exclusion; instance unsolved.',fontsize=10.9,color=CORAL,va='bottom')
    ax.add_patch(FancyBboxPatch((.365,.165),.270,.105,boxstyle='round,pad=0.009,rounding_size=0.010',
                              facecolor='#F2EEF8',edgecolor='#CFC4E1',linewidth=1.1))
    ax.text(.386,.251,'NEXT SEARCH · DEGREE 8',fontsize=10,color=PURPLE,weight='bold',va='top')
    ax.text(.386,.218,'175 cubic-direction parameters',fontsize=14,weight='bold',va='top')
    ax.text(.386,.183,'Ongoing; the full family remains open.',fontsize=11,color=MUTED,va='top')
    ax.text(.045,.093,'Curiosity chooses a route. Exact checks determine what survives.',fontsize=18,weight='bold')
    ax.text(.045,.055,'Independent notebook · sources, fixed targets, failed attempts and limits remain linked in the accompanying notes.',fontsize=11.5,color=MUTED)
    OUT.mkdir(parents=True,exist_ok=True)
    fig.savefig(OUT/'idea-atlas.png',dpi=160,facecolor=PAPER)
    svg=OUT/'idea-atlas.svg';fig.savefig(svg,facecolor=PAPER,metadata={'Date':None})
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8',newline='\n')
    plt.close(fig)


def main():
    assert __debug__,'Run without -O so the source checks remain enabled.'
    plt.rcParams.update({'font.family':'DejaVu Sans','text.color':INK,'axes.labelcolor':INK,
                         'svg.fonttype':'none','svg.hashsalt':'hodge-lab-idea-atlas-v1'})
    data=evidence();draw(data)
    data['renderer_lf_sha256']=sha(Path(__file__))
    (OUT/'plot-data.json').write_text(json.dumps(data,separators=(',',':'),ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
    assert all(sha(ROOT/name)==digest for name,digest in data['source_sha256'].items())
    print(json.dumps({'status':'PASS','source_bindings':len(data['source_sha256']),
                      'routes':len(data['routes']),'plot_data_bytes':(OUT/'plot-data.json').stat().st_size}))


if __name__=='__main__':
    main()
