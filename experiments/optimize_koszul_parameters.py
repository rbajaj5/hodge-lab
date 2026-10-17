"""Bounded variable projection on holdout's remaining selected triples.

Optimize real denominator parameters with fixed coefficient weights. Eliminate
the complete 840-dimensional numerator correction at each evaluation. Exact
rational checks apply only to rounded fixed directions, never an entire family.
--check uses the standard library; --independent uses a separate polynomial API.
"""
from pathlib import Path
from fractions import Fraction as Q
from functools import lru_cache
from itertools import combinations_with_replacement
import argparse, copy, gzip, hashlib, json, sys, time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'algebra'))
import degree7_triples as t
from fixed_denominator_search import solve

OUT=ROOT/'results/koszul-parameter-optimization'
SEED=202610162240
ANCHOR={(0,0,1),(1,2,3)}
CONFIG={'starts':2,'max_evaluations_per_start':80,'max_iterations':60,
        'optimizer_seconds_per_family':120,'box':4.,'round_denominator':1024,
        'lsmr_atol':1e-12,'lsmr_btol':1e-12,'lsmr_maxiter':4000}


def read_packet():
    with gzip.open(t.OUT/'certificates.json.gz','rt',encoding='utf-8') as f:return json.load(f)


def selection(packet):
    return [f for f in packet['families'] if f['status']=='unresolved_three_characters'
            and not ANCHOR <= set(map(tuple,f['characters']))]


def build(coords,pairs):
    D={};N=[{} for _ in range(6)]
    for i,c in coords:
        D=t.base.padd(D,pairs[i][0],Q(c))
        for j in range(6):N[j]=t.base.padd(N[j],pairs[i][1][j],Q(c))
    assert D and t.e1.directional(N)==t.base.pmul(t.base.A,D)
    assert t.modF(D)
    return D,N


def verify(case,pairs,fields):
    D,N=build(case['coordinates'],pairs)
    b=t.modF(t.B(D,N))
    columns=[t.modF(t.B(D,K)) for K in fields]
    if case['status']=='rejected':
        dual={tuple(m):Q(c) for m,c in case['dual_functional']}
        assert t.dot(dual,b)==1
        assert all(t.dot(dual,col)==0 for col in columns)
    else:
        assert case['status']=='solvable'
        for i,c in case['corrections']:b=t.base.padd(b,columns[i],Q(c))
        assert not b


def exact_case(coords,family,model):
    D,N=build(coords,model.pairs);b=t.modF(t.B(D,N))
    # Reuse a physical dual only when it is nonzero on this exact direction.
    # The final checker still checks it against every one of the 840 columns.
    for necessary in family['stages'][-1]['necessary']:
        dual=t.e1.decode(necessary['dual']);value=t.dot(dual,b)
        if value:
            result={'status':'rejected','discovery':'inherited necessary-condition functional',
                    'dual_functional':[[list(m),str(c/value)] for m,c in sorted(dual.items())]}
            break
    else:
        columns=[t.modF(t.B(D,K)) for K in model.fields]
        result=solve(b,columns);result['discovery']='full fixed-direction rational elimination'
    result['coordinates']=coords
    verify(result,model.pairs,model.fields)
    return result


class NumericModel:
    def __init__(self,model):
        import numpy as np
        from scipy import sparse
        self.np=np;self.sparse=sparse;self.model=model

    @lru_cache(None)
    def corrections(self,i):
        return [t.modF(t.B(self.model.pairs[i][0],K)) for K in self.model.fields]

    def prepare(self,family):
        np=self.np;sparse=self.sparse;model=self.model;ids=family['remaining'];n=len(ids)
        pairs=list(combinations_with_replacement(range(n),2))
        qq=[model.quadratic(ids[i],ids[j]) for i,j in pairs]
        mm=[self.corrections(i) for i in ids]
        mons=sorted(set().union(*(set(p) for p in qq),*(set(p) for row in mm for p in row)))
        lookup={m:j for j,m in enumerate(mons)}
        heights=[sum(abs(c) for c in model.pairs[i][0].values()) for i in ids]
        def matrix(polys,factors):
            entries=[(lookup[m],j,float(c*factors[j])) for j,p in enumerate(polys) for m,c in p.items()]
            rr,cc,vv=zip(*entries)
            return sparse.coo_matrix((vv,(rr,cc)),shape=(len(mons),len(polys))).tocsr()
        QM=matrix(qq,[1/(heights[i]*heights[j]) for i,j in pairs])
        matrices=[matrix(row,[1/h]*840) for row,h in zip(mm,heights)]
        denominators=[t.modF(model.pairs[i][0]) for i in ids]
        G=np.array([[float(sum(c*denominators[j].get(m,0) for m,c in D.items())/(heights[i]*heights[j]))
                     for j in range(n)] for i,D in enumerate(denominators)])
        assert np.linalg.eigvalsh(G).min()>0
        return Objective(np,QM,matrices,G,pairs,ids,heights,len(mons))


