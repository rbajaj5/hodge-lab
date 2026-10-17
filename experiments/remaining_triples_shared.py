"""Bounded shared-numerator continuation for selected families 17 and 151.

Normalize every surviving coefficient outside X1/Y1. The complete stabilizer
coset of numerator corrections and the quotient modulo F are retained.
"""
from fractions import Fraction as Q
from itertools import product, combinations_with_replacement
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import argparse, copy, hashlib, json, subprocess, sys, time
import eleven_quartic as x
e=x.e;q=x.q;cert=e.t.cert
OUT=e.ROOT/'results/remaining-triples-shared'
NUMBERS=[17,151]
RESIDUAL={(0,1,0),(5,3,0)}


def construct(model,number,ids=None):
    source=x.source()[number];ids=source['remaining'] if ids is None else ids
    chars=sorted({model.dc[i] for i in ids});assert len(chars)==3 and RESIDUAL<=set(chars)
    w=chars[0];group=list(product(range(6),repeat=3))
    H=[g for g in group if all(sum(a*b for a,b in zip(e.t.minus(c,w),g))%6==0 for c in chars)]
    ann=[c for c in group if all(sum(a*b for a,b in zip(c,g))%6==0 for g in H)]
    generated={e.t.plus(tuple(k*a%6 for a in e.t.minus(chars[1],w)),
                        tuple(l*a%6 for a in e.t.minus(chars[2],w))) for k in range(6) for l in range(6)}
    assert set(ann)==generated and len(H)*len(ann)==216
    wanted={e.t.plus(e.t.plus(model.alpha,w),a) for a in ann}
    field_chars=(model.field_chars if hasattr(model,'field_chars') else
                 [next(iter(e.t.e1.field_characters(K))) for K in model.fields])
    ks=[k for k,c in enumerate(field_chars) if c in wanted];lookup={k:j for j,k in enumerate(ks)}
    physical={};nD=len(ids)
    def add(p,parameter):
        for m,c in p.items():
            row=physical.setdefault(m,{})
            assert parameter not in row
            row[parameter]=c
    for i,j in combinations_with_replacement(range(nD),2):add(model.quadratic(ids[i],ids[j]),(i,j))
    for i,raw in enumerate(ids):
        for target in sorted({e.t.plus(model.dc[raw],c) for c in wanted}):
            for k,p in model.corrections(raw,target):
                assert k in lookup
                add(p,(i,nD+lookup[k]))
    mons=sorted(physical);eq=[physical[m] for m in mons]
    encoded={'physical_monomials':[list(m) for m in mons],'equations':[cert.encode(p) for p in eq]}
    desc={'number':number,'ids':ids,'characters':[list(c) for c in chars],
          'Koszul_indices':ks,'stabilizer_order':len(H),'annihilator':[list(a) for a in ann],
          'pivots':[i for i,raw in enumerate(ids) if model.dc[raw] not in RESIDUAL],
          'equation_count':len(eq),'equations_sha256':hashlib.sha256(json.dumps(encoded,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
    return desc,eq


def charts(number):
    started=time.perf_counter();desc,eq=construct(e.t.Model(),number)
    n=len(desc['ids'])+len(desc['Koszul_indices'])
    packet={'source_sha256':q.source_sha(),'system':desc,'charts':[],'completed':False}
    path=OUT/f'family-{number}.json.gz';q.save(path,packet)
    print('Built',number,'D',len(desc['ids']),'K',len(desc['Koszul_indices']),
          'H',desc['stabilizer_order'],'equations',len(eq),'pivots',desc['pivots'],flush=True)
    for pivot in desc['pivots']:
        start=time.perf_counter();proof=cert.prove_chart(eq,n,pivot)
        cert.verify_chart(eq,n,proof)
        packet['charts'].append(proof);packet['seconds']=time.perf_counter()-started;q.save(path,packet)
        print('Chart',number,pivot,'raw',desc['ids'][pivot],'excluded',proof['excluded'],
              'remaining',proof['remaining_variables'],'seconds',time.perf_counter()-start,flush=True)
    packet['completed']=True;q.save(path,packet)


def blocks(number):
    model=e.t.Model();stage=x.source()[number]['stages'][-1]
    ids=[i for i in stage['active'] if model.dc[i] not in RESIDUAL]
    equations=[cert.decode(r['polynomial']) for r in stage['necessary']]
    selected=[j for j,p in enumerate(equations) if all(i in ids for m in p for i in m)]
    eq=[equations[j] for j in selected];strands=[]
    for degree in [5,6]:
        start=time.perf_counter();record=e.strand(eq,ids,degree);strands.append(record)
        q.save(OUT/f'block-{number}.json.gz',{'source_sha256':q.source_sha(),'number':number,
            'ids':ids,'equation_indices':selected,'strands':strands})
        print('Block',number,'degree',degree,'rank',record['rank'],'/',record['codomain'],
              'zeros',[p['coordinate'] for p in record['vanishings']],
              'seconds',time.perf_counter()-start,flush=True)


def rebase(model,number):
    """Exact changes of denominator/lift basis after proved linear vanishings."""
    ids=x.source()[number]['remaining'][:]
    if number==17:
        ids.remove(56);return ids,{'eliminated':56,'replacement':[]}
    replacement={115:Q(1,2),234:Q(1,6),285:Q(1,6),288:Q(1,6)}
    D,N=model.pairs[133]
    def add(P,R,a):
        out=dict(P)
        for m,c in R.items():out[m]=out.get(m,Q(0))+a*c
        return {m:c for m,c in out.items() if c}
    for i,a in replacement.items():
        E,P=model.pairs[i]
        model.pairs[i]=(add(E,D,a),[add(U,V,a) for U,V in zip(P,N)])
    ids.remove(133)
    return ids,{'eliminated':133,'replacement':[[i,str(a)] for i,a in replacement.items()]}


def rebuild(number):
    start=time.perf_counter();model=e.t.Model();ids,change=rebase(model,number)
    necessary,ranks=model.necessities(ids)
    eq=[cert.decode(p['polynomial']) for p in necessary]
    small_ids=[i for i in ids if model.dc[i] not in RESIDUAL]
    indices=[j for j,p in enumerate(eq) if all(i in small_ids for m in p for i in m)]
    small=[eq[j] for j in indices];strands=[]
    for degree in [2,3,4,5,6]:
        record=e.strand(small,small_ids,degree);strands.append(record)
        print('Rebuilt block',number,degree,record['rank'],'/',record['codomain'],
              'zeros',[p['coordinate'] for p in record['vanishings']],flush=True)
    packet={'number':number,'source_sha256':q.source_sha(),'change':change,'active':ids,
            'necessary':necessary,'correction_ranks':ranks,
            'block':{'active':small_ids,'equation_indices':indices,'strands':strands},
            'seconds':time.perf_counter()-start}
    if number==151:
        packet['linear_square']={'linear':cert.encode({(115,):Q(3),(133,):Q(-6),(234,):Q(1),(285,):Q(1),(288,):Q(1)}),
            'products':[[13,[],'-54'],[12,[],'108'],[11,[],'-18']]}
        desc,physical=construct(model,number,ids)
        n=len(ids)+len(desc['Koszul_indices']);charts=[]
        for pivot in desc['pivots']:
            proof=cert.prove_chart(physical,n,pivot);cert.verify_chart(physical,n,proof);charts.append(proof)
            print('Rebuilt chart',number,desc['ids'][pivot],proof['excluded'],proof['remaining_variables'],flush=True)
        packet['shared']={'system':desc,'charts':charts,'completed':True}
    q.save(OUT/f'rebuilt-{number}.json.gz',packet)


def run():
    OUT.mkdir(parents=True,exist_ok=True)
    jobs=[(kind,number,300 if kind=='charts' else 60) for kind in ['charts','blocks'] for number in NUMBERS]
    plan={'jobs':[{'kind':kind,'number':number,'limit_seconds':limit} for kind,number,limit in jobs],
          'workers':2,'source_sha256':q.source_sha(),
          'chart_search':'exact affine and square-zero propagation; no polynomial multiplier follow-up in this first pass',
          'block_search':'pure complementary-character block, degrees five and six; all other characters unrestricted'}
    (OUT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    def worker(job):
        kind,number,limit=job;start=time.perf_counter()
        command=[sys.executable,'-S',str(Path(__file__).resolve()),'--'+kind,str(number)]
        try:
            r=subprocess.run(command,text=True,capture_output=True,timeout=limit)
            stdout=r.stdout;stderr=r.stderr;code=r.returncode;status='completed' if code==0 else 'error'
        except subprocess.TimeoutExpired as ex:
            def decode(s):return s.decode(errors='replace') if isinstance(s,bytes) else s or ''
            stdout=decode(ex.stdout);stderr=decode(ex.stderr);code=None;status='timeout'
        (OUT/f'{kind}-{number}.log').write_text(stdout+stderr,encoding='utf-8')
        result={'kind':kind,'number':number,'limit_seconds':limit,'status':status,'returncode':code,
                'seconds':time.perf_counter()-start}
        print(json.dumps(result),stdout,flush=True);return result
    records=[]
    with ThreadPoolExecutor(max_workers=2) as pool:
        for result in pool.map(worker,jobs):
            records.append(result);(OUT/'attempts.json').write_text(json.dumps(records,indent=2)+'\n')


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    OUT.mkdir(parents=True,exist_ok=True)
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--charts',type=int,choices=NUMBERS);p.add_argument('--blocks',type=int,choices=NUMBERS)
    p.add_argument('--rebuild',type=int,choices=NUMBERS)
    a=p.parse_args()
    if a.charts:charts(a.charts)
    elif a.blocks:blocks(a.blocks)
    elif a.rebuild:rebuild(a.rebuild)
    else:run()
