#!/usr/bin/env python3
"""Source-bound figures for the remaining-66 multiplier continuation.

The equation-basis change and the later physical rebuild are different steps.
Only exact, checked coordinate-power identities mark a parameter as zero.
"""
from __future__ import annotations

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

import plot_cyclic_fano_full_quadratic_multipliers as previous_plot

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'results/cyclic-fano-remaining66-multipliers'
OUT=ROOT/'results/cyclic-fano-remaining66-multipliers-figures'
INK,MUTED,PAPER='#17323B','#53666D','#FAFAF5'
TEAL,PURPLE,CORAL='#166A70','#7967AA','#B94D42'
sha=previous_plot.sha
load=previous_plot.load
decode_stage=previous_plot.decode_stage
add_scaled=previous_plot.add_scaled


def transformation_map(reduced):
    n=reduced['rank']
    entries=[]
    for column,equation in enumerate(reduced['equations']):
        seen=set()
        for row,coefficient in equation['combination']:
            assert 0<=row<n and row not in seen and Q(coefficient)
            seen.add(row);entries.append((row,column))
    return dict(shape=[n,n],bin_size=[1,1],binned_shape=[n,n],
                nonzero_coefficients=len(entries),occupied_bin_count=len(entries),
                occupancy_bits_base64=previous_plot.packed_occupancy(entries,[n,n]),
                bit_encoding='Row-major occupancy bits, most significant bit first; base64.',
                bin_rule='An occupied cell is an exact nonzero rational change-of-basis coefficient.')


def verify_transformation(original,reduced):
    assert original['active_raw_parameter_indices']==reduced['active_raw_parameter_indices']
    old,new=decode_stage(original),decode_stage(reduced)
    assert len(old)==len(new)==reduced['rank']
    assert reduced['original_term_count']==sum(map(len,old))
    assert reduced['reduced_term_count']==sum(map(len,new))
    products=0
    for equation,expected in zip(reduced['equations'],new):
        total={}
        for i,coefficient in equation['combination']:
            assert 0<=i<len(old)
            add_scaled(total,old[i],Q(coefficient));products+=len(old[i])
        assert total==expected
    pivots=[min(q) for q in new]
    assert len(set(pivots))==len(new)
    for i,pivot in enumerate(pivots):
        assert all(q.get(pivot,Q(0))==int(i==j) for j,q in enumerate(new))
    return dict(equations=len(new),coefficient_products=products,
                old_terms=sum(map(len,old)),new_terms=sum(map(len,new)),
                short_old=sum(len(q)<=4 for q in old),short_new=sum(len(q)<=4 for q in new))


def verify_power_identities(stage,proof,attempts=None):
    active=stage['active_raw_parameter_indices'];quadrics=decode_stage(stage)
    assert proof['status']=='completed'
    assert proof['active_raw_parameter_indices']==active
    forced=[];terms=products=0;degrees={}
    for identity in proof['identities']:
        k,power=identity['parameter_index'],identity['power']
        assert 0<=k<len(active) and k not in forced and power in (3,4)
        source=proof if 'term_threshold' in proof else attempts[identity['source_attempt']]
        assert source['coefficient_field']=='Q' and source['active_raw_parameter_indices']==active
        selected=[i for i,q in enumerate(quadrics) if len(q)<=source['term_threshold']]
        assert source['equation_indices']==selected
        assert {key:value for key,value in identity.items() if key!='source_attempt'} in source['identities']
        total={}
        for t in identity['multipliers']:
            q=t['equation_index'];assert q in selected
            factors=[t['linear_variable']] if power==3 else t['quadratic_variables']
            assert len(factors)==power-2 and all(0<=j<len(active) for j in factors)
            column={tuple(sorted((*m,*factors))):c for m,c in quadrics[q].items()}
            add_scaled(total,column,Q(t['coefficient']));terms+=1;products+=len(column)
        assert total=={(k,)*power:Q(1)}
        forced.append(k);degrees[str(power)]=degrees.get(str(power),0)+1
    assert proof['remaining_local_parameters']==[j for j in range(len(active)) if j not in forced]
    return dict(forced_raw_indices=[active[j] for j in forced],identities=len(forced),
                multiplier_terms=terms,coefficient_products=products,power_counts=degrees)


