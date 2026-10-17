#!/usr/bin/env python3
"""Bounded polynomial-multiplier experiments for all75 quadratic directions."""
from pathlib import Path
import argparse
import copy
from fractions import Fraction as Q
import gzip
import hashlib
import itertools
import json
import math
import subprocess
import sys
import time
import cyclic_fano_divisible_multipliers as previous

source=previous.source;arithmetic=previous.arithmetic;poly=previous.poly;base=previous.base
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/cyclic-fano-full-quadratic-multipliers'
WEIGHTS=(0,4,0,1,1,5)


def save(name,data):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/name).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')


def parameter_labels():
    return [{'component':i,'quadratic_powers':list(m),'charge':(sum(a*w for a,w in zip(m,WEIGHTS))-WEIGHTS[i])%6}
            for i in source.BASE for m in base.monomials(2)]


def compact_stage(stage):
    labels=parameter_labels();charges=[labels[i]['charge']for i in stage['active_raw_parameter_indices']]
    out={k:v for k,v in stage.items()if k!='equations'};out['equations']=[]
    for equation in stage['equations']:
        terms=[]
        for t in equation['polynomial']:
            indices=[i for i,n in enumerate(t['powers'])for _ in range(n)];assert len(indices)==2
            terms.append([*indices,t['coefficient']])
        qcharges={(charges[i]+charges[j])%6 for i,j,c in terms};assert len(qcharges)==1
        charge=qcharges.pop()
        assert all((sum(a*w for a,w in zip(t['powers'],WEIGHTS))-3)%6==charge for t in equation['dual'])
        out['equations'].append({'terms':terms,'charge':charge,'dual':[[t['powers'],t['coefficient']]for t in equation['dual']]})
    return out


def stage_path(index):
    return OUT/('necessary-quadrics.json.gz'if index==0 else'stage-'+str(index).zfill(2)+'-quadrics.json.gz')


def load_stage(index=0):
    return json.loads(gzip.decompress(stage_path(index).read_bytes()))


def save_stage(index,stage):
    raw=(json.dumps(stage,separators=(',',':'))+'\n').encode()
    stage_path(index).write_bytes(gzip.compress(raw,mtime=0))
    return {'uncompressed_bytes':len(raw),'gzip_bytes':stage_path(index).stat().st_size,
            'uncompressed_sha256':hashlib.sha256(raw).hexdigest(),
            'gzip_sha256':hashlib.sha256(stage_path(index).read_bytes()).hexdigest()}


def sparse_cubes(stage,threshold):
    n=len(stage['active_raw_parameter_indices']);rows={};indices=[]
    for qindex,q in enumerate(stage['equations']):
        if len(q['terms'])>threshold:continue
        indices.append(qindex)
        for k in range(n):rows[qindex,k]={tuple(sorted((i,j,k))):Q(c)for i,j,c in q['terms']}
    pivots=arithmetic.exact_row_basis(rows);identities=[]
    for k in range(n):
        remainder,track=arithmetic.exact_reduce({(k,k,k):Q(1)},pivots)
        if remainder:continue
        track=poly.scale(track,-1)
        assert base.total(poly.scale(rows[label],c)for label,c in track.items())=={(k,k,k):Q(1)}
        identities.append({'parameter_index':k,'power':3,'multipliers':[{'equation_index':i,'linear_variable':j,'coefficient':str(c)}for(i,j),c in sorted(track.items())]})
    return {'status':'completed','coefficient_field':'Q','term_threshold':threshold,'equation_indices':indices,
            'active_raw_parameter_indices':stage['active_raw_parameter_indices'],'columns':len(rows),'rank':len(pivots),
            'identities':identities,'remaining_local_parameters':[i for i in range(n)if i not in {v['parameter_index']for v in identities}]}


def verify_cubes(stage,proof):
    n=len(stage['active_raw_parameter_indices']);seen=set()
    assert proof['active_raw_parameter_indices']==stage['active_raw_parameter_indices']
    for identity in proof['identities']:
        i=identity['parameter_index'];assert i not in seen and 0<=i<n and identity['power']==3;seen.add(i)
        value={}
        for t in identity['multipliers']:
            q=stage['equations'][t['equation_index']];k=t['linear_variable'];assert 0<=k<n
            value=poly.add(value,{tuple(sorted((a,b,k))):Q(c)*Q(t['coefficient'])for a,b,c in q['terms']})
        assert value=={(i,i,i):Q(1)}
    assert proof['remaining_local_parameters']==[i for i in range(n)if i not in seen]


