#!/usr/bin/env python3
"""Draw the exact linear-polar exclusion and its actual coefficient maps."""
from __future__ import annotations
from fractions import Fraction as Q
import hashlib
from itertools import combinations_with_replacement
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
import sympy as S

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'results/cyclic-fano-linear-polars'
OUT=ROOT/'results/cyclic-fano-linear-polars-figures'
INK,MUTED,PAPER='#17323B','#53666D','#FAFAF5'
TEAL,PURPLE,CORAL='#166A70','#7967AA','#CA584C'


def sha(path):return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def sparse(terms):return {tuple(t['powers']):Q(t['coefficient']) for t in terms}
def dot(a,b):return sum((c*b.get(m,0) for m,c in a.items()),Q(0))
def poly(terms,variables):return S.Poly.from_dict({m:S.Rational(c.numerator,c.denominator) for m,c in sparse(terms).items()},variables)
def map_points(columns):
    rows=sorted({m for p in columns for m in p});lookup={m:i for i,m in enumerate(rows)}
    entries=[[lookup[m],j] for j,p in enumerate(columns) for m,c in p.items() if c]
    return {'shape':[len(rows),len(columns)],'row_monomials':[list(m) for m in rows],'nonzero_positions':entries}


def check_data():
    path=INPUT/'packet.json';packet=load(path)
    primary_path=INPUT/'validation.json';primary=load(primary_path)
    review_path=INPUT/'independent-validation.json';review=load(review_path)
    producer=ROOT/'experiments/cyclic_fano_linear_polars.py'
    checker=ROOT/'experiments/check_cyclic_fano_linear_polars.py'
    raw=ROOT/'results/cyclic-fano-curve/source/instance.rec'
    assert packet['schema']=='cyclic-fano-linear-polars-v1' and primary['schema']=='cyclic-fano-linear-polars-validation-v1'
    assert review['schema']=='cyclic-fano-linear-polars-independent-v1'
    assert packet['status']==primary['status']==review['status']=='PASS'
    assert packet['producer_sha256']==primary['producer_sha256']==sha(producer)
    assert primary['packet_sha256']==review['packet_lf_sha256']==sha(path)
    assert review['primary_validation_lf_sha256']==sha(primary_path) and review['checker_lf_sha256']==sha(checker)
    assert packet['source_instance_sha256']==review['source_instance_lf_sha256']==sha(raw)
    assert packet['instance']=='cyclic-triple-fano' and packet['q']==1 and packet['degree']==6
    bindings={p.relative_to(ROOT).as_posix():sha(p) for p in (path,primary_path,review_path,producer,checker,raw)}
    for dependency_map in (packet['dependencies'],review['independent_arithmetic_dependencies']):
        for name,digest in dependency_map.items():
            p=ROOT/'experiments'/name;assert sha(p)==digest;bindings[p.relative_to(ROOT).as_posix()]=digest
    x=S.symbols('X0 X1 Z Y0 Y1 Y2');base=(0,1,3,4,5);a=S.symbols('a0:5')
    Delta,Qp,Hp,beta=(poly(packet[name],x) for name in ('Delta','Q','H','beta'))
    assert Delta==Qp*Qp-4*Hp
    G=S.Poly(x[2]**2,x)+Qp*S.Poly(x[2],x)+Hp
    gradients=[G.diff(t) for t in x];zero=S.Poly(0,x)
    basis=packet['basis'];assert len(basis)==25
    for k,b in enumerate(basis):
        i,j=divmod(k,5);assert b['matrix_indices']==[i,j]
        E=S.Poly(x[base[j]],x)*Delta.diff(x[base[i]])
        assert E==poly(b['E'],x)
        field=[poly(p,x) for p in b['particular']]
        assert sum((p*g for p,g in zip(field,gradients)),zero)==beta*E
    residuals=packet['quadratic_residual_basis'];mixed=packet['mixed_correction_basis']
    pairs=list(combinations_with_replacement(range(25),2))
    assert len(residuals)==325 and [tuple(p['matrix_indices']) for p in residuals]==pairs
    assert len(mixed)==250 and [(p['matrix_index'],p['constant_pair_index']) for p in mixed]==[(i,j) for i in range(25) for j in range(10)]
    full_columns=[sparse(p['polynomial']) for p in residuals+mixed]
    full_map=map_points(full_columns)
    assert full_map['shape']==[859,575]
    assert packet['full_map']=={'potential_rows':1001,'active_rows':859,'columns':575,'quadratic_columns':325,'mixed_columns':250,'rank':414}
    off_diagonal=set(range(25))-set(range(0,25,6))
    assert {w['parameter_index'] for w in packet['off_diagonal_square_duals']}==off_diagonal
    for witness in packet['off_diagonal_square_duals']:
        k=witness['parameter_index'];dual=sparse(witness['dual']);target=pairs.index((k,k))
        assert all(dot(dual,column)==int(j==target) for j,column in enumerate(full_columns))
    diagonal=packet['diagonal_stage'];active=[0,6,12,18,24]
    assert diagonal['parameter_indices']==active
    diag_indices=[j for j,(k,l) in enumerate(pairs) if k in active and l in active]
    diag_indices += [325+j for j,p in enumerate(mixed) if p['matrix_index'] in active]
    diag_columns=[full_columns[j] for j in diag_indices];diag_map=map_points(diag_columns)
    assert len(diag_indices)==65 and diag_map['shape']==[219,65]
    q_pairs=list(combinations_with_replacement(range(5),2))
    monomials=[tuple(int(k==i)+int(k==j) for k in range(5)) for i,j in q_pairs]
    equations=[poly(e['polynomial'],a) for e in diagonal['equations']]
    assert len(equations)==12
    for equation,entry in zip(equations,diagonal['equations']):
        dual=sparse(entry['dual'])
        assert [dot(dual,p) for p in diag_columns[:15]]==[equation.coeff_monomial(m) for m in monomials]
        assert all(dot(dual,p)==0 for p in diag_columns[15:])
    qmatrix=S.Matrix([[q.coeff_monomial(m) for m in monomials] for q in equations])
    assert qmatrix.rank()==12
    cubic_columns=[];cubic_polys=[]
    for q in equations:
        for variable in a:
            p=q*S.Poly(variable,a);cubic_polys.append(p)
            cubic_columns.append({m:Q(str(c)) for m,c in p.terms()})
    cubic_map=map_points(cubic_columns);assert cubic_map['shape']==[35,60]
    cubic_matrix=S.Matrix([[p.get(tuple(m),0) for p in cubic_columns] for m in cubic_map['row_monomials']])
    assert cubic_matrix.rank()==35
    macaulay=packet['cubic_macaulay'];assert macaulay['rows']==35 and macaulay['columns']==60 and macaulay['rank']==35
    assert len(macaulay['identities'])==5
    cube_terms=[]
    for i,identity in enumerate(macaulay['identities']):
        assert identity['diagonal_variable']==i and identity['power']==3
        lhs=sum((S.Rational(t['coefficient'])*cubic_polys[5*t['equation_index']+t['variable']] for t in identity['multipliers']),S.Poly(0,a))
        target=S.Poly(a[i]**3,a)
        assert (lhs-target).is_zero and (poly(identity['target'],a)-target).is_zero
        cube_terms.append(len(identity['multipliers']))
    injection=packet['injectivity'];injection_matrix=S.Matrix([[poly(b['E'],x).coeff_monomial(tuple(m)) for b in basis] for m in injection['rows']])
    assert injection_matrix.rank()==25
    assert injection_matrix.det()==S.Rational(injection['determinant'])!=0
    assert packet['projection']['raw_fields_per_denominator']==85
    assert len(packet['projection']['raw_fields'])==85 and len(packet['projection']['quotient_multiplier_powers'])==75
    assert packet['projection']['raw_projection_identities']==2125 and packet['projection']['quotient_projection_identities']==75
    counts={'exact_E1_and_upstairs_Piola_lifts':25,'parameter_quadratic_coefficients_reconstructed':325,
            'complete_Koszul_fields':85,'full_Koszul_projection_checks':2125,'surviving_correction_generator_types':10,
            'surviving_mixed_columns':250,'quotient_columns':75,'off_diagonal_square_identities':20,
            'diagonal_quadrics':12,'diagonal_cube_identities':5,'negative_controls_rejected':11,
            'full_map_exact_rank':414,'diagonal_exact_rank':52,'diagonal_quadrics_rank':12,'cubic_macaulay_exact_rank':35,
            'dual_coefficient_pairings':12280}
    for key,n in counts.items():assert review[key]==n,(key,review[key])
    assert review['failed_diagonal_square_queries_checked_over_Q']==5
    assert review['Euler_normalization_basis_identities']==1875
    assert primary['negative_controls_rejected']==9
    return {'schema':'cyclic-fano-linear-polars-plot-v1','instance':'cyclic-triple-fano','discussion_number':112,
            'sha256_policy':'File bytes with CRLF normalized to LF','source_sha256':bindings,'plot_source_sha256':sha(Path(__file__)),
            'full_map':full_map,'diagonal_map':diag_map,'cubic_map':cubic_map,
            'diagonal_quadric_matrix':[[str(c) for c in row] for row in qmatrix.tolist()],
            'diagonal_quadric_column_monomials':[list(m) for m in monomials],
            'off_diagonal_zero_indices':sorted(off_diagonal),'cube_identity_terms':cube_terms,
            'full_map_exact_rank':414,'diagonal_map_exact_rank':52,'diagonal_mixed_rank':40,
            'cubic_map_exact_rank':35,'modular_discovery':packet['modular_discovery'],'attempts':packet['attempts'],
            'scope':packet['limits']}


