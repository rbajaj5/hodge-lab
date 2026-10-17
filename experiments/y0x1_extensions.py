"""Bounded block/shared/rebuild continuation on new Y0/X1 extensions."""
from concurrent.futures import ThreadPoolExecutor
from itertools import combinations
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,time
import x1y1_extensions as x
import degree7_triple_shared as shared
from check_quartic_exclusions import shared_system
q=x.q;e=x.e;t=x.t;cert=x.cert
OUT=e.ROOT/'results/y0x1-extensions'
ANCHOR={(0,1,0),(1,2,3)}


def selection(model):
    previous=set(model.families)|{tuple(tuple(c) for c in r['characters']) for r in x.selection(model)}
    assert len(previous)==284
    triples=sorted({tuple(sorted((*ANCHOR,c))) for c in model.groups if c not in ANCHOR}-previous)
    assert len(triples)==132
    wanted=set(triples);global_ids={c:i for i,c in enumerate(combinations(sorted(model.groups),3),1) if c in wanted}
    return [{'batch_number':i,'global_number':global_ids[c],'characters':[list(a) for a in c],
        'third_character':list(next(a for a in c if a not in ANCHOR)),
        'basis_indices':sorted(j for a in c for j in model.groups[a])} for i,c in enumerate(triples,1)]


def terminal(model,ids):
    if not ids:return 'excluded_directly'
    chars={model.dc[i] for i in ids}
    if chars<=ANCHOR:return 'pair22_dependency'
    if len(chars)==1:return 'single_character_dependency'
    return None


def blocks(model,item,ids=None,path=None):
    x.family(model,item,initial=ids,destination=path or OUT/f"family-{item['batch_number']:03d}.json.gz",finish=terminal)


def build(model,item,ids):
    chars={model.dc[i] for i in ids}
    if len(chars)==3:
        return shared.construct(model,{'number':item['global_number'],'remaining':ids,'characters':item['characters']},anchor=ANCHOR)
    system=shared_system(model,ids);eq=[cert.decode(p) for p in system['equations']]
    return {'family':item['global_number'],'characters':system['characters'],'basis_indices':ids,
        'Koszul_indices':system['ks'],'stabilizer_order':system['subgroup_order'],
        'equation_count':len(eq),'equations_sha256':hashlib.sha256(json.dumps(system,sort_keys=True).encode()).hexdigest(),
        'pivots':list(range(len(ids)))},eq


def follow(number):
    start=time.perf_counter();model=t.Model();item=selection(model)[number-1]
    source=OUT/f'family-{number:03d}.json.gz';initial=q.load(source);ids=initial['remaining'][:]
    assert initial['completed'] and not terminal(model,ids)
    path=OUT/f'follow-{number:03d}.json.gz'
    packet={'batch_number':number,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'cycles':[],'completed':False,'status':'running','remaining':ids};q.save(path,packet)
    for cycle in range(len(ids)+1):
        ending=terminal(model,ids)
        if ending:packet['status']=ending;break
        desc,eq=build(model,item,ids);n=len(ids)+len(desc['Koszul_indices'])
        stage={'system':desc,'charts':[],'completed':False};packet['cycles'].append(stage);q.save(path,packet)
        print('Shared',number,cycle,'D',len(ids),'K',len(desc['Koszul_indices']),len(eq),'rows',flush=True)
        for pivot in desc['pivots']:
            c=cert.prove_chart(eq,n,pivot);cert.verify_chart(eq,n,c);stage['charts'].append(c);q.save(path,packet)
            print('Chart',number,cycle,'raw',ids[pivot],c['excluded'],flush=True)
        removed=[ids[c['pivot']] for c in stage['charts'] if c['excluded']]
        stage['removed']=removed;stage['completed']=True;q.save(path,packet)
        if not removed:packet['status']='unresolved_shared_charts';break
        ids=[i for i in ids if i not in removed];stage['after_shared']=ids[:]
        rebuilt_path=OUT/f'rebuilt-{number:03d}-{cycle}.json.gz';blocks(model,item,ids,rebuilt_path)
        stage['rebuilt_file']=rebuilt_path.name;stage['rebuilt_sha256']=hashlib.sha256(rebuilt_path.read_bytes()).hexdigest()
        ids=q.load(rebuilt_path)['remaining'];packet['remaining']=ids;q.save(path,packet)
    else:raise AssertionError('Each follow-up cycle must decrease the active coordinate count')
    packet['completed']=True;packet['seconds']=time.perf_counter()-start;q.save(path,packet)
    print(number,packet['status'],ids,flush=True)


def run(phase,limit):
    model=t.Model();items=selection(model)
    jobs=[0,1] if phase=='blocks' else [r['batch_number'] for p in sorted(OUT.glob('family-*.json.gz')) if (r:=q.load(p))['completed'] and not terminal(model,r['remaining'])]
    plan={'sources':e.source_hashes(),'anchor':sorted(map(list,ANCHOR)),'previous_selection':284,
        'new_selection':items,'jobs':jobs,'phase':phase,'seconds_per_job':limit,'workers':2,'max_block_degree':4}
    (OUT/(phase+'-plan.json')).write_text(json.dumps(plan,indent=2)+'\n')
    def worker(j):
        start=time.perf_counter();args=['--chunk',str(j)] if phase=='blocks' else ['--follow',str(j)]
        try:
            p=subprocess.run([sys.executable,'-S',str(Path(__file__).resolve()),*args],capture_output=True,text=True,encoding='utf-8',timeout=limit)
            output=p.stdout+p.stderr;code=p.returncode;status='completed' if code==0 else 'error'
        except subprocess.TimeoutExpired as ex:
            dec=lambda v:v.decode('utf-8',errors='replace') if isinstance(v,bytes) else v or ''
            output=dec(ex.stdout)+dec(ex.stderr);code=None;status='timeout'
        (OUT/f'{phase}-{j:03d}.log').write_text(output,encoding='utf-8')
        r={'job':j,'status':status,'exit_code':code,'seconds':time.perf_counter()-start,'limit_seconds':limit}
        print(json.dumps(r),output,flush=True);return r
    records=[]
    with ThreadPoolExecutor(max_workers=2) as pool:
        for r in pool.map(worker,jobs):
            records.append(r);(OUT/(phase+'-attempts.json')).write_text(json.dumps(records,indent=2)+'\n')


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    OUT.mkdir(parents=True,exist_ok=True)
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--phase',choices=['blocks','follow'],default='blocks');p.add_argument('--limit',type=int,default=300)
    p.add_argument('--chunk',type=int,choices=[0,1]);p.add_argument('--follow',type=int);a=p.parse_args()
    if a.chunk is not None:
        model=t.Model()
        for item in selection(model)[a.chunk::2]:blocks(model,item)
    elif a.follow is not None:follow(a.follow)
    else:run(a.phase,a.limit)
