#!/usr/bin/env python3
"""Exact finite-field multiplication spectra of the cyclic Fano fixed fiber.

Discovery uses SymPy and FLINT; polynomial reduction and field arithmetic are
explicit. Matrices use columns for multiplication in the saved monomial basis.
No characteristic-zero nonreducedness is inferred from a bad special fiber.
"""
from __future__ import annotations
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

REPO=Path(__file__).resolve().parents[1]
INPUT=REPO/'results'/'cyclic-fano-fibers'
OUT=REPO/'results'/'cyclic-fano-spectrum'
P=101


def sha(path):return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()


def save(name,value):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')


def grevlex(mon):return sum(mon),tuple(-v for v in reversed(mon))
def plus(a,b):return tuple(x+y for x,y in zip(a,b))
def divides(a,b):return all(x<=y for x,y in zip(a,b))


def mod_coeff(pair):
    real,imag=map(Fraction,pair)
    return (real.numerator*pow(real.denominator,-1,P)
            +10*imag.numerator*pow(imag.denominator,-1,P))%P


def source_polynomials(packet):
    return [{tuple(t['powers']):mod_coeff(t['coefficient'])for t in terms if mod_coeff(t['coefficient'])}
            for terms in packet['remaining_equations']]


class NormalForm:
    def __init__(self,basis,standard):
        self.basis=[]
        for poly in basis:
            lead=max(poly,key=grevlex);coefficient=poly[lead]
            normalized={mon:c*pow(coefficient,-1,P)%P for mon,c in poly.items()}
            self.basis.append((lead,normalized))
        self.standard=set(standard);self.cache={mon:{mon:1}for mon in standard}

    def monomial(self,mon):
        if mon in self.cache:return self.cache[mon]
        for lead,poly in self.basis:
            if divides(lead,mon):
                shift=tuple(a-b for a,b in zip(mon,lead));result={}
                for term,coefficient in poly.items():
                    if term==lead:continue
                    for power,value in self.monomial(plus(term,shift)).items():
                        result[power]=(result.get(power,0)-coefficient*value)%P
                        if result[power]==0:del result[power]
                self.cache[mon]=result;return result
        raise AssertionError('Irreducible monomial absent from standard basis: '+str(mon))

    def polynomial(self,poly):
        result={}
        for mon,coefficient in poly.items():
            for term,value in self.monomial(mon).items():
                result[term]=(result.get(term,0)+coefficient*value)%P
                if result[term]==0:del result[term]
        return result


def dense(matrix):return [[int(matrix[i,j])for j in range(matrix.ncols())]for i in range(matrix.nrows())]


def polynomial_matrix(coefficients,matrix,eye,zero):
    result=zero
    for coefficient in reversed(coefficients):result=result*matrix+int(coefficient)*eye
    return result