def small_quartic(stage,threshold):
    n=len(stage['active_raw_parameter_indices']);indices=[];rows=[]
    for i,e in enumerate(stage['equations']):
        if len(e['terms'])>threshold:continue
        indices.append(i)
        for j,k in itertools.combinations_with_replacement(range(n),2):
            rows.append({tuple(sorted((a,b,j,k))):Q(c)for a,b,c in e['terms']})
    pivots={}
    for row in rows:
        row=row.copy()
        while row:
            j=min(row)
            if j not in pivots:pivots[j]=poly.scale(row,1/row[j]);break
            row=poly.add(row,pivots[j],-row[j])
    found=[i for i in range(n)if not arithmetic.exact_reduce({(i,i,i,i):Q(1)},{j:(r,{})for j,r in pivots.items()})[0]]
    return {'status':'completed','coefficient_field':'Q','degree':4,'term_threshold':threshold,
            'active_raw_parameter_indices':stage['active_raw_parameter_indices'],
            'equation_indices':indices,'columns':len(rows),'rank':len(pivots),
            'coordinate_fourth_powers_found':found,
            'limits':'Only the selected short-quadrics subsystem was searched, not the full degree-four ideal.'}


def pack(indices):
    i,j,k=sorted(indices);return -((i<<14)|(j<<7)|k)


def cubic_block(stage,charge,p=1009,forward=False):
    labels=parameter_labels();weights=[v['charge']for v in labels]
    encode_key=lambda indices:-pack(indices)if forward else pack(indices)
    suffix='-forward'if forward else ''
    generators=[];active_rows=set();started=time.perf_counter()
    for qindex,q in enumerate(stage['equations']):
        terms=[(i,j,arithmetic.modq(Q(c),p))for i,j,c in q['terms']]
        for k in range(75):
            if(q['charge']+weights[k])%6!=charge:continue
            row={encode_key((i,j,k)):c for i,j,c in terms if c}
            generators.append((qindex,k,row));active_rows.update(row)
    ambient=sum((weights[i]+weights[j]+weights[k])%6==charge for i in range(75)for j in range(i,75)for k in range(j,75))
    targets=[i for i,w in enumerate(weights) if 3*w%6==charge]
    pivots={};fill=0;processed=0;status='completed';update_operations=0
    for qindex,k,original in sorted(generators,key=lambda row:(len(row[2]),row[0],row[1])):
        row=original.copy()
        while row:
            pivot=min(row)
            if pivot not in pivots:
                c=pow(row[pivot],-1,p);normalized={j:a*c%p for j,a in row.items()}
                pivots[pivot]=normalized;fill+=len(normalized);break
            old=pivots[pivot];c=row[pivot];update_operations+=len(old)
            for j,a in old.items():
                value=(row.get(j,0)-c*a)%p
                if value:row[j]=value
                else:row.pop(j,None)
        processed+=1
        if processed%250==0:
            progress={'charge':charge,'prime':p,'processed_generators':processed,'total_generators':len(generators),'pivot_count':len(pivots),'pivot_nonzero_entries':fill,'update_operations':update_operations,'elapsed_seconds':time.perf_counter()-started}
            save('charge'+str(charge)+suffix+'-progress.json',progress);print(json.dumps(progress),flush=True)
        if fill>3000000 or update_operations>100000000:
            status='sparse_fill_limit';break
    found=[]
    for i in targets:
        if not arithmetic.mod_reduce({encode_key((i,i,i)):1},pivots,p):found.append(i)
    return {'status':status,'charge':charge,'prime':p,'potential_rows':ambient,'active_rows':len(active_rows),
            'monomial_order':'forward_packed_sorted_triples'if forward else'reverse_packed_sorted_triples',
            'columns':len(generators),'processed_generators':processed,'rank_mod_prime':len(pivots),
            'rank_scope':'full_block'if status=='completed'else'processed_generator_prefix',
            'coordinate_cube_targets':targets,'coordinate_cubes_found_mod_prime':found,
            'pivot_nonzero_entries':fill,'update_operations':update_operations,'elapsed_seconds':time.perf_counter()-started}


