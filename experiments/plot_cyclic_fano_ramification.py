#!/usr/bin/env python3
"""Visualize exact marked-evaluation ranks in both affine charts of the seed.

Every displayed entry and determinant comes from checked rational-polynomial
data. No singular values, real slices, or invented embeddings are sampled.
"""
from __future__ import annotations

import hashlib
from itertools import combinations
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import sympy as S

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'results'/'cyclic-fano-ramification'
OUT = ROOT/'results'/'cyclic-fano-ramification-figures'
TEAL, INK, MUTED = '#166A70', '#17323B', '#53666D'
PAPER, GRAY, TINT = '#FAFAF5', '#CBD3D0', '#DDECE8'
CORAL, PURPLE = '#CA584C', '#7967AA'


def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def relative(path):
    return path.relative_to(ROOT).as_posix()


def matrix(rows):
    return S.Matrix([[S.sympify(value) for value in row] for row in rows])


def decode(rows):
    return S.Matrix([[S.Rational(a)+S.I*S.Rational(b) for a,b in row] for row in rows])


def load_checked():
    packet_path=SOURCE/'packet.json';receipt_path=SOURCE/'validation.json'
    packet,receipt=load(packet_path),load(receipt_path)
    frozen_path=ROOT/'results'/'cyclic-fano-curve'/'cyclic-free-curve.json'
    frozen=load(frozen_path)
    checker=ROOT/'experiments'/'check_cyclic_fano_ramification.py'
    assert packet['schema']=='cyclic-fano-seed-ramification-v1'
    assert packet['instance']=='cyclic-triple-fano' and receipt['status']=='PASS'
    assert receipt['packet_lf_sha256']==sha(packet_path)
    assert packet['checker_lf_sha256']==receipt['checker_lf_sha256']==sha(checker)
    assert packet['frozen_curve_packet_lf_sha256']==sha(frozen_path)
    assert packet['source_instance_lf_sha256']==frozen['raw_instance_sha256']
    assert packet['upstream_commit']==frozen['upstream_commit']
    assert receipt['maximal_minors_checked']==10 and receipt['unit_minor_charts']==2
    assert receipt['rank_everywhere_on_seed']==4 and receipt['ramification_on_seed']=='empty'
    assert receipt['weighted_chart_transition']==receipt['hypersurface_tangent_identities']=='PASS'
    assert receipt['negative_controls_rejected']>=5
    assert packet['seed_curve']==frozen['curve']

    # Reconstruct both chart matrices from the frozen implicit family tangent.
    local=frozen['local_family']
    assert packet['family_coordinate_polynomials']==local['curve']
    parameters=S.symbols(' '.join(local['free_parameters']))
    dependent=S.symbols(' '.join(local['dependent_parameters']))
    s,t,r,u=S.symbols('s t r u')
    family=S.Matrix([S.sympify(value) for value in local['curve']])
    base={S.Symbol(name):S.Rational(a)+S.I*S.Rational(b) for name,(a,b) in local['base_point'].items()}
    implicit=decode(local['dependent_tangent_matrix'])
    assert implicit==matrix(packet['implicit_derivative_matrix'])
    tangent=(family.jacobian(parameters)+family.jacobian(dependent)*implicit).subs(base)
    assert tangent==matrix(packet['global_family_tangent_columns'])
    seed=family.subs(base)
    es=S.Matrix.hstack(tangent.subs({s:1,t:r}),seed.diff(t).subs({s:1,t:r}))[[0,2,3,4,5],:]
    et=S.Matrix.hstack(tangent.subs({s:u,t:1}),seed.diff(s).subs({s:u,t:1}))[[0,1,2,3,5],:]
    charts=packet['charts']
    assert len(charts)==2 and charts[0]['name']=='X1=1' and charts[1]['name']=='Y1=1'
    for chart,operator in zip(charts,(es,et)):
        assert matrix(chart['evaluation_matrix'])==operator
        assert operator.shape==(5,4)
        assert {tuple(item['rows']) for item in chart['maximal_minors']}==set(combinations(range(5),4))
        for item in chart['maximal_minors']:
            assert S.expand(operator[item['rows'],:].det()-S.sympify(item['determinant']))==0
        assert operator[chart['unit_minor_rows'],:].det()==1
        assert chart['unit_minor_determinant']=='1'
        assert chart['rank_at_every_complex_coordinate']==4
        assert matrix(chart['hypersurface_gradient'])*operator==S.zeros(1,4)
    assert charts[0]['unit_minor_rows']==[0,1,3,4]
    assert charts[1]['unit_minor_rows']==[0,1,2,3]
    assert es[[0,1,2,3],:].det()==r**5

    transition=packet['chart_transition']
    target_derivative=matrix(transition['target_derivative_on_seed'])
    source_derivative=matrix(transition['source_derivative_u_to_r'])
    assert source_derivative==S.diag(1,1,1,-1/u**2)
    assert S.simplify(target_derivative.subs(r,1/u)*es.subs(r,1/u)*source_derivative-et)==S.zeros(5,4)
    xx,zz,yy,rr,vv=S.symbols('xx zz yy rr vv')
    transition_functions=S.Matrix([S.sympify(value) for value in transition['target_from_X1_to_Y1']])
    reconstructed=transition_functions.jacobian((xx,zz,yy,rr,vv)).subs({xx:0,zz:0,yy:S.I,rr:r,vv:S.I*r})
    assert reconstructed==target_derivative

    boundary=packet['chosen_affine_boundary']
    endpoint=et.subs(u,0)[:,:3]
    assert endpoint==matrix(boundary['section_tangent_in_Y1_chart'])
    assert endpoint[boundary['unit_minor_rows'],:].det()==1
    assert endpoint.rank()==boundary['section_rank_at_seed_endpoint']==receipt['boundary_section_rank']==3
    assert boundary['containing_hypersurface']=='X1=0 on W'
    assert family.subs({s:0,t:1})==S.Matrix([S.sympify(value) for value in boundary['section_image']])
    opposite=packet['opposite_affine_boundary']
    assert es.subs(r,0)[:,:3][opposite['minor_rows'],:].det()==S.sympify(opposite['minor'])==-1
    return {'schema':'cyclic-fano-ramification-plot-v1','instance':'cyclic-triple-fano',
        'discussion_number':112,'sha256_policy':'UTF-8 bytes with CRLF normalized to LF',
        'packet_path':relative(packet_path),'packet_sha256':sha(packet_path),
        'validation_sha256':sha(receipt_path),'checker_path':relative(checker),'checker_sha256':sha(checker),
        'frozen_curve_path':relative(frozen_path),'frozen_curve_sha256':sha(frozen_path),
        'plot_source_sha256':sha(Path(__file__)),'upstream_commit':packet['upstream_commit'],
        's_chart_matrix':charts[0]['evaluation_matrix'],'t_chart_matrix':charts[1]['evaluation_matrix'],
        's_chart_unit_rows':charts[0]['unit_minor_rows'],'t_chart_unit_rows':charts[1]['unit_minor_rows'],
        's_chart_maximal_minors':charts[0]['maximal_minors'],'t_chart_maximal_minors':charts[1]['maximal_minors'],
        'maximal_minors_rechecked':10,'unit_minor_determinants':['1','1'],
        'misleading_single_minor':'r**5','chart_transition':transition,
        'chosen_affine_boundary':boundary,'rank_everywhere_on_seed':4,
        'metric_caveat':'Coordinate matrices and exact ranks; no canonical metric or intrinsic singular-value interpretation.',
        'scope':'The marked evaluation is unramified along this seed. The omitted source section has a rank-three image in X1=0 locally at its endpoint. This is not a complete support, global branch computation, certificate, or solution.'}


