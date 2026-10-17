#!/usr/bin/env python3
"""Plot checked finite-field multiplication operators and primary blocks.

All matrices act on the same 120-dimensional quotient over F_101. Nonzero
residues are shown with equal weight; they are not complex spectral locations.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import sympy as S

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'results'/'cyclic-fano-spectrum'
OUT=ROOT/'results'/'cyclic-fano-spectrum-figures'
P=101
TEAL,CORAL,GOLD,PURPLE='#166A70','#CA584C','#D5AB3E','#7967AA'
INK,MUTED,PAPER,GRAY='#17323B','#53666D','#FAFAF5','#CBD3D0'


def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def relative(path):
    return path.relative_to(ROOT).as_posix()


def trim(poly):
    poly=[int(value)%P for value in poly]
    while len(poly)>1 and poly[-1]==0:poly.pop()
    return poly


def product(a,b):
    out=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i+j]=(out[i+j]+x*y)%P
    return trim(out)


def remainder(a,b):
    a=trim(a);b=trim(b)
    assert b!=[0]
    while a!=[0] and len(a)>=len(b):
        q=a[-1]*pow(b[-1],-1,P)%P;offset=len(a)-len(b)
        for k,v in enumerate(b):a[offset+k]=(a[offset+k]-q*v)%P
        a=trim(a)
    return a


def divide(a,b):
    a=trim(a);b=trim(b);q=[0]*max(1,len(a)-len(b)+1)
    while a!=[0] and len(a)>=len(b):
        k=len(a)-len(b);v=a[-1]*pow(b[-1],-1,P)%P;q[k]=v
        for j,w in enumerate(b):a[k+j]=(a[k+j]-v*w)%P
        a=trim(a)
    assert a==[0]
    return trim(q)


def multiplicity(poly,factor):
    count=0;poly=trim(poly)
    while len(poly)>=len(factor) and remainder(poly,factor)==[0]:
        poly=divide(poly,factor);count+=1
    return count


def rank_mod(matrix):
    a=np.array(matrix,dtype=np.int64,copy=True)%P
    nrows,ncols=a.shape;r=0
    for c in range(ncols):
        pivots=np.flatnonzero(a[r:,c])
        if not len(pivots):continue
        k=r+int(pivots[0]);a[[r,k]]=a[[k,r]]
        a[r]=a[r]*pow(int(a[r,c]),-1,P)%P
        other=np.arange(nrows)!=r
        a[other]=(a[other]-a[other,c,None]*a[r,None,:])%P
        r+=1
        if r==nrows:break
    return r


def determinant_mod(matrix):
    a=np.array(matrix,dtype=np.int64,copy=True)%P
    n=len(a);assert a.shape==(n,n);det=1
    for c in range(n):
        pivots=np.flatnonzero(a[c:,c])
        if not len(pivots):return 0
        k=c+int(pivots[0])
        if k!=c:a[[c,k]]=a[[k,c]];det=-det
        pivot=int(a[c,c]);det=det*pivot%P
        if c+1<n:
            factors=a[c+1:,c]*pow(pivot,-1,P)%P
            a[c+1:]=(a[c+1:]-factors[:,None]*a[c,None,:])%P
    return det%P


def polynomial_at_matrix(coefficients,operator):
    identity=np.eye(len(operator),dtype=np.int64)
    out=np.zeros_like(operator)
    for coefficient in reversed(coefficients):out=(out@operator+int(coefficient)*identity)%P
    return out


def form_label(weights):
    pieces=[]
    for k,name in zip(weights,('b','c','v')):
        if k:pieces.append(name if k==1 else str(k)+name)
    return '+'.join(pieces)


def factor_label(coefficients):
    assert len(coefficients)==2 and coefficients[1]==1
    a=int(coefficients[0]);a=a if a<=P//2 else a-P
    return 't' if a==0 else ('t+'+str(a) if a>0 else 't'+str(a))


def load_checked():
    path=SOURCE/'spectrum-101.json';receipt_path=SOURCE/'validation.json'
    independent_path=SOURCE/'independent-validation.json'
    packet,receipt,independent=load(path),load(receipt_path),load(independent_path)
    assert packet['schema']=='cyclic-fano-fiber-spectrum-v1'
    assert receipt['status']==independent['status']=='PASS'
    assert receipt['packet_sha256']==independent['spectrum_packet_lf_sha256']==sha(path)
    producer=ROOT/'experiments'/'cyclic_fano_spectrum.py'
    checker=ROOT/'experiments'/'check_cyclic_fano_spectrum.py'
    assert packet['producer_sha256']==receipt['producer_sha256']==sha(producer)
    assert independent['checker_lf_sha256']==sha(checker)
    fiber_path=ROOT/'results'/'cyclic-fano-fibers'/'fiber-equations.json'
    groebner_path=fiber_path.with_name('groebner-101.json')
    infinity_path=fiber_path.with_name('infinity-witness.json')
    assert packet['source_packet_sha256']==independent['fiber_packet_lf_sha256']==sha(fiber_path)
    assert packet['groebner_packet_sha256']==sha(groebner_path)
    assert packet['infinity_witness_sha256']==independent['infinity_packet_lf_sha256']==sha(infinity_path)
    assert (packet['prime'],packet['i_image'],packet['dimension'])==(101,10,120)
    assert all(packet['checks'].values())
    assert not packet['squarefree_characteristic_polynomial_found'] and packet['geometric_separator_found']
    basis=packet['basis_order'];assert len(basis)==len({tuple(v) for v in basis})==120
    assert basis[packet['unit_basis_index']]==[0,0,0]
    matrices={name:np.array(packet['multiplication_matrices'][name],dtype=np.int64) for name in ('b','c','v')}
    for value in matrices.values():assert value.shape==(120,120) and np.all((value>=0)&(value<P))
    for x in matrices.values():
        for y in matrices.values():assert not np.any((x@y-y@x)%P)
    identity=np.eye(120,dtype=np.int64);unit=identity[:,packet['unit_basis_index']]
    attempts=[]
    for attempt in packet['linear_form_attempts']:
        char=attempt['characteristic_polynomial_ascending'];minimum=attempt['minimal_polynomial_ascending']
        assert len(char)==121 and len(minimum)==attempt['minimal_degree']+1
        factored=[1]
        for factor in attempt['factors']:
            assert len(factor['coefficients_ascending'])==factor['degree']+1
            for _ in range(factor['multiplicity']):factored=product(factored,factor['coefficients_ascending'])
        assert factored==char and remainder(char,minimum)==[0]
        repeated=[f for f in attempt['factors'] if f['multiplicity']>1]
        assert len(repeated)==1 and repeated[0]['degree']==1
        operator=sum(k*matrices[name] for k,name in zip(attempt['linear_form_weights'],('b','c','v')))%P
        # Cyclic powers of the algebra's unit certify the reported minimal degree.
        krylov=[];vector=unit.copy()
        for _ in range(120):krylov.append(vector.copy());vector=operator@vector%P
        assert rank_mod(np.column_stack(krylov))==attempt['minimal_degree']
        assert not np.any(polynomial_at_matrix(minimum,operator))
        assert not attempt['squarefree_characteristic_polynomial']
        factor=repeated[0]
        attempts.append({'weights':attempt['linear_form_weights'],'minimal_degree':attempt['minimal_degree'],
            'repeated_factor_label':factor_label(factor['coefficients_ascending']),
            'repeated_factor_coefficients':factor['coefficients_ascending'],
            'characteristic_multiplicity':factor['multiplicity'],
            'minimal_multiplicity':multiplicity(minimum,factor['coefficients_ascending']),
            'factor_degrees_and_multiplicities':[[f['degree'],f['multiplicity']] for f in attempt['factors']]})
    assert len(attempts)==7
    selected=packet['selected_operator'];assert selected['linear_form_weights']==[1,2,3]
    record=packet['linear_form_attempts'][selected['attempt_index']]
    assert record['characteristic_polynomial_ascending']==record['minimal_polynomial_ascending']
    operator=(matrices['b']+2*matrices['c']+3*matrices['v'])%P
    krylov=[];vector=unit.copy()
    for _ in range(120):krylov.append(vector.copy());vector=operator@vector%P
    assert determinant_mod(np.column_stack(krylov))==selected['krylov_determinant']==96
    for name,coefficients in selected['coordinate_polynomials_in_L_ascending'].items():
        assert np.array_equal(polynomial_at_matrix(coefficients,operator),matrices[name])
    projectors=[];ranks=[]
    for item in selected['projectors']:
        projector=polynomial_at_matrix(item['projector_coefficients_ascending'],operator)
        assert np.array_equal(projector@projector%P,projector)
        assert rank_mod(projector)==item['projector_rank']==item['factor_degree']*item['multiplicity']
        projectors.append(projector);ranks.append(item['projector_rank'])
    assert ranks==[1,3,16,23,35,42]
    assert np.array_equal(sum(projectors)%P,identity)
    for i,first in enumerate(projectors):
        for j,second in enumerate(projectors):
            if i!=j:assert not np.any(first@second%P)
    block=selected['nonreduced_primary_block']
    projector=np.array(block['projector_matrix'],dtype=np.int64)
    nilpotent=np.array(block['nilpotent_matrix'],dtype=np.int64)
    assert np.array_equal(projector,projectors[1])
    assert block['eigenvalue']==91 and np.array_equal((operator+10*identity)@projector%P,nilpotent)
    powers=[nilpotent,nilpotent@nilpotent%P]
    powers.append(powers[-1]@nilpotent%P)
    nranks=[rank_mod(m) for m in powers]
    assert [3]+nranks==block['ranks_E_N_N2_N3']==[3,2,1,0]
    chain=np.array(block['chain_basis_columns_N2E1_NE1_E1'],dtype=np.int64)
    restricted=np.array(block['restricted_nilpotent_matrix'],dtype=np.int64)
    assert rank_mod(chain)==3 and np.array_equal(nilpotent@chain%P,chain@restricted%P)
    assert np.array_equal(restricted,np.array([[0,1,0],[0,0,1],[0,0,0]],dtype=np.int64))
    traces=[];power=identity.copy()
    for _ in range(239):traces.append(int(np.trace(power))%P);power=power@operator%P
    assert traces==selected['power_traces']
    trace_form=np.array([[traces[i+j] for j in range(120)] for i in range(120)],dtype=np.int64)
    assert rank_mod(trace_form)==selected['trace_form_rank']==118
    minor=trace_form[np.ix_(selected['trace_form_minor_rows'],selected['trace_form_minor_columns'])]
    assert determinant_mod(minor)==selected['trace_form_minor_determinant']==89

    # Recheck the characteristic-zero jet separately from the modular spectrum.
    fiber=load(fiber_path);jet=packet['characteristic_zero_swapped_point']
    b,c,v=S.symbols('b c v');variables=(b,c,v)
    pair=lambda x:S.Rational(x[0])+S.I*S.Rational(x[1])
    equations=S.Matrix([S.expand(sum(pair(t['coefficient'])*S.prod(z**k for z,k in zip(variables,t['powers']))
                                      for t in terms)) for terms in fiber['remaining_equations']])
    point=dict(zip(variables,map(pair,jet['point'])))
    assert equations.subs(point)==S.zeros(3,1)
    jacobian=equations.jacobian(variables).subs(point)
    assert jacobian.rank()==jet['jacobian_rank']==2
    assert jacobian[jet['selected_rows'],jet['selected_columns']].det()==pair(jet['nonzero_minor'])==-180
    cjet=sum(pair(x)*b**j for j,x in enumerate(jet['c_jet_coefficients_ascending']))
    vjet=sum(pair(x)*b**j for j,x in enumerate(jet['v_jet_coefficients_ascending']))
    coefficients=[]
    for equation in equations:
        result=S.Poly(S.expand(equation.subs({c:cjet,v:vjet})),b)
        coefficients.append([result.coeff_monomial(b**j) for j in range(4)])
    assert coefficients[:2]==[[0]*4,[0]*4]
    assert coefficients[2][:3]==[0]*3
    assert coefficients[2][3]==pair(jet['remaining_scalar_cubic_coefficient'])==-1-48*S.I/175
    assert jet['local_length']==independent['exact_local_Qi_audit']['local_length']==3
    conclusion=independent['characteristic_zero_conclusion']
    assert (conclusion['geometric_points'],conclusion['triple_points'],conclusion['other_simple_points'])==(118,1,117)
    assert receipt['characteristic_zero_geometric_points']==118
    assert independent['negative_controls_rejected']>=6
    result={'schema':'cyclic-fano-spectrum-plot-v1','instance':'cyclic-triple-fano','discussion_number':112,
        'sha256_policy':'UTF-8 bytes with CRLF normalized to LF','packet_path':relative(path),'packet_sha256':sha(path),
        'validation_sha256':sha(receipt_path),'independent_validation_sha256':sha(independent_path),
        'source_sha256':{relative(p):sha(p) for p in (producer,checker,fiber_path,groebner_path,infinity_path)},
        'plot_source_sha256':sha(Path(__file__)),'prime':101,'i_image':10,'dimension':120,
        'matrix_convention':packet['matrix_convention'],'basis_order':basis,
        'basis_group_boundaries':[i for i in range(1,120) if basis[i][0]!=basis[i-1][0]],
        'matrix_nonzero_counts':{name:int(np.count_nonzero(m)) for name,m in matrices.items()},
        'attempts':attempts,'selected_form':[1,2,3],'projector_ranks':ranks,'nilpotent_ranks':nranks,
        'restricted_nilpotent_matrix':block['restricted_nilpotent_matrix'],
        'trace_form_rank':118,'trace_minor_determinant_mod101':89,'exact_Q_i_local_jet':jet,
        'characteristic_zero_conclusion':conclusion,
        'initial_implementation_failure_sha256':sha(SOURCE/'attempt-101-initial-type-coercion.json'),
        'scope':'Finite-field multiplication maps and exact primary blocks; the separate Q(i) jet and trace-minor lifting argument give the characteristic-zero point count. No complex spectral locations, positive Hermitian trace form, seed component degree, or certificate is claimed.'}
    return result,matrices


def style(ax):
    ax.set_facecolor(PAPER)
    for side in ('top','right'):ax.spines[side].set_visible(False)
    for side in ('left','bottom'):ax.spines[side].set_color(GRAY)
    ax.tick_params(colors=MUTED,labelsize=10)


def save(fig,name):
    OUT.mkdir(parents=True,exist_ok=True)
    fig.text(.945,.021,'cyclic-triple-fano · discussion #112',ha='right',fontsize=10,color=TEAL)
    fig.savefig(OUT/(name+'.png'),dpi=160,facecolor=PAPER)
    svg=OUT/(name+'.svg');fig.savefig(svg,facecolor=PAPER,metadata={'Date':None})
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',
                   encoding='utf-8',newline='\n')
    plt.close(fig)


def maps_figure(data,matrices):
    fig=plt.figure(figsize=(16,12),facecolor=PAPER)
    fig.text(.055,.95,'A finite quotient seen through multiplication operators',fontsize=24,weight='bold')
    fig.text(.055,.914,r'cyclic-triple-fano · #112  |  $A_{101}$ has dimension 120  |  Reduction $i\mapsto10$, with $10^2=-1$ mod 101',fontsize=12,color=MUTED)
    fig.text(.055,.864,'Actual coefficient support in the stored monomial basis',fontsize=17,color=TEAL)
    for j,name in enumerate(('b','c','v')):
        ax=fig.add_axes([.077+.314*j,.505,.24,.305]);style(ax)
        operator=matrices[name]
        rows,cols=np.nonzero(operator)
        ax.scatter(cols,rows,marker='s',s=2.9,color=TEAL,lw=0,rasterized=False)
        for boundary in data['basis_group_boundaries']:
            ax.axhline(boundary-.5,color=GRAY,lw=.5,zorder=0)
            ax.axvline(boundary-.5,color=GRAY,lw=.5,zorder=0)
        ax.set_xlim(-.5,119.5);ax.set_ylim(119.5,-.5);ax.set_aspect('equal')
        ax.set_xticks([0,30,60,90,119]);ax.set_yticks([0,30,60,90,119])
        ax.set_xlabel('input monomial index');ax.set_ylabel('output monomial index')
        ax.set_title(r'$M_'+name+r'$'+f'   ·   {len(rows):,} nonzero entries',fontsize=13,pad=14)
    fig.text(.055,.46,'Each mark is a nonzero residue. All 120 rows and columns remain; color does not encode an ordered magnitude.',fontsize=11,color=MUTED)
    fig.text(.055,.418,'Seven linear-form attempts',fontsize=17,weight='bold')
    ax=fig.add_axes([.05,.132,.9,.245]);ax.axis('off')
    table_rows=[]
    for item in data['attempts']:
        table_rows.append([form_label(item['weights']),str(item['minimal_degree']),
                           '('+item['repeated_factor_label']+')^'+str(item['characteristic_multiplicity']),
                           str(item['minimal_multiplicity']),'No'])
    table=ax.table(cellText=table_rows,
        colLabels=['linear form ℓ','degree of μℓ','repeated factor in χℓ','its power in μℓ','χℓ squarefree?'],
        colWidths=[.23,.17,.25,.18,.17],bbox=[0,0,1,1],cellLoc='center')
    table.auto_set_font_size(False);table.set_fontsize(11)
    for (r,c),cell in table.get_celld().items():
        cell.set_edgecolor('white');cell.set_linewidth(1.5)
        cell.set_text_props(color=INK)
        cell.set_facecolor('#E5ECE8' if r%2 else PAPER)
        if r==0:cell.set_facecolor(TEAL);cell.set_text_props(color='white',weight='bold')
        if r>0 and data['attempts'][r-1]['weights']==[1,2,3]:cell.set_facecolor('#F2DEDA')
    fig.text(.055,.081,'Every characteristic polynomial has degree 120. A repeated characteristic factor alone does not diagnose nilpotents.',fontsize=12,color=MUTED)
    fig.text(.055,.048,'No squarefree characteristic polynomial was found in these seven attempts. The selected operator is examined separately.',fontsize=12,color=MUTED)
    save(fig,'cyclic-fano-multiplication-maps')


def blocks_figure(data):
    fig=plt.figure(figsize=(16,12),facecolor=PAPER)
    fig.text(.055,.95,'The selected operator detects a genuine nilpotent block',fontsize=24,weight='bold')
    fig.text(.055,.913,'Selected ℓ = b + 2c + 3v over F₁₀₁, followed by a separate exact characteristic-zero confirmation',fontsize=12,color=MUTED)
    fig.text(.055,.853,r'$\mu_\ell(t)=\chi_\ell(t)=t(t+10)^3f_{16}(t)f_{23}(t)f_{35}(t)f_{42}(t)$',fontsize=23,color=TEAL)
    fig.text(.055,.812,r'Each $f_d$ is the stored irreducible factor of degree $d$; these are not complex eigenvalue locations.',fontsize=12,color=MUTED)
    ax=fig.add_axes([.085,.402,.37,.33]);style(ax)
    labels=[r'$t$',r'$(t+10)^3$',r'$f_{16}$',r'$f_{23}$',r'$f_{35}$',r'$f_{42}$']
    ranks=data['projector_ranks']
    ax.barh(np.arange(6),ranks,color=[TEAL,CORAL,TEAL,TEAL,TEAL,TEAL],height=.58)
    for j,value in enumerate(ranks):ax.text(value+.65,j,str(value),va='center',fontsize=13,color=INK)
    ax.set_yticks(range(6),labels);ax.invert_yaxis();ax.set_xlim(0,47)
    ax.set_xlabel('rank of the exact CRT projector');ax.grid(axis='x',color=GRAY,alpha=.5)
    ax.set_axisbelow(True)
    ax.set_title('Six algebraic primary blocks; total dimension 120',fontsize=14,loc='left',pad=20)
    ax=fig.add_axes([.58,.402,.35,.33]);style(ax)
    powers=np.array([1,2,3])
    ax.bar(powers-.17,data['nilpotent_ranks'],width=.31,color=CORAL,label='rank')
    ax.bar(powers+.17,[3-value for value in data['nilpotent_ranks']],width=.31,color=TEAL,label='kernel dimension in the 3D block')
    ax.set_xticks(powers,[r'$N$',r'$N^2$',r'$N^3$']);ax.set_yticks([0,1,2,3]);ax.set_ylim(0,3.6)
    ax.set_ylabel('dimension over F₁₀₁');ax.grid(axis='y',color=GRAY,alpha=.5);ax.set_axisbelow(True)
    ax.set_title(r'$N=(M_\ell+10I)P$, with $\operatorname{rank}P=3$',fontsize=16,loc='left',pad=20)
    ax.legend(loc='upper left',bbox_to_anchor=(.01,.99),frameon=False,fontsize=10)
    fig.text(.055,.303,r'$N^3=0\quad\mathrm{but}\quad N^2\ne0$',fontsize=25,color=CORAL)
    fig.text(.42,.308,'The minimal polynomial retains the cubic factor.\nThe corresponding block is F₁₀₁[ε]/(ε³).',fontsize=13,color=TEAL)
    fig.text(.055,.244,r'Over $\mathbf{Q}(i)$, the swapped curve is $[s:t]\mapsto[\,0:s:0:it:t:is\,]$.',fontsize=17)
    fig.text(.055,.194,r'Its remaining local equation is $(-1-48i/175)b^3+O(b^4)$ after solving the first two equations.',fontsize=16)
    fig.text(.055,.151,'The nonzero cubic coefficient proves local length 3 independently of reduction mod 101.',fontsize=12,color=TEAL)
    fig.text(.055,.108,'Trace rank 118 + the finite flat model + this exact jet: 118 characteristic-zero geometric points, one triple and 117 simple.',fontsize=12)
    fig.text(.055,.067,'This counts the complete selected incidence fiber; it does not give the seed component degree or a certificate.',fontsize=12,color=MUTED)
    save(fig,'cyclic-fano-primary-blocks')


def main():
    if not __debug__:raise RuntimeError('Run without -O so exact checks remain active.')
    data,matrices=load_checked()
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'text.color':INK,
        'axes.labelcolor':INK,'svg.fonttype':'none','svg.hashsalt':'cyclic-fano-spectrum-v1'})
    maps_figure(data,matrices);blocks_figure(data)
    (OUT/'plot-data.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':'PASS','figures':2,'dimension':120,'prime':101,
        'projector_ranks':data['projector_ranks'],'nilpotent_ranks':data['nilpotent_ranks']}))


if __name__=='__main__':main()
