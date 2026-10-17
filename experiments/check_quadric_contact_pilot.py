#!/usr/bin/env python3
"""Independent exact audit of one quartic denominator for quadric-contact-broken.

Only Python's standard library is used. Source expressions are parsed through a
restricted AST; all six-variable polynomials use sparse Fraction arithmetic.
No discovery module or CAS is imported.
"""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations
from math import comb
import ast
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'results/quadric-contact-pilot'
VARIABLES=('X0','X1','X2','Y0','Y1','Y2')
ZERO=(0,)*6
SOURCE_SHA='ecec257b5b6b8efe3b8345f9c71fc19f8120cf4172923ac4fae8a20c1a8179b4'

def sha(path):return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def clean(a):return {m:Q(v)for m,v in a.items()if v}
def add(a,b,scale=1):
    out=a.copy()
    for m,v in b.items():out[m]=out.get(m,0)+scale*v
    return clean(out)
def scalar(a,q):return clean({m:q*v for m,v in a.items()})
def mul(a,b):
    out={}
    for m,x in a.items():
        for n,y in b.items():
            k=tuple(i+j for i,j in zip(m,n));out[k]=out.get(k,0)+x*y
    return clean(out)
def power(a,n):
    assert type(n)==int and n>=0
    out={ZERO:Q(1)}
    while n:
        if n&1:out=mul(out,a)
        n//=2
        if n:a=mul(a,a)
    return out
def derivative(a,i):
    out={}
    for m,v in a.items():
        if m[i]:
            n=list(m);n[i]-=1;out[tuple(n)]=v*m[i]
    return clean(out)
def total(values):
    out={}
    for a in values:out=add(out,a)
    return out
def contraction(field,polynomial):return total(mul(n,derivative(polynomial,i))for i,n in enumerate(field))
def divergence(field):return total(derivative(n,i)for i,n in enumerate(field))
def B(D,field):return add(mul(D,divergence(field)),contraction(field,D),-1)
def parse(text):
    def visit(node):
        if isinstance(node,ast.Constant):
            assert type(node.value)==int;return {ZERO:Q(node.value)}if node.value else {}
        if isinstance(node,ast.Name):
            assert node.id in VARIABLES
            mon=[0]*6;mon[VARIABLES.index(node.id)]=1;return {tuple(mon):Q(1)}
        if isinstance(node,ast.UnaryOp):
            assert isinstance(node.op,(ast.USub,ast.UAdd))
            return scalar(visit(node.operand),-1 if isinstance(node.op,ast.USub)else 1)
        assert isinstance(node,ast.BinOp)
        if isinstance(node.op,ast.Pow):
            assert isinstance(node.right,ast.Constant)and type(node.right.value)==int
            return power(visit(node.left),node.right.value)
        left,right=visit(node.left),visit(node.right)
        if isinstance(node.op,ast.Add):return add(left,right)
        if isinstance(node.op,ast.Sub):return add(left,right,-1)
        if isinstance(node.op,ast.Mult):return mul(left,right)
        assert isinstance(node.op,ast.Div)and set(right)=={ZERO}and right[ZERO]
        return scalar(left,1/right[ZERO])
    return visit(ast.parse(text,mode='eval').body)
def decode(terms):
    out={}
    for term in terms:
        m=tuple(term['powers']);assert len(m)==6 and all(type(i)==int and i>=0 for i in m)
        assert m not in out;out[m]=Q(term['coefficient']);assert out[m]
    return out
def coefficient_entries(polynomial,index):return [[index[m],str(v)]for m,v in sorted(polynomial.items(),key=lambda item:index[item[0]])]
def qrank(vectors):
    pivots={}
    for vector in vectors:
        row=clean(vector)
        while row:
            pivot=max(row)
            if pivot not in pivots:
                q=row[pivot];pivots[pivot]=scalar(row,1/q);break
            row=add(row,pivots[pivot],-row[pivot])
    return len(pivots)
def check_equal(a,b):assert a==b
def rejects(fn):
    try:fn()
    except AssertionError:return 1
    raise AssertionError('Mutation was not detected')
