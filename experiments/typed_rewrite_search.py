"""Matched exact multiplier search with typed, proof-carrying zero rewrites.

This is an experiment inspired by a typing invariant, not an implementation
of a grammar theorem. The reference is the existing direct-minimum-pivot
Elimination. The typed version follows the same elimination and caches exact
normalized residual identities R=sum c_j E_j, permitting the rewrite R -> 0.
These identities remain true when the basis grows; nonzero normal forms are
never cached. Every used rule and final coefficient basis has exact witnesses.
"""
from collections import Counter,OrderedDict
from fractions import Fraction as Q
from pathlib import Path
import argparse,copy,hashlib,json,subprocess,sys,time
import typed_rewrite_families as h
import family151_multipliers as multiplier
import degree7_syzygies as syz

OUT=h.OUT/'comparison'
LIMIT=180
ROW_BUDGET=10000
CACHE_ENTRIES=256
CACHE_TERMS=50000
SNAPSHOTS=8
RULE_TERMS=1000


def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'))
def sha(value):return hashlib.sha256(canonical(value).encode()).hexdigest()
def encoded_key(key):return [key[0],list(key[1])]
def decode_key(key):return key[0],tuple(key[1])
def encode_row(row):return [[encoded_key(k),str(c)] for k,c in sorted(row.items())]
def decode_row(row):return {decode_key(k):Q(c) for k,c in row}
def encode_products(row):return [[j,list(mon),str(c)] for (j,mon),c in sorted(row.items()) if c]
def decode_products(row):return {(j,tuple(mon)):Q(c) for j,mon,c in row if Q(c)}


def derive_typing(model,desc,eq):
    """Derive an auxiliary coefficient grading from the actual physical fields."""
    weights=h.t.e1.WEIGHTS
    char=lambda m:tuple(sum(a*b for a,b in zip(w,m))%6 for w in weights)
    alpha=model.alpha;result=[]
    for raw in desc['basis_indices']:
        characters={char(m) for m in model.pairs[raw][0]}
        assert characters=={model.dc[raw]};result.append(next(iter(characters)))
    for raw in desc['Koszul_indices']:
        chars={tuple((a-w[component])%6 for a,w in zip(char(m),weights))
            for component,p in enumerate(model.fields[raw]) for m in p}
        assert len(chars)==1
        result.append(h.t.minus(next(iter(chars)),alpha))
    def typeof(mon):return (len(mon),)+tuple(sum(result[i][j] for i in mon)%6 for j in range(3))
    equation_types=[]
    for row in eq:
        types={typeof(m) for m in row};assert len(types)==1
        typ=types.pop();assert typ[0]==2;equation_types.append(list(typ))
    return {'denominator_weight':'character of the actual D_i polynomial',
        'numerator_weight':'character of actual K_j vector field minus character(A)',
        'interpretation':'Auxiliary grading of coefficient equations, not the contragredient action on numerical coefficients.',
        'alpha':list(alpha),'variable_weights':[list(c) for c in result],
        'equation_types':equation_types}


def setup(model,number):
    item=h.selection(model)[number-1];source=h.OUT/f'baseline-{number:03d}.json.gz';row=h.q.load(source)
    assert row['completed'] and not h.terminal(model,row['remaining'])
    desc,eq=h.build(model,item,row['remaining']);typing=derive_typing(model,desc,eq)
    nD=len(desc['basis_indices']);multipliers=[()]+[(i,) for i in range(nD)]
    labels=[(j,mon) for mon in multipliers for j in range(len(eq))]
    labels=labels[:ROW_BUDGET]
    return desc,eq,typing,labels,h.digest(source)


def row_type(row,weights):
    types={(len(mon),)+tuple(sum(weights[i][j] for i in mon)%6 for j in range(3)) for _,mon in row}
    assert len(types)==1
    return next(iter(types))


def physical_row(eq,nD,label):
    j,mon=label
    return {(int(not any(i>=nD for i in m+mon)),tuple(sorted(m+mon))):c for m,c in eq[j].items()}