def exact_swapped_point(packet):
    import sympy as S
    b,c,v=S.symbols('b c v');variables=(b,c,v)
    equations=[S.expand(sum((S.Rational(t['coefficient'][0])+S.I*S.Rational(t['coefficient'][1]))
                *S.prod(x**n for x,n in zip(variables,t['powers']))for t in terms))
               for terms in packet['remaining_equations']]
    point={b:0,c:S.I,v:-S.I}
    values=[S.simplify(q.subs(point))for q in equations]
    J=S.Matrix([[S.simplify(S.diff(q,x).subs(point))for x in variables]for q in equations])
    assert values==[0,0,0]and J.rank()==2
    assert J==S.I*S.Matrix([[0,6,-24],[0,12,-18],[0,6,0]])
    assert J[:,1:3][0:2,:].det()==-180
    alpha=-S.Rational(8,175)+S.I/6
    jet={c:S.I+alpha*b**3,v:-S.I-alpha*b**3}
    coefficients=[[S.expand(q.subs(jet)).coeff(b,k).simplify()for k in range(4)]for q in equations]
    assert coefficients[0]==[0]*4 and coefficients[1]==[0]*4
    assert coefficients[2]==[0,0,0,-1-S.Rational(48,175)*S.I]
    return {'field':'Q(i)','point':[['0','0'],['0','1'],['0','-1']],
            'coordinate_order':['b','c','v'],'equation_values':[['0','0']]*3,
            'jacobian':[[[str(S.re(z)),str(S.im(z))]for z in row]for row in J.tolist()],
            'jacobian_rank':2,'selected_rows':[0,1],'selected_columns':[1,2],
            'nonzero_minor':['-180','0'],'tangent_kernel_basis':[[1,0,0]],
            'implicit_jet_parameter':'b','c_jet_coefficients_ascending':[['0','1'],['0','0'],['0','0'],['-8/175','1/6']],
            'v_jet_coefficients_ascending':[['0','-1'],['0','0'],['0','0'],['8/175','-1/6']],
            'remaining_scalar_cubic_coefficient':['-1','-48/175'],'local_length':3,
            'local_jet_reason':'The first two equations have invertible (c,v) Jacobian. Their formal implicit solutions have the displayed jets; the third equation has first nonzero coefficient (−1−48i/175)b^3. Thus the completed local algebra is Q(i)[[b]]/(b^3).',
            'curve':['0','s','0','I*t','t','I*s'],
            'conclusion':'The characteristic-zero fixed-point fiber is finite, and this exact rational point has a nonzero tangent space. Hence its local Artinian ring is not reduced. This argument does not infer nonreducedness from reduction modulo101.'}


def rank_minor(matrix,p):
    a=[row[:]for row in matrix];row_labels=list(range(len(a)));rank=0;columns=[]
    for col in range(len(a[0])):
        pivot=next((i for i in range(rank,len(a))if a[i][col]%p),None)
        if pivot is None:continue
        a[rank],a[pivot]=a[pivot],a[rank];row_labels[rank],row_labels[pivot]=row_labels[pivot],row_labels[rank]
        inverse=pow(a[rank][col],-1,p);a[rank]=[v*inverse%p for v in a[rank]]
        for i in range(rank+1,len(a)):
            factor=a[i][col]
            if factor:a[i]=[(x-factor*y)%p for x,y in zip(a[i],a[rank])]
        columns.append(col);rank+=1
    return rank,row_labels[:rank],columns


