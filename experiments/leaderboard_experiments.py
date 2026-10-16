"""Read-only live leaderboard snapshot and bounded CUDA certificate-transfer screen.

Run from this workspace: python experiments/leaderboard_experiments.py
No submissions, external writes, or changes to the upstream checkout.
"""
from pathlib import Path
from fractions import Fraction
import collections, datetime, hashlib, json, subprocess, time, urllib.request
import numpy as np
import gpu_identity_screen as s

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = ROOT/'sources/sextics'
OUT = HERE.parent/'results/leaderboard-experiments'
OUT.mkdir(parents=True,exist_ok=True)

def fetch(path):
    raw = urllib.request.urlopen('https://hodge.computer/'+path, timeout=30).read()
    (OUT/path.replace('/', '__')).write_bytes(raw)
    return json.loads(raw)

def cpu_parts(case, point):
    A,F,D,Q = [s.cpu_eval(case[k],point) for k in ('A','F','D','Q')]
    nf=div=nd=0
    for i in range(6):
        n=s.cpu_eval(case['N'][i],point)
        nf += n*s.cpu_eval(s.derivative(case['F'],i),point)
        div += s.cpu_eval(s.derivative(case['N'][i],i),point)
        nd += n*s.cpu_eval(s.derivative(case['D'],i),point)
    b=A*D*D % s.P
    w=(-case['q']*D*nf+F*(D*div-nd)-pow(F,case['q']+1,s.P)*Q)%s.P
    return b,w