def binary_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def quadrics(stage):
    return [{(i,j):Q(c)for i,j,c in e['terms']}for e in stage['equations']]


def rebuild_gain(old,new):
    positions={raw:i for i,raw in enumerate(new['active_raw_parameter_indices'])}
    translation={i:positions[raw]for i,raw in enumerate(old['active_raw_parameter_indices'])if raw in positions}
    restricted=[{(translation[i],translation[j]):Q(c)for i,j,c in e['terms']if i in translation and j in translation}for e in old['equations']]
    fresh=quadrics(new);basis=arithmetic.exact_row_basis(dict(enumerate(fresh)))
    assert all(not arithmetic.exact_reduce(row,basis)[0]for row in restricted)
    oldrank=previous.untracked_rank(restricted);newrank=len(basis)
    return {'restricted_old_rank':oldrank,'rebuilt_rank':newrank,
            'added_independent_quadrics':newrank-oldrank,'span_inclusion':True}


def replay_stage(stage,data):
    active=stage['active_raw_parameter_indices'];n=len(active)
    assert active==sorted(set(active))and set(active)<=set(range(75))
    rows,kept=source.restricted_rows(data,set(active))
    pure=[j for j in sorted(kept)if data['labels'][j]['kind']=='a*a']
    mixed=[j for j in sorted(kept)if data['labels'][j]['kind']=='a*c']
    order=mixed+pure;lookup={j:k for k,j in enumerate(order)}
    assert (len(rows),len(order),len(pure),len(mixed))==(stage['rows'],stage['columns'],stage['pure_columns'],stage['mixed_columns'])
    assert len(pure)==n*(n+1)//2 and len(mixed)==55*n
    physical_pure={tuple(data['labels'][j]['indices']):j for j in pure}
    pairings=0
    for e in stage['equations']:
        value={}
        for spatial,c in e['dual']:
            value=poly.add(value,rows[tuple(spatial)],Q(c));pairings+=len(rows[tuple(spatial)])
        expected={physical_pure[active[i],active[j]]:Q(c)for i,j,c in e['terms']}
        assert value==expected
    reordered=[{lookup[j]:c for j,c in row.items()}for m,row in sorted(rows.items(),key=lambda t:(len(t[1]),t[0]))]
    # Exact echelon elimination without multiplier tracking certifies both ranks.
    pivots={}
    for row in reordered:
        row=row.copy()
        while row:
            j=min(row)
            if j not in pivots:pivots[j]=poly.scale(row,1/row[j]);break
            row=poly.add(row,pivots[j],-row[j])
    assert len(pivots)==stage['rank'] and sum(j<len(mixed)for j in pivots)==stage['mixed_rank']
    qb=arithmetic.exact_row_basis(dict(enumerate(quadrics(stage))))
    assert len(qb)==len(stage['equations'])==stage['rank']-stage['mixed_rank']
    square_hits=[i for i in range(n)if not arithmetic.exact_reduce({(i,i):Q(1)},qb)[0]]
    charges=[parameter_labels()[raw]['charge']for raw in active]
    for e in stage['equations']:
        assert {(charges[i]+charges[j])%6 for i,j,c in e['terms']}=={e['charge']}
        assert all((sum(a*w for a,w in zip(spatial,WEIGHTS))-3)%6==e['charge']for spatial,c in e['dual'])
    return {'physical_duals':len(stage['equations']),'coefficient_pairings':pairings,
            'rank':len(pivots),'mixed_rank':stage['mixed_rank'],'individual_squares_in_quadric_span':square_hits}


def replay_small_space(stage,proof):
    verify_cubes(stage,proof);n=len(stage['active_raw_parameter_indices'])
    indices=[i for i,e in enumerate(stage['equations'])if len(e['terms'])<=proof['term_threshold']]
    assert indices==proof['equation_indices']and proof['columns']==n*len(indices)
    rows=[]
    for i in indices:
        for k in range(n):rows.append({tuple(sorted((a,b,k))):Q(c)for a,b,c in stage['equations'][i]['terms']})
    # A full replay of this selected subsystem, not of the much larger cubic ideal.
    pivots={}
    for row in sorted(rows,key=len):
        row=row.copy()
        while row:
            j=min(row)
            if j not in pivots:pivots[j]=poly.scale(row,1/row[j]);break
            row=poly.add(row,pivots[j],-row[j])
    found=[i for i in range(n)if not arithmetic.exact_reduce({(i,i,i):Q(1)},{j:(r,{})for j,r in pivots.items()})[0]]
    assert len(pivots)==proof['rank']and found==[v['parameter_index']for v in proof['identities']]
    return {'rank':len(pivots),'columns':len(rows),'exact_cube_indices':found}