def calculate(publish=True):
    import sympy as S
    from flint import nmod_mat,nmod_poly
    start=time.perf_counter()
    packet=json.loads((INPUT/'fiber-equations.json').read_text(encoding='utf-8'))
    saved=json.loads((INPUT/'groebner-101.json').read_text(encoding='utf-8'))
    assert saved['input_packet_sha256']==sha(INPUT/'fiber-equations.json')
    assert saved['prime']==P and saved['i_image']==10
    polynomials=source_polynomials(packet)
    variables=S.symbols('b c v')
    # Poly.from_dict may coerce values in its dictionary; preserve native ints.
    source=[S.Poly.from_dict(dict(poly),variables,modulus=P)for poly in polynomials]
    rebuilt=S.groebner(source,*variables,modulus=P,order='grevlex',method='f5b')
    basis=[dict(zip(map(tuple,entry['powers']),entry['coefficients']))for entry in saved['basis']]
    assert [{m:int(c)%P for m,c in p.terms()}for p in rebuilt.polys]==basis
    standard=list(map(tuple,saved['standard_monomials']));size=len(standard);assert size==120
    index={mon:i for i,mon in enumerate(standard)};unit=index[(0,0,0)]
    reduce=NormalForm(basis,standard)
    for poly in polynomials:assert not reduce.polynomial(poly)
    matrices=[]
    for variable in range(3):
        array=[[0]*size for _ in range(size)]
        mon=tuple(int(i==variable)for i in range(3))
        for col,basis_mon in enumerate(standard):
            for term,value in reduce.monomial(plus(mon,basis_mon)).items():array[index[term]][col]=value
        matrices.append(nmod_mat(array,P))
    eye=nmod_mat([[int(i==j)for j in range(size)]for i in range(size)],P)
    zero=nmod_mat(size,size,P)
    for i in range(3):
        for j in range(i):assert matrices[i]*matrices[j]==matrices[j]*matrices[i]
    powers=[]
    for j in range(3):
        needed=max(max(mon[j]for poly in polynomials for mon in poly),max(mon[j]for mon in standard))
        row=[eye]
        for _ in range(needed):row.append(row[-1]*matrices[j])
        powers.append(row)
    for poly in polynomials:
        result=nmod_mat(size,size,P)
        for mon,coefficient in poly.items():result+=coefficient*(powers[0][mon[0]]*powers[1][mon[1]]*powers[2][mon[2]])
        assert result==zero
    unit_vector=nmod_mat([[int(i==unit)]for i in range(size)],P)
    for j,mon in enumerate(standard):
        result=powers[0][mon[0]]*(powers[1][mon[1]]*(powers[2][mon[2]]*unit_vector))
        assert all(int(result[i,0])==int(i==j)for i in range(size))
    attempts=[]
    for weights in [(1,0,0),(0,1,0),(0,0,1),(1,1,1),(1,2,3),(1,3,7),(2,5,11)]:
        matrix=sum((w*M for w,M in zip(weights,matrices)),nmod_mat(size,size,P))
        charpoly=matrix.charpoly();minimal=matrix.minpoly();gcd=charpoly.gcd(charpoly.derivative())
        unit_factor,factors=charpoly.factor()
        attempt={'linear_form_weights':list(weights),'characteristic_polynomial_ascending':list(map(int,charpoly)),
                 'minimal_polynomial_ascending':list(map(int,minimal)),
                 'characteristic_derivative_gcd_ascending':list(map(int,gcd)),
                 'squarefree_characteristic_polynomial':gcd.degree()==0,
                 'minimal_degree':minimal.degree(),'factors':[{'coefficients_ascending':list(map(int,f)),
                                                              'degree':f.degree(),'multiplicity':e}for f,e in factors]}
        assert minimal==charpoly or charpoly%minimal==nmod_poly([],P)
        attempts.append(attempt)
        print(json.dumps({'linear_form_weights':weights,'minimal_degree':minimal.degree(),'gcd_degree':gcd.degree(),
                          'factor_degrees':[(f.degree(),e)for f,e in factors]}),flush=True)
        if gcd.degree()==0:break
    selected=next(i for i,a in enumerate(attempts)if a['minimal_degree']==size)
    chosen=attempts[selected]
    L=sum((w*M for w,M in zip(chosen['linear_form_weights'],matrices)),nmod_mat(size,size,P))
    cp=nmod_poly(chosen['characteristic_polynomial_ascending'],P)
    vectors=[unit_vector]
    for _ in range(size):vectors.append(L*vectors[-1])
    krylov=nmod_mat([[int(vectors[j][i,0])for j in range(size)]for i in range(size)],P)
    assert krylov.rank()==size
    assert sum((int(cp[j])*vectors[j]for j in range(size+1)),nmod_mat(size,1,P))==nmod_mat(size,1,P)
    coordinate_polynomials={}
    for name,M in zip(('b','c','v'),matrices):
        coefficients=krylov.solve(M*unit_vector)
        coeff=[int(coefficients[j,0])for j in range(size)]
        assert polynomial_matrix(coeff,L,eye,zero)==M
        coordinate_polynomials[name]=coeff
    projectors=[];projector_matrices=[];nilpotent=None
    for factor in chosen['factors']:
        irreducible=nmod_poly(factor['coefficients_ascending'],P)
        primary=irreducible**factor['multiplicity'];complement=cp//primary
        gcd,inverse,other=complement.xgcd(primary)
        assert gcd==nmod_poly([1],P)
        polynomial=(complement*inverse)%cp
        E=polynomial_matrix(list(polynomial),L,eye,zero)
        assert E*E==E
        rank=E.rank();assert rank==factor['degree']*factor['multiplicity']
        record={'factor_coefficients_ascending':factor['coefficients_ascending'],
                'factor_degree':factor['degree'],'multiplicity':factor['multiplicity'],
                'projector_coefficients_ascending':list(map(int,polynomial)),'projector_rank':rank}
        projectors.append(record);projector_matrices.append(E)
        if factor['degree']==1 and factor['multiplicity']>1:
            eigenvalue=-int(irreducible[0])*pow(int(irreducible[1]),-1,P)%P
            N=(L-eigenvalue*eye)*E;power=E;ranks=[]
            for exponent in range(factor['multiplicity']+1):
                ranks.append(power.rank());power=power*N
            assert ranks==[3,2,1,0]
            cyclic=E*unit_vector;chain=[N*N*cyclic,N*cyclic,cyclic]
            chain_matrix=nmod_mat([[int(vector[i,0])for vector in chain]for i in range(size)],P)
            jordan=nmod_mat([[0,1,0],[0,0,1],[0,0,0]],P)
            assert chain_matrix.rank()==3 and N*chain_matrix==chain_matrix*jordan
            nilpotent={'eigenvalue':eigenvalue,'projector_matrix':dense(E),'nilpotent_matrix':dense(N),
                       'ranks_E_N_N2_N3':ranks,'local_kernel_dimensions':[3-r for r in ranks],
                       'chain_basis_columns_N2E1_NE1_E1':dense(chain_matrix),
                       'restricted_nilpotent_matrix':dense(jordan),
                       'exact_nilpotency_index':3}
    assert sum(projector_matrices,nmod_mat(size,size,P))==eye
    for i,E in enumerate(projector_matrices):
        for F in projector_matrices[:i]:assert E*F==zero
    # Newton identities use multiplication only, with no division by k; valid
    # also at k=101, where the characteristic divides the coefficient k.
    coefficients=list(map(int,cp));traces=[size%P]
    for k in range(1,2*size-1):
        value=sum(coefficients[size-j]*traces[k-j]for j in range(1,min(k,size)+1)if j<k)
        if k<=size:value+=k*coefficients[size-k]
        traces.append(-value%P)
    trace_form=nmod_mat([[traces[i+j]for j in range(size)]for i in range(size)],P)
    assert traces[1]==sum(int(L[i,i])for i in range(size))%P
    assert trace_form.rank()==118
    trace_rank,trace_rows,trace_columns=rank_minor(dense(trace_form),P)
    trace_minor=nmod_mat([[int(trace_form[i,j])for j in trace_columns]for i in trace_rows],P)
    trace_det=int(trace_minor.det());assert trace_rank==118 and trace_det!=0
    selected_record={'attempt_index':selected,'linear_form_weights':chosen['linear_form_weights'],
                     'krylov_basis_convention':'Columns 1,L1,...,L^119 1 in the saved monomial basis.',
                     'krylov_rank':size,'krylov_determinant':int(krylov.det()),
                     'coordinate_polynomials_in_L_ascending':coordinate_polynomials,
                     'projectors':projectors,'nonreduced_primary_block':nilpotent,
                     'power_traces':traces,'trace_form_basis':'1,L,...,L^119',
                     'trace_form_rank':118,'trace_form_nullity':2,
                     'trace_form_minor_rows':trace_rows,'trace_form_minor_columns':trace_columns,
                     'trace_form_minor_determinant':trace_det,
                     'separates_geometric_points_over_algebraic_closure':True,
                     'geometric_point_count_over_algebraic_closure':118}
    result={'schema':'cyclic-fano-fiber-spectrum-v1','prime':P,'i_image':10,'dimension':size,
            'producer_sha256':sha(Path(__file__)),
            'source_packet_sha256':sha(INPUT/'fiber-equations.json'),
            'groebner_packet_sha256':sha(INPUT/'groebner-101.json'),
            'infinity_witness_sha256':sha(INPUT/'infinity-witness.json'),
            'basis_order':[list(m)for m in standard],'unit_basis_index':unit,
            'matrix_convention':'Columns: multiplication of each listed monomial by b,c,v, followed by exact reduction.',
            'multiplication_matrices':{str(v):dense(m)for v,m in zip(variables,matrices)},
            'checks':{'groebner_reconstructed_from_source_equations':True,'original_equations_zero':True,
                      'matrices_pairwise_commute':True,'original_equations_vanish_as_matrices':True,
                      'monomial_orbit_of_unit_matches_full_basis':True},
            'linear_form_attempts':attempts,
            'selected_operator':selected_record,
            'characteristic_zero_swapped_point':exact_swapped_point(packet),
            'characteristic_zero_inference':{
                'geometric_points_over_C':118,'one_point_length':3,'remaining_simple_points':117,
                'argument':'Localize Z[i] at (101,i−10), with source denominators inverted. The degree13 no-infinity minor is a unit, so the fiber algebra is finite over this DVR. Generic and special lengths both120 imply freeness of rank120; the monomial basis and cyclic-power basis lift. The nonzero118 by118 trace minor lifts, giving at least118 geometric points in characteristic zero. The exact Q(i) local length3 at the swapped line and total length120 give at most118. Therefore there are exactly118 geometric points: the displayed length3 point and117 simple points.',
                'limits':'This describes the complete selected fixed-point incidence fiber. It does not give the degree of the seed covering component or a supporting divisor.'},
            'squarefree_characteristic_polynomial_found':any(a['squarefree_characteristic_polynomial']for a in attempts),
            'geometric_separator_found':True,
            'seconds':time.perf_counter()-start,
            'limits':'All listed operator spectra and CRT projectors are exact over F101 and its algebraic closure, not complex numeric eigenvalues. The separate characteristic-zero point-count conclusion uses the finite-free model, trace minor and exact local jet, rather than transferring repeated eigenvalues alone. No supporting divisor or certificate is constructed.'}
    if publish:
        save('spectrum-101.json',result)
        print(json.dumps({'status':'PASS','squarefree_characteristic_polynomial_found':result['squarefree_characteristic_polynomial_found'],
                          'geometric_separator_found':True,'seconds':result['seconds']}),flush=True)
    return result


