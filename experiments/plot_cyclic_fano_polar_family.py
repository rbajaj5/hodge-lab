#!/usr/bin/env python3
"""Visualize exact coefficient equations for the constant-direction polar family."""
from __future__ import annotations
import hashlib
import json
from itertools import combinations_with_replacement
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
import sympy as S

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'results/cyclic-fano-polar-family'
OUT=ROOT/'results/cyclic-fano-polar-family-figures'
INK,MUTED,PAPER='#17323B','#53666D','#FAFAF5'
TEAL,PURPLE,CORAL='#166A70','#7967AA','#CA584C'


def sha(path):return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def value(c):return S.Rational(c) if isinstance(c,str) else S.Rational(c[0])+S.I*S.Rational(c[1])
def decode(terms,variables):return S.Poly.from_dict({tuple(t['powers']):value(t['coefficient']) for t in terms},variables)
def encode(poly):return [{'powers':list(m),'coefficient':str(c)} for m,c in poly.terms() if c]


def check_data():
    path=INPUT/'packet.json';packet=load(path)
    vp=INPUT/'validation.json';validation=load(vp)
    rp=INPUT/'independent-validation.json';review=load(rp)
    producer=ROOT/'experiments/cyclic_fano_polar_family.py'
    checker=ROOT/'experiments/check_cyclic_fano_polar_family.py'
    raw=ROOT/'results/cyclic-fano-curve/source/instance.rec'
    assert packet['schema']=='cyclic-fano-constant-polar-family-v1'
    assert validation['schema']=='cyclic-fano-constant-polar-family-validation-v1'
    assert packet['instance']=='cyclic-triple-fano' and packet['degree']==5
    assert packet['status']==validation['status']==review['status']=='PASS'
    assert packet['producer_sha256']==validation['producer_sha256']==sha(producer)
    assert packet['source_instance_sha256']==sha(raw) and validation['packet_sha256']==sha(path)
    bindings={p.relative_to(ROOT).as_posix():sha(p) for p in (path,vp,rp,producer,checker,raw)}
    for name,digest in packet['dependencies'].items():
        p=ROOT/'experiments'/name;assert sha(p)==digest;bindings[p.relative_to(ROOT).as_posix()]=digest
    x=S.symbols('X0 X1 Z Y0 Y1 Y2');v=S.symbols('v0:5');ordinary=(0,1,3,4,5)
    assert packet['spatial_variables']==list(map(str,x))
    assert packet['parameter_variables']==['v_X0','v_X1','v_Y0','v_Y1','v_Y2']
    zero=S.Poly(0,x);Q,H,beta=(decode(packet[name],x) for name in ('Q','H','beta'))
    Delta=Q*Q-4*H;assert Delta==decode(packet['Delta'],x)
    G=S.Poly(x[2]**2,x)+Q*S.Poly(x[2],x)+H
    gradients=[G.diff(variable) for variable in x]
    assert beta==S.Poly(x[0]*x[3]**3/3,x)
    def action(E,P):return E*sum((P[i].diff(x[i]) for i in range(6)),zero)-sum((P[i]*E.diff(x[i]) for i in range(6)),zero)
    def even(poly):
        assert poly.degree(x[2])<=2
        parts=[S.Poly.from_dict({m[:2]+(0,)+m[3:]:c for m,c in poly.terms() if m[2]==j},x) for j in range(3)]
        return parts[0]-S.Rational(1,2)*Q*parts[1]+(S.Rational(1,2)*Q*Q-H)*parts[2]
    Es=[];Ps=[]
    assert len(packet['basis'])==5
    for j,i in enumerate(ordinary):
        basis=packet['basis'][j];assert basis['parameter']==j and basis['name']==str(x[i])
        E=Delta.diff(x[i]);P=[zero for _ in x];P[i]=-4*beta;P[2]=2*beta*Q.diff(x[i])
        assert E==decode(basis['E'],x)
        assert all(p==decode(t,x) for p,t in zip(P,basis['particular']))
        assert sum((P[k]*gradients[k] for k in range(6)),zero)==beta*E
        Es.append(E);Ps.append(P)
    expected_pairs=list(combinations_with_replacement(range(5),2))
    residuals={}
    for record,(i,j) in zip(packet['quadratic_residual_basis'],expected_pairs):
        powers=tuple(int(k==i)+int(k==j) for k in range(5))
        assert record['parameter_powers']==list(powers)
        polynomial=action(Es[i],Ps[j])
        if i!=j:polynomial+=action(Es[j],Ps[i])
        assert polynomial==decode(record['spatial_polynomial'],x)
        assert even(polynomial)==polynomial
        residuals[powers]=polynomial
    assert len(residuals)==len(packet['quadratic_residual_basis'])==15
    # All five direction coefficients of every complete Koszul correction
    # are projected, so this verification is uniform in the parameters.
    labels=set()
    for entry in packet['koszul_projection_checks']:
        j=entry['E_basis_index'];a,b=entry['pair'];powers=tuple(entry['multiplier_powers'])
        label=(j,a,b,powers);assert label not in labels;labels.add(label)
        multiplier=S.Poly.from_dict({powers:1},x)
        K=[zero for _ in x];K[a]=multiplier*gradients[b];K[b]=-multiplier*gradients[a]
        image=action(Es[j],K)
        assert image==decode(entry['raw_image'],x)
        assert even(image).is_zero and not entry['even_projection']
    units=[tuple(int(k==i) for k in range(6)) for i in ordinary]
    expected={(j,min(i,2),max(i,2),m) for j in range(5) for i in ordinary for m in units}
    assert labels==expected and len(labels)==125
    quotient_labels=set()
    for entry in packet['quotient_projection_checks']:
        powers=tuple(entry['multiplier_powers']);quotient_labels.add(powers)
        image=G*S.Poly.from_dict({powers:1},x)
        assert image==decode(entry['raw_image'],x)
        assert even(image).is_zero and not entry['even_projection']
    assert quotient_labels=={tuple(a[k]+b[k] for k in range(6)) for a,b in combinations_with_replacement(units,2)}
    equations=[]
    for equation in packet['coefficient_equations']:
        m=tuple(equation['spatial_powers'])
        parameter=S.Poly.from_dict({powers:p.coeff_monomial(m) for powers,p in residuals.items()},v)
        assert parameter==decode(equation['parameter_polynomial'],v)
        equations.append(parameter)
    expected_equations=[-160*v[1]**2,-160*v[3]**2,-160*v[4]**2,
                        -S.Rational(5472,49)*v[0]**2+S.Rational(400,147)*v[3]*v[4],-64*v[2]**2]
    assert equations==[S.Poly(p,v) for p in expected_equations]
    for identity in packet['coordinate_power_identities']:
        lhs=sum((decode(m['polynomial'],v)*equations[m['equation_index']] for m in identity['multipliers']),S.Poly(0,v))
        target=S.Poly(v[identity['variable']]**identity['power'],v)
        assert (lhs-target).is_zero and (lhs-decode(identity['target'],v)).is_zero
    assert len(packet['coordinate_power_identities'])==5
    injection=packet['injectivity'];matrix=S.Matrix([[E.coeff_monomial(tuple(m)) for E in Es] for m in injection['spatial_rows']])
    assert matrix==S.Matrix([[S.Rational(c) for c in row] for row in injection['matrix']])
    assert matrix.det()==S.Rational(injection['determinant'])!=0
    assert packet['complete_corrections_per_E']==25 and packet['basis_directions_checked']==5 and packet['quotient_dimension']==15
    for key,n in (('basis_lifts_checked',5),('quadratic_parameter_terms',15),('Koszul_images_checked',125),
                  ('quotient_images_checked',15),('coefficient_rows_checked',5),('coordinate_power_identities_checked',5),('negative_controls_rejected',7)):
        assert validation[key]==n
    check_review(review,path,vp,checker,raw,bindings,equations,v)
    display_order=[0,1,2,4,3]
    visible_powers=[tuple(2*int(k==j) for k in range(5)) for j in range(5)]+[(0,0,0,1,1)]
    visible=[[str(equations[i].coeff_monomial(m)) for m in visible_powers] for i in display_order]
    other=set(residuals)-set(visible_powers)
    assert len(other)==9 and all(e.coeff_monomial(m)==0 for e in equations for m in other)
    row_labels=['$'+S.latex(S.prod(x[k]**n for k,n in enumerate(packet['coefficient_equations'][i]['spatial_powers'])))+'$' for i in display_order]
    return {'schema':'cyclic-fano-constant-polar-family-plot-v1','instance':'cyclic-triple-fano','discussion_number':112,
            'sha256_policy':'File bytes with CRLF normalized to LF','source_sha256':bindings,'plot_source_sha256':sha(Path(__file__)),
            'visible_coefficient_matrix':visible,'visible_column_labels':['$v_0^2$','$v_1^2$','$v_2^2$','$v_3^2$','$v_4^2$','$v_3v_4$'],
            'visible_column_parameter_powers':[list(m) for m in visible_powers],'row_labels':row_labels,
            'source_equation_indices':display_order,'omitted_zero_quadratic_columns':9,
            'equations':[encode(p) for p in equations],'denominator_injectivity_determinant':str(matrix.det()),
            'projection_caption':'Zero even projections checked: 5 direction coefficients × 25 complete Koszul corrections = 125 images, plus all 15 quotient images.',
            'scope':packet['limits']}


