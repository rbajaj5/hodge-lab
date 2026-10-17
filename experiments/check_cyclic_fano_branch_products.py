#!/usr/bin/env python3
"""Independent exact audit of bounded powers/products of the branch guesses.

Uses only arithmetic and raw-source parsing from the previous independent
checker. Remainder duals are pulled back by a separately implemented monic
division recurrence, so every raw Koszul and quotient column can be audited
without constructing a large coefficient matrix.
"""
from pathlib import Path
from functools import lru_cache
from fractions import Fraction as Q
from itertools import combinations
import argparse
import json
import check_cyclic_fano_guided_denominators as A

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/cyclic-fano-branch-products'
SOURCE=ROOT/'results/cyclic-fano-curve'
INPUT=ROOT/'results/cyclic-fano-higher-unfolding/candidates.json'
W=A.WEIGHTS;ZMON=(0,)*6;ZERO,ONE=A.ZERO,A.ONE
ca,cn,cm=A.ca,A.cn,A.cm
add,mul,scale=A.add,A.mul,A.scale
derivative,monomials=A.derivative,A.monomials
SPECS=[('T2',(2,0,0,0,0)),('T4',(4,0,0,0,0)),('T8',(8,0,0,0,0)),
       ('C2',(0,2,0,0,0)),('C3',(0,3,0,0,0)),('S2',(0,0,2,0,0)),
       ('TC',(1,1,0,0,0)),('TS',(1,0,1,0,0)),('CS',(0,1,1,0,0)),
       ('RC',(0,1,0,1,0)),('RS',(0,0,1,1,0)),('R4',(0,0,0,4,0)),
       ('J2',(0,0,0,0,2)),('J3',(0,0,0,0,3)),('J4',(0,0,0,0,4)),
       ('JT2',(2,0,0,0,1)),('JTC',(1,1,0,0,1)),('JC2',(0,2,0,0,1)),
       ('JS',(0,0,1,0,1)),('JR2',(0,0,0,2,1)),('JTS',(1,0,1,0,1)),
       ('J2T2',(2,0,0,0,2)),('J2C2',(0,2,0,0,2)),
       ('J2R',(0,0,0,1,2)),('J3T',(1,0,0,0,3)),('J2S',(0,0,1,0,2))]

def shifted(mon,offset):return tuple(x+y for x,y in zip(mon,offset))
def product_data(G):
    old=A.candidate_data(G)
    factors=[old[name][1]for name in ('full-tangent-linear','Y0-center-cubic','Y0-leading-branch-sextic','tangent_norm_power_1')]+[derivative(G,2)]
    assert all(f and all(m[2]==0 for m in f)for f in factors[:4])
    assert factors[4]and all(m[2]<=1 for m in factors[4])
    result={}
    for name,exponents in SPECS:
        E={ZMON:ONE};cofactor={ZMON:ONE}
        for i,(f,n)in enumerate(zip(factors,exponents)):
            E=mul(E,A.power(f,n));cofactor=mul(cofactor,A.power(f,n-int(i==4 and n>0)))
        degree=sum(a*b for a,b in zip(exponents,(1,3,6,2,3)))
        result[name]=(exponents,degree,E,cofactor if exponents[4]else None)
    return result

def check_candidate(candidate,data):
    name=candidate['id'];exponents,d,E,K=data[name]
    assert candidate['factor_order']==['T','C','S','R','J']and candidate['exponents']==list(exponents)
    assert candidate['degree']==d and A.decode(candidate['denominator'])==E
    assert (candidate['jacobian_cofactor']is None)==(K is None)
    if K is not None:assert A.decode(candidate['jacobian_cofactor'])==K
    assert E and all(sum(w*x for w,x in zip(W,m))==d for m in E)
    return exponents,d,E,K

def remainder_functional(G,dual):
    """Pull a dual on canonical Z-degree<2 rows back to raw monomials."""
    leading=(0,0,2,0,0,0)
    assert G[leading]==ONE and all(m[2]<=2 for m in G)
    tail=[(m,c)for m,c in G.items()if m!=leading]
    assert all(m[2]<2 for m,c in tail)
    assert dual and all(m[2]<2 for m in dual)
    support=list(dual)
    @lru_cache(maxsize=None)
    def value(m):
        # Monic reduction only increases the five ordinary exponents.
        if not any(all(m[i]<=row[i]for i in (0,1,3,4,5))for row in support):return ZERO
        if m[2]<2:return dual.get(m,ZERO)
        lower=list(m);lower[2]-=2;answer=ZERO
        for term,c in tail:answer=ca(answer,cn(cm(c,value(shifted(lower,term)))))
        return answer
    return value

