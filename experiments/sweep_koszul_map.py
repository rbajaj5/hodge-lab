"""A two-parameter physical correction map, with exact ranks at 81 points.

D = D_42 + s D_272 + t D_294 (raw degree-seven E1 basis indices).
All 840 cubic Koszul corrections are retained. Fraction elimination computes
each full rank, independently checked modulo a prime. The visual frame is fixed.
"""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations_with_replacement
import argparse,gzip,hashlib,html,json,re,sys,time,os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
import numpy as np
from scipy import sparse
from scipy.linalg import eigvalsh
from scipy.sparse.linalg import lsmr

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'algebra'))
import degree7_triples as t
from degree7_verify_polynomials import poly,remainder,B as other_B
OUT=ROOT/'results/koszul-map-sweep'
VIS=ROOT/'visualizations'
IDS=[42,272,294]
GRID=[Q(i,2) for i in range(-4,5)]

def digest(path):
    raw=path.read_bytes()
    if path.suffix!='.gz':raw=raw.replace(b'\r\n',b'\n')
    return hashlib.sha256(raw).hexdigest()

def modular_rank(columns,p=1000003):
    basis={}
    for col in columns:
        c={m:(v.numerator*pow(v.denominator,-1,p))%p for m,v in col.items()}
        c={m:v for m,v in c.items() if v}
        while c:
            m=min(c);v=c[m]
            if m not in basis:
                inv=pow(v,-1,p);basis[m]={n:w*inv%p for n,w in c.items()};break
            for n,w in basis[m].items():
                z=(c.get(n,0)-v*w)%p
                if z:c[n]=z
                elif n in c:del c[n]
    return len(basis)

def combine(polys,weights):
    out={}
    for p,w in zip(polys,weights):out=t.base.padd(out,p,w)
    return out