def matrix_data(model,number):
    desc,eq,typing,labels,source=setup(model,number);nD=len(desc['basis_indices'])
    rows=[physical_row(eq,nD,label) for label in labels]
    cols=sorted({k for row in rows for k in row});lookup={k:i for i,k in enumerate(cols)}
    types=[list(row_type(r,typing['variable_weights'])) for r in rows]
    entries=[[i,lookup[k],str(c)] for i,row in enumerate(rows) for k,c in sorted(row.items())]
    column_types=[list(row_type({k:Q(1)},typing['variable_weights'])) for k in cols]
    assert all(types[i]==column_types[j] for i,j,_ in entries)
    info={'family':number,'system':desc,'source_sha256':source,'typing':typing,
        'row_labels':[[j,list(m)] for j,m in labels],'columns':[encoded_key(k) for k in cols],
        'row_types':types,'column_types':column_types,'entries':entries,
        'requested_rows':len(eq)*(nD+1),'row_budget':ROW_BUDGET}
    info['matrix_sha256']=sha(info)
    return info


def freeze():
    assert not (OUT/'plan.json').exists(),'Preserve the prospective comparison'
    model=h.Model();survivors=h.survivors(model);selected=survivors[:2];assert len(selected)==2
    # No comparison outcome has been generated before this deterministic choice.
    cases=[]
    for number in selected:
        desc,eq,typing,labels,source=setup(model,number)
        cases.append({'number':number,'system':desc,'typing':typing,'source_sha256':source,
            'physical_equations':len(eq),'requested_rows':len(eq)*(len(desc['basis_indices'])+1),
            'budgeted_rows':len(labels)})
    jobs=[]
    for replicate in range(2):
        modes=['untyped','typed'] if replicate==0 else ['typed','untyped']
        for number in selected:
            for mode in modes:jobs.append({'number':number,'mode':mode,'replicate':replicate})
    plan={'selection':'first two square-baseline survivors in increasing batch number','survivors':survivors,
        'cases':cases,'jobs':jobs,'workers':1,'seconds_per_process':LIMIT,'row_budget':ROW_BUDGET,
        'row_order':'constant, then each denominator variable in local order; original physical equation order within each multiplier',
        'multiplier_degree_bound':1,'cache':{'entries':CACHE_ENTRIES,'coefficient_terms':CACHE_TERMS,
            'snapshots_per_row':SNAPSHOTS,'max_rule_terms':RULE_TERMS},
        'reference':'Existing base.Elimination with direct minimum-pivot dictionary lookup; no irrelevant-pivot scanning.',
        'typed':'Same pivot strategy plus bounded type-keyed exact normalized residual-to-zero rewrite cache.',
        'timing':'Sequential isolated processes; two alternating mode orders. Runtime is exploratory and host activity is not controlled.',
        'limits':'Necessary relations only; no grammar theorem, speed theorem, family exclusion, or full projected-ideal claim.'}
    (OUT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'selected':selected,'cases':[(c['number'],c['budgeted_rows']) for c in cases],'jobs':len(jobs)}),flush=True)


