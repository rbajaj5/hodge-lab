"""Goal-directed character projection of mixed-degree necessary relations.

This is separate from the frozen rewrite-cache timing comparison. Full and
filtered Macaulay maps answer the same added-character coordinate-power
queries. Off-type rows are omitted only after checking their exact grading.
"""
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations_with_replacement
from pathlib import Path
import argparse, copy, json, subprocess, sys, time
import typed_rewrite_search as s
import check_typed_rewrite_families as check_families

h=s.h
OUT=h.OUT/'goal-powers'
DEGREES=[3,4]
LIMIT=180


def read(path):return json.loads(path.read_text(encoding='utf-8'))


def signature(mon,weights):
    return (len(mon),)+tuple(sum(weights[i][j] for i in mon)%6 for j in range(3))


def homogeneous(poly,weights):
    types={signature(mon,weights) for mon in poly}
    assert len(types)==1
    return next(iter(types))


def setup(model,number):
    item=h.selection(model)[number-1]
    source=h.OUT/f'baseline-{number:03d}.json.gz'
    ids,counts=check_families.baseline(model,item,h.q.load(source))
    desc,physical,typing,labels,digest=s.setup(model,number)
    assert desc['basis_indices']==ids
    packetpath=s.OUT/(s.basename(number,'typed',0)+'.json.gz')
    packet=h.q.load(packetpath)
    prefix=packet['rows_processed']
    assert len(physical)<=prefix<=len(labels)
    assert prefix%len(physical)==0
    if packet['completed']:assert prefix==len(labels)
    assert packet['job']=={'number':number,'mode':'typed','replicate':0}
    assert packet['source_sha256']==digest and packet['system']==desc and packet['typing']==typing
    assert packet['plan_sha256']==s.sha(read(s.OUT/'plan.json'))
    nD=len(ids);variables=list(range(nD))
    old,new,total=s.syz.select_new(packet['baseline'],packet['relations'],variables)
    assert new==packet['selected_new']
    selected=packet['baseline']+[packet['relations'][i] for i in new]
    allowed=set(labels[:prefix])
    assert all(not mon for r in packet['baseline'] for _,mon,_ in r['products'])
    for row in selected:
        assert all((j,tuple(mon)) in allowed for j,mon,_ in row['products'])
        counts['necessary_relation_products']+=s.syz.verify_relation(physical,nD,variables,row)
    eq=[h.cert.decode(row['polynomial']) for row in selected]
    weights=typing['variable_weights'][:nD]
    types=[homogeneous(row,weights) for row in eq]
    assert all(t[0] in [2,3] for t in types)
    targets=[i for i,raw in enumerate(ids) if model.dc[raw]==tuple(item['third_character'])]
    assert targets
    meta={'family':number,'system':desc,'source_packet_sha256':h.digest(packetpath),
          'baseline_packet_sha256':h.digest(source),'weights':weights,
          'source_run_completed':packet['completed'],'source_rows':prefix,
          'source_requested_rows':len(physical)*(nD+1),
          'generator_types':[list(t) for t in types],'generator_count':len(eq),
          'target_local_indices':targets,'target_raw_indices':[ids[i] for i in targets]}
    return item,meta,eq,counts


def maps(eq,weights,nvars,degree,target_character):
    labels=[];rows=[];types=[]
    for j,poly in enumerate(eq):
        gd=homogeneous(poly,weights)[0]
        if gd>degree:continue
        for mon in combinations_with_replacement(range(nvars),degree-gd):
            row=h.cert.product(poly,{mon:Q(1)})
            typ=homogeneous(row,weights);assert typ[0]==degree
            labels.append((j,mon));rows.append(row);types.append(typ)
    target=(degree,)+tuple(target_character)
    selected=[i for i,t in enumerate(types) if t==target]
    selected_set=set(selected)
    # Literal coefficient projection: excluded rows have zero target component,
    # and selected rows have no coefficient in any other component.
    projected=[]
    for i,row in enumerate(rows):
        p={m:c for m,c in row.items() if signature(m,weights)==target}
        assert p==(row if i in selected_set else {})
        if p:projected.append((i,p))
    assert [i for i,_ in projected]==selected
    return labels,rows,types,selected


