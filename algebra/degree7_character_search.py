"""Complete E2 tests within single-character degree-seven denominator families.

The restriction is on D. For each such family, projecting N to its required
character retains all possible solutions with that D. Every nonzero D chart
is tested with exact affine and square-zero consequences. Failed propagation
is recorded as unresolved, never as existence or nonexistence.
"""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations_with_replacement
import argparse, copy, gzip, hashlib, json, time
import degree6_e1 as base
from degree6_e2_model import modF
from degree6_quadratic_structure import B
import degree7_e1 as e1

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'results/degree7-characters'


def encode(p):return [[list(m),str(c)] for m,c in sorted(p.items()) if c]
def decode(p):return {tuple(m):Q(c) for m,c in p if Q(c)}


def product(p,q):
    result={}
    for m,c in p.items():
        for n,d in q.items():
            k=tuple(sorted(m+n));result[k]=result.get(k,0)+c*d
    return {m:c for m,c in result.items() if c}


def substitute(p,maps):
    result={}
    for mon,c in p.items():
        term={():c}
        for i in mon:term=product(term,maps.get(i,{(i,):Q(1)}))
        result=base.padd(result,term)
    return result


def build_system(indices,pairs,fields,field_chars,character):
    assert all({e1.character(m) for m in pairs[i][0]}=={character} for i in indices), 'This constructor requires one denominator character.'
    Achar=e1.character(next(iter(base.A)))
    needed=tuple((a+d)%6 for a,d in zip(Achar,character))
    correction_ids=[k for k,c in enumerate(field_chars) if c==needed]
    nD=len(indices);equations={}
    def append(physical,parameter):
        for m,c in modF(physical).items():
            row=equations.setdefault(m,{})
            row[parameter]=row.get(parameter,0)+c
    for i,j in combinations_with_replacement(range(nD),2):
        D,N=pairs[indices[i]];E,P=pairs[indices[j]]
        value=B(D,P)
        if i!=j:value=base.padd(value,B(E,N))
        append(value,(i,j))
    for i,index in enumerate(indices):
        for k,original in enumerate(correction_ids):append(B(pairs[index][0],fields[original]),(i,nD+k))
    equations={m:{v:c for v,c in row.items() if c} for m,row in equations.items()}
    equations={m:row for m,row in equations.items() if row}
    physical=sorted(equations)
    return [equations[m] for m in physical],physical,correction_ids


def reduce_span(polynomials):
    monomials=sorted({m for p in polynomials for m in p},key=lambda m:(-len(m),m))
    lookup={m:i for i,m in enumerate(monomials)};span=base.Elimination()
    for i,p in enumerate(polynomials):span.insert({lookup[m]:c for m,c in p.items()},{i:Q(1)})
    def witness(p):
        if any(m not in lookup for m in p):return None
        v={lookup[m]:c for m,c in p.items()};coeff={}
        while v:
            pivot=min(v)
            if pivot not in span.basis:return None
            c=v[pivot];row,comb=span.basis[pivot]
            v=base.padd(v,row,-c);coeff=base.padd(coeff,comb,c)
        return {'polynomial':encode(p),'equation_weights':[[i,str(c)] for i,c in sorted(coeff.items())]}
    linear=[{monomials[k]:c for k,c in row.items()}
            for pivot,(row,_) in sorted(span.basis.items()) if len(monomials[pivot])==1]
    return witness,linear,len(span.basis)


def prove_chart(equations,nvars,pivot):
    maps={i:({():Q(1)} if i==pivot else {(i,):Q(1)}) for i in range(nvars)}
    active=set(range(nvars))-{pivot};stages=[];excluded=False
    for iteration in range(nvars+2):
        rows=[substitute(p,maps) for p in equations]
        witness,linears,rank=reduce_span(rows)
        constant=witness({():Q(1)})
        stage={'active':sorted(active),'rank':rank,'inferences':[],'changes':{}}
        if constant:
            stage['inferences'].append({'kind':'contradiction','witness':constant});excluded=True
        else:
            changes={}
            for poly in reversed(linears):
                stage['inferences'].append({'kind':'linear','witness':witness(poly)})
                reduced=substitute(poly,changes);i=min(m[0] for m in reduced if m)
                changes[i]={m:-c/reduced[(i,)] for m,c in reduced.items() if m!=(i,)}
            for i in sorted(active-set(changes)):
                square=witness({(i,i):Q(1)})
                if square:
                    stage['inferences'].append({'kind':'square','coordinate':i,'witness':square})
                    changes[i]={}
            for i in sorted(changes,reverse=True):
                changes[i]=substitute(changes[i],{j:p for j,p in changes.items() if i!=j})
            assert all(all(i in active-set(changes) for i in m) for p in changes.values() for m in p)
            stage['changes']={str(i):encode(p) for i,p in sorted(changes.items())}
        stages.append(stage)
        if excluded or not stage['changes']:break
        maps={i:substitute(p,changes) for i,p in maps.items()};active-=set(changes)
    return {'pivot':pivot,'excluded':excluded,'stages':stages,'remaining_variables':len(active)}


