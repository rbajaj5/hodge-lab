#!/usr/bin/env python3
"""Show exact information loss on a closed slice of the fixed cyclic target."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sympy as S

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'results/cyclic-fano-slice-audit'
PRIOR=ROOT/'results/cyclic-fano-branch-polars'
OUT=ROOT/'results/cyclic-fano-slice-audit-figures'
INK,MUTED,PAPER='#17323B','#53666D','#FAFAF5'
TEAL,PURPLE,CORAL='#166A70','#7967AA','#CA584C'
IDS=('polar_X0','polar_X1','polar_Y0','polar_Y1','polar_Y2',
     'polar_X0_plus_Y0','polar_X1_plus_Y1')


def sha(path):return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def value(c):return S.Rational(c) if isinstance(c,str) else S.Rational(c[0])+S.I*S.Rational(c[1])
def decode(terms,variables):return S.Poly.from_dict({tuple(t['powers']):value(t['coefficient']) for t in terms},variables)
def encode(poly):return [{'powers':list(m),'coefficient':str(c)} for m,c in poly.terms() if c]
def math_poly(terms,variables):return '$'+S.latex(decode(terms,variables).as_expr())+'$'


def check_data():
    path=INPUT/'validation.json';packet=load(path)
    review_path=INPUT/'independent-validation.json';review=load(review_path)
    producer=ROOT/'experiments/cyclic_fano_slice_audit.py'
    checker=ROOT/'experiments/check_cyclic_fano_slice_audit.py'
    raw=ROOT/'results/cyclic-fano-curve/source/instance.rec'
    assert packet['schema']=='cyclic-fano-slice-audit-v1' and packet['instance']=='cyclic-triple-fano'
    assert review['schema']=='cyclic-fano-slice-audit-independent-v1'
    assert packet['status']==review['status']=='PASS'
    assert packet['producer_sha256']==sha(producer) and review['checker_lf_sha256']==sha(checker)
    assert review['primary_packet_lf_sha256']==sha(path)
    assert packet['source_instance_sha256']==review['source_instance_lf_sha256']==sha(raw)
    bindings={p.relative_to(ROOT).as_posix():sha(p) for p in (path,review_path,producer,checker,raw)}
    for field in ('arithmetic_dependencies',):
        for name,digest in packet[field].items():
            p=ROOT/'experiments'/name;assert sha(p)==digest;bindings[p.relative_to(ROOT).as_posix()]=digest
    for name,digest in review['independent_arithmetic_dependencies'].items():
        p=ROOT/'experiments'/name;assert sha(p)==digest;bindings[p.relative_to(ROOT).as_posix()]=digest
    for name,key in (('validation.json','prior_polar_validation_sha256'),
                     ('independent-validation.json','prior_polar_independent_validation_sha256')):
        p=PRIOR/name;assert load(p)['status']=='PASS' and sha(p)==packet[key]
        bindings[p.relative_to(ROOT).as_posix()]=sha(p)
    global_variables=S.symbols('X0 X1 Z Y0 Y1 Y2');X0,X1,Z,Y0,Y1,Y2=global_variables
    s,u,z,epsilon=S.symbols('s u Z epsilon');slice_variables=(s,u,z)
    assert packet['global_variables']==list(map(str,global_variables))
    assert packet['slice_variables']==list(map(str,slice_variables))
    assert packet['slice_substitution']==['s','u','Z','s','0','0']
    substitution={X0:s,X1:u,Z:z,Y0:s,Y1:0,Y2:0}
    def restrict(poly):return S.Poly(S.expand(poly.as_expr().subs(substitution,simultaneous=True)),slice_variables)
    beta=S.Poly(X0*Y0**3/3,global_variables)
    assert restrict(beta)==decode(packet['restricted_beta'],slice_variables)
    assert decode(packet['restricted_G'],slice_variables)==S.Poly(z*z+S.Rational(5,7)*s**3*z+2*s**6+u**6,slice_variables)
    assert decode(packet['restricted_Delta'],slice_variables)==S.Poly(-S.Rational(367,49)*s**6-4*u**6,slice_variables)
    cases={c['id']:c for c in packet['cases']};audits={c['id']:c for c in review['cases']}
    assert set(cases)==set(audits)==set(IDS)
    rows=[];y2_global=None;y2_field=None
    for identity in IDS:
        case=cases[identity];audit=audits[identity]
        prior_path=PRIOR/(identity+'.json');prior=load(prior_path)
        assert sha(prior_path)==case['prior_packet_sha256'] and prior['status']=='excluded'
        bindings[prior_path.relative_to(ROOT).as_posix()]=sha(prior_path)
        E=decode(case['global_denominator'],global_variables)
        residual=decode(case['global_residual'],global_variables)
        assert E==decode(prior['denominator'],global_variables)
        assert residual==decode(prior['residual'],global_variables)
        assert not E.is_zero and not residual.is_zero and E.degree(Z)==0
        assert E==decode(case['global_monic_remainder'],global_variables)
        es,rs=restrict(E),restrict(residual)
        assert (es-decode(case['restricted_denominator'],slice_variables)).is_zero
        assert (rs-decode(case['restricted_residual'],slice_variables)).is_zero
        assert (es-decode(audit['restricted_denominator'],slice_variables)).is_zero
        assert (rs-decode(audit['restricted_residual'],slice_variables)).is_zero
        field=[decode(p,global_variables) for p in prior['particular']]
        restricted_field=[restrict(p) for p in field]
        assert all((p-decode(t,slice_variables)).is_zero for p,t in zip(restricted_field,case['restricted_field']))
        defects=[restricted_field[3]-restricted_field[0],restricted_field[4],restricted_field[5]]
        assert all((p-decode(t,slice_variables)).is_zero for p,t in zip(defects,case['linear_slice_ideal_defects']))
        assert all((p-decode(t,slice_variables)).is_zero for p,t in zip(defects,audit['linear_slice_ideal_defects']))
        tangent=restrict(beta)*es
        assert (tangent-decode(audit['hypersurface_tangency_defect'],slice_variables)).is_zero
        assert any(not p.is_zero for p in defects) or not tangent.is_zero
        assert not audit['preserves_full_slice_ideal']
        assert not case['curve_vector_field_established'] and not case['slice_certificate_established']
        assert case['global_denominator_nonzero_mod_G']
        assert case['restricted_denominator_nonzero']==(not es.is_zero)
        assert case['restricted_residual_zero']==rs.is_zero
        witness=case['saved_obstruction_monomials'];assert len(witness)==1
        term=witness[0];mon=S.Poly.from_dict({tuple(term['global_powers']):1},global_variables)
        mon_restricted=restrict(mon)
        assert (mon_restricted-decode(term['restricted_monomial'],slice_variables)).is_zero
        assert term['vanishes_on_slice']==mon_restricted.is_zero
        assert term['global_powers']==prior['dual'][0]['powers'] and term['dual_coefficient']==prior['dual'][0]['coefficient']
        rows.append({'id':identity,'direction':case['direction'],'global_denominator_nonzero':True,
                     'restricted_denominator':encode(es),'restricted_residual':encode(rs),
                     'witness_monomial_restriction':encode(mon_restricted),'witness_monomial_lost':mon_restricted.is_zero,
                     'preserves_full_slice_ideal':False})
        if identity=='polar_Y2':
            y2_global=E;y2_field=field[5]
            assert es.is_zero and rs.is_zero
            assert restricted_field[5]==S.Poly(-S.Rational(4,3)*s**4,slice_variables)
    assert sum(bool(r['restricted_denominator']) for r in rows)==6
    control=packet['no_cancellation_control']
    assert control['id']=='polar_Y2' and not control['regular_at_generic_slice_point']
    assert decode(control['restricted_numerator'],slice_variables)==S.Poly(-S.Rational(4,3)*s**4,slice_variables)
    assert not control['restricted_denominator']
    assert review['zero_residual_case_has_generically_nonzero_field_numerator']
    assert review['ambient_derivatives_before_restriction_checked'] and review['slice_tangent_chain_rule_checked']
    # Two distinct ambient monomials merge, so survival is weaker than descent
    # of a coefficient functional. This is an exact restriction identity.
    collision=[restrict(S.Poly(X0*Y0**7,global_variables)),restrict(S.Poly(Y0**8,global_variables))]
    assert collision[0]==collision[1]==S.Poly(s**8,slice_variables)
    arcs=[]
    primary_arcs={a['id']:a for a in packet['transverse_arcs']['cases']}
    checked_arcs={a['id']:a for a in review['transverse_arc_checks']}
    assert set(primary_arcs)==set(checked_arcs)=={'Y1_arc','Y2_arc'}
    assert packet['transverse_arcs']['variables']==['s','u','epsilon']
    for axis in (Y1,Y2):
        replace={X0:s,X1:u,Y0:s,Y1:0,Y2:0};replace[axis]=epsilon
        polynomial=S.Poly(S.expand(y2_global.as_expr().subs(replace,simultaneous=True)),s,u,epsilon)
        numerator=S.Poly(S.expand(y2_field.as_expr().subs(replace,simultaneous=True)),s,u,epsilon)
        order=min(m[2] for m,c in polynomial.terms())
        assert numerator==S.Poly(-S.Rational(4,3)*s**4,s,u,epsilon)
        arc=primary_arcs[str(axis)+'_arc'];arc_audit=checked_arcs[str(axis)+'_arc']
        assert polynomial==decode(arc['denominator'],(s,u,epsilon))==decode(arc_audit['denominator'],(s,u,epsilon))
        assert numerator==decode(arc['numerator_P_Y2'],(s,u,epsilon))==decode(arc_audit['numerator_P_Y2'],(s,u,epsilon))
        assert order==arc['denominator_vanishing_order']==arc['rational_component_pole_order']==arc_audit['rational_component_pole_order']
        assert arc['numerator_vanishing_order']==0
        arcs.append({'axis':str(axis),'denominator':encode(polynomial),'numerator':encode(numerator),
                     'denominator_order_in_epsilon':order,'generic_field_pole_order':order,'generic_condition':'s != 0'})
    assert [a['denominator_order_in_epsilon'] for a in arcs]==[1,5]
    assert review['negative_controls_rejected']==9
    return {'schema':'cyclic-fano-slice-audit-plot-v1','instance':'cyclic-triple-fano','discussion_number':112,
            'sha256_policy':'File bytes with CRLF normalized to LF','source_sha256':bindings,'plot_source_sha256':sha(Path(__file__)),
            'cases':rows,'arcs':arcs,'restricted_G':packet['restricted_G'],'restricted_Delta':packet['restricted_Delta'],
            'noncancellation_numerator':control['restricted_numerator'],
            'local_lift_condition':'Delta_slice(s,u) != 0 at the chosen root of G_slice',
            'scope':'Exact polynomial restrictions and two selected base-arc orders. Original global exclusions remain intact; no descended vector field, slice solution, full polar-family exclusion or target certificate.'}


def draw(data):
    s,u,z,epsilon=S.symbols('s u Z epsilon')
    fig=plt.figure(figsize=(16,12.5),facecolor=PAPER)
    fig.text(.055,.954,'A closed slice can erase an obstruction without solving the target',fontsize=23,weight='bold')
    fig.text(.055,.922,'cyclic-triple-fano · discussion #112   |   Exact restriction audit of the same seven previously excluded polars',fontsize=12,color=MUTED)
    fig.text(.055,.873,r'$L:\ (X_0,X_1,Z,Y_0,Y_1,Y_2)=(s,u,Z,s,0,0),\qquad R_v=B_{E_v}(P^0)$',fontsize=19,color=TEAL)
    fig.text(.055,.827,r'$G|_L=Z^2+\frac{5}{7}s^3Z+2s^6+u^6,\qquad\Delta|_L=-\frac{367}{49}s^6-4u^6$',fontsize=18)
    fig.text(.055,.772,'A nonzero class modulo G can become zero on the closed slice',fontsize=16,weight='bold')
    ax=fig.add_axes([.055,.478,.89,.264]);ax.axis('off')
    names=[r'$e_{X_0}$',r'$e_{X_1}$',r'$e_{Y_0}$',r'$e_{Y_1}$',r'$e_{Y_2}$',r'$e_{X_0}+e_{Y_0}$',r'$e_{X_1}+e_{Y_1}$']
    rows=[[name,r'$\ne 0$',math_poly(r['restricted_denominator'],(s,u,z)),
           math_poly(r['restricted_residual'],(s,u,z)),math_poly(r['witness_monomial_restriction'],(s,u,z))]
          for name,r in zip(names,data['cases'])]
    table=ax.table(cellText=rows,colLabels=['direction v','Eᵥ modulo G','Eᵥ restricted to L','Rᵥ restricted to L','old witness monomial on L'],
                   colWidths=[.13,.09,.25,.36,.17],cellLoc='center',bbox=[0,0,1,1])
    table.auto_set_font_size(False);table.set_fontsize(13)
    for (row,col),cell in table.get_celld().items():
        cell.set_edgecolor('white');cell.set_linewidth(1.4);cell.set_text_props(color=INK)
        cell.set_facecolor('#E5ECE8' if row%2 else PAPER)
        if row==0:cell.set_facecolor(TEAL);cell.set_text_props(color='white',weight='bold',fontsize=10.5)
        elif row==5:cell.set_facecolor('#F5DFD5');cell.set_text_props(color=CORAL)
    fig.text(.055,.433,r'For $v=e_{Y_2}$: $(E_v,R_v,P^0_{Y_2})|_L=(0,0,-\frac{4}{3}s^4)$.',fontsize=20,color=CORAL)
    fig.text(.055,.396,'The residual vanishes, but the denominator vanishes too and a field numerator stays nonzero for s ≠ 0.',fontsize=12)
    fig.text(.055,.344,'Two exact approaches to the slice retain different denominator orders',fontsize=16,weight='bold')
    fig.text(.055,.298,r'$(Y_1,Y_2)=(\varepsilon,0):\quad E_{Y_2}=\frac{50}{49}s^4\varepsilon+\frac{50}{49}us^2\varepsilon^2-\frac{20}{7}su\varepsilon^3$',fontsize=17,color=TEAL)
    fig.text(.055,.255,r'$(Y_1,Y_2)=(0,\varepsilon):\quad E_{Y_2}=-24\varepsilon^5$',fontsize=17,color=PURPLE)
    fig.text(.665,.298,'order 1 → field pole order 1',fontsize=12,color=TEAL)
    fig.text(.665,.255,'order 5 → field pole order 5',fontsize=12,color=PURPLE)
    fig.text(.055,.215,'For s ≠ 0 these are exact pole orders along two base arcs; a local unramified lift to G = 0 also requires Δ|L ≠ 0.',fontsize=11.5,color=MUTED)
    fig.text(.055,.165,r'Even surviving monomials can merge: $X_0Y_0^7\mapsto s^8\longleftarrow Y_0^8$. An old coefficient functional need not descend.',fontsize=12)
    fig.text(.055,.122,'All seven particular fields fail preservation of the full slice ideal. Polynomial substitution does not establish a curve field.',fontsize=11.5,color=MUTED)
    fig.text(.055,.088,'The seven original global exclusions remain valid. No slice certificate or fourfold certificate is established here.',fontsize=12,color=CORAL)
    fig.text(.055,.043,'Reading context: Shafarevich, Basic Algebraic Geometry 1, Ch. 1 §§3.1–3.3; exact data and checks accompany the figure.',fontsize=10,color=MUTED)
    fig.text(.945,.019,'cyclic-triple-fano · discussion #112',ha='right',fontsize=10,color=TEAL)
    OUT.mkdir(parents=True,exist_ok=True);stem=OUT/'cyclic-fano-slice-audit'
    fig.savefig(stem.with_suffix('.png'),dpi=160,facecolor=PAPER)
    svg=stem.with_suffix('.svg');fig.savefig(svg,facecolor=PAPER,metadata={'Date':None})
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8',newline='\n')
    plt.close(fig)


def main():
    if not __debug__:raise RuntimeError('Run without -O so exact checks remain active.')
    data=check_data()
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'text.color':INK,'axes.labelcolor':INK,
                         'svg.fonttype':'none','svg.hashsalt':'cyclic-fano-slice-audit-v1'})
    draw(data)
    (OUT/'plot-data.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':'PASS','globally_nonzero':7,'nonzero_on_slice':6,'base_arc_orders':[1,5]}))


if __name__=='__main__':main()