def query(eq,weights,meta,degree):
    targets=meta['target_local_indices'];nvars=len(weights)
    chars={tuple((degree*x)%6 for x in weights[i]) for i in targets};assert len(chars)==1
    char=next(iter(chars));labels,rows,types,selected=maps(eq,weights,nvars,degree,char)
    full,_,rank=h.cert.reduce_span(rows)
    small,_,smallrank=h.cert.reduce_span([rows[i] for i in selected])
    answers=[]
    for i in targets:
        target={(i,)*degree:Q(1)};a=full(target);b=small(target)
        assert bool(a)==bool(b),'Projection must preserve the target membership question'
        def products(w,indices):
            if w is None:return None
            out=[[labels[indices[j]][0],list(labels[indices[j]][1]),c] for j,c in w['equation_weights']]
            assert h.e.expand_products(eq,out)==target
            return out
        answers.append({'local':i,'raw':meta['system']['basis_indices'][i],
            'power':degree,'found':bool(a),'full_products':products(a,list(range(len(rows)))),
            'typed_products':products(b,selected)})
    return {'degree':degree,'target_character':list(char),'full_rows':len(rows),
        'typed_rows':len(selected),'full_rank':rank,'typed_rank':smallrank,
        'full_nonzeros':sum(map(len,rows)),
        'typed_nonzeros':sum(len(rows[i]) for i in selected),
        'selected_indices':selected,'type_counts':[[list(t),n] for t,n in sorted(Counter(types).items())],
        'matrix_sha256':s.sha({'labels':[[j,list(m)] for j,m in labels],
                              'rows':[h.cert.encode(p) for p in rows]}),
        'queries':answers}