def save(fig,name):
    OUT.mkdir(parents=True,exist_ok=True);stem=OUT/name
    fig.savefig(stem.with_suffix('.png'),dpi=160,facecolor=PAPER)
    svg=stem.with_suffix('.svg');fig.savefig(svg,facecolor=PAPER,metadata={'Date':None})
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8',newline='\n')
    plt.close(fig)


def occupancy(ax,data,color):
    positions=np.array(data['nonzero_positions']);nr,nc=data['shape']
    ax.scatter(positions[:,1],positions[:,0],s=2.3,color=color,marker='s',linewidths=0,rasterized=False)
    ax.set(xlim=(-.5,nc-.5),ylim=(nr-.5,-.5))
    ax.tick_params(labelsize=11,colors=MUTED)
    for spine in ax.spines.values():spine.set_color('#CED6D2')
    ax.set_facecolor(PAPER)


def feature(data):
    fig=plt.figure(figsize=(14,8.5),facecolor=PAPER)
    fig.text(.055,.944,'An entire linear-polar family is excluded',fontsize=26,weight='bold')
    fig.text(.055,.894,r'cyclic-triple-fano · #112   |   $E_M=(Mx)\cdot\nabla\Delta$, with every constant $M\in\mathbb{C}^{5\times5}$ covered',fontsize=14,color=MUTED)
    ax1=fig.add_axes([.065,.402,.245,.365]);ax2=fig.add_axes([.382,.402,.255,.365]);ax3=fig.add_axes([.708,.402,.245,.365])
    ax1.set_title('25 parameters → 5',loc='left',fontsize=19,pad=16,color=TEAL)
    grid=np.ones((5,5));np.fill_diagonal(grid,0)
    ax1.imshow(grid,cmap=ListedColormap(['#DDD7EA','#E0ECE8']),vmin=0,vmax=1,aspect='auto')
    for i in range(5):
        for j in range(5):ax1.text(j,i,'$a_'+str(i)+'$' if i==j else '0',ha='center',va='center',fontsize=18,color=PURPLE if i==j else TEAL)
    ax1.set_xticks(range(5),[str(i) for i in range(5)],fontsize=12);ax1.set_yticks(range(5),[str(i) for i in range(5)],fontsize=12)
    ax1.set(xlabel='column j of M',ylabel='row i of M')
    ax1.set_xticks(np.arange(-.5,5,1),minor=True);ax1.set_yticks(np.arange(-.5,5,1),minor=True);ax1.grid(which='minor',color=PAPER,lw=2);ax1.tick_params(which='minor',length=0)
    qmatrix=np.array([[float(S.Rational(c)) for c in row] for row in data['diagonal_quadric_matrix']])
    ax2.imshow(np.sign(qmatrix),cmap=ListedColormap(['#B8D8D5',PAPER,'#E7B0A5']),vmin=-1,vmax=1,aspect='auto')
    ax2.set_title('12 exact quadrics',loc='left',fontsize=19,pad=16,color=PURPLE)
    ax2.set(xlabel='15 quadratic monomials in a',ylabel='equation index');ax2.tick_params(labelsize=11)
    ax2.set_xticks([0,5,10,14])
    occupancy(ax3,data['cubic_map'],TEAL)
    ax3.set_title('All 35 cubics spanned',loc='left',fontsize=18,pad=16,color=TEAL)
    ax3.set(xlabel='60 linear multiples of quadrics',ylabel='35 cubic monomials')
    fig.text(.065,.327,r'20 exact identities force $M_{ij}^2=0$ for $i\ne j$.',fontsize=14,color=TEAL)
    fig.text(.382,.327,'Map colors: negative / zero / positive.',fontsize=12,color=MUTED)
    fig.text(.708,.327,'Actual coefficient-map occupancy.',fontsize=12,color=MUTED)
    fig.text(.055,.250,r'Five exact identities:  $a_i^3=\sum_{r,j}c_{irj}\,a_jQ_r(a)$  $\Longrightarrow$  $a_0=\cdots=a_4=0$  $\Longrightarrow$  $M=0$.',fontsize=19,color=CORAL)
    fig.text(.055,.187,'The nonzero denominator family is therefore excluded. Other degree-six denominators remain open.',fontsize=15,weight='bold')
    fig.text(.055,.133,'Complete corrections retained: 85 Koszul fields and 75 quotient directions. No numerical threshold decides the result.',fontsize=12.5)
    fig.text(.055,.085,'History: modular screening suggested the constraints; rational identities prove them. Degree-two diagonal search did not isolate the squares.',fontsize=11.5,color=MUTED)
    fig.text(.055,.036,'Exact family obstruction · no certificate, Lean acceptance, or solved instance · reproducible detailed maps accompany this figure',fontsize=11,color=MUTED)
    save(fig,'cyclic-fano-linear-polars')


