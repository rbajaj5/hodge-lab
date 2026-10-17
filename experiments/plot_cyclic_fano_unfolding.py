#!/usr/bin/env python3
"""Plot checked cubic ramification and the measured rank-one unfolding map.

The circle diagram uses rescaled analytic normal-form coordinates. It is not
a numerical plot of the original target coordinates or global curve roots.
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
SOURCE=ROOT/'results'/'cyclic-fano-unfolding'
OUT=ROOT/'results'/'cyclic-fano-unfolding-figures'
TEAL,PURPLE,CORAL='#166A70','#7967AA','#CA584C'
INK,MUTED,PAPER,GRAY='#17323B','#53666D','#FAFAF5','#CBD3D0'
AXES=('X0','Y0','Y2')


def sha(path):return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def pair(value):return S.Rational(value[0])+S.I*S.Rational(value[1])
def pair_strings(value):
    real,imag=S.expand_complex(S.simplify(value)).as_real_imag()
    return [str(real),str(imag)]


def polynomial(terms,variables):
    return S.Poly(S.expand(sum(pair(item['coefficient'])*S.prod(x**n for x,n in zip(variables,item['powers']))
                             for item in terms)),*variables)


def check_packets():
    producer=ROOT/'experiments'/'cyclic_fano_unfolding.py'
    checker=ROOT/'experiments'/'check_cyclic_fano_unfolding.py'
    target=ROOT/'results'/'cyclic-fano-curve'/'target.json'
    fiber=ROOT/'results'/'cyclic-fano-fibers'/'fiber-equations.json'
    summary_path=SOURCE/'unfolding.json'
    summary=load(summary_path)
    assert summary['schema']=='cyclic-fano-unfolding-summary-v1'
    assert summary['producer_sha256']==sha(producer)
    assert summary['fixed_target_manifest_sha256']==sha(target)
    review_path=SOURCE/'independent-validation.json'
    review=load(review_path)
    assert review['status']=='PASS' and review['schema']=='cyclic-fano-unfolding-independent-v1'
    assert review['checker_lf_sha256']==sha(checker)
    assert review['summary_packet_lf_sha256']==sha(summary_path)
    assert review['negative_controls_rejected']>=15
    reviews={a['parameter_direction']:a for a in review['axes']}
    assert set(reviews)==set(AXES)
    raw_instance=target.parent/'source'/'instance.rec'
    sources={p.relative_to(ROOT).as_posix():sha(p) for p in (producer,checker,target,fiber,raw_instance)}
    b,p,h=S.symbols('b p h')
    matrices=[];central=[];packet_hashes={};receipt_hashes={}
    for axis in AXES:
        path=SOURCE/f'unfolding-{axis}.json';receipt_path=SOURCE/f'validation-{axis}.json'
        packet,receipt=load(path),load(receipt_path)
        assert summary['axis_packet_sha256'][axis]==sha(path)
        axis_review=reviews[axis]
        assert axis_review['status']=='PASS' and axis_review['packet_lf_sha256']==sha(path)
        assert axis_review['checker_lf_sha256']==sha(checker)
        assert axis_review['source_instance_lf_sha256']==sha(raw_instance)
        assert packet['schema']=='cyclic-fano-unfolding-v1' and packet['instance']=='cyclic-triple-fano'
        assert packet['parameter_direction']==axis and packet['jet_total_order']==4
        assert receipt['status']=='PASS' and receipt['packet_sha256']==sha(path)
        assert packet['producer_sha256']==receipt['producer_sha256']==sha(producer)
        assert packet['fixed_target_manifest_sha256']==sha(target)
        assert packet['base_fiber_packet_sha256']==sha(fiber)
        assert all(packet['checks'].values())
        assert pair(packet['target_z_derivative_at_origin'])==5*S.I/7
        jacobian=S.Matrix([[pair(v) for v in row] for row in packet['constant_implicit_jacobian']])
        assert S.simplify(jacobian.det())==pair(packet['constant_implicit_jacobian_determinant'])==22500*S.I/343
        germ=polynomial(packet['scalar_germ_jet'],(b,p,h))
        assert germ.total_degree()==4
        kappa=germ.coeff_monomial(b**3);quartic=germ.coeff_monomial(b**4)
        assert kappa==pair(packet['scalar_cubic_at_central_fiber'])==-1-48*S.I/175
        assert quartic==pair(packet['scalar_quartic_at_central_fiber'])==S.Rational(846,875)+613*S.I/175
        assert all(germ.coeff_monomial(b**j)==0 for j in range(3))
        T=S.Matrix([[germ.coeff_monomial(p),germ.coeff_monomial(h)],
                    [germ.coeff_monomial(b*p),germ.coeff_monomial(b*h)]])
        assert T==S.Matrix([[pair(v) for v in row] for row in packet['T1_parameter_matrix']])
        assert T==S.Matrix([[pair(v) for v in row] for row in axis_review['T1_matrix']])
        assert T.rank()==packet['T1_rank']==1 and T.det()==pair(packet['T1_determinant'])==0
        normalized=S.Matrix([[value/kappa for value in T.row(0)],
                             [S.simplify(T[1,j]/kappa-quartic*T[0,j]/kappa**2) for j in range(2)]])
        expected_normalized=S.Matrix([[pair(v) for v in row] for row in packet['normalized_Weierstrass_constant_and_linear_parameter_matrix']])
        assert all(S.simplify(value)==0 for value in normalized-expected_normalized)
        matrices.append(T)
        alpha=S.simplify(-kappa/T[0,1])
        beta=S.simplify(-(quartic+T[1,1]*alpha)/T[0,1])
        assert alpha==S.Rational(5,6)+8*S.I/35
        assert beta==-S.Rational(97,70)-2227*S.I/210
        # Check the actual substituted scalar equation through order b^4.
        substituted=S.Poly(S.expand(germ.as_expr().subs({p:0,h:alpha*b**3+beta*b**4})),b)
        assert all(substituted.coeff_monomial(b**j)==0 for j in range(5))
        central.append((alpha,beta))
        packet_hashes[path.name]=sha(path);receipt_hashes[receipt_path.name]=sha(receipt_path)
    assert len(set(central))==1 and all(T[:,1]==matrices[0][:,1] for T in matrices)
    full=S.Matrix.hstack(*(T[:,0] for T in matrices),matrices[0][:,1])
    assert full==S.Matrix([[0,0,-6*S.I/5,S.Rational(6,5)],
                           [0,0,S.Rational(252,25)-18*S.I/5,S.Rational(18,5)+252*S.I/25]])
    assert full.rank()==1 and all(S.expand(value)==0 for value in full[:,2]+S.I*full[:,3])
    reviewed_full=S.Matrix([[pair(v) for v in row] for row in review['all_four_target_directions']['T1_matrix']])
    assert review['all_four_target_directions']['coordinates']==['U','V','h','W']
    assert full==reviewed_full[:,[0,1,3,2]]
    assert full==S.Matrix([[pair(v) for v in row] for row in summary['full_T1_matrix']])
    assert summary['full_T1_rank']==1 and not summary['miniversal']
    assert summary['ramification_index']==3
    assert [pair(v) for v in summary['h_of_b_jet_coefficients_ascending']]==[0,0,0,*central[0]]
    assert review['actual_seed_path_branch_jet']['h_coefficients_ascending']==summary['h_of_b_jet_coefficients_ascending']
    assert review['actual_seed_path_branch_jet']['substitution_into_scalar_four_jet_zero']
    target_chart_tangent=S.Matrix([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,S.I]])
    assert target_chart_tangent.det()==-1
    assert target_chart_tangent==S.Matrix([[pair(v) for v in row] for row in summary['target_tangent_basis_matrix']])
    result={'schema':'cyclic-fano-unfolding-plot-v1','instance':'cyclic-triple-fano','discussion_number':112,
            'sha256_policy':'UTF-8 bytes with CRLF normalized to LF','packet_sha256':packet_hashes,
            'validation_sha256':receipt_hashes,'independent_validation_sha256':sha(review_path),
            'summary_sha256':sha(summary_path),
            'source_sha256':sources,'plot_source_sha256':sha(Path(__file__)),
            'jet_total_order':4,'slice_h_b3':pair_strings(central[0][0]),'slice_h_b4':pair_strings(central[0][1]),
            'T1_column_order':['X0','Y0','Y2','h'],'T1_row_basis':['1','b'],
            'T1_matrix':[[pair_strings(v) for v in row] for row in full.tolist()],'T1_rank':1,
            'transverse_attempt_outcomes':summary['axis_attempts'],
            'initial_implementation_failure_sha256':sha(SOURCE/'attempt-initial-serialization.json'),
            'target_chart_tangent_rank':4,'normal_form':'h=w^3 after an unspecified local analytic source change',
            'diagram_coordinates':'zeta=w/rho and eta=h/rho^3; no numerical value of rho is asserted',
            'scope':'Exact local jet coefficients and rank-one first-order T1 map. The circle diagram is a rescaled analytic normal-form illustration; it gives no original-coordinate radius, global roots, global branch equation, miniversal cusp, support, or certificate. Local evaluation-fiber monodromy is not identified with the original X2 cyclic deck action.'}
    return result


def style(ax):
    ax.set_facecolor(PAPER)
    for side in ('top','right'):ax.spines[side].set_visible(False)
    for side in ('left','bottom'):ax.spines[side].set_color(GRAY)
    ax.tick_params(colors=MUTED,labelsize=10)


def circular_axes(ax):
    style(ax);ax.set_xlim(-1.35,1.35);ax.set_ylim(-1.35,1.35);ax.set_aspect('equal')
    ax.set_xticks([-1,0,1]);ax.set_yticks([-1,0,1]);ax.axhline(0,color=GRAY,lw=.7,zorder=0)
    ax.axvline(0,color=GRAY,lw=.7,zorder=0)


def draw(data):
    fig=plt.figure(figsize=(16,12),facecolor=PAPER)
    fig.text(.055,.949,'Cubic ramification, with an incomplete first-order unfolding',fontsize=23,weight='bold')
    fig.text(.055,.914,'cyclic-triple-fano · discussion #112   |   The target hypersurface stays fixed; the marked target point moves.',fontsize=12,color=MUTED)
    fig.text(.055,.859,r'$h(b)=\left(\frac{5}{6}+\frac{8i}{35}\right)b^3-\left(\frac{97}{70}+\frac{2227i}{210}\right)b^4+O(b^5)$',fontsize=24,color=TEAL)
    fig.text(.055,.817,'Exact coefficients of the local slice. Its nonzero cubic term gives ramification index 3.',fontsize=12)
    fig.text(.055,.781,'The diagrams below use analytic normal-form coordinates, after an unspecified local coordinate change.',fontsize=11,color=MUTED)

    theta=np.linspace(0,2*np.pi,721)
    ax=fig.add_axes([.065,.437,.28,.298]);circular_axes(ax)
    colors=(TEAL,CORAL,PURPLE)
    tracks=[]
    for k,color in enumerate(colors):
        points=np.exp(1j*(theta+2*np.pi*k)/3);tracks.append(points)
        ax.plot(points.real,points.imag,color=color,lw=3)
        ax.scatter(points[0].real,points[0].imag,s=38,color=color,zorder=4)
        j=450;ax.annotate('',xy=(points[j+12].real,points[j+12].imag),xytext=(points[j].real,points[j].imag),
                          arrowprops={'arrowstyle':'-|>','color':color,'lw':2,'mutation_scale':15})
        start=points[0];ax.text(1.17*start.real,1.17*start.imag,str(k),color=color,fontsize=14,ha='center',va='center')
    ax.scatter(0,0,s=28,color=INK,marker='x');ax.set_xlabel(r'$\mathrm{Re}\,\zeta$');ax.set_ylabel(r'$\mathrm{Im}\,\zeta$')
    ax.set_title('Three local sheets over one target loop',fontsize=14,loc='left',pad=15)
    ax=fig.add_axes([.385,.437,.28,.298]);circular_axes(ax)
    points=np.exp(1j*theta);ax.plot(points.real,points.imag,color=TEAL,lw=2.8)
    j=110;ax.annotate('',xy=(points[j+16].real,points[j+16].imag),xytext=(points[j].real,points[j].imag),
                     arrowprops={'arrowstyle':'-|>','color':TEAL,'lw':2,'mutation_scale':15})
    ax.scatter(1,0,s=38,color=TEAL);ax.scatter(0,0,s=28,color=INK,marker='x')
    ax.text(.06,.08,'branch value',fontsize=10,color=MUTED)
    ax.set_xlabel(r'$\mathrm{Re}\,\eta$');ax.set_ylabel(r'$\mathrm{Im}\,\eta$')
    ax.set_title(r'Positive target loop: $\eta=e^{i\theta}$',fontsize=14,loc='left',pad=15)
    fig.text(.706,.69,r'$h=w^3$',fontsize=28,color=TEAL)
    fig.text(.706,.635,r'$\zeta=w/\rho,\quad\eta=h/\rho^3$',fontsize=17)
    fig.text(.706,.582,r'$\eta=\zeta^3$',fontsize=23)
    fig.text(.706,.524,'After one positive loop:',fontsize=12,color=MUTED)
    fig.text(.706,.479,r'$0\;\longrightarrow\;1\;\longrightarrow\;2\;\longrightarrow\;0$',fontsize=19,color=TEAL)
    fig.text(.055,.375,'Unit circles are rescaled normal-form coordinates. No neighborhood radius in the original coordinates is certified.',fontsize=11,color=MUTED)

    fig.text(.055,.331,'The actual first-order parameter map has rank 1',fontsize=18,weight='bold')
    fig.text(.055,.299,r'Target chart: $(U,1,z,i+V,1+h,i(1+h)+W)$, with $z$ determined by the fixed equation.',fontsize=12,color=MUTED)
    ax=fig.add_axes([.065,.165,.61,.105]);ax.axis('off')
    rows=[[r'$[1]$',r'$0$',r'$0$',r'$-6i/5$',r'$6/5$'],
          [r'$[b]$',r'$0$',r'$0$',r'$252/25-18i/5$',r'$18/5+252i/25$']]
    table=ax.table(cellText=rows,colLabels=[r'$T^1$ basis',r'$U\;(X_0)$',r'$V\;(Y_0)$',r'$W\;(Y_2)$',r'$h$'],
                   colWidths=[.14,.14,.14,.29,.29],cellLoc='center',bbox=[0,0,1,1])
    table.auto_set_font_size(False);table.set_fontsize(13)
    for (r,c),cell in table.get_celld().items():
        cell.set_edgecolor('white');cell.set_linewidth(1.5)
        cell.set_facecolor('#E5ECE8' if r%2 else PAPER);cell.set_text_props(color=INK)
        if r==0:cell.set_facecolor(TEAL);cell.set_text_props(color='white')
        elif c in (1,2):cell.set_text_props(color=MUTED)
    fig.text(.714,.235,r'$c_U=c_V=0$',fontsize=18)
    fig.text(.714,.192,r'$c_W=-i\,c_h$',fontsize=18,color=CORAL)
    fig.text(.055,.117,'Three transverse attempts were checked. Together with h they span the target tangent space, but their images span only one T¹ direction.',fontsize=11.5)
    fig.text(.055,.079,'This does not establish a miniversal cusp or a global branch equation. Higher-order transverse behavior remains open.',fontsize=12,color=CORAL)
    fig.text(.055,.052,'These are local evaluation-fiber sheets; no identification with the original X₂ cyclic deck action is established.',fontsize=10.5,color=MUTED)
    fig.text(.945,.028,'cyclic-triple-fano · discussion #112',ha='right',fontsize=10,color=TEAL)

    # Exact formulas define the normal-form tracks; floating arithmetic only draws them.
    for k,track in enumerate(tracks):
        assert np.max(np.abs(track**3-np.exp(1j*theta)))<32*np.finfo(float).eps
        assert abs(track[-1]-tracks[(k+1)%3][0])<1e-14
    data['normal_form_sample_count']=len(theta)
    data['normal_form_max_draw_residual']=float(max(np.max(np.abs(track**3-np.exp(1j*theta))) for track in tracks))
    data['monodromy_permutation']=[1,2,0]
    OUT.mkdir(parents=True,exist_ok=True)
    stem=OUT/'cyclic-fano-unfolding'
    fig.savefig(stem.with_suffix('.png'),dpi=160,facecolor=PAPER)
    svg=stem.with_suffix('.svg');fig.savefig(svg,facecolor=PAPER,metadata={'Date':None})
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8',newline='\n')
    plt.close(fig)


def main():
    if not __debug__:raise RuntimeError('Run without -O so exact checks remain active.')
    data=check_packets()
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'text.color':INK,
        'axes.labelcolor':INK,'svg.fonttype':'none','svg.hashsalt':'cyclic-fano-unfolding-v1'})
    draw(data)
    (OUT/'plot-data.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':'PASS','T1_rank':data['T1_rank'],'slice_ramification_index':3,'figures':1}))


if __name__=='__main__':main()
