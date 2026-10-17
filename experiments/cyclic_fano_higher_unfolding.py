#!/usr/bin/env python3
"""Higher exact jets of a fixed cyclic-Fano evaluation surface.

The frozen order-four producer supplies sparse Gaussian-rational arithmetic.
This experiment solves all seven physical incidence coefficients simultaneously
for the actual local evaluation graph, then centers its critical cubic germ.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

import sympy as S
from sympy.polys.domains import QQ_I
import cyclic_fano_unfolding as B

REPO=Path(__file__).resolve().parents[1]
OUT=REPO/'results'/'cyclic-fano-higher-unfolding'
ORDER=8
DIRECTION='X0'


def save(name,value):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')


def equations(terms,b,U,unknown):
    z,k,l,m,C,E,h=unknown
    return B.incidence(terms,b,U,h,z,[k,l,m,C,E])


def derivative(poly,index):
    out={}
    for m,c in poly.items():
        if m[index]:
            n=list(m);n[index]-=1
            out[tuple(n)]=c*m[index]
    return out


def power(poly,n):
    out=B.constant(1)
    for _ in range(n):out=B.mul(out,poly)
    return out


def substitute_b(poly,value):
    U=B.variable(1);out={}
    for (a,b,c),coefficient in poly.items():
        assert c==0
        out=B.add(out,B.scale(B.mul(power(value,a),power(U,b)),coefficient))
    return out


def decode(terms):
    return {tuple(t['powers']):QQ_I.convert(S.Rational(t['coefficient'][0])+S.I*S.Rational(t['coefficient'][1]))for t in terms}


def polynomial_terms(expression,variables):
    poly=S.Poly(S.expand(expression),*variables,domain=QQ_I)
    return [{'powers':list(m),'coefficient':B.pair(c)}for m,c in poly.terms()]


def derive():
    start=time.perf_counter();B.ORDER=ORDER;B.DIRECTION=DIRECTION
    manifest,y,G,terms=B.source()
    b,U=B.variable(0),B.variable(1)
    columns=[]
    for j in range(7):
        unknown=[{}for _ in range(7)];unknown[j]=b
        probe=equations(terms,{},{},unknown)
        columns.append([QQ_I.to_sympy(probe.get(i,{}).get((1,0,0),QQ_I.zero))for i in range(7)])
    J=S.Matrix(7,7,lambda i,j:columns[j][i]);assert J.det()!=0
    inverse=[[QQ_I.convert(x)for x in row]for row in J.inv().tolist()]
    unknown=[{}for _ in range(7)];stages=[]
    for degree in range(1,ORDER+1):
        residual=equations(terms,b,U,unknown)
        homogeneous=[B.homogeneous(residual.get(i,{}),degree)for i in range(7)]
        corrections=[]
        for row in inverse:
            correction={}
            for c,v in zip(row,homogeneous):correction=B.add(correction,B.scale(v,-c))
            corrections.append(correction)
        unknown=[B.add(v,c)for v,c in zip(unknown,corrections)]
        stages.append({'degree':degree,'corrections':[B.encode(c)for c in corrections]})
    residual=equations(terms,b,U,unknown)
    assert all(not residual.get(i,{})for i in range(7))
    H=unknown[-1];Hb=derivative(H,0);Hbb=derivative(Hb,0);Hbbb=derivative(Hbb,0)
    assert all(sum(m)>=3 for m in H)
    alpha=H.get((3,0,0),QQ_I.zero)
    assert alpha==QQ_I.convert(S.Rational(5,6)+8*S.I/35)
    # The implicit inflection center is unique because H_bbb(0,0)=6*alpha.
    center={}
    for degree in range(1,ORDER-1):
        r=B.homogeneous(substitute_b(Hbb,center),degree)
        center=B.add(center,B.scale(r,-1/(6*alpha)))
    center_residual=substitute_b(Hbb,center)
    assert not {m:c for m,c in center_residual.items()if sum(m)<=ORDER-2}
    height=substitute_b(H,center)
    linear={m:c for m,c in substitute_b(Hb,center).items()if sum(m)<=ORDER-1}
    cubic={m:c for m,c in B.scale(substitute_b(Hbbb,center),S.Rational(1,6)).items()if sum(m)<=ORDER-3}
    target=['U'if DIRECTION=='X0'else'0','1','z','I+U'if DIRECTION=='Y0'else'I','1+h','I*(1+h)']
    curve=[target[0]+'+b*u','1','z+k*u+l*u^2+m*u^3',target[3]+'+(I+C)*u','1+h+u','I*(1+h)+E*u']
    packet={'schema':'cyclic-fano-higher-unfolding-v1','producer_sha256':B.sha(Path(__file__)),
            'arithmetic_dependency_sha256':B.sha(Path(B.__file__)),
            'fixed_target_manifest_sha256':B.sha(B.SOURCE/'target.json'),
            'instance':manifest['instance'],'source_commit':manifest['upstream_commit'],
            'field':'Q(i)','parameter_direction':DIRECTION,'jet_variables':['b','U','unused'],'jet_total_order':ORDER,
            'target_coordinates':target,'curve_coordinates':curve,
            'unknown_order':['z','k','l','m','C','E','h'],
            'constant_implicit_jacobian':[[B.pair(x)for x in row]for row in J.tolist()],
            'constant_implicit_jacobian_determinant':B.pair(J.det()),
            'unknown_jets':[B.encode(x)for x in unknown],'hensel_stages':stages,
            'evaluation_graph_h':B.encode(H),
            'inflection_center_b':B.encode(center),'inflection_center_order':ORDER-2,
            'center_height':B.encode(height),'center_height_valid_order':ORDER,
            'centered_linear_coefficient':B.encode(linear),'centered_linear_valid_order':ORDER-1,
            'centered_cubic_coefficient':B.encode(cubic),'centered_cubic_valid_order':ORDER-3,
            'checks':{'all_seven_physical_coefficients_zero_through_total_order':ORDER,
                      'inflection_center_residual_zero_through_order':ORDER-2,
                      'evaluation_graph_has_no_terms_below_degree3':True},
            'precision_argument':'The graph remainder is O((b,U)^(n+1)). The inflection center is known through n−2. H_b has order at least2, so its error from the center is quadratic in a center error because H_bb vanishes at the exact center; the centered linear coefficient is therefore valid through n−1. The centered height error is a center error O(U^(n−1)) times H_b=O(U^2), so the height is valid through n. The cubic coefficient is retained only through n−3.',
            'limits':'Finite jets of the actual fixed-target local evaluation map. Neither a global branch equation nor a supporting denominator or certificate is established.',
            'seconds':time.perf_counter()-start}
    return packet


def candidates():
    paths={'X0':OUT/'unfolding-X0-order12.json','Y0':OUT/'unfolding-Y0-order8.json'}
    packets={axis:json.loads(path.read_text(encoding='utf-8'))for axis,path in paths.items()}
    for p in packets.values():
        assert p['producer_sha256']==B.sha(Path(__file__))
        assert p['arithmetic_dependency_sha256']==B.sha(Path(B.__file__))
    p=packets['Y0'];H=decode(p['evaluation_graph_h']);x,V,h=S.symbols('x V h')
    H3=S.expand(sum(QQ_I.to_sympy(c)*x**m[0]*V**m[1]for m,c in H.items()if sum(m)==3))
    a,d,e,f=[S.expand(H3).coeff(x,3-j).coeff(V,j)for j in range(4)]
    a,d,e,f=map(S.expand,(a,d,e,f))
    shift=S.expand(-d/(3*a)).expand(complex=True).simplify()
    lam=S.expand(e-d*d/(3*a)).expand(complex=True).simplify()
    mu=S.expand(f-d*e/(3*a)+2*d**3/(27*a*a)).expand(complex=True).simplify()
    gamma=S.expand(4*lam**3/(27*a)).expand(complex=True).simplify()
    assert a!=0 and lam!=0 and gamma!=0
    def value(pair):return S.Rational(pair[0])+S.I*S.Rational(pair[1])
    center=decode(p['inflection_center_b']);height=decode(p['center_height']);linear=decode(p['centered_linear_coefficient'])
    assert S.expand(shift-QQ_I.to_sympy(center[(0,1,0)]))==0
    assert S.expand(lam-QQ_I.to_sympy(linear[(0,2,0)]))==0
    assert S.expand(mu-QQ_I.to_sympy(height[(0,3,0)]))==0
    depressed=S.expand(H3.subs(x,x+shift*V))
    assert S.expand(depressed-(a*x**3+lam*V**2*x+mu*V**3))==0
    disc=S.discriminant(H3-h,x)
    normalized=S.Poly(disc,V,h,domain=QQ_I).mul_ground(S.expand(1/(-27*a*a)).expand(complex=True).simplify()).as_expr()
    branch=S.expand((h-mu*V**3)**2+gamma*V**6)
    assert S.Poly(normalized-branch,V,h,domain=QQ_I).is_zero
    X0,X1,Z,Y0,Y1,Y2=S.symbols('X0 X1 Z Y0 Y1 Y2');variables=(X0,X1,Z,Y0,Y1,Y2)
    tangent=-S.I*Y2-X1;transverse=Y0-S.I*X1
    center_candidate=tangent*X1**2-mu*transverse**3
    branch_candidate=S.expand(center_candidate**2+gamma*transverse**6)
    specs=[('full-tangent-linear',1,tangent,'The full first-order target deformation covector is h−iW=−iY2/X1−1. This is the uncorrected tangent control.'),
           ('Y0-center-cubic',3,center_candidate,'Homogenize h−mu3*V^3 from the centered critical value of the actual Y0 surface through its first nonzero transverse order.'),
           ('Y0-leading-branch-sextic',6,branch_candidate,'Homogenize the leading local branch equation (h−mu3*V^3)^2+gamma*V^6. It retains both local critical-value branches.')]
    output=[]
    for name,degree,expression,rationale in specs:
        entries=polynomial_terms(expression,variables)
        assert all(sum(a*w for a,w in zip(t['powers'],[1,1,3,1,1,1]))==degree for t in entries)
        assert S.Poly(expression.subs({X1:1,Y0:S.I+V,Y2:S.I*(1+h)})-{'full-tangent-linear':h,'Y0-center-cubic':h-mu*V**3,'Y0-leading-branch-sextic':branch}[name],V,h,domain=QQ_I).is_zero
        output.append({'id':name,'degree':degree,'quotient_denominator':entries,'rationale':rationale,
                       'scope':'A homogeneous guess over Q(i), obtained by extending data from the specified Y0 target surface using the verified full-target tangent covector. The extension away from that surface is a choice. It is not a proved global branch divisor or certificate; exact fixed-D checks are separate.'})
    return {'schema':'cyclic-fano-higher-unfolding-candidates-v1','producer_sha256':B.sha(Path(__file__)),
            'arithmetic_dependency_sha256':B.sha(Path(B.__file__)),
            'source_jet_packet_sha256':{axis:B.sha(path)for axis,path in paths.items()},
            'prior_full_T1_packet_sha256':B.sha(REPO/'results'/'cyclic-fano-unfolding'/'unfolding.json'),
            'fixed_target_manifest_sha256':B.sha(B.SOURCE/'target.json'),
            'variables':[str(v)for v in variables],'weights':[1,1,3,1,1,1],
            'leading_graph_variables':['b','V'],'leading_graph_cubic':polynomial_terms(H3,(x,V)),
            'leading_graph_coefficient_order':['b^3','b^2*V','b*V^2','V^3'],
            'leading_graph_coefficients':[B.pair(v)for v in (a,d,e,f)],
            'inflection_shift_linear':B.pair(shift),'centered_linear_leading':B.pair(lam),
            'center_height_leading':B.pair(mu),'leading_branch_gamma':B.pair(gamma),
            'leading_branch_variables':['V','h'],'leading_branch_equation':polynomial_terms(branch,(V,h)),
            'critical_branch_justification':'The graph has no terms below degree3. Substitute b=V*t in H_b and divide by V^2. Its constant quadratic in t has two distinct roots because lambda2 is nonzero. The analytic implicit-function theorem gives two critical branches with distinct slopes. Their images are h=c_plus*V^3+O(V^4) and h=c_minus*V^3+O(V^4), with (c−mu3)^2+gamma=0 and gamma nonzero. Thus the two local branch images have contact order3. The displayed degree6 equation is only their leading weighted equation, with weights wt(V)=1, wt(h)=3.',
            'local_branch_contact_order':3,'critical_value_leading_coefficients_are_distinct':True,
            'X0_negative_result':{'center_height_zero_through_order':12,'centered_linear_zero_through_order':11,
                                  'verified':not packets['X0']['center_height']and not packets['X0']['centered_linear_coefficient'],
                                  'limit':'No exact vanishing or global branch equality follows from these finite jets.'},
            'candidates':output,
            'limits':'The cubic preparation here concerns the leading homogeneous graph, not the full Weierstrass polynomial. Exact fixed-denominator searches must decide whether any heuristic extension yields a certificate.'}


def main():
    global ORDER,DIRECTION
    if not __debug__:raise RuntimeError('Run without -O.')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['run','worker','verify','candidates','verify-candidates'])
    parser.add_argument('--order',type=int,default=8)
    parser.add_argument('--axis',choices=['X0','Y0'],default='X0')
    args=parser.parse_args();ORDER=args.order;DIRECTION=args.axis
    assert 4<=ORDER<=12
    if args.command in ('candidates','verify-candidates'):
        packet=candidates()
        if args.command=='candidates':save('candidates.json',packet)
        else:
            assert json.loads((OUT/'candidates.json').read_text(encoding='utf-8'))==packet
            save('candidates-validation.json',{'status':'PASS','producer_sha256':B.sha(Path(__file__)),
                                              'packet_sha256':B.sha(OUT/'candidates.json'),'candidate_count':3,
                                              'local_branch_contact_order':3})
        print(json.dumps({'status':'PASS','candidate_degrees':[1,3,6],'local_branch_contact_order':3}),flush=True)
        return
    filename=f'unfolding-{DIRECTION}-order{ORDER}.json'
    if args.command=='worker':
        packet=derive();save(filename,packet)
        print(json.dumps({'status':'PASS','order':ORDER,'seconds':packet['seconds'],
                          'center_height':packet['center_height'],
                          'linear':packet['centered_linear_coefficient']}),flush=True);return
    if args.command=='verify':
        packet=json.loads((OUT/filename).read_text(encoding='utf-8'));expected=derive()
        for key in expected:
            if key!='seconds':assert packet[key]==expected[key],key
        result={'status':'PASS','packet_sha256':B.sha(OUT/filename),'producer_sha256':B.sha(Path(__file__)),
                'arithmetic_dependency_sha256':B.sha(Path(B.__file__)),'order':ORDER}
        save(f'validation-{DIRECTION}-order{ORDER}.json',result);print(json.dumps(result),flush=True);return
    start=time.perf_counter()
    try:
        process=subprocess.run([sys.executable,str(Path(__file__).resolve()),'worker','--order',str(ORDER),'--axis',DIRECTION],
                               capture_output=True,text=True,timeout=120)
        result={'status':'complete'if process.returncode==0 else'error','returncode':process.returncode,
                'stdout':process.stdout,'stderr':process.stderr}
    except subprocess.TimeoutExpired:result={'status':'timeout','stop_reason':'120-second wall-clock bound'}
    result.update(order=ORDER,parameter_direction=DIRECTION,time_limit_seconds=120,elapsed_seconds=time.perf_counter()-start)
    save(f'attempt-{DIRECTION}-order{ORDER}.json',result);print(json.dumps(result),flush=True)
    if result['status']!='complete':raise SystemExit(1)


if __name__=='__main__':main()
