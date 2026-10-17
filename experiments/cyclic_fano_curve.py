#!/usr/bin/env python3
"""Exact free-line and finite-dimensional spectral audit for cyclic-triple-fano.

The output is a geometric partial result, not a denominator or HasCertificate.
The parameter family is a diagnostic; its specialization c=5/7 is the fixed
target. Matrix adjoints use the explicitly chosen coefficient inner products.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys
import time

import sympy as S

REPO=Path(__file__).resolve().parents[1]
HERE=REPO/'results'/'cyclic-fano-curve'
ID='cyclic-triple-fano'
COMMIT='d96911d725077e66a8f10848908be01a643b1714'


def sha(path):return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
def encode(value):
    value=S.expand(value)
    return [str(S.re(value)),str(S.im(value))]
def matrix_json(matrix):return [[encode(v)for v in row]for row in matrix.tolist()]


def exact_fields(path):
    fields={};active=None
    for line in path.read_text(encoding='utf-8').splitlines():
        matched=False
        for key in ('F','A','q'):
            if line.startswith(key+': '):
                fields[key]=line[len(key)+2:];active=key;matched=True;break
        if matched:continue
        if active in ('F','A')and line.startswith('  '):
            fields[active]+=' '+line.strip()
        else:active=None
    return fields


def calculate():
    start=time.perf_counter()
    record_path=HERE/'source'/'instance.rec'
    frozen=json.loads((HERE/'target.json').read_text(encoding='utf-8'))
    record=exact_fields(record_path)
    assert frozen['upstream_commit']==COMMIT and frozen['instance']==ID
    assert frozen['target']==record
    assert frozen['upstream_source_sha256']['data/'+ID+'/instance.rec']==sha(record_path)
    names=('X0','X1','X2','Y0','Y1','Y2')
    x=S.symbols(' '.join(names));lookup=dict(zip(names,x))
    F=S.Poly(S.sympify(record['F'],locals=lookup),*x,domain=S.QQ)
    A=S.Poly(S.sympify(record['A'],locals=lookup),*x,domain=S.QQ)
    assert record['q']=='1'
    Z=S.Symbol('Z');y=(x[0],x[1],Z,x[3],x[4],x[5]);weights=(1,1,3,1,1,1)
    G=0
    for mon,coef in F.terms():
        assert mon[2]%3==0
        new=list(mon);new[2]//=3
        G+=coef*S.prod(z**power for z,power in zip(y,new))
    G=S.expand(G)
    assert S.expand(G.subs(Z,x[2]**3)-F.as_expr())==0
    assert S.expand(3*x[2]**2*(x[0]*x[3]**3/3)-A.as_expr())==0
    s,t=S.symbols('s t');c=S.Symbol('c',real=True)
    phi=(0,s,0,S.I*s,t,S.I*t);sub=dict(zip(y,phi))
    assert S.expand(G.subs(sub))==0
    fermat=y[0]**6+y[1]**6+Z**2+y[3]**6+y[4]**6+y[5]**6
    interaction=S.expand((G-fermat)*S.Rational(7,5))
    assert S.Poly(interaction,*y).domain==S.ZZ
    family=S.expand(fermat+c*interaction)
    assert S.expand(family.subs(c,S.Rational(5,7))-G)==0
    assert S.expand(family.subs(sub))==0
    partials=[S.expand(S.diff(family,z).subs(sub))for z in y]
    rowmon=[s**(5-j)*t**j for j in range(6)]
    # Natural weighted order: each weight-one coordinate contributes a constant;
    # the weight-three coordinate contributes s²,st,t².
    labels=[];column_polynomials=[]
    for i,w in enumerate(weights):
        for j in range(w):
            mon=s**(w-1-j)*t**j
            labels.append({'coordinate':str(y[i]),'section':str(mon)})
            column_polynomials.append(S.expand(partials[i]*mon))
    M=S.Matrix([[S.Poly(poly,s,t).coeff_monomial(mon)for poly in column_polynomials]for mon in rowmon])
    fixed=M.subs(c,S.Rational(5,7))
    gram=S.simplify(M*M.conjugate().T)
    expected=S.diag(72,c*c,c*c,c*c,c*c,72)
    assert gram==expected
    fixed_gram=fixed*fixed.conjugate().T
    inverse=S.diag(S.Rational(1,72),S.Rational(49,25),S.Rational(49,25),S.Rational(49,25),S.Rational(49,25),S.Rational(1,72))
    assert fixed_gram*inverse==S.eye(6)
    right_inverse=fixed.conjugate().T*inverse
    assert fixed*right_inverse==S.eye(6)
    selected=[1,2,3,4,0,6]
    minor=S.factor(fixed[:,selected].det())
    assert minor==S.Rational(22500,2401)
    assert fixed.rank()==6 and M.subs(c,0).rank()==2
    eigenvalues={str(e):int(m)for e,m in fixed_gram.eigenvals().items()}
    assert eigenvalues=={'72':2,'25/49':4}
    small=S.Rational(25,49);large=S.Integer(72)
    lower_remainder=fixed_gram-small*S.eye(6)
    assert lower_remainder.is_diagonal() and all(v>=0 for v in lower_remainder.diagonal())
    right_gram=right_inverse.conjugate().T*right_inverse
    assert right_gram==inverse
    assert max(right_gram.eigenvals())==S.Rational(49,25)
    Psmall=(large*S.eye(6)-fixed_gram)/(large-small)
    Plarge=(fixed_gram-small*S.eye(6))/(large-small)
    assert Psmall**2==Psmall and Plarge**2==Plarge
    assert Psmall*Plarge==S.zeros(6)and Psmall+Plarge==S.eye(6)
    assert fixed_gram==small*Psmall+large*Plarge
    assert inverse==Psmall/small+Plarge/large
    assert inverse==((small+large)*S.eye(6)-fixed_gram)/(small*large)
    lam=S.Symbol('lambda')
    resolvent=S.diag(*[1/(lam-value)for value in fixed_gram.diagonal()])
    assert S.simplify((lam*S.eye(6)-fixed_gram)*resolvent)==S.eye(6)
    # Untwisted incidence derivative: 14 coefficient variables and7 equations.
    ordinary=[];untwisted_columns=[];untwisted_labels=[]
    for i,w in enumerate(weights):
        for j in range(w+1):
            mon=s**(w-j)*t**j
            untwisted_columns.append(S.expand(partials[i].subs(c,S.Rational(5,7))*mon))
            ordinary.append(i);untwisted_labels.append({'coordinate':str(y[i]),'section':str(mon)})
    untwisted=S.Matrix([[S.Poly(poly,s,t).coeff_monomial(s**(6-j)*t**j)for poly in untwisted_columns]for j in range(7)])
    assert untwisted.shape==(7,14)and untwisted.rank()==7
    kernel=S.Matrix.hstack(*untwisted.nullspace());assert kernel.shape==(14,7)
    # At[1:1], use the ordinary chartX1=1. Normalize the weight-three coordinate
    # by X1³ and the other coordinates by X1. This removes weighted scaling.
    chart=[0,2,3,4,5];point=[S.sympify(v).subs({s:1,t:1})for v in phi]
    evaluation=S.Matrix([[int(component==i)-weights[i]*point[i]*int(component==1)
                          for component in ordinary]for i in chart])
    evaluation_on_kernel=S.simplify(evaluation*kernel)
    assert evaluation_on_kernel.rank()==4
    # An explicit local three-parameter algebraic family, rather than only
    # the abstract assertion that a free curve has a covering deformation.
    a,b,c0,y0,d0,e0,f,g,h,j=S.symbols('a b c y d e f g h j')
    free=(a,b,c0);dependent=(y0,d0,e0,f,g,h,j)
    family_curve=(a*s+b*t,s,f*s**3+g*s**2*t+h*s*t**2+j*t**3,
                  y0*s+c0*t,t,d0*s+e0*t)
    parameter_base={a:0,b:0,c0:0,y0:S.I,d0:0,e0:S.I,f:0,g:0,h:0,j:0}
    incidence=S.Poly(S.expand(G.subs(dict(zip(y,family_curve)))),s,t)
    equations=[incidence.coeff_monomial(s**(6-k)*t**k)for k in range(7)]
    assert all(S.simplify(q.subs(parameter_base))==0 for q in equations)
    Jdependent=S.Matrix([[S.diff(q,z).subs(parameter_base)for z in dependent]for q in equations])
    Jfree=S.Matrix([[S.diff(q,z).subs(parameter_base)for z in free]for q in equations])
    family_det=S.simplify(Jdependent.det())
    assert family_det==-S.Rational(135000,2401)*S.I
    dependent_tangent=-Jdependent.inv()*Jfree
    assert Jdependent*dependent_tangent+Jfree==S.zeros(7,3)
    r=S.Symbol('r')
    affine_family=[S.sympify(family_curve[i]).subs({s:1,t:r})for i in chart]
    family_evaluation=[]
    point_base=dict(parameter_base);point_base[r]=1
    for expression in affine_family:
        entry=[]
        for k,z in enumerate(free):
            derivative=S.diff(expression,z)+sum(S.diff(expression,u)*dependent_tangent[l,k]for l,u in enumerate(dependent))
            entry.append(S.simplify(derivative.subs(point_base)))
        entry.append(S.simplify(S.diff(expression,r).subs(point_base)))
        family_evaluation.append(entry)
    family_evaluation=S.Matrix(family_evaluation)
    assert family_evaluation.rank()==4
    eval_rows=next(list(sel)for sel in itertools.combinations(range(5),4)
                   if family_evaluation[list(sel),:].det()!=0)
    eval_minor=S.simplify(family_evaluation[eval_rows,:].det())
    # Every point of the curve is smooth: derivatives6s^5 and6t^5 never vanish
    # simultaneously onP1; ordinary coordinates s,t also prove basepoint freedom.
    assert partials[1]==6*s**5 and partials[4]==6*t**5
    result={'schema':'cyclic-fano-free-curve-v1','instance':ID,'upstream_commit':COMMIT,
            'source_sha256':frozen['upstream_source_sha256'],
            'frozen_target_sha256':sha(HERE/'target.json'),'raw_instance_sha256':sha(record_path),
            'sha256_policy':'UTF-8 bytes with CRLF normalized to LF',
            'target':{'q':1,'F':record['F'],'A':record['A']},
            'quotient_coordinates':[str(z)for z in y],'weights':list(weights),'quotient_equation':str(G),
            'curve':[str(v)for v in phi],'coefficient_field':'Q(i), i²=-1',
            'fixed_coupling':'5/7','diagnostic_family':str(family),'family_restricted_partials':[str(p)for p in partials],
            'twisted_map':{'row_monomials':[str(m)for m in rowmon],'column_labels':labels,
                           'matrix':matrix_json(fixed),'parameter_matrix':[[str(v)for v in row]for row in M.tolist()],
                           'rank':6,'selected_columns':selected,'minor_determinant':str(minor)},
            'spectral':{'inner_product':'Coefficient monomials and listed direct-sum sections declared orthonormal; coordinate-dependent, not a canonical geometric metric.',
                        'gram_matrix':matrix_json(fixed_gram),'gram_inverse':matrix_json(inverse),
                        'right_inverse':matrix_json(right_inverse),'eigenvalues':eigenvalues,
                        'smallest_eigenvalue':'25/49','largest_eigenvalue':'72',
                        'smallest_singular_value':'5/7','largest_singular_value':'6*sqrt(2)',
                        'lower_bound_remainder':matrix_json(lower_remainder),
                        'right_inverse_gram':matrix_json(right_gram),'right_inverse_operator_norm':'7/5',
                        'matrix_full_row_rank_perturbation_radius':'5/7',
                        'gram_invertibility_perturbation_radius':'25/49',
                        'perturbation_argument':'In the listed coefficient norms, ||E||_2<5/7 gives ||ER||_2<1, so (M+E)R=I+ER is invertible by the Neumann series. A Gram perturbation Delta with ||Delta||_2<25/49 similarly preserves invertibility. These are sufficient matrix bounds, not a geometric-neighborhood guarantee.',
                        'matrix_condition_number':'42*sqrt(2)/5','gram_condition_number':'3528/25',
                        'resolvent_diagonal':[str(v)for v in resolvent.diagonal()],
                        'small_eigenspace_projector':matrix_json(Psmall),'large_eigenspace_projector':matrix_json(Plarge),
                        'inverse_interpolation_polynomial':'((25/49+72)*I-H)/((25/49)*72)',
                        'real_parameter_gram_diagonal':[str(v)for v in gram.diagonal()],
                        'rank_at_c_zero':2,'rank_for_nonzero_real_c':6},
            'untwisted_map':{'column_labels':untwisted_labels,'matrix':matrix_json(untwisted),'rank':7,
                             'incidence_kernel_basis':matrix_json(kernel),'affine_evaluation_at_1_1':matrix_json(evaluation_on_kernel),
                             'affine_evaluation_rank':4},
            'local_family':{'curve':[str(v)for v in family_curve],
                             'free_parameters':[str(v)for v in free],'dependent_parameters':[str(v)for v in dependent],
                             'base_point':{str(z):encode(v)for z,v in parameter_base.items()},
                             'coefficient_equations':[str(q)for q in equations],
                             'coefficient_row_monomials':[str(s**(6-k)*t**k)for k in range(7)],
                             'dependent_Jacobian':matrix_json(Jdependent),'free_Jacobian':matrix_json(Jfree),
                             'dependent_Jacobian_determinant':encode(family_det),
                             'dependent_tangent_matrix':matrix_json(dependent_tangent),
                             'evaluation_chart_coordinates':['X0/X1','Z/X1^3','Y0/X1','Y1/X1','Y2/X1'],
                             'evaluation_columns':['a','b','c','r=t/s'],
                             'evaluation_matrix_at_base_r_1':matrix_json(family_evaluation),
                             'evaluation_rank':4,'evaluation_minor_rows':eval_rows,'evaluation_minor':encode(eval_minor),
                             'interpretation':'The seven equations define a smooth local three-dimensional algebraic incidence component etale over(a,b,c) at thisQ(i)point. Marked evaluation is dominant there. This is not a global polynomial parametrization or a computed support divisor.'},
            'checks':{'quotient_pullback':True,'target_density_pullback':True,'curve_on_fixed_target':True,
                      'curve_on_diagnostic_family':True,'basepoint_free':True,'smooth_along_curve':True,
                      'twisted_surjective':True,'gram_inverse_exact':True,'right_inverse_exact':True,
                      'spectral_projectors_exact':True,'inverse_functional_calculus_exact':True,
                      'gram_lower_bound_positive':True,'right_inverse_norm_exact':True,
                      'untwisted_surjective':True,'marked_evaluation_surjective':True},
            'geometric_interpretation':'The weightedEuler sequence twisted byO(-1) hasO(-1) kernel; normal sequence hasO(5) target. The exact8→6 surjection provesH1(phi*TW(-1))=0 and hencefreeness. Untwisted incidence is smooth here; evaluation has rank4.',
            'limitations':'No supporting divisor, denominator, numerator tuple, Lean proof, or accepted solve constructed. The line is onthecyclic quotient and inZ=0; freeness is not asserted forits lift totheoriginalsextic. The c-family is a separate diagnostic, not a change tothefixedproblem.',
            'reference':'Repository Chapter3 §§3.2–3.4; Bourbaki, Théories spectrales, Chapters1–2, ChapterI §1.2 spectrum/invertibility, §2.5 resolvent, §4.12 spectral projectors and §6.9 positive elements, finite-dimensional specialization.',
            'seconds':time.perf_counter()-start}
    return result


def decode_matrix(value):
    return S.Matrix([[S.Rational(v[0])+S.I*S.Rational(v[1])for v in row]for row in value])


def check_algebra(packet,expected):
    assert packet['curve']==expected['curve']and packet['twisted_map']['matrix']==expected['twisted_map']['matrix']
    M=decode_matrix(packet['twisted_map']['matrix'])
    H=decode_matrix(packet['spectral']['gram_matrix'])
    Hinv=decode_matrix(packet['spectral']['gram_inverse'])
    right=decode_matrix(packet['spectral']['right_inverse'])
    Ps=decode_matrix(packet['spectral']['small_eigenspace_projector'])
    Pl=decode_matrix(packet['spectral']['large_eigenspace_projector'])
    lower=decode_matrix(packet['spectral']['lower_bound_remainder'])
    right_gram=decode_matrix(packet['spectral']['right_inverse_gram'])
    assert H==M*M.conjugate().T and H*Hinv==S.eye(6)and M*right==S.eye(6)
    assert Ps*Ps==Ps and Pl*Pl==Pl and Ps*Pl==S.zeros(6)and Ps+Pl==S.eye(6)
    assert H==S.Rational(25,49)*Ps+72*Pl and Hinv==S.Rational(49,25)*Ps+Pl/72
    assert lower==H-S.Rational(25,49)*S.eye(6) and lower.is_diagonal()
    assert all(v>=0 for v in lower.diagonal())
    assert right_gram==right.conjugate().T*right==Hinv
    assert max(right_gram.eigenvals())==S.Rational(49,25)
    assert M[:,packet['twisted_map']['selected_columns']].det()==S.Rational(packet['twisted_map']['minor_determinant'])
    local=packet['local_family'];J=decode_matrix(local['dependent_Jacobian'])
    B=decode_matrix(local['free_Jacobian']);T=decode_matrix(local['dependent_tangent_matrix'])
    assert local['coefficient_equations']==expected['local_family']['coefficient_equations']
    assert local['dependent_Jacobian']==expected['local_family']['dependent_Jacobian']
    assert J*T+B==S.zeros(7,3)
    det=S.Rational(local['dependent_Jacobian_determinant'][0])+S.I*S.Rational(local['dependent_Jacobian_determinant'][1])
    assert J.det()==det and det!=0
    E=decode_matrix(local['evaluation_matrix_at_base_r_1'])
    assert local['evaluation_matrix_at_base_r_1']==expected['local_family']['evaluation_matrix_at_base_r_1']
    em=S.Rational(local['evaluation_minor'][0])+S.I*S.Rational(local['evaluation_minor'][1])
    assert E[local['evaluation_minor_rows'],:].det()==em and em!=0


def verify():
    start=time.perf_counter();path=HERE/'cyclic-free-curve.json'
    packet=json.loads(path.read_text(encoding='utf-8'));expected=calculate()
    check_algebra(packet,expected)
    for key in expected:
        if key!='seconds':assert packet[key]==expected[key],key
    mutations=[]
    tests=[('twisted_map','matrix',0,1),('spectral','gram_matrix',0,0),
           ('spectral','gram_inverse',0,0),('spectral','right_inverse',0,0),
           ('spectral','lower_bound_remainder',0,0),('spectral','right_inverse_gram',0,0),
           ('spectral','small_eigenspace_projector',0,0),('local_family','dependent_Jacobian',0,0),
           ('local_family','dependent_tangent_matrix',0,0),('local_family','evaluation_matrix_at_base_r_1',0,0)]
    for section,key,row,col in tests:
        altered=copy.deepcopy(packet);value=altered[section][key][row][col]
        value[0]=str(S.Rational(value[0])+1)
        try:check_algebra(altered,expected)
        except AssertionError:mutations.append(section+'.'+key)
        else:raise AssertionError('Mutationaccepted: '+section+'.'+key)
    result={'schema':'cyclic-fano-free-curve-validation-v1','status':'PASS','instance':ID,
            'packet_sha256':sha(path),'producer_sha256':sha(Path(__file__)),
            'twisted_rank':6,'untwisted_rank':7,'local_family_dimension':3,'marked_evaluation_rank':4,
            'exact_Gram_eigenvalues':packet['spectral']['eigenvalues'],'mutations_rejected':mutations,
            'certificate_found':False,'seconds':time.perf_counter()-start}
    (HERE/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result),flush=True)


def main():
    if not __debug__:raise RuntimeError('Run without -O.')
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['worker','run','verify'])
    args=parser.parse_args()
    if args.command=='worker':
        result=calculate();(HERE/'cyclic-free-curve.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
        print(json.dumps({'status':'PASS','twisted_rank':6,'gram_eigenvalues':result['spectral']['eigenvalues'],
                          'evaluation_rank':4,'seconds':result['seconds']}),flush=True)
    elif args.command=='verify':verify()
    else:
        start=time.perf_counter()
        try:
            process=subprocess.run([sys.executable,str(Path(__file__).resolve()),'worker'],capture_output=True,text=True,timeout=120)
            result={'status':'complete'if process.returncode==0 else'error','returncode':process.returncode,
                    'stdout':process.stdout,'stderr':process.stderr}
        except subprocess.TimeoutExpired:
            result={'status':'timeout'}
        result.update(time_limit_seconds=120,elapsed_seconds=time.perf_counter()-start)
        (HERE/'attempt.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(result),flush=True)
        if result['status']!='complete':raise SystemExit(1)


if __name__=='__main__':main()
