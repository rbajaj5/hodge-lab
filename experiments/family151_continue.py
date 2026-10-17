"""Bounded denominator power search using the new shared-map relations."""
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction as Q
from itertools import combinations_with_replacement
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,time
import family151_multipliers as f
e=f.e;q=f.q;cert=f.cert;syz=f.syz


def produce(raw,max_degree=4):
    start=time.perf_counter();path=f.OUT/f'{raw}.json.gz';packet=q.load(path)
    desc,rows,variables,pivot=f.build(e.t.Model(),raw);nD=len(desc['ids'])
    needed=packet['baseline']+[packet['relations'][j] for j in packet['selected_new']]
    necessary=[cert.decode(r['polynomial']) for r in needed]
    proof=cert.prove_chart(necessary,nD,pivot);cert.verify_chart(necessary,nD,proof)
    result={'raw_pivot':raw,'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'max_degree':max_degree,'denominator_chart':proof,'attempts':[],'claims':[],
        'completed':False,'excluded':proof['excluded']}
    out=f.OUT/f'follow-{raw}.json.gz';q.save(out,result)
    maps=syz.chart_maps(nD,pivot,proof)
    if not proof['excluded']:
        current=[cert.substitute(p,maps) for p in necessary]
        active=sorted({i for p in current for m in p for i in m})
        for degree in range(3,max_degree+1):
            step=time.perf_counter();expanded=[];labels=[]
            for j,p in enumerate(current):
                if not p:continue
                for size in range(degree-max(map(len,p))+1):
                    for mon in combinations_with_replacement(active,size):
                        expanded.append(cert.product(p,{mon:Q(1)}));labels.append((j,mon))
            witness,_,rank=cert.reduce_span(expanded);claims=[]
            targets=[('constant',None,0,{():Q(1)})]
            targets += [('power',i,d,{(i,)*d:Q(1)}) for i in active for d in range(1,degree+1)]
            found=set()
            for kind,i,power,target in targets:
                if i in found:continue
                w=witness(target)
                if w:
                    claims.append({'kind':kind,'coordinate':i,'power':power,'polynomial':cert.encode(target),
                        'products':[[labels[j][0],list(labels[j][1]),c] for j,c in w['equation_weights']]})
                    found.add(i)
                    if kind=='constant':break
            result['attempts'].append({'degree':degree,'variables':len(active),'rows':len(expanded),'rank':rank,
                'claims':len(claims),'seconds':time.perf_counter()-step})
            result['claims']=claims;result['claim_degree']=degree
            result['seconds']=time.perf_counter()-start;q.save(out,result)
            print(raw,'degree',degree,'rows',len(expanded),'rank',rank,'claims',[(v['kind'],v['coordinate'],v['power']) for v in claims],flush=True)
            if claims:break
        if result['claims'] and result['claims'][0]['kind']=='constant':result['excluded']=True
        else:
            changes={r['coordinate']:{} for r in result['claims']}
            maps={i:cert.substitute(p,changes) for i,p in maps.items()}
            physical=cert.prove_chart([cert.substitute(p,maps) for p in rows],nD+len(desc['Koszul_indices']),pivot)
            result['physical_closure']=physical;result['excluded']=physical['excluded']
    result['completed']=True;result['seconds']=time.perf_counter()-start;q.save(out,result)


def run(limit):
    def worker(raw):
        # Discovery writes its receipt only after the source packet is final.
        # Waiting is outside the declared algebra-search time limit.
        wait_start=time.perf_counter()
        while True:
            try:
                records=json.loads((f.OUT/'attempts.json').read_text())
                if any(r['raw_pivot']==raw for r in records):break
            except (FileNotFoundError,json.JSONDecodeError):pass
            if time.perf_counter()-wait_start>900:raise RuntimeError('Source discovery did not finish')
            time.sleep(1)
        start=time.perf_counter();cmd=[sys.executable,'-S',str(Path(__file__).resolve()),'--case',str(raw)]
        try:
            r=subprocess.run(cmd,text=True,capture_output=True,timeout=limit)
            output=r.stdout+r.stderr;code=r.returncode;status='completed' if code==0 else 'error'
        except subprocess.TimeoutExpired as ex:
            def dec(v):return v.decode(errors='replace') if isinstance(v,bytes) else v or ''
            output=dec(ex.stdout)+dec(ex.stderr);code=None;status='timeout'
        (f.OUT/f'follow-{raw}.log').write_text(output,encoding='utf-8')
        result={'raw_pivot':raw,'limit_seconds':limit,'status':status,'returncode':code,'seconds':time.perf_counter()-start}
        print(json.dumps(result),output,flush=True);return result
    plan={'cases':f.CASES[1:],'workers':2,'seconds_per_case':limit,'max_degree':4,
        'scope':'One coordinate-power stage through degree four, then affine/square propagation in the full shared equations.'}
    (f.OUT/'follow-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    records=[]
    with ThreadPoolExecutor(max_workers=2) as pool:
        for r in pool.map(worker,f.CASES[1:]):
            records.append(r);(f.OUT/'follow-attempts.json').write_text(json.dumps(records,indent=2)+'\n')


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--case',type=int);p.add_argument('--limit',type=int,default=120)
    a=p.parse_args();produce(a.case) if a.case else run(a.limit)
