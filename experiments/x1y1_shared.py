"""Bounded full shared-numerator chart tests on the nine surviving extensions."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,time
import x1y1_extensions as x
import degree7_triple_shared as shared
q=x.q;cert=x.cert;e=x.e


def survivors():
    return [r['batch_number'] for p in sorted(x.OUT.glob('family-*.json.gz'))
            if (r:=q.load(p))['status']=='unresolved_bounded_search']


def build(model,number):
    path=x.OUT/f'family-{number:03d}.json.gz';source=q.load(path)
    assert source['status']=='unresolved_bounded_search'
    desc,eq=shared.construct(model,{'number':source['global_number'],
        'remaining':source['remaining'],'characters':source['characters']},anchor=x.ANCHOR)
    return desc,eq,hashlib.sha256(path.read_bytes()).hexdigest()


def produce(number):
    start=time.perf_counter();desc,eq,digest=build(x.t.Model(),number)
    packet={'batch_number':number,'source_sha256':digest,'system':desc,'charts':[],'completed':False}
    path=x.OUT/f'shared-{number:03d}.json.gz';q.save(path,packet)
    print('Built',number,'D',len(desc['basis_indices']),'K',len(desc['Koszul_indices']),'H',desc['stabilizer_order'],len(eq),'rows',flush=True)
    for pivot in desc['pivots']:
        proof=cert.prove_chart(eq,len(desc['basis_indices'])+len(desc['Koszul_indices']),pivot)
        cert.verify_chart(eq,len(desc['basis_indices'])+len(desc['Koszul_indices']),proof)
        packet['charts'].append(proof);packet['seconds']=time.perf_counter()-start;q.save(path,packet)
        print(number,'raw',desc['basis_indices'][pivot],'excluded',proof['excluded'],'remaining',proof['remaining_variables'],flush=True)
    packet['completed']=True;q.save(path,packet)


def run(limit):
    selected=survivors();plan={'families':selected,'seconds_per_family':limit,'workers':2,
        'method':'Affine and square-zero propagation on full shared-numerator charts; no polynomial multiplier continuation in this pass.'}
    (x.OUT/'shared-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    def worker(number):
        start=time.perf_counter()
        try:
            p=subprocess.run([sys.executable,'-S',str(Path(__file__).resolve()),'--family',str(number)],text=True,capture_output=True,timeout=limit)
            output=p.stdout+p.stderr;code=p.returncode;status='completed' if code==0 else 'error'
        except subprocess.TimeoutExpired as ex:
            def dec(v):return v.decode(errors='replace') if isinstance(v,bytes) else v or ''
            output=dec(ex.stdout)+dec(ex.stderr);code=None;status='timeout'
        (x.OUT/f'shared-{number:03d}.log').write_text(output,encoding='utf-8')
        record={'batch_number':number,'status':status,'exit_code':code,'limit_seconds':limit,'seconds':time.perf_counter()-start}
        print(json.dumps(record),output,flush=True);return record
    records=[]
    with ThreadPoolExecutor(max_workers=2) as pool:
        for r in pool.map(worker,selected):
            records.append(r);(x.OUT/'shared-attempts.json').write_text(json.dumps(records,indent=2)+'\n')


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--family',type=int);p.add_argument('--limit',type=int,default=60)
    a=p.parse_args();produce(a.family) if a.family else run(a.limit)
