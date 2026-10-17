#!/usr/bin/env python3
"""Exact Taylor-coordinate fiber equations for the cyclic Fano covering family.

This experiment fixes one point of the weighted quotient. It does not construct
a supporting divisor or change the source sextic. Each CAS worker is bounded.
"""
from __future__ import annotations
import argparse
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

S=None  # Loaded only for symbolic commands; the Macaulay checker uses stdlib.

REPO=Path(__file__).resolve().parents[1]
SOURCE=REPO/'results'/'cyclic-fano-curve'
OUT=REPO/'results'/'cyclic-fano-fibers'


def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()


def save(name,data):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/name).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')


def pair(value):
    value=S.expand(value)
    return [str(S.re(value)),str(S.im(value))]


def sparse(poly,variables):
    return [{'powers':list(m),'coefficient':pair(c)}
            for m,c in S.Poly(S.expand(poly),*variables,extension=S.I).terms()]


def expression(terms,variables):
    return S.expand(sum((S.Rational(t['coefficient'][0])+S.I*S.Rational(t['coefficient'][1]))
                        *S.prod(v**n for v,n in zip(variables,t['powers'])) for t in terms))


def derive():
    frozen=json.loads((SOURCE/'target.json').read_text(encoding='utf-8'))
    X0,X1,X2,Y0,Y1,Y2=S.symbols('X0 X1 X2 Y0 Y1 Y2')
    x=(X0,X1,X2,Y0,Y1,Y2);Z=S.Symbol('Z')
    F=S.Poly(S.sympify(frozen['target']['F'],locals=dict(zip(frozen['variables'],x))),*x)
    y=(X0,X1,Z,Y0,Y1,Y2)
    G=0
    for mon,coef in F.terms():
        assert mon[2]%3==0
        m=list(mon);m[2]//=3
        G+=coef*S.prod(v**n for v,n in zip(y,m))
    G=S.expand(G)
    b,c,v,k,l,m,u=S.symbols('b c v k l m u')
    variables=(b,c,v,k,l,m)
    # s=1, r=1, u=t-r.  v is the deviation of the Y2 slope from i.
    curve=(b*u,1,k*u+l*u**2+m*u**3,S.I+c*u,1+u,S.I+(S.I+v)*u)
    substituted=S.Poly(S.expand(G.subs(dict(zip(y,curve)))),u)
    assert substituted.coeff_monomial(1)==0
    equations=[substituted.coeff_monomial(u**j)for j in range(1,7)]
    pivot=S.Rational(5,7)*S.I
    solutions={}
    stages=[]
    for eq,var in zip(equations[:3],(k,l,m)):
        current=S.expand(eq.subs(solutions))
        assert S.diff(current,var)==pivot
        rhs=S.expand(-current.subs(var,0)/pivot)
        assert set(rhs.free_symbols)<={b,c,v}
        solutions[var]=rhs
        assert S.expand(current.subs(var,rhs))==0
        stages.append({'variable':str(var),'pivot':pair(pivot),'solution':sparse(rhs,(b,c,v))})
    reduced=[S.expand(eq.subs(solutions))for eq in equations[3:]]
    assert all(S.expand(eq.subs(solutions))==0 for eq in equations[:3])
    assert S.expand(substituted.as_expr().subs(solutions)-sum(q*u**j for j,q in enumerate(reduced,4)))==0
    zero=dict.fromkeys(variables,0)
    jac=S.Matrix([[S.diff(eq,var).subs(zero)for var in variables]for eq in equations])
    redjac=S.Matrix([[S.diff(eq,var).subs(zero)for var in (b,c,v)]for eq in reduced])
    assert jac.det()!=0 and redjac.det()!=0
    assert all(eq.subs(zero)==0 for eq in equations)
    result={'schema':'cyclic-fano-fixed-fiber-v1','upstream_commit':frozen['upstream_commit'],
            'instance':frozen['instance'],'fixed_target_manifest_sha256':sha(SOURCE/'target.json'),
            'curve_packet_sha256':sha(SOURCE/'cyclic-free-curve.json'),
            'producer_sha256':sha(Path(__file__)),
            'field':'Q(i), i^2=-1','quotient_coordinates':[str(z)for z in y],
            'quotient_equation':str(G),'fixed_point':['0','1','0','I','1','I'],
            'taylor_parameter':'u=t/s-1','variables':[str(z)for z in variables],
            'curve_at_s_1':[str(z)for z in curve],
            'coefficient_equations':[sparse(eq,variables)for eq in equations],
            'coefficient_degrees':[S.Poly(eq,*variables).total_degree()for eq in equations],
            'triangular_solutions':stages,'remaining_variables':['b','c','v'],
            'remaining_equations':[sparse(eq,(b,c,v))for eq in reduced],
            'remaining_degrees':[S.Poly(eq,b,c,v).total_degree()for eq in reduced],
            'full_jacobian_at_origin':[[pair(z)for z in row]for row in jac.tolist()],
            'full_jacobian_determinant':pair(jac.det()),
            'reduced_jacobian_at_origin':[[pair(z)for z in row]for row in redjac.tolist()],
            'reduced_jacobian_determinant':pair(redjac.det()),
            'general_triangular_condition':'For a point (U,1,Z0,V,r,W), the Taylor coefficients k,l,m of Z are solved successively if G_Z(point) != 0. All three pivots equal G_Z(point); the constant equation is G(point)=0.',
            'conclusion':'The chosen fiber is reduced and zero-dimensional locally at the displayed line, by the nonzero exact Jacobian. The three remaining equations are equivalent to all six equations on this fixed-point fiber. No global dimension or generic fiber degree follows from the local Jacobian alone.',
            'certificate_found':False}
    return result


