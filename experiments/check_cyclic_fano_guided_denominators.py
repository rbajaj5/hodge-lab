#!/usr/bin/env python3
"""Independent source-based replay of fixed guided denominator obstructions.

Only generic Fraction-pair arithmetic from the frozen independent unfolding
checker is reused. No producer construction or external algebra system is
imported. Every allowed numerator/correction and quotient column is rebuilt.
"""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations
import json
import re
import check_cyclic_fano_unfolding as I

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/cyclic-fano-guided-denominators'
SOURCE=ROOT/'results/cyclic-fano-curve'
INPUT=ROOT/'results/cyclic-fano-higher-unfolding/candidates.json'
WEIGHTS=(1,1,3,1,1,1)
ZMON=(0,)*6
ZERO,ONE=I.ZERO,I.ONE
ca,cn,cm=I.ca,I.cn,I.cm
add,mul,scale=I.add,I.multiply,I.scale

def decode(terms):
    out={}
    for term in terms:
        m=tuple(term['powers']);c=tuple(map(Q,term['coefficient']))
        assert len(m)==6 and all(type(k)is int and k>=0 for k in m)
        assert len(c)==2 and c!=ZERO and m not in out
        out[m]=c
    return out

def derivative(poly,i):
    out={}
    for m,c in poly.items():
        if m[i]:
            n=list(m);n[i]-=1;out[tuple(n)]=cm(c,(Q(m[i]),Q(0)))
    return out

def total(polynomials):
    out={}
    for p in polynomials:out=add(out,p)
    return out