def derive():
    model=t.Model();pairs=[model.pairs[i] for i in IDS]
    coeffs=list(combinations_with_replacement(range(3),2))
    columns=[[t.modF(t.B(D,K)) for K in model.fields] for D,N in pairs]
    quad=[model.quadratic(IDS[i],IDS[j]) for i,j in coeffs]
    target=poly.load_target(ROOT/'sources/sextics/data/holdout')
    assert target['q']==1 and target['F']==t.base.F and target['A']==t.base.A
    # Independent polynomial assembly, with the opposite remainder order.
    DF=[poly.derivative(target['F'],i) for i in range(6)]
    _,labels=t.e1.koszul_fields()
    for k,(i,j,m) in enumerate(labels):
        K=[{} for _ in range(6)]
        K[i]=poly.mul({tuple(m):Q(1)},DF[j]);K[j]=poly.scale(poly.mul({tuple(m):Q(1)},DF[i]),-1)
        for a,(D,N) in enumerate(pairs):assert remainder(other_B(D,K),target['F'])==columns[a][k]
    for k,(i,j) in enumerate(coeffs):
        b=other_B(pairs[i][0],pairs[j][1])
        if i!=j:b=poly.add(b,other_B(pairs[j][0],pairs[i][1]))
        assert remainder(b,target['F'])==quad[k]
    with gzip.open(t.OUT/'certificates.json.gz','rt',encoding='utf-8') as f:packet=json.load(f)
    family=next(f for f in packet['families'] if f['number']==4)
    # Find a common annihilator whose target pairing is a nonzero constant
    # on this affine plane. This is a restriction of an archived necessity.
    for no,row in enumerate(family['stages'][-1]['necessary']):
        dual=t.e1.decode(row['dual']);vals=[t.dot(dual,b) for b in quad]
        if vals[0] and not any(vals[1:]):break
    else:raise AssertionError('No constant obstruction on chosen plane')
    dual={m:c/vals[0] for m,c in dual.items()}
    assert [t.dot(dual,b) for b in quad]==[1,0,0,0,0,0]
    assert all(t.dot(dual,c)==0 for row in columns for c in row)
    for D,N in pairs:assert t.e1.directional(N)==t.base.pmul(t.base.A,D)
    # Nonzero distinct-character directions make every denominator nonzero mod F.
    assert len({model.dc[i] for i in IDS})==3 and all(t.modF(D) for D,N in pairs)
    mons=sorted(set(dual)|set().union(*(set(c) for row in columns for c in row),*(set(b) for b in quad)))
    index={m:i for i,m in enumerate(mons)}
    def matrix(cols):
        entries=[(index[m],j,float(c)) for j,p in enumerate(cols) for m,c in p.items()]
        rr,cc,vv=zip(*entries)
        return sparse.coo_matrix((vv,(rr,cc)),shape=(len(mons),len(cols))).tocsr()
    mats=[matrix(row) for row in columns];qm=matrix(quad)
    M=sum(mats);wanted=-qm@np.ones(6)
    q1=np.asarray(M@(M.T@wanted));q1/=np.linalg.norm(q1)
    dense=M.toarray();orth=dense-q1[:,None]*(q1@dense)[None,:]
    lengths=np.sum(orth**2,axis=0);second=int(np.flatnonzero(lengths>=lengths.max()*(1-1e-12))[0])
    q2=orth[:,second]/np.linalg.norm(orth[:,second]);U=np.vstack([q1,q2])
    S=[np.asarray(U@a) for a in mats];xy=np.asarray(-U@qm)
    H=[S[i]@S[j].T+(S[j]@S[i].T if i!=j else 0) for i,j in coeffs]
    href=sum(H);refxy=xy@np.ones(6)
    radius=1.25*np.sqrt(refxy@np.linalg.solve(href,refxy))
    scale=radius*np.sqrt(np.linalg.eigvalsh(href)[-1])
    frames=[{'name':'Overall response','gramCoefficients':[(radius**2*h/scale**2).tolist() for h in H],
        'targetCoefficients':(xy/scale).tolist(),'horizontalScale':float(scale)}]
    # A second, fixed coordinate projection isolates rows supported only by
    # D_272 and only by D_294. Its rank can fall even when the full rank does not.
    supports=[set().union(*(set(c) for c in row)) for row in columns]
    exclusive=[]
    for k in [1,2]:
        candidates=supports[k]-set().union(*(supports[j] for j in range(3) if j!=k))
        energies={m:sum(c.get(m,0)**2 for c in columns[k]) for m in candidates}
        top=max(energies.values());exclusive.append(min(m for m,v in energies.items() if v==top))
    selector=np.zeros_like(U)
    for i,m in enumerate(exclusive):selector[i,index[m]]=1
    exactrows=[[c.get(m,Q(0)) for c in columns[k]] for k,m in zip([1,2],exclusive)]
    exactgram=[[sum(a*b for a,b in zip(r,v)) for v in exactrows] for r in exactrows]
    assert exactgram==[[Q(2308),Q(0)],[Q(0),Q(2308,9)]]
    assert all(not b.get(m,0) for b in quad for m in exclusive)
    sens=[np.asarray(selector@m) for m in mats]
    sh=[sens[i]@sens[j].T+(sens[j]@sens[i].T if i!=j else 0) for i,j in coeffs]
    sx=np.asarray(-selector@qm);ss=radius*np.sqrt(np.linalg.eigvalsh(sum(sh))[-1])
    assert np.linalg.det(sum(sh))>0
    frames.append({'name':'Parameter-sensitive rows','gramCoefficients':[(radius**2*h/ss**2).tolist() for h in sh],
        'targetCoefficients':(sx/ss).tolist(),'horizontalScale':float(ss),
        'rowMonomials':[list(m) for m in exclusive]})
    reduced=[t.modF(D) for D,N in pairs]
    Dgram=np.array([[float(sum(c*E.get(m,0) for m,c in D.items())) for E in reduced] for D in reduced])
    samples=[];started=time.perf_counter()
    for s in GRID:
        for u in GRID:
            a=[Q(1),s,u];weights=[a[i]*a[j] for i,j in coeffs]
            exactcols=[combine([columns[i][j] for i in range(3)],a) for j in range(840)]
            span=t.base.Elimination()
            for c in exactcols:span.insert(dict(c))
            rank=len(span.basis);mr=modular_rank(exactcols);assert rank==mr
            b=combine(quad,weights)
            assert t.dot(dual,b)==1 and all(t.dot(dual,c)==0 for c in exactcols)
            mat=sum(float(v)*m for v,m in zip(a,mats));rhs=qm@np.array(weights,dtype=float)
            norms=np.sqrt(np.asarray(mat.power(2).sum(axis=0)).ravel());active=norms>0
            T=mat[:,active].multiply(1/norms[active]).tocsr()
            fit=lsmr(T,-rhs,atol=1e-13,btol=1e-13,conlim=1e15,maxiter=6000)
            residual=rhs+T@fit[0];normal=np.linalg.norm(T.T@residual)/np.linalg.norm(rhs)
            assert fit[1] in (1,2,4,5) and normal<1e-9
            ev=eigvalsh((mat.T@mat).toarray(),check_finite=False)
            assert ev[-rank]>ev[-1]*1e-12
            assert np.max(np.abs(ev[:-rank]))<ev[-1]*1e-11
            samples.append({'s':float(s),'t':float(u),'rank':rank,'nullity':840-rank,
                'modularRank':mr,'prime':1000003,'sigmaRatio':float(np.sqrt(ev[-rank]/ev[-1])),
                'trackedRatio':float(np.sqrt(ev[-720]/ev[-1])) if rank>=720 else 0.,
                'score':float(residual@residual/(np.array(a,dtype=float)@Dgram@np.array(a,dtype=float))**2),
                'normalResidual':float(normal),'exactTargetPairing':'1'})
        print('ROW',str(s),'ranks',[v['rank'] for v in samples[-9:]],flush=True)
    display={'version':1,'family':4,'basis':IDS,'grid':[float(v) for v in GRID],
        'quadraticPairs':coeffs,'gramCoefficients':[(radius**2*h/scale**2).tolist() for h in H],
        'targetCoefficients':(xy/scale).tolist(),'sourceRadius':float(radius),
        'horizontalScale':float(scale),'samples':samples,'rows':len(mons),
        'frameReference':[1,1],'secondAxisColumn':second,'frames':frames}
    proof={'basis':IDS,'family':4,'necessityIndex':no,'dual':t.base.poly_json(dual),
        'targetQuadraticPairings':['1','0','0','0','0','0'],
        'conclusion':'Every D_42+s D_272+t D_294 fails E2 for all complex s,t. This follows by restricting a previously archived family-4 necessary condition; it does not exclude the full family.',
        'independentColumns':2520,'independentQuadraticTerms':6,'exactRanks':81,
        'modularRanks':81,'sensitiveRows':[list(m) for m in exclusive],
        'sensitiveGramAtOne':[[str(v) for v in row] for row in exactgram],
        'sensitiveTargetIdenticallyZero':True,'seconds':time.perf_counter()-started}
    return display,proof