class Objective:
    def __init__(self,np,QM,matrices,G,pairs,ids,heights,nrows):
        self.np=np;self.QM=QM;self.Ms=matrices;self.G=G;self.pairs=pairs
        self.ids=ids;self.heights=heights;self.nrows=nrows

    def fit(self,x,tight=False):
        from scipy.sparse.linalg import lsmr
        np=self.np;x=np.asarray(x);a=np.r_[1.,x];n=len(a)
        b=self.QM@np.array([a[i]*a[j] for i,j in self.pairs])
        M=sum(v*A for v,A in zip(a,self.Ms)).tocsr();M.eliminate_zeros()
        scales=np.sqrt(np.asarray(M.power(2).sum(axis=0)).ravel());active=scales>0
        T=M[:,active].multiply(1/scales[active]).tocsr()
        tol=1e-14 if tight else CONFIG['lsmr_atol']
        fit=lsmr(T,-b,atol=tol,btol=tol,conlim=1e15,maxiter=12000 if tight else CONFIG['lsmr_maxiter'])
        z=np.zeros(840);z[active]=fit[0]/scales[active]
        r=b+M@z;normal=float(np.linalg.norm(T.T@r)/max(np.linalg.norm(b),1e-30))
        valid=fit[1] in (0,1,2,4,5) and normal<1e-9
        dscale=float(a@self.G@a);energy=float(r@r);score=energy/dscale**2
        jac=np.zeros((len(self.pairs),n))
        for k,(i,j) in enumerate(self.pairs):jac[k,i]+=a[j];jac[k,j]+=a[i]
        jb=self.QM@jac
        grad=2*np.array([r@(jb[:,i]+self.Ms[i]@z) for i in range(n)])/dscale**2
        grad-=4*energy*(self.G@a)/dscale**3
        record={'x':x.tolist(),'score':score,'valid':valid,'normal_residual':normal,
                'lsmr_iterations':int(fit[2]),'lsmr_stop':int(fit[1]),
                'correction_coordinate_norm':float(np.linalg.norm(z)),
                'denominator_norm_squared':dscale}
        return score,grad[1:],record

    def rationalize(self,x):
        return [[i,str(Q(float(v)).limit_denominator(CONFIG['round_denominator'])/h)]
                for i,v,h in zip(self.ids,[1.,*x],self.heights)]


class BudgetStop(Exception):pass
class FitStop(Exception):pass