def check_review(review,path,vp,checker,raw,bindings,equations,v):
    assert review['schema']=='cyclic-fano-constant-polar-family-independent-v1'
    assert review['packet_lf_sha256']==sha(path) and review['primary_validation_lf_sha256']==sha(vp)
    assert review['checker_lf_sha256']==sha(checker) and review['source_instance_lf_sha256']==sha(raw)
    for name,digest in review['independent_arithmetic_dependencies'].items():
        dep=ROOT/'experiments'/name;assert sha(dep)==digest;bindings[dep.relative_to(ROOT).as_posix()]=digest
    for key,n in (('exact_E1_and_original_Piola_basis_lifts_checked',5),('all_parameter_quadratic_terms_reconstructed',15),
                  ('complete_Koszul_fields_per_denominator',25),('basis_correction_columns_checked',125),
                  ('quotient_columns_checked',15),('negative_controls_rejected',8)):
        assert review[key]==n
    assert review['Euler_normalization_basis_identities_checked']==180
    assert review['all_corrections_have_zero_even_projection'] and review['nonzero_parameter_implies_nonzero_denominator']
    assert review['coordinate_power_identities_checked']=={'v_X0':4,'v_X1':2,'v_Y0':2,'v_Y1':2,'v_Y2':2}
    assert [decode(e['parameter_polynomial'],v) for e in review['five_coefficient_equations']]==equations
    assert review['pure_coefficient_matrix_determinant']=='-340402176/49'


