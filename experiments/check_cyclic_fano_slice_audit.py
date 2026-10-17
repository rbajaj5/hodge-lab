#!/usr/bin/env python3
"""Independent source-based restriction audit for the seven fixed polars.

No producer arithmetic is imported.  The arithmetic and physical reconstruction
come from the previously independent polar audit, with dependency hashes bound
in this receipt.  This checks a closed slice, not a certificate on the fourfold.
"""
from pathlib import Path
from fractions import Fraction as Q
import copy
import json
import check_cyclic_fano_branch_polars as C

A=C.A
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/cyclic-fano-slice-audit'
PRIOR=ROOT/'results/cyclic-fano-branch-polars'
ZERO,ONE=A.ZERO,A.ONE


def decode(terms,n):
    result={}
    for term in terms:
        m=tuple(term['powers']);c=(Q(term['coefficient']),Q(0))
        assert len(m)==n and all(isinstance(e,int)and e>=0 for e in m)
        assert m not in result and c!=ZERO
        result[m]=c
    return result


def restrict(poly):
    """Substitute (X0,X1,Z,Y0,Y1,Y2)=(s,u,Z,s,0,0)."""
    result={}
    for m,c in poly.items():
        if m[4]or m[5]:continue
        n=(m[0]+m[3],m[1],m[2])
        coefficient=A.ca(result.get(n,ZERO),c)
        if coefficient==ZERO:result.pop(n,None)
        else:result[n]=coefficient
    return result


def base_arc(poly,varying):
    """Evaluate a base polynomial on one of the two transverse arcs."""
    assert varying in (4,5)
    killed=9-varying;result={}
    for m,c in poly.items():
        assert m[2]==0
        if m[killed]:continue
        n=(m[0]+m[3],m[1],m[varying])
        coefficient=A.ca(result.get(n,ZERO),c)
        if coefficient==ZERO:result.pop(n,None)
        else:result[n]=coefficient
    return result


