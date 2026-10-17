#!/usr/bin/env python3
"""Independent exact chart audit for a polar denominator in a normal plane."""
from pathlib import Path
from fractions import Fraction as Q
import copy
import json
import check_cyclic_fano_branch_polars as C

A=C.A
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/cyclic-fano-blowup-audit'
ZERO,ONE=A.ZERO,A.ONE


def normal_plane(poly):
    """Set X0=Y0=1, X1=u, Y1=y, Y2=z in a base polynomial."""
    result={}
    for m,c in poly.items():
        assert m[2]==0
        n=(m[1],m[4],m[5]);value=A.ca(result.get(n,ZERO),c)
        if value==ZERO:result.pop(n,None)
        else:result[n]=value
    return result


def chart(poly,y_chart):
    result={}
    for (u,y,z),c in poly.items():
        n=(u,y+z,z if y_chart else y);value=A.ca(result.get(n,ZERO),c)
        if value==ZERO:result.pop(n,None)
        else:result[n]=value
    return result


def zero_coordinate(poly,i):
    return {m:c for m,c in poly.items()if not m[i]}


def decode(terms,n=3):
    result={}
    for term in terms:
        m=tuple(term['powers']);c=(Q(term['coefficient']),Q(0))
        assert len(m)==n and all(isinstance(e,int)and e>=0 for e in m)
        assert m not in result and c!=ZERO
        result[m]=c
    return result


def overlap_transform(poly):
    result={}
    for (u,r,t),c in poly.items():
        m=(u,r,1+r-t);assert m[2]>=0
        value=A.ca(result.get(m,ZERO),c)
        if value==ZERO:result.pop(m,None)
        else:result[m]=value
    return result


def leading_branch_substitute(poly,coefficient):
    result={}
    for (u,r,t),c in poly.items():
        m=(u,r+4*t,0);value=A.ca(result.get(m,ZERO),A.cm(c,(coefficient**t,Q(0))))
        if value==ZERO:result.pop(m,None)
        else:result[m]=value
    return result


def derive():
    F,original_A,G,beta=A.target()
    original=C.physical((0,0,0,0,1),G,beta)
    E=normal_plane(original['E']);P=normal_plane(original['field'][5])
    assert P=={(0,0,0):(Q(-4,3),Q(0))}
    assert E=={(0,1,0):(Q(50,49),Q(0)),(1,2,0):(Q(50,49),Q(0)),
               (0,2,1):(Q(50,49),Q(0)),(0,1,1):(Q(-40,7),Q(0)),
               (1,3,0):(Q(-20,7),Q(0)),(0,0,5):(Q(-24),Q(0))}
    totals=[chart(E,True),chart(E,False)]
    assert [min(m[1]for m in p)for p in totals]==[1,1]
    stricts=[{(m[0],m[1]-1,m[2]):c for m,c in p.items()}for p in totals]
    a,b=stricts
    a_exc,b_exc=[zero_coordinate(p,1)for p in stricts]
    assert a_exc=={(0,0,0):(Q(50,49),Q(0))}
    assert b_exc=={(0,0,1):(Q(50,49),Q(0))}
    # On the overlap r_z=r_y*t_y and t_z=1/t_y, the strict factors
    # obey A=t_y*B(r_y*t_y,1/t_y).  Multiplication by t_y clears all
    # negative exponents, so this verifies a polynomial identity.
    overlap=overlap_transform(b)
    assert overlap==a and overlap_transform(a)==b
    strict_axis=zero_coordinate(b,2)
    assert strict_axis=={(0,4,0):(Q(-24),Q(0))}
    branches=A.add(b,A.scale(strict_axis,A.cn(ONE)))
    assert all(m[2]>=1 for m in branches)
    U={(m[0],m[1],m[2]-1):c for m,c in branches.items()}
    assert zero_coordinate(zero_coordinate(U,1),2)=={(0,0,0):(Q(50,49),Q(0))}
    assert zero_coordinate(zero_coordinate(A.derivative(b,1),1),2)=={}
    assert zero_coordinate(zero_coordinate(A.derivative(b,2),1),2)=={(0,0,0):(Q(50,49),Q(0))}
    leading=Q(24)/Q(50,49)
    assert leading==Q(588,25)
    remainder=leading_branch_substitute(b,leading)
    assert remainder and min(m[1]for m in remainder)==5
    # Smoothness of the original denominator germ is separate from the
    # target's smoothness and from any certificate equation.
    original_y=zero_coordinate(zero_coordinate(A.derivative(E,1),1),2)
    assert original_y=={(0,0,0):(Q(50,49),Q(0))}
    J=A.derivative(G,2)
    assert A.add(A.mul(J,J),A.scale(original['Delta'],A.cn(ONE)))==A.scale(G,(Q(4),Q(0)))
    return {'original':original,'normal_denominator':E,'normal_numerator':P,
            'total_transforms':totals,'strict_transforms':stricts,
            'exceptional_restrictions':[a_exc,b_exc],'overlap':overlap,
            'strict_axis':strict_axis,'implicit_unit':U,'branch_leading_coefficient':leading,
            'leading_branch_remainder':remainder}


