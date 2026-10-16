"""Exact necessary E2 obstruction and additional sparse linear consequences.

Reproduces Discussion44's quadratic reduction of B_D(N0) modulo J(F).
Then searches for rational two-parameter linear forms whose SQUARE lies
in the residual quadratic rowspace. Such a form must vanish over C.
No zero-set classification, full E2 solvability, or certificate is claimed.
"""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations_with_replacement,combinations
import importlib.util,json,time
spec=importlib.util.spec_from_file_location('e1',Path(__file__).with_name('degree6_e1.py'))
e1=importlib.util.module_from_spec(spec);spec.loader.exec_module(e1)

def B(D,N):
    out={}
    for i in range(6):
        out=e1.padd(out,e1.pmul(D,e1.diff(N[i],i)))
        out=e1.padd(out,e1.pmul(N[i],e1.diff(D,i)),-1)
    return out
def normal(v,basis):
    v=dict(v);out={}
    while v:
        k=min(v);c=v[k]
        if k not in basis:out[k]=c;del v[k];continue
        for j,e in basis[k][0].items():
            z=v.get(j,0)-c*e
            if z:v[j]=z
            elif j in v:del v[j]
    return out
def main():
    start=time.perf_counter();report,pairs,jacobian=e1.rational_run()
    rows={u:i for i,u in enumerate(e1.mons(12))};n=len(pairs);quadratics=list(combinations_with_replacement(range(n),2));qindex={q:i for i,q in enumerate(quadratics)}
    equations={}
    for k,(i,j) in enumerate(quadratics):
        D,Ni=pairs[i];Dj,Nj=pairs[j]
        p=B(D,Nj)
        if i!=j:p=e1.padd(p,B(Dj,Ni))
        for row,c in normal({rows[u]:c for u,c in p.items()},jacobian).items():equations.setdefault(row,{})[k]=c
    active=set(range(n));rounds=[]
    while True:
        span=e1.Elimination();allowed={k for k,(i,j) in enumerate(quadratics) if i in active and j in active}
        for eq in equations.values():span.insert({k:c for k,c in eq.items() if k in allowed})
        forced=[i for i in sorted(active) if not normal({qindex[i,i]:Q(1)},span.basis)]
        rounds.append({'active':len(active),'rank':len(span.basis),'forced':forced});print(rounds[-1],flush=True)
        if not forced:break
        active-=set(forced)
    # Compute quotient images of the quadratic monomials, and seek a
    # rank-one binary quadratic relation using exact small rational ratios.
    cache={k:normal({k:Q(1)},span.basis) for k in allowed}
    relations=[];ratios=sorted({Q(a,b) for a in range(-12,13) for b in range(1,13) if a})
    relation_span=e1.Elimination()
    for i,j in combinations(sorted(active),2):
        x=cache[qindex[i,i]];y=cache[qindex[i,j]];z=cache[qindex[j,j]]
        # A coordinate supplies a degree<=2 equation restricting possible t.
        key=next(iter(x));aa=z.get(key,0);bb=2*y.get(key,0);cc=x[key]
        candidates=[t for t in ratios if aa*t*t+bb*t+cc==0]
        for t in candidates:
            residual=e1.padd(e1.padd(x,y,2*t),z,t*t)
            if not residual:
                rel={i:Q(1),j:t}
                independent=relation_span.insert(dict(rel)) is None
                relations.append({'terms':{str(i):'1',str(j):str(t)},'independent':independent})
    # Euler's denominator-F gauge is checked independently as polynomial
    # identities for each of the 109 lifts, and every 315 Koszul generator.
    EulerA=[]
    for i in range(6):
        z=[0]*6;z[i]=1;EulerA.append({e1.expadd(u,tuple(z)):Q(c,6) for u,c in e1.A.items()})
    gaugechecks=[]
    for D,N in pairs:
        div={}
        for i in range(6):div=e1.padd(div,e1.diff(N[i],i))
        linear=e1.padd(B(e1.F,N),B(D,EulerA))
        gaugechecks.append(linear==e1.pmul(e1.F,div))
    assert all(gaugechecks) and B(e1.F,EulerA)==e1.pmul(e1.A,e1.F)
    koszul_gaugechecks=[]
    for i,j in combinations(range(6),2):
        for u in e1.mons(2):
            K=[{}for _ in range(6)];K[i]=e1.pmul({u:1},e1.DF[j]);K[j]={v:-c for v,c in e1.pmul({u:1},e1.DF[i]).items()}
            div={}
            for k in range(6):div=e1.padd(div,e1.diff(K[k],k))
            koszul_gaugechecks.append(B(e1.F,K)==e1.pmul(e1.F,div))
    assert len(koszul_gaugechecks)==315 and all(koszul_gaugechecks)
    result={'instance':'holdout','field':'Q','necessary_quadratic_rounds':rounds,'binary_square_relations':relations,'independent_new_linear_relations':len(relation_span.basis),
            'searched_ratios':'Nonzero a/b with -12<=a<=12, 1<=b<=12; this bounded scan is not a full rank-one classification',
            'F_gauge_identity_verified_for_all_109_lifts':all(gaugechecks),
            'F_gauge_identity_verified_for_all_315_Koszul_corrections':all(koszul_gaugechecks),
            'F_gauge_identity':'B_(D+cF)(N+c A Euler/6) = B_D(N)+c F div(N)+c^2 A F, assuming N(F)=AD and degD=6',
            'F_gauge_quotient_update':'C -> C+c div(N)+c^2 A','F_gauge_legality':'gcd(D+cF,F)=gcd(D,F)',
            'seconds':time.perf_counter()-start,'scope':'Necessary quadratic obstruction only; no full E2 solution or degree-six exclusion'}
    (e1.OUT/'degree6_quadratic_structure.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2),flush=True)
    # Sparse exact equations are a reusable artifact; coefficients refer to
    # the unchanged full E1 denominator basis in degree6_e1_basis.json.
    exported={'parameters':n,'monomials':[list(q) for q in quadratics],
              'equations':[[[int(k),str(c)] for k,c in sorted(eq.items())] for eq in equations.values()],
              'active_after_individual_squares':sorted(active)}
    (e1.OUT/'degree6_necessary_quadratics.json').write_text(json.dumps(exported,separators=(',',':')),encoding='utf-8')

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    main()
