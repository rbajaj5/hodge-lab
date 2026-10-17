#!/usr/bin/env python3
"""Show checked higher local jets, heuristic denominators and exact failures.

The coefficient support and local leading cubic are exact data. Extending a
local branch approximation to a global denominator is explicitly a heuristic.
"""
from __future__ import annotations
import ast
import cmath
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import sympy as S

ROOT=Path(__file__).resolve().parents[1]
HIGH=ROOT/'results/cyclic-fano-higher-unfolding'
TESTS=ROOT/'results/cyclic-fano-guided-denominators'
OUT=ROOT/'results/cyclic-fano-higher-unfolding-figures'
INK,MUTED,PAPER,GRAY='#17323B','#53666D','#FAFAF5','#CBD3D0'
TEAL,PURPLE,CORAL='#166A70','#7967AA','#CA584C'
WEIGHTS=(1,1,3,1,1,1)
IDS=('full-tangent-linear','Y0-center-cubic','Y0-leading-branch-sextic',
     'tangent_norm_power_1','tangent_norm_power_2','tangent_norm_power_3',
     'jacobian_tangent','jacobian_center_cubic','jacobian_tangent_norm')


def sha(path):return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def pair(value):return S.Rational(value[0])+S.I*S.Rational(value[1])
def pairs(value):return [str(x) for x in S.expand_complex(S.simplify(value)).as_real_imag()]
def decode(terms):return {tuple(t['powers']):pair(t['coefficient']) for t in terms}
def expression(terms,variables):return S.expand(sum(pair(t['coefficient'])*S.prod(x**n for x,n in zip(variables,t['powers'])) for t in terms))


