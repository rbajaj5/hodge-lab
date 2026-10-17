#!/usr/bin/env python3
"""Bounded continuation of the remaining66 quadratic-direction parameters."""
from pathlib import Path
from fractions import Fraction as Q
import argparse
import copy
import gzip
import hashlib
import heapq
import itertools
import json
import subprocess
import sys
import time
import cyclic_fano_full_quadratic_multipliers as prior

poly=prior.poly;arithmetic=prior.arithmetic;base=prior.base
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/cyclic-fano-remaining66-multipliers'


def save(name,data):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/name).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')


def original(index=0):
    if index:return json.loads(gzip.decompress((OUT/f'stage-{index:02d}-quadrics.json.gz').read_bytes()))
    stage=prior.load_stage(2)
    assert len(stage['active_raw_parameter_indices'])==66 and len(stage['equations'])==393
    return stage


def reduce_basis(stage):
    rows=[{(i,j):Q(c)for i,j,c in e['terms']}for e in stage['equations']]
    pivots=arithmetic.exact_row_basis(dict(enumerate(rows)));reduced={}
    for key,(row,track)in sorted(pivots.items(),reverse=True):
        row=row.copy();track=track.copy()
        for pivot,(old,oldtrack)in sorted(reduced.items()):
            c=row.get(pivot,Q(0))
            if c:row=poly.add(row,old,-c);track=poly.add(track,oldtrack,-c)
        assert base.total(poly.scale(rows[i],c)for i,c in track.items())==row
        reduced[key]=(row,track)
    equations=[]
    charges=[prior.parameter_labels()[raw]['charge']for raw in stage['active_raw_parameter_indices']]
    for key,(row,track)in sorted(reduced.items()):
        qs={(charges[i]+charges[j])%6 for i,j in row};assert len(qs)==1
        equations.append({'terms':[[i,j,str(c)]for(i,j),c in sorted(row.items())],
                          'combination':[[i,str(c)]for i,c in sorted(track.items())],'charge':qs.pop()})
    return {'active_raw_parameter_indices':stage['active_raw_parameter_indices'],'equations':equations,
            'rank':len(reduced),'original_term_count':sum(map(len,rows)),
            'reduced_term_count':sum(len(e['terms'])for e in equations),
            'transformation':'exact rational reduced row echelon form; combinations refer to this stage\'s complete physical necessary quadrics'}


def prefix(index):
    return f'stage-{index:02d}-'if index else ''


def load_basis(name,index=0):
    if name=='original':return original(index)
    return json.loads(gzip.decompress((OUT/(prefix(index)+'reduced-quadrics.json.gz')).read_bytes()))


def quartic_proof(stage,threshold):
    n=len(stage['active_raw_parameter_indices']);pivots={};pivot_rows=[];relations=[];columns=0;indices=[]
    for qi,e in enumerate(stage['equations']):
        if len(e['terms'])>threshold:continue
        indices.append(qi)
        for j,k in itertools.combinations_with_replacement(range(n),2):
            row={tuple(sorted((a,b,j,k))):Q(c)for a,b,c in e['terms']};history=[];columns+=1
            while row:
                key=min(row);c=row[key]
                if key not in pivots:
                    scale=1/c;pid=len(pivot_rows);pivots[key]=pid
                    pivot_rows.append(poly.scale(row,scale));relations.append(((qi,j,k),scale,history));break
                pid=pivots[key];history.append((pid,c));row=poly.add(row,pivot_rows[pid],-c)
    identities=[]
    for target in range(n):
        row={(target,)*4:Q(1)};weights={}
        while row:
            key=min(row)
            if key not in pivots:break
            pid=pivots[key];c=row[key];weights[pid]=weights.get(pid,Q(0))+c
            row=poly.add(row,pivot_rows[pid],-c)
        if row:continue
        todo=[-pid for pid,c in weights.items()if c];heapq.heapify(todo);queued=set(weights);answer={}
        while todo:
            pid=-heapq.heappop(todo);queued.remove(pid);c=weights.pop(pid,Q(0))
            if not c:continue
            label,scale,history=relations[pid];factor=c*scale
            answer[label]=answer.get(label,Q(0))+factor
            for old,z in history:
                weights[old]=weights.get(old,Q(0))-factor*z
                if old not in queued:heapq.heappush(todo,-old);queued.add(old)
        answer={label:c for label,c in answer.items()if c}
        identity={'parameter_index':target,'power':4,'multipliers':[{'equation_index':qi,'quadratic_variables':[j,k],'coefficient':str(c)}for(qi,j,k),c in sorted(answer.items())]}
        replay_quartic_identity(stage,identity);identities.append(identity)
    return {'status':'completed','coefficient_field':'Q','degree':4,'term_threshold':threshold,
            'active_raw_parameter_indices':stage['active_raw_parameter_indices'],'equation_indices':indices,
            'columns':columns,'rank':len(pivots),'identities':identities,
            'remaining_local_parameters':[i for i in range(n)if i not in {v['parameter_index']for v in identities}],
            'discovery_method':'exact sparse elimination with deferred pivot-provenance DAG expansion'}