def contraction(field,poly):return total(mul(p,derivative(poly,i))for i,p in enumerate(field))
def divergence(field):return total(derivative(p,i)for i,p in enumerate(field))
def B(E,field):return add(mul(E,divergence(field)),scale(contraction(field,E),cn(ONE)))
def power(poly,n):return I.power(poly,n,ZMON)
def monomials(degree,weights=WEIGHTS):
    if degree<0:return []
    if len(weights)==1:return [(degree//weights[0],)]if degree%weights[0]==0 else []
    return [(k,)+m for k in range(degree//weights[0]+1)for m in monomials(degree-k*weights[0],weights[1:])]
def pullback(poly):
    out={}
    for m,c in poly.items():n=list(m);n[2]*=3;out[tuple(n)]=c
    return out
def lift(field):
    delta={(0,0,2,0,0,0):(Q(3),Q(0))}
    return [pullback(p)if i==2 else mul(delta,pullback(p))for i,p in enumerate(field)]
def tagged(poly,tag):return {(tag,)+m:c for m,c in poly.items()}
def pairing(dual,poly):
    ans=ZERO
    for m,c in dual.items():ans=ca(ans,cm(c,poly.get(m,ZERO)))
    return ans
def mod5(poly):
    out={}
    for m,(r,i)in poly.items():
        assert i==0 and r.denominator%5
        v=r.numerator*pow(r.denominator,-1,5)%5
        if v:out[m]=v
    return out

def target():
    values={};key=None
    for line in (SOURCE/'source/instance.rec').read_text(encoding='utf-8').splitlines():
        match=re.match(r'^(q|F|A):\s*(.*)$',line)
        if match:key=match[1];values[key]=match[2]
        elif key and line.startswith('  '):values[key]+=' '+line.strip()
        else:key=None
    assert I.sha(SOURCE/'source/instance.rec')=='d99d10c84d25dc5def72cd7a9a17e5d022e18f562660c8e33bf106675b4a418c'
    assert values==I.load(SOURCE/'target.json')['target']and values['q']=='1'
    F,A=map(I.parse,(values['F'],values['A']));G={};beta={}
    for m,c in F.items():
        assert m[2]%3==0;n=list(m);n[2]//=3;G[tuple(n)]=c
    for m,c in A.items():
        assert m[2]%3==2;n=list(m);n[2]=(n[2]-2)//3;beta[tuple(n)]=cm(c,(Q(1,3),Q(0)))
    assert beta=={(1,0,0,3,0,0):(Q(1,3),Q(0))}
    fermat={tuple(6*int(i==j)for i in range(6)):1 for j in range(6)}
    assert mod5(F)==fermat
    for j in range(6):assert mod5(derivative(F,j))=={tuple(5*int(i==j)for i in range(6)):1}
    assert F==pullback(G)and A==mul({(0,0,2,0,0,0):(Q(3),Q(0))},pullback(beta))
    return F,A,G,beta

def candidate_data(G):
    packet=I.load(INPUT)
    expected={c['id']:(c['degree'],decode(c['quotient_denominator']),None)for c in packet['candidates']}
    assert len(expected)==3
    norm={(0,2,0,0,0,0):ONE,(0,0,0,0,0,2):ONE}
    for k in (1,2,3):expected['tangent_norm_power_'+str(k)]=(2*k,power(norm,k),None)
    for name,source in [('jacobian_tangent','full-tangent-linear'),('jacobian_center_cubic','Y0-center-cubic'),('jacobian_tangent_norm','tangent_norm_power_1')]:
        degree,factor,_=expected[source]
        expected[name]=(degree+3,mul(derivative(G,2),factor),factor)
    assert len(expected)==9
    return expected

def check_packet(path,expected,F,G,beta):
    packet=I.load(path);candidate=packet['candidate'];name=candidate['id']
    assert packet['schema']=='cyclic-fano-guided-denominator-v1'
    assert packet['producer_sha256']==I.sha(ROOT/'experiments/cyclic_fano_guided_denominators.py')
    assert packet['candidate_input_sha256']==I.sha(INPUT)
    assert packet['source_instance_sha256']==I.sha(SOURCE/'source/instance.rec')
    assert set(packet['arithmetic_dependencies'])=={'cyclic_fano_transfer.py','quadric_contact_pilot.py'}
    for filename,digest in packet['arithmetic_dependencies'].items():assert I.sha(ROOT/'experiments'/filename)==digest
    d,E,factor=expected[name]
    assert candidate['degree']==d and decode(candidate['quotient_denominator'])==E
    mode='full_coefficient_basis'if factor is None else 'complete_Koszul'
    assert packet['numerator_parameterization']==mode
    if factor is not None:
        assert candidate['parameterization']==mode and decode(candidate['jacobian_factor'])==factor
        particular=[{}for _ in range(6)];particular[2]=mul(beta,factor)
        assert contraction(particular,G)==mul(beta,E)
        assert all(sum(w*k for w,k in zip(WEIGHTS,m))==d+WEIGHTS[i]-2 for i,p in enumerate(particular)for m in p)
    assert E and all(sum(w*k for w,k in zip(WEIGHTS,m))==d for m in E)
    # Since F is smooth and irreducible, a nonzero D of degree<6 is coprime.
    # At degree6, a Z exponent below2 rules out a scalar multiple of G.
    assert 1<=d<=6 and (d<6 or all(m[2]<2 for m in E))
    euler_checks=0
    for mon in monomials(d-2):
        R={mon:ONE};normalizer=[]
        for i,w in enumerate(WEIGHTS):
            m=list(mon);m[i]+=1
            normalizer.append({tuple(m):(Q(w,6),Q(0))})
        assert contraction(normalizer,G)==mul(R,G)
        assert B(E,normalizer)==mul(E,R)
        euler_checks+=1
    labels=packet['column_labels'];columns=[];keys=[];piola_count=0
    delta={(0,0,2,0,0,0):(Q(3),Q(0))}
    for label in labels:
        mon=tuple(label['powers']);assert all(type(k)is int and k>=0 for k in mon)and len(mon)==6
        if label['kind']=='numerator':
            assert factor is None
            i=label['coordinate'];assert type(i)is int and 0<=i<6
            keys.append(('numerator',i,mon));field=[{}for _ in range(6)];field[i]={mon:ONE}
            normal=contraction(field,G);tangential=B(E,field)
            N=lift(field)
            assert contraction(N,F)==mul(delta,pullback(normal))
            assert divergence(N)==mul(delta,pullback(divergence(field)))
            assert B(pullback(E),N)==mul(delta,pullback(tangential))
            assert all(sum(m)==d+1 for p in N for m in p)
            columns.append({**tagged(normal,'E1'),**tagged(tangential,'E2')});piola_count+=1
        elif label['kind']=='Koszul':
            assert factor is not None
            i,j=label['coordinates'];assert type(i)is int and type(j)is int and 0<=i<j<6
            keys.append(('Koszul',i,j,mon));field=[{}for _ in range(6)]
            field[i]=mul({mon:ONE},derivative(G,j))
            field[j]=scale(mul({mon:ONE},derivative(G,i)),cn(ONE))
            assert not contraction(field,G)
            assert all(sum(w*k for w,k in zip(WEIGHTS,m))==d+WEIGHTS[c]-2 for c,p in enumerate(field)for m in p)
            tangential=B(E,field);N=lift(field)
            assert not contraction(N,F)
            assert divergence(N)==mul(delta,pullback(divergence(field)))
            assert B(pullback(E),N)==mul(delta,pullback(tangential))
            columns.append(tagged(tangential,'E2'));piola_count+=1
        elif label['kind']=='G_quotient':
            keys.append(('G_quotient',mon));columns.append(tagged(scale(mul(G,{mon:ONE}),cn(ONE)),'E2'))
        else:raise AssertionError('Unknown correction label')
    full_count=sum(len(monomials(d+w-2))for w in WEIGHTS)
    if factor is None:
        expected_keys={('numerator',i,m)for i,w in enumerate(WEIGHTS)for m in monomials(d+w-2)}
        rhs=tagged(mul(beta,E),'E1')
    else:
        expected_keys={('Koszul',i,j,m)for i,j in combinations(range(6),2)for m in monomials(d+WEIGHTS[i]+WEIGHTS[j]-8)}
        rhs=tagged(scale(B(E,particular),cn(ONE)),'E2')
    numerator_count=len(expected_keys)
    expected_keys|={('G_quotient',m)for m in monomials(2*d-8)}
    assert set(keys)==expected_keys and len(keys)==len(expected_keys)
    assert packet['numerator_parameters']==numerator_count and packet['full_numerator_coefficients']==full_count
    assert packet['quotient_coefficients']==len(monomials(2*d-8))
    rows=list(map(tuple,packet['coefficient_rows']))
    support=set(rhs)
    for col in columns:support.update(col)
    assert rows==sorted(support)and packet['matrix_shape']==[len(rows),len(columns)]
    assert all(sum(w*k for w,k in zip(WEIGHTS,row[1:]))==(d+4 if row[0]=='E1'else 2*d-2)for row in rows)
    dual={}
    for row,c in packet['obstruction_functional']:
        assert type(row)is int and 0<=row<len(rows)and rows[row]not in dual
        c=tuple(map(Q,c));assert len(c)==2 and c!=ZERO;dual[rows[row]]=c
    assert pairing(dual,rhs)==ONE and all(pairing(dual,col)==ZERO for col in columns)
    assert packet['status']=='excluded'and packet['solution_coefficients']is None and packet['exact_rank_computed']is False
    mutations=0
    mutations+=I.rejects(lambda:I.check_equal(pairing({m:cm((Q(2),Q(0)),c)for m,c in dual.items()},rhs),ONE))
    bad=columns[0].copy();row=next(iter(dual));bad[row]=ca(bad.get(row,ZERO),ONE)
    mutations+=I.rejects(lambda:I.check_equal(pairing(dual,bad),ZERO))
    return {'id':name,'packet_lf_sha256':I.sha(path),'degree':d,'matrix_shape':packet['matrix_shape'],
            'numerator_parameterization':mode,'full_numerator_coefficients':full_count,
            'complete_numerator_or_correction_columns':numerator_count,'quotient_columns':len(monomials(2*d-8)),
            'all_column_pairings_zero':True,'rhs_pairing':['1','0'],'dual_terms':len(dual),
            'physical_dual':[{'equation':r[0],'powers':list(r[1:]),'coefficient':I.strings(c)}for r,c in dual.items()],
            'Piola_basis_checks':piola_count,'Euler_normalization_basis_checks':euler_checks,
            'negative_controls_rejected':mutations}

def main():
    assert __debug__,'Run without -O'
    F,A,G,beta=target();expected=candidate_data(G)
    checks=[check_packet(OUT/(name+'.json'),expected,F,G,beta)for name in expected]
    result={'schema':'cyclic-fano-guided-denominators-independent-v1','status':'PASS',
            'checker_lf_sha256':I.sha(Path(__file__)),
            'independent_arithmetic_dependency_lf_sha256':I.sha(Path(I.__file__)),
            'source_instance_lf_sha256':I.sha(SOURCE/'source/instance.rec'),
            'candidate_input_lf_sha256':I.sha(INPUT),'checks':checks,
            'arithmetic':'Python standard-library Fraction pairs; independent physical columns; no producer or CAS import',
            'source_and_gradient_mod5_Fermat_checked':True,
            'completeness_argument':'Character averaging preserves a certificate at each fixed invariant denominator. Weighted Euler normalization makes P(G)=beta*E exactly. All homogeneous numerator monomials and all G-multiple E2 quotient columns are checked. Smooth Fermat reduction proves F smooth in characteristic zero. Any nonzero common zero of the weighted G partials would lift under Z=X2^3 to a nonzero common zero of the F partials. Thus the weighted partials form a regular sequence; their syzygies are generated by the Koszul fields with homogeneous multiplier weights d+w_i+w_j-8.',
            'negative_controls_rejected':sum(c['negative_controls_rejected']for c in checks),
            'limits':'Only the individually displayed fixed denominators are excluded over C. No exact full matrix ranks, arbitrary-degree exclusion, global support divisor, certificate or Lean proof is claimed.'}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'independent-validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':'PASS','candidates':len(checks),'physical_columns':sum(c['matrix_shape'][1]for c in checks),'negative_controls':result['negative_controls_rejected']}))

if __name__=='__main__':main()
