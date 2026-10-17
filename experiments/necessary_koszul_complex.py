"""Finite Koszul homology of the three checked necessary-block ideals.

This is K(P; S), not an identification with Yang's geometric K_{p,q}(B,L).
"""
from fractions import Fraction as Q
from itertools import combinations, combinations_with_replacement
from pathlib import Path
import argparse, hashlib, json
import graded_map_patterns as g

OUT=g.OUT.parent/'necessary-koszul-complex'


def add(a,b,c=Q(1)):
    out=dict(a)
    for i,v in b.items():
        out[i]=out.get(i,Q(0))+c*v
        if not out[i]:del out[i]
    return out


class Span:
    def __init__(self):self.rows={}
    def reduce(self,v):
        v=dict(v)
        for pivot,row in sorted(self.rows.items()):
            if pivot in v:v=add(v,row,-v[pivot])
        return v
    def insert(self,v):
        v=self.reduce(v)
        if not v:return False
        pivot=min(v);self.rows[pivot]={i:c/v[pivot] for i,c in v.items()}
        return True


def image(cols):
    span=Span()
    for c in cols:span.insert(c)
    return span


def apply(cols,v):
    out={}
    for i,c in v.items():out=add(out,cols[i],c)
    return out


def kernel(cols):
    pivots={};result=[]
    for j,column in enumerate(cols):
        v=dict(column);w={j:Q(1)}
        for pivot,(row,coeff) in sorted(pivots.items()):
            if pivot in v:
                c=v[pivot];v=add(v,row,-c);w=add(w,coeff,-c)
        if not v:
            assert not apply(cols,w);result.append(w)
        else:
            pivot=min(v);c=v[pivot]
            pivots[pivot]=({i:a/c for i,a in v.items()},{i:a/c for i,a in w.items()})
    assert len(result)+len(pivots)==len(cols)
    assert len(image(result).rows)==len(result)
    return result


def complex_at(eq,ids,degree):
    r=len(eq);bases=[]
    assert all(p and {len(m) for m in p}=={2} for p in eq)
    for k in range(r+1):
        bases.append([(I,m) for I in combinations(range(r),k)
            for m in combinations_with_replacement(ids,degree-2*k)] if degree>=2*k else [])
    differentials=[[]]
    for k in range(1,r+1):
        index={v:i for i,v in enumerate(bases[k-1])};cols=[]
        for I,m in bases[k]:
            col={}
            for pos,j in enumerate(I):
                J=I[:pos]+I[pos+1:]
                for mon,c in eq[j].items():
                    at=index[(J,tuple(sorted(m+mon)))];col[at]=col.get(at,Q(0))+(-1)**pos*c
            cols.append({i:c for i,c in col.items() if c})
        differentials.append(cols)
    compositions=0
    for k in range(2,r+1):
        for col in differentials[k]:assert not apply(differentials[k-1],col);compositions+=1
    ranks=[0]+[len(image(c).rows) for c in differentials[1:]]+[0]
    homology=[len(bases[k])-ranks[k]-ranks[k+1] for k in range(r+1)]
    cycles=kernel(differentials[1]);boundaries=image(differentials[2] if r>=2 else [])
    representatives=[]
    for v in cycles:
        if boundaries.insert(v):representatives.append(v)
    assert len(representatives)==homology[1]
    assert sum((-1)**k*len(b) for k,b in enumerate(bases))==sum((-1)**k*h for k,h in enumerate(homology))
    return {'degree':degree,'dimensions':[len(b) for b in bases],
        'differential_ranks':ranks[1:-1],'homology':homology,
        'kernel_d1':len(cycles),'boundaries_d2':ranks[2],
        'h1_representatives':[[[i,str(c)] for i,c in sorted(v.items())] for v in representatives],
        'k1_basis':[[list(I),list(m)] for I,m in bases[1]],
        'zero_compositions_checked':compositions}


