#!/usr/bin/env python3
"""Complete five-variable E2 system for E=G_Z**a*K, a>0.

Reflection projection and reduction of Koszul multipliers modulo G retain
every fixed-denominator solution. This module imports only frozen arithmetic
and candidate data; it does not import the branch-products search driver.
"""
from fractions import Fraction as Q
from functools import lru_cache
from math import comb
from pathlib import Path
import json
import cyclic_fano_guided_denominators as old

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'results/cyclic-fano-higher-unfolding/candidates.json'
PINNED_INPUT_SHA='4900bc9ef14f4cc310dbc457f4282df10317a6f10c39312e4a9fcf176ec49b02'
base=old.base
poly=base.poly
GQ=old.GQ
NAMES=('X0','X1','Y0','Y1','Y2')
ZERO=(0,)*5


def power(p,n):
    assert n>=0
    out={ZERO:Q(1)}
    for _ in range(n):out=poly.mul(out,p)
    return out


def drop_z(p):
    assert all(m[2]==0 for m in p)
    return {m[:2]+m[3:]:c for m,c in p.items()}


def insert_z(p):return {m[:2]+(0,)+m[2:]:c for m,c in p.items()}


def ordinary_count(degree):return comb(degree+4,4)if degree>=0 else 0


def weighted_count(degree):
    return sum(ordinary_count(degree-3*j)for j in range(degree//3+1))if degree>=0 else 0


def monomial_product(p,m,c=1):
    if not c:return{}
    return {tuple(a+b for a,b in zip(n,m)):v*c for n,v in p.items()if v*c}


@lru_cache(maxsize=1)
def data():
    assert poly.sha(INPUT)==PINNED_INPUT_SHA
    packet=json.loads(INPUT.read_text(encoding='utf-8'))
    _,_,G,beta=base.target()
    assert G[(0,0,2,0,0,0)]==1 and all(m[2]<=2 for m in G)
    q=drop_z({m[:2]+(0,)+m[3:]:c for m,c in G.items()if m[2]==1})
    h=drop_z({m:c for m,c in G.items()if m[2]==0})
    delta=poly.add(poly.mul(q,q),h,-4)
    assert delta and all(sum(m)==6 for m in delta)
    factors=[drop_z(old.decode(x['quotient_denominator']))for x in packet['candidates']]
    factors.append({(0,2,0,0,0):Q(1),(0,0,0,0,2):Q(1)})
    return delta,drop_z(beta),tuple(factors),G


def setup(candidate):
    exponents=tuple(candidate['exponents'])
    assert len(exponents)==5 and all(isinstance(n,int)and n>=0 for n in exponents)
    assert candidate.get('factor_order',['T','C','S','R','J'])==['T','C','S','R','J']
    a=exponents[4];assert a>0
    delta,beta,factors,G=data()
    K={ZERO:GQ(1)}
    for factor,n in zip(factors,exponents[:4]):K=poly.mul(K,power(factor,n))
    k=sum(n*w for n,w in zip(exponents[:4],(1,3,6,2)))
    d=3*a+k;assert candidate['degree']==d and K and all(sum(m)==k for m in K)
    # A supplied denominator must be exactly the product specified by the
    # exponents; the compact system must not silently ignore changed data.
    if 'denominator'in candidate:
        J=poly.derivative(G,2);jp={(0,)*6:Q(1)}
        for _ in range(a):jp=poly.mul(jp,J)
        assert old.decode(candidate['denominator'])==poly.mul(insert_z(K),jp)
    return a,k,d,K,delta,beta


def system(candidate):
    """Return (column iterator, rhs, metadata); polynomials have five exponents."""
    a,k,d,K,delta,beta=setup(candidate)
    epsilon=a%2;half=(a+1)//2
    delta_d=[poly.derivative(delta,i)for i in range(5)]
    Kd=[poly.derivative(K,i)for i in range(5)]
    pure=not any(candidate['exponents'][:4])
    xx_degree=d-6-3*epsilon
    xt_degree=d-7+3*epsilon
    # For K=1 the even/odd adjacent powers share precisely the mixed map.
    # W_ij(f)=-(L_i(partial_j f)-L_j(partial_i f))/(2*half-1),
    # and W_ij(Delta*f)=Delta*W_ij(f), so all xx columns are redundant.
    xx_count=0 if pure else 10*ordinary_count(xx_degree)
    xt_count=5*ordinary_count(xt_degree)
    degree=2*k+6*half-2
    rhs=poly.scale(poly.mul(poly.mul(beta,power(delta,half-1)),poly.mul(K,K)),2)
    assert rhs and all(sum(m)==degree for m in rhs)
    delta_e=delta if epsilon else {ZERO:Q(1)}
    mixed_derivative=poly.scale(poly.mul(delta,K),2)
    mixed_constant=[poly.add(poly.scale(poly.mul(delta,Kd[i]),-2),
                            poly.mul(K,delta_d[i]),1-epsilon-a)for i in range(5)]
    def iterator():
        if not pure:
            for i in range(5):
                for j in range(i+1,5):
                    di=poly.mul(delta_e,poly.mul(K,delta_d[i]))
                    dj=poly.mul(delta_e,poly.mul(K,delta_d[j]))
                    zeroth=poly.scale(poly.mul(delta_e,poly.add(poly.mul(delta_d[i],Kd[j]),poly.mul(delta_d[j],Kd[i]),-1)),-1)
                    for m in base.monomials(xx_degree,(1,)*5):
                        column=monomial_product(zeroth,m)
                        if m[j]:
                            n=list(m);n[j]-=1
                            column=poly.add(column,monomial_product(di,tuple(n),m[j]))
                        if m[i]:
                            n=list(m);n[i]-=1
                            column=poly.add(column,monomial_product(dj,tuple(n),m[i]),-1)
                        assert all(sum(n)==degree for n in column)
                        yield {'kind':'compact_base_base','coordinates':[i,j],'powers':list(m),'multiplier_t_power':epsilon},column
        for i in range(5):
            for m in base.monomials(xt_degree,(1,)*5):
                column=monomial_product(mixed_constant[i],m)
                if m[i]:
                    n=list(m);n[i]-=1
                    column=poly.add(column,monomial_product(mixed_derivative,tuple(n),m[i]))
                assert all(sum(n)==degree for n in column)
                yield {'kind':'compact_base_t','coordinate':i,'powers':list(m),'multiplier_t_power':1-epsilon},column
    metadata={'schema':'cyclic-fano-branch-compact-system-v1','helper_sha256':poly.sha(Path(__file__)),
              'candidate_input_sha256':PINNED_INPUT_SHA,'a':a,'epsilon':epsilon,'k':k,'d':d,
              'variables':list(NAMES),'coordinate_change':'t=2Z+Q; g=t^2-Delta=4G; Delta=Q^2-4H',
              'pushforward':'V_i=P_i; V_t=2P_Z+sum_i Q_i P_i; constant Jacobian2 preserves divergence',
              'base_base_multiplier_degree':xx_degree,'base_t_multiplier_degree':xt_degree,
              'base_base_columns':xx_count,'base_t_columns':xt_count,'columns':xx_count+xt_count,
              'coefficient_degree':degree,'ambient_5var_rows':ordinary_count(degree),
              'raw_Koszul_coefficients':10*weighted_count(d-6)+5*weighted_count(d-4),
              'raw_E2_quotient_coefficients':weighted_count(2*d-8),
              'cancelled_Delta_power':a//2,'quotient_eliminated_exactly':True,
              'reflection_projection_complete':True,'Koszul_coefficients_reduced_modulo_g':True,
              'pure_J_pair_shortcut':pure,
              'paired_J_exponents':[2*half-1,2*half]if pure else None,
              'scope':'Complete E2 feasibility for this fixed invariant denominator after exact E1 particular field, reflection projection, Koszul reduction modulo g, and cancellation of a nonzero polynomial. No repeated-K cancellation.'}
    return iterator(),rhs,metadata


def self_check():
    """Actual polynomial checks against uncompressed six-variable fields."""
    delta,beta,_,_=data()
    def lift(p,t_power=0):return {m+(t_power,):c for m,c in p.items()}
    def reduce_even(p):
        out={}
        for m,c in p.items():
            assert m[-1]%2==0
            out=poly.add(out,monomial_product(power(delta,m[-1]//2),m[:-1],c))
        return out
    tested=0
    for exponents in [(1,0,0,0,1),(0,0,0,1,2),(1,0,0,0,3),(0,0,0,0,4)]:
        d=sum(n*w for n,w in zip(exponents,(1,3,6,2,3)))
        candidate={'exponents':list(exponents),'degree':d}
        a,k,d,K,delta,beta=setup(candidate)
        columns,rhs,meta=system(candidate);columns=list(columns)
        assert len(columns)==meta['columns']
        E=lift(K,a)
        particular=[{}for _ in range(6)];particular[5]=poly.scale(lift(poly.mul(beta,K),a-1),2)
        residual=base.B(E,particular)
        assert residual==poly.scale(lift(poly.mul(beta,poly.mul(K,K)),2*a-2),-2)
        assert reduce_even(poly.scale(residual,-1))==poly.mul(power(delta,a//2),rhs)
        for index in sorted({0,len(columns)//2,len(columns)-1})if columns else []:
            label,column=columns[index];m=tuple(label['powers']);tp=label['multiplier_t_power']
            H={m+(tp,):Q(1)};field=[{}for _ in range(6)]
            if label['kind']=='compact_base_t':
                i=label['coordinate']
                field[i]=poly.scale({m+(tp+1,):Q(1)},2)
                field[5]=poly.mul(H,lift(poly.derivative(delta,i)))
            else:
                i,j=label['coordinates']
                field[i]=poly.scale(poly.mul(H,lift(poly.derivative(delta,j))),-1)
                field[j]=poly.mul(H,lift(poly.derivative(delta,i)))
            g=poly.add({(0,0,0,0,0,2):Q(1)},lift(delta),-1)
            assert not base.contraction(field,g)
            assert reduce_even(base.B(E,field))==poly.mul(power(delta,a//2),column)
            tested+=1
    left,lr,lm=system({'exponents':[0,0,0,0,3],'degree':9})
    right,rr,rm=system({'exponents':[0,0,0,0,4],'degree':12})
    left=list(left);right=list(right)
    assert lr==rr and len(left)==len(right)==630
    assert all(x[1]==y[1]for x,y in zip(left,right))
    # Explicit curl identity explaining why the extra pure-J4 xx columns
    # add no freedom, independently of comparing the retained mixed maps.
    curl_tests=0
    for m in [(6,0,0,0,0),(3,3,0,0,0),(1,1,2,1,1)]:
        f={m:Q(1)};i,j=0,1
        wi=poly.derivative(delta,i);wj=poly.derivative(delta,j)
        Wf=poly.add(poly.mul(wi,poly.derivative(f,j)),poly.mul(wj,poly.derivative(f,i)),-1)
        vi=poly.derivative(f,j);vj=poly.scale(poly.derivative(f,i),-1)
        lhs={}
        for coordinate,v in ((i,vi),(j,vj)):
            L=poly.add(poly.scale(poly.mul(delta,poly.derivative(v,coordinate)),2),
                       poly.mul(poly.derivative(delta,coordinate),v),-3)
            lhs=poly.add(lhs,L)
        assert lhs==poly.scale(Wf,-3)
        curl_tests+=1
    return {'status':'PASS','physical_column_samples':tested,'particular_residuals':4,
            'pure_J3_J4_identical_columns':630,'pure_power_curl_identities':curl_tests,
            'helper_sha256':poly.sha(Path(__file__))}


if __name__=='__main__':
    assert __debug__,'Run without -O.'
    print(json.dumps(self_check()))