def draw(data):
    fig=plt.figure(figsize=(16,11.5),facecolor=PAPER)
    fig.text(.055,.951,'Five coefficient equations exclude every constant-direction polar',fontsize=23,weight='bold')
    fig.text(.055,.917,'cyclic-triple-fano · discussion #112   |   Exact family obstruction; the fixed target remains unsolved',fontsize=12,color=MUTED)
    fig.text(.055,.866,r'$E_v=\sum_{j=0}^{4}v_j\,\partial_{x_j}\Delta,\qquad x=(X_0,X_1,Y_0,Y_1,Y_2),\quad v\in\mathbb{C}^5\setminus\{0\}$',fontsize=20,color=TEAL)
    fig.text(.055,.817,'The E1 lift exists for every v. A uniform projection removes all available E2 corrections.',fontsize=15,weight='bold')
    fig.text(.055,.778,r'$\Pi_{\mathrm{even}}(B_{E_v}(K)\ \mathrm{mod}\ G)=0;\qquad \mathrm{E2}\ \Longrightarrow\ \Pi_{\mathrm{even}}(B_{E_v}(P^0_v)\ \mathrm{mod}\ G)=0$',fontsize=18)
    fig.text(.055,.741,'Even projection uses the reflection w ↦ −w, with w = 2Z + Q. The surviving equations are quadratic in v.',fontsize=11.5,color=MUTED)
    fig.text(.055,.693,'Actual coefficient map: five selected physical monomials × six nonzero quadratic columns',fontsize=16,weight='bold')
    ax=fig.add_axes([.24,.377,.69,.268])
    matrix=[[S.Rational(c) for c in row] for row in data['visible_coefficient_matrix']]
    signs=np.array([[int(S.sign(c)) for c in row] for row in matrix])
    ax.imshow(signs,cmap=ListedColormap(['#DCEAE8','#F0F1EC','#F4DCD3']),vmin=-1,vmax=1,aspect='auto')
    ax.set_xticks(range(6),data['visible_column_labels'],fontsize=15)
    ax.xaxis.tick_top();ax.tick_params(axis='x',length=0,pad=9)
    ax.set_yticks(range(5),data['row_labels'],fontsize=15)
    ax.tick_params(axis='y',length=0,pad=12)
    for i,row in enumerate(matrix):
        for j,c in enumerate(row):
            label='$'+S.latex(c)+'$' if c else '·'
            ax.text(j,i,label,ha='center',va='center',fontsize=17 if c else 12,color=INK if c else '#9EA9A9')
    ax.set_xticks(np.arange(-.5,6,1),minor=True);ax.set_yticks(np.arange(-.5,5,1),minor=True)
    ax.grid(which='minor',color=PAPER,linewidth=2);ax.tick_params(which='minor',length=0)
    for spine in ax.spines.values():spine.set_visible(False)
    fig.text(.055,.344,'Nine other quadratic columns are zero in these five rows and are omitted. Entries are exact rational coefficients, not numerical scores.',fontsize=11.3,color=MUTED)
    fig.text(.055,.285,r'First four rows:  $v_1^2=v_3^2=v_4^2=v_2^2=0\quad\Longrightarrow\quad v_1=v_3=v_4=v_2=0$.',fontsize=18,color=TEAL)
    fig.text(.055,.235,r'Last row then becomes  $-\frac{5472}{49}v_0^2=0\quad\Longrightarrow\quad v_0=0$.',fontsize=18,color=PURPLE)
    fig.text(.055,.184,r'Thus $v=0$, contradicting the required nonzero direction. This excludes the entire displayed polar family.',fontsize=17,color=CORAL)
    fig.text(.055,.133,data['projection_caption'],fontsize=11.5)
    fig.text(.055,.098,'The denominator coefficient map is injective, so a nonzero direction really gives a nonzero class modulo G.',fontsize=11.5,color=MUTED)
    fig.text(.055,.061,'This is an exact obstruction with complete numerator freedom for this family; it does not exclude other degree-five denominators or solve the target.',fontsize=11.3)
    fig.text(.945,.023,'cyclic-triple-fano · discussion #112',ha='right',fontsize=10,color=TEAL)
    OUT.mkdir(parents=True,exist_ok=True);stem=OUT/'cyclic-fano-polar-family'
    fig.savefig(stem.with_suffix('.png'),dpi=160,facecolor=PAPER)
    svg=stem.with_suffix('.svg');fig.savefig(svg,facecolor=PAPER,metadata={'Date':None})
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8',newline='\n')
    plt.close(fig)


def main():
    if not __debug__:raise RuntimeError('Run without -O so exact checks remain active.')
    data=check_data()
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'text.color':INK,'axes.labelcolor':INK,
                         'svg.fonttype':'none','svg.hashsalt':'cyclic-fano-polar-family-v1'})
    draw(data)
    (OUT/'plot-data.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':'PASS','five_coefficient_rows':True,'all_nonzero_constant_directions_excluded':True}))


if __name__=='__main__':main()