def validate(packet,exact):
    assert packet['schema']=='cyclic-fano-blowup-audit-v1'and packet['status']=='PASS'
    assert packet['instance']=='cyclic-triple-fano'
    assert packet['source_commit']=='d96911d725077e66a8f10848908be01a643b1714'
    assert packet['source_instance_sha256']==A.I.sha(C.SOURCE/'source/instance.rec')
    assert packet['producer_sha256']==A.I.sha(ROOT/'experiments/cyclic_fano_blowup_audit.py')
    assert packet['dependencies']=={name:A.I.sha(ROOT/'experiments'/name)for name in ('cyclic_fano_transfer.py','quadric_contact_pilot.py')}
    prior=ROOT/'results/cyclic-fano-slice-audit'
    assert packet['prior_slice_packet_sha256']==A.I.sha(prior/'validation.json')
    assert packet['prior_slice_independent_receipt_sha256']==A.I.sha(prior/'independent-validation.json')
    assert packet['global_variables']==['X0','X1','Z','Y0','Y1','Y2']
    assert decode(packet['global_denominator'],6)==exact['original']['E']
    assert packet['plane_variables']==['u','y','z']
    assert packet['plane_substitution']==['1','u','Z','1','y','z']
    assert decode(packet['plane_denominator'])==exact['normal_denominator']
    assert decode(packet['scalar_numerator'])==exact['normal_numerator']
    derivative={(0,0,0):(Q(50,49),Q(0))}
    assert decode(packet['plane_derivative_E_y_at_origin'])==derivative
    assert packet['plane_divisor_smooth_at_origin']is True
    assert set(packet['charts'])=={'y','z'}
    for i,name in enumerate(('y','z')):
        saved=packet['charts'][name]
        assert saved['variables']==['u','r','t']
        assert saved['substitution']==({'y':'r','z':'r*t'}if name=='y'else{'y':'r*t','z':'r'})
        assert decode(saved['total_transform'])==exact['total_transforms'][i]
        assert decode(saved['strict_transform'])==exact['strict_transforms'][i]
        assert decode(saved['exceptional_factor'])=={(0,1,0):ONE}
        assert saved['exceptional_multiplicity']==1
        assert decode(saved['restriction_to_exceptional'])==exact['exceptional_restrictions'][i]
        assert decode(saved['scalar_numerator'])==exact['normal_numerator']
        assert A.mul(decode(saved['strict_transform']),decode(saved['exceptional_factor']))==decode(saved['total_transform'])
    overlap=packet['overlap']
    assert overlap['coordinate_change']=='r_z=r_y*t_y, t_z=1/t_y'
    assert overlap['strict_identity']=='H_y(u,r,t)=t*H_z(u,r*t,1/t)'
    assert overlap['reverse_identity']=='H_z(u,r,t)=t*H_y(u,r*t,1/t)'
    assert overlap['both_polynomial_identities_checked']is True
    crossing=packet['exceptional_intersection']
    assert crossing['y_chart']=='empty'and crossing['z_chart_t']==0
    assert crossing['intersection_multiplicity']==1
    assert decode(crossing['strict_derivative_t'])==derivative
    assert decode(crossing['strict_derivative_r'])=={}
    assert Q(crossing['jacobian_r_H_at_origin'])==Q(50,49)
    assert crossing['strict_transform_smooth']is True and crossing['crossing_transverse']is True
    axis=packet['special_axis']
    assert axis['chart']=='z'and axis['equation']=='t=0'
    assert decode(axis['strict_transform_restriction'])==exact['strict_axis']
    assert axis['strict_contact_order']==4 and axis['exceptional_contact_order']==1
    assert axis['total_denominator_order']==5
    leading=axis['implicit_strict_branch_leading_term']
    assert Q(leading['t_coefficient'])==exact['branch_leading_coefficient']
    assert leading['r_power']==4 and leading['error_order']==5
    assert decode(axis['leading_branch_substitution_remainder'])==exact['leading_branch_remainder']
    for i,name in enumerate(('y','z')):
        p=zero_coordinate(exact['total_transforms'][i],2)
        assert decode(packet['axis_controls'][name+'_axis_total'])==p
        assert packet['axis_controls'][name+'_axis_order']==min(m[1]for m in p)==(1 if i==0 else 5)
    orders=packet['local_divisor_orders']
    for key in ('denominator_exceptional','denominator_strict_transform','scalar_pole_exceptional','scalar_pole_strict_transform'):
        assert orders[key]==1


