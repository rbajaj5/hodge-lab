#!/usr/bin/env python3
"""Reproducible, source-bound figures for degree-eight cubic-direction polars.

Images encode exact polynomial supports and the scope of checked searches.
Occupancy is not a metric, spectrum, geometric dimension, or phase transition.
"""
from __future__ import annotations

import base64
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT/'results/cyclic-fano-cubic-polars'
OUT = ROOT/'results/cyclic-fano-cubic-polars-figures'
BASE = (0, 1, 3, 4, 5)
NAMES = ('X0', 'X1', 'Y0', 'Y1', 'Y2')
INK, MUTED, PAPER = '#17323B', '#53666D', '#FAFAF5'
TEAL, PURPLE, CORAL = '#166A70', '#7967AA', '#B94D42'
GOLD, GREY = '#C59A4D', '#DFE3DF'


def sha(path):
    raw = path.read_bytes()
    return hashlib.sha256(raw if path.suffix=='.gz' else raw.replace(b'\r\n', b'\n')).hexdigest()


def load(path):
    raw = gzip.decompress(path.read_bytes()) if path.suffix=='.gz' else path.read_bytes()
    return json.loads(raw)


def monomial_label(powers):
    parts = []
    for coordinate, name in zip(BASE, NAMES):
        power = powers[coordinate]
        if power:
            symbol = name[0]+'_{'+name[1]+'}'
            parts.append(symbol if power==1 else symbol+'^{'+str(power)+'}')
    return '$'+''.join(parts)+'$'


def cubic_groups(monomials):
    """Keep real packet indices, grouping by the partition of total degree 3."""
    groups = [[], [], []]
    for index, powers in enumerate(monomials):
        assert len(powers)==6 and powers[2]==0 and sum(powers)==3
        support = sum(p>0 for p in powers)
        groups[support-1].append(index)
    assert [len(g) for g in groups]==[5, 20, 10]
    return groups