class TypedRewrite:
    def __init__(self,weights,label_index):
        self.basis={};self.operations=0;self.weights=weights;self.label_index=label_index
        self.cache=OrderedDict();self.cache_terms=0;self.stats=Counter()
        self.used_rules=[];self.used_lookup={};self.applications=[];self.row_number=-1

    def add_rule(self,typ,key,proof):
        assert key and proof
        assert all(self.label_index[label]<self.row_number for label in proof)
        terms=len(key)+len(proof)
        if terms>RULE_TERMS or terms>CACHE_TERMS:self.stats['oversize_rules_skipped']+=1;return
        cachekey=(typ,key)
        if cachekey in self.cache:return
        while self.cache and (len(self.cache)>=CACHE_ENTRIES or self.cache_terms+terms>CACHE_TERMS):
            _,old=self.cache.popitem(last=False);self.cache_terms-=old['terms'];self.stats['evictions']+=1
        self.cache[cachekey]={'type':typ,'row':dict(key),'proof':proof,'terms':terms,
            'created_row':self.row_number,'created_rank':len(self.basis)}
        self.cache_terms+=terms;self.stats['rules_created']+=1
        self.stats['peak_cache_entries']=max(self.stats['peak_cache_entries'],len(self.cache))
        self.stats['peak_cache_terms']=max(self.stats['peak_cache_terms'],self.cache_terms)

    def insert(self,v,comb):
        typ=row_type(v,self.weights);snapshots=[]
        while v:
            k=min(v);c=v[k];self.stats['pivot_tests']+=1
            if k not in self.basis:
                inv=Q(1,c);self.basis[k]=({i:a*inv for i,a in v.items()},{i:a*inv for i,a in comb.items()})
                return None
            key=tuple((i,a/c) for i,a in sorted(v.items()))
            cachekey=(typ,key);self.stats['cache_lookups']+=1
            rule=self.cache.get(cachekey)
            if rule is not None:
                self.stats['cache_hits']+=1;self.cache.move_to_end(cachekey)
                assert rule['type']==typ and rule['created_row']<self.row_number
                # Delta is a proof of this residual, never a previous input's final combination.
                comb=h.t.base.padd(comb,rule['proof'],-c)
                identity=(typ,key,tuple(sorted(rule['proof'].items())))
                if identity not in self.used_lookup:
                    self.used_lookup[identity]=len(self.used_rules)
                    self.used_rules.append({'type':list(typ),'row':encode_row(rule['row']),
                        'products':encode_products(rule['proof']),'created_row':rule['created_row'],
                        'created_rank':rule['created_rank']})
                self.applications.append({'rule':self.used_lookup[identity],'row':self.row_number,'scale':str(c),
                    'use_rank':len(self.basis)})
                v={};break
            if len(snapshots)<SNAPSHOTS and len(key)+len(comb)<=RULE_TERMS:
                snapshots.append((key,c,dict(comb)))
            other,track=self.basis[k]
            v=h.t.base.padd(v,other,-c);comb=h.t.base.padd(comb,track,-c)
            self.operations+=1
        for key,c,before in snapshots:
            delta=h.t.base.padd(before,comb,-1)
            delta={i:a/c for i,a in delta.items() if a}
            self.add_rule(typ,key,delta)
        return comb


def basename(number,mode,replicate):return f'family-{number:03d}-{mode}-{replicate}'


def produce(number,mode,replicate):
    plan=json.loads((OUT/'plan.json').read_text(encoding='utf-8'));job={'number':number,'mode':mode,'replicate':replicate}
    assert job in plan['jobs'];model=h.Model();desc,eq,typing,labels,source=setup(model,number)
    case=next(c for c in plan['cases'] if c['number']==number)
    assert case['system']==desc and case['typing']==typing and case['source_sha256']==source
    nD=len(desc['basis_indices']);label_index={label:i for i,label in enumerate(labels)}
    span=h.t.base.Elimination() if mode=='untyped' else TypedRewrite(typing['variable_weights'],label_index)
    packet={'job':job,'plan_sha256':sha(plan),'source_sha256':source,
        'system':desc,'typing':typing,'completed':False,'rows_processed':0,'checkpoints':[],
        'basis':[],'baseline':[],'relations':[],'selected_new':[],'used_rules':[],'applications':[]}
    path=OUT/(basename(number,mode,replicate)+'.json.gz');elapsed=0.;h.q.save(path,packet)
    for i,label in enumerate(labels):
        row=physical_row(eq,nD,label)
        if mode=='typed':span.row_number=i
        started=time.perf_counter();span.insert(row,{label:Q(1)});elapsed+=time.perf_counter()-started
        if (i+1)%len(eq)==0 or i+1==len(labels):
            packet['rows_processed']=i+1
            packet['basis']=[{'pivot':encoded_key(k),'row':encode_row(p),'products':encode_products(track)}
                for k,(p,track) in sorted(span.basis.items())]
            packet['relations']=multiplier.relations(span)
            if i+1==len(eq):packet['baseline']=packet['relations'][:]
            old,new,total=syz.select_new(packet['baseline'],packet['relations'],list(range(nD)))
            packet['selected_new']=new
            stats=dict(span.stats) if mode=='typed' else {'pivot_tests':span.operations+len(span.basis)}
            stats.update(elimination_steps=span.operations)
            if mode=='typed':
                stats.update(retained_cache_entries=len(span.cache),retained_cache_terms=span.cache_terms)
                packet['used_rules']=span.used_rules;packet['applications']=span.applications
            packet['statistics']=stats;packet['elimination_seconds']=elapsed
            packet['checkpoints'].append({'rows':i+1,'rank':len(span.basis),'relations':len(packet['relations']),
                'additional':len(new),'baseline_multiple_rank':old,'combined_rank':total,
                'elimination_seconds':elapsed,'statistics':stats})
            packet['basis_sha256']=sha([r['row'] for r in packet['basis']]);h.q.save(path,packet)
            print(number,mode,replicate,i+1,len(span.basis),len(new),round(elapsed,3),flush=True)
    packet['completed']=True;packet['full_requested_rows_completed']=len(labels)==len(eq)*(nD+1)
    h.q.save(path,packet)