def final_packet():
    stage_files=[stage_path(0)]+sorted(OUT.glob('stage-??-quadrics.json.gz'))
    stages=[];loaded=[];previous_remaining=None
    for index,path in enumerate(stage_files):
        stage=load_stage(index);loaded.append(stage)
        proofs=[]
        for file in sorted(OUT.glob('stage-'+str(index).zfill(2)+'-small-*.json')):
            proof=json.loads(file.read_text());verify_cubes(stage,proof)
            proofs.append((file,proof))
        best=max((len(proof['identities'])for file,proof in proofs),default=-1)
        candidates=[v for v in proofs if len(v[1]['identities'])==best]
        # Use a short witness when it proves a reduction; at a plateau replay
        # the widest completed selected subsystem, not merely its smallest subset.
        chosen=(max if best==0 else min)(candidates,key=lambda v:v[1]['term_threshold'])if candidates else None
        if previous_remaining is not None:assert stage['active_raw_parameter_indices']==previous_remaining
        if chosen:
            file,proof=chosen;previous_remaining=[stage['active_raw_parameter_indices'][i]for i in proof['remaining_local_parameters']]
        else:previous_remaining=stage['active_raw_parameter_indices']
        stages.append({'index':index,'quadrics_file':path.name,'quadrics_sha256':binary_sha(path),
                       'quadrics_uncompressed_sha256':hashlib.sha256(gzip.decompress(path.read_bytes())).hexdigest(),
                       'cube_proof_file':chosen[0].name if chosen else None,'cube_proof_sha256':binary_sha(chosen[0])if chosen else None,
                       'parameters':len(stage['active_raw_parameter_indices']),
                       'physical_rows':stage['rows'],'physical_columns':stage['columns'],
                       'rank':stage['rank'],'mixed_rank':stage['mixed_rank'],'necessary_quadrics':len(stage['equations']),
                       'newly_forced_raw_parameters':[]if not chosen else[stage['active_raw_parameter_indices'][v['parameter_index']]for v in chosen[1]['identities']]})
    diagnostics=[{'stage':i,**rebuild_gain(loaded[i-1],loaded[i])}for i in range(1,len(loaded))]
    prior=source.OUT/'packet.json';prior_receipt=source.OUT/'validation.json'
    p=json.loads(prior.read_text());r=json.loads(prior_receipt.read_text())
    assert p['producer_sha256']==poly.sha(Path(source.__file__))and r['packet_sha256']==poly.sha(prior)
    attempt_files=sorted(OUT.glob('charge*-probe.json'))+sorted(OUT.glob('stage-??-small-*.json'))+sorted(OUT.glob('stage-??-quartic-*.json'))+sorted(OUT.glob('*-timeout.json'))+sorted(OUT.glob('*-attempt.json'))
    attempts=[{'file':f.name,'sha256':binary_sha(f),'status':json.loads(f.read_text())['status']}for f in attempt_files]
    return {'schema':'cyclic-fano-full-quadratic-multipliers-v1','status':'checked_partial_progress',
            'instance':'cyclic-triple-fano','q':1,'degree':7,'source_commit':'d96911d725077e66a8f10848908be01a643b1714',
            'source_instance_sha256':poly.sha(base.SOURCE/'source/instance.rec'),'producer_sha256':poly.sha(Path(__file__)),
            'dependencies':{Path(m.__file__).name:poly.sha(Path(m.__file__))for m in(previous,source,arithmetic,base,poly)},
            'prior_projection_proof':{'packet':str(prior.relative_to(ROOT)).replace('\\','/'),'packet_sha256':poly.sha(prior),
                'primary_receipt_sha256':poly.sha(prior_receipt),'independent_receipt_sha256':poly.sha(source.OUT/'independent-validation.json'),
                'raw_Koszul_fields':230,'compact_correction_types':55,'quotient_directions':246},
            'parameter_order':parameter_labels(),'base_variables':['X0','X1','Z','Y0','Y1','Y2'],
            'symmetry':{'modulus':6,'spatial_weights':list(WEIGHTS),'beta_and_A_charge':3,
                'parameter_charge_rule':'weight(quadratic monomial)-weight(component)',
                'physical_row_to_quadric_charge_shift':-3,
                'scope':'Equivariant grading: F and Delta invariant; A has character3 and is not fixed pointwise.',
                'target_cube_charges':[0,3]},
            'stages':stages,'rebuild_diagnostics':diagnostics,'attempts':attempts,
            'remaining_raw_parameter_indices':previous_remaining,
            'bounds':{'necessary_and_rebuild_seconds':120,'sparse_exact_cubic_seconds':120,
                      'modular_block_seconds':180,'modular_pivot_entry_cap':3000000,'modular_update_cap':100000000,
                      'small_quartic_seconds':30,'aggregate_primary_replay_seconds':600},
            'conclusion':'Exact coordinate-cube identities force the listed parameters to vanish; fresh complete physical rebuilds retain all55 correction types. The remaining parameter family is unresolved.',
            'limits':'Selected sparse-cubic plateaus and incomplete modular prefixes are not tests of the whole cubic ideal. No full75-family exclusion, support construction, HasCertificate proof or solve is claimed.'}


