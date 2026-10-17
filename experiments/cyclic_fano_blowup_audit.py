#!/usr/bin/env python3
"""Exact two-chart audit of a scalar polar-denominator pole in a normal plane."""
from pathlib import Path
from fractions import Fraction as Q
import argparse
import copy
import json
import time
import cyclic_fano_transfer as base

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/cyclic-fano-blowup-audit'
poly=base.poly
ZERO=(0,0,0)


def encode(p):
    return [{'powers':list(m),'coefficient':str(c)}for m,c in sorted(p.items())]


def accumulate(out,m,c):
    out[m]=out.get(m,Q(0))+c
    if not out[m]:del out[m]


def normal_plane(p):
    """Set X0=Y0=1, X1=u, Y1=y,Y2=z; p must be independent of Z."""
    assert all(m[2]==0 for m in p)
    out={}
    for m,c in p.items():accumulate(out,(m[1],m[4],m[5]),c)
    return out


def chart(p,kind):
    # Both outputs use (u,r,t). In y-chart y=r,z=r*t;
    # in z-chart z=r,y=r*t.
    assert kind in ('y','z')
    out={}
    for (u,y,z),c in p.items():accumulate(out,(u,y+z,z if kind=='y'else y),c)
    return out


def at_zero(p,coordinate):
    return {m:c for m,c in p.items()if m[coordinate]==0}


def origin(p):return {m:c for m,c in p.items()if m[1]==m[2]==0}


def divide_r(p):
    assert p and min(m[1]for m in p)==1
    return {(m[0],m[1]-1,m[2]):c for m,c in p.items()}


def overlap(strict):
    """t*strict(u,r*t,1/t), a Laurent substitution that cancels exactly."""
    out={}
    for (u,r,t),c in strict.items():
        assert 1+r-t>=0
        accumulate(out,(u,r,1+r-t),c)
    return out


def substitute_t_leading(p,coefficient,order):
    out={}
    for (u,r,t),c in p.items():accumulate(out,(u,r+order*t,0),c*coefficient**t)
    return out


