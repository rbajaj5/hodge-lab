#!/usr/bin/env python3
"""Exact marked-evaluation audit along the whole cyclic Fano seed curve.

Reconstructs the fixed quotient and the local incidence derivatives from the
frozen instance, without importing the preceding construction or checker.
The recorded boundary section is only one input to a future support equation.
"""
from pathlib import Path
from itertools import combinations
import hashlib
import json
import sympy as S

REPO=Path(__file__).resolve().parents[1]
HERE=REPO/'results/cyclic-fano-ramification'
PREVIOUS=REPO/'results/cyclic-fano-curve'
SOURCE=PREVIOUS/'source/instance.rec'
EXPECTED_SOURCE='d99d10c84d25dc5def72cd7a9a17e5d022e18f562660c8e33bf106675b4a418c'
EXPECTED_PACKET='a1a67db6e117bc2ff39f997db176401f1b7a762f63d9c26176eac399c842220a'
COMMIT='d96911d725077e66a8f10848908be01a643b1714'

def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()

def matrix_json(matrix):
    return [[str(S.factor(x)) for x in row] for row in matrix.tolist()]

def equality(actual,expected):
    assert actual.shape==expected.shape
    assert all(S.cancel(x)==0 for x in actual-expected)

def reject(operation):
    try:operation()
    except AssertionError:return 1
    raise AssertionError('Altered data were accepted')

def fields(path):
    result={};active=None
    for line in path.read_text(encoding='utf-8').splitlines():
        if any(line.startswith(k+': ') for k in ('F','A','q')):
            active,value=line.split(': ',1);result[active]=value
        elif active in ('F','A') and line.startswith('  '):
            result[active]+=' '+line.strip()
        else:active=None
    return result

