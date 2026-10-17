#!/usr/bin/env python3
"""Reproducible figures for the full quadratic-direction multiplier search.

Only identities from the checked full-family packet can eliminate a parameter
here. Earlier restricted-family results do not set full-family parameters to
zero. Monomials are stored as short sorted index tuples to avoid expanding
large cubic maps into 75-component exponent vectors.
"""
from __future__ import annotations

from fractions import Fraction as Q
import base64
import gzip
import hashlib
from itertools import combinations_with_replacement
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT/'results/cyclic-fano-full-quadratic-multipliers'
OUT = ROOT/'results/cyclic-fano-full-quadratic-multipliers-figures'
INK, MUTED, PAPER = '#17323B', '#53666D', '#FAFAF5'
TEAL, PURPLE, CORAL = '#166A70', '#7967AA', '#B94D42'
NAMES = ('X0', 'X1', 'Y0', 'Y1', 'Y2')


def sha(path):
    raw = path.read_bytes()
    return hashlib.sha256(raw if path.suffix == '.gz' else raw.replace(b'\r\n', b'\n')).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def load_stage(path):
    return json.loads(gzip.decompress(path.read_bytes()))


def decode_stage(stage):
    quadrics = []
    n=len(stage['active_raw_parameter_indices'])
    for equation in stage['equations']:
        polynomial = {}
        for i,j,coefficient in equation['terms']:
            assert 0 <= i <= j < n and (i,j) not in polynomial
            coefficient = Q(coefficient)
            assert coefficient
            polynomial[i,j] = coefficient
        quadrics.append(polynomial)
    return quadrics


def compact_polynomial(terms, degree):
    out = {}
    for term in terms:
        m = tuple(i for i, power in enumerate(term['powers']) for _ in range(power))
        assert len(m) == degree and m not in out
        coefficient = Q(term['coefficient'])
        assert coefficient
        out[m] = coefficient
    return out


def add_scaled(result, polynomial, coefficient):
    for m, value in polynomial.items():
        updated = result.get(m, Q(0)) + coefficient*value
        if updated:
            result[m] = updated
        else:
            result.pop(m, None)


def linear_multiple(polynomial, variable):
    return {tuple(sorted((*m, variable))): c for m, c in polynomial.items()}


def packed_occupancy(occupied, shape):
    grid=np.zeros(shape,dtype=np.uint8)
    for r,c in occupied:
        grid[r,c]=1
    return base64.b64encode(np.packbits(grid.reshape(-1),bitorder='big').tobytes()).decode('ascii')


