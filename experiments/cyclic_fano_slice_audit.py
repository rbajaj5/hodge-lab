#!/usr/bin/env python3
"""Exact restriction audit; no candidate search or slice certificate claim."""
from pathlib import Path
from fractions import Fraction as Q
import argparse
import copy
import json
import cyclic_fano_guided_denominators as arithmetic

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/cyclic-fano-slice-audit'
PRIOR=ROOT/'results/cyclic-fano-branch-polars'
base=arithmetic.base; poly=base.poly
BASE=(0,1,3,4,5)
NAMES=('X0','X1','Y0','Y1','Y2')
SPECS=[('polar_'+name,tuple(int(i==j)for i in range(5)))for j,name in enumerate(NAMES)]
SPECS += [('polar_X0_plus_Y0',(1,0,1,0,0)),('polar_X1_plus_Y1',(0,1,0,1,0))]
DEPS=('cyclic_fano_guided_denominators.py','cyclic_fano_transfer.py','quadric_contact_pilot.py')


def restrict(p):
    out={}
    for m,c in p.items():
        if m[4]or m[5]:continue
        n=(m[0]+m[3],m[1],m[2])
        out[n]=out.get(n,Q(0))+c
        if not out[n]:del out[n]
    return out


def directional(p,v):
    return base.total(poly.scale(poly.derivative(p,j),v[i])for i,j in enumerate(BASE))


def encode(p):
    return [{'powers':list(m),'coefficient':str(c)}for m,c in sorted(p.items())]


def transverse_arc(p,epsilon_coordinate):
    """Base-polynomial arc with powers (s,u,epsilon); no Z variable here."""
    assert epsilon_coordinate in (4,5)and all(m[2]==0 for m in p)
    zero_coordinate=9-epsilon_coordinate;out={}
    for m,c in p.items():
        if m[zero_coordinate]:continue
        n=(m[0]+m[3],m[1],m[epsilon_coordinate])
        out[n]=out.get(n,Q(0))+c
        if not out[n]:del out[n]
    return out


def assert_polar_binding(packet,E,P,residual,v):
    assert packet['direction']==list(v)
    assert arithmetic.decode(packet['denominator'])==E
    assert [arithmetic.decode(p)for p in packet['particular']]==P
    assert arithmetic.decode(packet['residual'])==residual
    assert packet['status']=='excluded'