def modular_polys(packet,p,imaginary):
    assert p%4==1 and (imaginary*imaginary+1)%p==0
    variables=S.symbols('b c v')
    result=[]
    for terms in packet['remaining_equations']:
        q={}
        for term in terms:
            real,imag=map(S.Rational,term['coefficient'])
            value=(int(real.p)*pow(int(real.q),-1,p)+imaginary*int(imag.p)*pow(int(imag.q),-1,p))%p
            if value:q[tuple(term['powers'])]=value
        result.append(S.Poly.from_dict(q,variables,modulus=p))
    return variables,result


def monomials(degree):
    return [(a,b,degree-a-b)for a in range(degree,-1,-1)for b in range(degree-a,-1,-1)]


def modular_rank_minor(matrix,p):
    a=[row[:]for row in matrix];rows=len(a);cols=len(a[0]);rank=0;selected=[];det=1
    for col in range(cols):
        pivot=next((i for i in range(rank,rows)if a[i][col]%p),None)
        if pivot is None:continue
        if pivot!=rank:a[rank],a[pivot]=a[pivot],a[rank];det=-det
        lead=a[rank][col]%p;det=det*lead%p;inv=pow(lead,-1,p)
        a[rank]=[z*inv%p for z in a[rank]]
        for i in range(rank+1,rows):
            factor=a[i][col]%p
            if factor:a[i]=[(z-factor*w)%p for z,w in zip(a[i],a[rank])]
        selected.append(col);rank+=1
        if rank==rows:break
    return rank,selected,det%p


def infinity_witness(packet,prime=101):
    imaginary=next(a for a in range(1,prime)if(a*a+1)%prime==0)
    variables,polys=modular_polys(packet,prime,imaginary)
    degree=13;rows=monomials(degree);index={m:i for i,m in enumerate(rows)}
    columns=[];descriptions=[]
    for i,poly in enumerate(polys):
        topdegree=poly.total_degree()
        top={m:int(c)%prime for m,c in poly.terms()if sum(m)==topdegree}
        for multiple in monomials(degree-topdegree):
            col=[0]*len(rows)
            for mon,coefficient in top.items():
                shifted=tuple(a+b for a,b in zip(mon,multiple))
                col[index[shifted]]=coefficient
            columns.append(col)
            descriptions.append({'source_equation_index':i,'multiplier_powers':list(multiple),
                                 'entries':[[j,c]for j,c in enumerate(col)if c]})
    matrix=[list(row)for row in zip(*columns)]
    rank,selected,det=modular_rank_minor(matrix,prime)
    assert (len(rows),len(columns),rank)==(105,136,105)and det!=0
    return {'schema':'cyclic-fano-fiber-infinity-witness-v1','prime':prime,'i_image':imaginary,
            'homogeneous_degree':degree,'rows':[list(m)for m in rows],
            'columns':descriptions,'matrix_shape':[len(rows),len(columns)],
            'rank':rank,'selected_columns':selected,'selected_minor_determinant_mod_p':det,
            'interpretation':'A selected 105 by105 minor of the degree13 Macaulay matrix is nonzero modulo101 under i→10. Every coefficient denominator is invertible there, so the same minor is nonzero over Q(i). Thus the highest homogeneous parts span all degree13 monomials and have no common projective zero over C. The selected fixed-point fiber is finite in characteristic zero; its three equations of degrees4,5,6 form a complete intersection of length120 counted with multiplicity. This is not a computed support divisor or a statement that all120 points are distinct.'}


