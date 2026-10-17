"""Geometric, syzygy-preserving projections of three actual correction maps.

The pictures use rounded finalists already rejected in the optimization packet.
All 840 columns are reconstructed over Fraction. Two numerical response axes
and an exact dual functional define a three-dimensional quotient view.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse,gzip,hashlib,html,json,re,sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'algebra'))
import degree7_e1 as e1
import degree6_e1 as base
from degree6_e2_model import modF
from degree6_quadratic_structure import B
from degree7_verify_polynomials import poly,remainder,B as independent_B
OUT=ROOT/'results/koszul-geometry'
VIS=ROOT/'visualizations'
SOURCE=ROOT/'results/koszul-parameter-optimization/certificates.json.gz'


def digest(path):
    raw=path.read_bytes()
    if path.suffix!='.gz':raw=raw.replace(b'\r\n',b'\n')
    return hashlib.sha256(raw).hexdigest()


def decode_case(case,pairs):
    D={};N=[{} for _ in range(6)]
    for i,c in case['coordinates']:
        D=base.padd(D,pairs[i][0],Q(c))
        N=[base.padd(n,p,Q(c)) for n,p in zip(N,pairs[i][1])]
    return D,N


def derive():
    with gzip.open(SOURCE,'rt',encoding='utf-8') as f:packet=json.load(f)
    data,pairs=e1.load();fields,labels=e1.koszul_fields()
    target=poly.load_target(ROOT/'sources/sextics/data/holdout')
    F,A=target['F'],target['A']
    assert target['q']==1 and F==base.F and A==base.A and len(fields)==840
    selected={}
    for case in packet['cases']:
        if case['method']!='optimized':continue
        D,N=decode_case(case,pairs)
        n=len({e1.character(m) for m in modF(D)})
        if n not in selected:selected[n]=(case,D,N)
    assert set(selected)=={1,2,3}
    output=[];checks=[]
    for n,(case,D,N) in sorted(selected.items()):
        assert e1.directional(N)==base.pmul(A,D) and modF(D)
        b=modF(B(D,N));columns=[modF(B(D,K)) for K in fields]
        dual={tuple(m):Q(c) for m,c in case['dual_functional']}
        dot=lambda p:sum(c*dual.get(m,0) for m,c in p.items())
        assert dot(b)==1 and all(dot(col)==0 for col in columns)
        assert remainder(independent_B(D,N),F)==b
        DF=[poly.derivative(F,i) for i in range(6)]
        for j,(i,k,m) in enumerate(labels):
            K=[{} for _ in range(6)]
            K[i]=poly.mul({tuple(m):Q(1)},DF[k])
            K[k]=poly.scale(poly.mul({tuple(m):Q(1)},DF[i]),-1)
            assert remainder(independent_B(D,K),F)==columns[j]
        mons=sorted(set(b)|set(dual)|set().union(*(set(c) for c in columns)))
        index={m:i for i,m in enumerate(mons)}
        M=np.zeros((len(mons),840));wanted=np.zeros(len(mons));lam=np.zeros(len(mons))
        for j,col in enumerate(columns):
            for m,c in col.items():M[index[m],j]=float(c)
        for m,c in b.items():wanted[index[m]]=-float(c)
        for m,c in dual.items():lam[index[m]]=float(c)
        # First observable follows one Gram response to the target. The second
        # uses the column with greatest energy transverse to that response.
        response=M@(M.T@wanted);q1=response/np.linalg.norm(response)
        orth=M-q1[:,None]*(q1@M)[None,:]
        lengths=np.sum(orth*orth,axis=0)
        # Resolve numerical ties by the original column order, so BLAS
        # summation differences do not select a different display plane.
        second=int(np.flatnonzero(lengths>=lengths.max()*(1-1e-12))[0])
        q2=orth[:,second]/np.linalg.norm(orth[:,second])
        U=np.vstack([q1,q2]);S=U@M;H=S@S.T
        eig,V=np.linalg.eigh(H);order=np.argsort(eig)[::-1]
        eig=eig[order];V=V[:,order]
        assert eig[1]>eig[0]*1e-12
        # Stable eigenvector signs, including an axis along the target.
        for j in range(2):
            if (V[:,j]@(U@wanted))<0:V[:,j]*=-1
        sigma=np.sqrt(eig);right=S.T@V/sigma[None,:]
        observed=V.T@(U@wanted)
        zfit=observed/sigma
        radius=1.25*np.linalg.norm(zfit)
        scale=np.linalg.norm(wanted)
        axes=radius*sigma/scale
        target_xy=observed/scale
        fit=target_xy/axes
        # q1,q2 are orthonormal and in im M; the exact dual annihilates
        # every column. The vertical display uses -lambda, not a unit normal.
        orth_error=float(np.max(np.abs(U@U.T-np.eye(2))))
        right_error=float(np.max(np.abs(right.T@right-np.eye(2))))
        map_error=float(np.max(np.abs(V.T@U@M@right-np.diag(sigma)))/sigma[0])
        dual_error=float(np.max(np.abs(lam@M))/max(1.,np.linalg.norm(lam)*np.linalg.norm(M)))
        assert max(orth_error,right_error,map_error,dual_error)<1e-10
        assert np.max(np.abs((axes*fit)-target_xy))<1e-12
        assert abs(np.linalg.norm(fit)-.8)<1e-10
        # Repeated symmetric eigenvalues need a different frame convention.
        assert eig[0]-eig[1]>1e-8*eig[0]
        display={'family':case['family'],'characters':n,'method':'optimized',
            'axes':axes.tolist(),'target':[float(target_xy[0]),float(target_xy[1]),1.],
            'fit':fit.tolist(),'correctionRadius':float(radius),'rowCount':len(mons),
            'axisRatio':float(sigma[1]/sigma[0]),'dualTarget':'-1','displayGap':'1',
            'sourceCommit':'13ed038b1740c6a35203d395910340ae1d36afb8'}
        output.append(display)
        checks.append({'family':case['family'],'character_count':n,'exact_columns_checked':840,
            'independently_reconstructed_columns':840,'target_pairing':'1',
            'second_axis_column':second,'orthonormal_error':orth_error,
            'right_modes_error':right_error,'map_error':map_error,'dual_float_error':dual_error})
    return {'version':1,'cases':output},checks


def close(a,b):
    if isinstance(a,dict):
        assert a.keys()==b.keys()
        for k in a:close(a[k],b[k])
    elif isinstance(a,list):
        assert len(a)==len(b)
        for x,y in zip(a,b):close(x,y)
    elif isinstance(a,float):assert np.isclose(a,b,rtol=1e-9,atol=1e-12),(a,b)
    else:assert a==b,(a,b)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true');args=parser.parse_args()
    display,checks=derive();OUT.mkdir(exist_ok=True)
    sources={'packet':digest(SOURCE),'basis':digest(e1.BASIS),
        'instance':digest(ROOT/'sources/sextics/data/holdout/instance.rec')}
    if args.check:
        saved=json.loads((OUT/'geometry.json').read_text(encoding='utf-8'))
        close(display,saved)
        validation=json.loads((OUT/'validation.json').read_text(encoding='utf-8'))
        assert validation['sources_sha256']==sources
        display=saved
    else:
        (OUT/'geometry.json').write_text(json.dumps(display,indent=2)+'\n',encoding='utf-8',newline='\n')
        (OUT/'validation.json').write_text(json.dumps({'status':'PASS','sources_sha256':sources,'cases':checks,
          'scope':'Three archived fixed-denominator rejections. Two response modes and an exact dual define a quotient-space view. No full rank claim, new search, or genus identification.'},indent=2)+'\n',encoding='utf-8',newline='\n')
    template=VIS/'koszul-geometry.template.html';fragment=VIS/'koszul-geometry.html'
    if template.exists():
        expected=template.read_text(encoding='utf-8').replace('__KOSZUL_GEOMETRY__',json.dumps(display,separators=(',',':')))
        assert len(expected.encode())<1_000_000
        if args.check:
            assert fragment.read_text(encoding='utf-8')==expected
            export=(VIS/'koszul-geometry-standalone.html').read_text(encoding='utf-8')
            embedded=re.search(r'data-srcdoc="([^"]+)"',export)
            assert embedded and expected in html.unescape(embedded.group(1))
        else:fragment.write_text(expected,encoding='utf-8',newline='\n')
    print(json.dumps({'status':'PASS','families':[v['family'] for v in checks],
        'exact_column_checks':sum(v['exact_columns_checked'] for v in checks),
        'independent_column_checks':sum(v['independently_reconstructed_columns'] for v in checks),
        'maximum_map_error':max(v['map_error'] for v in checks)},indent=2))


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    main()