def calculate():
    F,A,G,beta=base.target()
    q={m[:2]+(0,)+m[3:]:c for m,c in G.items()if m[2]==1}
    h={m:c for m,c in G.items()if not m[2]}
    Delta=poly.add(poly.mul(q,q),h,-4);J=poly.derivative(G,2)
    assert G[(0,0,2,0,0,0)]==1
    gs=restrict(G);ds=restrict(Delta);bs=restrict(beta)
    assert gs=={(0,0,2):Q(1),(3,0,1):Q(5,7),(6,0,0):Q(2),(0,6,0):Q(1)}
    assert ds=={(6,0,0):Q(-367,49),(0,6,0):Q(-4)}
    assert bs=={(4,0,0):Q(1,3)}
    cases=[]
    for name,v in SPECS:
        path=PRIOR/(name+'.json');prior=json.loads(path.read_text(encoding='utf-8'))
        E=directional(Delta,v)
        assert E and all(m[2]==0 for m in E)
        assert E==poly.add(poly.scale(poly.mul(J,directional(q,v)),2),directional(G,v),-4)
        P=[{}for _ in range(6)]
        for i,j in enumerate(BASE):P[j]=poly.scale(beta,-4*v[i])
        P[2]=poly.scale(poly.mul(beta,directional(q,v)),2)
        assert base.contraction(P,G)==poly.mul(beta,E)
        residual=base.B(E,P)
        formula=poly.scale(poly.add(poly.mul(beta,directional(E,v)),poly.mul(directional(beta,v),E),-1),4)
        assert residual==formula and residual
        assert_polar_binding(prior,E,P,residual,v)
        # Monic Z division: a nonzero base polynomial is its own remainder.
        global_remainder=E
        es=restrict(E);rs=restrict(residual)
        assert restrict(poly.mul(beta,E))==poly.mul(bs,es)
        defects=[restrict(poly.add(P[3],P[0],-1)),restrict(P[4]),restrict(P[5])]
        witnesses=[]
        for term in prior['dual']:
            mon=tuple(term['powers']);monomial={mon:Q(1)}
            witnesses.append({'global_powers':list(mon),'dual_coefficient':term['coefficient'],
                              'restricted_monomial':encode(restrict(monomial)),
                              'vanishes_on_slice':not bool(restrict(monomial))})
        cases.append({'id':name,'direction':list(v),'prior_packet_sha256':poly.sha(path),
                      'global_denominator':encode(E),'global_monic_remainder':encode(global_remainder),
                      'global_residual':encode(residual),'restricted_denominator':encode(es),
                      'restricted_residual':encode(rs),
                      'restricted_field':[encode(restrict(p))for p in P],
                      'global_denominator_nonzero_mod_G':bool(global_remainder),
                      'restricted_denominator_nonzero':bool(es),'restricted_residual_zero':not bool(rs),
                      'restriction_status':'denominator_vanishes_identically'if not es else 'nonzero_denominator_only',
                      'saved_obstruction_monomials':witnesses,
                      'linear_slice_ideal_defects':[encode(p)for p in defects],
                      'preserves_linear_slice_ideal':not any(defects),
                      'curve_vector_field_established':False,'slice_certificate_established':False})
    y2=next(c for c in cases if c['id']=='polar_Y2')
    assert not y2['restricted_denominator_nonzero']and y2['restricted_residual_zero']
    assert y2['restricted_field'][5]==encode({(4,0,0):Q(-4,3)})
    assert all(c['global_denominator_nonzero_mod_G']for c in cases)
    e_y2=poly.derivative(Delta,5);p_y2=poly.scale(beta,-4)
    arcs=[]
    expected_arcs=[{(4,0,1):Q(50,49),(2,1,2):Q(50,49),(1,1,3):Q(-20,7)},
                   {(0,0,5):Q(-24)}]
    for coordinate,expected in zip((4,5),expected_arcs):
        ep=transverse_arc(e_y2,coordinate);np=transverse_arc(p_y2,coordinate)
        assert ep==expected and np=={(4,0,0):Q(-4,3)}
        order=min(m[2]for m in ep)
        arcs.append({'id':'Y1_arc'if coordinate==4 else 'Y2_arc',
                     'base_substitution':['s','u','s','epsilon'if coordinate==4 else '0','epsilon'if coordinate==5 else '0'],
                     'denominator':encode(ep),'numerator_P_Y2':encode(np),
                     'denominator_vanishing_order':order,'numerator_vanishing_order':0,
                     'rational_component_pole_order':order})
    control={(0,0,0,0,1,0):Q(1)}
    assert control and not restrict(control)and all(m[2]<2 for m in control)
    return {'schema':'cyclic-fano-slice-audit-v1','status':'PASS','instance':'cyclic-triple-fano',
            'source_commit':'d96911d725077e66a8f10848908be01a643b1714',
            'source_instance_sha256':poly.sha(base.SOURCE/'source/instance.rec'),
            'producer_sha256':poly.sha(Path(__file__)),
            'arithmetic_dependencies':{name:poly.sha(ROOT/'experiments'/name)for name in DEPS},
            'prior_polar_validation_sha256':poly.sha(PRIOR/'validation.json'),
            'prior_polar_independent_validation_sha256':poly.sha(PRIOR/'independent-validation.json'),
            'global_variables':['X0','X1','Z','Y0','Y1','Y2'],'slice_variables':['s','u','Z'],
            'slice_substitution':['s','u','Z','s','0','0'],
            'restricted_G':encode(gs),'restricted_Delta':encode(ds),'restricted_beta':encode(bs),
            'linear_slice_ideal_generators':['Y0-X0','Y1','Y2'],'cases':cases,
            'noninjectivity_control':{'polynomial':'Y1','global_monic_remainder':encode(control),
                                      'restricted_polynomial':encode(restrict(control)),
                                      'meaning':'A globally nonzero polynomial can vanish on this closed slice.'},
            'no_cancellation_control':{'id':'polar_Y2','field_component':'P_Y2/E',
                                       'restricted_numerator':y2['restricted_field'][5],
                                       'restricted_denominator':y2['restricted_denominator'],
                                       'regular_at_generic_slice_point':False,
                                       'meaning':'The numerator is generically nonzero on the slice while E vanishes there; vanishing of the residual does not regularize this rational field component.'},
            'transverse_arcs':{'variables':['s','u','epsilon'],'base_variables':list(NAMES),
                               'cases':arcs,'generic_nonzero_assumptions':['s != 0','Delta_slice(s,u) != 0 for an unramified lift to G=0'],
                               'lift_scope':'These are exact base arcs. At a chosen root Z0 of G_slice with G_Z != 0, the formal implicit theorem supplies a local lift. No explicit global Z-parameterization is asserted.',
                               'meaning':'Orders one and five are directional pole orders of the same rational component, not a phase transition or a proof that blowing up removes the pole.'},
            'scope':'Restriction audit of seven previously excluded fixed polars. No new candidate solve, curve-field descent, full polar-family exclusion or fourfold certificate.',
            'reading':'Shafarevich, Basic Algebraic Geometry 1, third edition, Ch.1 §§3.1–3.3: irreducibility, rational functions and rational maps.'}


def save(packet):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'validation.json').write_text(json.dumps(packet,indent=2)+'\n',encoding='utf-8',newline='\n')


def main():
    assert __debug__,'Run without -O'
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('run','verify'));args=parser.parse_args()
    expected=calculate()
    if args.command=='run':save(expected)
    else:
        actual=json.loads((OUT/'validation.json').read_text(encoding='utf-8'))
        assert actual==expected
        # Alter three distinct substantive conclusions; exact replay must reject each.
        mutated=[]
        bad=copy.deepcopy(actual);bad['cases'][4]['restricted_denominator_nonzero']=True;mutated.append(bad)
        bad=copy.deepcopy(actual);bad['noninjectivity_control']['restricted_polynomial']=[{'powers':[0,0,0],'coefficient':'1'}];mutated.append(bad)
        bad=copy.deepcopy(actual);bad['cases'][0]['global_monic_remainder']=[];mutated.append(bad)
        for bad in mutated:
            try:assert bad==calculate()
            except AssertionError:pass
            else:raise AssertionError('Mutated restriction packet was accepted')
    print(json.dumps({'status':'PASS','command':args.command,'cases':7,
                      'denominator_collapses':[c['id']for c in expected['cases']if not c['restricted_denominator_nonzero']],
                      'slice_certificate_found':False,'packet_sha256':poly.sha(OUT/'validation.json'),
                      'mutation_controls_rejected':3 if args.command=='verify'else 0}))


if __name__=='__main__':main()