def polynomial_pair(value,poly,offset=ZMON):
    answer=ZERO
    for m,c in poly.items():answer=ca(answer,cm(c,value(shifted(m,offset))))
    return answer

def decode5(terms):
    out={}
    for term in terms:
        m=tuple(term['powers']);c=tuple(map(Q,term['coefficient']))
        assert len(m)==5 and all(type(k)is int and k>=0 for k in m)
        assert len(c)==2 and c!=ZERO and m not in out;out[m]=c
    return out

def power5(poly,n):return A.I.power(poly,n,(0,)*5)
def drop_z(poly):
    assert all(m[2]==0 for m in poly)
    return {m[:2]+m[3:]:c for m,c in poly.items()}

def compact_data(exponents,E,G,beta,data):
    """Derive the reflection-reduced first-order operators independently."""
    a=exponents[4];assert a>=1
    eps=a%2;half=a//2;ceil=(a+1)//2
    Qpoly={m[:2]+m[3:]:c for m,c in G.items()if m[2]==1}
    H=drop_z({m:c for m,c in G.items()if m[2]==0})
    Delta=add(mul(Qpoly,Qpoly),scale(H,(Q(-4),Q(0))))
    assert Delta and all(sum(m)==6 for m in Delta)
    beta5=drop_z(beta);factors=A.candidate_data(G)
    K={(0,)*5:ONE}
    for index,name in enumerate(('full-tangent-linear','Y0-center-cubic','Y0-leading-branch-sextic','tangent_norm_power_1')):
        K=mul(K,power5(drop_z(factors[name][1]),exponents[index]))
    degreeK=sum(n*w for n,w in zip(exponents[:4],(1,3,6,2)))
    assert all(sum(m)==degreeK for m in K)
    embedK={m[:2]+(0,)+m[2:]:c for m,c in K.items()}
    assert E==mul(A.power(derivative(G,2),a),embedK)
    d=3*a+degreeK
    ordinary_degree=d-6-3*eps;mixed_degree=d-7+3*eps
    rhs=scale(mul(mul(beta5,power5(Delta,ceil-1)),mul(K,K)),(Q(2),Q(0)))
    delta_derivatives=[derivative(Delta,i)for i in range(5)]
    k_derivatives=[derivative(K,i)for i in range(5)]
    # Before dividing Delta^half, the ordinary-pair operator is multiplied
    # by t^(a+eps), and the mixed derivative/zeroth terms by
    # t^(a+2-eps) and t^(a-eps). These parity identities certify the
    # known common factor; no division by a parameter or polynomial value.
    assert (a+eps)//2-half==eps and (a+2-eps)//2-half==1
    assert (a-eps)//2-half==0 and a-1-half==ceil-1
    pair_operators=[]
    for i,j in combinations(range(5),2):
        base=mul(power5(Delta,eps),add(mul(delta_derivatives[j],k_derivatives[i]),scale(mul(delta_derivatives[i],k_derivatives[j]),cn(ONE))))
        lead_i=scale(mul(mul(power5(Delta,eps),K),delta_derivatives[j]),cn(ONE))
        lead_j=mul(mul(power5(Delta,eps),K),delta_derivatives[i])
        pair_operators.append((i,j,base,lead_i,lead_j))
    mixed=[]
    for i in range(5):
        base=add(scale(mul(Delta,k_derivatives[i]),(Q(-2),Q(0))),
                 scale(mul(K,delta_derivatives[i]),(Q(1-eps-a),Q(0))))
        leading=scale(mul(Delta,K),(Q(2),Q(0)))
        mixed.append((i,base,leading))
    pure=not any(exponents[:4])
    if pure:
        assert K=={(0,)*5:ONE}
        c=2*ceil-1;assert 1-eps-a==-c
        assert mixed_degree==6*ceil-7
        # Exact first-order operator identity:
        # sum L_l(curl_ij(f)_l) = -c*(Delta_i*f_j-Delta_j*f_i).
        # Cross second derivatives cancel; W_ij(Delta)=0. Thus ordinary
        # directions are redundant at the prescribed homogeneous degrees.
        for i,j in combinations(range(5),2):
            assert add(mul(delta_derivatives[i],delta_derivatives[j]),scale(mul(delta_derivatives[j],delta_derivatives[i]),cn(ONE)))=={}
    return {'a':a,'epsilon':eps,'degreeK':degreeK,'d':d,'Delta':Delta,'K':K,'rhs':rhs,
            'beta':beta5,
            'row_degree':2*degreeK+6*ceil-2,'ordinary_degree':ordinary_degree,'mixed_degree':mixed_degree,
            'pair_operators':pair_operators,'mixed_operators':mixed,'pure_J':pure,
            'cancelled_Delta_power':half,'rhs_Delta_power':ceil-1}