def run():
    plan=json.loads((OUT/'plan.json').read_text(encoding='utf-8'))
    assert not (OUT/'attempts.json').exists(),'Preserve the original sequential runs'
    attempts=[]
    for job in plan['jobs']:
        name=basename(job['number'],job['mode'],job['replicate']);start=time.perf_counter()
        command=[sys.executable,'-S',str(Path(__file__).resolve()),'--produce',str(job['number']),job['mode'],str(job['replicate'])]
        try:
            p=subprocess.run(command,text=True,capture_output=True,encoding='utf-8',timeout=plan['seconds_per_process'])
            output=p.stdout+p.stderr;code=p.returncode;status='completed' if code==0 else 'error'
        except subprocess.TimeoutExpired as ex:
            dec=lambda v:v.decode('utf-8',errors='replace') if isinstance(v,bytes) else v or ''
            output=dec(ex.stdout)+dec(ex.stderr);code=None;status='timeout'
        (OUT/(name+'.log')).write_text(output,encoding='utf-8')
        attempt={**job,'status':status,'exit_code':code,'wall_seconds':time.perf_counter()-start,'limit':plan['seconds_per_process']}
        attempts.append(attempt);(OUT/'attempts.json').write_text(json.dumps(attempts,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(attempt),output,flush=True)


def replay_products(eq,nD,products,label_index,prefix):
    result={}
    for j,mon,value in products:
        label=(j,tuple(mon));assert label in label_index and label_index[label]<prefix
        coefficient=Q(value)
        for key,c in physical_row(eq,nD,label).items():
            new=result.get(key,Q(0))+coefficient*c
            if new:result[key]=new
            elif key in result:del result[key]
    return result


def check_rule(rule,eq,nD,weights,label_index):
    row=decode_row(rule['row']);assert row and row[min(row)]==1
    assert list(row_type(row,weights))==rule['type']
    assert replay_products(eq,nD,rule['products'],label_index,rule['created_row'])==row
    assert len(rule['row'])+len(rule['products'])<=RULE_TERMS


def check_packet(model,number,mode,replicate,attempt,proof_cache=None):
    desc,eq,typing,labels,source=setup(model,number);nD=len(desc['basis_indices'])
    label_index={label:i for i,label in enumerate(labels)};path=OUT/(basename(number,mode,replicate)+'.json.gz')
    if not path.exists():
        assert attempt['status'] in ['error','timeout'];return {'job':attempt,'no_packet':True}
    p=h.q.load(path);assert p['job']=={'number':number,'mode':mode,'replicate':replicate}
    assert p['plan_sha256']==sha(json.loads((OUT/'plan.json').read_text(encoding='utf-8'))) and p['source_sha256']==source
    assert p['system']==desc and p['typing']==typing
    prefix=p['rows_processed'];assert 0<=prefix<=len(labels)
    if p['completed']:
        assert prefix==len(labels)
        assert p['full_requested_rows_completed']==(len(labels)==len(eq)*(nD+1))
    assert attempt['status'] in ['completed','timeout','error'] and attempt['wall_seconds']>=0
    if attempt['status']=='completed':assert p['completed'] and attempt['exit_code']==0
    elif attempt['status']=='timeout':assert attempt['exit_code'] is None
    else:assert isinstance(attempt['exit_code'],int) and attempt['exit_code']!=0
    assert attempt['limit']==LIMIT
    if prefix==0:return {'job':attempt,'rows':0,'completed':p['completed']}
    proof_cache={} if proof_cache is None else proof_cache
    payload={k:p[k] for k in ['system','typing','source_sha256','rows_processed','basis','baseline','relations','selected_new']}
    previous=proof_cache.get((number,prefix));reused=previous is not None and previous['payload']==payload
    if reused:basis,products=previous['basis'],previous['products']
    else:
        basis={};products=0
        for row in p['basis']:
            pivot=decode_key(row['pivot']);poly=decode_row(row['row'])
            assert poly and min(poly)==pivot and poly[pivot]==1 and pivot not in basis
            assert replay_products(eq,nD,row['products'],label_index,prefix)==poly
            row_type(poly,typing['variable_weights']);basis[pivot]=poly;products+=len(row['products'])
        # Both containments: basis rows have source witnesses, and every processed
        # input row reduces to zero against this triangular independent basis.
        for label in labels[:prefix]:
            row=physical_row(eq,nD,label)
            while row:
                pivot=min(row);assert pivot in basis;coefficient=row[pivot]
                for key,c in basis[pivot].items():
                    new=row.get(key,Q(0))-coefficient*c
                    if new:row[key]=new
                    elif key in row:del row[key]
        proof_cache[number,prefix]={'payload':payload,'basis':basis,'products':products}
    assert p['basis_sha256']==sha([r['row'] for r in p['basis']])
    counts=Counter(basis_coefficient_products=0 if reused else products,source_rows_reduced=0 if reused else prefix,used_rules=len(p['used_rules']))
    if reused:counts['exact_proof_content_reused']=1
    for rule in p['used_rules']:check_rule(rule,eq,nD,typing['variable_weights'],label_index)
    for application in p['applications']:
        rule=p['used_rules'][application['rule']]
        assert rule['created_row']<application['row']<prefix and Q(application['scale'])
        assert rule['created_rank']<=application['use_rank']<=len(basis)
    stats=p['statistics']
    assert p['elimination_seconds']>=0 and stats['elimination_steps']>=0
    assert p['checkpoints'][-1]['rows']==prefix and p['checkpoints'][-1]['rank']==len(basis)
    expected_checkpoints=list(range(len(eq),prefix+1,len(eq)))
    if prefix%len(eq):expected_checkpoints.append(prefix)
    assert [c['rows'] for c in p['checkpoints']]==expected_checkpoints
    assert p['checkpoints'][-1]['statistics']==stats
    if mode=='typed':
        assert stats.get('cache_hits',0)==len(p['applications'])
        assert stats.get('peak_cache_entries',0)<=CACHE_ENTRIES and stats.get('peak_cache_terms',0)<=CACHE_TERMS
        assert stats.get('retained_cache_entries',0)<=CACHE_ENTRIES and stats.get('retained_cache_terms',0)<=CACHE_TERMS
        if p['used_rules']:
            bad=copy.deepcopy(p['used_rules'][0]);bad['type'][1]=(bad['type'][1]+1)%6
            try:check_rule(bad,eq,nD,typing['variable_weights'],label_index)
            except AssertionError:counts['wrong_type_rejected']+=1
            else:raise AssertionError('Incorrect rule type accepted')
            bad=copy.deepcopy(p['used_rules'][0]);bad['products'][0][2]=str(Q(bad['products'][0][2])+1)
            try:check_rule(bad,eq,nD,typing['variable_weights'],label_index)
            except AssertionError:counts['altered_rule_rejected']+=1
            else:raise AssertionError('Altered rule witness accepted')
    else:assert not p['used_rules'] and not p['applications']
    # Match exported necessary relations to the actual coefficient basis.
    expected=[{'polynomial':h.cert.encode({m:c for (_,m),c in decode_row(r['row']).items()}),
        'products':r['products']} for r in p['basis'] if decode_key(r['pivot'])[0]==1]
    assert expected==p['relations']
    baseline,_=syz.necessary_relations(eq,nD,[()]);assert baseline==p['baseline']
    old,new,total=syz.select_new(p['baseline'],p['relations'],list(range(nD)))
    assert new==p['selected_new'] and old==p['checkpoints'][-1]['baseline_multiple_rank'] and total==p['checkpoints'][-1]['combined_rank']
    return {'job':p['job'],'completed':p['completed'],'rows':prefix,'requested_rows':len(eq)*(nD+1),
        'basis_sha256':p['basis_sha256'],'rank':len(basis),'baseline_relations':len(baseline),
        'additional_relations':len(new),'statistics':stats,'checks':dict(counts),
        'exact_proof_reused':reused,'proof_evidence_size':{'basis_products':products,'source_rows':prefix},
        'elimination_seconds':p['elimination_seconds'],'wall_seconds':attempt['wall_seconds']}


def cache_selftest():
    """The zero rule survives basis growth and adjusts a new witness context."""
    eq=[{(0,0):Q(1)},{(0,0):Q(2)},{(1,1):Q(1)},{(0,0):Q(3)}]
    labels=[(j,()) for j in range(4)];lookup={v:i for i,v in enumerate(labels)}
    weights=[[0,0,0],[0,1,0]];span=TypedRewrite(weights,lookup)
    final=None
    for i,label in enumerate(labels):
        span.row_number=i;final=span.insert(physical_row(eq,2,label),{label:Q(1)})
    assert final=={(3,()):Q(1),(0,()):Q(-3)}
    assert len(span.used_rules)==len(span.applications)==1
    rule=span.used_rules[0];application=span.applications[0]
    assert rule['created_rank']==1 and application['use_rank']==2
    check_rule(rule,eq,2,weights,lookup)
    bad=copy.deepcopy(rule);bad['products']=[[3,[],str(Q(1,3))]]
    try:check_rule(bad,eq,2,weights,lookup)
    except AssertionError:pass
    else:raise AssertionError('A valid polynomial identity using future work was accepted')
    return {'zero_rule_survives_basis_growth':True,'new_witness_context_adjusted':True,
        'future_source_row_rejected':True}


def check(independent=False):
    if independent:
        from check_degree7_triples import IndependentModel
        model=IndependentModel()
    else:model=h.Model()
    plan=json.loads((OUT/'plan.json').read_text(encoding='utf-8'));attempts=json.loads((OUT/'attempts.json').read_text(encoding='utf-8'))
    assert plan['survivors']==h.survivors(model) and [c['number'] for c in plan['cases']]==plan['survivors'][:2]
    assert plan['workers']==1 and plan['seconds_per_process']==LIMIT and plan['row_budget']==ROW_BUDGET
    assert plan['multiplier_degree_bound']==1
    assert plan['cache']=={'entries':CACHE_ENTRIES,'coefficient_terms':CACHE_TERMS,
        'snapshots_per_row':SNAPSHOTS,'max_rule_terms':RULE_TERMS}
    selected=plan['survivors'][:2]
    expected_jobs=[{'number':n,'mode':mode,'replicate':r} for r in range(2) for n in selected
        for mode in (['untyped','typed'] if r==0 else ['typed','untyped'])]
    assert plan['jobs']==expected_jobs
    for case in plan['cases']:
        desc,eq,typing,labels,source=setup(model,case['number'])
        assert case=={'number':case['number'],'system':desc,'typing':typing,'source_sha256':source,
            'physical_equations':len(eq),'requested_rows':len(eq)*(len(desc['basis_indices'])+1),
            'budgeted_rows':len(labels)}
    assert [{k:a[k] for k in ['number','mode','replicate']} for a in attempts]==plan['jobs']
    records=[];proof_cache={}
    for a in attempts:
        records.append(check_packet(model,a['number'],a['mode'],a['replicate'],a,proof_cache))
        print('verified',a['number'],a['mode'],a['replicate'],flush=True)
    matches=[]
    for case in plan['cases']:
        rs=[r for r in records if r['job']['number']==case['number']]
        completed=[r for r in rs if r.get('completed')]
        if len(completed)==4:
            assert len({r['basis_sha256'] for r in completed})==1
            matches.append({'number':case['number'],'all_four_completed':True,'equal_coefficient_basis':True,
                'rows':completed[0]['rows'],'rank':completed[0]['rank']})
        else:matches.append({'number':case['number'],'all_four_completed':False,
            'limits':'No matched full-work timing or complete-span claim for interrupted runs.'})
    report={'status':'PASS','independent_physical_polynomials':independent,'records':records,'matches':matches,
        'cache_selftest':cache_selftest(),
        'scope':'Exact processed-prefix rowspaces and used zero rewrites; matched completed-work timing is exploratory, not a speed theorem or family exclusion.'}
    (OUT/(('independent-' if independent else '')+'validation.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'PASS','matches':matches}),flush=True)


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    OUT.mkdir(parents=True,exist_ok=True)
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--freeze',action='store_true');p.add_argument('--run',action='store_true')
    p.add_argument('--produce',nargs=3,metavar=('NUMBER','MODE','REPLICATE'));p.add_argument('--check',action='store_true')
    p.add_argument('--independent',action='store_true');a=p.parse_args()
    if a.freeze:freeze()
    elif a.run:run()
    elif a.produce:produce(int(a.produce[0]),a.produce[1],int(a.produce[2]))
    elif a.check:check(a.independent)
