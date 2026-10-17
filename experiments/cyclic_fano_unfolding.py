#!/usr/bin/env python3
"""Exact jets of the actual cyclic Fano evaluation map near its triple fiber.

The hypersurface is fixed. The target varies on an explicitly defined algebraic
surface germ. Every displayed jet is verified in a stated truncated local ring.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

import sympy as S
from sympy.polys.domains import QQ_I

REPO=Path(__file__).resolve().parents[1]
SOURCE=REPO/'results'/'cyclic-fano-curve'
OUT=REPO/'results'/'cyclic-fano-unfolding'
ORDER=4
ZERO=(0,0,0)
DIRECTION='X0'


def sha(path):return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()


def save(name,data):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/name).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')


def constant(value):
    value=QQ_I.convert(value)
    return {ZERO:value}if value else{}


def variable(i):return {tuple(int(j==i)for j in range(3)):QQ_I.one}


def add(a,b):
    out=dict(a)
    for mon,value in b.items():
        out[mon]=out.get(mon,QQ_I.zero)+value
        if not out[mon]:del out[mon]
    return out


def scale(a,value):
    value=QQ_I.convert(value)
    return {mon:c*value for mon,c in a.items()if c*value}


def mul(a,b):
    out={}
    for m,c in a.items():
        for n,d in b.items():
            mon=tuple(x+y for x,y in zip(m,n))
            if sum(mon)>ORDER:continue
            out[mon]=out.get(mon,QQ_I.zero)+c*d
            if not out[mon]:del out[mon]
    return out


def homogeneous(a,degree):return {m:c for m,c in a.items()if sum(m)==degree}


def uadd(a,b):
    out=dict(a)
    for power,jet in b.items():
        out[power]=add(out.get(power,{}),jet)
        if not out[power]:del out[power]
    return out


def umul(a,b):
    out={}
    for i,x in a.items():
        for j,y in b.items():
            if i+j>6:continue
            out[i+j]=add(out.get(i+j,{}),mul(x,y))
            if not out[i+j]:del out[i+j]
    return out


def compose(terms,coordinates):
    powers=[]
    for i,coord in enumerate(coordinates):
        row=[{0:constant(1)}]
        for _ in range(max(m[i]for m,c in terms)):row.append(umul(row[-1],coord))
        powers.append(row)
    out={}
    for mon,coefficient in terms:
        term={0:constant(coefficient)}
        for i,n in enumerate(mon):term=umul(term,powers[i][n])
        out=uadd(out,term)
    return out


def encode(jet):return [{'powers':list(m),'coefficient':[str(c.x),str(c.y)]}for m,c in sorted(jet.items(),reverse=True)]
def pair(value):
    if not hasattr(value,'x'):value=QQ_I.convert(S.expand(value))
    return [str(value.x),str(value.y)]


def source():
    manifest=json.loads((SOURCE/'target.json').read_text(encoding='utf-8'))
    x=S.symbols('X0 X1 X2 Y0 Y1 Y2');Z=S.Symbol('Z')
    F=S.Poly(S.sympify(manifest['target']['F'],locals=dict(zip(manifest['variables'],x))),*x,domain=S.QQ)
    terms=[]
    for mon,coefficient in F.terms():
        assert mon[2]%3==0
        m=list(mon);m[2]//=3;terms.append((tuple(m),QQ_I.convert(coefficient)))
    y=(x[0],x[1],Z,x[3],x[4],x[5])
    G=S.expand(sum(QQ_I.to_sympy(c)*S.prod(z**n for z,n in zip(y,m))for m,c in terms))
    return manifest,y,G,terms


def incidence(terms,b,U,h,z,unknown):
    k,l,m,C,E=unknown
    r=add(constant(1),h)
    target_x=U if DIRECTION=='X0'else{}
    target_y0=add(constant(S.I),U)if DIRECTION=='Y0'else constant(S.I)
    target_y2=add(scale(r,S.I),U)if DIRECTION=='Y2'else scale(r,S.I)
    coords=[{0:target_x,1:b},{0:constant(1)},{0:z,1:k,2:l,3:m},
            {0:target_y0,1:add(constant(S.I),C)},
            {0:r,1:constant(1)},{0:target_y2,1:E}]
    return compose(terms,coords)


def derive():
    start=time.perf_counter();manifest,y,G,terms=source()
    b,U,h=map(variable,range(3))
    probe=variable(0)
    # Independent columns of the constant Jacobian in k,l,m,C,E.
    jac=[]
    for j in range(5):
        unknown=[{}for _ in range(5)];unknown[j]=probe
        equations=incidence(terms,{},{},{},{},unknown)
        jac.append([QQ_I.to_sympy(equations.get(i,{}).get((1,0,0),QQ_I.zero))for i in range(1,6)])
    J=S.Matrix(5,5,lambda i,j:jac[j][i]);assert J.det()!=0
    inverse=J.inv();inverse_gauss=[[QQ_I.convert(z)for z in row]for row in inverse.tolist()]
    # The target surface is p(U,h)=(U,1,z,i,1+h,i(1+h)), G=0,
    # choosing the etale quadratic branch z(0,0)=0.
    z={};pivot=QQ_I.convert(5*S.I/7)
    for degree in range(1,ORDER+1):
        residual=incidence(terms,{},U,h,z,[{}for _ in range(5)]).get(0,{})
        z=add(z,scale(homogeneous(residual,degree),-1/pivot))
    assert not incidence(terms,{},U,h,z,[{}for _ in range(5)]).get(0,{})
    unknown=[{}for _ in range(5)]
    stages=[]
    for degree in range(1,ORDER+1):
        equations=incidence(terms,b,U,h,z,unknown)
        residual=[homogeneous(equations.get(i,{}),degree)for i in range(1,6)]
        correction=[]
        for row in inverse_gauss:
            value={}
            for coefficient,poly in zip(row,residual):value=add(value,scale(poly,-coefficient))
            correction.append(value)
        unknown=[add(a,c)for a,c in zip(unknown,correction)]
        stages.append({'degree':degree,'corrections':[encode(c)for c in correction]})
    equations=incidence(terms,b,U,h,z,unknown)
    assert all(not equations.get(i,{})for i in range(6))
    scalar=equations.get(6,{})
    kappa=scalar.get((3,0,0),QQ_I.zero)
    assert kappa==QQ_I.convert(-1-48*S.I/175)
    assert all(not c for mon,c in scalar.items()if mon[1:]==(0,0)and mon[0]<3)
    ks=S.Matrix([[QQ_I.to_sympy(scalar.get(mon,QQ_I.zero))for mon in row]
                  for row in [[(0,1,0),(0,0,1)],[(1,1,0),(1,0,1)]]])
    fourth=scalar.get((4,0,0),QQ_I.zero)
    normalized=S.Matrix([[z/QQ_I.to_sympy(kappa)for z in ks.row(0)],
                         [(ks[1,j]/QQ_I.to_sympy(kappa)-QQ_I.to_sympy(fourth)*ks[0,j]/QQ_I.to_sympy(kappa)**2).simplify()for j in range(2)]])
    parameter_name={'X0':'U','Y0':'V','Y2':'W'}[DIRECTION]
    u_symbol,h_symbol,z_symbol=S.symbols(parameter_name+' h z')
    target=(u_symbol if DIRECTION=='X0'else 0,1,z_symbol,
            S.I+u_symbol if DIRECTION=='Y0'else S.I,1+h_symbol,
            S.I*(1+h_symbol)+u_symbol if DIRECTION=='Y2'else S.I*(1+h_symbol))
    target_eq=S.expand(G.subs(dict(zip(y,target))))
    curve=[str(value)for value in target]
    curve[0]+='+b*u';curve[2]+='+k*u+l*u**2+m*u**3';curve[3]+='+(I+C)*u';curve[4]+='+u';curve[5]+='+E*u'
    line_slice={m:c for m,c in scalar.items()if m[1]==0}
    result={'schema':'cyclic-fano-unfolding-v1','producer_sha256':sha(Path(__file__)),
            'fixed_target_manifest_sha256':sha(SOURCE/'target.json'),
            'base_fiber_packet_sha256':sha(REPO/'results'/'cyclic-fano-fibers'/'fiber-equations.json'),
            'instance':manifest['instance'],'source_commit':manifest['upstream_commit'],
            'field':'Q(i)','parameter_direction':DIRECTION,'jet_variables':['b',parameter_name,'h'],'jet_total_order':ORDER,
            'target_surface_coordinates':[str(value)for value in target],
            'exact_target_surface_equation':str(target_eq),'chosen_target_branch':'z(0,0)=0',
            'target_z_derivative_at_origin':pair(pivot),'target_z_jet':encode(z),
            'curve_coordinates':curve,
            'unknown_order':['k','l','m','C','E'],
            'constant_implicit_jacobian':[[pair(a)for a in row]for row in J.tolist()],
            'constant_implicit_jacobian_determinant':pair(J.det()),
            'unknown_jets':[encode(v)for v in unknown],'hensel_stages':stages,
            'scalar_germ_jet':encode(scalar),'scalar_cubic_at_central_fiber':pair(kappa),
            'scalar_quartic_at_central_fiber':pair(fourth),
            'T1_basis':['1','b'],'T1_parameter_order':[parameter_name,'h'],
            'T1_parameter_matrix':[[pair(a)for a in row]for row in ks.tolist()],
            'T1_rank':ks.rank(),'T1_determinant':pair(ks.det()),
            'normalized_Weierstrass_constant_and_linear_parameter_matrix':[[pair(a)for a in row]for row in normalized.tolist()],
            'seed_line_slice_second_parameter_zero':encode(line_slice),
            'checks':{'target_equation_zero_through_order4':True,'first_five_incidence_equations_zero_through_order4':True,
                      'central_cubic_matches_prior_packet':True},
            'limits':'The full target surface equation is exact. The target coordinate, eliminated curve coefficients and scalar germ are truncated through total degree4. No global branch equation, support divisor or certificate is claimed.',
            'seconds':time.perf_counter()-start}
    return result


def summarize():
    packets={axis:json.loads((OUT/f'unfolding-{axis}.json').read_text(encoding='utf-8'))for axis in ('X0','Y0','Y2')}
    for packet in packets.values():assert packet['producer_sha256']==sha(Path(__file__))
    def value(entry):return S.Rational(entry[0])+S.I*S.Rational(entry[1])
    matrices={axis:S.Matrix([[value(v)for v in row]for row in p['T1_parameter_matrix']])for axis,p in packets.items()}
    full=S.Matrix.hstack(*(matrices[axis][:,0]for axis in ('X0','Y0','Y2')),matrices['X0'][:,1])
    assert full.rank()==1 and full[:,0]==S.zeros(2,1)and full[:,1]==S.zeros(2,1)
    assert (full[:,2]+S.I*full[:,3]).applyfunc(S.simplify)==S.zeros(2,1)
    # In target-chart coordinates(X0,Y0,Y1,Y2), these four tangent
    # directions form a basis; Z is determined by G_Z=5i/7.
    tangent=S.Matrix([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,S.I]])
    assert tangent.det()==-1
    common=packets['X0']['seed_line_slice_second_parameter_zero']
    assert all(p['seed_line_slice_second_parameter_zero']==common for p in packets.values())
    coeff={tuple(t['powers']):value(t['coefficient'])for t in common}
    alpha=S.simplify(-coeff[(3,0,0)]/coeff[(0,0,1)])
    beta=S.simplify(-(coeff[(4,0,0)]+coeff[(1,0,1)]*alpha)/coeff[(0,0,1)])
    assert S.expand(alpha-(S.Rational(5,6)+8*S.I/35))==0
    assert S.expand(beta-(-S.Rational(97,70)-2227*S.I/210))==0
    b=S.Symbol('b');series=alpha*b**3+beta*b**4
    substituted=S.expand(sum(c*b**mon[0]*series**mon[2]for mon,c in coeff.items()))
    assert all(S.expand(substituted).coeff(b,k)==0 for k in range(5))
    return {'schema':'cyclic-fano-unfolding-summary-v1','producer_sha256':sha(Path(__file__)),
            'axis_packet_sha256':{axis:sha(OUT/f'unfolding-{axis}.json')for axis in packets},
            'fixed_target_manifest_sha256':sha(SOURCE/'target.json'),
            'axis_attempts':{'X0':'Rank1: added target direction has zero T1 class.',
                             'Y0':'Rank1: added target direction has zero T1 class.',
                             'Y2':'Rank1: added target direction has−i times the h T1 class.'},
            'target_tangent_coordinate_order':['X0','Y0','Y1','Y2'],
            'target_tangent_direction_order':['X0 perturbation','Y0 perturbation','Y2 perturbation','seed-line h'],
            'target_tangent_basis_matrix':[[pair(v)for v in row]for row in tangent.tolist()],
            'target_tangent_basis_determinant':['-1','0'],
            'full_T1_matrix':[[pair(v)for v in row]for row in full.tolist()],
            'full_T1_rank':1,'miniversal':False,
            'actual_seed_line_target':['0','1','0','I','1+h','I*(1+h)'],
            'h_of_b_jet_coefficients_ascending':[['0','0'],['0','0'],['0','0'],pair(alpha),pair(beta)],
            'h_of_b_remainder':'O(b^5)','ramification_index':3,
            'ramification_reason':'The exact implicit incidence germ has nonzero g_h=6/5. It defines a smooth source curve h=h(b). Its first nonzero term is(5/6+8i/35)b^3, so the target-map ramification index is exactly3. An analytic coordinate change makes this local one-dimensional map z→z^3.',
            'local_monodromy':'A three-cycle on the three nearby sheets of this one-dimensional analytic germ.',
            'limits':'All four target tangent directions are accounted for, and their T1 image has rank1; a miniversal cusp unfolding is not established. The order4 jets do not give a global branch polynomial, support divisor, certificate, or degree of the seed covering component.'}


def main():
    global DIRECTION
    if not __debug__:raise RuntimeError('Run without -O.')
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['run','worker','verify','summary'])
    parser.add_argument('--axis',choices=['X0','Y0','Y2'],default='X0')
    args=parser.parse_args()
    DIRECTION=args.axis;filename=f'unfolding-{DIRECTION}.json'
    if args.command=='summary':
        packet=summarize();save('unfolding.json',packet)
        print(json.dumps({'status':'PASS','full_T1_rank':1,'ramification_index':3,
                          'packet_sha256':sha(OUT/'unfolding.json')}),flush=True);return
    if args.command=='worker':
        packet=derive();save(filename,packet)
        print(json.dumps({'status':'PASS','T1_rank':packet['T1_rank'],'T1_matrix':packet['T1_parameter_matrix'],
                          'T1_determinant':packet['T1_determinant'],'seconds':packet['seconds']}),flush=True);return
    if args.command=='verify':
        packet=json.loads((OUT/filename).read_text(encoding='utf-8'));expected=derive()
        for key in expected:
            if key!='seconds':assert packet[key]==expected[key],key
        result={'status':'PASS','packet_sha256':sha(OUT/filename),'producer_sha256':sha(Path(__file__)),
                'T1_rank':packet['T1_rank'],'total_jet_order':ORDER,'certificate_found':False}
        save(f'validation-{DIRECTION}.json',result);print(json.dumps(result),flush=True);return
    start=time.perf_counter()
    try:
        process=subprocess.run([sys.executable,str(Path(__file__).resolve()),'worker','--axis',DIRECTION],capture_output=True,text=True,timeout=120)
        result={'status':'complete'if process.returncode==0 else'error','returncode':process.returncode,'stdout':process.stdout,'stderr':process.stderr}
    except subprocess.TimeoutExpired:result={'status':'timeout','stop_reason':'120-second wall-clock bound'}
    result.update(parameter_direction=DIRECTION,time_limit_seconds=120,elapsed_seconds=time.perf_counter()-start)
    save(f'attempt-{DIRECTION}.json',result);print(json.dumps(result),flush=True)
    if result['status']!='complete':raise SystemExit(1)


if __name__=='__main__':main()
