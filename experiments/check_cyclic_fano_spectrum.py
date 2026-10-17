#!/usr/bin/env python3
"""Independent stdlib audit of the finite cyclic-Fano fiber spectrum.

Uses no CAS or primary construction imports. Identifies the modular quotient
from its cyclic commuting representation, checks a Krylov companion relation,
and verifies the exact Q(i) local jet with Fraction arithmetic.
"""
from pathlib import Path
from fractions import Fraction as Q
import hashlib
import json
import time

ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'results/cyclic-fano-spectrum'
FIBER=ROOT/'results/cyclic-fano-fibers'
P=101
N=120
SOURCE_HASH='f409a8993bcaeb9d5961dd46095d121f96ded4969aaf6ee6973744680cb380d4'
INFINITY_HASH='3c18a5e9bdabdeba01e10ea461951d0ef838ffb2917cc57a05c04c68a30484f9'
GROEBNER_HASH='0a5d3953f1324d8773896119649ce57ca97c7ec629d77af9184547eac7edafd5'

def sha(path):return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def qmod(value):
    q=Q(value);return q.numerator*pow(q.denominator,-1,P)%P
def cmod(pair):return (qmod(pair[0])+10*qmod(pair[1]))%P
def eyevector(j,n=N):return [int(k==j)for k in range(n)]
def columns(matrix):return [[(i,v)for i,v in enumerate(col)if v]for col in zip(*matrix)]
def mv(cols,vector):
    out=[0]*len(vector)
    for j,value in enumerate(vector):
        if value:
            for i,entry in cols[j]:out[i]+=value*entry
    return [v%P for v in out]
def linear_combination(coefficients,vectors):
    return [sum(c*v[j]for c,v in zip(coefficients,vectors))%P for j in range(N)]
def trim(poly):
    poly=[x%P for x in poly]
    while poly and poly[-1]==0:poly.pop()
    return poly
def padd(a,b,scale=1):
    c=a[:]+[0]*max(0,len(b)-len(a))
    for j,x in enumerate(b):c[j]=(c[j]+scale*x)%P
    return trim(c)
def pmul(a,b):
    if not a or not b:return []
    c=[0]*(len(a)+len(b)-1)
    for j,x in enumerate(a):
        for k,y in enumerate(b):c[j+k]+=x*y
    return trim(c)
def pdiv(a,b):
    a=trim(a);b=trim(b);assert b
    out=[0]*max(0,len(a)-len(b)+1);inv=pow(b[-1],-1,P)
    while len(a)>=len(b):
        degree=len(a)-len(b);coefficient=a[-1]*inv%P;out[degree]=coefficient
        for j,x in enumerate(b):a[j+degree]=(a[j+degree]-coefficient*x)%P
        a=trim(a)
    return trim(out),a
def pgcd(a,b):
    while b:a,b=b,pdiv(a,b)[1]
    return [(x*pow(a[-1],-1,P))%P for x in a]if a else []
def ppow(a,n,modulus):
    out=[1]
    while n:
        if n&1:out=pdiv(pmul(out,a),modulus)[1]
        a=pdiv(pmul(a,a),modulus)[1];n//=2
    return out