def verify_packet(actual):
    assert actual==final_packet();data=source.system();summaries=[];controls=0;stages=[]
    for info in actual['stages']:
        stage=load_stage(info['index']);stages.append(stage);summary=replay_stage(stage,data)
        print(json.dumps({'stage':info['index'],'physical_replay':'PASS','rank':summary['rank']}),flush=True)
        if info['cube_proof_file']:
            proof=json.loads((OUT/info['cube_proof_file']).read_text());summary['selected_cubic_space']=replay_small_space(stage,proof)
            if proof['identities']:
                bad=copy.deepcopy(proof);bad['identities'][0]['multipliers'][0]['coefficient']='0'
                try:verify_cubes(stage,bad)
                except AssertionError:controls+=1
                else:raise AssertionError('Corrupt multiplier accepted')
        # Negative physical-dual control evaluated on the actual source map.
        bad=copy.deepcopy(stage['equations'][0]);bad['dual'][0][1]=str(Q(bad['dual'][0][1])+1)
        rows,kept=source.restricted_rows(data,set(stage['active_raw_parameter_indices']))
        value=base.total(poly.scale(rows[tuple(m)],Q(c))for m,c in bad['dual'])
        normal=base.total(poly.scale(rows[tuple(m)],Q(c))for m,c in stage['equations'][0]['dual'])
        assert value!=normal;controls+=1;summaries.append(summary)
    for i,gain in enumerate(actual['rebuild_diagnostics'],1):assert gain=={'stage':i,**rebuild_gain(stages[i-1],stages[i])}
    quartics=[]
    for file in sorted(OUT.glob('stage-??-quartic-*.json')):
        proof=json.loads(file.read_text());stage=stages[proof['stage']]
        expected=small_quartic(stage,proof['term_threshold'])
        assert all(proof[k]==v for k,v in expected.items());quartics.append({'file':file.name,'rank':proof['rank'],'columns':proof['columns'],'coordinate_fourth_powers_found':proof['coordinate_fourth_powers_found']})
    for field in ('source_instance_sha256','producer_sha256','remaining_raw_parameter_indices'):
        bad=copy.deepcopy(actual);bad[field]=None
        assert bad!=final_packet();controls+=1
    save('validation.json',{'schema':'cyclic-fano-full-quadratic-multipliers-validation-v1','status':'PASS',
         'producer_sha256':poly.sha(Path(__file__)),'packet_sha256':poly.sha(OUT/'packet.json'),
         'stage_checks':summaries,'quartic_checks':quartics,'negative_controls_rejected':controls,
         'scope':'Exact source-map, all physical-dual, selected-cubic rank/query and identity replay; failed modular discovery is retained without rerunning it.'})


