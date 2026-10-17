"""Bounded exact polynomial multipliers on rebuilt family 151.

Each exported relation is a sum of denominator-polynomial multiples of the
actual shared-numerator equations. Checkpoints are partial spans, not claims
that all relations of the stated degree have been found.
"""
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction as Q
from pathlib import Path
import argparse, hashlib, json, subprocess, sys, time
import remaining_triples_shared as s
import degree7_syzygies as syz
e=s.e; q=s.q; cert=s.cert
OUT=e.ROOT/'results/family151-multipliers'
SOURCE=s.OUT/'rebuilt-151.json.gz'
CASES=[None,115,234,271,285,288]


def build(model,raw):
    ids,change=s.rebase(model,151)
    desc,eq=s.construct(model,151,ids)
    source=q.load(SOURCE)
    assert desc==source['shared']['system'] and change==source['change']
    pivot=None if raw is None else ids.index(raw)
    assert pivot is None or pivot in desc['pivots']
    rows=eq if pivot is None else [cert.substitute(p,{pivot:{():Q(1)}}) for p in eq]
    return desc,rows,[i for i in range(len(ids)) if i!=pivot],pivot


def label(raw):return 'global' if raw is None else str(raw)


def relations(span):
    return [{'polynomial':cert.encode({m:c for (_,m),c in row.items()}),
             'products':[[j,list(mon),str(c)] for (j,mon),c in sorted(track.items())]}
            for pivot,(row,track) in sorted(span.basis.items()) if pivot[0]==1]


def produce(raw):
    start=time.perf_counter();desc,rows,variables,pivot=build(e.t.Model(),raw)
    nD=len(desc['ids']);span=e.t.base.Elimination()
    packet={'family':151,'raw_pivot':raw,'pivot':pivot,'system':desc,
        'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'variables':variables,'multiplier_degree_bound':1,'completed':False,
        'completed_multipliers':[],'checkpoints':[],'baseline':[],'relations':[]}
    path=OUT/f'{label(raw)}.json.gz'
    print('Built',label(raw),len(rows),'rows',len(variables),'D variables',flush=True)
    for mon in [()]+[(i,) for i in variables]:
        step=time.perf_counter()
        for j,row in enumerate(rows):
            value={(0 if any(i>=nD for i in m+mon) else 1,tuple(sorted(m+mon))):c for m,c in row.items()}
            span.insert(value,{(j,mon):Q(1)})
        packet['completed_multipliers'].append(list(mon))
        packet['relations']=relations(span)
        if not mon:packet['baseline']=packet['relations'][:]
        old,new,total=syz.select_new(packet['baseline'],packet['relations'],variables)
        packet['selected_new']=new
        packet['checkpoints'].append({'multiplier':list(mon),'equation_rank':len(span.basis),
            'relations':len(packet['relations']),'new_relations':len(new),
            'baseline_multiple_rank':old,'combined_relation_rank':total,
            'seconds':time.perf_counter()-step})
        packet['seconds']=time.perf_counter()-start
        q.save(path,packet)
        print(label(raw),'multiplier',mon,'rank',len(span.basis),'relations',len(packet['relations']),
              'new',len(new),'seconds',round(packet['seconds'],2),flush=True)
    packet['completed']=True;q.save(path,packet)


def run(limit=180):
    OUT.mkdir(parents=True,exist_ok=True)
    plan={'family':151,'cases':CASES,'seconds_per_case':limit,'workers':2,
          'multiplier_degree_bound':1,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          'checkpoint_scope':'Only fully processed multiplier blocks are exported; an interrupted block is omitted.'}
    (OUT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    def worker(raw):
        start=time.perf_counter();cmd=[sys.executable,'-S',str(Path(__file__).resolve()),'--case',label(raw)]
        try:
            p=subprocess.run(cmd,text=True,capture_output=True,timeout=limit)
            output=p.stdout+p.stderr;code=p.returncode;status='completed' if code==0 else 'error'
        except subprocess.TimeoutExpired as ex:
            def dec(v):return v.decode(errors='replace') if isinstance(v,bytes) else v or ''
            output=dec(ex.stdout)+dec(ex.stderr);code=None;status='timeout'
        (OUT/f'{label(raw)}.log').write_text(output,encoding='utf-8')
        result={'raw_pivot':raw,'status':status,'returncode':code,'limit_seconds':limit,'seconds':time.perf_counter()-start}
        print(json.dumps(result),output,flush=True);return result
    records=[]
    with ThreadPoolExecutor(max_workers=2) as pool:
        for result in pool.map(worker,CASES):
            records.append(result);(OUT/'attempts.json').write_text(json.dumps(records,indent=2)+'\n')


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    OUT.mkdir(parents=True,exist_ok=True)
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case');parser.add_argument('--limit',type=int,default=180)
    args=parser.parse_args()
    if args.case is not None:produce(None if args.case=='global' else int(args.case))
    else:run(args.limit)
