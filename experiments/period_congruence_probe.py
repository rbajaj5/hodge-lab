"""Exact constant-term arithmetic for the actual holdout sextic.

Inspired by rbajaj5/a183068-supercongruence's multinomial and Dwork notes.
This probes a period of a pencil through F; it does not solve target (F,q,A).
Run: python experiments/period_congruence_probe.py
"""
from pathlib import Path
from functools import cache
from collections import defaultdict
import datetime, hashlib, json, math, subprocess, time
import gpu_identity_screen as screen

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
OUT=HERE.parent/'results/period-congruence'
OUT.mkdir(parents=True,exist_ok=True)

@cache
def fac(n):return math.factorial(n)

@cache
def period(m):
    """CT (F / (X0 X1 X2 Y0 Y1 Y2))^(6m)."""
    value=0
    for u in range(m//3+1):
        for v in range((m-u)//3+1):
            parts=(m-3*u,m-u-3*v,m-v,m-u,m-u-v,m-v,6*u,6*v)
            assert min(parts)>=0 and sum(parts)==6*m
            numerator=fac(6*m);denominator=math.prod(fac(k) for k in parts)
            quotient,remainder=divmod(numerator,denominator)
            assert remainder==0
            value+=quotient
    return value

def direct_coefficient(F,n):
    """Independent repeated polynomial multiplication, truncated at target."""
    terms={tuple(e):int(c) for e,c in F.items()}
    poly={(0,)*6:1}
    for step in range(n):
        out=defaultdict(int)
        for a,c in poly.items():
            for b,d in terms.items():
                e=tuple(x+y for x,y in zip(a,b))
                if max(e)<=n:out[e]+=c*d
        poly=out
    return poly.get((n,)*6,0)

def vp(n,p):
    if n==0:return None
    n=abs(n);r=0
    while n%p==0:r+=1;n//=p
    return r

def main():
    start=time.perf_counter()
    target=screen.load_target(ROOT/'sources/sextics/data/holdout')
    expected=screen.parse_polynomial('X0**6+X1**6+X2**6+Y0**6+Y1**6+Y2**6+X0**3*X1*Y0*Y1+X1**3*X2*Y1*Y2')
    assert target['F']==expected
    # Pure powers are the simplex vertices; the coupling exponents lie in it.
    # After subtracting (1,...,1), its only relative-interior integral point
    # has all coordinates >=0 and sum 0, hence is the origin.
    direct=[]
    for n in [0,1,2,3,4,5,6,7,12,18]:
        actual=direct_coefficient(target['F'],n)
        expected=period(n//6) if n%6==0 else 0
        assert actual==expected
        direct.append({'power':n,'coefficient':str(actual),'matches_multinomial_formula':True})
    records=[]
    for p in [2,3,5,7,11,13]:
        for n in [1,2]:
            for r in [1,2]:
                m=n*p**r;previous=n*p**(r-1)
                delta=period(m)-period(previous)
                diagonal=fac(6*m)//fac(m)**6-fac(6*previous)//fac(previous)**6
                observed=vp(delta,p);fermat=vp(diagonal,p)
                # The q=1 certificate target is not tested by this arithmetic.
                # 3r is just the naive cubic benchmark, not an asserted bound.
                records.append({'p':p,'n':n,'r':r,'upper_index':m,
                                'holdout_valuation':observed,'fermat_valuation':fermat,
                                'cubic_benchmark':3*r,
                                'passes_cubic_benchmark':observed is None or observed>=3*r,
                                'defect_mod_cubic_power':delta%(p**(3*r))})
    failures=[r for r in records if r['p']>=5 and not r['passes_cubic_benchmark']]
    report={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'hodge_commit':subprocess.check_output(['git','-C',str(ROOT/'sources/sextics'),'rev-parse','HEAD'],text=True).strip(),
            'inspiration_commit':subprocess.check_output(['git','-C',str(ROOT/'sources/a183068-supercongruence'),'rev-parse','HEAD'],text=True).strip(),
            'sources':['https://github.com/rbajaj5/a183068-supercongruence/blob/main/related-results/BhattSinghDworkPeriodSupercongruence.md','https://github.com/rbajaj5/a183068-supercongruence/blob/main/related-results/FrobeniusQuotientConstantTerms.md','https://github.com/hodge-computer/sextics/blob/main/data/holdout/instance.rec'],
            'constant_term':'beta(k)=CT (F/(X0*X1*X2*Y0*Y1*Y2))^k; beta(k)=0 unless 6 divides k; C(m)=beta(6m).',
            'coefficient_formula':'C(m)=sum_(0<=u<=floor(m/3),0<=v<=floor((m-u)/3)) (6m)!/[(m-3u)!(m-u-3v)!(m-v)!^2(m-u)!(m-u-v)!(6u)!(6v)!].',
            'geometric_scope':'The torus integral of 1/(1-t*F/M), M=product of coordinates, expands as sum C(m)*t^(6m). After fixing one projective coordinate, it is a five-variable torus period of the complement of the pencil M-tF=0, with residue interpretation on smooth members. The fixed holdout F=0 lies at t=infinity; this is not a period evaluation at that endpoint, nor a certificate for A=X0^3 Y0^3.',
            'newton_polytope':'In the rank-five lattice sum_i e_i=0, the simplex e_i>=-1 has the origin as its sole relative-interior lattice point. The two coupling monomials lie inside that same simplex. This alone does not establish a cubic supercongruence.',
            'initial_C':[str(period(m)) for m in range(10)],
            'independent_polynomial_multiplication_checks':direct,
            'exact_adjacent_scale_cases':len(records),'prime_ge5_cubic_failures':len(failures),
            'first_prime_ge5_cubic_failure':failures[0] if failures else None,
            'cases':records,'seconds':time.perf_counter()-start,
            'status':'Exact finite arithmetic and an elementary coefficient formula; no new supercongruence theorem or accepted Hodge solve claimed.'}
    (OUT/'report.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({k:report[k] for k in ['initial_C','exact_adjacent_scale_cases','prime_ge5_cubic_failures','first_prime_ge5_cubic_failure','seconds']},indent=2))

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O; verification assertions are required.')
    main()