def calculate():
    _,_,G,beta=base.target()
    q={m[:2]+(0,)+m[3:]:c for m,c in G.items()if m[2]==1}
    h={m:c for m,c in G.items()if not m[2]}
    Delta=poly.add(poly.mul(q,q),h,-4)
    global_E=poly.derivative(Delta,5)
    E=normal_plane(global_E);numerator=normal_plane(poly.scale(beta,-4))
    assert E=={(0,1,0):Q(50,49),(1,2,0):Q(50,49),(0,2,1):Q(50,49),
               (0,1,1):Q(-40,7),(1,3,0):Q(-20,7),(0,0,5):Q(-24)}
    assert numerator=={ZERO:Q(-4,3)}
    ey0=origin(poly.derivative(E,1));assert ey0=={ZERO:Q(50,49)}
    charts={}
    for kind in ('y','z'):
        total=chart(E,kind);strict=divide_r(total)
        assert poly.mul({(0,1,0):Q(1)},strict)==total
        charts[kind]={'variables':['u','r','t'],'substitution':{'y':'r'if kind=='y'else 'r*t','z':'r*t'if kind=='y'else 'r'},
                      'total_transform':encode(total),'strict_transform':encode(strict),
                      'exceptional_factor':encode({(0,1,0):Q(1)}),'exceptional_multiplicity':1,
                      'restriction_to_exceptional':encode(at_zero(strict,1)),
                      'scalar_numerator':encode(chart(numerator,kind))}
    Y=divide_r(chart(E,'y'));Z=divide_r(chart(E,'z'))
    assert at_zero(Y,1)=={ZERO:Q(50,49)}
    assert at_zero(Z,1)=={(0,0,1):Q(50,49)}
    assert overlap(Z)==Y and overlap(Y)==Z
    z_t=origin(poly.derivative(Z,2));z_r=origin(poly.derivative(Z,1))
    assert z_t=={ZERO:Q(50,49)}and not z_r
    # Jacobian of (r,H) with respect to (r,t) is H_t.
    crossing_jacobian=Q(50,49)
    y_axis=at_zero(chart(E,'y'),2);z_axis=at_zero(chart(E,'z'),2)
    assert y_axis=={(0,1,0):Q(50,49),(1,2,0):Q(50,49),(1,3,0):Q(-20,7)}
    assert z_axis=={(0,5,0):Q(-24)}
    strict_axis=at_zero(Z,2);assert strict_axis=={(0,4,0):Q(-24)}
    leading=Q(588,25)
    trial=substitute_t_leading(Z,leading,4)
    assert trial and min(m[1]for m in trial)==5
    return {'schema':'cyclic-fano-blowup-audit-v1','status':'PASS','instance':'cyclic-triple-fano',
            'source_commit':'d96911d725077e66a8f10848908be01a643b1714',
            'source_instance_sha256':poly.sha(base.SOURCE/'source/instance.rec'),
            'producer_sha256':poly.sha(Path(__file__)),
            'dependencies':{'cyclic_fano_transfer.py':poly.sha(Path(base.__file__)),
                            'quadric_contact_pilot.py':poly.sha(Path(poly.__file__))},
            'prior_slice_packet_sha256':poly.sha(ROOT/'results/cyclic-fano-slice-audit/validation.json'),
            'prior_slice_independent_receipt_sha256':poly.sha(ROOT/'results/cyclic-fano-slice-audit/independent-validation.json'),
            'global_variables':['X0','X1','Z','Y0','Y1','Y2'],'global_denominator':encode(global_E),
            'plane_variables':['u','y','z'],'plane_substitution':['1','u','Z','1','y','z'],
            'plane_denominator':encode(E),'scalar_numerator':encode(numerator),
            'plane_derivative_E_y_at_origin':encode(ey0),'plane_divisor_smooth_at_origin':True,
            'charts':charts,
            'overlap':{'coordinate_change':'r_z=r_y*t_y, t_z=1/t_y',
                       'strict_identity':'H_y(u,r,t)=t*H_z(u,r*t,1/t)',
                       'reverse_identity':'H_z(u,r,t)=t*H_y(u,r*t,1/t)',
                       'both_polynomial_identities_checked':True},
            'exceptional_intersection':{'y_chart':'empty','z_chart_t':0,'intersection_multiplicity':1,
                                        'strict_derivative_t':encode(z_t),'strict_derivative_r':encode(z_r),
                                        'jacobian_r_H_at_origin':str(crossing_jacobian),
                                        'strict_transform_smooth':True,'crossing_transverse':True},
            'special_axis':{'chart':'z','equation':'t=0','strict_transform_restriction':encode(strict_axis),
                            'strict_contact_order':4,'exceptional_contact_order':1,'total_denominator_order':5,
                            'implicit_strict_branch_leading_term':{'t_coefficient':str(leading),'r_power':4,'error_order':5},
                            'leading_branch_substitution_remainder':encode(trial)},
            'axis_controls':{'y_axis_total':encode(y_axis),'y_axis_order':1,
                             'z_axis_total':encode(z_axis),'z_axis_order':5},
            'local_divisor_orders':{'denominator_exceptional':1,'denominator_strict_transform':1,
                                     'scalar_pole_exceptional':1,'scalar_pole_strict_transform':1,
                                     'scope':'Near the exceptional curve over the normal-plane origin; local branches, not a global factorization.'},
            'scalar_scope':'The scalar coefficient f=P_Y2/E is pulled back in its fixed ambient frame. This is not a transformation of the entire vector field to blowup tangent coordinates.',
            'geometric_scope':'Two charts of the blowup of the normal (y,z) plane at its origin, with u a parameter. No full-fourfold blowup, new certificate, pole removal or phase transition is claimed.',
            'lift_condition':'Delta at y=z=0 equals -367/49-4*u^6. If this is nonzero, a chosen unramified root of G lifts the base charts locally; no global lift is asserted.',
            'reading':'Shafarevich, Basic Algebraic Geometry 1, third edition, Ch.2 §§4.2–4.3 and Ch.3 §§1.1–1.2.'}


def save(name,packet):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/name).write_text(json.dumps(packet,indent=2)+'\n',encoding='utf-8',newline='\n')


def main():
    assert __debug__,'Run without -O'
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('run','verify'));args=parser.parse_args()
    started=time.perf_counter();expected=calculate()
    if args.command=='run':save('packet.json',expected)
    else:
        actual=json.loads((OUT/'packet.json').read_text(encoding='utf-8'));assert actual==expected
        mutations=[]
        for path,value in [(('plane_divisor_smooth_at_origin',),False),
                           (('charts','z','exceptional_multiplicity'),5),
                           (('exceptional_intersection','intersection_multiplicity'),4),
                           (('special_axis','strict_contact_order'),5),
                           (('axis_controls','z_axis_order'),1),
                           (('scalar_numerator',),[])]:
            bad=copy.deepcopy(actual);cursor=bad
            for key in path[:-1]:cursor=cursor[key]
            cursor[path[-1]]=value;mutations.append(bad)
        for bad in mutations:
            try:assert bad==calculate()
            except AssertionError:pass
            else:raise AssertionError('Mutated blowup packet was accepted')
        save('validation.json',{'schema':'cyclic-fano-blowup-audit-validation-v1','status':'PASS',
                               'producer_sha256':poly.sha(Path(__file__)),'packet_sha256':poly.sha(OUT/'packet.json'),
                               'negative_controls_rejected':len(mutations),'both_chart_identities_checked':True,
                               'overlap_checked':True,'axis_orders':[1,5]})
    print(json.dumps({'status':'PASS','command':args.command,'packet_sha256':poly.sha(OUT/'packet.json'),
                      'seconds':time.perf_counter()-started}))


if __name__=='__main__':main()