def replay_quartic_identity(stage,identity):
    n=len(stage['active_raw_parameter_indices']);i=identity['parameter_index'];assert 0<=i<n and identity['power']==4
    total={}
    for t in identity['multipliers']:
        j,k=t['quadratic_variables'];assert 0<=j<=k<n
        e=stage['equations'][t['equation_index']]
        total=poly.add(total,{tuple(sorted((a,b,j,k))):Q(c)*Q(t['coefficient'])for a,b,c in e['terms']})
    assert total=={(i,)*4:Q(1)}


def verify_powers(stage,proof,degree):
    if degree==3:return prior.verify_cubes(stage,proof)
    assert proof['active_raw_parameter_indices']==stage['active_raw_parameter_indices']
    seen=[]
    for identity in proof['identities']:
        if identity['power']==3:
            single={'active_raw_parameter_indices':stage['active_raw_parameter_indices'],'identities':[identity],'remaining_local_parameters':[i for i in range(len(stage['active_raw_parameter_indices']))if i!=identity['parameter_index']]}
            prior.verify_cubes(stage,single)
        else:replay_quartic_identity(stage,identity)
        seen.append(identity['parameter_index'])
    assert len(seen)==len(set(seen))
    assert proof['remaining_local_parameters']==[i for i in range(len(stage['active_raw_parameter_indices']))if i not in seen]


def combine_powers(stage,index,basis):
    selected={};keys={};files=sorted(OUT.glob(prefix(index)+'cubic-'+basis+'-*.json'))+sorted(OUT.glob(prefix(index)+'quartic-proof-'+basis+'-*.json'))
    for file in files:
        proof=json.loads(file.read_text())
        if proof['status']!='completed':continue
        degree=4 if file.name.startswith(prefix(index)+'quartic-proof')else 3
        verify_powers(stage,proof,degree)
        for identity in proof['identities']:
            i=identity['parameter_index'];key=(identity['power'],len(identity['multipliers']),proof['term_threshold'])
            if i not in keys or key<keys[i]:keys[i]=key;selected[i]={**identity,'source_attempt':file.name}
    result={'status':'completed','active_raw_parameter_indices':stage['active_raw_parameter_indices'],
            'identities':[selected[i]for i in sorted(selected)],
            'remaining_local_parameters':[i for i in range(len(stage['active_raw_parameter_indices']))if i not in selected],
            'basis':basis,'stage':index,'scope':'Union of explicitly replayed powers; lower degree preferred, then fewer multiplier terms.'}
    verify_powers(stage,result,0);return result


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_basis(physical,reduced):
    assert physical['active_raw_parameter_indices']==reduced['active_raw_parameter_indices']
    old=[{(i,j):Q(c)for i,j,c in e['terms']}for e in physical['equations']]
    pivots=[];terms=0;charges=[prior.parameter_labels()[raw]['charge']for raw in physical['active_raw_parameter_indices']]
    for e in reduced['equations']:
        row={(i,j):Q(c)for i,j,c in e['terms']}
        assert base.total(poly.scale(old[i],Q(c))for i,c in e['combination'])==row
        pivot=min(row);assert row[pivot]==1 and pivot not in pivots;pivots.append(pivot)
        assert {(charges[i]+charges[j])%6 for i,j in row}=={e['charge']};terms+=len(e['combination'])
    for pivot,e in zip(pivots,reduced['equations']):
        assert {(i,j)for i,j,c in e['terms']}.intersection(pivots)=={pivot}
    assert len(pivots)==reduced['rank']==len(old)
    assert reduced['original_term_count']==sum(map(len,old))
    assert reduced['reduced_term_count']==sum(len(e['terms'])for e in reduced['equations'])
    squares=[physical['active_raw_parameter_indices'][e['terms'][0][0]]for e in reduced['equations']if len(e['terms'])==1 and e['terms'][0][0]==e['terms'][0][1]]
    return {'equivalent_basis_rank':len(pivots),'combination_terms':terms,'individual_squares':squares,
            'original_terms':reduced['original_term_count'],'reduced_terms':reduced['reduced_term_count']}