def check_macaulay(packet,witness):
    """Reconstruct the exact modular witness without SymPy or other packages."""
    p=witness['prime'];imaginary=witness['i_image']
    assert p==101 and imaginary==10 and (imaginary*imaginary+1)%p==0
    rows=monomials(13);index={m:i for i,m in enumerate(rows)}
    assert witness['rows']==[list(m)for m in rows]
    expected=[]
    for i,terms in enumerate(packet['remaining_equations']):
        degree=max(sum(t['powers'])for t in terms)
        assert degree==[4,5,6][i]
        for multiplier in monomials(13-degree):
            col=[0]*len(rows)
            for term in terms:
                if sum(term['powers'])!=degree:continue
                re,im=map(Fraction,term['coefficient'])
                value=(re.numerator*pow(re.denominator,-1,p)
                       +imaginary*im.numerator*pow(im.denominator,-1,p))%p
                mon=tuple(a+b for a,b in zip(term['powers'],multiplier))
                col[index[mon]]=value
            expected.append({'source_equation_index':i,'multiplier_powers':list(multiplier),
                             'entries':[[j,c]for j,c in enumerate(col)if c]})
    assert witness['columns']==expected
    selected=witness['selected_columns'];assert len(selected)==105 and len(set(selected))==105
    minor=[]
    for row in range(105):
        minor.append([dict(expected[col]['entries']).get(row,0)for col in selected])
    rank,pivots,det=modular_rank_minor(minor,p)
    assert rank==105 and det==witness['selected_minor_determinant_mod_p']==47
    assert witness['matrix_shape']==[105,136] and witness['rank']==105


def portable_verify():
    packet=json.loads((OUT/'fiber-equations.json').read_text(encoding='utf-8'))
    witness=json.loads((OUT/'infinity-witness.json').read_text(encoding='utf-8'))
    assert witness['input_packet_sha256']==sha(OUT/'fiber-equations.json')
    assert packet['fixed_target_manifest_sha256']==sha(SOURCE/'target.json')
    assert packet['curve_packet_sha256']==sha(SOURCE/'cyclic-free-curve.json')
    assert packet['producer_sha256']==sha(Path(__file__))
    check_macaulay(packet,witness)
    rejected=[]
    for mutation in ('column_coefficient','repeated_minor_column','wrong_i_image'):
        bad=copy.deepcopy(witness)
        if mutation=='column_coefficient':bad['columns'][0]['entries'][0][1]=(bad['columns'][0]['entries'][0][1]+1)%101
        elif mutation=='repeated_minor_column':bad['selected_columns'][1]=bad['selected_columns'][0]
        else:bad['i_image']=11
        try:check_macaulay(packet,bad)
        except AssertionError:rejected.append(mutation)
        else:raise AssertionError('Mutation accepted: '+mutation)
    result={'schema':'cyclic-fano-fiber-macaulay-validation-v1','status':'PASS',
            'input_packet_sha256':sha(OUT/'fiber-equations.json'),
            'witness_sha256':sha(OUT/'infinity-witness.json'),'producer_sha256':sha(Path(__file__)),
            'standard_library_only':True,'prime':101,'rank':105,'minor_determinant':47,
            'mutations_rejected':rejected,
            'scope':'Reconstructs the degree13 coefficient matrix from the exported rational Gaussian polynomials and verifies its nonzero residue-field minor. Exact source-to-fiber symbolic identities are checked separately by verify and the independent checker.'}
    save('macaulay-validation.json',result);print(json.dumps(result),flush=True)