def main():
    if not __debug__:raise RuntimeError('Run without -O.')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['run','worker','verify'])
    args=parser.parse_args()
    if args.command=='worker':calculate();return
    if args.command=='verify':
        packet=json.loads((OUT/'spectrum-101.json').read_text(encoding='utf-8'))
        expected=calculate(publish=False)
        for key in expected:
            if key!='seconds':assert packet[key]==expected[key],key
        result={'status':'PASS','packet_sha256':sha(OUT/'spectrum-101.json'),
                'producer_sha256':sha(Path(__file__)),'dimension':120,'trace_rank':118,
                'exact_Q_i_local_length':3,'characteristic_zero_geometric_points':118,
                'characteristic_zero_simple_points':117,'certificate_found':False}
        save('validation.json',result);print(json.dumps(result),flush=True);return
    start=time.perf_counter()
    try:
        process=subprocess.run([sys.executable,str(Path(__file__).resolve()),'worker'],capture_output=True,text=True,timeout=180)
        result={'status':'complete'if process.returncode==0 else'error','returncode':process.returncode,
                'stdout':process.stdout,'stderr':process.stderr}
    except subprocess.TimeoutExpired as err:
        result={'status':'timeout','stop_reason':'180-second wall-clock bound',
                'stdout':err.stdout.decode()if isinstance(err.stdout,bytes)else err.stdout or ''}
    result.update(time_limit_seconds=180,elapsed_seconds=time.perf_counter()-start)
    save('attempt-101.json',result);print(json.dumps(result),flush=True)
    if result['status']!='complete':raise SystemExit(1)


if __name__=='__main__':main()