def validate(packet,exact):
    assert packet['schema']=='cyclic-fano-slice-audit-v1'
    assert packet['status']=='PASS'and packet['instance']=='cyclic-triple-fano'
    assert packet['source_commit']=='d96911d725077e66a8f10848908be01a643b1714'
    assert packet['source_instance_sha256']==A.I.sha(C.SOURCE/'source/instance.rec')
    assert packet['producer_sha256']==A.I.sha(ROOT/'experiments/cyclic_fano_slice_audit.py')
    expected_dependencies=('cyclic_fano_guided_denominators.py','cyclic_fano_transfer.py','quadric_contact_pilot.py')
    assert packet['arithmetic_dependencies']=={name:A.I.sha(ROOT/'experiments'/name)for name in expected_dependencies}
    assert packet['prior_polar_validation_sha256']==A.I.sha(PRIOR/'validation.json')
    assert packet['prior_polar_independent_validation_sha256']==A.I.sha(PRIOR/'independent-validation.json')
    assert packet['global_variables']==['X0','X1','Z','Y0','Y1','Y2']
    assert packet['slice_variables']==['s','u','Z']
    assert packet['slice_substitution']==['s','u','Z','s','0','0']
    assert packet['linear_slice_ideal_generators']==['Y0-X0','Y1','Y2']
    G,beta,Delta=exact['G'],exact['beta'],exact['Delta']
    assert decode(packet['restricted_G'],3)==restrict(G)
    assert decode(packet['restricted_Delta'],3)==restrict(Delta)
    assert decode(packet['restricted_beta'],3)==restrict(beta)
    assert len(packet['cases'])==7
    seen=set()
    for case in packet['cases']:
        name=case['id'];assert name in exact['cases']and name not in seen;seen.add(name)
        ex=exact['cases'][name]
        E,residual,field=ex['E'],ex['residual'],ex['field']
        path=PRIOR/(name+'.json');prior=A.I.load(path)
        assert case['prior_packet_sha256']==A.I.sha(path)
        assert case['direction']==prior['direction']==list(ex['direction'])
        assert A.decode(prior['denominator'])==E and A.decode(prior['residual'])==residual
        assert [A.decode(p)for p in prior['particular']]==field
        assert prior['status']=='excluded'
        for key,poly in [('global_denominator',E),('global_monic_remainder',E),('global_residual',residual)]:
            assert decode(case[key],6)==poly
        assert E and residual and all(m[2]==0 for m in E|residual)
        es,rs=restrict(E),restrict(residual)
        assert decode(case['restricted_denominator'],3)==es
        assert decode(case['restricted_residual'],3)==rs
        assert [decode(p,3)for p in case['restricted_field']]==[restrict(p)for p in field]
        assert case['global_denominator_nonzero_mod_G']is True
        assert case['restricted_denominator_nonzero']==bool(es)
        assert case['restricted_residual_zero']==(not bool(rs))
        assert case['restriction_status']==('nonzero_denominator_only'if es else 'denominator_vanishes_identically')
        defects=[restrict(A.add(field[3],A.scale(field[0],A.cn(ONE)))),restrict(field[4]),restrict(field[5])]
        assert [decode(p,3)for p in case['linear_slice_ideal_defects']]==defects
        assert case['preserves_linear_slice_ideal']==(not any(defects))
        hypersurface_defect=restrict(A.contraction(field,G))
        assert hypersurface_defect==A.mul(restrict(beta),es)
        # All defects are base-only, so a nonzero one cannot be a multiple of
        # the monic quadratic slice equation.  None of these seven fields
        # preserves the full ideal (G,Y0-X0,Y1,Y2).
        assert any(defects+[hypersurface_defect])
        assert all(m[2]==0 for p in defects+[hypersurface_defect]for m in p)
        assert case['curve_vector_field_established']is False
        assert case['slice_certificate_established']is False
        witnesses=case['saved_obstruction_monomials']
        assert len(witnesses)==len(prior['dual'])
        for witness,term in zip(witnesses,prior['dual']):
            mon=tuple(term['powers']);restricted=restrict({mon:ONE})
            assert witness['global_powers']==term['powers']
            assert witness['dual_coefficient']==term['coefficient']
            assert decode(witness['restricted_monomial'],3)==restricted
            assert witness['vanishes_on_slice']==(not bool(restricted))
    assert seen==set(C.NAMES)
    control={(0,0,0,0,1,0):ONE}
    assert packet['noninjectivity_control']['polynomial']=='Y1'
    assert decode(packet['noninjectivity_control']['global_monic_remainder'],6)==control
    assert decode(packet['noninjectivity_control']['restricted_polynomial'],3)==restrict(control)=={}
    no_cancel=packet['no_cancellation_control']
    assert no_cancel['id']=='polar_Y2'and no_cancel['field_component']=='P_Y2/E'
    y2=exact['cases']['polar_Y2']
    numerator=restrict(y2['field'][5]);denominator=restrict(y2['E'])
    assert numerator=={(4,0,0):(Q(-4,3),Q(0))}and not denominator
    assert decode(no_cancel['restricted_numerator'],3)==numerator
    assert decode(no_cancel['restricted_denominator'],3)==denominator
    assert no_cancel['regular_at_generic_slice_point']is False
    arcs=packet['transverse_arcs']
    assert arcs['variables']==['s','u','epsilon']
    assert arcs['base_variables']==['X0','X1','Y0','Y1','Y2']
    assert len(arcs['cases'])==2
    assert arcs['generic_nonzero_assumptions']==['s != 0','Delta_slice(s,u) != 0 for an unramified lift to G=0']
    for saved,(name,varying,substitution)in zip(arcs['cases'],[
            ('Y1_arc',4,['s','u','s','epsilon','0']),
            ('Y2_arc',5,['s','u','s','0','epsilon'])]):
        e=base_arc(y2['E'],varying);p=base_arc(y2['field'][5],varying)
        assert saved['id']==name and saved['base_substitution']==substitution
        assert decode(saved['denominator'],3)==e
        assert decode(saved['numerator_P_Y2'],3)==p
        e_order=min(m[2]for m in e);p_order=min(m[2]for m in p)
        assert saved['denominator_vanishing_order']==e_order
        assert saved['numerator_vanishing_order']==p_order==0
        assert saved['rational_component_pole_order']==e_order-p_order
        assert e_order==(1 if varying==4 else 5)