def matrix_plot(ax,operator,selected,row_labels,col_labels):
    nr,nc=operator.shape
    for r in range(nr):
        for c in range(nc):
            ax.add_patch(Rectangle((c-.5,r-.5),1,1,
                facecolor=TINT if r in selected else PAPER,edgecolor='white',lw=2))
            value=operator[r,c]
            ax.text(c,r,r'$'+S.latex(value)+r'$' if value else '·',
                    fontsize=18,ha='center',va='center',color=INK if value else '#A6B5B0')
        if r in selected:
            ax.add_patch(Rectangle((-.58,r-.43),.045,.86,facecolor=TEAL,clip_on=False))
    ax.set_xlim(-.5,nc-.5);ax.set_ylim(nr-.5,-.5)
    ax.set_xticks(range(nc),col_labels);ax.set_yticks(range(nr),row_labels)
    ax.tick_params(length=0,pad=12,labelsize=13,colors=INK)
    for r,label in enumerate(ax.get_yticklabels()):
        label.set_color(TEAL if r in selected else MUTED)
    for spine in ax.spines.values():spine.set_visible(False)


def save(fig):
    OUT.mkdir(parents=True,exist_ok=True)
    fig.savefig(OUT/'cyclic-fano-ramification.png',dpi=160,facecolor=PAPER)
    svg=OUT/'cyclic-fano-ramification.svg'
    fig.savefig(svg,facecolor=PAPER,metadata={'Date':None})
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',
                   encoding='utf-8',newline='\n')
    plt.close(fig)


