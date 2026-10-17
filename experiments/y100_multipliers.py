"""Bounded polynomial-syzygy probe of the remaining Y0/X1 batch case 100."""
from fractions import Fraction as Q
from pathlib import Path
import argparse,copy,hashlib,json,subprocess,sys,time
import y0x1_extensions as y
import family151_multipliers as f
import degree7_syzygies as syz
OUT=y.OUT/'multipliers-100'


def build(model):
    item=y.selection(model)[99];source=y.OUT/'follow-100.json.gz';p=y.q.load(source)
    assert p['completed'] and p['status']=='unresolved_shared_charts'
    desc,eq=y.build(model,item,p['remaining']);return desc,eq,hashlib.sha256(source.read_bytes()).hexdigest()


def produce():
    start=time.perf_counter();desc,eq,digest=build(y.t.Model());nD=len(desc['basis_indices']);span=y.t.base.Elimination()
    packet={'system':desc,'source_sha256':digest,'completed':False,'completed_multipliers':[],
        'baseline':[],'relations':[],'selected_new':[],'checkpoints':[]}
    for mon in [()]+[(i,) for i in range(nD)]:
        for j,row in enumerate(eq):
            p={(0 if any(i>=nD for i in m+mon) else 1,tuple(sorted(m+mon))):c for m,c in row.items()}
            span.insert(p,{(j,mon):Q(1)})
        packet['relations']=f.relations(span)
        if not mon:packet['baseline']=packet['relations'][:]
        old,new,total=syz.select_new(packet['baseline'],packet['relations'],list(range(nD)))
        packet['selected_new']=new;packet['completed_multipliers'].append(list(mon))
        packet['checkpoints'].append({'multiplier':list(mon),'relations':len(packet['relations']),
            'additional':len(new),'baseline_multiple_rank':old,'combined_rank':total})
        packet['seconds']=time.perf_counter()-start;y.q.save(OUT/'global.json.gz',packet)
        print(mon,len(packet['relations']),len(new),round(packet['seconds'],2),flush=True)
    packet['completed']=True;y.q.save(OUT/'global.json.gz',packet)


def check(independent=False):
    if independent:
        from check_degree7_triples import IndependentModel
        model=IndependentModel()
    else:model=y.t.Model()
    desc,eq,digest=build(model);p=y.q.load(OUT/'global.json.gz');assert p['system']==desc and p['source_sha256']==digest
    nD=len(desc['basis_indices']);variables=list(range(nD));assert p['completed_multipliers']==[[]]+[[i] for i in variables][:len(p['completed_multipliers'])-1]
    if p['completed']:assert len(p['completed_multipliers'])==nD+1
    baseline,_=syz.necessary_relations(eq,nD,[()]);assert baseline==p['baseline']
    independence=y.t.base.Elimination()
    for r in p['relations']:
        assert independence.insert(y.cert.decode(r['polynomial'])) is None
        assert all(mon in p['completed_multipliers'] for _,mon,_ in r['products'])
    assert [r['multiplier'] for r in p['checkpoints']]==p['completed_multipliers']
    counts=sum(syz.verify_relation(eq,nD,variables,r) for r in p['relations'])
    counts+=sum(syz.verify_relation(eq,nD,variables,r) for r in p['baseline'])
    old,new,total=syz.select_new(p['baseline'],p['relations'],variables);assert new==p['selected_new']
    assert old==p['checkpoints'][-1]['baseline_multiple_rank'] and total==p['checkpoints'][-1]['combined_rank']
    broken=copy.deepcopy(p['relations'][0]);broken['products'][0][2]=str(Q(broken['products'][0][2])+1)
    try:syz.verify_relation(eq,nD,variables,broken)
    except AssertionError:pass
    else:raise AssertionError('Altered multiplier accepted')
    pure=[]
    for char in sorted({model.dc[i] for i in desc['basis_indices']}):
        ids=[j for j,i in enumerate(desc['basis_indices']) if model.dc[i]==char]
        rows=[r for r in p['baseline']]+[p['relations'][j] for j in new]
        indices=[i for i,r in enumerate(rows) if all(j in ids for m in y.cert.decode(r['polynomial']) for j in m)]
        pure.append({'character':list(char),'variables':ids,'relation_indices':indices})
    report={'status':'PASS','independent_physical_polynomials':independent,'completed':p['completed'],
        'multiplier_blocks':len(p['completed_multipliers']),'requested_blocks':nD+1,
        'baseline_relations':len(p['baseline']),'additional_relations':len(new),'coefficient_products':counts,
        'mutation_rejected':True,'pure_blocks':pure,'scope':'Verified necessary relations only; no family exclusion is asserted by this probe.'}
    (OUT/(('independent-' if independent else '')+'validation.json')).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


def blocks(check=False):
    import family151_cubic_blocks as cb
    model=y.t.Model();source=OUT/'global.json.gz';p=y.q.load(source)
    eq=[y.cert.decode(r['polynomial']) for r in p['baseline']]+[y.cert.decode(p['relations'][j]['polynomial']) for j in p['selected_new']]
    ids=p['system']['basis_indices'];result=[]
    old=y.q.load(OUT/'pure-blocks.json.gz') if check else None
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    if check:assert old['source_sha256']==digest
    for b,char in enumerate(sorted({model.dc[i] for i in ids})):
        smallids=[j for j,i in enumerate(ids) if model.dc[i]==char]
        chosen=[j for j,r in enumerate(eq) if all(i in smallids for m in r for i in m)];small=[eq[j] for j in chosen]
        records=[]
        for degree in [3,4]:
            strand=old['blocks'][b]['strands'][degree-3] if check else cb.strand(small,smallids,degree)
            cb.verify_strand(small,smallids,strand);records.append(strand)
        block={'character':list(char),'ids':smallids,'equation_indices':chosen,'strands':records}
        if check:assert block==old['blocks'][b]
        result.append(block)
        print(char,[(r['degree'],r['rank'],r['codomain'],[ids[v['coordinate']] for v in r['vanishings']]) for r in records])
    if not check:y.q.save(OUT/'pure-blocks.json.gz',{'source_sha256':digest,'blocks':result,'completed':True,'max_degree':4})


def run(limit):
    (OUT/'plan.json').write_text(json.dumps({'seconds':limit,'multipliers':'constant and all 13 denominator coordinates','workers':1},indent=2)+'\n')
    start=time.perf_counter()
    try:
        p=subprocess.run([sys.executable,'-S',str(Path(__file__).resolve()),'--produce'],capture_output=True,text=True,encoding='utf-8',timeout=limit)
        output=p.stdout+p.stderr;code=p.returncode;status='completed' if code==0 else 'error'
    except subprocess.TimeoutExpired as ex:
        dec=lambda v:v.decode('utf-8',errors='replace') if isinstance(v,bytes) else v or ''
        output=dec(ex.stdout)+dec(ex.stderr);code=None;status='timeout'
    (OUT/'attempt.log').write_text(output,encoding='utf-8')
    r={'status':status,'exit_code':code,'seconds':time.perf_counter()-start,'limit':limit}
    (OUT/'attempt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),output)


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    OUT.mkdir(parents=True,exist_ok=True);p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--produce',action='store_true');p.add_argument('--blocks',action='store_true');p.add_argument('--check',action='store_true');p.add_argument('--independent',action='store_true');p.add_argument('--limit',type=int,default=180);a=p.parse_args()
    if a.blocks:blocks(a.check)
    elif a.produce:produce()
    elif a.check:check(a.independent)
    else:run(a.limit)