def main():
    assert __debug__,'Run without -O'
    assert sha(SOURCE)==EXPECTED_SOURCE
    assert sha(PREVIOUS/'cyclic-free-curve.json')==EXPECTED_PACKET
    raw=fields(SOURCE)
    assert raw['q']=='1'
    x=S.symbols('X0 X1 X2 Y0 Y1 Y2')
    X0,X1,X2,Y0,Y1,Y2=x
    Z,s,t,r,u=S.symbols('Z s t r u')
    lookup=dict(zip(map(str,x),x))
    F=S.Poly(S.sympify(raw['F'],locals=lookup),*x,domain=S.QQ)
    G=0
    coordinates=(X0,X1,Z,Y0,Y1,Y2)
    for mon,coefficient in F.terms():
        assert mon[2]%3==0
        exponents=list(mon);exponents[2]//=3
        G+=coefficient*S.prod(v**n for v,n in zip(coordinates,exponents))
    G=S.expand(G)
    assert S.expand(G.subs(Z,X2**3)-F.as_expr())==0
    a,b,c,y,d,e,f,g,h,j=S.symbols('a b c y d e f g h j')
    free=(a,b,c);dependent=(y,d,e,f,g,h,j)
    curve=S.Matrix([a*s+b*t,s,f*s**3+g*s**2*t+h*s*t**2+j*t**3,
                    y*s+c*t,t,d*s+e*t])
    seed=S.Matrix([0,s,0,S.I*s,t,S.I*t])
    base={a:0,b:0,c:0,y:S.I,d:0,e:S.I,f:0,g:0,h:0,j:0}
    assert curve.subs(base)==seed
    incidence=S.Poly(S.expand(G.subs(dict(zip(coordinates,curve)),simultaneous=True)),s,t)
    equations=S.Matrix([incidence.coeff_monomial(s**(6-k)*t**k) for k in range(7)])
    assert equations.subs(base)==S.zeros(7,1)
    Jdep=equations.jacobian(dependent).subs(base)
    Jfree=equations.jacobian(free).subs(base)
    assert S.simplify(Jdep.det())==-135000*S.I/2401
    implicit=-Jdep.inv()*Jfree
    equality(Jdep*implicit+Jfree,S.zeros(7,3))
    tangents=(curve.jacobian(free)+curve.jacobian(dependent)*implicit).subs(base)
    equality(tangents,S.Matrix([[s,t,0],[0,0,0],[-t**3,0,-42*s**3/5],
                                [0,0,t],[0,0,0],[0,-5*s/42,0]]))

    # X1=s=1 and Y1=t=1 cover the complete seed P1.
    s_rows=(0,2,3,4,5)
    t_rows=(0,1,2,3,5)
    Jr=S.Matrix.hstack(tangents.subs({s:1,t:r}),seed.diff(t).subs({s:1,t:r}))[list(s_rows),:]
    Ju=S.Matrix.hstack(tangents.subs({s:u,t:1}),seed.diff(s).subs({s:u,t:1}))[list(t_rows),:]
    equality(Jr,S.Matrix([[1,r,0,0],[-r**3,0,-S.Rational(42,5),0],[0,0,r,0],
                          [0,0,0,1],[0,-S.Rational(5,42),0,S.I]]))
    equality(Ju,S.Matrix([[u,1,0,0],[0,0,0,1],[-1,0,-42*u**3/5,0],
                          [0,0,1,S.I],[0,-5*u/42,0,0]]))
    rowsets=list(combinations(range(5),4))
    minors_r=[S.factor(Jr[list(rows),:].det()) for rows in rowsets]
    minors_u=[S.factor(Ju[list(rows),:].det()) for rows in rowsets]
    assert minors_r==[r**5,S.I*r**5,S.Integer(1),-5*r/42,5*r**4/42]
    assert minors_u==[S.Integer(1),-u**5,5*u**2/42,S.I*u**5,5*u/42]
    assert minors_r[2]==minors_u[0]==1

    # The columns lie in the actual hypersurface tangent space at every point.
    chart_r_coordinates=(X0,Z,Y0,Y1,Y2)
    chart_u_coordinates=(X0,X1,Z,Y0,Y2)
    affine_r=G.subs(X1,1)
    affine_u=G.subs(Y1,1)
    point_r={X0:0,Z:0,Y0:S.I,Y1:r,Y2:S.I*r}
    point_u={X0:0,X1:u,Z:0,Y0:S.I*u,Y2:S.I}
    gradient_r=S.Matrix([[S.diff(affine_r,z).subs(point_r) for z in chart_r_coordinates]])
    gradient_u=S.Matrix([[S.diff(affine_u,z).subs(point_u) for z in chart_u_coordinates]])
    equality(gradient_r*Jr,S.zeros(1,4))
    equality(gradient_u*Ju,S.zeros(1,4))
    assert gradient_r[0,2]==gradient_u[0,4]==6*S.I
    # Signed maximal minors are proportional to the hypersurface gradient.
    cofactors_r=S.Matrix([[(-1)**k*Jr[[z for z in range(5) if z!=k],:].det() for k in range(5)]])
    cofactors_u=S.Matrix([[(-1)**k*Ju[[z for z in range(5) if z!=k],:].det() for k in range(5)]])
    equality(cofactors_r,gradient_r/(6*S.I))
    equality(cofactors_u,gradient_u/(6*S.I))

    # Weighted ambient coordinate transition, including the marked coordinate.
    xx,zz,yy,rr,vv=S.symbols('xx zz yy rr vv')
    transition=S.Matrix([xx/rr,1/rr,zz/rr**3,yy/rr,vv/rr])
    target_change=transition.jacobian((xx,zz,yy,rr,vv)).subs({xx:0,zz:0,yy:S.I,rr:r,vv:S.I*r})
    source_change=S.diag(1,1,1,-1/u**2)
    equality(target_change.subs(r,1/u)*Jr.subs(r,1/u)*source_change,Ju)
    assert S.factor(target_change.det())==-1/r**8

    # Boundary of the chosen A1 chart s != 0, and the symmetric alternative.
    section_infinity=curve.subs({s:0,t:1})
    assert section_infinity[1]==0 and section_infinity[4]==1
    infinity_tangent=Ju.subs(u,0)[:,:3]
    assert infinity_tangent.rank()==3
    assert infinity_tangent[[0,2,3],:].det()==1
    assert infinity_tangent[1,:]==S.zeros(1,3)
    section_zero=curve.subs({s:1,t:0})
    assert section_zero[4]==0 and section_zero[1]==1
    zero_tangent=Jr.subs(r,0)[:,:3]
    assert zero_tangent.rank()==3
    assert zero_tangent[[0,1,4],:].det()==-1
    assert zero_tangent[3,:]==S.zeros(1,3)
    # Distinguish the finite quotient's branch divisor from evaluation ramification.
    assert Jr[1,2]==-S.Rational(42,5) and Ju[2,0]==-1

    def assert_scalar(actual,expected):assert S.cancel(actual-expected)==0
    negative=0
    negative+=reject(lambda:assert_scalar(minors_r[2]+1,1))
    negative+=reject(lambda:assert_scalar(minors_u[0]+1,1))
    corrupted=S.Matrix(Jr);corrupted[0,0]+=1
    negative+=reject(lambda:equality(gradient_r*corrupted,S.zeros(1,4)))
    bad_source=S.diag(1,1,1,1/u**2)
    negative+=reject(lambda:equality(target_change.subs(r,1/u)*Jr.subs(r,1/u)*bad_source,Ju))
    negative+=reject(lambda:assert_scalar(infinity_tangent[[0,2,3],:].det(),0))

    def chart(name,coordinate,rows,matrix,minors,gradient,unitrows):
        return {'name':name,'source_coordinate':str(coordinate),'target_coordinates':list(rows),
                'source_columns':['a','b','c',str(coordinate)],'evaluation_matrix':matrix_json(matrix),
                'maximal_minors':[{'rows':list(ix),'determinant':str(value)} for ix,value in zip(rowsets,minors)],
                'unit_minor_rows':list(unitrows),'unit_minor_determinant':'1',
                'maximal_minor_ideal':'(1)','rank_at_every_complex_coordinate':4,
                'hypersurface_gradient':matrix_json(gradient)}
    packet={'schema':'cyclic-fano-seed-ramification-v1','instance':'cyclic-triple-fano',
            'upstream_commit':COMMIT,'source_instance_lf_sha256':EXPECTED_SOURCE,
            'frozen_curve_packet_lf_sha256':EXPECTED_PACKET,'checker_lf_sha256':sha(Path(__file__)),
            'coefficient_field':'Q(i), i^2=-1','quotient_coordinates':list(map(str,coordinates)),
            'seed_curve':list(map(str,seed)),'family_coordinate_polynomials':list(map(str,curve)),
            'family_basepoint':{str(k):str(v) for k,v in base.items()},
            'implicit_derivative_matrix':matrix_json(implicit),'global_family_tangent_columns':matrix_json(tangents),
            'charts':[chart('X1=1',r,['X0','Z','Y0','Y1','Y2'],Jr,minors_r,gradient_r,(0,1,3,4)),
                      chart('Y1=1',u,['X0','X1','Z','Y0','Y2'],Ju,minors_u,gradient_u,(0,1,2,3))],
            'chart_transition':{'overlap':'r*u=1','target_from_X1_to_Y1':list(map(str,transition)),
                                'target_variables':['xx=X0/X1','zz=Z/X1^3','yy=Y0/X1','rr=Y1/X1','vv=Y2/X1'],
                                'target_derivative_on_seed':matrix_json(target_change),
                                'source_derivative_u_to_r':matrix_json(source_change),
                                'identity':'J_u(u)=T(1/u) J_r(1/u) diag(1,1,1,-1/u^2)',
                                'identity_verified':True},
            'ramification_along_seed':{'scheme':'empty','all_maximal_minors_checked':10,
                                        'reason':'The maximal-minor ideal is the unit ideal on each of two charts covering P1.',
                                        'misleading_single_minor':'r^5 vanishes at r=0 while the evaluation still has rank four.'},
            'chosen_affine_boundary':{'removed_source_section':'s=0','section_image':list(map(str,section_infinity)),
                                     'containing_hypersurface':'X1=0 on W',
                                     'section_tangent_in_Y1_chart':matrix_json(infinity_tangent),
                                     'section_rank_at_seed_endpoint':3,'unit_minor_rows':[0,2,3],
                                     'unit_minor':'1','target_gradient_Y2_at_endpoint':'6*I',
                                     'interpretation':'The section image is locally a divisor in W at this endpoint, contained in X1=0. X1 can cover this one boundary image in the chosen support procedure.'},
            'opposite_affine_boundary':{'removed_source_section':'t=0','section_image':list(map(str,section_zero)),
                                       'containing_hypersurface':'Y1=0 on W',
                                       'section_rank_at_seed_endpoint':3,'minor_rows':[0,1,4],'minor':'-1'},
            'quotient_branch_comparison':{'branch_divisor_of_X_to_W':'Z=0','seed_contained':True,
                                          'normal_Z_family_derivative_X1_chart':matrix_json(Jr[1,:3]),
                                          'normal_Z_family_derivative_Y1_chart':matrix_json(Ju[2,:3]),
                                          'interpretation':'The family has a nonzero normal deformation to Z=0 at every seed point. This branch divisor is not the ramification locus of the marked evaluation.'},
            'geometric_consequences':[
                'The fixed local incidence component is smooth of dimension three at the base parameter. The two unit minors show marked evaluation is etale at every point of the seed fiber.',
                'After shrinking the smooth parameter component, evaluation can be made etale along the complete family: its critical locus is closed in P1 times S, and its projection to S is closed by properness.',
                'This does not compute the branch or boundary images of a compactification. Other sheets or parameter boundaries can still meet the seed image downstairs.'
            ],
            'limitations':[
                'No global elimination, degree of the generically finite evaluation, complete branch divisor, or parameter-compactification boundary has been computed.',
                'X1 is a factor covering only the chosen removed source section; X1 alone is not established as a support, and no claim is made that every certificate denominator contains X1.',
                'No rational primitive, certificate, Lean proof, or solution is supplied. All freeness and evaluation statements concern W, not a rational or free lift to X.'
            ]}
    HERE.mkdir(parents=True,exist_ok=True)
    path=HERE/'packet.json'
    path.write_text(json.dumps(packet,indent=2)+'\n',encoding='utf-8',newline='\n')
    receipt={'schema':'cyclic-fano-seed-ramification-validation-v1','status':'PASS',
             'packet_lf_sha256':sha(path),'checker_lf_sha256':sha(Path(__file__)),
             'maximal_minors_checked':10,'unit_minor_charts':2,'rank_everywhere_on_seed':4,
             'ramification_on_seed':'empty','boundary_section_rank':3,
             'weighted_chart_transition':'PASS','hypersurface_tangent_identities':'PASS',
             'negative_controls_rejected':negative}
    (HERE/'validation.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(receipt))

if __name__=='__main__':main()
