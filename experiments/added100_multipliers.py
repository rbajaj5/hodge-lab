"""Bounded shared-numerator multiplier continuation for added-character A100.

The original comparison and continuation packets remain unchanged. This
separate experiment uses constants and all linear denominator multipliers,
eliminating every numerator-containing monomial before denominator monomials.
Its exported relations are necessary conditions, not family exclusions.
"""
from fractions import Fraction as Q
from collections import Counter
from pathlib import Path
import argparse,copy,json,subprocess,sys,time
import added_character_homology as h
import family151_multipliers as f
import degree7_syzygies as syz

OUT=h.OUT/'multipliers-100'


def build(model):
    item=h.selection(model)[99];source=h.OUT/'follow-100.json.gz';packet=h.q.load(source)
    assert packet['batch_number']==100 and packet['completed'] and packet['status']=='unresolved'
    desc,eq=h.build(model,item,packet['remaining'])
    assert desc['pivots']==[0,10]
    return desc,eq,h.digest(source)


def produce():
    start=time.perf_counter();desc,eq,digest=build(h.t.Model());nD=len(desc['basis_indices'])
    span=h.t.base.Elimination()
    packet={'batch_number':100,'system':desc,'source_sha256':digest,
        'multiplier_degree_bound':1,'completed':False,'completed_multipliers':[],
        'baseline':[],'relations':[],'selected_new':[],'checkpoints':[]}
    path=OUT/'global.json.gz'
    h.q.save(path,packet)
    for mon in [()]+[(i,) for i in range(nD)]:
        for j,row in enumerate(eq):
            value={(0 if any(i>=nD for i in m+mon) else 1,tuple(sorted(m+mon))):c for m,c in row.items()}
            span.insert(value,{(j,mon):Q(1)})
        packet['relations']=f.relations(span)
        if not mon:packet['baseline']=packet['relations'][:]
        old,new,total=syz.select_new(packet['baseline'],packet['relations'],list(range(nD)))
        packet['selected_new']=new;packet['completed_multipliers'].append(list(mon))
        packet['checkpoints'].append({'multiplier':list(mon),'relations':len(packet['relations']),
            'additional':len(new),'baseline_multiple_rank':old,'combined_rank':total,
            'equation_rank':len(span.basis)})
        packet['seconds']=time.perf_counter()-start;h.q.save(path,packet)
        print(mon,len(packet['relations']),len(new),round(packet['seconds'],3),flush=True)
    packet['completed']=True;h.q.save(path,packet)