def mod5(a):
    out={}
    for m,v in a.items():
        assert v.denominator%5
        value=v.numerator*pow(v.denominator,-1,5)%5
        if value:out[m]=value
    return out

def main():
    assert __debug__,'Run without -O'
    packet=load(HERE/'pilot.json');target=load(HERE/'target.json')
    assert packet['schema']=='quadric-contact-quartic-pilot-v1'
    assert packet['instance']==target['instance']=='quadric-contact-broken'
    assert sha(HERE/'target.json')==packet['frozen_target_sha256']
    assert sha(ROOT/'experiments/quadric_contact_pilot.py')==packet['producer_sha256']
    for name,value in target['source_sha256'].items():assert sha(HERE/'source'/name)==value
    assert sha(HERE/'source/instance.rec')==SOURCE_SHA
    text=(HERE/'source/instance.rec').read_text(encoding='utf-8')
    values={};key=None
    for line in text.splitlines():
        match=re.match(r'^(q|F|A):\s*(.*)$',line)
        if match:key=match[1];values[key]=match[2]
        elif key and line.startswith('  '):values[key]+=' '+line.strip()
        else:key=None
    assert values==target['target'] and values['q']=='1'
    F,A=map(parse,(values['F'],values['A']))
    assert len(F)==16 and len(A)==2 and all(sum(m)==6 for m in F|A)
    D=parse('4*(X0**2+Y0**2)*X0*Y0+(5/7)*X1*Y1*(X2**2+2*Y2**2)')
    initial=[parse('-X1**2*X0*Y0**2'),{},{},parse('X1**2*X0**2*Y0'),{},{}]
    assert decode(packet['denominator'])==D
    assert list(map(decode,packet['initial_numerator']))==initial
    assert all(sum(m)==4 for m in D) and all(sum(m)==5 for n in initial for m in n)
    assert contraction(initial,F)==mul(A,D) and packet['E1_identity_exact'] is True
    residual=B(D,initial)
    expected_residual=parse('(5/7)*X1**3*Y1*(X2**2+2*Y2**2)*(X0**2-Y0**2)')
    assert residual==expected_residual==decode(packet['E2_initial_residual'])

    # Smooth Fermat reduction proves the homogeneous gradient sequence regular
    # in characteristic zero. All degree5 syzygies are then constant Koszul.
    fermat={tuple(6*int(i==j)for i in range(6)):1 for j in range(6)}
    assert mod5(F)==fermat
    grad=[derivative(F,i)for i in range(6)]
    for j,g in enumerate(grad):assert mod5(g)=={tuple(5*int(i==j)for i in range(6)):1}

    reconstructed=[];koszul_indices=[];quadratic_monomials=[]
    assert len(packet['matrix_columns'])==36
    for column in packet['matrix_columns']:
        if column['kind']=='Koszul':
            i,j=column['indices'];assert 0<=i<j<6
            field=[{}for _ in range(6)];field[i]=grad[j];field[j]=scalar(grad[i],-1)
            assert contraction(field,F)=={} and divergence(field)=={}
            reconstructed.append(B(D,field));koszul_indices.append((i,j))
        else:
            assert column['kind']=='F_quotient'and column['sign']==-1
            mon=tuple(column['multiplier_powers']);assert len(mon)==6 and sum(mon)==2 and all(type(x)==int and x>=0 for x in mon)
            reconstructed.append(scalar(mul(F,{mon:Q(1)}),-1));quadratic_monomials.append(mon)
    assert sorted(koszul_indices)==list(combinations(range(6),2))
    assert len(set(quadratic_monomials))==len(quadratic_monomials)==comb(7,5)==21
    rhs=scalar(residual,-1)
    rows=list(map(tuple,packet['coefficient_rows']));index={m:i for i,m in enumerate(rows)}
    support=set(rhs)
    for column in reconstructed:support.update(column)
    assert len(rows)==len(index)==487 and set(rows)==support and all(sum(m)==8 for m in rows)
    assert packet['matrix_shape']==[487,36] and packet['full_homogeneous_degree8_row_count']==comb(13,5)==1287
    for physical,exported in zip(reconstructed,packet['matrix_columns']):assert coefficient_entries(physical,index)==exported['entries']
    assert coefficient_entries(rhs,index)==packet['rhs_entries']
    rank=qrank(reconstructed);augmented=qrank(reconstructed+[rhs])
    assert rank==packet['coefficient_rank']==36 and augmented==packet['augmented_rank']==37
    assert packet['consistent'] is False and packet['solution_coefficients'] is None
    functional={rows[i]:Q(q)for i,q in packet['obstruction_functional']}
    assert len(functional)==len(packet['obstruction_functional'])==1
    witness_mon=(2,3,2,0,1,0)
    assert functional=={witness_mon:Q(-7,5)}
    def pairing(poly,dual=functional):return sum(q*poly.get(m,0)for m,q in dual.items())
    assert all(pairing(column)==0 for column in reconstructed)
    assert pairing(rhs)==1 and residual[witness_mon]==Q(5,7)

    negative=0
    negative+=rejects(lambda:check_equal(contraction(initial,F),mul(A,scalar(D,2))))
    changed_column=add(reconstructed[0],{witness_mon:Q(1)})
    negative+=rejects(lambda:check_equal(pairing(changed_column),0))
    negative+=rejects(lambda:check_equal(pairing(rhs,{witness_mon:Q(-14,5)}),1))
    changed_residual=add(residual,{witness_mon:Q(1)})
    negative+=rejects(lambda:check_equal(B(D,initial),changed_residual))
    negative+=rejects(lambda:check_equal(mod5(add(F,{(5,1,0,0,0,0):Q(1)})),fermat))
    receipt={
        'schema':'quadric-contact-pilot-independent-v1','status':'PASS',
        'checker_lf_sha256':sha(Path(__file__)),'pilot_lf_sha256':sha(HERE/'pilot.json'),
        'target_lf_sha256':sha(HERE/'target.json'),'instance_rec_lf_sha256':SOURCE_SHA,
        'arithmetic':'Python standard-library Fraction sparse polynomials and rational elimination; no CAS or producer imports',
        'target':{'instance':'quadric-contact-broken','q':1,'source_snapshot_commit':target['source_snapshot_commit']},
        'exact_E1_checked':True,'exact_E2_residual_checked':True,
        'smoothness':{'prime':5,'F_reduction':'sum(z_i^6)','gradient_reductions':'z_i^5 for i=0,...,5',
                      'argument':'The projective gradient zero locus is empty in the special fiber. Properness gives emptiness in characteristic zero. The six homogeneous gradients are a regular sequence in the six-variable polynomial ring.'},
        'complete_fixed_denominator_space':{
            'denominator_degree':4,'numerator_degree':5,'Koszul_directions':15,'quotient_degree':2,'quotient_monomials':21,
            'argument':'Euler normalization turns every legal fixed-D certificate into N(F)=AD. The regular gradient sequence has all its degree-five syzygies spanned by the constant Koszul fields. The full nonzero E2 quotient has degree two. No field parity restriction is imposed.',
            'denominator_admissibility':'A smooth sextic in P5 is geometrically irreducible; the nonzero quartic D is therefore relatively prime to F over C.'},
        'matrix':{'compressed_rows':487,'all_degree8_rows':1287,'columns':36,'rational_rank':rank,'rational_augmented_rank':augmented},
        'exact_obstruction':{'monomial_powers':list(witness_mon),'functional_coefficient':'-7/5',
                             'all_36_correction_pairings_zero':True,'rhs_pairing':'1','uncorrected_residual_coefficient':'5/7'},
        'conclusion':'Every legal homogeneous numerator with this particular quartic denominator is excluded, over C. The same holds for its nonzero scalar multiples.',
        'limits':'No exclusion of all quartic denominators, powers of this denominator, other supports, or certificates of arbitrary degree. No Lean proof or solution is produced.',
        'negative_controls_rejected':negative}
    out=HERE/'independent-validation.json';out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':'PASS','rank':rank,'augmented_rank':augmented,'dual_terms':1,
                      'full_fixed_denominator_scope':True,'negative_controls':negative}))

if __name__=='__main__':main()