def main():
    assert __debug__,'Run without -O'
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['necessary','_necessary','compact','cubic0','_cubic0','cubic3','_cubic3','forward0','_forward0','forward3','_forward3','small','_small','rebuild','_rebuild','quartic','_quartic','run','_run','verify','_verify']);parser.add_argument('--stage',type=int,default=0);parser.add_argument('--threshold',type=int,default=128);args=parser.parse_args()
    if args.command in ('necessary','cubic0','cubic3','forward0','forward3','small','rebuild','quartic','run','verify'):
        start=time.perf_counter()
        bound=600 if args.command in ('run','verify')else 30 if args.command=='quartic'else 120 if args.command in ('necessary','small','rebuild') else 180
        try:r=subprocess.run([sys.executable,'-S',str(Path(__file__)),'_'+args.command,'--stage',str(args.stage),'--threshold',str(args.threshold)],timeout=bound)
        except subprocess.TimeoutExpired:
            name=args.command+'-stage-'+str(args.stage).zfill(2)+'-threshold-'+str(args.threshold)+'-timeout.json'
            save(name,{'status':'timeout','command':args.command,'stage':args.stage,'threshold':args.threshold,'bound_seconds':bound,'elapsed_seconds':time.perf_counter()-start});raise SystemExit(2)
        raise SystemExit(r.returncode)
    if args.command in ('_run','_verify'):
        started=time.perf_counter()
        if args.command=='_run':save('packet.json',final_packet())
        else:verify_packet(json.loads((OUT/'packet.json').read_text()))
        print(json.dumps({'status':'PASS','command':args.command[1:],'seconds':time.perf_counter()-started,'packet_sha256':poly.sha(OUT/'packet.json')}));return
    if args.command=='_quartic':
        started=time.perf_counter();result=small_quartic(load_stage(args.stage),args.threshold)
        result.update({'stage':args.stage,'bound_seconds':30,'elapsed_seconds':time.perf_counter()-started})
        save('stage-'+str(args.stage).zfill(2)+'-quartic-'+str(args.threshold)+'.json',result)
        print(json.dumps({k:v for k,v in result.items()if k not in ('active_raw_parameter_indices','equation_indices')}));return
    if args.command=='_small':
        started=time.perf_counter();stage=load_stage(args.stage);proof=sparse_cubes(stage,args.threshold);verify_cubes(stage,proof)
        proof['seconds']=time.perf_counter()-started;save('stage-'+str(args.stage).zfill(2)+'-small-'+str(args.threshold)+'.json',proof)
        print(json.dumps({'status':'PASS','stage':args.stage,'threshold':args.threshold,'rank':proof['rank'],'columns':proof['columns'],'cubes':[v['parameter_index']for v in proof['identities']],'seconds':proof['seconds']}));return
    if args.command=='_rebuild':
        assert args.stage>0;started=time.perf_counter();prior=load_stage(args.stage-1)
        proof=json.loads((OUT/('stage-'+str(args.stage-1).zfill(2)+'-small-'+str(args.threshold)+'.json')).read_text());verify_cubes(prior,proof)
        active=[prior['active_raw_parameter_indices'][i]for i in proof['remaining_local_parameters']]
        assert active and len(active)<len(prior['active_raw_parameter_indices'])
        full=previous.necessary_equations(active);stage=compact_stage(full);metadata=save_stage(args.stage,stage)
        print(json.dumps({'status':'PASS','stage':args.stage,'parameters':len(active),'quadrics':len(stage['equations']),'rank':stage['rank'],'mixed_rank':stage['mixed_rank'],'seconds':time.perf_counter()-started,**metadata}));return
    if args.command=='compact':
        stage=compact_stage(json.loads((OUT/'necessary-probe.json').read_text()))
        raw=(json.dumps(stage,separators=(',',':'))+'\n').encode()
        (OUT/'necessary-quadrics.json.gz').write_bytes(gzip.compress(raw,mtime=0))
        print(json.dumps({'uncompressed_bytes':len(raw),'gzip_bytes':(OUT/'necessary-quadrics.json.gz').stat().st_size,'sha256':hashlib.sha256(raw).hexdigest()}));return
    if args.command in ('_cubic0','_cubic3','_forward0','_forward3'):
        charge=int(args.command[-1]);forward=args.command.startswith('_forward');result=cubic_block(load_stage(),charge,forward=forward)
        save('charge'+str(charge)+('-forward'if forward else'')+'-probe.json',result);print(json.dumps(result));return
    started=time.perf_counter();result=previous.necessary_equations(list(range(75)))
    save('necessary-probe.json',result)
    print(json.dumps({'status':'PASS','seconds':time.perf_counter()-started,
                      **{k:v for k,v in result.items()if k!='equations'},'necessary_quadrics':len(result['equations'])}))


if __name__=='__main__':main()