def groebner_worker(prime):
    start=time.perf_counter();packet=json.loads((OUT/'fiber-equations.json').read_text(encoding='utf-8'))
    imaginary=next(a for a in range(1,prime)if(a*a+1)%prime==0)
    variables,polys=modular_polys(packet,prime,imaginary)
    basis=S.groebner(polys,*variables,modulus=prime,order='grevlex',method='f5b')
    leading=[p.LM(order=basis.order).exponents for p in basis.polys]
    pure=[]
    for i in range(3):
        powers=[mon[i]for mon in leading if mon[i]and all(mon[j]==0 for j in range(3)if j!=i)]
        pure.append(min(powers)if powers else None)
    normal_monomials=[]
    if all(pure):
        import itertools
        for mon in itertools.product(*[range(n)for n in pure]):
            if not any(all(a>=b for a,b in zip(mon,lm))for lm in leading):normal_monomials.append(mon)
    assert all(basis.reduce(p.as_expr())[1]==0 for p in polys)
    result={'schema':'cyclic-fano-fiber-groebner-v1','prime':prime,'i_image':imaginary,
            'input_packet_sha256':sha(OUT/'fiber-equations.json'),'order':'grevlex','algorithm':'SymPy f5b',
            'basis':[{'powers':[list(m)for m,c in p.terms()],
                      'coefficients':[int(c)%prime for m,c in p.terms()]}for p in basis.polys],
            'basis_size':len(basis.polys),'zero_dimensional':bool(basis.is_zero_dimensional),
            'pure_leading_powers':pure,'standard_monomials':[list(m)for m in normal_monomials],
            'quotient_dimension':len(normal_monomials)if all(pure)else None,
            'original_equations_reduce_to_zero':True,'seconds':time.perf_counter()-start,
            'limits':'This calculation concerns the complete selected fixed-point fiber modulo this prime. It does not establish a characteristic-zero fiber degree or a support divisor.'}
    save(f'groebner-{prime}.json',result)
    print(json.dumps({k:result[k]for k in ('prime','basis_size','zero_dimensional','quotient_dimension','seconds')}),flush=True)


def main():
    global S
    if not __debug__:raise RuntimeError('Run without -O.')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['derive','verify','verify-macaulay','groebner','worker'])
    parser.add_argument('--prime',type=int,default=101)
    args=parser.parse_args()
    if args.command=='verify-macaulay':portable_verify();return
    import sympy as S
    if args.command=='derive':
        result=derive();save('fiber-equations.json',result)
        witness=infinity_witness(result)
        witness['input_packet_sha256']=sha(OUT/'fiber-equations.json')
        save('infinity-witness.json',witness)
        print(json.dumps({'status':'PASS','reduced_degrees':result['remaining_degrees'],
                          'reduced_jacobian_determinant':result['reduced_jacobian_determinant'],
                          'infinity_matrix_shape':witness['matrix_shape'],'infinity_rank':witness['rank'],
                          'nonzero_minor_mod_101':witness['selected_minor_determinant_mod_p']}),flush=True)
    elif args.command=='verify':
        packet=json.loads((OUT/'fiber-equations.json').read_text(encoding='utf-8'))
        assert packet==derive()
        witness=json.loads((OUT/'infinity-witness.json').read_text(encoding='utf-8'))
        expected=infinity_witness(packet)
        expected['input_packet_sha256']=sha(OUT/'fiber-equations.json')
        assert witness==expected
        result={'status':'PASS','packet_sha256':sha(OUT/'fiber-equations.json'),
                'infinity_witness_sha256':sha(OUT/'infinity-witness.json'),
                'producer_sha256':sha(Path(__file__)),'exact_equivalent_triangularization':True,
                'nonzero_local_jacobian':True,'highest_parts_span_all_degree13_monomials_over_Q_i':True,
                'finite_characteristic_zero_fixed_point_fiber':True,'fiber_length_with_multiplicity':120,
                'certificate_found':False}
        save('validation.json',result);print(json.dumps(result),flush=True)
    elif args.command=='worker':groebner_worker(args.prime)
    else:
        start=time.perf_counter()
        try:
            process=subprocess.run([sys.executable,str(Path(__file__).resolve()),'worker','--prime',str(args.prime)],
                                   capture_output=True,text=True,timeout=120)
            result={'status':'complete'if process.returncode==0 else'error','returncode':process.returncode,
                    'stdout':process.stdout,'stderr':process.stderr}
        except subprocess.TimeoutExpired:
            result={'status':'timeout','stop_reason':'120-second wall-clock bound'}
        result.update(prime=args.prime,time_limit_seconds=120,elapsed_seconds=time.perf_counter()-start)
        save(f'attempt-{args.prime}.json',result);print(json.dumps(result),flush=True)
        if result['status']!='complete':raise SystemExit(1)


if __name__=='__main__':main()