def check(independent=False):
    start=time.perf_counter()
    if independent:
        from check_degree7_triples import IndependentModel
        model=IndependentModel()
    else:model=h.t.Model()
    desc,eq,digest=build(model);p=h.q.load(OUT/'global.json.gz')
    assert p['system']==desc and p['source_sha256']==digest and p['multiplier_degree_bound']==1
    nD=len(desc['basis_indices']);variables=list(range(nD));expected=[[]]+[[i] for i in variables]
    plan=json.loads((OUT/'plan.json').read_text(encoding='utf-8'))
    attempt=json.loads((OUT/'attempt.json').read_text(encoding='utf-8'))
    assert plan['batch_number']==p['batch_number']==100
    assert plan['system']==desc and plan['source_sha256']==digest
    assert plan['multipliers']==expected and plan['multiplier_degree_bound']==1
    assert plan['physical_equation_count']==len(eq) and plan['workers']==1
    assert 0<plan['seconds']==attempt['limit']<=180
    assert attempt['status'] in ['completed','timeout','error']
    if attempt['status']=='completed':assert attempt['exit_code']==0 and p['completed']
    elif attempt['status']=='timeout':assert attempt['exit_code'] is None
    else:assert isinstance(attempt['exit_code'],int) and attempt['exit_code']!=0
    assert p['completed_multipliers']==expected[:len(p['completed_multipliers'])]
    if p['completed']:assert p['completed_multipliers']==expected
    assert p['completed_multipliers'],'No complete multiplier block was retained'
    baseline,_=syz.necessary_relations(eq,nD,[()]);assert baseline==p['baseline']
    independence=h.t.base.Elimination()
    for r in p['relations']:
        polynomial=h.cert.decode(r['polynomial'])
        assert polynomial and max(map(len,polynomial))<=3
        assert independence.insert(polynomial) is None
        assert all(mon in p['completed_multipliers'] for _,mon,_ in r['products'])
    assert [r['multiplier'] for r in p['checkpoints']]==p['completed_multipliers']
    products=sum(syz.verify_relation(eq,nD,variables,r) for r in p['relations']+p['baseline'])
    old,new,total=syz.select_new(p['baseline'],p['relations'],variables)
    assert new==p['selected_new'] and old==p['checkpoints'][-1]['baseline_multiple_rank']
    assert total==p['checkpoints'][-1]['combined_rank']
    broken=copy.deepcopy(p['relations'][0]);broken['products'][0][2]=str(Q(broken['products'][0][2])+1)
    try:syz.verify_relation(eq,nD,variables,broken)
    except AssertionError:pass
    else:raise AssertionError('Altered multiplier accepted')
    pure=[];rows=p['baseline']+[p['relations'][j] for j in new]
    for char in sorted({model.dc[i] for i in desc['basis_indices']}):
        ids=[j for j,i in enumerate(desc['basis_indices']) if model.dc[i]==char]
        indices=[i for i,r in enumerate(rows) if all(j in ids for m in h.cert.decode(r['polynomial']) for j in m)]
        pure.append({'character':list(char),'variables':ids,'raw_ids':[desc['basis_indices'][i] for i in ids],
            'relation_indices':indices})
    report={'status':'PASS','independent_physical_polynomials':independent,
        'completed':p['completed'],'multiplier_blocks':len(p['completed_multipliers']),
        'requested_blocks':nD+1,'baseline_relations':len(p['baseline']),
        'additional_relations':len(new),'coefficient_products':products,'mutation_rejected':True,
        'pure_blocks':pure,'seconds':time.perf_counter()-start,
        'scope':'Necessary denominator relations verified over Q; no A100 exclusion or full projected ideal claim.'}
    (OUT/(('independent-' if independent else '')+'validation.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2),flush=True)


def block_setup(model):
    import family151_cubic_blocks as cb
    source=OUT/'global.json.gz';p=h.q.load(source);desc,physical,digest=build(model)
    assert p['system']==desc and p['source_sha256']==digest
    relations=p['baseline']+[p['relations'][j] for j in p['selected_new']]
    nD=len(desc['basis_indices']);variables=list(range(nD))
    products=sum(syz.verify_relation(physical,nD,variables,r) for r in relations)
    eq=[h.cert.decode(r['polynomial']) for r in relations]
    groups=[]
    for char in sorted({model.dc[i] for i in desc['basis_indices']}):
        ids=[j for j,i in enumerate(desc['basis_indices']) if model.dc[i]==char]
        chosen=[j for j,p in enumerate(eq) if all(i in ids for m in p for i in m)]
        groups.append({'character':list(char),'ids':ids,
            'raw_ids':[desc['basis_indices'][i] for i in ids],'equation_indices':chosen})
    return desc,eq,groups,products,cb


def produce_blocks():
    desc,eq,groups,_,cb=block_setup(h.t.Model())
    packet={'source_sha256':h.digest(OUT/'global.json.gz'),'system':desc,
        'degree_bound':4,'blocks':[],'completed':False}
    path=OUT/'pure-blocks.json.gz';h.q.save(path,packet)
    for group in groups:
        block={**group,'strands':[]};packet['blocks'].append(block)
        small=[eq[i] for i in group['equation_indices']]
        for degree in [3,4]:
            record=cb.strand(small,group['ids'],degree);cb.verify_strand(small,group['ids'],record)
            block['strands'].append(record);h.q.save(path,packet)
            print(group['character'],'degree',degree,'rank',record['rank'],'/',record['codomain'],
                'zeros',[desc['basis_indices'][w['coordinate']] for w in record['vanishings']],flush=True)
    packet['completed']=True;h.q.save(path,packet)


def check_bounded_phase(phase,completed):
    plan=json.loads((OUT/f'{phase}-plan.json').read_text(encoding='utf-8'))
    attempt=json.loads((OUT/f'{phase}-attempt.json').read_text(encoding='utf-8'))
    source=OUT/('global.json.gz' if phase=='blocks' else 'pure-blocks.json.gz')
    assert plan['batch_number']==100 and plan['phase']==phase
    assert plan['source_sha256']==h.digest(source) and plan['degree_bound']==4
    assert plan['workers']==1 and 0<plan['seconds']==attempt['limit']<=180
    assert attempt['status'] in ['completed','timeout','error'] and attempt['seconds']>=0
    if attempt['status']=='completed':assert attempt['exit_code']==0 and completed
    elif attempt['status']=='timeout':assert attempt['exit_code'] is None
    else:assert isinstance(attempt['exit_code'],int) and attempt['exit_code']!=0


def replay_blocks(model):
    desc,eq,groups,products,cb=block_setup(model);p=h.q.load(OUT/'pure-blocks.json.gz')
    assert p['source_sha256']==h.digest(OUT/'global.json.gz') and p['system']==desc
    assert p['degree_bound']==4
    check_bounded_phase('blocks',p['completed'])
    assert len(p['blocks'])<=len(groups)
    if p['completed']:assert len(p['blocks'])==len(groups)
    forced=set();counts=Counter(relation_products=products);details=[]
    for block,group in zip(p['blocks'],groups):
        for key,value in group.items():assert block[key]==value
        degrees=[r['degree'] for r in block['strands']];assert degrees==[3,4][:len(degrees)]
        if p['completed']:assert degrees==[3,4]
        small=[eq[i] for i in group['equation_indices']]
        detail={**group,'maps':[]}
        for record in block['strands']:
            cb.verify_strand(small,group['ids'],record);counts['graded_maps']+=1
            detail['maps'].append({k:record[k] for k in ['degree','domain','codomain','rank','kernel','quotient_dimension']})
            for witness in record['vanishings']:
                forced.add(desc['basis_indices'][witness['coordinate']]);counts['power_identities']+=1
                counts['power_products']+=len(witness['products'])
                broken=copy.deepcopy(witness['products']);broken[0][2]=str(Q(broken[0][2])+1)
                assert h.e.expand_products(small,broken)!={(witness['coordinate'],)*witness['power']:Q(1)}
                counts['altered_powers_rejected']+=1
        detail['forced_raw_ids']=sorted({desc['basis_indices'][w['coordinate']] for r in block['strands'] for w in r['vanishings']})
        details.append(detail)
    return desc,sorted(forced),counts,details,p['completed']


def check_blocks(independent=False):
    if independent:
        from check_degree7_triples import IndependentModel
        model=IndependentModel()
    else:model=h.t.Model()
    desc,forced,counts,details,completed=replay_blocks(model)
    report={'status':'PASS','independent_physical_polynomials':independent,'completed':completed,
        'forced_raw_ids':forced,'blocks':details,'checks':dict(counts),
        'scope':'Exact coordinate-power consequences of the verified selected necessary relations; no family exclusion by this packet alone.'}
    (OUT/(('independent-' if independent else '')+'blocks-validation.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2),flush=True)


def produce_closure():
    model=h.t.Model();desc,forced,_,_,complete=replay_blocks(model);assert complete
    ids=[i for i in desc['basis_indices'] if i not in forced];item=h.selection(model)[99]
    packet={'batch_number':100,'forced':forced,'source_sha256':h.digest(OUT/'pure-blocks.json.gz'),
        'cycles':[],'completed':False,'remaining':ids};path=OUT/'closure.json.gz';h.q.save(path,packet)
    if not forced:
        packet.update(completed=True,status='no_new_coordinate_powers');h.q.save(path,packet);return
    for cycle in range(len(ids)+1):
        blockpath=OUT/f'power-rebuilt-{cycle}.json.gz'
        h.x.family(model,item,initial=ids,destination=blockpath,finish=h.terminal)
        stage={'before':ids,'block_file':blockpath.name,'block_sha256':h.digest(blockpath)}
        ids=h.q.load(blockpath)['remaining'];packet['cycles'].append(stage)
        packet['remaining']=ids;h.q.save(path,packet)
        if h.terminal(model,ids):break
        system,eq=h.build(model,item,ids);stage['system']=system;stage['charts']=[]
        nv=len(ids)+len(system['Koszul_indices'])
        for pivot in system['pivots']:
            chart=h.cert.prove_chart(eq,nv,pivot);h.cert.verify_chart(eq,nv,chart)
            stage['charts'].append(chart);h.q.save(path,packet)
            print('rebuilt',cycle,'chart',ids[pivot],chart['excluded'],flush=True)
        removed=[ids[c['pivot']] for c in stage['charts'] if c['excluded']]
        stage['removed']=removed;ids=[i for i in ids if i not in removed]
        packet['remaining']=ids;h.q.save(path,packet)
        if not removed:break
    else:raise AssertionError('Successful cycles strictly decrease coordinates')
    packet.update(completed=True,status=h.terminal(model,ids) or 'unresolved',remaining=ids)
    h.q.save(path,packet);print('A100 continuation',packet['status'],ids,flush=True)


def check_closure(independent=False):
    from check_x1y1_extensions import replay_stages
    from check_quartic_exclusions import single_character
    from added_homology_pair import replay as replay_pair
    if independent:
        from check_degree7_triples import IndependentModel
        model=IndependentModel()
    else:model=h.t.Model()
    desc,forced,counts,_,complete=replay_blocks(model);assert complete
    ids=[i for i in desc['basis_indices'] if i not in forced];item=h.selection(model)[99]
    p=h.q.load(OUT/'closure.json.gz')
    assert p['batch_number']==100 and p['forced']==forced
    assert p['source_sha256']==h.digest(OUT/'pure-blocks.json.gz')
    check_bounded_phase('closure',p['completed'])
    cycles=[]
    for cycle,stage in enumerate(p['cycles']):
        assert stage['before']==ids and stage['block_file']==f'power-rebuilt-{cycle}.json.gz'
        path=OUT/stage['block_file'];assert h.digest(path)==stage['block_sha256']
        block=h.q.load(path)
        for k,v in item.items():assert block[k]==v
        assert block['starting_indices']==ids and block['sources']==h.e.source_hashes() and block['completed']
        ids,zeros,_,cc=replay_stages(model,block,ids,finish=h.terminal);counts.update(cc)
        assert block['status']==(h.terminal(model,ids) or 'unresolved_bounded_search')
        detail={'before':stage['before'],'block_zeros':zeros,'after_blocks':ids[:],'charts':[]}
        if 'system' in stage:
            assert not h.terminal(model,ids)
            system,eq=h.build(model,item,ids);assert system==stage['system']
            assert [c['pivot'] for c in stage['charts']]==system['pivots'][:len(stage['charts'])]
            if p['completed'] or 'removed' in stage:assert [c['pivot'] for c in stage['charts']]==system['pivots']
            removed=[];nv=len(ids)+len(system['Koszul_indices'])
            for chart in stage['charts']:
                counts['chart_inferences']+=h.cert.verify_chart(eq,nv,chart);counts['charts']+=1
                detail['charts'].append({'raw':ids[chart['pivot']],'excluded':chart['excluded']})
                if chart['excluded']:removed.append(ids[chart['pivot']]);counts['excluded_charts']+=1
            if 'removed' in stage:
                assert stage['removed']==removed;ids=[i for i in ids if i not in removed]
        detail['after']=ids[:];cycles.append(detail)
    assert p['remaining']==ids;ending=h.terminal(model,ids);dependency=None
    if p['completed']:assert p['status']==(ending or ('unresolved' if forced else 'no_new_coordinate_powers'))
    if ending=='x0_x1_dependency':dependency,cc=replay_pair(model);counts.update(cc)
    elif ending=='single_character_dependency':dependency=single_character(model,model.dc[ids[0]],ids)
    report={'status':'PASS','independent_physical_polynomials':independent,'completed':p['completed'],
        'excluded':ending is not None,'forced_raw_ids':forced,'remaining':ids,'cycles':cycles,
        'checks':dict(counts),'dependency':dependency,
        'scope':'Separate A100 continuation; the original 131/132 comparison batch remains unchanged.'}
    (OUT/(('independent-' if independent else '')+'closure-validation.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2),flush=True)


def run(limit,phase='global'):
    assert 0<limit<=180
    stem='' if phase=='global' else phase+'-'
    assert not (OUT/f'{stem}plan.json').exists(),'Preserve the first bounded attempt'
    desc,eq,digest=build(h.t.Model())
    plan={'batch_number':100,'seconds':limit,'workers':1,'multiplier_degree_bound':1,
        'multipliers':[[]]+[[i] for i in range(len(desc['basis_indices']))],
        'source_sha256':digest,'system':desc,'physical_equation_count':len(eq),
        'checkpoint_scope':'Only fully processed multiplier blocks are retained; interrupted blocks are omitted.'}
    if phase!='global':
        source=OUT/('global.json.gz' if phase=='blocks' else 'pure-blocks.json.gz')
        plan={'batch_number':100,'phase':phase,'seconds':limit,'workers':1,'source_sha256':h.digest(source),
            'degree_bound':4,'scope':'Pure-character degree 3/4 maps' if phase=='blocks' else 'Rebuild only after exact coordinate powers; same chart method'}
    (OUT/f'{stem}plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    start=time.perf_counter()
    try:
        flag='--produce' if phase=='global' else '--produce-'+phase
        p=subprocess.run([sys.executable,'-S',str(Path(__file__).resolve()),flag],capture_output=True,text=True,encoding='utf-8',timeout=limit)
        output=p.stdout+p.stderr;code=p.returncode;status='completed' if code==0 else 'error'
    except subprocess.TimeoutExpired as ex:
        dec=lambda v:v.decode('utf-8',errors='replace') if isinstance(v,bytes) else v or ''
        output=dec(ex.stdout)+dec(ex.stderr);code=None;status='timeout'
    (OUT/f'{stem}attempt.log').write_text(output,encoding='utf-8')
    result={'status':status,'exit_code':code,'seconds':time.perf_counter()-start,'limit':limit}
    (OUT/f'{stem}attempt.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result),output,flush=True)


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    OUT.mkdir(parents=True,exist_ok=True)
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--produce',action='store_true')
    p.add_argument('--check',action='store_true');p.add_argument('--independent',action='store_true')
    p.add_argument('--produce-blocks',action='store_true');p.add_argument('--check-blocks',action='store_true')
    p.add_argument('--produce-closure',action='store_true');p.add_argument('--check-closure',action='store_true')
    p.add_argument('--phase',choices=['global','blocks','closure'],default='global')
    p.add_argument('--limit',type=int,default=180);a=p.parse_args()
    if a.produce:produce()
    elif a.produce_blocks:produce_blocks()
    elif a.produce_closure:produce_closure()
    elif a.check_blocks:check_blocks(a.independent)
    elif a.check_closure:check_closure(a.independent)
    elif a.check:check(a.independent)
    else:run(a.limit,a.phase)