def stage_count():
    return 1+len(list(OUT.glob('stage-??-quadrics.json.gz')))


def closure_binding(remaining):
    path=prior.previous.OUT/'packet.json';old=json.loads(path.read_text())
    active=old['initial_stage']['active_raw_parameter_indices']
    assert set(remaining)<=set(active)
    return {'packet':str(path.relative_to(ROOT)).replace('\\','/'),'packet_sha256':poly.sha(path),
            'primary_receipt_sha256':poly.sha(prior.previous.OUT/'validation.json'),
            'independent_receipt_sha256':poly.sha(prior.previous.OUT/'independent-validation.json'),
            'embedding':[{'raw_parameter_index':i,'old_local_parameter_index':active.index(i)}for i in remaining]}


def replay_closure(binding,remaining,data):
    assert binding==closure_binding(remaining)
    old=json.loads((ROOT/binding['packet']).read_text())
    assert old['producer_sha256']==poly.sha(Path(prior.previous.__file__))
    assert old['source_instance_sha256']==poly.sha(base.SOURCE/'source/instance.rec')
    for name,digest in old['dependencies'].items():assert poly.sha(ROOT/'experiments'/name)==digest
    checks=[]
    for stage_key,proof_key in [('initial_stage','cubic_stage'),('rebuild_stage','final_cubic_stage')]:
        stage=old[stage_key];proof=old[proof_key]
        checks.append(prior.replay_stage(prior.compact_stage(stage),data))
        prior.previous.verify_cubic(stage,proof)
    kept=[old['initial_stage']['active_raw_parameter_indices'][i]for i in old['cubic_stage']['remaining_parameter_indices']]
    assert kept==old['rebuild_stage']['active_raw_parameter_indices']
    assert old['final_cubic_stage']['remaining_parameter_indices']==[]
    return {'status':'PASS','survivor_embedding':binding['embedding'],'physical_stages':checks,
            'physical_identities':167,'coordinate_cubes':25,
            'scope':'The surviving ten-parameter subspace is contained in the separately replayed excluded coordinate-divisible25 family.'}