def main():
    assert __debug__,'Run without -O'
    F,original_A,G,beta=A.target()
    Qpoly,H,Delta=C.split_G(G)
    exact={'G':G,'beta':beta,'Delta':Delta,'cases':{}}
    for name,direction in zip(C.NAMES,C.EXPECTED_DIRECTIONS):
        exact['cases'][name]=C.physical(direction,G,beta)
    gs,ds,bs=restrict(G),restrict(Delta),restrict(beta)
    assert gs=={(0,0,2):ONE,(0,6,0):ONE,(3,0,1):(Q(5,7),Q(0)),(6,0,0):(Q(2),Q(0))}
    assert ds=={(6,0,0):(Q(-367,49),Q(0)),(0,6,0):(Q(-4),Q(0))}
    assert bs=={(4,0,0):(Q(1,3),Q(0))}
    # Tangent chain rule is checked after ambient differentiation; transverse
    # derivatives cannot be inferred by differentiating an erased variable.
    assert A.derivative(ds,0)==restrict(A.add(A.derivative(Delta,0),A.derivative(Delta,3)))
    assert A.derivative(ds,1)==restrict(A.derivative(Delta,1))
    J=A.derivative(G,2)
    assert A.add(A.mul(J,J),A.scale(Delta,A.cn(ONE)))==A.scale(G,(Q(4),Q(0)))
    # Hence along G=0, Delta!=0 implies G_Z!=0, providing the formal local
    # lift of either base arc. No global parameterization is being inferred.
    path=OUT/'validation.json';packet=A.I.load(path)
    validate(packet,exact)
    bad=[]
    changed=copy.deepcopy(packet);changed['cases'][4]['restricted_denominator_nonzero']=True;bad.append(changed)
    changed=copy.deepcopy(packet);changed['cases'][0]['restricted_residual']=[];bad.append(changed)
    changed=copy.deepcopy(packet);changed['cases'][4]['preserves_linear_slice_ideal']=True;bad.append(changed)
    changed=copy.deepcopy(packet);changed['noninjectivity_control']['restricted_polynomial']=[{'powers':[0,0,0],'coefficient':'1'}];bad.append(changed)
    changed=copy.deepcopy(packet);changed['cases'][0]['global_monic_remainder']=[];bad.append(changed)
    changed=copy.deepcopy(packet);changed['cases'][1]['curve_vector_field_established']=True;bad.append(changed)
    changed=copy.deepcopy(packet);changed['no_cancellation_control']['restricted_numerator']=[];bad.append(changed)
    changed=copy.deepcopy(packet);changed['transverse_arcs']['cases'][1]['rational_component_pole_order']=1;bad.append(changed)
    changed=copy.deepcopy(packet);changed['transverse_arcs']['cases'][0]['denominator'][0]['coefficient']='1';bad.append(changed)
    rejected=sum(A.I.rejects(lambda p=p:validate(p,exact))for p in bad)
    assert rejected==9
    cases=[]
    for name in C.NAMES:
        ex=exact['cases'][name];E,R,P=ex['E'],ex['residual'],ex['field']
        defects=[restrict(A.add(P[3],A.scale(P[0],A.cn(ONE)))),restrict(P[4]),restrict(P[5])]
        cases.append({'id':name,'restricted_denominator':A.I.sparse(restrict(E)),
                      'restricted_residual':A.I.sparse(restrict(R)),
                      'linear_slice_ideal_defects':[A.I.sparse(p)for p in defects],
                      'hypersurface_tangency_defect':A.I.sparse(restrict(A.contraction(P,G))),
                      'preserves_full_slice_ideal':False})
    receipt={'schema':'cyclic-fano-slice-audit-independent-v1','status':'PASS',
             'checker_lf_sha256':A.I.sha(Path(__file__)),
             'primary_packet_lf_sha256':A.I.sha(path),
             'source_instance_lf_sha256':A.I.sha(C.SOURCE/'source/instance.rec'),
             'independent_arithmetic_dependencies':{Path(p).name:A.I.sha(Path(p))for p in (C.__file__,A.__file__,A.I.__file__)},
             'cases':cases,'ambient_derivatives_before_restriction_checked':True,
             'slice_tangent_chain_rule_checked':True,'negative_controls_rejected':rejected,
             'only_zero_restricted_residual':'polar_Y2',
             'zero_residual_case_denominator_also_zero':True,
             'zero_residual_case_has_generically_nonzero_field_numerator':True,
             'transverse_arc_checks':[{'id':c['id'],'denominator':c['denominator'],
                                      'numerator_P_Y2':c['numerator_P_Y2'],
                                      'rational_component_pole_order':c['rational_component_pole_order']}
                                     for c in packet['transverse_arcs']['cases']],
             'formal_arc_lift_condition_checked':'On G=0, (G_Z)^2=Delta, so Delta!=0 permits the formal implicit lift through a chosen root Z0. The pole orders assume s!=0.',
             'dense_open_vs_closed_slice':'The genus-two curve is a proper closed slice. Restriction is noninjective, and its inclusion does not induce an inclusion of the ambient function field. A denominator may be nonzero modulo G but vanish identically on this slice.',
             'scope':'Exact restriction and tangency audit of seven previously excluded fixed polar candidates; no slice certificate, fourfold certificate, curve solve, or new family-wide exclusion.'}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'independent-validation.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':'PASS','cases':7,'negative_controls_rejected':rejected,
                      'slice_certificate_found':False,'preserves_full_slice_ideal_count':0,
                      'receipt_lf_sha256':A.I.sha(OUT/'independent-validation.json')}))


if __name__=='__main__':main()
