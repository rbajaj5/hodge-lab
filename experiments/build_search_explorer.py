"""Derive character-energy trajectories for the recorded optimization search.

This changes presentation only. It neither reruns optimization nor adds exact
rejections. Each character's contribution is its squared coefficient norm in
the chosen remainder representative D mod F, including within-sector cross terms.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse,gzip,hashlib,html,json,re,sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'algebra'))
import degree7_e1 as e1
import degree6_e1 as p
from degree6_e2_model import modF
SRC=ROOT/'results/koszul-parameter-optimization'
OUT=ROOT/'visualizations'


def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()


def derive():
    report=json.loads((SRC/'report.json').read_text(encoding='utf-8'))
    with gzip.open(SRC/'certificates.json.gz','rt',encoding='utf-8') as f:cert=json.load(f)
    _,pairs=e1.load();families=[];checks=0
    for row in report['families']:
        ids=row['basis_indices'];heights=list(map(Q,row['coefficient_heights']))
        D=[modF(pairs[i][0]) for i in ids]
        chars=[tuple(c) for c in row['characters']]
        assert len(chars)==len(set(chars))==3
        assert len(row['optimizer_evaluations'])==len(row['random_evaluations'])
        labels=[]
        for d in D:
            labels.append(next(iter({e1.character(m) for m in d})))
            assert {e1.character(m) for m in d}=={labels[-1]}
        grams=[]
        for character in chars:
            G=np.zeros((len(ids),len(ids)))
            for i,di in enumerate(D):
                for j,dj in enumerate(D):
                    product=sum(c*dj.get(m,0) for m,c in di.items())/(heights[i]*heights[j])
                    if labels[i]!=labels[j]:assert product==0
                    if labels[i]==labels[j]==character:G[i,j]=float(product)
            grams.append(G)
        def shares(x):
            a=np.array([1.,*x]);energy=np.array([float(a@G@a) for G in grams])
            assert energy.min()>-1e-12 and energy.sum()>0
            energy=np.maximum(energy,0);return energy/energy.sum()
        def exact_shares(coords):
            d={}
            for i,c in coords:d=p.padd(d,pairs[i][0],Q(c))
            d=modF(d);energy=[sum(c*c for m,c in d.items() if e1.character(m)==character) for character in chars]
            total=sum(energy);assert total>0
            return [float(v/total) for v in energy],sum(v!=0 for v in energy)
        # Direct polynomial checks at both ends of both recorded sequences.
        for method in ['optimizer_evaluations','random_evaluations']:
            for rec in [row[method][0],row[method][-1]]:
                coords=[[i,str(Q(str(v))/h)] for i,v,h in zip(ids,[1.,*rec['x']],heights)]
                direct,_=exact_shares(coords)
                assert np.max(np.abs(shares(rec['x'])-direct))<1e-12;checks+=1
        rounded={}
        for method in ['optimized','random']:
            case=next(c for c in cert['cases'] if c['family']==row['family'] and c['method']==method)
            exact,count=exact_shares(case['coordinates'])
            rounded[method]={'shares':exact,'characters':count,'status':case['status']}
        def compact(records):
            return [[float(format(rec['score'],'.9g')),*[float(format(v,'.9g')) for v in shares(rec['x'])]] for rec in records]
        families.append({'id':row['family'],'characters':row['characters'],
            'optimized':compact(row['optimizer_evaluations']),'random':compact(row['random_evaluations']),
            'restartAt':1+row['optimizer_runs'][0]['evaluations'],'rounded':rounded})
    assert len(families)==16 and checks==64
    data={'version':1,'families':families,'rowFormat':['score','share_0','share_1','share_2'],
          'sourceCommit':'13ed038b1740c6a35203d395910340ae1d36afb8'}
    validation={'status':'PASS','families':16,'optimizer_states':sum(len(f['optimized']) for f in families),
                'random_states':sum(len(f['random']) for f in families),'direct_polynomial_share_checks':checks,
                'source_sha256':{'report':sha(SRC/'report.json'),'basis':sha(e1.BASIS),
                  'certificates_gzip':hashlib.sha256((SRC/'certificates.json.gz').read_bytes()).hexdigest()},
                'interpretation':'Squared coefficient norm shares of the three characters in D mod F. Within-character cross terms retained. A display of existing searches only.'}
    return data,validation


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    data,validation=derive();template=OUT/'koszul-search.template.html';fragment=OUT/'koszul-search.html'
    encoded=json.dumps(data,separators=(',',':'))
    assert '</script' not in encoded
    expected=template.read_text(encoding='utf-8').replace('__KOSZUL_DATA__',encoded)
    assert len(expected.encode())<1_000_000 and '__KOSZUL_DATA__' not in expected
    validation['fragment_bytes']=len(expected.encode())
    validation['fragment_sha256']=hashlib.sha256(expected.encode()).hexdigest()
    if args.check:
        assert fragment.read_text(encoding='utf-8')==expected
        assert json.loads((SRC/'explorer-validation.json').read_text(encoding='utf-8'))==validation
        exported=(OUT/'koszul-search-standalone.html').read_text(encoding='utf-8')
        embedded=re.search(r'data-srcdoc="([^"]+)"',exported)
        assert embedded and expected in html.unescape(embedded.group(1)), 'Standalone export is stale.'
    else:
        fragment.write_text(expected,encoding='utf-8',newline='\n')
        (SRC/'explorer-validation.json').write_text(json.dumps(validation,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(validation,indent=2))


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    main()