def data():
    source=g.OUT/'data.json';patterns=json.loads(source.read_text(encoding='utf-8'))
    # Reconstruct physical necessities and verify the exact changes of basis.
    assert patterns==g.data()
    records=[]
    for case in patterns['cases']:
        number=case['batch_number'];packet=g.x.q.load(g.x.OUT/f'family-{number:03d}.json.gz')
        stage=packet['stages'][-1];block=next(b for b in stage['blocks'] if b['character']==packet['third_character'])
        eq=[g.x.cert.decode(stage['necessary'][j]['polynomial']) for j in block['equation_indices']]
        cfg=g.config(number);adapted=cfg[3];ids=list(range(len(cfg[1])))
        for degree in range(2,7):
            raw=complex_at(eq,block['active'],degree);new=complex_at(adapted,ids,degree)
            if degree in [3,4]:
                previous=next(m for m in case['maps'] if m['degree']==degree)
                for basis,result in [('raw',raw),('adapted',new)]:
                    assert result['differential_ranks'][0]==previous[basis]['rank']
                    assert result['kernel_d1']==previous[basis]['kernel']
            for key in ['dimensions','differential_ranks','homology','kernel_d1','boundaries_d2']:
                assert raw[key]==new[key]
            records.append({'case':number,'raw':raw,'adapted':new})
    # The degree-three cycle (-u,v,0) is not a boundary: K2,3 is zero.
    target=next(r['adapted'] for r in records if r['case']==19 and r['adapted']['degree']==3)
    assert target['homology'][1]==1 and target['boundaries_d2']==0
    g19=g.config(19)[3]
    assert not g.x.t.base.padd(g.x.cert.product(g19[0],{(0,):Q(-1)}),g.x.cert.product(g19[1],{(1,):Q(1)}))
    return {'source_canonical_json_sha256':hashlib.sha256(json.dumps(patterns,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        'records':records,'scope':'Finite degree 2 through 6 Koszul homology of three necessary-block ideals; no new family exclusion, full resolution, or geometric Kpq identification.',
        'explicit_B19_cycle':'(-u, v, 0)',
        'checked_complexes':2*len(records)}


def figure(d):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    from matplotlib.ticker import MaxNLocator
    plt.rcParams.update({'font.size':11,'svg.fonttype':'none','svg.hashsalt':'necessary-koszul-complex'})
    fig,axes=plt.subplots(1,3,figsize=(12,4.5),layout='constrained')
    for ax,number in zip(axes,[19,49,100]):
        rs=[r['adapted'] for r in d['records'] if r['case']==number]
        degrees=[r['degree'] for r in rs];b=[r['boundaries_d2'] for r in rs];h=[r['homology'][1] for r in rs]
        ax.bar(degrees,b,color='#5a819c');ax.bar(degrees,h,bottom=b,color='#b5783c')
        for x,y,z in zip(degrees,b,h):
            ax.annotate(str(y+z),(x,y+z),xytext=(0,4),textcoords='offset points',ha='center')
        ax.set(xlabel='Total polynomial degree',ylabel='Dimension over Q',xticks=degrees,
            title=f'B{number}: relations = boundaries + H1',ylim=(0,max(2,max(a+c for a,c in zip(b,h))*1.22)))
        ax.spines[['top','right']].set_visible(False)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    fig.suptitle('Koszul homology: which relations remain after removing boundaries?',fontsize=14)
    fig.legend(handles=[Patch(color='#5a819c',label='Koszul boundaries'),Patch(color='#b5783c',label='H1 quotient')],loc='outside lower center',ncol=2,frameon=False)
    fig.savefig(OUT/'koszul-homology.png',dpi=180);fig.savefig(OUT/'koszul-homology.svg',metadata={'Date':None});plt.close(fig)
    p=OUT/'koszul-homology.svg';p.write_text('\n'.join(l.rstrip() for l in p.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')


def run(check=False):
    OUT.mkdir(parents=True,exist_ok=True);d=data();p=OUT/'data.json'
    if check:assert json.loads(p.read_text(encoding='utf-8'))==d
    else:p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8');figure(d)
    report={'status':'PASS','complexes':d['checked_complexes'],'degrees':[2,3,4,5,6],
        'd_squared_zero_columns':sum(r[b]['zero_compositions_checked'] for r in d['records'] for b in ['raw','adapted']),
        'basis_invariance':True,'scope':d['scope']}
    (OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
    print([(r['case'],r['adapted']['degree'],r['adapted']['kernel_d1'],r['adapted']['boundaries_d2'],r['adapted']['homology'][1]) for r in d['records']])


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');run(p.parse_args().check)