def check_data():
    packet_path=INPUT/'packet.json';primary_path=INPUT/'validation.json';review_path=INPUT/'independent-validation.json'
    packet,primary,review=map(load,(packet_path,primary_path,review_path))
    assert packet['schema']=='cyclic-fano-remaining66-multipliers-v1'
    assert primary['schema']=='cyclic-fano-remaining66-multipliers-validation-v1'
    assert review['schema']=='cyclic-fano-remaining66-multipliers-independent-v1'
    assert packet['status']=='full_quadratic_direction_family_excluded' and primary['status']==review['status']=='PASS'
    assert (packet['instance'],packet['q'],packet['degree'])==('cyclic-triple-fano',1,7)
    producer=ROOT/'experiments/cyclic_fano_remaining66_multipliers.py'
    checker=ROOT/'experiments/check_cyclic_fano_remaining66_multipliers.py'
    source=ROOT/'results/cyclic-fano-curve/source/instance.rec'
    assert packet['producer_sha256']==primary['producer_sha256']==sha(producer)
    assert primary['packet_sha256']==review['packet_lf_sha256']==sha(packet_path)
    assert review['checker_lf_sha256']==sha(checker)
    assert review['primary_validation_lf_sha256']==sha(primary_path)
    assert packet['source_instance_sha256']==review['source_instance_lf_sha256']==sha(source)
    bindings={p.relative_to(ROOT).as_posix():sha(p) for p in
              (packet_path,primary_path,review_path,producer,checker,source,Path(previous_plot.__file__))}

    def bind(path,digest=None,binary=False):
        actual=hashlib.sha256(path.read_bytes()).hexdigest() if binary else sha(path)
        if digest is not None:assert actual==digest,path
        bindings[path.relative_to(ROOT).as_posix()]=sha(path)
        return path

    for dependencies in (packet['dependencies'],review['independent_arithmetic_dependencies']):
        for name,digest in dependencies.items():bind(ROOT/'experiments'/name,digest)
    prior=packet['prior_proof'];prior_path=ROOT/prior['packet'];old_packet=load(bind(prior_path,prior['packet_sha256']))
    bind(prior_path.parent/'validation.json',prior['primary_receipt_sha256'])
    bind(prior_path.parent/'independent-validation.json',prior['independent_receipt_sha256'])
    assert review['prior_packet_lf_sha256']==prior['packet_sha256']
    assert review['prior_independent_validation_lf_sha256']==prior['independent_receipt_sha256']
    assert prior['initial_parameters']==66
    earlier=prior['prior_forced_raw_parameters'];assert earlier==[8,13,26,28,38,53,56,61,66]
    assert packet['parameter_order']==old_packet['parameter_order']
    labels=packet['parameter_order'];assert len(labels)==75
    assert packet['complete_correction_types']==review['retained_correction_types']==55
    assert packet['complete_raw_Koszul_fields']==review['full_raw_Koszul_fields']==230
    assert packet['quotient_directions']==review['quotient_directions_replayed']==246
    attempts={};attempt_checks={r['file']:r for r in review['attempt_checks']}
    assert len(attempt_checks)==len(packet['attempts'])
    for entry in packet['attempts']:
        path=bind(INPUT/entry['file'],entry['sha256'],True);data=load(path)
        assert data['status']==entry['status'] and attempt_checks[entry['file']]['sha256']==entry['sha256']
        attempts[entry['file']]=data
    for entry in packet['auxiliary_files']:
        bind(INPUT/entry['file'],entry['sha256'],entry.get('hash_mode')!='LF-normalized text')
    assert len(packet['stages'])==len(primary['stages'])==len(review['stages'])
    stages=[];checks=[];rounds=[];active=old_packet['remaining_raw_parameter_indices'];forced=[]
    assert len(active)==66
    for index,info in enumerate(packet['stages']):
        assert info['index']==index
        path=ROOT/prior['physical_file'] if info['physical_file'] is None else INPUT/info['physical_file']
        physical=json.loads(gzip.decompress(bind(path,info['physical_sha256'],True).read_bytes()))
        reduced=json.loads(gzip.decompress(bind(INPUT/info['reduced_file'],info['reduced_sha256'],True).read_bytes()))
        assert physical['active_raw_parameter_indices']==active
        assert info['parameters']==len(active)
        r=review['stages'][index];p=primary['stages'][index]
        for key in ('parameters','physical_rows','physical_columns','rank','mixed_rank','necessary_quadrics'):
            assert info[key]==r[key]
        assert physical['rows']==info['physical_rows'] and physical['columns']==info['physical_columns']
        assert physical['rank']==p['physical']['rank']==info['rank']
        assert physical['mixed_rank']==p['physical']['mixed_rank']==info['mixed_rank']
        assert len(physical['equations'])==info['necessary_quadrics']==physical['rank']-physical['mixed_rank']
        assert physical['mixed_columns']==len(active)*55
        assert physical['pure_columns']==len(active)*(len(active)+1)//2
        basis_check=verify_transformation(physical,reduced)
        assert basis_check['equations']==r['reduced_basis']['rank']==r['reduced_basis']['exact_linear_combinations']
        assert basis_check['old_terms']==r['reduced_basis']['original_term_count']
        assert basis_check['new_terms']==r['reduced_basis']['reduced_term_count']
        assert r['reduced_basis']['same_quadric_span'] and r['reduced_basis']['reduced_row_echelon_form']
        proof=load(bind(INPUT/info['power_proof_file'],info['power_proof_sha256'],True))
        power_check=verify_power_identities(reduced,proof,attempts)
        assert power_check['forced_raw_indices']==info['newly_forced_raw_parameters']==r['selected_powers']['forced_raw_parameters']
        assert power_check['identities']==p['coordinate_powers']==r['selected_powers']['explicit_power_identities']
        assert power_check['multiplier_terms']==p['multiplier_terms']==r['selected_powers']['multiplier_terms']
        for degree in (3,4):assert power_check['power_counts'].get(str(degree),0)==r['selected_powers'][f'degree{degree}_identities']
        stages.append(dict(physical=physical,reduced=reduced,proof=proof,info=info))
        checks.append(dict(stage=index,basis=basis_check,powers=power_check))
        if power_check['identities']:
            rounds.append(dict(stage=index,**power_check))
        forced.extend(power_check['forced_raw_indices'])
        active=[j for j in active if j not in power_check['forced_raw_indices']]
    assert active==packet['remaining_raw_parameter_indices']==review['remaining_raw_parameter_indices']
    assert forced==review['newly_forced_raw_parameter_indices'] and len(forced)==review['new_power_identities']
    assert sum(c['powers']['multiplier_terms'] for c in checks)==review['multiplier_terms']
    assert len(forced)==56 and len(active)==10
    assert [dict(stage=g['stage'],restricted_old_rank=g['restricted_initial_rank'],rebuilt_rank=g['fresh_rank'],
                 added_independent_quadrics=g['additional_quadrics'],span_inclusion=g['span_inclusion'])
            for g in review['rebuild_diagnostics']]==packet['rebuild_diagnostics']
    closure=packet['coordinate_divisible_closure'];closure_review=review['coordinate_divisible_closure']
    closure_path=ROOT/closure['packet'];closure_packet=load(bind(closure_path,closure['packet_sha256']))
    closure_primary=load(bind(closure_path.parent/'validation.json',closure['primary_receipt_sha256']))
    closure_prior_review=load(bind(closure_path.parent/'independent-validation.json',closure['independent_receipt_sha256']))
    assert closure_packet['status']==closure_primary['status']==closure_prior_review['status']==closure_review['status']=='PASS'
    assert closure_review['packet_lf_sha256']==closure['packet_sha256']
    assert closure_review['independent_receipt_lf_sha256']==closure['independent_receipt_sha256']
    assert closure_review['embedding']==closure['embedding']
    assert closure_review['necessary_quadric_identities']==167 and closure_review['coordinate_cube_identities']==25
    assert closure_review['full_correction_types']==55 and closure_review['quotient_directions']==246
    assert closure_packet['source_instance_sha256']==packet['source_instance_sha256']
    assert not closure_packet['final_cubic_stage']['remaining_parameter_indices']
    assert [entry['raw_parameter_index'] for entry in closure['embedding']]==active
    for entry in closure['embedding']:
        label=labels[entry['raw_parameter_index']]
        old_label=closure_packet['parameter_order'][entry['old_local_parameter_index']]
        assert old_label['raw_parameter_index']==entry['raw_parameter_index']
        assert old_label['quadratic_powers']==label['quadratic_powers']
        assert [0,1,3,4,5][old_label['matrix_row']]==label['component']
        assert label['quadratic_powers'][label['component']]>=1
    assert set(earlier)|set(forced)|set(active)==set(range(75))
    assert len(earlier)+len(forced)+len(active)==75
    first=stages[0];old=decode_stage(first['physical']);reduced=decode_stage(first['reduced'])
    assert (sum(map(len,old)),sum(map(len,reduced)))==(41288,47734)
    assert (sum(len(q)<=4 for q in old),sum(len(q)<=4 for q in reduced))==(40,76)
    # Two short, source-bound cancellations from the original 66-parameter basis.
    for example in review['exact_short_combinations']:
        total={}
        for i,c in example['combination']:add_scaled(total,old[i],Q(c))
        pair=tuple(sorted(first['physical']['active_raw_parameter_indices'].index(j) for j in example['raw_parameter_pair']))
        assert total=={pair:Q(1)}
    # The displayed two-term cube identity comes from the later rebuilt 60-stage.
    sixty=next(s for s in stages if s['info']['parameters']==60)
    basis=decode_stage(sixty['reduced']);order=sixty['reduced']['active_raw_parameter_indices']
    i,j=order.index(65),order.index(70)
    assert basis[386]=={(i,i):Q(1),(j,j):Q(588,5)} and basis[387]=={(i,j):Q(1)}
    total={}
    add_scaled(total,previous_plot.linear_multiple(basis[386],i),Q(1))
    add_scaled(total,previous_plot.linear_multiple(basis[387],j),-Q(588,5))
    assert total=={(i,i,i):Q(1)}
    amap=previous_plot.quadric_map(old,4,1);bmap=previous_plot.quadric_map(reduced,4,1)
    assert amap['row_monomial_indices']==bmap['row_monomial_indices']
    comparison=[];selected=[]
    timeout_name='cubic-original-128-timeout.json'
    assert attempts[timeout_name]['status']=='timeout' and attempts[timeout_name]['bound_seconds']==120
    selected.append(timeout_name)
    for stage in stages:
        proof=stage['proof'];names={v['source_attempt'] for v in proof['identities']}
        if not names:
            names={name for name,a in attempts.items() if a['status']=='completed' and a.get('stage',0)==stage['info']['index']}
        for degree in (3,4):
            options=[name for name in names if attempts[name].get('degree',3)==degree]
            if not options:
                options=[name for name,a in attempts.items() if a['status']=='completed' and
                         a.get('stage',0)==stage['info']['index'] and a.get('degree',3)==degree and a.get('basis')=='reduced']
            if options:selected.append(max(options,key=lambda n:(attempts[n]['term_threshold'],'identities' in attempts[n],n)))
    for name in selected:
        attempt=attempts[name];index=attempt.get('stage',0);basis_name=attempt['basis'];stage=stages[index]
        equations=decode_stage(stage['physical'] if basis_name=='original' else stage['reduced'])
        n=stage['info']['parameters'];degree=attempt.get('degree',3)
        threshold=attempt.get('term_threshold',attempt.get('threshold'))
        count=sum(len(q)<=threshold for q in equations)
        columns=count*(n if degree==3 else n*(n+1)//2)
        if attempt['status']=='completed':
            audit=attempt_checks[name]
            assert attempt['columns']==audit['multiplier_generators']==columns
            assert attempt['rank']==audit['exact_rank']
            found=len(audit['forced_raw_parameters'])
            power_name = ('cube' if found==1 else 'cubes') if degree==3 else ('fourth power' if found==1 else 'fourth powers')
            result=f"{found} {power_name}" if found else 'no powers in selected span'
            rank=attempt['rank']
        else:
            assert attempt_checks[name]['status']=='recorded_timeout'
            result=f"timeout {attempt['bound_seconds']} s; unresolved";rank=None
        comparison.append(dict(file=name,label=f'{n} params / {basis_name} / ≤{threshold} terms',degree=degree,
                               selected_quadrics=count,columns=columns,rank=rank,outcome=result))
    chain=[66]+[s['info']['parameters']-len(s['info']['newly_forced_raw_parameters'])
                for s in stages if s['info']['newly_forced_raw_parameters']]
    return dict(schema='cyclic-fano-remaining66-multipliers-plot-v1',instance='cyclic-triple-fano',discussion_number=112,
                source_sha256=bindings,plot_source_sha256=sha(Path(__file__)),
                sha256_policy='Text CRLF normalized to LF; gzip input files are hashed as exact binary bytes.',
                previous_forced_raw_indices=earlier,new_forced_raw_indices=forced,
                closure_raw_indices=active,remaining_raw_indices=[],coordinate_divisible_closure=closure,
                exact_rounds=rounds,verification=checks,parameter_order=labels,
                witness_degree_scope='The saved identities use powers three or four; some later coefficients also have direct square witnesses. No minimal-degree claim.',
                quadratic_monomials=[p['quadratic_powers'] for p in labels[:15]],
                original_map=amap,transformation_map=transformation_map(first['reduced']),reduced_map=bmap,
                comparison_rows=comparison,rebuild_diagnostics=packet['rebuild_diagnostics'],
                product_examples=review['exact_short_combinations'],
                cube_example=dict(stage=sixty['info']['index'],raw_parameters=[65,70],equation_indices=[386,387]),
                chain_title='Quadratic-direction polars: the full family is excluded',
                parameter_chain=chain+[0],
                power_caption=f'{len(forced)} new power identities reduce 66 → 10; the earlier 25-parameter exclusion closes the remainder.',
                rebuild_caption='Rebuild gains beyond substitution: '+', '.join('+'+str(g['added_independent_quadrics']) for g in packet['rebuild_diagnostics'])+' necessary quadrics.',
                failure_caption='The original-basis cubic search hit its 120-second limit; bounded failures remain recorded alongside the proofs.',
                independent_validation=dict(necessary_quadric_identities=review['necessary_quadric_identities'],
                    basis_transformation_identities=review['basis_transformation_identities'],
                    negative_controls_rejected=review['negative_controls_rejected']),limits=packet['limits'])


def save(fig,name):
    OUT.mkdir(parents=True,exist_ok=True)
    fig.savefig(OUT/(name+'.png'),dpi=160,facecolor=PAPER)
    path=OUT/(name+'.svg')
    fig.savefig(path,facecolor=PAPER,metadata={'Date':None})
    path.write_text('\n'.join(s.rstrip() for s in path.read_text(encoding='utf-8').splitlines())+'\n',
                    encoding='utf-8',newline='\n')
    plt.close(fig)


def feature(data):
    new=data['new_forced_raw_indices'];remaining=data['remaining_raw_indices']
    fig=plt.figure(figsize=(14,10.5),facecolor=PAPER)
    fig.text(.055,.947,data['chain_title'],fontsize=23,weight='bold')
    fig.text(.055,.907,'cyclic-triple-fano · discussion #112   |   Joint quadratic-direction family, degree 7',
             fontsize=14,color=MUTED)
    fig.text(.055,.864,'Parameter chain: '+' → '.join(map(str,data['parameter_chain']))+'  (final step: prior subfamily proof)',
             fontsize=13,color=TEAL,weight='bold')
    ax=fig.add_axes([.145,.540,.765,.280])
    grid=np.zeros((5,15),dtype=int)
    for k in data['previous_forced_raw_indices']:
        grid[k//15,k%15]=1
    for step,round_data in enumerate(data['exact_rounds'],2):
        for k in round_data['forced_raw_indices']:
            assert grid[k//15,k%15]==0
            grid[k//15,k%15]=step
    palette=['#C5E0DA','#DFD5ED','#EDD7B3','#B7D4E7','#F4D3CA','#DDE1B9']
    colors=['#E9ECE7','#E2E4E0']+[palette[i%len(palette)] for i in range(len(data['exact_rounds']))]
    closure_index=len(colors);colors.append('#F0D3A0')
    for k in data['closure_raw_indices']:
        assert grid[k//15,k%15]==0
        grid[k//15,k%15]=closure_index
    assert grid.max()<len(colors)
    ax.imshow(grid,cmap=ListedColormap(colors),vmin=0,vmax=len(colors)-1,aspect='auto')
    for i in range(5):
        for j in range(15):
            value=grid[i,j]
            label='·' if value==0 else '×' if value==1 else 'C' if value==closure_index else str(value-1)
            ax.text(j,i,label,ha='center',va='center',fontsize=17,
                    color=TEAL if value==2 else PURPLE if value>2 else MUTED,weight='bold')
    ax.set_yticks(range(5),[r'$v_{X_0}$',r'$v_{X_1}$',r'$v_{Y_0}$',r'$v_{Y_1}$',r'$v_{Y_2}$'],fontsize=15)
    ax.set_xticks(range(15),[previous_plot.monomial_label(p) for p in data['quadratic_monomials']],
                  rotation=40,ha='right',fontsize=12)
    ax.set_xticks(np.arange(-.5,15,1),minor=True);ax.set_yticks(np.arange(-.5,5,1),minor=True)
    ax.grid(which='minor',color=PAPER,linewidth=2);ax.tick_params(which='both',length=0)
    for spine in ax.spines.values():spine.set_visible(False)
    round_labels='1–'+str(len(data['exact_rounds']))
    ax.set_title(f'×  {len(data["previous_forced_raw_indices"])} earlier zeros      {round_labels}  {len(new)} new power vanishings      C  {len(data["closure_raw_indices"])} closed by the prior proof',
                 loc='left',fontsize=14,pad=17)
    fig.text(.055,.460,'First step: an equivalent basis of the same 393-dimensional quadric span',fontsize=17,weight='bold')
    fig.text(.055,.421,'Total coefficient terms: 41,288 → 47,734     |     Equations with ≤4 terms: 40 → 76',fontsize=15,color=TEAL)
    fig.text(.055,.383,'The basis becomes denser overall, while exposing more short equations for the bounded multiplier search.',
             fontsize=12.5,color=MUTED)
    fig.text(.055,.329,r'$R_{386}=a_{65}^{2}+\frac{588}{5}a_{70}^{2}=0,\qquad R_{387}=a_{65}a_{70}=0$',fontsize=18)
    fig.text(.055,.274,r'$a_{65}^{3}=a_{65}R_{386}-\frac{588}{5}a_{70}R_{387}\quad\Longrightarrow\quad a_{65}=0$',fontsize=18)
    fig.text(.055,.228,'Exact example from the later 60-parameter rebuilt basis; R indices are zero-based. The parameters may be complex.',fontsize=12,color=MUTED)
    fig.text(.055,.177,data['power_caption'],
             fontsize=14,weight='bold',color=TEAL)
    fig.text(.055,.130,data['rebuild_caption'],fontsize=13,weight='bold')
    fig.text(.055,.084,data['failure_caption'],fontsize=12,color=MUTED)
    fig.text(.055,.038,'This excludes the quadratic-direction polar family, not arbitrary degree-7 denominators. The instance remains unsolved.',
             fontsize=12,color=CORAL)
    save(fig,'cyclic-fano-remaining66-multipliers')


def detail(data):
    fig=plt.figure(figsize=(16,11+.38*max(0,len(data['comparison_rows'])-6)),facecolor=PAPER)
    fig.text(.055,.944,'Changing the basis preserves the equations, but changes the search',fontsize=24,weight='bold')
    fig.text(.055,.902,'cyclic-triple-fano · discussion #112   |   Actual rational coefficient maps: B = A C',fontsize=14,color=MUTED)
    specs=[(.065,.445,.245,.355,'original_map','A · original 393 quadrics'),
           (.377,.445,.245,.355,'transformation_map','C · exact basis transformation'),
           (.690,.445,.245,.355,'reduced_map','B · reduced 393 quadrics')]
    for x,y,w,h,key,title in specs:
        ax=fig.add_axes([x,y,w,h]);previous_plot.occupancy(ax,data[key],PURPLE if key=='transformation_map' else TEAL)
        ax.set_title(title,loc='left',fontsize=15,pad=16)
        ax.set_xlabel('equation column',fontsize=11)
        ax.set_ylabel('old equation index' if key=='transformation_map' else 'quadratic-monomial index',fontsize=11)
    fig.text(.065,.381,'41,288 nonzeros; 40 equations with ≤4 terms',fontsize=11.5)
    fig.text(.377,.381,f"{data['transformation_map']['nonzero_coefficients']:,} exact transformation coefficients",fontsize=11.5)
    fig.text(.690,.381,'47,734 nonzeros; 76 equations with ≤4 terms',fontsize=11.5)
    fig.text(.055,.346,'Search results within a stage overlap; the parameter chain counts their union once.',fontsize=11.5,color=MUTED)
    ax=fig.add_axes([.055,.137,.890,.185]);ax.axis('off')
    rows=[[r['label'],r['degree'],r['selected_quadrics'],f"{r['columns']:,}",
           f"{r['rank']:,}" if r['rank'] is not None else 'not established',r['outcome']]
          for r in data['comparison_rows']]
    table=ax.table(cellText=rows,colLabels=['Multiplier search','Power','Quadrics','Columns','Exact rank','Result'],
                   colWidths=[.33,.065,.085,.12,.13,.27],cellLoc='left',colLoc='left',bbox=[0,0,1,1])
    table.auto_set_font_size(False);table.set_fontsize(10.5)
    for (r,c),cell in table.get_celld().items():
        cell.set_edgecolor('#D8DEDA');cell.set_linewidth(.5)
        cell.set_facecolor('#E4ECE6' if r==0 else PAPER)
        cell.get_text().set_color(INK)
        if r==0:cell.get_text().set_weight('bold')
    fig.text(.055,.102,'A and B use the same monomial rows; display bins combine 4 rows × 1 column. C shows individual exact nonzeros.',
             fontsize=11.5,color=MUTED)
    fig.text(.055,.065,'Rebuilding removes vanished parameter × correction columns, then eliminates corrections again; substitution alone can miss equations.',
             fontsize=11.5,color=MUTED)
    fig.text(.055,.028,'Ranks count finite-degree spans, not solutions. The final closure uses the earlier 25-parameter proof; all 55 correction types are retained.',
             fontsize=12,color=CORAL)
    save(fig,'cyclic-fano-remaining66-multipliers-maps')


def main():
    assert __debug__,'Run without -O so all data checks remain enabled.'
    plt.rcParams.update({'font.family':'DejaVu Sans','text.color':INK,'axes.labelcolor':INK,
                         'axes.titlecolor':INK,'svg.fonttype':'none',
                         'svg.hashsalt':'cyclic-fano-remaining66-multipliers-v1'})
    data=check_data()
    feature(data);detail(data)
    (OUT/'plot-data.json').write_text(json.dumps(data,separators=(',',':'))+'\n',encoding='utf-8',newline='\n')
    assert all(sha(ROOT/path)==digest for path,digest in data['source_sha256'].items())
    print(json.dumps(dict(status='PASS',source_bindings=len(data['source_sha256']),
                         new_exact_zeros=data['new_forced_raw_indices'],remaining_parameters=len(data['remaining_raw_indices']),
                         plot_data_bytes=(OUT/'plot-data.json').stat().st_size)))


if __name__=='__main__':
    main()