def optimize_family(family,numeric):
    import numpy as np
    from scipy.optimize import minimize
    start=time.perf_counter();o=numeric.prepare(family);rng=np.random.default_rng(SEED+family['number'])
    n=len(o.ids)-1;records=[];runs=[];gradient_checks=[]
    # Check the envelope derivative against finite differences away from chart boundaries.
    pilot=rng.uniform(-1.5,1.5,n);f,g,rec=o.fit(pilot)
    assert rec['valid']
    for k in sorted(set([0,n//2,n-1])):
        h=1e-5;dx=np.zeros(n);dx[k]=h
        plus,_,pr=o.fit(pilot+dx);minus,_,mr=o.fit(pilot-dx)
        fd=(plus-minus)/(2*h);error=abs(fd-g[k])/max(1.,abs(fd),abs(g[k]))
        assert pr['valid'] and mr['valid'] and error<2e-5
        gradient_checks.append({'coordinate':k,'analytic':float(g[k]),'finite_difference':fd,'scaled_error':error})
    opt_start=time.perf_counter()
    for restart in range(CONFIG['starts']):
        initial=rng.uniform(-1.5,1.5,n);begin=len(records);status='';result=None
        def fun(x):
            if len(records)-begin>=CONFIG['max_evaluations_per_start']:raise BudgetStop('evaluation cap')
            if time.perf_counter()-opt_start>CONFIG['optimizer_seconds_per_family']:raise BudgetStop('wall-clock cap')
            f,g,r=o.fit(x);r['restart']=restart;records.append(r)
            if not r['valid']:raise FitStop('inner least squares did not meet the recorded tolerance')
            return f,g
        try:
            result=minimize(fun,initial,method='L-BFGS-B',jac=True,bounds=[(-CONFIG['box'],CONFIG['box'])]*n,
                options={'maxiter':CONFIG['max_iterations'],'maxfun':CONFIG['max_evaluations_per_start'],
                         'ftol':1e-13,'gtol':1e-9,'maxls':15})
            status=str(result.message)
        except (BudgetStop,FitStop) as e:status=str(e)
        runs.append({'restart':restart,'initial_x':initial.tolist(),'evaluations':len(records)-begin,
                     'success':bool(result.success) if result is not None else False,'message':status})
    assert records and any(r['valid'] for r in records)
    # Equal number of objective evaluations; no optimization of metric weights.
    random_records=[]
    for _ in records:
        _,_,r=o.fit(rng.uniform(-CONFIG['box'],CONFIG['box'],n));random_records.append(r)
    best=min((r for r in records if r['valid']),key=lambda r:r['score'])
    control=min((r for r in random_records if r['valid']),key=lambda r:r['score'])
    finalists={}
    for method,record in [('optimized',best),('random',control)]:
        _,_,tight=o.fit(record['x'],tight=True);assert tight['valid']
        assert abs(tight['score']-record['score'])<1e-8*max(1.,record['score'])
        coords=o.rationalize(record['x'])
        rounded_x=[float(Q(c)*h) for (_,c),h in zip(coords,o.heights)][1:]
        _,_,rounded=o.fit(rounded_x,tight=True);assert rounded['valid']
        finalists[method]={'coordinates':coords,'float_recheck':tight,'rounded_recheck':rounded}
    return {'family':family['number'],'characters':family['characters'],'basis_indices':o.ids,
            'physical_rows':o.nrows,'correction_columns':840,'parameter_count':n,
            'coefficient_heights':[str(h) for h in o.heights],'gradient_checks':gradient_checks,
            'optimizer_runs':runs,'optimizer_evaluations':records,'random_evaluations':random_records,
            'finalists':finalists,'seconds':time.perf_counter()-start}


def save(report,cases):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    with gzip.open(OUT/'certificates.json.gz','wt',encoding='utf-8') as f:
        json.dump({'target':{'F':t.base.poly_json(t.base.F),'A':t.base.poly_json(t.base.A),'q':1},
                   'basis_sha256':hashlib.sha256(t.e1.BASIS.read_bytes()).hexdigest(),'cases':cases},f,separators=(',',':'))


def run(limit=None):
    model=t.Model();source=read_packet();families=selection(source);assert len(families)==16
    if limit:families=families[:limit]
    numeric=NumericModel(model);cases=[]
    report={'seed':SEED,'configuration':CONFIG,'instance':'holdout','target_commit':'b8c4edeb80a82395ec07164caf445cfa43bbbd56',
            'selected_families':[f['number'] for f in families],
            'selection_source_sha256':hashlib.sha256((t.OUT/'certificates.json.gz').read_bytes()).hexdigest(),
            'objective':'min_z ||b(a)+M(a)z||_2^2 / ||D(a) mod F||_2^4',
            'metric':'fixed unweighted physical remainder coefficients',
            'scope':'Real bounded affine charts in surviving degree-seven triple spans. Two L-BFGS-B starts and an equal-evaluation random comparator. Rounded exact rejections are only fixed-direction statements. No family exclusion or global optimum claimed.',
            'compute':'CPU SciPy sparse variable projection; exact Fraction validation',
            'families':[],'complete':False}
    for family in families:
        print('BUILD/OPTIMIZE',family['number'],len(family['remaining'])-1,'parameters',flush=True)
        record=optimize_family(family,numeric)
        for method,finalist in record['finalists'].items():
            case=exact_case(finalist['coordinates'],family,model)
            case.update(family=family['number'],method=method);cases.append(case)
        report['families'].append(record);save(report,cases)
        print('DONE',family['number'],{k:(v['float_recheck']['score'],v['rounded_recheck']['score']) for k,v in record['finalists'].items()},
              'evaluations',len(record['optimizer_evaluations']),'seconds',round(record['seconds'],2),flush=True)
    report['complete']=True;save(report,cases);check(write_reports=True)


def check(independent=False,numerics=False,write_reports=False):
    assert not numerics or independent
    report=json.loads((OUT/'report.json').read_text(encoding='utf-8'))
    with gzip.open(OUT/'certificates.json.gz','rt',encoding='utf-8') as f:packet=json.load(f)
    assert packet['basis_sha256']==hashlib.sha256(t.e1.BASIS.read_bytes()).hexdigest()
    assert packet['target']=={'F':t.base.poly_json(t.base.F),'A':t.base.poly_json(t.base.A),'q':1}
    assert report['configuration']==CONFIG and report['seed']==SEED and report['complete']
    assert report['selection_source_sha256']==hashlib.sha256((t.OUT/'certificates.json.gz').read_bytes()).hexdigest()
    selected=selection(read_packet());allowed=[f['number'] for f in selected]
    assert report['selected_families']==allowed[:len(report['selected_families'])]
    assert [r['family'] for r in report['families']]==report['selected_families']
    assert len(packet['cases'])==2*len(report['families'])
    _,pairs=t.e1.load();fields,_=t.e1.koszul_fields()
    for row in report['families']:
        family=next(f for f in selected if f['number']==row['family'])
        assert row['basis_indices']==family['remaining'] and row['correction_columns']==840
        assert row['parameter_count']==len(row['basis_indices'])-1
        assert len(row['optimizer_evaluations'])==len(row['random_evaluations'])
        assert sum(r['evaluations'] for r in row['optimizer_runs'])==len(row['optimizer_evaluations'])
        for method,key in [('optimized','optimizer_evaluations'),('random','random_evaluations')]:
            best=min((r for r in row[key] if r['valid']),key=lambda r:r['score'])
            coords=[[i,str(Q(v).limit_denominator(CONFIG['round_denominator'])/Q(h))]
                    for i,v,h in zip(row['basis_indices'],[1.,*best['x']],row['coefficient_heights'])]
            case=next(c for c in packet['cases'] if c['family']==row['family'] and c['method']==method)
            assert case['coordinates']==coords==row['finalists'][method]['coordinates']
            if not independent:verify(case,pairs,fields)
    numerical_rechecks=[]
    if independent:
        from degree7_verify_polynomials import poly,decode,remainder,B
        target=poly.load_target(ROOT/'sources/sextics/data/holdout');F,A=target['F'],target['A']
        assert target['q']==1 and F==decode(packet['target']['F']) and A==decode(packet['target']['A'])
        # Separate derivative/multiplication API and opposite reduction order.
        DF=[poly.derivative(F,i) for i in range(6)];indfields=[]
        mons=[(a,b,c,d,e,3-a-b-c-d-e) for a in range(4) for b in range(4-a)
              for c in range(4-a-b) for d in range(4-a-b-c) for e in range(4-a-b-c-d)]
        from itertools import combinations
        for i,j in combinations(range(6),2):
            for m in mons:
                K=[{} for _ in range(6)];K[i]=poly.mul({m:Q(1)},DF[j]);K[j]=poly.scale(poly.mul({m:Q(1)},DF[i]),-1)
                indfields.append(K)
        assert len(indfields)==840
        for case in packet['cases']:
            assert case['status']=='rejected','A solvable candidate needs a full admissibility check before any success claim.'
            D={};N=[{} for _ in range(6)]
            for i,c in case['coordinates']:
                D=poly.add(D,poly.scale(pairs[i][0],Q(c)))
                N=[poly.add(n,poly.scale(p,Q(c))) for n,p in zip(N,pairs[i][1])]
            directional={}
            for n,df in zip(N,DF):directional=poly.add(directional,poly.mul(n,df))
            assert directional==poly.mul(A,D) and remainder(D,F)
            dual={tuple(m):Q(c) for m,c in case['dual_functional']}
            rhs=remainder(B(D,N),F)
            columns=[remainder(B(D,K),F) for K in indfields]
            assert sum(c*dual.get(m,0) for m,c in rhs.items())==1
            assert all(sum(c*dual.get(m,0) for m,c in col.items())==0 for col in columns)
            if numerics:
                import numpy as np
                from scipy import sparse
                from scipy.sparse.linalg import lsmr
                mons=sorted(set(rhs).union(*(set(col) for col in columns)));lookup={m:i for i,m in enumerate(mons)}
                b=np.zeros(len(mons))
                for m,c in rhs.items():b[lookup[m]]=float(c)
                entries=[(lookup[m],j,float(c)) for j,col in enumerate(columns) for m,c in col.items()]
                rr,cc,vv=zip(*entries);M=sparse.coo_matrix((vv,(rr,cc)),shape=(len(mons),840)).tocsr()
                scales=np.sqrt(np.asarray(M.power(2).sum(axis=0)).ravel());active=scales>0
                T=M[:,active].multiply(1/scales[active]).tocsr()
                fit=lsmr(T,-b,atol=1e-14,btol=1e-14,conlim=1e15,maxiter=12000)
                r=b+T@fit[0];normal=float(np.linalg.norm(T.T@r)/max(np.linalg.norm(b),1e-30))
                assert fit[1] in (0,1,2,4,5) and normal<1e-9
                dscale=sum(float(c)**2 for c in remainder(D,F).values())
                score=float(r@r)/dscale**2
                row=next(v for v in report['families'] if v['family']==case['family'])
                expected=row['finalists'][case['method']]['rounded_recheck']['score']
                error=abs(score-expected)/max(abs(expected),1e-30)
                assert error<1e-6
                numerical_rechecks.append({'family':case['family'],'method':case['method'],
                    'independently_assembled_score':score,'relative_score_difference':error,'normal_residual':normal})
    else:
        bad=copy.deepcopy(next(c for c in packet['cases'] if c['status']=='rejected'))
        bad['dual_functional']=[[m,str(2*Q(c))] for m,c in bad['dual_functional']]
        try:verify(bad,pairs,fields)
        except AssertionError:pass
        else:raise AssertionError('Corrupted dual accepted')
    result={'status':'PASS','families':len(report['families']),'exact_directions':len(packet['cases']),
            'rejected':sum(c['status']=='rejected' for c in packet['cases']),
            'independent_polynomial_api':independent,'correction_columns_checked':840*len(packet['cases'])}
    print(json.dumps(result),flush=True)
    # Verification must not replace archived floating-point results with a
    # different platform's last-bit values before their hashes are checked.
    if write_reports:
        (OUT/('independent-validation.json' if independent else 'validation.json')).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    if numerics:
        result['numerical_rechecks']=numerical_rechecks
        print(json.dumps({'numerical_rechecks':len(numerical_rechecks),
              'max_relative_score_difference':max(v['relative_score_difference'] for v in numerical_rechecks)}),flush=True)
        if write_reports:
            (OUT/'numerical-validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true');parser.add_argument('--independent',action='store_true')
    parser.add_argument('--numerics',action='store_true',help='Recheck rounded scores with the independent polynomial assembly.')
    parser.add_argument('--write-reports',action='store_true',help='Explicitly replace archived validation reports after checking.')
    parser.add_argument('--limit',type=int)
    args=parser.parse_args()
    if args.write_reports and not args.check:parser.error('--write-reports requires --check')
    if args.check:check(args.independent,args.numerics,args.write_reports)
    else:run(args.limit)