def close(a,b):
    if isinstance(a,dict):
        assert a.keys()==b.keys()
        for k in a:close(a[k],b[k])
    elif isinstance(a,(list,tuple)):
        assert len(a)==len(b)
        for x,y in zip(a,b):close(x,y)
    elif isinstance(a,float):assert np.isclose(a,b,rtol=1e-8,atol=1e-11),(a,b)
    else:assert a==b,(a,b)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    data,proof=derive()
    sources={p.relative_to(ROOT).as_posix():digest(p) for p in [t.e1.BASIS,t.OUT/'certificates.json.gz',ROOT/'sources/sextics/data/holdout/instance.rec']}
    if args.check:
        saved=json.loads((OUT/'sweep.json').read_text());close(data,saved);data=saved
        report=json.loads((OUT/'validation.json').read_text());assert report['sources']==sources
        old=report['proof'];old.pop('seconds');proof.pop('seconds');assert old==proof
    else:
        OUT.mkdir(exist_ok=True);(OUT/'sweep.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
        (OUT/'validation.json').write_text(json.dumps({'status':'PASS','sources':sources,'proof':proof},indent=2)+'\n',encoding='utf-8',newline='\n')
    template=VIS/'koszul-map-sweep.template.html'
    if template.exists():
        content=template.read_text(encoding='utf-8').replace('__SWEEP_DATA__',json.dumps(data,separators=(',',':')))
        assert len(content.encode())<1000000
        fragment=VIS/'koszul-map-sweep.html'
        if args.check:
            assert fragment.read_text(encoding='utf-8')==content
            embedded=re.search(r'data-srcdoc="([^"]+)"',(VIS/'koszul-map-sweep-standalone.html').read_text(encoding='utf-8'))
            assert embedded and content in html.unescape(embedded.group(1))
        else:fragment.write_text(content,encoding='utf-8',newline='\n')
    print(json.dumps({'status':'PASS','ranks':sorted({p['rank'] for p in data['samples']}),'samples':len(data['samples'])}))

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O')
    main()
