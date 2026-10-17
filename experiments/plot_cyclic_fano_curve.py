#!/usr/bin/env python3
"""Render the checked cyclic quotient curve and its finite coefficient operators.

Run cyclic_fano_curve.py and check_cyclic_fano_curve.py first. Matrix entries,
Gram products, spectral projectors, and right inverses are checked exactly;
only the explicitly labeled sensitivity and resolvent curves are sampled.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle
import numpy as np
import sympy as S

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'results' / 'cyclic-fano-curve'
OUT = ROOT / 'results' / 'cyclic-fano-curve-figures'
TEAL, CORAL, GOLD, PURPLE = '#166A70', '#CA584C', '#D5AB3E', '#7967AA'
INK, MUTED, PAPER, GRAY = '#17323B', '#53666D', '#FAFAF5', '#CBD3D0'


def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def relative(path):
    return path.relative_to(ROOT).as_posix()


def decode(rows):
    return S.Matrix([[S.Rational(a) + S.I*S.Rational(b) for a, b in row] for row in rows])


def encode(matrix):
    return [[[str(S.re(v)), str(S.im(v))] for v in row] for row in matrix.tolist()]


def plain_matrix(rows):
    return S.Matrix([[S.sympify(v) for v in row] for row in rows])


def load_checked():
    packet_path = SOURCE / 'cyclic-free-curve.json'
    receipt_path = SOURCE / 'independent-validation.json'
    primary_receipt_path = SOURCE / 'validation.json'
    packet, review = load(packet_path), load(receipt_path)
    primary_receipt = load(primary_receipt_path)
    assert packet['schema'] == 'cyclic-fano-free-curve-v1'
    assert packet['instance'] == 'cyclic-triple-fano'
    assert review['status'] == 'PASS'
    assert primary_receipt['status'] == 'PASS'
    assert primary_receipt['packet_sha256'] == review['primary_packet_lf_sha256'] == sha(packet_path)
    assert primary_receipt['producer_sha256'] == sha(ROOT/'experiments'/'cyclic_fano_curve.py')
    assert not primary_receipt['certificate_found']
    assert review['source_commit'] == packet['upstream_commit']
    assert review['source_lf_sha256'] == packet['raw_instance_sha256']
    assert sha(SOURCE/'target.json') == packet['frozen_target_sha256']
    assert sha(SOURCE/'source'/'instance.rec') == packet['raw_instance_sha256']
    assert packet['target']['q'] == 1 and packet['fixed_coupling'] == '5/7'
    assert packet['curve'] == review['curve'] == ['0', 's', '0', 'I*s', 't', 'I*t']
    assert packet['weights'] == review['quotient_weights'] == [1,1,3,1,1,1]
    assert all(packet['checks'].values())
    checker = ROOT/'experiments'/'check_cyclic_fano_curve.py'
    assert review['checker_lf_sha256'] == sha(checker)

    # The independent reconstruction orders the same eight columns differently.
    labels = packet['twisted_map']['column_labels']
    expected_labels = [('X0','1'),('X1','1'),('Z','s**2'),('Z','s*t'),
                       ('Z','t**2'),('Y0','1'),('Y1','1'),('Y2','1')]
    assert [(item['coordinate'],item['section']) for item in labels] == expected_labels
    matrix = decode(packet['twisted_map']['matrix'])
    independent = plain_matrix(review['twisted_derivative']['matrix'])
    assert independent == matrix[:,[0,1,5,6,7,2,3,4]]
    assert matrix.shape == (6,8) and matrix.rank() == packet['twisted_map']['rank'] == 6
    assert matrix[:,packet['twisted_map']['selected_columns']].det() == S.Rational(22500,2401)
    gram = matrix*matrix.conjugate().T
    low, high = S.Rational(25,49), S.Integer(72)
    assert gram == decode(packet['spectral']['gram_matrix']) == S.diag(high,low,low,low,low,high)
    assert packet['spectral']['eigenvalues'] == {'72':2,'25/49':4}
    slow = (high*S.eye(6)-gram)/(high-low)
    fast = S.eye(6)-slow
    assert slow*slow == slow and fast*fast == fast and slow*fast == S.zeros(6)
    assert slow.rank() == 4 and fast.rank() == 2
    assert slow == decode(packet['spectral']['small_eigenspace_projector'])
    assert fast == decode(packet['spectral']['large_eigenspace_projector'])
    inverse = slow/low + fast/high
    assert gram*inverse == S.eye(6) and inverse == decode(packet['spectral']['gram_inverse'])
    right_inverse = matrix.conjugate().T*inverse
    assert right_inverse == decode(packet['spectral']['right_inverse'])
    assert matrix*right_inverse == S.eye(6)
    assert right_inverse.conjugate().T*right_inverse == decode(packet['spectral']['right_inverse_gram']) == inverse
    assert decode(packet['spectral']['lower_bound_remainder']) == gram-low*S.eye(6)
    assert packet['spectral']['matrix_full_row_rank_perturbation_radius'] == '5/7'
    assert packet['spectral']['right_inverse_operator_norm'] == '7/5'
    parameter_matrix = plain_matrix(packet['twisted_map']['parameter_matrix'])
    c = next(symbol for symbol in parameter_matrix.free_symbols if str(symbol) == 'c')
    parameter_gram = S.simplify(parameter_matrix*parameter_matrix.conjugate().T).subs(S.conjugate(c),c)
    assert parameter_gram == S.diag(72,c*c,c*c,c*c,c*c,72)
    assert parameter_matrix.subs(c,S.Rational(5,7)) == matrix
    assert parameter_matrix.subs(c,0).rank() == 2
    # A symbolic right inverse proves surjectivity for every real c != 0.
    assert S.simplify(parameter_matrix*(parameter_matrix.conjugate().T).subs(S.conjugate(c),c)
                      *S.diag(S.Rational(1,72),c**-2,c**-2,c**-2,c**-2,S.Rational(1,72))) == S.eye(6)
    assert review['three_parameter_family']['evaluation_rank'] == 4
    assert review['negative_controls_rejected'] >= 3
    family = review['three_parameter_family']
    assert plain_matrix(family['unknown_jacobian']).det() == S.sympify(family['unknown_jacobian_determinant'])
    evaluation = plain_matrix(family['evaluation_jacobian_at_s_t_1'])
    assert evaluation[family['evaluation_minor_rows'],:].det() == 1
    result = {
        'schema':'cyclic-fano-curve-plot-v1',
        'instance':'cyclic-triple-fano','discussion_number':112,
        'sha256_policy':'UTF-8 bytes with CRLF normalized to LF',
        'packet_path':relative(packet_path),'packet_sha256':sha(packet_path),
        'primary_validation_sha256':sha(primary_receipt_path),
        'independent_validation_sha256':sha(receipt_path),
        'plot_source_sha256':sha(Path(__file__)),
        'experiment_source_sha256':{relative(p):sha(p) for p in
            [ROOT/'experiments'/'cyclic_fano_curve.py',checker]},
        'upstream_commit':packet['upstream_commit'],
        'frozen_target_sha256':packet['frozen_target_sha256'],
        'raw_instance_sha256':packet['raw_instance_sha256'],
        'source_sha256':packet['source_sha256'],
        'curve':packet['curve'],'weights':packet['weights'],
        'matrix':encode(matrix),'row_monomials':packet['twisted_map']['row_monomials'],
        'column_labels':labels,'rank':6,'kernel_dimension':2,
        'minor_columns':packet['twisted_map']['selected_columns'],'minor_determinant':'22500/2401',
        'gram':encode(gram),'slow_projector':encode(slow),'fast_projector':encode(fast),
        'gram_inverse':encode(inverse),'right_inverse':encode(right_inverse),
        'spectrum':{'25/49':4,'72':2},'smallest_singular_value':'5/7',
        'right_inverse_operator_norm':'7/5','matrix_condition_number':'42*sqrt(2)/5',
        'matrix_full_row_rank_perturbation_radius':'5/7',
        'perturbation_scope':packet['spectral']['perturbation_argument'],
        'projector_ranks':[4,2],'exact_reconstruction_verified':True,
        'inner_product':packet['spectral']['inner_product'],
        'separate_target_family':{'parameter_gram_diagonal':['72','c**2','c**2','c**2','c**2','72'],
            'rank_at_zero':2,'rank_for_nonzero_real_c':6,'fixed_coupling':'5/7',
            'limitation':'Varying c changes F. This is sensitivity of the construction across a separate target family, not a search within the fixed puzzle.'},
        'resolvent':{'formula':'||(zI-H)^(-1)||_2 = 1/min(|z-25/49|,|z-72|)',
                     'domain':'Complex z outside {25/49,72}; coefficient Euclidean operator norm.',
                     'at_zero':'49/25','sampling':'Curves are floating-point renderings of this exact formula.'},
        'covering_family_seed':{'unknown_jacobian_determinant':family['unknown_jacobian_determinant'],
             'marked_evaluation_rank':4,'marked_evaluation_minor':'1'},
        'scope':'A checked free rational curve on the weighted cyclic quotient and a concrete covering-family seed. No support equation, certificate, Lean proof, or accepted solve. Freeness of its lift to the original sextic is not asserted.'}
    return result


def style(ax):
    ax.set_facecolor(PAPER)
    for side in ('top','right'):
        ax.spines[side].set_visible(False)
    for side in ('left','bottom'):
        ax.spines[side].set_color(GRAY)
    ax.tick_params(colors=MUTED,labelsize=10)


def matrix_plot(ax,matrix,row_labels=None,col_labels=None,fontsize=12):
    """Print every coefficient; color distinguishes real and imaginary entries."""
    nr,nc = matrix.shape
    for r in range(nr):
        for c in range(nc):
            value = matrix[r,c]
            color = PAPER if value == 0 else (TEAL if S.im(value)==0 else PURPLE)
            ax.add_patch(Rectangle((c-.5,r-.5),1,1,facecolor=color,edgecolor='white',lw=1.5))
            label = r'$'+S.latex(value)+r'$' if value else '·'
            ax.text(c,r,label,ha='center',va='center',fontsize=fontsize,
                    color='white' if value else '#ABB5B4')
    ax.set_xlim(-.5,nc-.5);ax.set_ylim(nr-.5,-.5)
    ax.set_xticks(range(nc),col_labels if col_labels is not None else [])
    ax.set_yticks(range(nr),row_labels if row_labels is not None else [])
    ax.tick_params(axis='both',length=0,pad=10,labelsize=11,colors=INK)
    for spine in ax.spines.values():spine.set_visible(False)


def save(fig,name):
    OUT.mkdir(parents=True,exist_ok=True)
    fig.text(.94,.016,'cyclic-triple-fano · discussion #112',
             ha='right',fontsize=10,color=TEAL)
    fig.savefig(OUT/(name+'.png'),dpi=160,facecolor=PAPER)
    svg=OUT/(name+'.svg')
    fig.savefig(svg,facecolor=PAPER,metadata={'Date':None})
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',
                   encoding='utf-8',newline='\n')
    plt.close(fig)


def map_figure(data):
    fig=plt.figure(figsize=(15,11),facecolor=PAPER)
    fig.text(.06,.95,'A complex curve with a surjective deformation map',fontsize=23,weight='bold')
    fig.text(.06,.916,'cyclic-triple-fano  |  Fixed target q = 1, c = 5/7  |  Exact coefficients in Q(i)',fontsize=12,color=MUTED)
    fig.text(.06,.858,r'$\phi:\mathbf{P}^{1}_{\mathbf{C}}\longrightarrow W\subset\mathbf{P}(1,1,3,1,1,1)$',fontsize=21,color=TEAL)
    fig.text(.06,.807,r'$[s:t]\longmapsto[\,0:s:0:is:t:it\,]$',fontsize=25)
    fig.text(.59,.861,'Weighted coordinates',fontsize=12,color=MUTED)
    fig.text(.59,.818,r'$(X_0,X_1,Z,Y_0,Y_1,Y_2),\quad Z=X_2^3$',fontsize=19)
    fig.text(.59,.777,r'$G\circ\phi=0,\qquad i^2=-1$',fontsize=20,color=TEAL)
    fig.text(.06,.745,'A complex projective curve given by coordinates; this diagram is not a real 3D embedding.',fontsize=11,color=MUTED)
    fig.text(.06,.691,r'$M:H^0(\mathcal{O}^{5}\oplus\mathcal{O}(2))\longrightarrow H^0(\mathcal{O}(5))$',fontsize=21,color=TEAL)
    fig.text(.71,.691,'8 input coefficients → 6 output coefficients',fontsize=12)
    ax=fig.add_axes([.17,.275,.75,.36])
    cols=[r'$\delta X_0$',r'$\delta X_1$',r'$s^2\delta Z$',r'$st\delta Z$',r'$t^2\delta Z$',
          r'$\delta Y_0$',r'$\delta Y_1$',r'$\delta Y_2$']
    rows=[r'$s^5$',r'$s^4t$',r'$s^3t^2$',r'$s^2t^3$',r'$st^4$',r'$t^5$']
    matrix_plot(ax,decode(data['matrix']),rows,cols,16)
    ax.set_ylabel('output monomial',fontsize=11,labelpad=22,color=MUTED)
    fig.legend(handles=[Patch(color=TEAL,label='real coefficient'),Patch(color=PURPLE,label='imaginary coefficient')],
               loc='center',bbox_to_anchor=(.58,.211),ncol=2,frameon=False,fontsize=11)
    fig.text(.06,.17,r'Nonzero $6\times6$ minor: $22500/2401$     •     rank $M=6$     •     kernel dimension $=2$',fontsize=16,color=TEAL)
    fig.text(.06,.123,'The weighted tangent sequence gives a free rational curve on W; marked evaluation has rank 4.',fontsize=12)
    fig.text(.06,.087,'This supplies a concrete covering-family seed. A support equation and the required certificate remain unconstructed.',fontsize=12,color=MUTED)
    fig.text(.06,.051,'Freeness is claimed on the cyclic quotient, not for the curve lifted to the original sextic.',fontsize=11,color=MUTED)
    save(fig,'cyclic-fano-map')


def spectral_figure(data):
    fig=plt.figure(figsize=(16,12),facecolor=PAPER)
    fig.text(.055,.952,'Spectral projectors turn the map into an exact right inverse',fontsize=22,weight='bold')
    fig.text(.055,.916,'Finite-dimensional functional calculus  |  Chosen coefficient bases are orthonormal',fontsize=12,color=MUTED)
    fig.text(.055,.865,r'$H=MM^*=\operatorname{diag}(72,25/49,25/49,25/49,25/49,72)$',fontsize=21,color=TEAL)
    fig.text(.055,.823,r'$P_{\rm slow}=\dfrac{72I-H}{72-25/49},\qquad P_{\rm fast}=I-P_{\rm slow}$',fontsize=22)
    rows=[r'$s^5$',r'$s^4t$',r'$s^3t^2$',r'$s^2t^3$',r'$st^4$',r'$t^5$']
    ax=fig.add_axes([.065,.49,.245,.255]);matrix_plot(ax,decode(data['slow_projector']),row_labels=rows,fontsize=12)
    ax.tick_params(labelsize=9)
    ax.set_title('Four small-eigenvalue directions',fontsize=13,loc='left',pad=17)
    ax.set_xlabel(r'$P_{\rm slow}^{2}=P_{\rm slow},\quad\operatorname{rank}=4$',fontsize=15,labelpad=16)
    ax=fig.add_axes([.355,.49,.245,.255]);matrix_plot(ax,decode(data['fast_projector']),row_labels=rows,fontsize=12)
    ax.tick_params(labelsize=9)
    ax.set_title('Two large-eigenvalue directions',fontsize=13,loc='left',pad=17)
    ax.set_xlabel(r'$P_{\rm fast}^{2}=P_{\rm fast},\quad\operatorname{rank}=2$',fontsize=15,labelpad=16)
    ax=fig.add_axes([.685,.49,.26,.255]);style(ax)
    vals=[25/49]*4+[72]*2
    ax.scatter(vals,[1,2,3,4,5,6],s=65,c=[TEAL]*4+[GOLD]*2,zorder=3)
    ax.set_xscale('log');ax.set_xlim(.2,150);ax.set_ylim(.5,6.5)
    ax.set_xticks([25/49,1,10,72],[r'$25/49$','1','10','72'])
    ax.set_yticks(range(1,7));ax.grid(axis='x',color=GRAY,alpha=.6)
    ax.set_title('Six positive eigenvalues of H',loc='left',fontsize=13,pad=17)
    ax.set_xlabel('eigenvalue (log scale)',labelpad=14)
    ax.set_ylabel('eigenvalue index')
    fig.text(.055,.389,r'$H^{-1}=\dfrac{P_{\rm slow}}{25/49}+\dfrac{P_{\rm fast}}{72},\qquad R=M^*H^{-1},\qquad MR=I_6$',fontsize=23,color=TEAL)
    inputs=[r'$\delta X_0$',r'$\delta X_1$',r'$s^2\delta Z$',r'$st\delta Z$',r'$t^2\delta Z$',
            r'$\delta Y_0$',r'$\delta Y_1$',r'$\delta Y_2$']
    ax=fig.add_axes([.085,.115,.29,.215]);matrix_plot(ax,decode(data['right_inverse']),inputs,rows,fontsize=12)
    ax.tick_params(labelsize=8,pad=5)
    ax.set_title(r'Actual $8\times6$ right inverse $R$',fontsize=13,loc='left',pad=14)
    fig.text(.435,.295,r'$\sigma_{\min}(M)=5/7,\qquad\|R\|_2=7/5$',fontsize=23)
    fig.text(.435,.242,r'$\|E\|_2<5/7\quad\Longrightarrow\quad\operatorname{rank}(M+E)=6$',fontsize=20)
    fig.text(.435,.194,'A sufficient matrix bound, not a geometric-neighborhood guarantee.',fontsize=11,color=MUTED)
    fig.text(.435,.158,'The operator identities are checked in exact Q(i) arithmetic.',fontsize=12,color=TEAL)
    fig.text(.435,.122,'These coefficient norms are not a canonical metric on W.',fontsize=12,color=MUTED)
    fig.text(.435,.086,'The 8×8 matrix M* M would have two zero eigenvalues.',fontsize=12,color=MUTED)
    fig.text(.055,.045,'Bourbaki’s spectral viewpoint has a concrete role here: separate spectral blocks, then invert their nonzero eigenvalues.',fontsize=12,color=MUTED)
    save(fig,'cyclic-fano-spectrum')


def sensitivity_figure(data):
    fig=plt.figure(figsize=(16,11),facecolor=PAPER)
    fig.text(.06,.949,'Sensitivity and resolvent: two different parameters',fontsize=24,weight='bold')
    fig.text(.06,.912,'c changes the hypersurface in an auxiliary family; z only probes the fixed target’s Gram operator.',fontsize=12,color=MUTED)
    grid=fig.add_gridspec(2,2,left=.085,right=.95,bottom=.19,top=.815,wspace=.27,hspace=.47,height_ratios=[1.4,1])
    ax=fig.add_subplot(grid[0,0]);style(ax)
    c=np.linspace(-1.5,1.5,601)
    ax.plot(c,c*c,color=TEAL,lw=2.8)
    ax.scatter([5/7],[25/49],s=70,color=CORAL,zorder=5)
    ax.annotate(r'fixed target $c=5/7$',xy=(5/7,25/49),xytext=(-.25,1.25),fontsize=12,
                arrowprops={'arrowstyle':'->','color':CORAL},color=CORAL)
    ax.set_xlim(-1.5,1.5);ax.set_ylim(0,2.5)
    ax.set_ylabel(r'$\lambda_{\min}(H(c))=c^2$ on this interval',fontsize=12)
    ax.set_xlabel('auxiliary coupling c');ax.grid(color=GRAY,alpha=.6)
    ax.set_title('A  Sensitivity across a separate target family',fontsize=14,loc='left',weight='bold',pad=20)
    ax=fig.add_subplot(grid[1,0]);style(ax)
    ax.plot([-1.5,0],[6,6],color=TEAL,lw=2.5);ax.plot([0,1.5],[6,6],color=TEAL,lw=2.5)
    ax.scatter([0],[6],facecolor=PAPER,edgecolor=TEAL,s=75,lw=2,zorder=4)
    ax.scatter([0],[2],color=CORAL,s=75,zorder=4)
    ax.set_xlim(-1.5,1.5);ax.set_ylim(1.5,6.6);ax.set_yticks([2,6]);ax.set_ylabel('exact rank M(c)')
    ax.set_xlabel('auxiliary coupling c');ax.grid(axis='y',color=GRAY,alpha=.6)
    ax.text(.09,3.1,'Rank drops only at c = 0.\nThe fixed puzzle stays at c = 5/7.',fontsize=11,color=MUTED)
    ax=fig.add_subplot(grid[:,1]);style(ax)
    # A resolvent slice at z=x+i*eta. eta>0 avoids the two spectral poles.
    eta=.35
    re=np.linspace(-5,78,1500)
    norm=1/np.minimum(np.abs(re+1j*eta-25/49),np.abs(re+1j*eta-72))
    ax.plot(re,norm,color=PURPLE,lw=2.5)
    for eig in (25/49,72):ax.axvline(eig,color=GOLD,lw=1.4,ls='--')
    ax.set_yscale('log');ax.set_xlim(-5,78);ax.set_ylim(.02,4)
    ax.set_xticks([0,20,40,60,72]);ax.set_xlabel(r'$\operatorname{Re}z$, along $\operatorname{Im}z=0.35$',fontsize=12)
    ax.set_ylabel(r'$\|(zI-H)^{-1}\|_2$ (log scale)',fontsize=12)
    ax.grid(axis='y',color=GRAY,alpha=.5)
    ax.set_title('B  Resolvent of the fixed operator H',fontsize=14,loc='left',weight='bold',pad=20)
    ax.text(.22,.83,r'$\|(zI-H)^{-1}\|_2=$'+'\n'+r'$\dfrac{1}{\min(|z-25/49|,|z-72|)}$',
            transform=ax.transAxes,fontsize=18,bbox={'facecolor':PAPER,'edgecolor':'none','alpha':.96})
    ax.text(.22,.55,r'At $z=0$: $\|H^{-1}\|_2=49/25$',transform=ax.transAxes,fontsize=14)
    ax.text(.22,.45,'Dashed lines mark the real spectrum.\nThe plotted complex slice avoids both poles.',transform=ax.transAxes,fontsize=11,color=MUTED)
    fig.text(.06,.12,r'$H(c)=\operatorname{diag}(72,c^2,c^2,c^2,c^2,72)$',fontsize=18,color=TEAL)
    fig.text(.06,.077,'Exact formulas determine the ranks and norms; curves are numerical renderings. No physical phase transition is claimed.',fontsize=12,color=MUTED)
    fig.text(.06,.041,'Varying c changes F and is not a candidate search within the fixed hodge.computer instance.',fontsize=12,color=MUTED)
    save(fig,'cyclic-fano-sensitivity')


def main():
    if not __debug__:
        raise RuntimeError('Run without -O so consistency checks remain enabled.')
    data=load_checked()
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'text.color':INK,
        'axes.labelcolor':INK,'svg.fonttype':'none','svg.hashsalt':'cyclic-fano-curve-v1'})
    map_figure(data);spectral_figure(data);sensitivity_figure(data)
    (OUT/'plot-data.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':'PASS','rank':data['rank'],'projector_ranks':data['projector_ranks'],
        'right_inverse_exact':data['exact_reconstruction_verified'],'figures':3,
        'scope':'quotient covering-family seed; no certificate'}))


if __name__=='__main__':
    main()