def ideal_certificate(equations,nvars,proof,max_degree=3):
    maps={i:({():Q(1)} if i==proof['pivot'] else {(i,):Q(1)}) for i in range(nvars)}
    for stage in proof['stages']:
        changes={int(i):decode(p) for i,p in stage['changes'].items()}
        maps={i:substitute(p,changes) for i,p in maps.items()}
    rows=[substitute(p,maps) for p in equations]
    active=sorted({i for p in rows for m in p for i in m})
    for degree in range(3,max_degree+1):
        multiplied=[];labels=[]
        for index,p in enumerate(rows):
            if not p:continue
            for size in range(degree-max(map(len,p))+1):
                for mon in combinations_with_replacement(active,size):
                    multiplied.append(product(p,{mon:Q(1)}));labels.append((index,mon))
        witness,_,rank=reduce_span(multiplied)
        constant=witness({():Q(1)})
        if constant:
            terms=[[labels[i][0],list(labels[i][1]),c] for i,c in constant['equation_weights']]
            return {'degree_bound':degree,'matrix_rows':len(multiplied),'matrix_rank':rank,'products':terms}
    return None


def verify_chart(equations,nvars,proof):
    """Replay original-row combinations; do not trust the generator's ranks."""
    pivot=proof['pivot'];assert 0<=pivot<nvars
    maps={i:({():Q(1)} if i==pivot else {(i,):Q(1)}) for i in range(nvars)}
    active=set(range(nvars))-{pivot};excluded=False;count=0
    for stage in proof['stages']:
        assert not excluded and stage['active']==sorted(active)
        relations=[]
        for item in stage['inferences']:
            claim=decode(item['witness']['polynomial']);actual={}
            for index,c in item['witness']['equation_weights']:
                assert 0<=index<len(equations)
                actual=base.padd(actual,equations[index],Q(c))
            assert substitute(actual,maps)==claim
            count+=1
            if item['kind']=='contradiction':assert claim=={():Q(1)};excluded=True
            elif item['kind']=='square':
                i=item['coordinate'];assert i in active and claim=={(i,i):Q(1)}
                relations.append({(i,):Q(1)})
            else:
                assert item['kind']=='linear' and all(len(m)<=1 for m in claim)
                relations.append(claim)
        if excluded:
            assert not stage['changes'];continue
        changes={int(i):decode(p) for i,p in stage['changes'].items()}
        assert set(changes)<=active
        # Prove each proposed substitution follows from the verified linear
        # relations (including the field implication x^2=0 => x=0).
        constant_id=nvars;basis={}
        for relation in relations:
            v={(m[0] if m else constant_id):c for m,c in relation.items()}
            while v:
                i=min(v);c=v[i]
                if i not in basis:basis[i]={j:d/c for j,d in v.items()};break
                v=base.padd(v,basis[i],-c)
        assert constant_id not in basis
        for i,p in changes.items():
            assert all(len(m)<=1 and all(j in active-set(changes) for j in m) for m in p)
            rel=base.padd({(i,):Q(1)},p,-1)
            v={(m[0] if m else constant_id):c for m,c in rel.items()}
            while v:
                j=min(v);assert j in basis
                v=base.padd(v,basis[j],-v[j])
        maps={i:substitute(p,changes) for i,p in maps.items()};active-=set(changes)
    if proof.get('ideal_contradiction'):
        assert not excluded
        actual={}
        for index,mon,c in proof['ideal_contradiction']['products']:
            assert 0<=index<len(equations) and all(i in active for i in mon)
            term=product(substitute(equations[index],maps),{tuple(mon):Q(c)})
            assert all(len(m)<=proof['ideal_contradiction']['degree_bound'] for m in term)
            actual=base.padd(actual,term)
        assert actual=={():Q(1)};excluded=True;count+=1
    assert excluded==proof['excluded'] and len(active)==proof['remaining_variables']
    return count


