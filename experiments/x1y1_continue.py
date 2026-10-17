"""Rebuild after globally valid shared-numerator chart exclusions."""
import hashlib,json,time
import x1y1_extensions as x
import x1y1_shared as s


def run():
    model=x.t.Model();items={r['batch_number']:r for r in x.selection(model)};records=[]
    for number in s.survivors():
        start=time.perf_counter();path=x.OUT/f'shared-{number:03d}.json.gz';packet=x.q.load(path)
        assert packet['completed'];desc=packet['system']
        removed=[desc['basis_indices'][c['pivot']] for c in packet['charts'] if c['excluded']]
        ids=[i for i in desc['basis_indices'] if i not in removed]
        destination=x.OUT/f'continued-{number:03d}.json.gz'
        x.family(model,items[number],initial=ids,destination=destination)
        result=x.q.load(destination);result['shared_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
        result['shared_removed']=removed;x.q.save(destination,result)
        records.append({'batch_number':number,'removed_by_shared_charts':removed,
            'remaining':result['remaining'],'status':result['status'],'seconds':time.perf_counter()-start})
        (x.OUT/'continuation-attempts.json').write_text(json.dumps(records,indent=2)+'\n')


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    run()
