#!/usr/bin/env python3
"""Visualize seven exact first-polar tests and an actual Koszul coefficient map."""
from __future__ import annotations
import ast
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
import sympy as S

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'results/cyclic-fano-branch-polars'
OUT=ROOT/'results/cyclic-fano-branch-polars-figures'
NAMES=('X0','X1','Y0','Y1','Y2')
BASE=(0,1,3,4,5)
W=(1,1,3,1,1,1)
SPECS=[('polar_'+name,tuple(int(i==j) for i in range(5))) for j,name in enumerate(NAMES)]
SPECS += [('polar_X0_plus_Y0',(1,0,1,0,0)),('polar_X1_plus_Y1',(0,1,0,1,0))]
INK,MUTED,PAPER,GRAY='#17323B','#53666D','#FAFAF5','#CBD3D0'
TEAL,PURPLE,CORAL='#166A70','#7967AA','#CA584C'


def sha(path):return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def pair(value):return S.Rational(value[0])+S.I*S.Rational(value[1])
def decode(terms,variables):return S.Poly.from_dict({tuple(t['powers']):pair(t['coefficient']) for t in terms},variables)
def monomials(degree,weights=W):
    if degree<0:return []
    if len(weights)==1:return [(degree//weights[0],)] if degree%weights[0]==0 else []
    return [(k,)+tail for k in range(degree//weights[0],-1,-1) for tail in monomials(degree-k*weights[0],weights[1:])]


def parse_polynomial(text,variables):
    names={str(x):x for x in variables}
    def visit(node):
        if isinstance(node,ast.Constant) and type(node.value) is int:return S.Integer(node.value)
        if isinstance(node,ast.Name) and node.id in names:return names[node.id]
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
    return S.Poly(S.expand(visit(ast.parse(text,mode='eval').body)),variables)


def check_data():
    producer=ROOT/'experiments/cyclic_fano_branch_polars.py'
    checker=ROOT/'experiments/check_cyclic_fano_branch_polars.py'
    primary_path=INPUT/'validation.json';primary=load(primary_path)
    review_path=INPUT/'independent-validation.json';review=load(review_path)
    target_path=ROOT/'results/cyclic-fano-curve/target.json';target=load(target_path)
    raw=target_path.parent/'source/instance.rec'
    assert primary['status']==review['status']=='PASS'
    assert review['schema']=='cyclic-fano-branch-polars-independent-v1'
    assert primary['producer_sha256']==sha(producer) and review['checker_lf_sha256']==sha(checker)
    assert primary['source_instance_sha256']==review['source_instance_lf_sha256']==sha(raw)
    assert not primary['unresolved'] and not review.get('unresolved',[])
    assert review['negative_controls_rejected']==21
    bindings={p.relative_to(ROOT).as_posix():sha(p) for p in (producer,checker,primary_path,review_path,target_path,raw)}
    for name,digest in review['independent_arithmetic_dependencies'].items():
        path=ROOT/'experiments'/name;assert sha(path)==digest
        bindings[path.relative_to(ROOT).as_posix()]=digest
    audited={c['id']:c for c in review['checks']};checked={c['id']:c for c in primary['checks']}
    assert set(audited)==set(checked)=={name for name,v in SPECS}
    variables=S.symbols('X0 X1 Z Y0 Y1 Y2');X0,X1,Z,Y0,Y1,Y2=variables
    original=S.symbols('X0 X1 X2 Y0 Y1 Y2')
    F=parse_polynomial(target['target']['F'],original);terms={}
    for m,c in F.terms():
        assert m[2]%3==0;n=list(m);n[2]//=3;terms[tuple(n)]=c
    G=S.Poly.from_dict(terms,variables)
    q=S.Poly.from_dict({m[:2]+(0,)+m[3:]:c for m,c in G.terms() if m[2]==1},variables)
    h=S.Poly.from_dict({m:c for m,c in G.terms() if m[2]==0},variables)
    Delta=q*q-4*h;beta=S.Poly(X0*Y0**3/3,variables)
    assert G==S.Poly(Z**2,variables)+q*S.Poly(Z,variables)+h
    zero=S.Poly(0,variables);grad=[G.diff(x) for x in variables]
    labels=[]
    for i in range(6):
        for j in range(i+1,6):
            labels.extend({'coordinates':[i,j],'powers':list(m)} for m in monomials(5+W[i]+W[j]-8))
    assert len(labels)==25 and len(monomials(2))==15
    results=[];example=None
    for name,v in SPECS:
        path=INPUT/(name+'.json');packet=load(path)
        attempt_path=INPUT/('attempt-'+name+'.json');attempt=load(attempt_path)
        audit=audited[name]
        assert packet['schema']=='cyclic-fano-branch-polars-v1'
        assert packet['id']==name and packet['status']==audit['status']=='excluded'
        assert packet['producer_sha256']==sha(producer)
        assert packet['source_instance_sha256']==sha(raw)
        assert packet['direction']==list(v) and packet['direction_variables']==list(NAMES)
        assert packet['weighted_variables']==list(map(str,variables)) and packet['degree']==5
        assert attempt['status']=='completed' and attempt['returncode']==0
        assert attempt['bindings']['producer_sha256']==sha(producer) and attempt['direction']==list(v)
        assert audit['packet_lf_sha256']==checked[name]['packet_sha256']==sha(path)
        assert audit['attempt_lf_sha256']==sha(attempt_path)
        assert audit['E1_exact_lift_checked'] and audit['Piola_identities_checked_on_original_target']
        assert audit['raw_Koszul_columns_checked']==25 and audit['raw_quotient_columns_checked']==15
        assert audit['all_40_columns_have_zero_even_projection'] and audit['nonzero_even_residual_checked']
        for dependency,digest in packet['dependencies'].items():
            dep=ROOT/'experiments'/dependency;assert sha(dep)==digest
            bindings[dep.relative_to(ROOT).as_posix()]=digest
        def derivative(poly):return sum((v[i]*poly.diff(variables[j]) for i,j in enumerate(BASE)),zero)
        E=derivative(Delta)
        assert E==decode(packet['denominator'],variables) and Delta==decode(packet['Delta'],variables)
        assert all(m[2]==0 and sum(m)==5 for m in E.monoms())
        P=[zero for _ in range(6)]
        for i,j in enumerate(BASE):P[j]=-4*v[i]*beta
        P[2]=2*beta*derivative(q)
        assert all((p-decode(terms,variables)).is_zero for p,terms in zip(P,packet['particular']))
        assert sum((p*g for p,g in zip(P,grad)),zero)==beta*E
        divergence=sum((p.diff(x) for p,x in zip(P,variables)),zero)
        residual=E*divergence-sum((p*E.diff(x) for p,x in zip(P,variables)),zero)
        assert residual==4*(beta*derivative(E)-derivative(beta)*E)
        assert residual==decode(packet['residual'],variables)
        assert residual==decode(audit['particular_residual'],variables)
        rhs=-residual;assert rhs==decode(packet['rhs'],variables)
        assert len(packet['dual'])==1
        dual=packet['dual'][0];row=tuple(dual['powers']);weight=pair(dual['coefficient'])
        coefficient=rhs.coeff_monomial(row)
        assert S.simplify(weight*coefficient)==1
        def physical_dual(poly):
            return S.simplify(sum(pair(t['coefficient'])*poly.coeff_monomial(tuple(t['powers']))
                                  for t in audit['producer_dual_on_full_physical_rows']))
        assert physical_dual(rhs)==pair(audit['rhs_pairing'])==1
        assert [c['label'] for c in packet['columns']]==labels
        supports=[]
        for column,label in zip(packet['columns'],labels):
            i,j=label['coordinates'];m=S.Poly.from_dict({tuple(label['powers']):1},variables)
            divergence=m.diff(variables[i])*grad[j]-m.diff(variables[j])*grad[i]
            raw_column=E*divergence-m*(grad[j]*E.diff(variables[i])-grad[i]*E.diff(variables[j]))
            # Here all 25 degree-five columns already have Z-degree at most 1.
            assert raw_column.degree(Z)<=1
            assert raw_column==decode(column['polynomial'],variables)
            assert raw_column.coeff_monomial(row)==0
            assert physical_dual(raw_column)==0
            supports.append(set(raw_column.monoms()) if not raw_column.is_zero else set())
        for m in monomials(2):
            assert physical_dual(G*S.Poly.from_dict({m:1},variables))==0
        active=sorted(set(rhs.monoms()).union(*supports))
        assert len(active)==packet['active_rows']
        assert packet['ambient_remainder_rows']==len([m for m in monomials(8) if m[2]<2])==621
        assert packet['complete_Koszul_directions']==25 and packet['quotient_dimension_eliminated']==15
        assert packet['full_projected_numerator_dimension']==sum(len(monomials(5+w-2)) for w in W)==621
        results.append({'id':name,'direction':list(v),'degree':5,'status':'excluded','E1_identity_checked':True,
                        'dual_monomial':list(row),'rhs_coefficient':str(coefficient),'dual_weight':str(weight),
                        'correction_coefficient_at_dual_row':0,'dual_rhs_pairing':1,
                        'rhs_terms':len(rhs.terms()),'active_rows':len(active),'columns':25,
                        'quotient_directions_eliminated':15,'packet_lf_sha256':sha(path)})
        if name=='polar_Y0':
            row_index={m:i for i,m in enumerate(active)}
            example={'id':name,'row_monomials':[list(m) for m in active],
                     'column_labels':labels,'nonzero_correction_entries':[[row_index[m],j] for j,col in enumerate(supports) for m in sorted(col)],
                     'nonzero_rhs_rows':[row_index[m] for m in rhs.monoms()],
                     'obstruction_row':row_index[row],'zero_rows_omitted':621-len(active),'ambient_rows':621}
        bindings[path.relative_to(ROOT).as_posix()]=sha(path)
        bindings[attempt_path.relative_to(ROOT).as_posix()]=sha(attempt_path)
    assert example is not None
    return {'schema':'cyclic-fano-branch-polars-plot-v1','instance':'cyclic-triple-fano','discussion_number':112,
            'sha256_policy':'File bytes with CRLF normalized to LF','source_sha256':bindings,'plot_source_sha256':sha(Path(__file__)),
            'direction_variables':list(NAMES),'tests':results,'example_map':example,
            'scope':'Seven fixed first polars of Delta only. Their explicit E1 lifts exist; complete E2 systems fail. The full projective family of polar directions is not excluded.'}


def monomial_label(powers):
    names=('X_0','X_1','Z','Y_0','Y_1','Y_2')
    return '$'+''.join(x+(f'^{{{n}}}' if n>1 else '') for x,n in zip(names,powers) if n)+'$'


def draw(data):
    fig=plt.figure(figsize=(16,11),facecolor=PAPER)
    fig.text(.055,.95,'First polars solve E1; seven tested directions fail E2',fontsize=23,weight='bold')
    fig.text(.055,.916,'cyclic-triple-fano · discussion #112   |   Seven fixed degree-five denominators; exact rational arithmetic',fontsize=12,color=MUTED)
    fig.text(.055,.86,r'$G=Z^2+QZ+H,\quad\Delta=Q^2-4H,\quad E_v=\partial_v\Delta,\quad\beta=X_0Y_0^3/3$',fontsize=18,color=TEAL)
    fig.text(.055,.804,r'$P_i^0=-4\beta v_i\ (i\ne Z),\quad P_Z^0=2\beta\partial_vQ\qquad\Longrightarrow\qquad P^0(G)=\beta E_v$',fontsize=20)
    fig.text(.055,.767,'The E1 lift is explicit. E2 still requires a correction among all 25 weighted Koszul directions.',fontsize=12,color=MUTED)
    fig.text(.055,.706,'Each remainder coefficient gives an exact obstruction',fontsize=16,weight='bold')
    ax=fig.add_axes([.055,.405,.47,.267]);ax.axis('off')
    names=[r'$e_{X_0}$',r'$e_{X_1}$',r'$e_{Y_0}$',r'$e_{Y_1}$',r'$e_{Y_2}$',r'$e_{X_0}+e_{Y_0}$',r'$e_{X_1}+e_{Y_1}$']
    rows=[[name,monomial_label(r['dual_monomial']),r['rhs_coefficient'],r['dual_weight']] for name,r in zip(names,data['tests'])]
    table=ax.table(cellText=rows,colLabels=['direction v','coefficient monomial','rhs coefficient','dual weight ℓ'],
                   colWidths=[.26,.32,.22,.20],cellLoc='center',bbox=[0,0,1,1])
    table.auto_set_font_size(False);table.set_fontsize(11.5)
    for (row,col),cell in table.get_celld().items():
        cell.set_edgecolor('white');cell.set_linewidth(1.4);cell.set_text_props(color=INK)
        cell.set_facecolor('#E5ECE8' if row%2 else PAPER)
        if row==0:cell.set_facecolor(TEAL);cell.set_text_props(color='white',weight='bold',fontsize=10.5)
    fig.text(.055,.367,'At each listed monomial: every correction coefficient is zero.',fontsize=11.5)
    fig.text(.055,.329,r'Every row therefore gives $\ell M=0$ but $\ell\,\mathrm{rhs}=1$.',fontsize=16,color=PURPLE)
    fig.text(.055,.277,r'$B_{E_v}(P^0)=4\left(\beta\partial_vE_v-(\partial_v\beta)E_v\right)$',fontsize=17,color=TEAL)
    fig.text(.055,.239,'A nonzero residual alone would not prove failure.',fontsize=11.5,color=MUTED)
    fig.text(.055,.210,'The exact dual rules out every allowed Koszul correction.',fontsize=11.5,color=MUTED)

    example=data['example_map'];nrows=len(example['row_monomials'])
    occupancy=np.zeros((nrows,27),dtype=int)
    for row,col in example['nonzero_correction_entries']:occupancy[row,col]=1
    for row in example['nonzero_rhs_rows']:occupancy[row,26]=2
    ax=fig.add_axes([.615,.329,.315,.343])
    ax.imshow(occupancy,cmap=ListedColormap([PAPER,TEAL,CORAL]),vmin=0,vmax=2,aspect='auto',interpolation='nearest')
    selected=example['obstruction_row']
    ax.axhline(selected,color=PURPLE,lw=1.3,ls='--')
    ax.scatter([26],[selected],s=45,facecolors='none',edgecolors=PURPLE,linewidths=1.3,zorder=4)
    ax.set_xticks([0,4,9,14,19,24,26],['1','5','10','15','20','25','rhs'])
    ax.set_xlabel('25 complete Koszul correction columns + rhs',fontsize=10.5)
    ax.set_ylabel('active monomial row (zero rows omitted)',fontsize=10.5)
    ax.tick_params(labelsize=9,colors=MUTED)
    for spine in ax.spines.values():spine.set_color(GRAY)
    fig.text(.615,.706,r'Actual coefficient map for $v=e_{Y_0}$',fontsize=16,weight='bold')
    fig.text(.615,.272,'Teal: nonzero matrix coefficient · Coral: right-hand side.',fontsize=10.5,color=MUTED)
    fig.text(.615,.245,f"{nrows} active rows; {example['zero_rows_omitted']} all-zero rows omitted from 621.",fontsize=10.5,color=MUTED)
    fig.text(.615,.213,r'Highlighted row: $X_0Y_0^7$, rhs $=64$, $\ell=1/64$.',fontsize=12,color=PURPLE)
    fig.text(.055,.153,'Exact division modulo G preserves all 15 allowed quotient directions; none are forced to zero.',fontsize=12)
    fig.text(.055,.111,'All seven fixed denominators are excluded. The full family of polar directions and the target certificate remain open.',fontsize=12,color=CORAL)
    fig.text(.055,.067,'First-polar construction: Dolgachev, Classical Algebraic Geometry, §1.1.2 (user-supplied excerpt).',fontsize=10.5,color=MUTED)
    fig.text(.945,.028,'cyclic-triple-fano · discussion #112',ha='right',fontsize=10,color=TEAL)
    OUT.mkdir(parents=True,exist_ok=True);stem=OUT/'cyclic-fano-branch-polars'
    fig.savefig(stem.with_suffix('.png'),dpi=160,facecolor=PAPER)
    svg=stem.with_suffix('.svg');fig.savefig(svg,facecolor=PAPER,metadata={'Date':None})
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8',newline='\n')
    plt.close(fig)


def main():
    if not __debug__:raise RuntimeError('Run without -O so exact checks remain active.')
    data=check_data()
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'text.color':INK,'axes.labelcolor':INK,
                         'svg.fonttype':'none','svg.hashsalt':'cyclic-fano-branch-polars-v1'})
    draw(data)
    (OUT/'plot-data.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':'PASS','fixed_polars_excluded':len(data['tests']),
                      'Koszul_columns_reconstructed':25*len(data['tests']),'quotient_columns_checked':15*len(data['tests'])}))


if __name__=='__main__':main()