def main():
    checked=datetime.datetime.now(datetime.timezone.utc).isoformat()
    index=fetch('data/index.json')['records']
    credits=fetch('leaderboard/credits.json')
    accounts=fetch('leaderboard/accounts.json')
    current=subprocess.check_output(['gh','api','repos/hodge-computer/sextics/commits/main','--jq','.sha'],text=True).strip()
    local=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip()
    assert current==local, 'Refresh inputs before running against a changed upstream.'
    records={r['id']:r for r in index}
    credited=collections.defaultdict(set)
    for c in credits['credits']:
        r=records[c['instanceId']]
        assert r['status']=='solved' and r['formalStatus']=='proved' and r['certificateAvailable']
        credited[c['githubLogin']].add(c['instanceId'])
    open_ids=[r['id'] for r in index if r['status']=='open']
    candidates=[]; sources={}; skipped=[]; hashes={}
    targets={}
    for target_id in open_ids:
        try: targets[target_id]=s.load_target(REPO/'data'/target_id)
        except Exception as exc:
            raise ValueError(f'Cannot load {target_id}: {exc}') from exc
    for id in sorted(set().union(*credited.values())):
        folder=REPO/'data'/id
        path=folder/'witness.json'
        if not path.exists():
            skipped.append({'id':id,'reason':'No exported rational witness.'}); continue
        w=json.loads(path.read_text())
        if w['d']>6 or sum(map(len,[w['D'],w['Q']]+w['N']))>4000:
            skipped.append({'id':id,'reason':'Outside degree<=6 and expression-length<=4000 screen.'}); continue
        source=s.load_target(folder)
        witness={'D':s.parse_polynomial(w['D']),'N':[s.parse_polynomial(n) for n in w['N']],'Q':s.parse_polynomial(w['Q'])}
        source.update(witness)
        sources[id]=source
        candidates.append({**source,'source':id,'control':True})
        for target_id in open_ids:
            target=targets[target_id]
            if target['q']==source['q']:
                candidates.append({**target,**witness,'source':id,'control':False})
    for id in set(open_ids)|set(sources):
        for name in ['instance.rec','record.json','witness.json','acceptance.json']:
            path=REPO/'data'/id/name
            if path.exists(): hashes[path.relative_to(REPO).as_posix()]=s.source_sha256(path)
    offsets=[0]; coeff=[]; exps=[]
    for c in candidates:
        for p in s.case_polys(c):
            for e,v in sorted(p.items()): coeff.append(s.modcoeff(v)); exps.append(e)
            offsets.append(len(coeff))
    cp,handles=s.load_cupy()
    seed=202610161953; count=512
    points=np.random.default_rng(seed).integers(0,s.P,size=(count,6),dtype=np.int64)
    args=[cp.asarray(points),cp.asarray(offsets,dtype=cp.int32),cp.asarray(coeff,dtype=cp.int64),cp.asarray(exps,dtype=cp.uint8),cp.asarray([c['q'] for c in candidates],dtype=cp.int32)]
    residual=cp.empty((len(candidates),count),dtype=cp.int64); base=cp.empty_like(residual)
    cuda=s.CUDA.replace('long long* out){','long long* out,long long* basevalues){').replace('out[id]=(t1+PRIME-t2+t3+PRIME-t4)%PRIME;','basevalues[id]=t1; out[id]=(t1+PRIME-t2+t3+PRIME-t4)%PRIME;')
    assert 'basevalues[id]=t1' in cuda
    kernel=cp.RawKernel(cuda,'residuals')
    def launch():
        kernel(((residual.size+127)//128,),(128,),(np.int32(count),np.int32(len(candidates)),*args,residual,base))
    launch();cp.cuda.Device().synchronize()
    start=time.perf_counter();launch();cp.cuda.Device().synchronize();seconds=time.perf_counter()-start
    R=cp.asnumpy(residual); B=cp.asnumpy(base); W=(R-B)%s.P
    results=[]
    for i,c in enumerate(candidates):
        nz=np.flatnonzero(W[i])
        scale=(-int(B[i,nz[0]])*pow(int(W[i,nz[0]]),-1,s.P))%s.P if len(nz) else 0
        scaled=(B[i]+scale*W[i])%s.P
        bad=np.flatnonzero(scaled)
        check_indices=set([0,1,2,3])
        if len(bad):check_indices.add(int(bad[0]))
        if len(nz):check_indices.add(int(nz[0]))
        for j in check_indices:
            b,w=cpu_parts(c,points[j])
            assert b==int(B[i,j]) and w==int(W[i,j])
        if c['control']:
            assert not np.any(R[i]) and scale==1
        result={'source':c['source'],'target':c['id'],'accepted_control':c['control'],
                'direct_transfer_nonzero_count':int(np.count_nonzero(R[i])),
                'fitted_modular_scale':scale,'scaled_transfer_nonzero_count':int(len(bad)),
                'cpu_checks_matched':len(check_indices)}
        if len(bad):
            j=int(bad[0]);result['counterexample']={'point':points[j].tolist(),'base_term':int(B[i,j]),'witness_term':int(W[i,j]),'scaled_residual':int(scaled[j])}
            k=int(nz[0]) if len(nz) else None
            if k is not None:
                result['scale_fitting_point']={'point':points[k].tolist(),'base_term':int(B[i,k]),'witness_term':int(W[i,k])}
                result['nonzero_two_point_determinant_mod_p']=int((int(B[i,k])*int(W[i,j])-int(B[i,j])*int(W[i,k]))%s.P)
                assert result['nonzero_two_point_determinant_mod_p']
        results.append(result)
    trials=[r for r in results if not r['accepted_control']]
    report={'checked_utc':checked,'repository_commit':local,'leaderboard':{k:len(v) for k,v in credited.items()},
            'open_instances':len(open_ids),'solved_instances':sum(r['status']=='solved' for r in index),
            'gpu':cp.cuda.runtime.getDeviceProperties(0)['name'].decode(),
            'method':'For each eligible accepted rational witness, reuse D,N,Q on every open target with the same q. Also test whether multiplying all N_i and Q by a common scalar can repair the identity. No coordinate transformations, denominator changes, or numerator corrections searched.',
            'accepted_controls':len(sources),'transfer_trials':len(trials),'direct_transfer_passes':sum(r['direct_transfer_nonzero_count']==0 for r in trials),
            'scaled_transfer_passes':sum(r['scaled_transfer_nonzero_count']==0 for r in trials),
            'prime':s.P,'points_per_trial':count,'point_seed':seed,'gpu_warm_kernel_seconds':seconds,
            'timing_scope':'One synchronized warmed kernel; excludes parsing, transfers, compilation, CPU checking and report writing.',
            'interpretation':'A nonzero modular residual rejects the direct rational polynomial identity. A nonzero two-point determinant also rules out any complex constant rescaling of N,Q: proportional rational coefficient polynomials would have every such rational evaluation determinant zero. No conclusion about other witnesses, changes to Q, or unrestricted certificate existence. Passing controls are checks of existing accepted inputs, not new proofs.',
            'input_hash_encoding':'Source bytes with CRLF normalized to LF.',
            'skipped_witnesses':skipped,'input_sha256':hashes,'cases':results}
    (OUT/'report.json').write_text(json.dumps(report,indent=2))
    np.savez_compressed(OUT/'residues.npz',points=points,residuals=R,base_terms=B)
    print(json.dumps({k:v for k,v in report.items() if k not in ['cases','input_sha256','skipped_witnesses']},indent=2))

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O; verification assertions are required.')
    main()