def freeze():
    assert not (OUT/'plan.json').exists(),'Preserve the first bounded attempt'
    p=read(s.OUT/'plan.json');cases=[r['number'] for r in p['cases']]
    plan={'families':cases,'comparison_plan_sha256':s.sha(p),'degrees':DEGREES,
          'seconds_per_family':LIMIT,'workers':1,'source_mode':'typed replicate 0 retained checkpoint',
          'target':'Every retained coefficient in the added character; no anchor coefficients set to zero.',
          'method':'Same complete mixed-degree Macaulay map, with exact target-character projection.',
          'limits':'Coordinate-power queries only; no global rank equality, timing speedup, or full ideal claim.'}
    (OUT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')


def produce(number):
    plan=read(OUT/'plan.json');assert number in plan['families']
    model=h.Model();item,meta,eq,counts=setup(model,number)
    packet={'family':number,'plan_sha256':s.sha(plan),'metadata':meta,
            'records':[],'completed':False}
    path=OUT/f'family-{number:03d}.json.gz';h.q.save(path,packet)
    for degree in DEGREES:
        record=query(eq,meta['weights'],meta,degree)
        packet['records'].append(record);h.q.save(path,packet)
        print(number,degree,record['full_rows'],'->',record['typed_rows'],
              'powers',[(q['raw'],q['found']) for q in record['queries']],flush=True)
    packet['completed']=True;h.q.save(path,packet)


def run():
    plan=read(OUT/'plan.json');assert not (OUT/'attempts.json').exists()
    attempts=[]
    for number in plan['families']:
        started=time.perf_counter()
        try:
            p=subprocess.run([sys.executable,'-S',str(Path(__file__).resolve()),'--produce',str(number)],
                text=True,capture_output=True,encoding='utf-8',timeout=LIMIT)
            status='completed' if p.returncode==0 else 'error';code=p.returncode;output=p.stdout+p.stderr
        except subprocess.TimeoutExpired as ex:
            dec=lambda x:x.decode('utf-8',errors='replace') if isinstance(x,bytes) else x or ''
            status='timeout';code=None;output=dec(ex.stdout)+dec(ex.stderr)
        (OUT/f'family-{number:03d}.log').write_text(output,encoding='utf-8')
        a={'family':number,'status':status,'exit_code':code,'limit':LIMIT,'seconds':time.perf_counter()-started}
        attempts.append(a);(OUT/'attempts.json').write_text(json.dumps(attempts,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(a),output,flush=True)


def check(independent=False):
    if independent:
        from check_degree7_triples import IndependentModel
        model=IndependentModel()
    else:model=h.Model()
    plan=read(OUT/'plan.json');comparison=read(s.OUT/'plan.json');attempts=read(OUT/'attempts.json')
    assert plan['families']==[r['number'] for r in comparison['cases']]
    assert plan['comparison_plan_sha256']==s.sha(comparison) and plan['degrees']==DEGREES
    assert plan['seconds_per_family']==LIMIT and plan['workers']==1 and plan['source_mode']=='typed replicate 0 retained checkpoint'
    assert [a['family'] for a in attempts]==plan['families']
    cases=[];counts=Counter();pair=None;pair_counts=Counter()
    for attempt in attempts:
        n=attempt['family'];assert attempt['limit']==LIMIT and attempt['seconds']>=0
        assert attempt['status'] in ['completed','timeout','error']
        if attempt['status']=='completed':assert attempt['exit_code']==0
        elif attempt['status']=='timeout':assert attempt['exit_code'] is None
        else:assert isinstance(attempt['exit_code'],int) and attempt['exit_code']!=0
        path=OUT/f'family-{n:03d}.json.gz'
        if not path.exists():
            assert attempt['status']!='completed';cases.append({'family':n,'no_packet':True});continue
        item,meta,eq,cc=setup(model,n);counts.update(cc);packet=h.q.load(path)
        assert packet['family']==n and packet['plan_sha256']==s.sha(plan) and packet['metadata']==meta
        degrees=[r['degree'] for r in packet['records']];assert degrees==DEGREES[:len(degrees)]
        if packet['completed']:assert degrees==DEGREES
        if attempt['status']=='completed':assert packet['completed']
        forced=set()
        for record in packet['records']:
            assert record==query(eq,meta['weights'],meta,record['degree'])
            counts['full_and_projected_maps']+=2;counts['coordinate_power_queries']+=len(record['queries'])
            for answer in record['queries']:
                if answer['found']:
                    forced.add(answer['raw']);counts['power_identities']+=2
                    bad=copy.deepcopy(answer['typed_products']);bad[0][2]=str(Q(bad[0][2])+1)
                    assert h.e.expand_products(eq,bad)!={(answer['local'],)*answer['power']:Q(1)}
                    counts['altered_powers_rejected']+=1
        ids=[i for i in meta['system']['basis_indices'] if i not in forced]
        ending=h.terminal(model,ids)
        if ending=='x0_y1_dependency' and pair is None:pair,pair_counts=check_families.replay_pair(model)
        assert ending in [None,'x0_y1_dependency']
        cases.append({'family':n,'completed':packet['completed'],'forced_raw':sorted(forced),
                      'remaining':ids,'excluded':ending is not None,'metadata':meta,'records':packet['records']})
    report={'status':'PASS','independent_physical_polynomials':independent,'cases':cases,
        'checks':dict(counts),'pair_dependency':pair,'pair_checks':dict(pair_counts),
        'scope':'Same finite coordinate-power questions in full and exactly projected maps. Overlaps with ordinary continuation are not counted twice.'}
    (OUT/(('independent-' if independent else '')+'validation.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'PASS','cases':[{k:r.get(k) for k in ['family','forced_raw','excluded']} for r in cases],
                      'checks':dict(counts)}),flush=True)


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    OUT.mkdir(parents=True,exist_ok=True)
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--freeze',action='store_true')
    p.add_argument('--run',action='store_true');p.add_argument('--produce',type=int)
    p.add_argument('--check',action='store_true');p.add_argument('--independent',action='store_true');a=p.parse_args()
    if a.freeze:freeze()
    elif a.run:run()
    elif a.produce is not None:produce(a.produce)
    elif a.check:check(a.independent)
