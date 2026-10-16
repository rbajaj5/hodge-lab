"""Reconstruct the full degree-seven E1 space and its six F*S1 gauges.

The dimensions 295, 289 and 840 were reported by fqlx in Discussion 44.
This independently adapts this repository's degree-six elimination; E1 is
only preprocessing and does not imply the second certificate equation.
"""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations
import argparse, hashlib, json, time
import degree6_e1 as base

HERE=Path(__file__).resolve().parent
BASIS=HERE/'degree7_e1_basis.json'
REPORT=HERE/'degree7_e1_report.json'
WEIGHTS=((0,0,1,1,5,0),(0,1,0,2,3,0),(1,0,0,3,0,0))


def character(exponent):
    return tuple(sum(w*x for w,x in zip(row,exponent))%6 for row in WEIGHTS)


def field_characters(field):
    weights=set()
    for i,p in enumerate(field):
        coordinate=tuple(row[i] for row in WEIGHTS)
        for m in p:weights.add(tuple((a-b)%6 for a,b in zip(character(m),coordinate)))
    return weights


def decode(p):return {tuple(m):Q(c) for c,m in p}


def koszul_fields():
    fields=[];labels=[]
    for i,j in combinations(range(6),2):
        for m in base.mons(3):
            K=[{} for _ in range(6)]
            K[i]=base.pmul({m:Q(1)},base.DF[j])
            K[j]={v:-c for v,c in base.pmul({m:Q(1)},base.DF[i]).items()}
            fields.append(K);labels.append([i,j,list(m)])
    return fields,labels


def directional(field):
    out={}
    for i,N in enumerate(field):out=base.padd(out,base.pmul(N,base.DF[i]))
    return out


def span_coordinates(v,span):
    v=dict(v);answer={}
    while v:
        p=min(v);c=v[p];row,track=span.basis[p]
        v=base.padd(v,row,-c);answer=base.padd(answer,track,c)
    return answer


def run(check=False):
    start=time.perf_counter();rows={m:i for i,m in enumerate(base.mons(13))}
    span=base.Elimination();labels=[];pairs=[];nullity=0
    for i in range(6):
        for m in base.mons(8):
            index=len(labels);labels.append(('N',i,m))
            col={rows[base.expadd(m,v)]:Q(c) for v,c in base.DF[i].items()}
            if span.insert(col,{index:Q(1)}) is not None:nullity+=1
    rank=len(span.basis);nN=len(labels)
    for m in base.mons(7):
        index=len(labels);labels.append(('D',m))
        col={rows[base.expadd(m,v)]:Q(c) for v,c in base.A.items()}
        null=span.insert(col,{index:Q(1)})
        if null is None:continue
        D={};N=[{} for _ in range(6)]
        for j,c in null.items():
            label=labels[j]
            if label[0]=='D':D[label[1]]=c
            else:N[label[1]][label[2]]=-c
        assert D and directional(N)==base.pmul(base.A,D)
        pairs.append((D,N))
    assert (nN,rank,nullity,len(pairs),len(span.basis))==(7722,6882,840,295,7379)
    mon8={m:i for i,m in enumerate(base.mons(8))};ks=base.Elimination()
    fields,labelsK=koszul_fields()
    for K in fields:
        assert not directional(K)
        ks.insert({i*len(mon8)+mon8[m]:c for i,p in enumerate(K) for m,c in p.items()})
    assert len(fields)==len(ks.basis)==840
    mon7={m:i for i,m in enumerate(base.mons(7))};ds=base.Elimination()
    for i,(D,_) in enumerate(pairs):ds.insert({mon7[m]:c for m,c in D.items()},{i:Q(1)})
    assert len(ds.basis)==295
    gauges=[];gspan=base.Elimination()
    for coordinate in range(6):
        unit=tuple(int(i==coordinate) for i in range(6))
        Fh=base.pmul(base.F,{unit:Q(1)})
        a=span_coordinates({mon7[m]:c for m,c in Fh.items()},ds)
        reconstructed={}
        for i,c in a.items():reconstructed=base.padd(reconstructed,pairs[i][0],c)
        assert reconstructed==Fh
        gspan.insert(dict(a));gauges.append({'coordinate':coordinate,'basis_coordinates':[[i,str(c)] for i,c in sorted(a.items())]})
    dropped=sorted(gspan.basis);retained=sorted(set(range(295))-set(dropped))
    assert len(dropped)==6 and len(retained)==289
    Achar=character(next(iter(base.A)));groups={}
    for i,(D,N) in enumerate(pairs):
        chars={character(m) for m in D};assert len(chars)==1
        char=chars.pop();expected=tuple((x+y)%6 for x,y in zip(char,Achar))
        assert field_characters(N)=={expected}
        if i in retained:groups.setdefault(char,[]).append(i)
    result={'degree':7,'F':base.poly_json(base.F),'A':base.poly_json(base.A),
        'basis':[{'D':base.poly_json(D),'N':[base.poly_json(p) for p in N]} for D,N in pairs],
        'gauge_vectors':gauges,'dropped_basis_indices':dropped,'retained_basis_indices':retained,
        'character_generators':[list(w) for w in WEIGHTS],
        'character_families':[{'character':list(c),'basis_indices':v} for c,v in sorted(groups.items())],
        'koszul_labels':labelsK}
    encoded=(json.dumps(result,separators=(',',':'))+'\n').encode('utf-8')
    if check:assert BASIS.read_bytes()==encoded,'Stored degree-seven basis differs from exact reconstruction.'
    else:BASIS.write_bytes(encoded)
    report={'numerator_columns':nN,'numerator_rank':rank,'numerator_kernel_dimension':nullity,
        'augmented_rank':len(span.basis),'denominator_columns':len(mon7),'denominator_dimension':len(pairs),
        'F_times_linear_gauge_dimension':6,'denominator_dimension_mod_gauge':289,
        'Koszul_dimension_verified':len(ks.basis),'all_E1_lifts_checked':True,
        'retained_character_families':len(groups),'maximum_family_dimension':max(map(len,groups.values())),
        'basis_sha256':hashlib.sha256(BASIS.read_bytes()).hexdigest(),'seconds':time.perf_counter()-start,
        'prior_work':'fqlx, Discussion 44 and pinned gist 4d7b74cea96f656c63dd30f291147b56 at 9afdfe668c9a967e9b8c7d9bc9ce8750a76e62a5. These dimensions are reproduced, not new.',
        'scope':'Complete exact E1 only; no E2 solution or degree-seven exclusion.'}
    if not check:REPORT.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2),flush=True)


def load():
    data=json.loads(BASIS.read_text())
    pairs=[(decode(p['D']),[decode(n) for n in p['N']]) for p in data['basis']]
    return data,pairs


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true')
    run(parser.parse_args().check)