def manifest():
    stages=[];gains=[];remaining=None
    for index in range(stage_count()):
        physical=original(index);rp=OUT/(prefix(index)+'reduced-quadrics.json.gz');reduced=load_basis('reduced',index)
        pp=OUT/(prefix(index)+'powers.json');proof=json.loads(pp.read_text());verify_powers(reduced,proof,0)
        if remaining is not None:assert physical['active_raw_parameter_indices']==remaining
        remaining=[physical['active_raw_parameter_indices'][i]for i in proof['remaining_local_parameters']]
        degrees=sorted({v['power']for v in proof['identities']})
        path=prior.stage_path(2)if index==0 else OUT/f'stage-{index:02d}-quadrics.json.gz'
        stages.append({'index':index,'physical_file':None if index==0 else path.name,'physical_sha256':sha(path),
                       'reduced_file':rp.name,'reduced_sha256':sha(rp),'power_proof_file':pp.name,'power_proof_sha256':sha(pp),
                       'power_degree':degrees[0]if len(degrees)==1 else'mixed'if degrees else None,
                       'parameters':len(physical['active_raw_parameter_indices']),'physical_rows':physical['rows'],'physical_columns':physical['columns'],
                       'rank':physical['rank'],'mixed_rank':physical['mixed_rank'],'necessary_quadrics':len(physical['equations']),
                       'newly_forced_raw_parameters':[physical['active_raw_parameter_indices'][v['parameter_index']]for v in proof['identities']]})
        if index:gains.append({'stage':index,**prior.rebuild_gain(original(index-1),physical)})
    attempts=[]
    for file in sorted(OUT.glob('*.json')):
        if not any(s in file.name for s in ('cubic-','quartic-','cas-','timeout')):continue
        data=json.loads(file.read_text());attempts.append({'file':file.name,'sha256':sha(file),'status':data['status']})
    prior_packet=prior.OUT/'packet.json';prior_receipt=prior.OUT/'independent-validation.json'
    return {'schema':'cyclic-fano-remaining66-multipliers-v1','status':'full_quadratic_direction_family_excluded','instance':'cyclic-triple-fano','q':1,'degree':7,
            'source_commit':'d96911d725077e66a8f10848908be01a643b1714','source_instance_sha256':poly.sha(base.SOURCE/'source/instance.rec'),
            'producer_sha256':poly.sha(Path(__file__)),'dependencies':{Path(m.__file__).name:poly.sha(Path(m.__file__))for m in(prior,prior.previous,prior.source,arithmetic,base,poly)},
            'prior_proof':{'packet':str(prior_packet.relative_to(ROOT)).replace('\\','/'),'packet_sha256':poly.sha(prior_packet),
                           'independent_receipt_sha256':poly.sha(prior_receipt),'primary_receipt_sha256':poly.sha(prior.OUT/'validation.json'),
                           'physical_file':str(prior.stage_path(2).relative_to(ROOT)).replace('\\','/'),'physical_sha256':sha(prior.stage_path(2)),
                           'initial_parameters':66,'prior_forced_raw_parameters':[8,13,26,28,38,53,56,61,66]},
            'parameter_order':prior.parameter_labels(),'stages':stages,'rebuild_diagnostics':gains,'attempts':attempts,
            'auxiliary_files':[{'file':f.name,'sha256':poly.sha(f),'hash_mode':'LF-normalized text'}for f in sorted(OUT.glob('cas-*'))if f.suffix!='.json'],
            'remaining_raw_parameter_indices':remaining,'complete_correction_types':55,'complete_raw_Koszul_fields':230,'quotient_directions':246,
            'coordinate_divisible_closure':closure_binding(remaining),
            'bounds':{'individual_primary_attempt_seconds':120,'modular_Singular_seconds':60,'aggregate_primary_replay_seconds':900},
            'conclusion':'Together with the bound prior75 reductions and the directly replayed coordinate-divisible25 exclusion, every nonzero homogeneous quadratic vector direction gives an excluded degree-seven polar denominator.',
            'limits':'This excludes the75-parameter quadratic-direction polar family only, not arbitrary degree-seven denominators. No HasCertificate proof, solution, or upstream acceptance is claimed. Timeouts yield no rank or nonmembership result; selected multiplier spaces are not the full homogeneous ideal.'}


def check_bindings(packet,expected):
    assert packet==expected