def main():
    assert __debug__,'Run without -O'
    exact=derive()
    path=OUT/'packet.json';packet=A.I.load(path);validate(packet,exact)
    negative=[]
    altered=copy.deepcopy(packet);altered['plane_denominator'][0]['coefficient']='1';negative.append(altered)
    altered=copy.deepcopy(packet);altered['charts']['y']['strict_transform'][0]['coefficient']='1';negative.append(altered)
    altered=copy.deepcopy(packet);altered['charts']['z']['exceptional_multiplicity']=5;negative.append(altered)
    altered=copy.deepcopy(packet);altered['overlap']['coordinate_change']='r_z=r_y, t_z=t_y';negative.append(altered)
    altered=copy.deepcopy(packet);altered['exceptional_intersection']['strict_derivative_t']=[];negative.append(altered)
    altered=copy.deepcopy(packet);altered['special_axis']['implicit_strict_branch_leading_term']['t_coefficient']='1';negative.append(altered)
    altered=copy.deepcopy(packet);altered['scalar_numerator']=[];negative.append(altered)
    altered=copy.deepcopy(packet);altered['local_divisor_orders']['scalar_pole_exceptional']=0;negative.append(altered)
    rejected=sum(A.I.rejects(lambda p=p:validate(p,exact))for p in negative)
    assert rejected==8
    primary=A.I.load(OUT/'validation.json')
    assert primary['status']=='PASS'and primary['packet_sha256']==A.I.sha(path)
    assert primary['producer_sha256']==packet['producer_sha256']
    receipt={'schema':'cyclic-fano-blowup-audit-independent-v1','status':'PASS',
             'checker_lf_sha256':A.I.sha(Path(__file__)),
             'packet_lf_sha256':A.I.sha(path),'primary_validation_lf_sha256':A.I.sha(OUT/'validation.json'),
             'source_instance_lf_sha256':A.I.sha(C.SOURCE/'source/instance.rec'),
             'independent_arithmetic_dependencies':{Path(p).name:A.I.sha(Path(p))for p in (C.__file__,A.__file__,A.I.__file__)},
             'both_chart_factorizations_checked':True,'both_overlap_identities_checked':True,
             'original_plane_divisor_smooth':True,'exceptional_multiplicity':1,
             'strict_transform_transverse_to_exceptional':True,
             'strict_transform_at_special_axis':A.I.sparse(exact['strict_axis']),
             'implicit_strict_branch_leading_coefficient':str(exact['branch_leading_coefficient']),
             'implicit_strict_branch_order':4,'implicit_strict_branch_remainder_order':5,
             'implicit_branch_unit':A.I.sparse(exact['implicit_unit']),
             'axis_scalar_pole_orders':[1,5],
             'scalar_numerator':A.I.sparse(exact['normal_numerator']),
             'negative_controls_rejected':rejected,
             'local_unit_scope':'The y-chart strict factor is a unit in each local ring along the exceptional divisor; it is a nonconstant polynomial, not a unit of the entire affine chart coordinate ring.',
             'frame_scope':'The orders belong to the pullback of the scalar coefficient P_Y2/E in its fixed ambient frame. No transformation of the full vector field to a blowup tangent basis is asserted.',
             'target_scope':'This is the blowup of a two-dimensional normal-plane slice with u a parameter, not the whole fourfold. Linking the base charts to a chosen target root requires Delta(1,u,1,0,0)!=0, where (G_Z)^2=Delta on G=0.',
             'limits':'No pole removal, new denominator success, fourfold certificate, full target blowup, or phase transition is established.'}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'independent-validation.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':'PASS','charts':2,'negative_controls_rejected':rejected,
                      'exceptional_multiplicity':1,'axis_scalar_pole_orders':[1,5],
                      'receipt_lf_sha256':A.I.sha(OUT/'independent-validation.json')}))


if __name__=='__main__':main()