def packed_map(columns, row_bin=1, column_bin=1):
    """Read exact nonzero coefficients; compress only the displayed occupancy."""
    rows = sorted({m for p in columns for m, c in p.items() if c})
    lookup = {m:i for i,m in enumerate(rows)}
    shape = [len(rows),len(columns)]
    bshape = [(shape[0]+row_bin-1)//row_bin,(shape[1]+column_bin-1)//column_bin]
    occupancy = np.zeros(bshape,dtype=np.uint8)
    terms = 0
    for j, polynomial in enumerate(columns):
        for m, c in polynomial.items():
            if c:
                occupancy[lookup[m]//row_bin,j//column_bin] = 1
                terms += 1
    return dict(shape=shape,rows=[list(m) for m in rows],
                nonzero_coefficients=terms,bin_size=[row_bin,column_bin],
                binned_shape=bshape,occupied_bins=int(occupancy.sum()),
                occupancy_bits_base64=base64.b64encode(np.packbits(occupancy.reshape(-1),bitorder='big')).decode(),
                encoding='Row-major bits, most significant bit first; zero-padded last byte; base64.',
                bin_rule='Occupied iff at least one exact nonzero coefficient lies in this bin.')


def draw_map(ax, data, color=TEAL):
    shape = data['binned_shape']
    bits = np.unpackbits(np.frombuffer(base64.b64decode(data['occupancy_bits_base64']),dtype=np.uint8),bitorder='big')
    grid = bits[:shape[0]*shape[1]].reshape(shape)
    ax.imshow(grid,origin='upper',aspect='auto',interpolation='nearest',
              extent=[0,data['shape'][1],data['shape'][0],0],
              cmap=ListedColormap([PAPER,color]),vmin=0,vmax=1)
    ax.tick_params(colors=MUTED,labelsize=10)
    for spine in ax.spines.values():
        spine.set_color('#CFD7D2')


def quadric_columns(packet):
    result=[]
    for equation in packet['equations']:
        polynomial={}
        for i,j,c in equation['terms']:
            assert i<=j and (i,j) not in polynomial and Q(c)
            polynomial[i,j]=Q(c)
        result.append(polynomial)
    return result


def add_scaled(target, polynomial, coefficient):
    for monomial,value in polynomial.items():
        changed=target.get(monomial,Q(0))+coefficient*value
        if changed:
            target[monomial]=changed
        else:
            target.pop(monomial,None)


def verify_basis_change(physical, reduced):
    source=quadric_columns(physical);target=quadric_columns(reduced)
    assert physical['active_raw_parameter_indices']==reduced['active_raw_parameter_indices']
    products=0
    for saved,expected in zip(reduced['equations'],target):
        result={}
        for index,coefficient in saved['combination']:
            add_scaled(result,source[index],Q(coefficient));products+=len(source[index])
        assert result==expected
    assert len(source)==len(target)
    return products


def verify_powers(reduced, proof):
    quadrics=quadric_columns(reduced)
    assert proof['status']=='completed'
    assert proof['active_raw_parameter_indices']==reduced['active_raw_parameter_indices']
    selected=[i for i,q in enumerate(quadrics) if len(q)<=proof['term_threshold']]
    assert selected==proof['equation_indices']
    forced=[];terms=products=0
    for identity in proof['identities']:
        index=identity['parameter_index'];power=identity['power'];result={}
        for multiplier in identity['multipliers']:
            q=multiplier['equation_index'];assert q in selected
            variables=([multiplier['linear_variable']] if power==3 else multiplier['quadratic_variables'])
            multiple={tuple(sorted((*monomial,*variables))):value for monomial,value in quadrics[q].items()}
            add_scaled(result,multiple,Q(multiplier['coefficient']))
            terms+=1;products+=len(multiple)
        assert result=={(index,)*power:Q(1)}
        forced.append(reduced['active_raw_parameter_indices'][index])
    assert len(set(forced))==len(forced)
    return dict(forced_raw_indices=forced,identities=len(forced),multiplier_terms=terms,coefficient_products=products)


def cubic_map(reduced, proof, row_bin=1, column_bin=1):
    quadrics=quadric_columns(reduced);n=len(reduced['active_raw_parameter_indices'])
    generators=[(i,k) for i in proof['equation_indices'] for k in range(n)]
    columns=[{tuple(sorted((*m,k))):c for m,c in quadrics[i].items()} for i,k in generators]
    result=packed_map(columns,row_bin,column_bin)
    assert result['shape'][1]==proof['columns']
    result['column_quadric_variable_pairs']=[list(p) for p in generators]
    return result


def check_data():
    import cyclic_fano_cubic_polars as producer
    bindings={}
    def bind(path,digest=None):
        observed=sha(path)
        if digest is not None:assert observed==digest,(path,observed,digest)
        bindings[path.relative_to(ROOT).as_posix()]=observed
        return load(path)
    packet=bind(INPUT/'packet.json');primary=bind(INPUT/'validation.json');review=bind(INPUT/'independent-validation.json')
    assert packet['schema']=='cyclic-fano-cubic-polars-v1'
    assert packet['status']=='five_component_families_excluded_full_family_open'
    assert primary['status']==review['status']=='PASS'
    assert packet['instance']=='cyclic-triple-fano' and packet['q']==1 and packet['degree']==8
    assert primary['packet_sha256']==review['primary_packet_sha256']==sha(INPUT/'packet.json')
    assert review['primary_producer_sha256']==packet['producer_sha256']
    for path,digest in [(Path(producer.__file__),packet['producer_sha256']),
                        (ROOT/'experiments/check_cyclic_fano_cubic_polars.py',review['checker_sha256']),
                        (ROOT/'results/cyclic-fano-curve/source/instance.rec',packet['source_instance_sha256'])]:
        assert sha(path)==digest
        bindings[path.relative_to(ROOT).as_posix()]=digest
    assert primary['producer_sha256']==packet['producer_sha256']
    for name,digest in packet['dependencies'].items():
        path=ROOT/'experiments'/name;assert sha(path)==digest;bindings[path.relative_to(ROOT).as_posix()]=digest
    for name,digest in review['independent_dependencies'].items():
        path=ROOT/name;assert sha(path)==digest;bindings[path.relative_to(ROOT).as_posix()]=digest
    for attempt in packet['attempts']:
        saved=bind(INPUT/attempt['file'],attempt['sha256'])
        assert saved.get('status','completed')==attempt['status']
    raw=producer.prepare()
    assert len(raw['basis'])==len(packet['parameter_basis'])==175
    for i,(actual,saved) in enumerate(zip(raw['basis'],packet['parameter_basis'])):
        assert all(actual[k]==saved[k] for k in actual)
        assert saved['E']==producer.encode(raw['Es'][i])
        assert saved['particular']==[producer.encode(v) for v in raw['Ps'][i]]
    projection=packet['projection']
    assert projection['raw_field_count']==len(projection['raw_field_labels'])==525
    assert projection['compact_count']==len(projection['compact_labels'])==175
    assert projection['compact_labels']==raw['correction_labels']
    assert len(projection['quotient_monomials'])==636 and projection['Euler_gauge_count']==246
    assert len(projection['universal_correction_relations'])==25 and projection['correction_rank_upper_bound']==150
    assert primary['full_family_remaining_open'] is True
    assert primary['universal_correction_relations']==25
    independent_projection=review['source_projection']
    assert independent_projection['status']=='PASS'
    assert [independent_projection[k] for k in ['parameters','raw_Koszul_fields','retained_correction_types',
            'universal_correction_relations','exact_correction_rank_upper_bound','quotient_directions']]==[175,525,175,25,150,636]
    dimensions=packet['full_family_dimensions']
    assert dimensions==dict(parameters=175,potential_rows=3060,pure_quadratic_columns=15400,
                           mixed_columns=30625,formal_columns=46025,full_map_constructed=False)
    monomials=[item['cubic_powers'] for item in packet['parameter_basis'][:35]]
    groups=cubic_groups(monomials)
    rounds=np.zeros((5,35),dtype=int)
    components=[];kept=[];identity_count=terms=products=basis_products=direct_squares=0
    for c,(family,primary_family,independent_family) in enumerate(zip(packet['component_families'],primary['components'],review['component_families'])):
        assert family['component_index']==c and family['component']==BASE[c]==primary_family['component']
        assert independent_family['status']=='PASS' and independent_family['component']==BASE[c]
        active=list(range(35*c,35*(c+1)));summaries=[];stages=[]
        assert len(family['stages'])==2
        for r,(info,primary_stage,independent_stage) in enumerate(zip(family['stages'],primary_family['stages'],independent_family['stages'])):
            physical=bind(INPUT/info['physical_file'],info['physical_sha256'])
            reduced=bind(INPUT/info['reduced_file'],info['reduced_sha256'])
            proof=bind(INPUT/info['cubic_file'],info['cubic_sha256'])
            assert physical['active_raw_parameter_indices']==active
            assert info['parameters']==len(active)==(35 if r==0 else 10)
            assert physical['rows']==info['physical_rows'] and physical['columns']==info['physical_columns']
            assert physical['columns']==len(active)*(len(active)+1)//2+175*len(active)
            assert physical['rank']==info['rank']==primary_stage['rank']
            assert physical['mixed_rank']==info['mixed_rank']==primary_stage['mixed_rank']
            assert independent_stage['physical']['rank']==physical['rank']
            assert independent_stage['physical']['correction_rank']==physical['mixed_rank']
            for kind in ['physical','reduced','cubic']:
                assert info[kind+'_sha256']==independent_stage[kind+'_sha256']
            assert len(physical['equations'])==info['necessary_quadrics']==physical['rank']-physical['mixed_rank']
            basis_products+=verify_basis_change(physical,reduced)
            checks=verify_powers(reduced,proof)
            assert checks['forced_raw_indices']==info['forced_raw_parameters']
            assert checks['identities']==primary_stage['cube_identities'] and checks['multiplier_terms']==primary_stage['multiplier_terms']
            assert checks['identities']==independent_stage['cubic']['coordinate_cube_identities']
            assert checks['multiplier_terms']==independent_stage['cubic']['multiplier_terms']
            assert proof['rank']==independent_stage['cubic']['exact_rank']
            assert len(checks['forced_raw_indices'])==(25 if r==0 else 10)
            if r==0:
                expected=[35*c+i for i in sorted(groups[0]+groups[1])]
                assert checks['forced_raw_indices']==expected and not primary_stage['square_query_hits']
            else:
                quadrics=quadric_columns(reduced)
                assert all({(i,i):Q(1)} in quadrics for i in range(10))
                direct_squares+=10
                assert independent_stage['basis']['singleton_square_parameters_raw']==active
                assert len(quadrics)==45 and proof['columns']==450 and proof['rank']==220
            for index in checks['forced_raw_indices']:
                rounds[c,index-35*c]=r+1
            active=[i for i in active if i not in checks['forced_raw_indices']]
            identity_count+=checks['identities'];terms+=checks['multiplier_terms'];products+=checks['coefficient_products']
            summaries.append(dict(parameters=info['parameters'],physical_rows=info['physical_rows'],physical_columns=info['physical_columns'],
                                  rank=info['rank'],correction_rank=info['mixed_rank'],quadrics=info['necessary_quadrics'],
                                  cube_rank=proof['rank'],cube_columns=proof['columns'],power_replay=checks))
            stages.append((physical,reduced,proof))
        assert active==family['remaining_raw_parameter_indices']==primary_family['remaining_parameters']==[]
        gain=family['rebuild_diagnostic']
        assert gain==dict(restricted_old_rank=45,fresh_rebuilt_rank=45,additional_independent_quadrics=0,span_inclusion=True)
        assert independent_family['rebuild_diagnostic']==dict(restricted_old_rank=45,rebuilt_rank=45,additional_independent_quadrics=0,span_inclusion=True)
        components.append(dict(component=BASE[c],name=NAMES[c],excluded=True,stages=summaries,rebuild_diagnostic=gain))
        if c==0:kept=stages
    assert len(components)==5 and identity_count==175 and terms==344 and direct_squares==50
    assert review['totals']['coordinate_cube_identities']==identity_count and review['totals']['multiplier_terms']==terms
    assert review['totals']['final_singleton_square_rows']==direct_squares
    # Actual maps are reconstructed once for the displayed component, not the whole46,025-column relaxation.
    first_physical=producer.system(kept[0][0]['active_raw_parameter_indices'],raw)
    last_physical=producer.system(kept[1][0]['active_raw_parameter_indices'],raw)
    maps={
        'polar_map':packed_map(raw['Es']),
        'initial_physical_map':packed_map(first_physical['columns'],4,8),
        'initial_cubic_map':cubic_map(kept[0][1],kept[0][2],8,8),
        'rebuilt_physical_map':packed_map(last_physical['columns'],4,3),
        'rebuilt_quadric_map':packed_map(quadric_columns(kept[1][1])),
        'final_cubic_map':cubic_map(kept[1][1],kept[1][2])}
    for key,physical in [('initial_physical_map',kept[0][0]),('rebuilt_physical_map',kept[1][0])]:
        assert maps[key]['shape']==[physical['rows'],physical['columns']]
    assert maps['polar_map']['shape']==[409,175] and maps['polar_map']['nonzero_coefficients']==1085
    assert maps['final_cubic_map']['shape']==[220,450]
    ambient_rows=dict(polar_map=495,initial_physical_map=3060,initial_cubic_map=7770,
                      rebuilt_physical_map=3060,rebuilt_quadric_map=55,final_cubic_map=220)
    for key,matrix in maps.items():
        matrix['ambient_row_count']=ambient_rows[key]
        matrix['zero_rows_omitted']=ambient_rows[key]-matrix['shape'][0]
        assert matrix['zero_rows_omitted']>=0
        matrix['row_order']='Lexicographic order of the listed supported monomials; zero rows omitted.'
    labels={
        'polar_map':('direction coefficient','supported degree-8 monomial','409 × 175; rank 175 by the checked minor.\n1,085 exact nonzero coefficients.'),
        'initial_physical_map':('quadratic + correction-product column','supported degree-14 monomial','X0 component: 2,793 × 6,755.\nRank 1,687; correction rank 1,479.'),
        'initial_cubic_map':('quadric × parameter','supported cubic parameter monomial',f"{maps['initial_cubic_map']['shape'][0]:,} × 7,280; exact rank 5,590.\n25 cube identities; 10 parameters remain."),
        'rebuilt_physical_map':('quadratic + correction-product column','supported degree-14 monomial','10 parameters: 2,348 × 1,805.\nRank 1,019; correction rank 974.'),
        'rebuilt_quadric_map':('necessary quadric','supported quadratic parameter monomial',f"45 quadrics; {maps['rebuilt_quadric_map']['shape'][0]} of 55 monomial rows.\nAll 10 coordinate squares occur directly."),
        'final_cubic_map':('quadric × surviving parameter','cubic parameter monomial','220 × 450; full image, rank 220.\nSaved cubes are one-term square multiples.')}
    for key,(col,row,caption) in labels.items():
        maps[key].update(column_label=col,row_label=row,caption=caption)
    comparisons=[]
    constant=bind(ROOT/'results/cyclic-fano-polar-family/packet.json')
    linear=bind(ROOT/'results/cyclic-fano-linear-polars/packet.json')
    quadratic=bind(ROOT/'results/cyclic-fano-quadratic-polars/packet.json')
    closure=bind(ROOT/'results/cyclic-fano-remaining66-multipliers/packet.json')
    assert len(constant['basis'])==5 and constant['complete_corrections_per_E']==25 and constant['quotient_dimension']==15
    assert len(linear['basis'])==25 and linear['projection']['raw_fields_per_denominator']==85
    assert len(linear['projection']['surviving_constant_base_pairs'])==10 and linear['projection']['quotient_projection_identities']==75
    assert len(quadratic['parameter_basis'])==75 and quadratic['projection']['raw_field_count']==230
    assert quadratic['projection']['compact_generator_count']==55 and quadratic['projection']['quotient_projection_identities']==246
    assert closure['status']=='full_quadratic_direction_family_excluded'
    for name in ['cyclic-fano-polar-family','cyclic-fano-linear-polars','cyclic-fano-quadratic-polars','cyclic-fano-remaining66-multipliers']:
        older=bind(ROOT/'results'/name/'independent-validation.json')
        assert older['status']=='PASS' and older['packet_lf_sha256']==sha(ROOT/'results'/name/'packet.json')
    for name,d,p,raw_count,retained,quotients,status in [('constant',5,5,25,0,15,'excluded'),('linear',6,25,85,10,75,'excluded'),
          ('quadratic',7,75,230,55,246,'excluded'),('cubic',8,175,525,175,636,'open; component cases excluded')]:
        comparisons.append(dict(direction=name,degree=d,parameters=p,raw_corrections=raw_count,retained_corrections=retained,quotient_directions=quotients,scope=status))
    gpu=bind(ROOT/'results/cyclic-fano-cubic-gpu/report.json')
    assert review['gpu_report_lf_sha256']==sha(ROOT/'results/cyclic-fano-cubic-gpu/report.json')
    assert gpu['status']=='PASS' and gpu['prime']==65521 and len(gpu['cases'])==16
    for name,digest in gpu['bindings'].items():
        path=ROOT/name;assert sha(path)==digest
        bindings[path.relative_to(ROOT).as_posix()]=digest
    fixed_review=review['fixed_direction_minor_audit']
    assert fixed_review['status']=='PASS' and fixed_review['nonzero_minors_checked']==16
    fixed=[]
    for case,checked in zip(gpu['cases'],fixed_review['cases']):
        assert case['matrix_sha256']==checked['matrix_sha256'] and case['kind']==checked['kind']
        assert [case['rank_mod_prime'],case['augmented_rank_mod_prime']]==[150,151]
        assert case['consistent_control_ranks']==[150,150]
        assert checked['rational_rank_upper_bound']==150 and checked['augmented_minor_size']==151
        assert checked['nonzero_determinant_mod_prime']==case['augmented_minor_determinant_mod_prime']!=0
        fixed.append(dict(kind=case['kind'],direction=case['direction'],matrix_sha256=case['matrix_sha256'],
                          coefficient_rank=150,augmented_rank=151,prime=65521,
                          consistent_control_ranks=case['consistent_control_ranks'],
                          minor_determinant_mod_prime=case['augmented_minor_determinant_mod_prime']))
    assert sum(c['kind']=='monomial-control' for c in fixed)==5 and len(fixed)==16
    assert [c['kind'] for c in fixed]==['monomial-control']*5+['two-component']*5+['seeded-eight-term']*3+['seeded-dense']*3
    relation_columns=[{} for _ in range(175)]
    for i,relation in enumerate(projection['universal_correction_relations']):
        entries={j:Q(c) for j,c in relation['terms']}
        assert len(entries)==len(relation['terms'])
        assert {j:c for j,c in entries.items() if j>=150}=={150+i:Q(3)}
        for j,c in entries.items():relation_columns[j][(i,)]=c
    relation_map=packed_map(relation_columns)
    assert relation_map['shape']==[25,175]
    gpu_summary=dict(device=gpu['device'],prime=gpu['prime'],seed=gpu['seed'],
                     cpu_checked_matrices=gpu['cpu_checked_matrices'],constructed_consistent_controls=gpu['constructed_consistent_controls'],
                     toy_controls=gpu['toy_controls'],construction_seconds=gpu['construction_seconds'],
                     gpu_rank_seconds=gpu['gpu_rank_seconds'],cpu_rank_seconds=gpu['cpu_rank_seconds'],
                     relation_map=relation_map,actual_GPU_columns=175,
                     timing_scope='GPU elimination only, excluding compilation, upload and minor extraction; batch-specific CPU comparison, no general speedup claim.',
                     roles='AI-assisted design/code; GPU modular rank computations; CPU exact operator relations and nonzero-minor replay.')
    assert [gpu_summary[k] for k in ['cpu_checked_matrices','constructed_consistent_controls','toy_controls']]==[32,16,3]
    return dict(schema='cyclic-fano-cubic-polars-figures-v1',source_sha256=bindings,components=components,
                cubic_monomials=monomials,cubic_groups=groups,conditional_parameter_rounds=rounds.tolist(),
                degree_comparison=comparisons,maps=maps,identity_replay=dict(cubes=identity_count,multiplier_terms=terms,
                    coefficient_products=products,basis_combination_products=basis_products,direct_final_squares=direct_squares),
                correction_caption='175 retained types have 25 exact universal relations: rank ≤150 for each fixed denominator; these are not 175 independent corrections.',
                limits='Each35→10→0 proof sets the other four vector components to zero. The full175-dimensional family remains open. Rebuilding gains0 independent quadrics here.',
                full_family_dimensions=dimensions,representative_component='X0',fixed_direction_tests=fixed,gpu_summary=gpu_summary)


def save(fig, name):
    OUT.mkdir(parents=True,exist_ok=True)
    fig.savefig(OUT/(name+'.png'),dpi=160,facecolor=PAPER)
    target = OUT/(name+'.svg')
    fig.savefig(target,facecolor=PAPER,metadata={'Date':None})
    target.write_text('\n'.join(line.rstrip() for line in target.read_text(encoding='utf-8').splitlines())+'\n',
                      encoding='utf-8',newline='\n')
    plt.close(fig)


def feature(data):
    fig=plt.figure(figsize=(17,11),facecolor=PAPER)
    fig.text(.05,.947,'Cubic polar directions: five separate component searches',fontsize=26,weight='bold')
    fig.text(.05,.906,'cyclic-triple-fano · discussion #112   |   Degree 8 denominators',fontsize=14,color=MUTED)
    fig.text(.05,.862,r'Each row assumes $v=f\,\partial_{x_i}$, with $f$ an arbitrary cubic and every other component zero.',fontsize=16)
    fig.text(.05,.823,'These conditional proofs do not exclude the full 175-parameter mixed-component family.',fontsize=15,color=CORAL,weight='bold')
    ax=fig.add_axes([.085,.525,.76,.235])
    order=[i for group in data['cubic_groups'] for i in group]
    grid=np.array(data['conditional_parameter_rounds'])[:,order]
    ax.imshow(grid,aspect='auto',cmap=ListedColormap([GREY,'#A4CBC4','#C9BDE1']),vmin=0,vmax=2)
    ax.set_yticks(range(5),[r'$v_{X_0}$',r'$v_{X_1}$',r'$v_{Y_0}$',r'$v_{Y_1}$',r'$v_{Y_2}$'],fontsize=15)
    ax.set_xticks(range(35),[monomial_label(data['cubic_monomials'][i]) for i in order],rotation=50,ha='right',fontsize=10.5)
    ax.set_xticks(np.arange(-.5,35,1),minor=True);ax.set_yticks(np.arange(-.5,5,1),minor=True)
    ax.grid(which='minor',color=PAPER,linewidth=1.2);ax.tick_params(which='both',length=0)
    for spine in ax.spines.values():spine.set_visible(False)
    for a,b,label in [(0,5,'5 pure cubes'),(5,25,'20 square × linear monomials'),(25,35,'10 squarefree triples')]:
        ax.text((a+b-1)/2,-.79,label,ha='center',va='bottom',fontsize=12,color=MUTED)
    for i,component in enumerate(data['components']):
        ax.text(35.25,i,'35 → 10 → 0' if component['excluded'] else 'unresolved',fontsize=11,va='center',color=TEAL if component['excluded'] else CORAL)
    fig.text(.05,.438,'Teal: 25 coefficient cubes.   Purple: 10 direct squares after reduction and rebuilding.',fontsize=13)
    fig.text(.05,.396,'All 175 correction types remain available at both stages; color marks a proof round, not a parameter value.',fontsize=12,color=MUTED)
    fig.text(.05,.344,'Why the next degree is a larger problem',fontsize=18,weight='bold')
    tax=fig.add_axes([.05,.155,.90,.155]);tax.axis('off')
    rows=[[r['direction'],r['degree'],r['parameters'],r['raw_corrections'],r['retained_corrections'],r['quotient_directions'],r['scope']]
          for r in data['degree_comparison']]
    tab=tax.table(cellText=rows,colLabels=['Direction','Denominator\ndegree','Parameters','Raw Koszul\nfields','Retained\ntypes','Quotient\ndirections','Joint-family status'],
                  colWidths=[.13,.11,.09,.12,.10,.12,.23],cellLoc='left',colLoc='left',bbox=[0,0,1,1])
    tab.auto_set_font_size(False);tab.set_fontsize(11.5)
    for (r,c),cell in tab.get_celld().items():
        cell.set_edgecolor('#D5DDD7');cell.set_linewidth(.6)
        cell.set_facecolor('#E7EEE8' if r==0 else PAPER)
        cell.get_text().set_color(INK)
        if r==0:cell.get_text().set_weight('bold')
    fig.text(.05,.105,data['correction_caption'],fontsize=12,color=MUTED)
    fig.text(.05,.061,'Initial square tests failed. Rebuilding then simplifies the equations; it adds no independent quadrics in these five cases.',fontsize=12,color=MUTED)
    fig.text(.05,.023,'This is a family search with exact witnesses. It is not a certificate of existence or a solution of the instance.',fontsize=12,color=CORAL)
    save(fig,'cyclic-fano-cubic-polars')


def companion(data):
    fig=plt.figure(figsize=(17,12.5),facecolor=PAPER)
    fig.text(.05,.951,'From cubic directions to the actual coefficient maps',fontsize=25,weight='bold')
    fig.text(.05,.915,'cyclic-triple-fano · discussion #112   |   A representative one-component proof; the full mixed family is open',fontsize=13.5,color=MUTED)
    fig.text(.05,.878,'16 fixed directions also fail: exact rank 150 versus augmented rank 151 (5 controls, 11 mixed tests).',fontsize=12.5,color=TEAL)
    specs=[(.065,.565,.25,.265,'polar_map','Polar construction: v → E'),
           (.380,.565,.25,.265,'initial_physical_map','Initial physical equations'),
           (.695,.565,.25,.265,'initial_cubic_map','First polynomial multipliers'),
           (.065,.165,.25,.265,'rebuilt_physical_map','Rebuilt physical equations'),
           (.380,.165,.25,.265,'rebuilt_quadric_map','Correction-free quadrics'),
           (.695,.165,.25,.265,'final_cubic_map','Saved cubic map; squares suffice')]
    for x,y,w,h,key,title in specs:
        ax=fig.add_axes([x,y,w,h]);m=data['maps'][key]
        draw_map(ax,m,PURPLE if 'cubic' in key else TEAL)
        ax.set_title(title,loc='left',fontsize=15,pad=15)
        ax.set_xlabel(m['column_label'],fontsize=10)
        ax.set_ylabel(m['row_label'],fontsize=10)
        fig.text(x,y-.065,m['caption'],fontsize=11,color=MUTED,linespacing=1.4)
    fig.text(.05,.060,'Colors record exact nonzero coefficients. Display bins and any omitted zero rows are specified in plot-data.json.',fontsize=11.5,color=MUTED)
    fig.text(.05,.025,'Matrix ranks describe finite coefficient spaces; they are not dimensions or counts of geometric solutions.',fontsize=12,color=CORAL)
    save(fig,'cyclic-fano-cubic-polars-maps')


def gpu_hero(data):
    from matplotlib.patches import FancyBboxPatch
    fig=plt.figure(figsize=(17,11.5),facecolor=PAPER)
    fig.text(.05,.951,'GPU rank tests meet exact column relations',fontsize=29,weight='bold')
    fig.text(.05,.908,'cyclic-triple-fano · discussion #112   |   Degree 8, fixed denominator tests   |   '+data['gpu_summary']['device'],fontsize=13,color=MUTED)
    rel=data['gpu_summary']['relation_map']
    ax=fig.add_axes([.065,.602,.405,.217]);draw_map(ax,rel,PURPLE)
    ax.axvline(150,color=CORAL,lw=1.2)
    ax.set_title('The actual 25 × 175 relation matrix',loc='left',fontsize=16,pad=17)
    ax.set_ylabel('independent relation',fontsize=11)
    ax.set_xlabel('150 base-pair types  |  25 mixed types',fontsize=11)
    fig.text(.065,.538,f"{rel['nonzero_coefficients']} rational nonzeros; the last block is exactly 3I.",fontsize=12,color=MUTED)
    fig.text(.545,.825,r'$175\;\longrightarrow\;\leq150$',fontsize=38,weight='bold',color=TEAL,va='top')
    fig.text(.545,.755,'25 exact relations hold for every homogeneous\ndegree-eight denominator in this construction.',fontsize=16,linespacing=1.45,va='top')
    fig.text(.545,.680,'The GPU run keeps all 175 columns.\nThe relations prove the rank bound used to certify\nthe result; no compression speedup was measured.',fontsize=12.5,color=MUTED,linespacing=1.5,va='top')
    fig.text(.05,.502,'What the GPU actually computed: ranks modulo 65,521',fontsize=18,weight='bold')
    ranks=np.array([[case['coefficient_rank'] for case in data['fixed_direction_tests']],
                    [case['augmented_rank'] for case in data['fixed_direction_tests']],
                    [case['consistent_control_ranks'][1] for case in data['fixed_direction_tests']]])
    ax=fig.add_axes([.125,.330,.825,.125])
    ax.imshow(ranks,aspect='auto',cmap=ListedColormap(['#D7E8E3','#ECC8C2']),vmin=150,vmax=151)
    for i in range(3):
        for j in range(16):ax.text(j,i,str(ranks[i,j]),ha='center',va='center',fontsize=12,color=CORAL if i==1 else TEAL,weight='bold')
    ax.set_yticks(range(3),[r'$M$',r'$[M\mid b]$',r'$[M\mid Mz]$'],fontsize=15)
    labels=['C'+str(i+1) for i in range(5)]+['T'+str(i+1) for i in range(5)]+['S'+str(i+1) for i in range(3)]+['D'+str(i+1) for i in range(3)]
    ax.set_xticks(range(16),labels,fontsize=11)
    ax.set_xticks(np.arange(-.5,16,1),minor=True);ax.set_yticks(np.arange(-.5,3,1),minor=True)
    ax.grid(which='minor',color=PAPER,lw=1.5);ax.tick_params(which='both',length=0)
    for spine in ax.spines.values():spine.set_visible(False)
    fig.text(.05,.285,'C: 5 prior-covered controls   ·   T: 5 two-component   ·   S: 3 sparse   ·   D: 3 dense seeded directions',fontsize=12,color=MUTED)
    fig.text(.05,.250,'32 CPU rank cross-checks · 16 constructed consistent controls · 16 nonzero augmented 151 × 151 minors',fontsize=12.5,weight='bold')
    times=[('Polynomial construction','construction_seconds'),('GPU modular elimination','gpu_rank_seconds'),('CPU modular rank checks','cpu_rank_seconds')]
    for j,(label,key) in enumerate(times):
        x=.05+j*.305
        fig.add_artist(FancyBboxPatch((x,.142),.278,.080,boxstyle='round,pad=.007,rounding_size=.008',
                       transform=fig.transFigure,facecolor='#ECF0EA',edgecolor='#D2DBD3',lw=.8))
        fig.text(x+.012,.202,label,fontsize=11.5,color=MUTED)
        fig.text(x+.012,.161,f"{data['gpu_summary'][key]:.3f} s",fontsize=22,weight='bold',color=TEAL)
    fig.text(.05,.112,'Times are for this batch. GPU timing excludes compilation, uploads and minor extraction; no general speedup is claimed.',fontsize=10.5,color=MUTED)
    fig.text(.05,.070,r'CPU exact bound $\mathrm{rank}(M)\leq150$ + nonzero 151-minor $\Longrightarrow$ 16 fixed denominators excluded over $\mathbb{C}$.',fontsize=15,weight='bold')
    fig.text(.05,.026,'AI assisted design and code. GPU performed rank tests; CPU replay certifies the obstructions. The full 175-parameter family remains open.',fontsize=11.5,color=CORAL)
    save(fig,'cyclic-fano-cubic-gpu-shortcut')


def main():
    assert __debug__,'Run without -O so all source and identity checks remain enabled.'
    plt.rcParams.update({'font.family':'DejaVu Sans','text.color':INK,'axes.labelcolor':INK,
                         'svg.fonttype':'none','svg.hashsalt':'cyclic-fano-cubic-polars-v1'})
    data=check_data();feature(data);companion(data);gpu_hero(data)
    data['renderer_lf_sha256']=sha(Path(__file__))
    (OUT/'plot-data.json').write_text(json.dumps(data,separators=(',',':'))+'\n',encoding='utf-8',newline='\n')
    assert all(sha(ROOT/path)==digest for path,digest in data['source_sha256'].items())
    print(json.dumps(dict(status='PASS',source_bindings=len(data['source_sha256']),
                         identity_replay=data['identity_replay'],fixed_direction_tests=len(data['fixed_direction_tests']),
                         conditional_components=len(data['components']),full_family_open=True,
                         plot_data_bytes=(OUT/'plot-data.json').stat().st_size)))


if __name__=='__main__':
    main()