def verify_manifest(packet):
    expected_packet=manifest();check_bindings(packet,expected_packet);data=prior.source.system();checks=[];controls=0
    for info in packet['stages']:
        index=info['index'];physical=original(index);reduced=load_basis('reduced',index)
        physical_check=prior.replay_stage(physical,data);basis_check=verify_basis(physical,reduced)
        proof=json.loads((OUT/info['power_proof_file']).read_text());assert proof==combine_powers(reduced,index,'reduced')
        verify_powers(reduced,proof,0)
        if proof['identities']:
            bad=copy.deepcopy(proof);bad['identities'][0]['multipliers'][0]['coefficient']='0'
            try:verify_powers(reduced,bad,0)
            except AssertionError:controls+=1
            else:raise AssertionError('Corrupt power accepted')
        e=reduced['equations'][0];bad=copy.deepcopy(e);bad['combination'][0][1]=str(Q(bad['combination'][0][1])+1)
        old=[{(i,j):Q(c)for i,j,c in row['terms']}for row in physical['equations']]
        assert base.total(poly.scale(old[i],Q(c))for i,c in bad['combination'])!={(i,j):Q(c)for i,j,c in e['terms']};controls+=1
        checks.append({'index':index,'physical':physical_check,'equivalent_basis':basis_check,
                       'coordinate_powers':len(proof['identities']),'multiplier_terms':sum(len(i['multipliers'])for i in proof['identities'])})
        print(json.dumps({'stage':index,'status':'PASS','parameters':info['parameters']}),flush=True)
    completed=[];quartic_cache={}
    for record in packet['attempts']:
        attempt=json.loads((OUT/record['file']).read_text())
        if attempt['status']!='completed':continue
        if record['file'].startswith('cas-'):continue
        index=attempt.get('stage',0);stage=load_basis(attempt['basis'],index)
        if 'quartic' in record['file']:
            key=(index,attempt['basis'],attempt['term_threshold'])
            if key not in quartic_cache:quartic_cache[key]=prior.small_quartic(stage,attempt['term_threshold'])
            expected=quartic_cache[key]
            assert (attempt['rank'],attempt['columns'])==(expected['rank'],expected['columns'])
            if 'identities'in attempt:
                verify_powers(stage,attempt,4)
                assert [v['parameter_index']for v in attempt['identities']]==expected['coordinate_fourth_powers_found']
            else:assert attempt['coordinate_fourth_powers_found']==expected['coordinate_fourth_powers_found']
        else:prior.replay_small_space(stage,attempt)
        completed.append(record['file'])
    closure_check=replay_closure(packet['coordinate_divisible_closure'],packet['remaining_raw_parameter_indices'],data)
    for name in ('producer_sha256','source_instance_sha256','remaining_raw_parameter_indices','coordinate_divisible_closure'):
        bad=copy.deepcopy(packet);bad[name]=None
        try:check_bindings(bad,expected_packet)
        except AssertionError:controls+=1
        else:raise AssertionError('Corrupt binding accepted')
    save('validation.json',{'schema':'cyclic-fano-remaining66-multipliers-validation-v1','status':'PASS',
                           'producer_sha256':poly.sha(Path(__file__)),'packet_sha256':poly.sha(OUT/'packet.json'),
                           'stages':checks,'coordinate_divisible_closure':closure_check,'completed_attempts_replayed':completed,'negative_controls_rejected':controls,
                           'scope':'Source maps, exact basis combinations and power multipliers replayed; incomplete discovery attempts retained without rerunning their timeout.'})