def multiplier_map(quadrics, generators, row_bin=1, col_bin=1, rows=None):
    """Stream supports twice; never allocate the full rational Macaulay map."""
    if rows is None:
        rows = sorted({tuple(sorted((*m, variable))) for q, variable in generators for m in quadrics[q]})
    lookup = {m: i for i, m in enumerate(rows)}
    occupied = set()
    nonzero = 0
    for j, (q, variable) in enumerate(generators):
        for m in quadrics[q]:
            key = tuple(sorted((*m, variable)))
            occupied.add((lookup[key]//row_bin, j//col_bin))
            nonzero += 1
    nr, nc = len(rows), len(generators)
    bin_shape=[(nr+row_bin-1)//row_bin,(nc+col_bin-1)//col_bin]
    return dict(shape=[nr,nc], row_monomial_indices=[list(m) for m in rows],
                column_equation_variable_pairs=[list(g) for g in generators],
                nonzero_coefficients=nonzero, bin_size=[row_bin,col_bin],
                binned_shape=bin_shape, occupied_bin_count=len(occupied),
                occupancy_bits_base64=packed_occupancy(occupied,bin_shape),
                bit_encoding='Row-major occupancy bits, most significant bit first; zero-padded final byte; base64.',
                bin_rule='Occupied iff at least one exact nonzero coefficient lies in this bin.')


def quadric_map(quadrics, row_bin=1, col_bin=1):
    rows = sorted({m for q in quadrics for m in q})
    lookup = {m: i for i,m in enumerate(rows)}
    occupied = {(lookup[m]//row_bin, j//col_bin) for j,q in enumerate(quadrics) for m in q}
    nr, nc = len(rows),len(quadrics)
    bin_shape=[(nr+row_bin-1)//row_bin,(nc+col_bin-1)//col_bin]
    return dict(shape=[nr,nc], row_monomial_indices=[list(m) for m in rows],
                nonzero_coefficients=sum(map(len,quadrics)), bin_size=[row_bin,col_bin],
                binned_shape=bin_shape, occupied_bin_count=len(occupied),
                occupancy_bits_base64=packed_occupancy(occupied,bin_shape),
                bit_encoding='Row-major occupancy bits, most significant bit first; zero-padded final byte; base64.',
                bin_rule='Occupied iff at least one exact nonzero coefficient lies in this bin.')


def verify_cubes(stage,quadrics,proof):
    active=stage['active_raw_parameter_indices'];n=len(active)
    assert proof['status']=='completed' and proof['coefficient_field']=='Q'
    assert proof['active_raw_parameter_indices']==active
    selected=[j for j,q in enumerate(quadrics) if len(q)<=proof['term_threshold']]
    assert proof['equation_indices']==selected and proof['columns']==n*len(selected)
    seen=set();terms=products=0
    for identity in proof['identities']:
        k=identity['parameter_index']
        assert 0<=k<n and k not in seen and identity['power']==3
        seen.add(k);total={}
        for term in identity['multipliers']:
            q,j=term['equation_index'],term['linear_variable']
            assert q in selected and 0<=j<n
            column=linear_multiple(quadrics[q],j)
            add_scaled(total,column,Q(term['coefficient']))
            terms+=1;products+=len(column)
        assert total=={(k,k,k):Q(1)}
    assert proof['remaining_local_parameters']==[j for j in range(n) if j not in seen]
    return dict(forced_raw_indices=[active[j] for j in sorted(seen)],identities=len(seen),
                multiplier_terms=terms,coefficient_products=products,selected_quadrics=len(selected),
                columns=proof['columns'],exact_rank=proof['rank'],term_threshold=proof['term_threshold'])


def check_data():
    packet_path,primary_path,review_path=[INPUT/name for name in ('packet.json','validation.json','independent-validation.json')]
    packet,primary,review=map(load,(packet_path,primary_path,review_path))
    producer_path=ROOT/'experiments/cyclic_fano_full_quadratic_multipliers.py'
    checker_path=ROOT/'experiments/check_cyclic_fano_full_quadratic_multipliers.py'
    raw=ROOT/'results/cyclic-fano-curve/source/instance.rec'
    assert packet['schema']=='cyclic-fano-full-quadratic-multipliers-v1'
    assert primary['schema']=='cyclic-fano-full-quadratic-multipliers-validation-v1'
    assert review['schema']=='cyclic-fano-full-quadratic-multipliers-independent-v1'
    assert packet['status']=='checked_partial_progress' and primary['status']==review['status']=='PASS'
    assert packet['instance']=='cyclic-triple-fano' and packet['degree']==7 and packet['q']==1
    assert packet['producer_sha256']==primary['producer_sha256']==sha(producer_path)
    assert primary['packet_sha256']==review['packet_lf_sha256']==sha(packet_path)
    assert review['primary_validation_lf_sha256']==sha(primary_path)
    assert review['checker_lf_sha256']==sha(checker_path)
    assert packet['source_instance_sha256']==review['source_instance_lf_sha256']==sha(raw)
    bindings={p.relative_to(ROOT).as_posix():sha(p) for p in
              (packet_path,primary_path,review_path,producer_path,checker_path,raw)}
    for dependencies in (packet['dependencies'],review['independent_arithmetic_dependencies']):
        for name,digest in dependencies.items():
            p=ROOT/'experiments'/name
            assert sha(p)==digest
            bindings[p.relative_to(ROOT).as_posix()]=digest
    projection=packet['prior_projection_proof']
    prior_path=ROOT/projection['packet'];prior_primary=prior_path.parent/'validation.json';prior_review=prior_path.parent/'independent-validation.json'
    assert sha(prior_path)==projection['packet_sha256']
    assert sha(prior_primary)==projection['primary_receipt_sha256']
    assert sha(prior_review)==projection['independent_receipt_sha256']
    prior=load(prior_path)
    assert prior['status']==load(prior_primary)['status']==load(prior_review)['status']=='PASS'
    assert projection['raw_Koszul_fields']==230 and projection['compact_correction_types']==55 and projection['quotient_directions']==246
    for p in (prior_path,prior_primary,prior_review):
        bindings[p.relative_to(ROOT).as_posix()]=sha(p)
    labels=packet['parameter_order'];assert len(labels)==75
    spatial=packet['symmetry']['spatial_weights'];assert spatial==[0,4,0,1,1,5]
    assert packet['symmetry']['beta_and_A_charge']==3 and packet['symmetry']['modulus']==6
    weights=[]
    for k,label in enumerate(labels):
        basis=prior['parameter_basis'][k]
        assert label['component']==basis['component'] and label['quadratic_powers']==basis['quadratic_powers']
        weight=(sum(a*w for a,w in zip(label['quadratic_powers'],spatial))-spatial[label['component']])%6
        assert label['charge']==weight
        weights.append(weight)
    assert [weights.count(k) for k in range(6)]==[12,16,11,11,13,12]
    assert labels[61]['component']==5 and labels[61]['quadratic_powers']==[1,1,0,0,0,0]
    stage_data=[];checks=[];rounds=[];expected_active=list(range(75))
    assert len(packet['stages'])==len(primary['stage_checks'])==len(review['stages'])==3
    for index,info in enumerate(packet['stages']):
        path=INPUT/info['quadrics_file'];compressed=path.read_bytes();payload=gzip.decompress(compressed)
        assert hashlib.sha256(compressed).hexdigest()==info['quadrics_sha256']
        assert hashlib.sha256(payload).hexdigest()==info['quadrics_uncompressed_sha256']
        bindings[path.relative_to(ROOT).as_posix()]=sha(path)
        stage=json.loads(payload);quadrics=decode_stage(stage)
        active=stage['active_raw_parameter_indices']
        assert active==expected_active and len(active)==info['parameters']
        for source_key,summary_key in (('rows','physical_rows'),('columns','physical_columns'),('rank','rank'),('mixed_rank','mixed_rank')):
            assert stage[source_key]==info[summary_key]
        assert len(quadrics)==info['necessary_quadrics']==stage['rank']-stage['mixed_rank']
        assert stage['mixed_columns']==55*len(active)
        assert stage['pure_columns']==len(active)*(len(active)+1)//2
        local_weights=[weights[k] for k in active]
        for equation,polynomial in zip(stage['equations'],quadrics):
            assert {(local_weights[i]+local_weights[j])%6 for i,j in polynomial}=={equation['charge']}
            assert all((sum(a*w for a,w in zip(m,spatial))-3)%6==equation['charge'] for m,c in equation['dual'])
        proof_path=INPUT/info['cube_proof_file']
        assert hashlib.sha256(proof_path.read_bytes()).hexdigest()==info['cube_proof_sha256']
        bindings[proof_path.relative_to(ROOT).as_posix()]=sha(proof_path)
        proof=load(proof_path);check=verify_cubes(stage,quadrics,proof)
        assert check['forced_raw_indices']==info['newly_forced_raw_parameters']
        primary_stage=primary['stage_checks'][index];review_stage=review['stages'][index]
        assert review_stage['index']==info['index']==index
        for key in ('parameters','physical_rows','physical_columns','rank','mixed_rank'):
            assert review_stage[key]==info[key]
        for key in ('rank','mixed_rank'):
            assert primary_stage[key]==stage[key]
        assert primary_stage['physical_duals']==len(quadrics)
        assert primary_stage['individual_squares_in_quadric_span']==review_stage['isolated_squares']==[]
        small=review_stage['selected_cubic_space'];primary_small=primary_stage['selected_cubic_space']
        assert small['exact_rank']==check['exact_rank']==primary_small['rank']
        assert small['multiplier_generators']==check['columns']==primary_small['columns']
        assert small['multiplier_terms']==check['multiplier_terms']
        assert small['forced_raw_parameters']==check['forced_raw_indices']
        assert small['forced_local_parameters']==primary_small['exact_cube_indices']
        assert small['selected_quadrics']==check['selected_quadrics']
        assert small['term_threshold']==check['term_threshold']
        assert review_stage['quadrics_binary_sha256']==info['quadrics_sha256']
        expected_active=[k for k in active if k not in check['forced_raw_indices']]
        if check['forced_raw_indices']:
            rounds.append(check['forced_raw_indices'])
        checks.append(check);stage_data.append((stage,quadrics))
    assert rounds==[[8,13,26,28,38,53,56,61],[66]]
    assert expected_active==packet['remaining_raw_parameter_indices'] and len(expected_active)==66
    assert sum(c['identities'] for c in checks)==9 and sum(c['multiplier_terms'] for c in checks)==130
    assert review['coordinate_cube_identities']==9 and review['cube_multiplier_terms']==130
    assert review['forced_raw_parameter_indices']==sum(rounds,[])
    assert review['remaining_raw_parameter_indices']==expected_active
    assert review['necessary_quadric_identities']==1200
    assert review['exact_failed_square_queries']==208
    assert review['retained_correction_types']==55 and review['quotient_directions_replayed']==246
    assert packet['rebuild_diagnostics']==[
        dict(stage=1,restricted_old_rank=391,rebuilt_rank=396,added_independent_quadrics=5,span_inclusion=True),
        dict(stage=2,restricted_old_rank=393,rebuilt_rank=393,added_independent_quadrics=0,span_inclusion=True)]
    assert [dict(stage=g['stage'],restricted_old_rank=g['restricted_initial_rank'],
                 rebuilt_rank=g['fresh_rank'],added_independent_quadrics=g['additional_quadrics'],
                 span_inclusion=g['span_inclusion']) for g in review['rebuild_diagnostics']]==packet['rebuild_diagnostics']

    attempts={}
    review_attempts={entry['file']:entry for entry in review['attempt_checks']}
    assert len(review_attempts)==len(packet['attempts'])
    for entry in packet['attempts']:
        path=INPUT/entry['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==entry['sha256']
        bindings[path.relative_to(ROOT).as_posix()]=sha(path)
        attempt=load(path);assert attempt['status']==entry['status'];attempts[entry['file']]=attempt
        assert review_attempts[entry['file']]['sha256']==entry['sha256']
    quartic=attempts['stage-02-quartic-4.json'];quartic_check=review_attempts['stage-02-quartic-4.json']
    assert quartic['status']=='completed' and quartic['coefficient_field']=='Q' and quartic['degree']==4
    assert quartic['active_raw_parameter_indices']==expected_active and quartic['term_threshold']==4
    assert quartic['equation_indices']==[j for j,q in enumerate(stage_data[2][1]) if len(q)<=4]
    assert len(quartic['equation_indices'])==quartic_check['selected_quadrics']==40
    assert quartic['columns']==quartic_check['multiplier_generators']==40*66*67//2==88440
    assert quartic['rank']==quartic_check['exact_rank']==85051
    assert quartic['coordinate_fourth_powers_found']==quartic_check['coordinate_fourth_powers']==[]
    assert primary['quartic_checks']==[dict(file='stage-02-quartic-4.json',rank=85051,columns=88440,
                                           coordinate_fourth_powers_found=[])]
    stage,quadrics=stage_data[0]
    example={}
    add_scaled(example,linear_multiple(quadrics[401],61),Q(2))
    add_scaled(example,linear_multiple(quadrics[402],60),Q(-2))
    assert example=={(61,61,61):Q(1)}
    blocks={};maps={}
    for charge in (0,3):
        block=attempts[f'charge{charge}-probe.json']
        replay=review_attempts[f'charge{charge}-probe.json']
        assert block['status']=='sparse_fill_limit' and block['rank_scope']=='processed_generator_prefix'
        assert block['prime']==1009 and block['processed_generators']<block['columns']
        assert block['pivot_nonzero_entries']>3000000 or block['update_operations']>100000000
        for key in ('charge','prime','processed_generators','columns','rank_mod_prime'):
            assert replay[key]==block[key]
        assert replay['scope']=='processed_generator_prefix'
        generators=[(q,k) for q,e in enumerate(stage['equations']) for k,w in enumerate(weights) if (e['charge']+w)%6==charge]
        rows=[m for m in combinations_with_replacement(range(75),3) if sum(weights[j] for j in m)%6==charge]
        assert len(rows)==block['potential_rows']==block['active_rows']
        assert len(generators)==block['columns']
        assert block['coordinate_cube_targets']==[j for j,w in enumerate(weights) if 3*w%6==charge]
        actual=multiplier_map(quadrics,generators,20,8,rows)
        assert actual['shape']==[block['active_rows'],block['columns']]
        # The rational support really occupies every listed row; no omitted row is hidden.
        covered={tuple(sorted((*m,k))) for q,k in generators for m in quadrics[q]}
        assert len(covered)==len(rows)
        blocks[str(charge)]=block;maps[f'charge{charge}_map']=actual
    assert set(blocks['0']['coordinate_cube_targets']) | set(blocks['3']['coordinate_cube_targets'])==set(range(75))
    return dict(schema='cyclic-fano-full-quadratic-multipliers-plot-v1',instance='cyclic-triple-fano',discussion_number=112,
                source_sha256=bindings,plot_source_sha256=sha(Path(__file__)),
                sha256_policy='Text: CRLF normalized to LF. Gzip inputs: exact compressed bytes; payload hashes also checked.',
                parameter_order=labels,quadratic_monomials=[p['quadratic_powers'] for p in labels[:15]],
                exact_rounds=rounds,forced_raw_indices=sorted(set().union(*map(set,rounds))),
                remaining_raw_indices=expected_active,exact_cube_checks=checks,
                stages=packet['stages'],rebuild_diagnostics=packet['rebuild_diagnostics'],attempts=attempts,
                independent_validation=dict(necessary_quadric_identities=review['necessary_quadric_identities'],
                    physical_coefficient_pairings=review['physical_coefficient_pairings'],
                    negative_controls_rejected=review['negative_controls_rejected']),
                selected_quartic_check=quartic_check,
                initial_quadric_map=quadric_map(quadrics,6,1),blocks=blocks,**maps,
                example_identity=dict(target_parameter=61,power=3,terms=[[401,61,'2'],[402,60,'-2']]),
                rebuild_caption='Rebuilding: 75 → 67 → 66 parameters. First rebuild adds five independent quadrics; the next adds none.',
                bin_caption='Display bins: quadrics 6 rows × 1 column; cubic blocks 20 × 8. A bin is filled iff it contains an exact nonzero coefficient.',
                limits=packet['limits'])


def occupancy(ax, matrix, color=TEAL):
    bits=np.frombuffer(base64.b64decode(matrix['occupancy_bits_base64']),dtype=np.uint8)
    count=int(np.prod(matrix['binned_shape']))
    grid=np.unpackbits(bits,bitorder='big')[:count].reshape(matrix['binned_shape'])
    assert int(grid.sum())==matrix['occupied_bin_count']
    nr,nc = matrix['shape'];br,bc = matrix['bin_size']
    ax.imshow(grid,cmap=ListedColormap([PAPER,color]),interpolation='nearest',aspect='auto',
              extent=(-.5,grid.shape[1]*bc-.5,grid.shape[0]*br-.5,-.5),rasterized=True)
    ax.set(xlim=(-.5,nc-.5),ylim=(nr-.5,-.5))
    ax.tick_params(labelsize=11,colors=MUTED)
    for spine in ax.spines.values():
        spine.set_color('#CED6D2')


def save(fig,name):
    OUT.mkdir(parents=True,exist_ok=True)
    path=OUT/name
    fig.savefig(path.with_suffix('.png'),dpi=160,facecolor=PAPER)
    svg=path.with_suffix('.svg')
    fig.savefig(svg,facecolor=PAPER,metadata={'Date':None})
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',
                   encoding='utf-8',newline='\n')
    plt.close(fig)


def monomial_label(powers):
    names = ('X_0','X_1','Z','Y_0','Y_1','Y_2')
    return '$'+''.join(names[i]+('^{'+str(p)+'}' if p != 1 else '')
                      for i,p in enumerate(powers) if p)+'$'


def feature(data):
    count = len(data['forced_raw_indices'])
    fig=plt.figure(figsize=(14,9.6),facecolor=PAPER)
    fig.text(.055,.944,f'Full quadratic directions: {count} parameters eliminated',fontsize=25,weight='bold')
    fig.text(.055,.901,'cyclic-triple-fano · #112   |   Joint 75-parameter degree 7 search; all five components vary together',
             fontsize=14,color=MUTED)
    ax=fig.add_axes([.150,.445,.750,.350])
    grid=np.zeros((5,15),dtype=int)
    for round_index,indices in enumerate(data['exact_rounds'],1):
        for k in indices:
            assert not grid[k//15,k%15]
            grid[k//15,k%15]=round_index
    colors=['#E9ECE7','#C5E0DA','#DFD5ED','#EDD7B3','#B7D4E7']
    assert grid.max()<len(colors)
    ax.imshow(grid,cmap=ListedColormap(colors),vmin=0,vmax=len(colors)-1,aspect='auto')
    for i in range(5):
        for j in range(15):
            value=grid[i,j]
            ax.text(j,i,str(value) if value else '·',ha='center',va='center',fontsize=18,
                    color=TEAL if value==1 else PURPLE if value else MUTED,weight='bold')
    ax.set_yticks(range(5),['$v_{'+n[0]+'_'+n[1]+'}$' for n in NAMES],fontsize=16)
    ax.set_xticks(range(15),[monomial_label(m) for m in data['quadratic_monomials']],rotation=40,ha='right',fontsize=13)
    ax.set_xticks(np.arange(-.5,15,1),minor=True)
    ax.set_yticks(np.arange(-.5,5,1),minor=True)
    ax.grid(which='minor',color=PAPER,linewidth=2)
    ax.tick_params(which='both',length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_title('Coefficient of each quadratic monomial: exact elimination round; dots remain unresolved',
                 loc='left',fontsize=14,pad=17)
    fig.text(.055,.358,f'{count} exact vanishings    ·    {75-count} coefficients remain in the search',fontsize=18,weight='bold',color=TEAL)
    fig.text(.055,.312,r'Example: $a_{61}^{3}=2a_{61}Q_{401}-2a_{60}Q_{402}$  forces $a_{61}=0$ over $\mathbb{C}$.',
             fontsize=18)
    fig.text(.055,.275,r'Here $a_{61}$ is the $X_0X_1$ coefficient in $v_{Y_2}$; the $Q_j$ are necessary quadrics, using zero-based packet indices.',
             fontsize=11.5,color=MUTED)
    fig.text(.055,.218,'Full cubic-block searches reached their operation budgets.',fontsize=16,weight='bold',color=CORAL)
    fig.text(.055,.174,'The final 40-quadric subset produced no isolated fourth powers; the full quartic search remains open.',
             fontsize=13,color=MUTED)
    fig.text(.055,.123,data['rebuild_caption'],fontsize=14,weight='bold')
    fig.text(.055,.077,'All 55 correction types and 246 quotient directions remain allowed. Earlier restricted-family results do not set entries here to zero.',
             fontsize=11.5,color=MUTED)
    fig.text(.055,.038,'The full quadratic-direction family remains unresolved. No certificate, Lean proof, or solved instance is claimed.',
             fontsize=12,color=CORAL)
    save(fig,'cyclic-fano-full-quadratic-multipliers')


def detail(data):
    fig=plt.figure(figsize=(16,10),facecolor=PAPER)
    fig.text(.055,.942,'Exact necessary equations and bounded cubic searches',fontsize=25,weight='bold')
    fig.text(.055,.897,'cyclic-triple-fano · discussion #112   |   Occupancy of actual rational coefficient maps',fontsize=14,color=MUTED)
    rects=[(.065,.418,.220,.360),(.355,.418,.265,.360),(.690,.418,.265,.360)]
    keys=['initial_quadric_map','charge0_map','charge3_map']
    titles=['411 necessary quadrics','Cubic character 0 block','Cubic character 3 block']
    for rect,key,title in zip(rects,keys,titles):
        ax=fig.add_axes(rect)
        occupancy(ax,data[key],TEAL if key!='charge3_map' else PURPLE)
        ax.set_title(title,loc='left',fontsize=17,pad=18)
        ax.set(xlabel='equation / multiplier column',ylabel='monomial-row index')
    qmap=data['initial_quadric_map']
    fig.text(.065,.351,f"{qmap['shape'][0]:,} active monomials × 411 quadrics",fontsize=12)
    fig.text(.065,.315,'Full physical map: 1,799 × 6,975',fontsize=12,color=MUTED)
    fig.text(.065,.280,'Exact ranks: 1,759 total; 1,348 correction.',fontsize=11.5,color=MUTED)
    for x,charge in ((.355,0),(.690,3)):
        block=data['blocks'][str(charge)]
        fig.text(x,.351,f"{block['active_rows']:,} rows × {block['columns']:,} columns",fontsize=13)
        fig.text(x,.315,f"Processed {block['processed_generators']:,} / {block['columns']:,} generators",fontsize=12,color=CORAL)
        fig.text(x,.280,f"Prefix rank {block['rank_mod_prime']:,} modulo {block['prime']} only",fontsize=12,color=CORAL)
    fig.text(.055,.216,'These two characters contain all 75 coordinate cubes. The pictures show complete blocks; the searches processed only prefixes.',
             fontsize=13,weight='bold')
    fig.text(.055,.165,'The μ₆ grading is equivariant: β and A have character 3. Block sizes and ranks do not count geometric solutions.',
             fontsize=12.5,color=MUTED)
    fig.text(.055,.112,data['bin_caption'],fontsize=12,color=MUTED)
    fig.text(.055,.062,'The exact exclusions use rational polynomial identities, not the density, shape, or modular rank of these pictures.',
             fontsize=13,color=CORAL)
    save(fig,'cyclic-fano-full-quadratic-multipliers-maps')


def main():
    assert __debug__,'Run without -O so all data checks remain enabled.'
    plt.rcParams.update({'font.family':'DejaVu Sans','text.color':INK,'axes.labelcolor':INK,
                         'axes.titlecolor':INK,'svg.fonttype':'none',
                         'svg.hashsalt':'cyclic-fano-full-quadratic-multipliers-v1'})
    data=check_data()
    feature(data);detail(data)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'plot-data.json').write_text(json.dumps(data,separators=(',',':'))+'\n',encoding='utf-8',newline='\n')
    assert all(sha(ROOT/path)==digest for path,digest in data['source_sha256'].items())
    print(json.dumps({'status':'PASS','source_bindings':len(data['source_sha256']),
                      'exact_cube_identities':sum(c['identities'] for c in data['exact_cube_checks']),
                      'cube_multiplier_terms':sum(c['multiplier_terms'] for c in data['exact_cube_checks']),
                      'remaining_parameters':len(data['remaining_raw_indices']),
                      'plot_data_bytes':(OUT/'plot-data.json').stat().st_size,
                      'figures':['cyclic-fano-full-quadratic-multipliers.png','cyclic-fano-full-quadratic-multipliers-maps.png']}))


if __name__=='__main__':
    main()