def compact_physical_operator_checks(compact):
    """Check every coefficient of each first-order multiplier operator.

    Both sides are first order in h, so equality on1 and the relevant linear
    coordinates identifies their complete operator, not only a degree slice.
    """
    Delta=compact['Delta'];K=compact['K'];a=compact['a'];eps=compact['epsilon']
    def lift(poly,t_power=0):return {m+(t_power,):c for m,c in poly.items()}
    delta_powers={n:power5(Delta,n)for n in range(a+2)}
    def reduce_even(poly):
        out={}
        for mon,c in poly.items():
            assert mon[5]%2==0
            for m,v in delta_powers[mon[5]//2].items():
                key=shifted(m,mon[:5]);out[key]=ca(out.get(key,ZERO),cm(c,v))
        return {m:c for m,c in out.items()if c!=ZERO}
    g=add({(0,0,0,0,0,2):ONE},scale(lift(Delta),cn(ONE)))
    E=lift(K,a);grad=[derivative(g,i)for i in range(6)]
    common=delta_powers[compact['cancelled_Delta_power']]
    particular=[{}for _ in range(6)]
    particular[5]=scale(lift(mul(compact['beta'],K),a-1),(Q(2),Q(0)))
    assert A.contraction(particular,g)==scale(mul(lift(compact['beta']),E),(Q(4),Q(0)))
    assert reduce_even(scale(A.B(E,particular),cn(ONE)))==mul(common,compact['rhs'])
    checks=0
    for i,j,base,lead_i,lead_j in compact['pair_operators']:
        for coordinate in (None,i,j):
            mon=tuple(int(k==coordinate)for k in range(5));h={mon:ONE}
            H=lift(h,eps);field=[{}for _ in range(6)]
            field[i]=mul(H,grad[j]);field[j]=scale(mul(H,grad[i]),cn(ONE))
            expected=mul(h,base)
            if coordinate==i:expected=add(expected,lead_i)
            if coordinate==j:expected=add(expected,lead_j)
            assert A.contraction(field,g)=={}
            assert reduce_even(A.B(E,field))==mul(common,expected);checks+=1
    for i,base,leading in compact['mixed_operators']:
        for coordinate in (None,i):
            mon=tuple(int(k==coordinate)for k in range(5));h={mon:ONE}
            H=lift(h,1-eps);field=[{}for _ in range(6)]
            field[i]=mul(H,grad[5]);field[5]=scale(mul(H,grad[i]),cn(ONE))
            expected=mul(h,base)
            if coordinate==i:expected=add(expected,leading)
            assert A.contraction(field,g)=={}
            assert reduce_even(A.B(E,field))==mul(common,expected);checks+=1
    assert checks==40
    return checks

def compact_columns_check(dual,compact,omit_ordinary):
    value=lambda m:dual.get(m,ZERO);checked=0
    if not omit_ordinary:
        for i,j,base,lead_i,lead_j in compact['pair_operators']:
            for m in monomials(compact['ordinary_degree'],(1,)*5):
                answer=polynomial_pair(value,base,m)
                if m[i]:
                    n=list(m);n[i]-=1
                    answer=ca(answer,cm((Q(m[i]),Q(0)),polynomial_pair(value,lead_i,n)))
                if m[j]:
                    n=list(m);n[j]-=1
                    answer=ca(answer,cm((Q(m[j]),Q(0)),polynomial_pair(value,lead_j,n)))
                assert answer==ZERO;checked+=1
    else:assert compact['pure_J']
    for i,base,leading in compact['mixed_operators']:
        for m in monomials(compact['mixed_degree'],(1,)*5):
            answer=polynomial_pair(value,base,m)
            if m[i]:
                n=list(m);n[i]-=1
                answer=ca(answer,cm((Q(m[i]),Q(0)),polynomial_pair(value,leading,n)))
            assert answer==ZERO;checked+=1
    assert polynomial_pair(value,compact['rhs'],(0,)*5)==ONE
    return checked

def check_compact_metadata(metadata,candidate,compact,normal_count,koszul_count,quotient_count):
    assert metadata['schema']=='cyclic-fano-branch-compact-system-v1'
    assert metadata['helper_sha256']==A.I.sha(ROOT/'experiments/cyclic_fano_branch_compact.py')
    assert metadata['candidate_input_sha256']==A.I.sha(INPUT)
    expected={'a':compact['a'],'epsilon':compact['epsilon'],'k':compact['degreeK'],'d':compact['d'],
              'base_base_multiplier_degree':compact['ordinary_degree'],'base_t_multiplier_degree':compact['mixed_degree'],
              'coefficient_degree':compact['row_degree'],'ambient_5var_rows':len(monomials(compact['row_degree'],(1,)*5)),
              'raw_Koszul_coefficients':koszul_count,'raw_E2_quotient_coefficients':quotient_count,
              'cancelled_Delta_power':compact['cancelled_Delta_power']}
    for key,value in expected.items():assert metadata[key]==value,(key,metadata[key],value)
    assert metadata['variables']==['X0','X1','Y0','Y1','Y2']
    for key in ('quotient_eliminated_exactly','reflection_projection_complete','Koszul_coefficients_reduced_modulo_g'):
        assert metadata[key]is True
    assert metadata['pure_J_pair_shortcut']==compact['pure_J']
    base_count=0 if compact['pure_J']else 10*len(monomials(compact['ordinary_degree'],(1,)*5))
    mixed_count=5*len(monomials(compact['mixed_degree'],(1,)*5))
    assert metadata['base_base_columns']==base_count and metadata['base_t_columns']==mixed_count
    assert metadata['columns']==base_count+mixed_count
    paired=[2*((compact['a']+1)//2)-1,2*((compact['a']+1)//2)]if compact['pure_J']else None
    assert metadata['paired_J_exponents']==paired
    return base_count+mixed_count

def normal_columns_check(value,d,G):
    checked=0
    for i,w in enumerate(W):
        grad=derivative(G,i)
        for m in monomials(d+w-2):
            assert polynomial_pair(value,grad,m)==ZERO;checked+=1
    return checked

def koszul_columns_check(value,d,E,G):
    grad=[derivative(G,i)for i in range(6)]
    ed=[derivative(E,i)for i in range(6)]
    eg=[mul(E,p)for p in grad];checked=0
    for i,j in combinations(range(6),2):
        base=add(mul(grad[i],ed[j]),scale(mul(grad[j],ed[i]),cn(ONE)))
        # The multiplier derivative terms matter; the base Koszul field alone
        # has zero divergence, but a nonconstant multiple generally does not.
        for m in monomials(d+W[i]+W[j]-8):
            answer=polynomial_pair(value,base,m)
            if m[i]:
                lower=list(m);lower[i]-=1
                answer=ca(answer,cm((Q(m[i]),Q(0)),polynomial_pair(value,eg[j],lower)))
            if m[j]:
                lower=list(m);lower[j]-=1
                answer=ca(answer,cn(cm((Q(m[j]),Q(0)),polynomial_pair(value,eg[i],lower))))
            assert answer==ZERO;checked+=1
    return checked

def check_result(path,data,G,beta):
    item=A.I.load(path);candidate=item['candidate'];name=candidate['id']
    exponents,d,E,K=check_candidate(candidate,data)
    assert item['schema']=='cyclic-fano-branch-products-v1'and item['instance']=='cyclic-triple-fano'
    assert item['producer_sha256']==A.I.sha(ROOT/'experiments/cyclic_fano_branch_products.py')
    assert item['dependencies']=={s:A.I.sha(ROOT/'experiments'/s)for s in ('cyclic_fano_guided_denominators.py','cyclic_fano_transfer.py','quadric_contact_pilot.py','cyclic_fano_branch_compact.py')}
    assert item['candidate_input_sha256']==A.I.sha(INPUT)and item['source_instance_sha256']==A.I.sha(SOURCE/'source/instance.rec')
    normal_count=sum(len(monomials(d+w-2))for w in W)
    koszul_count=sum(len(monomials(d+W[i]+W[j]-8))for i,j in combinations(range(6),2))
    quotient_count=len(monomials(2*d-8))
    assert item['full_numerator_dimension']==normal_count and item['complete_Koszul_directions']==koszul_count
    assert item['quotient_dimension_eliminated']==quotient_count and item['exact_rank_claim']is False
    assert item['status']=='excluded','A non-obstruction requires a separate direct witness audit'
    stage=item['obstruction_stage'];compact=None
    dual=decode5(item['dual'])if stage=='E2_reflection_compact'else A.decode(item['dual'])
    if stage=='E2_reflection_compact':
        assert K is not None and item['particular']is None
        compact=compact_data(exponents,E,G,beta,data)
        expected_count=check_compact_metadata(item['compact_metadata'],candidate,compact,normal_count,koszul_count,quotient_count)
        assert all(sum(m)==compact['row_degree']for m in dual)
        count=compact_columns_check(dual,compact,compact['pure_J']);assert count==expected_count
        physical_operator_checks=compact_physical_operator_checks(compact)
        value=lambda m:dual.get(m,ZERO);rhs=compact['rhs']
        quotient_checked=0;cache_size=0
        if 'reused_dual_packet'in item:
            prior=item['reused_dual_packet'];assert name=='J4'and prior['id']=='J3'
            prior_path=OUT/'J3.json';assert A.I.sha(prior_path)==prior['sha256']
            assert A.I.load(prior_path)['dual']==item['dual']
    elif stage=='E1':
        assert item['particular']is None
        assert all(sum(w*x for w,x in zip(W,m))==d+4 for m in dual)
        value=lambda m:dual.get(m,ZERO)
        rhs=mul(beta,E);count=normal_columns_check(value,d,G)
        assert count==normal_count
        quotient_checked=0;cache_size=0
    else:
        assert stage=='E2_mod_G'
        field=[A.decode(p)for p in item['particular']]
        assert len(field)==6 and A.contraction(field,G)==mul(beta,E)
        assert all(sum(w*x for w,x in zip(W,m))==d+W[i]-2 for i,p in enumerate(field)for m in p)
        rhs=scale(A.B(E,field),cn(ONE))
        if K is not None:
            assert field==[{}, {},mul(beta,K),{}, {},{}]
            assert rhs==scale(mul(beta,mul(K,K)),(Q(2),Q(0)))
        assert all(sum(w*x for w,x in zip(W,m))==2*d-2 for m in dual)
        value=remainder_functional(G,dual)
        count=koszul_columns_check(value,d,E,G);assert count==koszul_count
        quotient_checked=0
        for m in monomials(2*d-8):
            assert polynomial_pair(value,G,m)==ZERO;quotient_checked+=1
        assert quotient_checked==quotient_count
        cache_size=value.cache_info().currsize
    assert count==item['stages'][-1]['columns']and polynomial_pair(value,rhs)==ONE
    # Two negative controls: RHS scaling and a changed physical coefficient.
    mutations=A.I.rejects(lambda:A.I.check_equal(polynomial_pair(value,scale(rhs,(Q(2),Q(0)))),ONE))
    changed_row=next(iter(dual))
    mutations+=A.I.rejects(lambda:A.I.check_equal(polynomial_pair(value,{changed_row:ONE}),ZERO))
    receipt={'id':name,'attempt_id':path.stem,'degree':d,'exponents':list(exponents),'packet_lf_sha256':A.I.sha(path),
            'status':'excluded','stage':stage,'physical_columns_checked':count,'quotient_columns_checked':quotient_checked,
            'dual_terms':len(dual),'rhs_pairing':['1','0'],'all_physical_column_pairings_zero':True,
            'remainder_pullback_monomials_cached':cache_size,'negative_controls_rejected':mutations,
            'rank_claim':'No discovery rank or row-count claim is used in this proof audit.'}
    if compact is not None:
        receipt['compact_reduction']={'helper_lf_sha256':item['compact_metadata']['helper_sha256'],
            'a':compact['a'],'epsilon':compact['epsilon'],'row_degree':compact['row_degree'],
            'base_base_multiplier_degree':compact['ordinary_degree'],'base_t_multiplier_degree':compact['mixed_degree'],
            'base_base_columns':item['compact_metadata']['base_base_columns'],'base_t_columns':item['compact_metadata']['base_t_columns'],
            'cancelled_Delta_power':compact['cancelled_Delta_power'],'pure_J_pair_shortcut':compact['pure_J'],
            'raw_Koszul_directions_represented':koszul_count,'raw_quotient_directions_eliminated':quotient_count,
            'first_order_operator_coefficient_checks':physical_operator_checks,
            'argument':'The polynomial coordinate change t=2Z+Q has constant determinant2 and preserves divergence. Reflection averaging selects the required field parity. Reducing Koszul multipliers modulo t^2-Delta leaves E2 unchanged modulo that equation. Each retained E2 term has the common nonzero factor Delta^floor(a/2); cancellation takes place in a polynomial domain. For K=1, ordinary-pair directions lie in the mixed image by the curl identity, so paired exponents2m-1 and2m have identical complete systems.'}
    return receipt

def main():
    assert __debug__,'Run without -O'
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--candidate');args=parser.parse_args()
    F,Apoly,G,beta=A.target();data=product_data(G);checks=[];unresolved=[]
    names=[args.candidate]if args.candidate else list(data)+['raw-'+name for name in data if (OUT/('attempt-raw-'+name+'.json')).exists()]
    assert all(name.removeprefix('raw-')in data for name in names)
    for name in names:
        attempt_path=OUT/('attempt-'+name+'.json');attempt=A.I.load(attempt_path)
        check_candidate(attempt['candidate'],data)
        assert attempt['producer_sha256']==A.I.sha(ROOT/'experiments/cyclic_fano_branch_products.py')
        if attempt['status']=='completed':
            assert attempt['returncode']==0
            checks.append(check_result(OUT/(name+'.json'),data,G,beta))
        else:
            assert attempt['status']in('timeout','error')
            unresolved.append({'id':name,'status':attempt['status'],'attempt_lf_sha256':A.I.sha(attempt_path),
                               'conclusion':'No exclusion or solution follows from an unfinished/error attempt.'})
    result={'schema':'cyclic-fano-branch-products-independent-v1','status':'PASS',
            'checker_lf_sha256':A.I.sha(Path(__file__)),
            'independent_arithmetic_dependencies':{Path(p).name:A.I.sha(Path(p))for p in (A.__file__,A.I.__file__)},
            'source_instance_lf_sha256':A.I.sha(SOURCE/'source/instance.rec'),
            'candidate_input_lf_sha256':A.I.sha(INPUT),'checks':checks,'unresolved':unresolved,
            'admissibility':'For E=J^a*K, the polynomial coordinate t=2Z+Q gives the unique remainder Delta^floor(a/2)*t^(a mod2)*K modulo t^2-Delta. Delta and K are nonzero base polynomials, so this remainder is nonzero; the a=0 case is K itself. Monic division and Z=X2^3 then give a nonzero remainder of X2-degree below6 modulo F. This proves admissibility at every tested degree, without a degree<6 assumption.',
            'quotient_completeness':'Monic Z-division gives a unique remainder with Z-degree<2. B_E(P) has weight2d-2; a vanishing remainder is equivalent to an allowed G quotient of weight2d-8. Raw E2 cases check every raw Koszul and quotient monomial. Compact cases check every column in the complete reflection-reduced five-variable system, whose metadata identifies all represented raw directions.',
            'normalization_and_syzygies':'The prior source-based checker verifies smoothness and the Piola character transformation. Euler normalization and regularity of the six weighted G partials hold at all degrees. Homogeneous syzygies are generated by all H_ij(G_j e_i-G_i e_j), with weight(H_ij)=d+w_i+w_j-8.',
            'negative_controls_rejected':sum(c['negative_controls_rejected']for c in checks),
            'limits':'Only these individually checked finite products are excluded. No universal exponent bound, global support statement, solution certificate or Lean proof is inferred.'}
    if not args.candidate:
        OUT.mkdir(parents=True,exist_ok=True)
        (OUT/'independent-validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':'PASS','checks':len(checks),'unresolved':unresolved,
                      'physical_columns':sum(c['physical_columns_checked']for c in checks),
                      'quotient_columns':sum(c['quotient_columns_checked']for c in checks),
                      'negative_controls':result['negative_controls_rejected']}))

if __name__=='__main__':main()