def main():
    assert __debug__
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['cubic','_cubic','reduce','_reduce','quartic','_quartic','quartic-proof','_quartic-proof','combine','_combine','rebuild','_rebuild','run','_run','verify','_verify']);parser.add_argument('--threshold',type=int,default=128);parser.add_argument('--basis',choices=['original','reduced'],default='original');parser.add_argument('--bound',type=int,default=120);parser.add_argument('--stage',type=int,default=0);parser.add_argument('--degree',type=int,choices=[0,3,4],default=3);args=parser.parse_args()
    if not args.command.startswith('_'):
        started=time.perf_counter();name=prefix(args.stage)+args.command+'-'+args.basis+'-'+str(args.threshold)
        if args.command in ('run','verify'):args.bound=900
        try:result=subprocess.run([sys.executable,'-S',str(Path(__file__)),'_'+args.command,'--threshold',str(args.threshold),'--basis',args.basis,'--bound',str(args.bound),'--stage',str(args.stage),'--degree',str(args.degree)],timeout=args.bound)
        except subprocess.TimeoutExpired:
            save(name+'-timeout.json',{'status':'timeout','command':args.command,'stage':args.stage,'basis':args.basis,'threshold':args.threshold,'bound_seconds':args.bound,'elapsed_seconds':time.perf_counter()-started,'limits':'Incomplete search; no rank or nonmembership conclusion.'});raise SystemExit(2)
        raise SystemExit(result.returncode)
    started=time.perf_counter();OUT.mkdir(parents=True,exist_ok=True)
    if args.command in ('_run','_verify'):
        if args.command=='_run':
            for i in range(stage_count()):save(prefix(i)+'powers.json',combine_powers(load_basis('reduced',i),i,'reduced'))
            save('packet.json',manifest())
        else:verify_manifest(json.loads((OUT/'packet.json').read_text()))
        print(json.dumps({'status':'PASS','command':args.command[1:],'seconds':time.perf_counter()-started,'packet_sha256':poly.sha(OUT/'packet.json')}));return
    if args.command=='_rebuild':
        assert args.stage>0;old=load_basis(args.basis,args.stage-1)
        proofkind='cubic'if args.degree==3 else'quartic-proof'
        filename=prefix(args.stage-1)+'powers.json'if args.degree==0 else prefix(args.stage-1)+proofkind+'-'+args.basis+'-'+str(args.threshold)+'.json'
        proof=json.loads((OUT/filename).read_text());verify_powers(old,proof,args.degree)
        active=[old['active_raw_parameter_indices'][i]for i in proof['remaining_local_parameters']]
        assert len(active)<len(old['active_raw_parameter_indices'])
        stage=prior.compact_stage(prior.previous.necessary_equations(active));raw=(json.dumps(stage,separators=(',',':'))+'\n').encode()
        path=OUT/f'stage-{args.stage:02d}-quadrics.json.gz';path.write_bytes(gzip.compress(raw,mtime=0))
        summary={'status':'PASS','stage':args.stage,'parameters':len(active),'necessary_quadrics':len(stage['equations']),'rank':stage['rank'],'mixed_rank':stage['mixed_rank'],'seconds':time.perf_counter()-started,'gzip_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'rebuild_diagnostic':prior.rebuild_gain(original(args.stage-1),stage)}
        save(prefix(args.stage)+'rebuild-validation.json',summary);print(json.dumps(summary));return
    if args.command=='_reduce':
        result=reduce_basis(original(args.stage));raw=(json.dumps(result,separators=(',',':'))+'\n').encode()
        path=OUT/(prefix(args.stage)+'reduced-quadrics.json.gz');path.write_bytes(gzip.compress(raw,mtime=0))
        summary={k:v for k,v in result.items()if k!='equations'and k!='active_raw_parameter_indices'}
        summary.update({'status':'PASS','seconds':time.perf_counter()-started,'gzip_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        save(prefix(args.stage)+'reduced-basis-validation.json',summary);print(json.dumps(summary));return
    stage=load_basis(args.basis,args.stage)
    if args.command=='_combine':
        result=combine_powers(stage,args.stage,args.basis);save(prefix(args.stage)+'powers.json',result)
        print(json.dumps({'stage':args.stage,'status':'PASS','raw_parameters':[stage['active_raw_parameter_indices'][i['parameter_index']]for i in result['identities']]}));return
    if args.command=='_cubic':
        result=prior.sparse_cubes(stage,args.threshold);prior.verify_cubes(stage,result)
    elif args.command=='_quartic-proof':result=quartic_proof(stage,args.threshold)
    else:result=prior.small_quartic(stage,args.threshold)
    result.update({'stage':args.stage,'basis':args.basis,'bound_seconds':args.bound,'elapsed_seconds':time.perf_counter()-started})
    name=prefix(args.stage)+args.command[1:]+'-'+args.basis+'-'+str(args.threshold)+'.json';save(name,result)
    print(json.dumps({k:v for k,v in result.items()if k not in ('equation_indices','active_raw_parameter_indices','remaining_local_parameters','identities')}|{'coordinate_powers':[stage['active_raw_parameter_indices'][v['parameter_index']]for v in result.get('identities',[])]}))


if __name__=='__main__':main()