def run():
    start=time.perf_counter();data,pairs=e1.load();fields,labels=e1.koszul_fields()
    field_chars=[]
    for K in fields:
        chars=e1.field_characters(K);assert len(chars)==1;field_chars.append(chars.pop())
    families=[];details=[]
    for family in data['character_families']:
        indices=family['basis_indices'];char=tuple(family['character'])
        equations,physical,corrections=build_system(indices,pairs,fields,field_chars,char)
        nvars=len(indices)+len(corrections)
        proofs=[prove_chart(equations,nvars,pivot) for pivot in range(len(indices))]
        for proof in proofs:
            if not proof['excluded']:
                certificate=ideal_certificate(equations,nvars,proof)
                if certificate:proof['ideal_contradiction']=certificate;proof['excluded']=True
        for proof in proofs:verify_chart(equations,nvars,proof)
        row={'character':list(char),'denominator_basis_indices':indices,'Koszul_indices':corrections,
             'equation_count':len(equations),'variable_count':nvars,
             'excluded_pivots':[p['pivot'] for p in proofs if p['excluded']],
             'unresolved_pivots':[p['pivot'] for p in proofs if not p['excluded']]}
        families.append(row);details.append({**row,'physical_monomials':[list(m) for m in physical],
            'equations':[encode(p) for p in equations],'charts':proofs})
        print('Family',len(families),char,'D',len(indices),'K',len(corrections),
              'excluded charts',len(row['excluded_pivots']),'/',len(indices),flush=True)
    OUT.mkdir(parents=True,exist_ok=True)
    packet={'basis_sha256':hashlib.sha256(e1.BASIS.read_bytes()).hexdigest(),'families':details}
    with gzip.open(OUT/'certificates.json.gz','wt',encoding='utf-8') as f:json.dump(packet,f,separators=(',',':'))
    report={'degree':7,'basis_sha256':packet['basis_sha256'],'character_families':len(families),
        'fully_excluded_families':sum(not r['unresolved_pivots'] for r in families),
        'excluded_charts':sum(len(r['excluded_pivots']) for r in families),
        'unresolved_charts':sum(len(r['unresolved_pivots']) for r in families),
        'total_charts':sum(len(r['denominator_basis_indices']) for r in families),'families':families,
        'seconds':time.perf_counter()-start,
        'scope':'Only denominators in one diagonal-character eigenspace, modulo the full F*S1 gauge. Every numerator correction for that restricted family is retained by character projection. Mixed-character denominators remain untested here. No unrestricted degree-seven exclusion or Hodge solve.'}
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='families'},indent=2),flush=True)


def check():
    data,pairs=e1.load();fields,_=e1.koszul_fields()
    field_chars=[next(iter(e1.field_characters(K))) for K in fields]
    with gzip.open(OUT/'certificates.json.gz','rt') as f:packet=json.load(f)
    assert packet['basis_sha256']==hashlib.sha256(e1.BASIS.read_bytes()).hexdigest()
    assert len(packet['families'])==len(data['character_families'])
    charts=inferences=0;broken_tested=False
    for expected,family in zip(data['character_families'],packet['families']):
        assert expected['character']==family['character'] and expected['basis_indices']==family['denominator_basis_indices']
        eq,physical,corrections=build_system(expected['basis_indices'],pairs,fields,field_chars,tuple(expected['character']))
        assert [encode(p) for p in eq]==family['equations']
        assert [list(m) for m in physical]==family['physical_monomials'] and corrections==family['Koszul_indices']
        nvars=len(expected['basis_indices'])+len(corrections)
        assert [p['pivot'] for p in family['charts']]==list(range(len(expected['basis_indices'])))
        assert family['excluded_pivots']==[p['pivot'] for p in family['charts'] if p['excluded']]
        assert family['unresolved_pivots']==[p['pivot'] for p in family['charts'] if not p['excluded']]
        for proof in family['charts']:
            inferences+=verify_chart(eq,nvars,proof);charts+=1
            if not broken_tested and proof['excluded']:
                broken=copy.deepcopy(proof)
                item=next(i for s in broken['stages'] for i in s['inferences'])
                item['witness']['equation_weights']=[[j,str(2*Q(c))] for j,c in item['witness']['equation_weights']]
                try:verify_chart(eq,nvars,broken)
                except AssertionError:broken_tested=True
                else:raise AssertionError('Corrupted proof was accepted')
    assert broken_tested
    report=json.loads((OUT/'report.json').read_text())
    assert report['basis_sha256']==packet['basis_sha256']
    for field in ['character','denominator_basis_indices','Koszul_indices','equation_count','variable_count','excluded_pivots','unresolved_pivots']:
        assert [r[field] for r in report['families']]==[r[field] for r in packet['families']]
    assert report['character_families']==len(packet['families'])
    assert report['fully_excluded_families']==sum(not r['unresolved_pivots'] for r in packet['families'])
    assert report['excluded_charts']==sum(len(r['excluded_pivots']) for r in packet['families'])
    assert report['unresolved_charts']==sum(len(r['unresolved_pivots']) for r in packet['families'])
    assert report['total_charts']==charts
    print(json.dumps({'rebuilt_families':len(packet['families']),'charts_checked':charts,
        'exact_inferences_checked':inferences,'corrupted_witness_rejected':True}),flush=True)


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true')
    if parser.parse_args().check:check()
    else:run()