def detail(data):
    fig=plt.figure(figsize=(16,9.5),facecolor=PAPER)
    fig.text(.055,.94,'The actual coefficient maps behind the linear-polar exclusion',fontsize=24,weight='bold')
    fig.text(.055,.897,'cyclic-triple-fano · discussion #112   |   Nonzero coefficient positions; zero rows omitted only where stated',fontsize=13,color=MUTED)
    specs=[('full_map',(.07,.36,.37,.43),'Full parameter system','859 × 575 · exact rank 414'),
           ('diagonal_map',(.505,.36,.20,.43),'Rebuilt diagonal system','219 × 65 · exact rank 52'),
           ('cubic_map',(.765,.36,.19,.43),'Cubic multiplier map','35 × 60 · exact rank 35')]
    for key,rect,title,caption in specs:
        ax=fig.add_axes(rect);occupancy(ax,data[key],TEAL if key!='diagonal_map' else PURPLE)
        ax.set_title(title,loc='left',fontsize=15,pad=16)
        ax.set(xlabel='column index',ylabel='coefficient-row index')
        fig.text(rect[0],.285,caption,fontsize=13,color=INK)
    fig.text(.07,.242,'325 quadratic M terms + 250 M·c terms',fontsize=12)
    fig.text(.505,.242,'15 quadratic a terms + 50 a·c terms',fontsize=11)
    fig.text(.765,.242,'12 quadrics × 5 linear variables',fontsize=11)
    fig.text(.055,.192,'Full map: 142 of 1,001 ambient coefficient rows are identically zero. Rebuilt map: 782 are zero; both use the exact active rows.',fontsize=12,color=MUTED)
    fig.text(.055,.145,'Twenty row functionals isolate the off-diagonal squares. Twelve more eliminate correction variables; five cubic identities finish the proof.',fontsize=12.5)
    fig.text(.055,.100,'An initial helper rejected five valid Z·x quotient multipliers; the corrected monic recurrence retains and checks all 75 directions.',fontsize=12,color=MUTED)
    fig.text(.055,.054,'Sparsity and rank alone are not the exclusion proof. Exact identities are independently checked, with full numerator freedom in this family.',fontsize=12,color=CORAL)
    save(fig,'cyclic-fano-linear-polars-maps')


def main():
    if not __debug__:raise RuntimeError('Run without -O so exact checks remain active.')
    data=check_data()
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'text.color':INK,'axes.labelcolor':INK,
                         'svg.fonttype':'none','svg.hashsalt':'cyclic-fano-linear-polars-v1'})
    feature(data);detail(data)
    (OUT/'plot-data.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':'PASS','exact_square_duals':20,'exact_diagonal_quadrics':12,'exact_cube_identities':5,'figures':2}))


if __name__=='__main__':main()