def monomials(degree,weights=WEIGHTS):
    if degree<0:return []
    if len(weights)==1:return [(degree//weights[0],)] if degree%weights[0]==0 else []
    return [(k,)+tail for k in range(degree//weights[0],-1,-1) for tail in monomials(degree-k*weights[0],weights[1:])]


def parse(text,names):
    symbols=S.symbols(' '.join(names))
    def visit(node):
        if isinstance(node,ast.Constant) and type(node.value) is int:return S.Integer(node.value)
        if isinstance(node,ast.Name) and node.id in names:return symbols[names.index(node.id)]
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,ast.USub):return -visit(node.operand)
        if isinstance(node,ast.BinOp):
            left=visit(node.left)
            if isinstance(node.op,ast.Pow):
                assert isinstance(node.right,ast.Constant) and type(node.right.value) is int and node.right.value>=0
                return left**node.right.value
            right=visit(node.right)
            if isinstance(node.op,ast.Add):return left+right
            if isinstance(node.op,ast.Sub):return left-right
            if isinstance(node.op,ast.Mult):return left*right
            if isinstance(node.op,ast.Div):
                assert right.is_Rational and right!=0
                return left/right
        raise ValueError('Unsupported polynomial syntax')
    return symbols,S.Poly(S.expand(visit(ast.parse(text,mode='eval').body)),*symbols)


def check_data():
    producer=ROOT/'experiments/cyclic_fano_higher_unfolding.py'
    arithmetic=ROOT/'experiments/cyclic_fano_unfolding.py'
    checker=ROOT/'experiments/check_cyclic_fano_higher_unfolding.py'
    candidate_path=HIGH/'candidates.json';candidates=load(candidate_path)
    target_path=ROOT/'results/cyclic-fano-curve/target.json';target=load(target_path)
    raw=target_path.parent/'source/instance.rec'
    review_path=HIGH/'independent-validation.json';review=load(review_path)
    assert candidates['schema']=='cyclic-fano-higher-unfolding-candidates-v1'
    assert candidates['producer_sha256']==sha(producer)
    assert candidates['arithmetic_dependency_sha256']==sha(arithmetic)
    assert candidates['fixed_target_manifest_sha256']==sha(target_path)
    assert review['status']=='PASS' and review['checker_lf_sha256']==sha(checker)
    assert review['source_instance_lf_sha256']==sha(raw)
    independent_arithmetic=ROOT/'experiments/check_cyclic_fano_unfolding.py'
    assert review['independent_arithmetic_dependency_lf_sha256']==sha(independent_arithmetic)
    candidate_receipt_path=HIGH/'candidates-validation.json';candidate_receipt=load(candidate_receipt_path)
    assert candidate_receipt['status']=='PASS' and candidate_receipt['producer_sha256']==sha(producer)
    assert candidate_receipt['packet_sha256']==review['candidate_construction']['packet_lf_sha256']==sha(candidate_path)
    prior_T1=ROOT/'results/cyclic-fano-unfolding/unfolding.json'
    assert review['candidate_construction']['prior_full_T1_packet_lf_sha256']==sha(prior_T1)
    axis_reviews={a['parameter_direction']:a for a in review['axes']}
    jets={};bindings={};b,V,w=S.symbols('b V w')
    for axis,order in (('X0',12),('Y0',8)):
        path=HIGH/f'unfolding-{axis}-order{order}.json';receipt_path=HIGH/f'validation-{axis}-order{order}.json'
        packet,receipt=load(path),load(receipt_path)
        assert packet['schema']=='cyclic-fano-higher-unfolding-v1' and packet['instance']=='cyclic-triple-fano'
        assert packet['producer_sha256']==receipt['producer_sha256']==sha(producer)
        assert packet['jet_total_order']==order and packet['parameter_direction']==axis
        assert receipt['status']=='PASS'
        assert receipt['packet_sha256']==axis_reviews[axis]['packet_lf_sha256']==candidates['source_jet_packet_sha256'][axis]==sha(path)
        assert packet['fixed_target_manifest_sha256']==sha(target_path)
        assert packet['arithmetic_dependency_sha256']==sha(arithmetic)
        assert pair(packet['constant_implicit_jacobian_determinant'])==-S.Rational(135000,2401)
        assert packet['checks']['all_seven_physical_coefficients_zero_through_total_order']==order
        assert all(len(t['powers'])==3 and t['powers'][2]==0 and sum(t['powers'])<=order for t in packet['evaluation_graph_h'])
        graph=S.Poly(expression(packet['evaluation_graph_h'],(b,V,S.Symbol('unused'))),b,V)
        assert min(sum(m) for m,c in graph.terms())==3
        for key,limit in (('center_height','center_height_valid_order'),('centered_linear_coefficient','centered_linear_valid_order'),
                          ('centered_cubic_coefficient','centered_cubic_valid_order')):
            assert all(t['powers'][0]==t['powers'][2]==0 and t['powers'][1]<=packet[limit] for t in packet[key])
        jets[axis]=(packet,graph)
        bindings[path.relative_to(ROOT).as_posix()]=sha(path)
        bindings[receipt_path.relative_to(ROOT).as_posix()]=sha(receipt_path)
    X0=jets['X0'][0]
    assert not X0['center_height'] and not X0['centered_linear_coefficient']
    assert X0['center_height_valid_order']==12 and X0['centered_linear_valid_order']==11
    packet,graph=jets['Y0']
    cubic=S.expand(sum(c*b**m[0]*V**m[1] for m,c in graph.terms() if sum(m)==3))
    assert cubic==expression(candidates['leading_graph_cubic'],(b,V))
    a=S.Rational(5,6)+8*S.I/35;B=S.Rational(5,21)+S.I/2;c=5*S.I/42
    assert S.expand(cubic-a*b**3-B*b**2*V-c*b*V**2)==0
    shift=S.simplify(-B/(3*a));assert S.simplify(shift-pair(candidates['inflection_shift_linear']))==0
    centered=S.Poly(S.expand(cubic.subs(b,w+shift*V)),w,V)
    lam=centered.coeff_monomial(w*V**2);mu=centered.coeff_monomial(V**3)
    assert centered.coeff_monomial(w**2*V)==0
    assert S.simplify(lam-pair(candidates['centered_linear_leading']))==0 and lam!=0
    assert S.simplify(mu-pair(candidates['center_height_leading']))==0
    gamma=S.simplify(4*lam**3/(27*a))
    assert S.simplify(gamma-pair(candidates['leading_branch_gamma']))==0 and gamma!=0
    h=S.Symbol('h');branch=expression(candidates['leading_branch_equation'],(V,h))
    assert S.Poly(S.expand(branch-(h-mu*V**3)**2-gamma*V**6),V,h).is_zero
    assert candidates['local_branch_contact_order']==3 and candidates['critical_value_leading_coefficients_are_distinct']
    critical_values=[complex(mu.evalf())+cmath.sqrt(-complex(gamma.evalf())),complex(mu.evalf())-cmath.sqrt(-complex(gamma.evalf()))]
    critical_values.sort(key=lambda z:z.real)

    # Rebuild candidate polynomials from their stated homogenization rule.
    X0s,X1,Z,Y0,Y1,Y2=S.symbols('X0 X1 Z Y0 Y1 Y2');variables=(X0s,X1,Z,Y0,Y1,Y2)
    T=-X1-S.I*Y2;L=Y0-S.I*X1;C=X1**2*T-mu*L**3;D=C**2+gamma*L**6;R=X1**2+Y2**2
    expected=dict(zip(IDS[:6],(T,C,D,R,R**2,R**3)))
    input_candidates={candidate['id']:candidate for candidate in candidates['candidates']}
    original_symbols,F=parse(target['target']['F'],('X0','X1','X2','Y0','Y1','Y2'))
    _,A=parse(target['target']['A'],('X0','X1','X2','Y0','Y1','Y2'))
    assert A.as_expr()==original_symbols[0]*original_symbols[2]**2*original_symbols[3]**3
    Gterms={}
    for powers,value in F.terms():
        assert powers[2]%3==0
        m=list(powers);m[2]//=3;Gterms[tuple(m)]=value
    G=S.Poly.from_dict(Gterms,variables)
    partials=[S.Poly(S.diff(G.as_expr(),x),*variables).as_dict() for x in variables]
    Gz=G.diff(Z);beta=S.Poly(X0s*Y0**3/3,*variables)
    expected.update(dict(zip(IDS[6:],(Gz.as_expr()*T,Gz.as_expr()*C,Gz.as_expr()*R))))
    repair_factors=dict(zip(IDS[6:],(T,C,R)))
    tests_producer=ROOT/'experiments/cyclic_fano_guided_denominators.py'
    tests_checker=ROOT/'experiments/check_cyclic_fano_guided_denominators.py'
    tests_primary_path=TESTS/'validation.json';tests_primary=load(tests_primary_path)
    tests_review_path=TESTS/'independent-validation.json';tests_review=load(tests_review_path)
    assert tests_primary['status']==tests_review['status']=='PASS'
    assert tests_primary['candidate_input_sha256']==tests_review['candidate_input_lf_sha256']==sha(candidate_path)
    assert tests_review['checker_lf_sha256']==sha(tests_checker)
    assert tests_review['independent_arithmetic_dependency_lf_sha256']==sha(independent_arithmetic)
    assert tests_review['source_instance_lf_sha256']==sha(raw)
    assert tests_review['source_and_gradient_mod5_Fermat_checked']
    assert not tests_primary['certificate_found'] and tests_review['negative_controls_rejected']==18
    primary_checks={item['id']:item for item in tests_primary['checks']}
    review_checks={item['id']:item for item in tests_review['checks']}
    assert set(primary_checks)==set(review_checks)==set(IDS)
    tests=[]
    for identity in IDS:
        path=TESTS/(identity+'.json');item=load(path)
        assert item['schema']=='cyclic-fano-guided-denominator-v1' and item['status']=='excluded'
        assert item['candidate_input_sha256']==sha(candidate_path)
        assert item['source_instance_sha256']==sha(raw)
        assert item['producer_sha256']==sha(tests_producer)
        for name,digest in item['arithmetic_dependencies'].items():assert sha(ROOT/'experiments'/name)==digest
        audit=review_checks[identity];primary=primary_checks[identity]
        assert audit['packet_lf_sha256']==primary['packet_sha256']==sha(path)
        assert audit['all_column_pairings_zero'] and pair(audit['rhs_pairing'])==1
        if identity in input_candidates:assert item['candidate']==input_candidates[identity]
        candidate=item['candidate'];degree=candidate['degree']
        E=S.Poly(expression(candidate['quotient_denominator'],variables),*variables)
        assert (E-S.Poly(S.expand(expected[identity]),*variables)).is_zero
        assert all(sum(e*q for e,q in zip(m,WEIGHTS))==degree for m in E.monoms())
        labels=[];mode=item['numerator_parameterization']
        if mode=='full_coefficient_basis':
            for i,weight in enumerate(WEIGHTS):
                labels.extend({'kind':'numerator','coordinate':i,'powers':list(m)} for m in monomials(degree+weight-2))
        else:
            assert mode=='complete_Koszul' and identity in repair_factors
            for i,wi in enumerate(WEIGHTS):
                for j in range(i+1,6):
                    labels.extend({'kind':'Koszul','coordinates':[i,j],'powers':list(m)}
                                  for m in monomials(degree+wi+WEIGHTS[j]-8))
        numerator_count=len(labels)
        labels.extend({'kind':'G_quotient','powers':list(m)} for m in monomials(2*degree-8))
        assert labels==item['column_labels']
        assert numerator_count==item['numerator_parameters']==audit['complete_numerator_or_correction_columns']
        assert sum(len(monomials(degree+weight-2)) for weight in WEIGHTS)==item['full_numerator_coefficients']==audit['full_numerator_coefficients']
        assert len(labels)-numerator_count==item['quotient_coefficients']==audit['quotient_columns']
        assert item['matrix_shape']==audit['matrix_shape']==primary['shape']
        assert item['matrix_shape'][1]==len(labels)
        physical=[]
        for row,coefficient in item['obstruction_functional']:
            source_row=item['coefficient_rows'][row]
            physical.append({'equation':source_row[0],'powers':source_row[1:],'coefficient':coefficient})
        assert physical==audit['physical_dual']
        stage='E1' if mode=='full_coefficient_basis' else 'E2'
        assert all(t['equation']==stage for t in physical)
        def apply_dual(polynomial):
            return S.simplify(sum(pair(t['coefficient'])*polynomial.coeff_monomial(tuple(t['powers'])) for t in physical))
        if mode=='full_coefficient_basis':
            # Replay the actual E1 dual against every complete weighted numerator column.
            assert len(physical)==1
            term=physical[0];monomial=tuple(term['powers']);functional=pair(term['coefficient'])
            for label in labels:
                if label['kind']=='G_quotient':continue
                difference=tuple(x-y for x,y in zip(monomial,label['powers']))
                value=0 if min(difference)<0 else partials[label['coordinate']].get(difference,0)
                assert S.simplify(functional*value)==0
            assert apply_dual(beta*E)==1
        else:
            factor=S.Poly(expression(candidate['jacobian_factor'],variables),*variables)
            assert (factor-S.Poly(S.expand(repair_factors[identity]),*variables)).is_zero
            assert (E-Gz*factor).is_zero and factor.diff(Z).is_zero
            P0z=beta*factor
            assert (P0z*Gz-beta*E).is_zero
            rhs=-(E*P0z.diff(Z)-P0z*E.diff(Z))
            assert (rhs-2*beta*factor**2).is_zero
            assert apply_dual(rhs)==1
            # Build every E2 correction from its physical Koszul field and every G quotient.
            for label in labels:
                mon=S.Poly.from_dict({tuple(label['powers']):S.Integer(1)},variables)
                if label['kind']=='G_quotient':column=-G*mon
                else:
                    i,j=label['coordinates'];Gi,Gj=G.diff(variables[i]),G.diff(variables[j])
                    divergence=mon.diff(variables[i])*Gj-mon.diff(variables[j])*Gi
                    derivative=mon*(Gj*E.diff(variables[i])-Gi*E.diff(variables[j]))
                    column=E*divergence-derivative
                assert apply_dual(column)==0
        assert not item['exact_rank_computed']
        tests.append({'id':identity,'degree':degree,'numerator_parameters':numerator_count,
                      'numerator_parameterization':mode,'full_numerator_coefficients':item['full_numerator_coefficients'],
                      'quotient_coefficients':item['quotient_coefficients'],'shape':item['matrix_shape'],
                      'physical_dual':physical,'obstruction_stage':stage,
                      'status':'excluded','dual_terms':len(physical),'source_packet_sha256':sha(path)})
        bindings[path.relative_to(ROOT).as_posix()]=sha(path)
    sources=(producer,arithmetic,checker,target_path,raw,candidate_path,review_path,
             independent_arithmetic,candidate_receipt_path,prior_T1,
             tests_producer,tests_checker,tests_primary_path,tests_review_path,
             *(ROOT/'experiments'/name for name in item['arithmetic_dependencies']))
    bindings.update({p.relative_to(ROOT).as_posix():sha(p) for p in sources})
    support=[list(m) for m,value in graph.terms()]
    result={'schema':'cyclic-fano-higher-unfolding-plot-v1','instance':'cyclic-triple-fano','discussion_number':112,
            'sha256_policy':'UTF-8 bytes with CRLF normalized to LF','source_sha256':bindings,'plot_source_sha256':sha(Path(__file__)),
            'Y0_graph_total_order':8,'Y0_graph_support_b_V':support,'leading_cubic_terms':candidates['leading_graph_cubic'],
            'center_shift_linear':pairs(shift),'lambda2':pairs(lam),'mu3':pairs(mu),'gamma':pairs(gamma),
            'critical_value_leading_coefficients_display':[[z.real,z.imag] for z in critical_values],
            'leading_curve_display':{'real_V_interval':[-1,1],'samples':201,'formula':'h=c*V^3',
                                     'higher_terms_displayed':False,'certified_approximation_radius':None},
            'critical_image_contact_order':3,'X0_height_zero_through_order':12,'X0_linear_zero_through_order':11,
            'tests':tests,'all_physical_dual_column_pairings_checked':sum(t['shape'][1] for t in tests),
            'scope':'Exact finite jets and local contact-order-three consequence; leading branch polynomial only. Homogenized denominators are heuristic extensions. Exact E1 obstructions reject six direct fixed candidates; exact E2 obstructions reject three Jacobian repairs with complete Koszul and quotient freedom. No arbitrary denominator, unspecified power, global support or certificate conclusion.'}
    return result


def style(ax):
    ax.set_facecolor(PAPER)
    for side in ('top','right'):ax.spines[side].set_visible(False)
    for side in ('left','bottom'):ax.spines[side].set_color(GRAY)
    ax.tick_params(colors=MUTED,labelsize=10)


def draw(data):
    fig=plt.figure(figsize=(16,14),facecolor=PAPER)
    fig.text(.055,.953,'Higher jets guide nine candidates; exact tests reject each one',fontsize=23,weight='bold')
    fig.text(.055,.922,'cyclic-triple-fano · discussion #112   |   Selected Y₀ target surface · exact local jets over Q(i)',fontsize=12,color=MUTED)
    ax=fig.add_axes([.065,.542,.345,.314]);style(ax)
    for j in range(9):
        for k in range(9-j):ax.scatter(k,j,s=17,facecolors='none',edgecolors=GRAY,lw=.8)
    for j,k in data['Y0_graph_support_b_V']:
        ax.scatter(k,j,s=80 if j+k==3 else 38,color=CORAL if j+k==3 else TEAL,marker='o',zorder=3)
    ax.plot([0,8],[8,0],color=GRAY,lw=1,ls='--')
    ax.set_xlim(-.6,8.6);ax.set_ylim(-.6,8.6);ax.set_aspect('equal');ax.set_xticks(range(9));ax.set_yticks(range(9))
    ax.set_xlabel('power of transverse target coordinate V');ax.set_ylabel('power of curve parameter b')
    ax.set_title('Exact coefficient support of H(b,V) through degree 8',fontsize=14,loc='left',pad=16)
    fig.text(.065,.487,'Filled: nonzero coefficient  ·  Open: checked zero  ·  Coral: degree 3',fontsize=10.5,color=MUTED)
    fig.text(.065,.464,'Degrees beyond the triangle remain unknown.',fontsize=10.5,color=MUTED)

    x=.465
    fig.text(x,.866,'Two local critical-value branches have contact order 3',fontsize=16,weight='bold')
    fig.text(x,.818,r'$H_3=\left(\frac{5}{6}+\frac{8i}{35}\right)b^3+\left(\frac{5}{21}+\frac{i}{2}\right)b^2V+\frac{5i}{42}bV^2$',fontsize=19,color=TEAL)
    fig.text(x,.771,r'$h=c_\pm V^3+O(V^4),\qquad(c_\pm-\mu_3)^2+\gamma=0$',fontsize=18)
    values=data['critical_value_leading_coefficients_display']
    display=data['leading_curve_display']
    v=np.linspace(*display['real_V_interval'],display['samples'])
    for component,left in enumerate((.485,.755)):
        curve=fig.add_axes([left,.542,.19,.174]);style(curve)
        for number,(value,color) in enumerate(zip(values,(TEAL,PURPLE))):
            curve.plot(v,value[component]*v**3,color=color,lw=2.3,
                       ls='-' if number==0 else '--',label='branch '+str(number+1))
        curve.axhline(0,color=GRAY,lw=.8,zorder=0);curve.axvline(0,color=GRAY,lw=.8,zorder=0)
        curve.set_xlim(-1,1);curve.set_xticks([-1,0,1]);curve.set_xlabel('real V',labelpad=2)
        curve.set_title(('Re h','Im h')[component]+' of the leading jets',fontsize=11,pad=11)
        curve.ticklabel_format(axis='y',style='sci',scilimits=(0,0))
        if component==0:curve.legend(frameon=False,fontsize=8.5,loc='upper left')
    fig.text(x,.496,'Curves show only h = c±V³ on a chosen real-V display interval.',fontsize=10.5,color=MUTED)
    fig.text(x,.475,'Higher terms omitted; no convergence or approximation radius is certified.',fontsize=10.5,color=MUTED)
    fig.text(x,.449,r'X₀ attempt: $\mu=O(U^{13})$, $\lambda=O(U^{12})$; no exact vanishing claim.',fontsize=11,color=PURPLE)

    fig.text(.055,.420,'Heuristic extension to denominators on the full target',fontsize=18,weight='bold')
    fig.text(.055,.383,r'$T=-X_1-iY_2,\quad L=Y_0-iX_1,\quad C=X_1^2T-\mu_3L^3,\quad S=C^2+\gamma L^6,\quad R=X_1^2+Y_2^2$',fontsize=17,color=TEAL)
    fig.text(.055,.353,'The extension away from the chosen target surface is a guess. Each resulting polynomial is then tested exactly.',fontsize=11,color=MUTED)
    ax=fig.add_axes([.06,.128,.88,.201]);ax.axis('off')
    labels=[r'$T$',r'$C$',r'$S$',r'$R$',r'$R^2$',r'$R^3$',r'$G_ZT$',r'$G_ZC$',r'$G_ZR$']
    rows=[]
    for label,t in zip(labels,data['tests']):
        mode='direct coefficients' if t['numerator_parameterization']=='full_coefficient_basis' else 'Koszul corrections'
        rows.append([label,str(t['degree']),f"{t['numerator_parameters']} {mode}",str(t['quotient_coefficients']),
                     str(t['dual_terms']),t['obstruction_stage']+' excluded'])
    table=ax.table(cellText=rows,colLabels=['denominator','degree','numerator search coordinates','quotient coefficients','dual terms','exact result'],
                   colWidths=[.13,.07,.30,.20,.12,.18],cellLoc='center',bbox=[0,0,1,1])
    table.auto_set_font_size(False);table.set_fontsize(11.5)
    for (r,c),cell in table.get_celld().items():
        cell.set_edgecolor('white');cell.set_linewidth(1.4);cell.set_text_props(color=INK)
        cell.set_facecolor('#E5ECE8' if r%2 else PAPER)
        if r==0:cell.set_facecolor(TEAL);cell.set_text_props(color='white',weight='bold')
        elif c==5:cell.set_text_props(color=CORAL)
    fig.text(.055,.096,r'For the last three, $G_Z=\partial G/\partial Z$, $\beta=X_0Y_0^3/3$, and $P_Z^0=\beta f$ solve E1; all Koszul corrections still fail E2.',fontsize=12)
    fig.text(.055,.071,r'Every displayed dual gives $\ell M=0$ and $\ell\,\mathrm{rhs}=1$. Counts include the complete quotient freedom; no full matrix ranks are claimed.',fontsize=11.5)
    fig.text(.055,.042,'Nine fixed denominators are excluded. Other denominators, global support, and a certificate remain open.',fontsize=12,color=CORAL)
    fig.text(.945,.017,'cyclic-triple-fano · discussion #112',ha='right',fontsize=10,color=TEAL)
    OUT.mkdir(parents=True,exist_ok=True);stem=OUT/'cyclic-fano-higher-unfolding'
    fig.savefig(stem.with_suffix('.png'),dpi=160,facecolor=PAPER)
    svg=stem.with_suffix('.svg');fig.savefig(svg,facecolor=PAPER,metadata={'Date':None})
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8',newline='\n')
    plt.close(fig)


def main():
    if not __debug__:raise RuntimeError('Run without -O so exact checks remain active.')
    data=check_data()
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'text.color':INK,'axes.labelcolor':INK,
                         'svg.fonttype':'none','svg.hashsalt':'cyclic-fano-higher-unfolding-v1'})
    draw(data)
    (OUT/'plot-data.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':'PASS','Y0_jet_order':8,'X0_jet_order':12,'fixed_candidates_excluded':len(data['tests'])}))


if __name__=='__main__':main()