def render(data):
    fig=plt.figure(figsize=(16,12),facecolor=PAPER)
    fig.text(.06,.949,r'No marked-evaluation rank drop along the seed $\mathbf{P}^{1}$',fontsize=24,weight='bold')
    fig.text(.06,.911,'cyclic-triple-fano · discussion #112  |  Exact chart matrices in Q(i)[r] and Q(i)[u]',fontsize=12,color=MUTED)
    fig.text(.06,.856,r'$\phi([s:t])=[\,0:s:0:is:t:it\,]\ \in W$',fontsize=23,color=TEAL)
    fig.text(.59,.859,r'$s\ne0,\quad t\ne0:\qquad u=1/r$',fontsize=21)
    fig.text(.59,.827,'The two charts cover the whole complex projective seed.',fontsize=11,color=MUTED)
    fig.text(.095,.774,r'$U_s:\ s\ne0,\qquad r=t/s$',fontsize=22,color=TEAL)
    fig.text(.57,.774,r'$U_t:\ t\ne0,\qquad u=s/t$',fontsize=22,color=TEAL)
    fig.text(.095,.741,r'Normalize $X_1=1$; $r=0$ is $[1:0]$.',fontsize=12,color=MUTED)
    fig.text(.57,.741,r'Normalize $Y_1=1$; $u=0$ is $[0:1]$.',fontsize=12,color=MUTED)
    ax=fig.add_axes([.12,.405,.33,.286])
    matrix_plot(ax,matrix(data['s_chart_matrix']),data['s_chart_unit_rows'],
                [r'$X_0$',r'$Z$',r'$Y_0$',r'$Y_1$',r'$Y_2$'],
                [r'$\delta a$',r'$\delta b$',r'$\delta c$',r'$\delta r$'])
    ax=fig.add_axes([.595,.405,.33,.286])
    matrix_plot(ax,matrix(data['t_chart_matrix']),data['t_chart_unit_rows'],
                [r'$X_0$',r'$X_1$',r'$Z$',r'$Y_0$',r'$Y_2$'],
                [r'$\delta a$',r'$\delta b$',r'$\delta c$',r'$\delta u$'])
    fig.text(.12,.345,r'Highlighted $4\times4$ minor: $\det=1$',fontsize=18,color=TEAL)
    fig.text(.595,.345,r'Highlighted $4\times4$ minor: $\det=1$',fontsize=18,color=TEAL)
    fig.text(.12,.305,r'$\operatorname{rank}(d\,\mathrm{ev})=4$ for every $r\in\mathbf{C}$.',fontsize=17)
    fig.text(.595,.305,r'$\operatorname{rank}(d\,\mathrm{ev})=4$ for every $u\in\mathbf{C}$.',fontsize=17)
    fig.text(.06,.271,r'Cutting to $s\ne0$ omits the section $s=0$: its image lies in $X_1=0$, with rank 3 at the seed endpoint.',fontsize=12,color=MUTED)
    fig.text(.06,.237,'A vanishing minor is not automatically ramification',fontsize=17,weight='bold')
    fig.text(.06,.198,r'In $U_s$, choosing rows $(X_0,Z,Y_0,Y_1)$ instead gives $r^5$. It vanishes at $r=0$,',fontsize=14)
    fig.text(.06,.165,'but the highlighted minor remains 1 there. The marked evaluation keeps full rank.',fontsize=14,color=TEAL)
    fig.text(.06,.108,'No marked-evaluation ramification along the seed; global branch/boundary images and a certificate remain uncomputed.',fontsize=12)
    fig.text(.06,.071,'The entries depend on affine coordinates and tangent bases; no intrinsic metric or singular-value interpretation is asserted.',fontsize=11,color=MUTED)
    fig.text(.94,.028,'cyclic-triple-fano · discussion #112',ha='right',fontsize=10,color=TEAL)
    save(fig)


def main():
    if not __debug__:
        raise RuntimeError('Run without -O so exact consistency checks remain active.')
    data=load_checked()
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'text.color':INK,
        'axes.labelcolor':INK,'svg.fonttype':'none','svg.hashsalt':'cyclic-fano-ramification-v1'})
    render(data)
    (OUT/'plot-data.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':'PASS','figures':1,'rank_along_seed':4,
        's_chart_unit_minor':1,'t_chart_unit_minor':1,'scope':'seed only; no certificate'}))


if __name__=='__main__':
    main()