def irreducible(poly):
    degree=len(poly)-1;assert degree>0 and poly[-1]==1
    x=[0,1];frob=x;cache={0:x}
    for k in range(1,degree+1):frob=ppow(frob,P,poly);cache[k]=frob
    assert pdiv(padd(cache[degree],x,-1),poly)[1]==[]
    factors=[];n=degree;prime=2
    while prime*prime<=n:
        if n%prime==0:
            factors.append(prime)
            while n%prime==0:n//=prime
        prime+=1
    if n>1:factors.append(n)
    for prime in factors:assert pgcd(poly,padd(cache[degree//prime],x,-1))==[1]

def eliminate(matrix):
    """Return rank, original row choices, pivot columns, and square determinant."""
    a=[row[:]for row in matrix];m=len(a);n=len(a[0]);labels=list(range(m))
    row=0;choices=[];pivots=[];det=1;sign=1
    for col in range(n):
        found=next((k for k in range(row,m)if a[k][col]%P),None)
        if found is None:continue
        if found!=row:a[row],a[found]=a[found],a[row];labels[row],labels[found]=labels[found],labels[row];sign=-sign
        pivot=a[row][col]%P;det=det*pivot%P;inv=pow(pivot,-1,P)
        choices.append(labels[row]);pivots.append(col)
        for k in range(row+1,m):
            factor=a[k][col]*inv%P
            if factor:a[k][col:]=[(x-factor*y)%P for x,y in zip(a[k][col:],a[row][col:])]
        row+=1
        if row==m:break
    return row,choices,pivots,(sign*det)%P if m==n==row else None

ZERO=(Q(0),Q(0));ONE=(Q(1),Q(0));II=(Q(0),Q(1))
def ca(a,b):return (a[0]+b[0],a[1]+b[1])
def cm(a,b):return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
def cp(a,n):
    out=ONE
    for _ in range(n):out=cm(out,a)
    return out
def exact_value(terms,point,derivative=None):
    out=ZERO
    for term in terms:
        mon=term['powers'][:];coefficient=tuple(map(Q,term['coefficient']))
        if derivative is not None:
            factor=mon[derivative]
            if not factor:continue
            coefficient=cm(coefficient,(Q(factor),Q(0)));mon[derivative]-=1
        for x,n in zip(point,mon):coefficient=cm(coefficient,cp(x,n))
        out=ca(out,coefficient)
    return out
def smul(a,b):
    out=[ZERO]*4
    for j,x in enumerate(a):
        for k,y in enumerate(b[:4-j]):out[j+k]=ca(out[j+k],cm(x,y))
    return out
def spow(a,n):
    out=[ONE,ZERO,ZERO,ZERO]
    for _ in range(n):out=smul(out,a)
    return out
def jet_value(terms,series):
    out=[ZERO]*4
    for term in terms:
        value=[tuple(map(Q,term['coefficient'])),ZERO,ZERO,ZERO]
        for x,n in zip(series,term['powers']):value=smul(value,spow(x,n))
        out=[ca(x,y)for x,y in zip(out,value)]
    return out
def exact_strings(pair):return list(map(str,pair))
def assert_equal(a,b):assert a==b
def rejected(operation):
    try:operation()
    except AssertionError:return 1
    raise AssertionError('Mutation was not detected')

def main():
    assert __debug__,'Run without -O'
    start=time.monotonic();path=HERE/'spectrum-101.json';packet=load(path)
    source=load(FIBER/'fiber-equations.json');infinity=load(FIBER/'infinity-witness.json')
    assert sha(FIBER/'fiber-equations.json')==SOURCE_HASH==packet['source_packet_sha256']
    assert sha(FIBER/'infinity-witness.json')==INFINITY_HASH==packet['infinity_witness_sha256']
    assert sha(FIBER/'groebner-101.json')==GROEBNER_HASH==packet['groebner_packet_sha256']
    assert sha(ROOT/'experiments/cyclic_fano_spectrum.py')==packet['producer_sha256']
    assert packet['prime']==P and packet['i_image']==10 and packet['dimension']==N
    assert 10*10%P==P-1
    polynomials=[{tuple(t['powers']):cmod(t['coefficient'])for t in raw if cmod(t['coefficient'])}
                 for raw in source['remaining_equations']]
    assert [max(map(sum,p))for p in polynomials]==[4,5,6]

    # The previous full-row-rank leading-form map provides the dimension upper bound.
    rowmon=list(map(tuple,infinity['rows']));rowindex={m:j for j,m in enumerate(rowmon)}
    assert len(rowindex)==105 and all(sum(m)==13 for m in rowmon)
    macaulay=[]
    for raw in infinity['columns']:
        k=raw['source_equation_index'];shift=raw['multiplier_powers'];assert sum(shift)==13-[4,5,6][k]
        column=[0]*105
        for mon,value in polynomials[k].items():
            if sum(mon)==[4,5,6][k]:column[rowindex[tuple(x+y for x,y in zip(mon,shift))]]=value
        assert [[j,v]for j,v in enumerate(column)if v]==raw['entries'];macaulay.append(column)
    selected=infinity['selected_columns'];assert len(set(selected))==105
    macaulay_det=eliminate([[macaulay[j][i]for j in selected]for i in range(105)])[3]
    assert macaulay_det==47==infinity['selected_minor_determinant_mod_p']

    basis=list(map(tuple,packet['basis_order']));assert len(basis)==len(set(basis))==N
    unit=packet['unit_basis_index'];assert basis[unit]==(0,0,0)
    dense=[packet['multiplication_matrices'][name]for name in ('b','c','v')]
    for matrix in dense:assert len(matrix)==N and all(len(row)==N and all(type(x)==int and 0<=x<P for x in row)for row in matrix)
    operators=[columns(m)for m in dense]
    # Commutation is verified on all 120 coordinate vectors, with own arithmetic.
    for a in range(3):
        for b in range(a):
            for j in range(N):assert mv(operators[a],[row[j]for row in dense[b]])==mv(operators[b],[row[j]for row in dense[a]])
    cache={(0,0,0):eyevector(unit)}
    def orbit(mon):
        if mon not in cache:
            variable=next(j for j,v in enumerate(mon)if v);smaller=list(mon);smaller[variable]-=1
            cache[mon]=mv(operators[variable],orbit(tuple(smaller)))
        return cache[mon]
    for j,mon in enumerate(basis):assert orbit(mon)==eyevector(j)
    for polynomial in polynomials:
        total=[0]*N
        for mon,value in polynomial.items():total=[(x+value*y)%P for x,y in zip(total,orbit(mon))]
        assert total==[0]*N

    # A full Krylov basis proves charpoly and minimal polynomial without FLINT.
    chosen=next(a for a in packet['linear_form_attempts']if a['linear_form_weights']==[1,2,3])
    L=[[sum(w*dense[k][i][j]for k,w in enumerate((1,2,3)))%P for j in range(N)]for i in range(N)]
    Lop=columns(L);vectors=[eyevector(unit)]
    for _ in range(N):vectors.append(mv(Lop,vectors[-1]))
    krylov_det=eliminate([list(row)for row in zip(*vectors[:N])])[3]
    assert krylov_det is not None and krylov_det!=0
    characteristic=trim(chosen['characteristic_polynomial_ascending'])
    assert len(characteristic)==N+1 and characteristic[-1]==1
    relation=[sum(coefficient*vector[j]for coefficient,vector in zip(characteristic,vectors))%P for j in range(N)]
    assert relation==[0]*N
    assert chosen['minimal_polynomial_ascending']==characteristic
    derivative=[j*characteristic[j]%P for j in range(1,len(characteristic))]
    gcd=pgcd(characteristic,derivative)
    assert gcd==chosen['characteristic_derivative_gcd_ascending'] and len(gcd)==3
    product=[1];factor_summary=[]
    for factor in chosen['factors']:
        polynomial=trim(factor['coefficients_ascending']);assert len(polynomial)-1==factor['degree']
        irreducible(polynomial)
        for _ in range(factor['multiplicity']):product=pmul(product,polynomial)
        factor_summary.append({'degree':factor['degree'],'multiplicity':factor['multiplicity']})
    assert product==characteristic
    cubic=pmul(pmul([10,1],[10,1]),[10,1]);other,remainder=pdiv(characteristic,cubic)
    assert remainder==[] and pgcd(cubic,other)==[1]
    kernel_growth=[len(pgcd(characteristic,ppow([10,1],j,characteristic)))-1 for j in (1,2,3,4)]
    assert kernel_growth==[1,2,3,3]

    # Check every reported trial. An annihilator of the cyclic unit annihilates
    # the entire commutative representation. Krylov rank proves minimality.
    # Only degree0/1/2 remains between each minimal and characteristic polynomial;
    # traces of A and A^2 recover that remaining factor without a CAS routine.
    trial_receipts=[]
    for attempt in packet['linear_form_attempts']:
        weights=attempt['linear_form_weights']
        matrix=[[sum(w*dense[k][i][j]for k,w in enumerate(weights))%P for j in range(N)]for i in range(N)]
        operator=columns(matrix);minimal=trim(attempt['minimal_polynomial_ascending']);degree=len(minimal)-1
        assert minimal[-1]==1 and degree==attempt['minimal_degree'] and N-2<=degree<=N
        powers=[eyevector(unit)]
        for _ in range(degree):powers.append(mv(operator,powers[-1]))
        assert eliminate([list(row)for row in zip(*powers[:degree])])[0]==degree
        assert linear_combination(minimal,powers)==[0]*N
        trace1=sum(matrix[j][j]for j in range(N))%P
        trace2=sum(matrix[i][j]*matrix[j][i]for i in range(N)for j in range(N))%P
        remaining1=(trace1+minimal[-2])%P
        remaining2=(trace2-minimal[-2]**2+2*minimal[-3])%P
        if degree==N:
            assert remaining1==remaining2==0;quotient=[1]
        elif degree==N-1:
            assert remaining2==remaining1**2%P;quotient=[-remaining1%P,1]
        else:quotient=[(remaining1**2-remaining2)*pow(2,-1,P)%P,-remaining1%P,1]
        trial_characteristic=pmul(minimal,quotient)
        assert trial_characteristic==attempt['characteristic_polynomial_ascending']
        trial_gcd=pgcd(trial_characteristic,[j*trial_characteristic[j]%P for j in range(1,N+1)])
        assert trial_gcd==attempt['characteristic_derivative_gcd_ascending']
        assert attempt['squarefree_characteristic_polynomial']==(trial_gcd==[1])
        trial_product=[1]
        for factor in attempt['factors']:
            polynomial=trim(factor['coefficients_ascending']);irreducible(polynomial)
            assert len(polynomial)-1==factor['degree']
            for _ in range(factor['multiplicity']):trial_product=pmul(trial_product,polynomial)
        assert trial_product==trial_characteristic
        trial_receipts.append({'weights':weights,'minimal_degree':degree,
                               'characteristic_derivative_gcd_degree':len(trial_gcd)-1})
    assert len(trial_receipts)==7 and packet['squarefree_characteristic_polynomial_found'] is False

    selected_packet=packet['selected_operator']
    assert packet['linear_form_attempts'][selected_packet['attempt_index']]==chosen
    assert selected_packet['linear_form_weights']==[1,2,3]
    assert selected_packet['krylov_rank']==N and selected_packet['krylov_determinant']==krylov_det
    for k,name in enumerate(('b','c','v')):
        coordinate_poly=selected_packet['coordinate_polynomials_in_L_ascending'][name]
        assert len(coordinate_poly)<=N
        assert linear_combination(coordinate_poly,vectors)==[row[unit]for row in dense[k]]

    # Polynomial CRT idempotents are verified algebraically. They need not be
    # orthogonal projections for a Hermitian form in the chosen monomial basis.
    projectors=selected_packet['projectors'];assert len(projectors)==len(chosen['factors'])
    projector_polynomials=[];projector_ranks=[];sum_projectors=[];exceptional=None
    for projector,factor in zip(projectors,chosen['factors']):
        f=trim(projector['factor_coefficients_ascending']);power=projector['multiplicity']
        assert f==factor['coefficients_ascending'] and power==factor['multiplicity']
        assert projector['factor_degree']==len(f)-1
        primary=[1]
        for _ in range(power):primary=pmul(primary,f)
        complementary,remainder=pdiv(characteristic,primary);assert remainder==[]
        e=trim(projector['projector_coefficients_ascending']);assert len(e)<=N
        assert pdiv(e,primary)[1]==[1] and pdiv(e,complementary)[1]==[]
        assert pdiv(padd(pmul(e,e),e,-1),characteristic)[1]==[]
        assert projector['projector_rank']==len(primary)-1
        for previous in projector_polynomials:assert pdiv(pmul(e,previous),characteristic)[1]==[]
        projector_polynomials.append(e);projector_ranks.append(len(primary)-1)
        sum_projectors=padd(sum_projectors,e)
        if f==[10,1]:assert power==3;exceptional=e
    assert pdiv(sum_projectors,characteristic)[1]==[1] and sum(projector_ranks)==N and exceptional is not None
    block=selected_packet['nonreduced_primary_block'];assert block['eigenvalue']==91
    E=block['projector_matrix'];Nil=block['nilpotent_matrix']
    for matrix in (E,Nil):assert len(matrix)==N and all(len(row)==N and all(type(x)==int and 0<=x<P for x in row)for row in matrix)
    Eop=columns(E);Nop=columns(Nil);E1=linear_combination(exceptional,vectors)
    expected_E_power=E1
    for vector in vectors[:N]:
        assert mv(Eop,vector)==expected_E_power
        expected_E_power=mv(Lop,expected_E_power)
    for j in range(N):
        column=[row[j]for row in E]
        assert [row[j]for row in Nil]==[(x-91*y)%P for x,y in zip(mv(Lop,column),column)]
    NE1=mv(Nop,E1);N2E1=mv(Nop,NE1);assert mv(Nop,N2E1)==[0]*N
    chain=[N2E1,NE1,E1]
    assert eliminate([list(row)for row in zip(*chain)])[0]==3
    assert block['chain_basis_columns_N2E1_NE1_E1']==[list(row)for row in zip(*chain)]
    assert block['restricted_nilpotent_matrix']==[[0,1,0],[0,0,1],[0,0,0]]
    assert block['ranks_E_N_N2_N3']==[3,2,1,0]
    assert block['local_kernel_dimensions']==[0,1,2,3] and block['exact_nilpotency_index']==3
    assert selected_packet['separates_geometric_points_over_algebraic_closure'] is True
    assert selected_packet['geometric_point_count_over_algebraic_closure']==118 and packet['geometric_separator_found'] is True

    # Newton's identities use no divisions, including at indices divisible by101.
    traces=[N%P]
    for k in range(1,2*N-1):
        if k<=N:
            value=-sum(characteristic[N-j]*traces[k-j]for j in range(1,k))-k*characteristic[N-k]
        else:value=-sum(characteristic[N-j]*traces[k-j]for j in range(1,N+1))
        traces.append(value%P)
    hankel=[[traces[i+j]for j in range(N)]for i in range(N)]
    trace_rank,trace_rows,trace_cols,_=eliminate(hankel)
    assert trace_rank==118
    trace_minor=eliminate([[hankel[i][j]for j in trace_cols]for i in trace_rows])[3]
    assert trace_minor not in (None,0)
    assert selected_packet['power_traces']==traces
    assert selected_packet['trace_form_rank']==trace_rank and selected_packet['trace_form_nullity']==2
    saved_rows=selected_packet['trace_form_minor_rows'];saved_cols=selected_packet['trace_form_minor_columns']
    assert len(saved_rows)==len(set(saved_rows))==len(saved_cols)==len(set(saved_cols))==118
    assert all(0<=i<N for i in saved_rows+saved_cols)
    saved_trace_minor=eliminate([[hankel[i][j]for j in saved_cols]for i in saved_rows])[3]
    assert saved_trace_minor==selected_packet['trace_form_minor_determinant']!=0

    # Exact characteristic-zero singular point and cubic local algebra.
    point=(ZERO,II,(Q(0),Q(-1)))
    equations=source['remaining_equations']
    assert all(exact_value(eq,point)==ZERO for eq in equations)
    jacobian=[[exact_value(eq,point,k)for k in range(3)]for eq in equations]
    expected=[[ZERO,(Q(0),Q(6)),(Q(0),Q(-24))],
              [ZERO,(Q(0),Q(12)),(Q(0),Q(-18))],
              [ZERO,(Q(0),Q(6)),ZERO]]
    assert jacobian==expected
    determinant=ca(cm(jacobian[0][1],jacobian[1][2]),cm((Q(-1),Q(0)),cm(jacobian[0][2],jacobian[1][1])))
    assert determinant==(Q(-180),Q(0))
    alpha=(Q(-8,175),Q(1,6));beta=(Q(8,175),Q(-1,6))
    series=[[ZERO,ONE,ZERO,ZERO],[II,ZERO,ZERO,alpha],[(Q(0),Q(-1)),ZERO,ZERO,beta]]
    values=[jet_value(eq,series)for eq in equations]
    obstruction=(Q(-1),Q(-48,175))
    assert values==[[ZERO]*4,[ZERO]*4,[ZERO,ZERO,ZERO,obstruction]]
    swapped=packet['characteristic_zero_swapped_point']
    assert swapped['point']==[exact_strings(x)for x in point] and swapped['coordinate_order']==['b','c','v']
    assert swapped['equation_values']==[['0','0']]*3
    assert swapped['jacobian']==[[exact_strings(x)for x in row]for row in jacobian]
    assert swapped['jacobian_rank']==2 and swapped['selected_rows']==[0,1] and swapped['selected_columns']==[1,2]
    assert swapped['nonzero_minor']==exact_strings(determinant) and swapped['tangent_kernel_basis']==[[1,0,0]]
    assert swapped['c_jet_coefficients_ascending']==[exact_strings(x)for x in series[1]]
    assert swapped['v_jet_coefficients_ascending']==[exact_strings(x)for x in series[2]]
    assert swapped['remaining_scalar_cubic_coefficient']==exact_strings(obstruction) and swapped['local_length']==3
    inference=packet['characteristic_zero_inference']
    assert (inference['geometric_points_over_C'],inference['one_point_length'],inference['remaining_simple_points'])==(118,3,117)

    negative=0
    altered=characteristic[:];altered[0]=(altered[0]+1)%P
    altered_relation=[sum(coefficient*vector[j]for coefficient,vector in zip(altered,vectors))%P for j in range(N)]
    negative+=rejected(lambda:assert_equal(altered_relation,[0]*N))
    altered_L=[row[:]for row in L];altered_L[0][unit]=(altered_L[0][unit]+1)%P
    negative+=rejected(lambda:assert_equal(mv(columns(altered_L),vectors[0]),vectors[1]))
    negative+=rejected(lambda:assert_equal(macaulay_det,(macaulay_det+1)%P))
    negative+=rejected(lambda:assert_equal(trace_minor,(trace_minor+1)%P))
    altered_series=[row[:]for row in series];altered_series[1][3]=ca(alpha,ONE)
    negative+=rejected(lambda:assert_equal(jet_value(equations[0],altered_series),[ZERO]*4))
    negative+=rejected(lambda:assert_equal(jet_value(equations[2],series)[3],ZERO))
    altered_projector=padd(exceptional,[1])
    negative+=rejected(lambda:assert_equal(pdiv(altered_projector,cubic)[1],[1]))
    altered_N=[row[:]for row in Nil];altered_N[0][unit]=(altered_N[0][unit]+1)%P
    negative+=rejected(lambda:assert_equal(mv(columns(altered_N),eyevector(unit)),[row[unit]for row in Nil]))
    altered_trace=traces[:];altered_trace[0]=(altered_trace[0]+1)%P
    negative+=rejected(lambda:assert_equal(altered_trace,selected_packet['power_traces']))

    receipt={'schema':'cyclic-fano-spectrum-independent-v1','status':'PASS',
             'spectrum_packet_lf_sha256':sha(path),'checker_lf_sha256':sha(Path(__file__)),
             'fiber_packet_lf_sha256':SOURCE_HASH,'infinity_packet_lf_sha256':INFINITY_HASH,
             'arithmetic':'Python standard-library integers and Fraction; no CAS imports',
             'prime':P,'i_image':10,'dimension':N,
             'quotient_identification':{'Macaulay_minor_dimension':105,'Macaulay_minor_mod101':macaulay_det,
                                        'pairwise_commutation_checks':3*N,'unit_monomial_orbits_checked':N,
                                        'original_equations_on_cyclic_unit_checked':3,
                                        'argument':'The commuting cyclic representation is a dimension120 quotient of the original finite complete intersection, whose dimension is120. It is therefore the entire quotient algebra.'},
             'selected_operator':{'weights':[1,2,3],'Krylov_basis_determinant_mod101':krylov_det,
                                  'characteristic_equals_minimal_degree':120,
                                  'characteristic_polynomial_ascending':characteristic,
                                  'derivative_gcd_ascending':gcd,
                                  'irreducible_factors_verified':factor_summary,
                                  'kernel_growth_at_eigenvalue_91':kernel_growth,
                                  'coordinate_polynomials_verified':3,'CRT_projectors_verified':6,
                                  'projector_ranks':projector_ranks,'exported_projector_and_nilpotent_matrices_verified':True,
                                  'exported_Jordan_chain_verified':True,
                                  'conclusion':'One local length-three nilpotent block, one simple rational block, and116 simple geometric points in extension-field blocks, over the algebraic closure of F101.'},
             'all_linear_form_attempts_independently_verified':trial_receipts,
             'algebraic_trace_pairing':{'basis':'1,L,...,L^119','power_traces_mod101':traces,
                                        'rank_mod101':trace_rank,'nonzero_minor_rows':trace_rows,
                                        'nonzero_minor_columns':trace_cols,'nonzero_minor_determinant_mod101':trace_minor,
                                        'producer_selected_minor_determinant_checked':saved_trace_minor,
                                        'scope':'Symmetric bilinear algebra trace; not a positive Hermitian Gram matrix.'},
             'exact_local_Qi_audit':{'point':[[str(x)for x in pair]for pair in point],
                                    'Jacobian':[[exact_strings(x)for x in row]for row in jacobian],
                                    'Jacobian_rank':2,'first_two_equations_cv_minor':'-180',
                                    'c_series_b3_coefficient':exact_strings(alpha),
                                    'v_series_b3_coefficient':exact_strings(beta),
                                    'third_equation_b3_coefficient':exact_strings(obstruction),
                                    'local_length':3,
                                    'argument':'The first two equations solve c,v formally in b because their minor is nonzero. The third restricted equation has nonzero order-three term, so the completed local algebra is Q(i)[[b]]/(b^3).'},
             'characteristic_zero_conclusion':{
                 'geometric_points':118,'triple_points':1,'other_simple_points':117,
                 'argument':[
                     'The degree13 leading-form minor is a unit in Z[i] localized at (101,i-10), proving finiteness over that DVR.',
                     'Generic and special fiber dimensions120 make this finite module free of rank120; the modular standard monomials lift to a basis.',
                     'The nonzero size118 algebraic trace minor lifts to characteristic zero and proves at least118 geometric points.',
                     'The independently verified exact length-three point plus total length120 allows at most118 geometric points. Equality gives this triple point and117 simple points.'
                 ]},
             'negative_controls_rejected':negative,
             'limits':'No covering degree for the seed component, global branch divisor, supporting denominator, certificate, or Lean proof is established. Finite-field factor degrees are not complex eigenvalue locations.',
             'elapsed_seconds':time.monotonic()-start}
    HERE.mkdir(parents=True,exist_ok=True)
    out=HERE/'independent-validation.json';out.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':'PASS','Krylov_determinant':krylov_det,'trace_rank':trace_rank,
                      'trace_minor':trace_minor,'exact_local_length':3,'geometric_points_char0':118,
                      'negative_controls':negative,'seconds':receipt['elapsed_seconds']}))

if __name__=='__main__':main()
