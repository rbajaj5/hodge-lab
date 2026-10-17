"""Bounded follow-up that prevents drift into one/two-character boundaries.

Families 1, 4, 149; two seeded balanced starts each; SLSQP with each character
carrying at least 10% of denominator coefficient energy. All 840 corrections.
The score is unchanged from the preceding variable-projection experiment.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse,gzip,json,hashlib,time,os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
import optimize_koszul_parameters as op

ROOT=op.ROOT;OUT=ROOT/'results/koszul-interior-search'
FAMILIES=[1,4,149];SEED=202610170201
CONFIG={'families':FAMILIES,'starts':2,'floor':.1,'box':4,'max_evaluations':120,
        'max_iterations':80,'seconds_per_start':120,'round_denominator':1024}

def shares(coords,pairs):
    D,N=op.build(coords,pairs);D=op.t.modF(D);energy={}
    for m,c in D.items():
        char=op.t.e1.character(m);energy[char]=energy.get(char,Q(0))+c*c
    total=sum(energy.values())
    return [[list(c),str(v/total)] for c,v in sorted(energy.items())]

def save(report,cases):
    OUT.mkdir(exist_ok=True)
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    with gzip.open(OUT/'certificates.json.gz','wt',encoding='utf-8') as f:json.dump({'cases':cases},f,separators=(',',':'))

def run():
    import numpy as np
    from scipy.optimize import minimize
    model=op.t.Model();numeric=op.NumericModel(model);source=op.read_packet()
    report={'configuration':CONFIG,'seed':SEED,'complete':False,'runs':[],
        'basis_sha256':hashlib.sha256(op.t.e1.BASIS.read_bytes()).hexdigest(),
        'source_sha256':hashlib.sha256((op.t.OUT/'certificates.json.gz').read_bytes()).hexdigest(),
        'scope':'Six bounded real searches; two balanced starts in each of three selected families. No global optimum or family exclusion. Character energy constraint is a search restriction, not part of HasCertificate.'}
    cases=[]
    for no in FAMILIES:
        family=next(f for f in op.selection(source) if f['number']==no)
        print('BUILD',no,flush=True);o=numeric.prepare(family)
        chars=[model.dc[i] for i in o.ids];groups=sorted(set(chars))
        masks=[np.array([c==g for c in chars]) for g in groups]
        Gc=[o.G*mask[:,None]*mask[None,:] for mask in masks]
        C=[g-CONFIG['floor']*o.G for g in Gc];rng=np.random.default_rng(SEED+no)
        def constraints(x):
            a=np.r_[1.,x];return np.array([a@g@a for g in C])
        def cjac(x):
            a=np.r_[1.,x];return np.array([2*g@a for g in C])[:,1:]
        for restart in range(CONFIG['starts']):
            for _ in range(10000):
                a=rng.uniform(-1,1,len(chars));a[0]=1
                for mask,g in zip(masks,Gc):a[mask]/=np.sqrt(a@g@a)
                a/=a[0]
                if abs(a).max()<=4:break
            else:raise AssertionError('No feasible balanced start')
            initial=a[1:].copy();assert min(constraints(initial))>0
            records=[];start=time.perf_counter();result=None;status=''
            def fun(x):
                if len(records)>=CONFIG['max_evaluations']:raise op.BudgetStop('evaluation cap')
                if time.perf_counter()-start>CONFIG['seconds_per_start']:raise op.BudgetStop('wall-clock cap')
                f,g,r=o.fit(x);a=np.r_[1.,x];den=a@o.G@a
                r['character_shares']=[float(a@c@a/den) for c in Gc]
                r['feasible']=bool(min(r['character_shares'])>=CONFIG['floor']-1e-9 and abs(a).max()<=4+1e-9)
                records.append(r)
                if not r['valid']:raise op.FitStop('inner least squares tolerance')
                return f,g
            try:
                result=minimize(fun,initial,method='SLSQP',jac=True,bounds=[(-4,4)]*len(initial),
                    constraints=[{'type':'ineq','fun':constraints,'jac':cjac}],
                    options={'maxiter':80,'ftol':1e-11})
                status=str(result.message)
            except (op.BudgetStop,op.FitStop) as e:status=str(e)
            best=min((r for r in records if r['valid'] and r['feasible']),key=lambda r:r['score'])
            coords=o.rationalize(best['x']);case=op.exact_case(coords,family,model)
            case.update(family=no,restart=restart);cases.append(case)
            rounded=[float(Q(c)*h) for (i,c),h in zip(coords,o.heights)][1:]
            _,_,recheck=o.fit(rounded,tight=True);assert recheck['valid']
            exactshares=shares(coords,model.pairs);assert len(exactshares)==3
            row={'family':no,'restart':restart,'basis_indices':o.ids,'heights':[str(h) for h in o.heights],
                'initial_x':initial.tolist(),'initial_score':records[0]['score'],'evaluations':records,
                'status':status,'optimizer_success':bool(result.success) if result is not None else False,
                'best':best,'coordinates':coords,'exact_character_shares':exactshares,
                'rounded_recheck':recheck,'seconds':time.perf_counter()-start}
            report['runs'].append(row);save(report,cases)
            print('DONE',no,restart,'score',best['score'],'shares',[round(float(Q(v)),5) for c,v in exactshares],case['status'],status,flush=True)
    report['complete']=True;save(report,cases)
    validation=check()
    (OUT/'validation.json').write_text(json.dumps(validation,indent=2)+'\n',encoding='utf-8',newline='\n')

def check():
    report=json.loads((OUT/'report.json').read_text())
    with gzip.open(OUT/'certificates.json.gz','rt') as f:packet=json.load(f)
    assert report['configuration']==CONFIG and report['seed']==SEED and report['complete']
    assert report['basis_sha256']==hashlib.sha256(op.t.e1.BASIS.read_bytes()).hexdigest()
    assert report['source_sha256']==hashlib.sha256((op.t.OUT/'certificates.json.gz').read_bytes()).hexdigest()
    _,pairs=op.t.e1.load();fields,labels=op.t.e1.koszul_fields()
    from degree7_verify_polynomials import poly,remainder,B
    target=poly.load_target(ROOT/'sources/sextics/data/holdout');F=target['F'];A=target['A']
    assert F==op.t.base.F and A==op.t.base.A and target['q']==1
    DF=[poly.derivative(F,i) for i in range(6)];indfields=[]
    for i,j,m in labels:
        K=[{} for _ in range(6)];K[i]=poly.mul({tuple(m):Q(1)},DF[j]);K[j]=poly.scale(poly.mul({tuple(m):Q(1)},DF[i]),-1);indfields.append(K)
    assert [(r['family'],r['restart']) for r in report['runs']]==[(f,r) for f in FAMILIES for r in range(2)]
    assert len(packet['cases'])==6
    assert len({json.dumps(c['coordinates']) for c in packet['cases']})==6
    for row,case in zip(report['runs'],packet['cases']):
        assert (row['family'],row['restart'])==(case['family'],case['restart'])
        assert len(row['evaluations'])<=CONFIG['max_evaluations']
        best=min((r for r in row['evaluations'] if r['valid'] and r['feasible']),key=lambda r:r['score'])
        assert best==row['best'] and row['initial_score']==row['evaluations'][0]['score']
        expected=[[i,str(Q(float(v)).limit_denominator(1024)/Q(h))] for i,v,h in zip(row['basis_indices'],[1,*best['x']],row['heights'])]
        assert expected==row['coordinates']==case['coordinates']
        assert shares(case['coordinates'],pairs)==row['exact_character_shares']
        assert len(row['exact_character_shares'])==3
        op.verify(case,pairs,fields)
        assert case['status']=='rejected','A solvable candidate requires full admissibility checks.'
        D={};N=[{} for _ in range(6)]
        for i,c in case['coordinates']:
            D=poly.add(D,poly.scale(pairs[i][0],Q(c)))
            N=[poly.add(n,poly.scale(p,Q(c))) for n,p in zip(N,pairs[i][1])]
        directional={}
        for n,df in zip(N,DF):directional=poly.add(directional,poly.mul(n,df))
        assert directional==poly.mul(A,D) and remainder(D,F)
        dual={tuple(m):Q(c) for m,c in case['dual_functional']}
        dot=lambda p:sum(c*dual.get(m,0) for m,c in p.items())
        assert dot(remainder(B(D,N),F))==1
        assert all(dot(remainder(B(D,K),F))==0 for K in indfields)
    validation={'status':'PASS','exact_rejections':6,'independent_column_checks':5040,
        'total_evaluations':sum(len(r['evaluations']) for r in report['runs']),
        'sha256':{name:hashlib.sha256((OUT/name).read_bytes()).hexdigest() for name in ['report.json','certificates.json.gz']}}
    print(json.dumps(validation));return validation

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O')
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true')
    if p.parse_args().check:
        actual=check();assert actual==json.loads((OUT/'validation.json').read_text())
    else:run()
