"""Prospective finite homology ranking of new Y0/Y1 triple families."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,time
import y0x1_extensions as y
import necessary_koszul_complex as kh
import degree7_triple_shared as shared
from check_quartic_exclusions import shared_system
x=y.x;e=x.e;t=x.t;cert=x.cert;q=x.q
OUT=e.ROOT/'results/homology-guided-triples'
ANCHOR={(1,2,3),(5,3,0)}


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def selection(model):
    previous=set(model.families)|{tuple(tuple(c) for c in r['characters']) for r in x.selection(model)+y.selection(model)}
    assert len(previous)==416
    triples=sorted({tuple(sorted((*ANCHOR,c))) for c in model.groups if c not in ANCHOR}-previous)
    assert len(triples)==132
    wanted=set(triples);global_ids={c:i for i,c in enumerate(combinations(sorted(model.groups),3),1) if c in wanted}
    return [{'batch_number':i,'global_number':global_ids[c],'characters':[list(a) for a in c],
        'third_character':list(next(a for a in c if a not in ANCHOR)),
        'basis_indices':sorted(j for a in c for j in model.groups[a])} for i,c in enumerate(triples,1)]


def terminal(model,ids):
    if not ids:return 'excluded_directly'
    chars={model.dc[i] for i in ids}
    if chars<=ANCHOR:return 'y0_y1_dependency'
    if len(chars)==1:return 'single_character_dependency'
    return None


def pair_binding():
    import check_quartic_exclusions as c
    model=t.Model();ids=sorted(i for char in ANCHOR for i in model.groups[char])
    old=q.load(c.q.OUT/'y0-y1-closure.json.gz')['ids']
    finish=lambda model,active:'prior_pair_dependency' if set(active)<=set(old) else None
    x.family(model,{'characters':sorted(map(list,ANCHOR)),'basis_indices':ids,'batch_number':0,'third_character':None},
        destination=OUT/'full-pair-binding.json.gz',finish=finish)


def baseline(model,item):
    ids=item['basis_indices'][:];packet={**item,'sources':e.source_hashes(),'stages':[],'completed':False}
    path=OUT/f"baseline-{item['batch_number']:03d}.json.gz"
    for _ in range(len(ids)+1):
        if terminal(model,ids):break
        necessary,ranks=model.necessities(ids);eq=[cert.decode(r['polynomial']) for r in necessary]
        witness,_,rank=cert.reduce_span(eq);squares=[]
        for i in ids:
            w=witness({(i,i):Q(1)})
            if w:squares.append({'coordinate':i,'products':[[j,[],c] for j,c in w['equation_weights']]})
        packet['stages'].append({'active':ids,'necessary':necessary,'correction_ranks':ranks,
            'rank':rank,'squares':squares})
        ids=[i for i in ids if i not in {w['coordinate'] for w in squares}]
        packet['remaining']=ids;q.save(path,packet)
        if not squares:break
    else:raise AssertionError('Coordinate count must decrease')
    packet.update(completed=True,remaining=ids,status=terminal(model,ids) or 'unresolved_squares')
    q.save(path,packet);print(item['batch_number'],len(item['basis_indices']),'->',len(ids),packet['status'],flush=True)


def survivors(model):
    return [r['batch_number'] for p in sorted(OUT.glob('baseline-*.json.gz'))
        if (r:=q.load(p))['completed'] and not terminal(model,r['remaining'])]


def profile(number):
    model=t.Model();path=OUT/f'baseline-{number:03d}.json.gz';packet=q.load(path)
    assert not terminal(model,packet['remaining']);stage=packet['stages'][-1]
    assert stage['active']==packet['remaining'];eq=[cert.decode(r['polynomial']) for r in stage['necessary']]
    result={'batch_number':number,'source_sha256':digest(path),'blocks':[],'completed':False}
    for char in sorted({model.dc[i] for i in packet['remaining']}):
        ids=[i for i in packet['remaining'] if model.dc[i]==char]
        selected=[j for j,p in enumerate(eq) if all(i in ids for m in p for i in m)]
        small=[eq[j] for j in selected];records=[kh.complex_at(small,ids,d) for d in [3,4]] if small else []
        block={'character':list(char),'ids':ids,'equation_indices':selected,'homology':records}
        result['blocks'].append(block);q.save(OUT/f'profile-{number:03d}.json.gz',result)
    result['score']=sum(b['homology'][1]['homology'][1] for b in result['blocks'] if b['homology'])
    result['score_degree3']=sum(b['homology'][0]['homology'][1] for b in result['blocks'] if b['homology'])
    result['completed']=True;q.save(OUT/f'profile-{number:03d}.json.gz',result)
    print(number,'H1 degree 3,4:',result['score_degree3'],result['score'],flush=True)


def rank_plan():
    model=t.Model();records=[]
    for n in survivors(model):
        p=OUT/f'profile-{n:03d}.json.gz';r=q.load(p)
        assert r['completed'];records.append({'number':n,'score':r['score'],'profile_sha256':digest(p)})
    order=sorted(records,key=lambda r:(-r['score'],r['number']))
    high=order[:min(4,len(order))];used={r['number'] for r in high}
    low=sorted([r for r in records if r['number'] not in used],key=lambda r:(r['score'],r['number']))[:4]
    p={'score':'sum of dim H1 at total degree 4 over pure-character necessary blocks',
        'ordering':'descending score, then ascending batch number',
        'high':high,'low_control':low,'all_profiles':order,
        'strategy':'same degree 3/4 blocks, shared affine/square charts, and rebuilding for both groups',
        'follow_seconds_per_family':120,'workers':2,
        'limits':'Prospective priority heuristic; not a randomized efficacy trial. No theorem equates H1 with new constraints.'}
    assert not (OUT/'ranking-plan.json').exists(),'Keep the original prospective ranking'
    (OUT/'ranking-plan.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8');print(json.dumps(p,indent=2))


def build(model,item,ids):
    if len({model.dc[i] for i in ids})==3:
        return shared.construct(model,{'number':item['global_number'],'remaining':ids,'characters':item['characters']},anchor=ANCHOR)
    s=shared_system(model,ids);eq=[cert.decode(p) for p in s['equations']]
    return {'family':item['global_number'],'characters':s['characters'],'basis_indices':ids,'Koszul_indices':s['ks'],
        'stabilizer_order':s['subgroup_order'],'equations_sha256':hashlib.sha256(json.dumps(s,sort_keys=True).encode()).hexdigest(),
        'pivots':list(range(len(ids)))},eq


def follow(number):
    model=t.Model();item=selection(model)[number-1];source=OUT/f'baseline-{number:03d}.json.gz';ids=q.load(source)['remaining'][:]
    p={'batch_number':number,'source_sha256':digest(source),'cycles':[],'completed':False,'remaining':ids}
    path=OUT/f'follow-{number:03d}.json.gz'
    for cycle in range(len(ids)+1):
        blockpath=OUT/f'rebuild-{number:03d}-{cycle}.json.gz'
        x.family(model,item,initial=ids,destination=blockpath,finish=terminal)
        stage={'before':ids,'block_file':blockpath.name,'block_sha256':digest(blockpath)}
        ids=q.load(blockpath)['remaining'];p['cycles'].append(stage);p['remaining']=ids;q.save(path,p)
        if terminal(model,ids):break
        desc,eq=build(model,item,ids);stage['system']=desc;stage['charts']=[]
        for pivot in desc['pivots']:
            c=cert.prove_chart(eq,len(ids)+len(desc['Koszul_indices']),pivot)
            cert.verify_chart(eq,len(ids)+len(desc['Koszul_indices']),c)
            stage['charts'].append(c);q.save(path,p);print(number,cycle,'chart',ids[pivot],c['excluded'],flush=True)
        removed=[ids[c['pivot']] for c in stage['charts'] if c['excluded']];stage['removed']=removed
        ids=[i for i in ids if i not in removed];p['remaining']=ids;q.save(path,p)
        if not removed:break
    else:raise AssertionError('Each cycle must decrease coordinates')
    p.update(completed=True,status=terminal(model,ids) or 'unresolved');q.save(path,p);print(number,p['status'],flush=True)


def run(phase,limit):
    model=t.Model();items=selection(model)
    if phase=='baseline':jobs=[0,1]
    elif phase=='profile':jobs=survivors(model)
    else:
        p=json.loads((OUT/'ranking-plan.json').read_text(encoding='utf-8'))
        jobs=[r['number'] for r in p['high']+p['low_control']]
        assert limit==p['follow_seconds_per_family']
        if phase=='remaining':jobs=[r['number'] for r in p['all_profiles'] if r['number'] not in jobs]
    plan={'phase':phase,'jobs':jobs,'seconds_per_job':limit,'workers':2,'sources':e.source_hashes(),'selection':items}
    (OUT/f'{phase}-plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    def worker(n):
        start=time.perf_counter();args=['--chunk',str(n)] if phase=='baseline' else ['--'+('follow' if phase=='remaining' else phase),str(n)]
        try:
            p=subprocess.run([sys.executable,'-S',str(Path(__file__).resolve()),*args],capture_output=True,text=True,encoding='utf-8',timeout=limit)
            status='completed' if p.returncode==0 else 'error';code=p.returncode;output=p.stdout+p.stderr
        except subprocess.TimeoutExpired as ex:
            dec=lambda v:v.decode('utf-8',errors='replace') if isinstance(v,bytes) else v or ''
            status='timeout';code=None;output=dec(ex.stdout)+dec(ex.stderr)
        (OUT/f'{phase}-{n:03d}.log').write_text(output,encoding='utf-8')
        r={'job':n,'status':status,'exit_code':code,'seconds':time.perf_counter()-start,'limit':limit}
        print(json.dumps(r),output,flush=True);return r
    results=[]
    with ThreadPoolExecutor(max_workers=2) as pool:
        for r in pool.map(worker,jobs):
            results.append(r);(OUT/f'{phase}-attempts.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    OUT.mkdir(parents=True,exist_ok=True);p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--phase',choices=['baseline','profile','follow','remaining']);p.add_argument('--limit',type=int,default=300)
    p.add_argument('--chunk',type=int);p.add_argument('--profile',type=int);p.add_argument('--follow',type=int);p.add_argument('--rank',action='store_true');p.add_argument('--pair',action='store_true');a=p.parse_args()
    if a.chunk is not None:
        model=t.Model()
        for item in selection(model)[a.chunk::2]:baseline(model,item)
    elif a.profile is not None:profile(a.profile)
    elif a.follow is not None:follow(a.follow)
    elif a.rank:rank_plan()
    elif a.pair:pair_binding()
    else:run(a.phase,a.limit)
