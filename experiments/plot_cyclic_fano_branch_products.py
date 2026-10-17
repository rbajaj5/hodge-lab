#!/usr/bin/env python3
"""Plot a finite product manifest and exact reductions, without rank guesses.

The figure distinguishes checked exclusions from bounded unresolved searches.
It does not treat selected products as an exhaustive degree-bounded family.
"""
from __future__ import annotations

import ast
from collections import Counter
import hashlib
import json
from math import comb
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
import numpy as np
import sympy as S

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'results/cyclic-fano-branch-products'
OUT=ROOT/'results/cyclic-fano-branch-products-figures'
FACTOR_NAMES=('T','C','S','R','J')
FACTOR_DEGREES=(1,3,6,2,3)
WEIGHTS=(1,1,3,1,1,1)
INK,MUTED,PAPER,GRAY='#17323B','#53666D','#FAFAF5','#CBD3D0'
TEAL,PURPLE,AMBER,CORAL='#166A70','#7967AA','#A56A12','#CA584C'
SPECS=(('T2',(2,0,0,0,0)),('T4',(4,0,0,0,0)),('T8',(8,0,0,0,0)),
       ('C2',(0,2,0,0,0)),('C3',(0,3,0,0,0)),('S2',(0,0,2,0,0)),
       ('TC',(1,1,0,0,0)),('TS',(1,0,1,0,0)),('CS',(0,1,1,0,0)),
       ('RC',(0,1,0,1,0)),('RS',(0,0,1,1,0)),('R4',(0,0,0,4,0)),
       ('J2',(0,0,0,0,2)),('J3',(0,0,0,0,3)),('J4',(0,0,0,0,4)),
       ('JT2',(2,0,0,0,1)),('JTC',(1,1,0,0,1)),('JC2',(0,2,0,0,1)),
       ('JS',(0,0,1,0,1)),('JR2',(0,0,0,2,1)),('JTS',(1,0,1,0,1)),
       ('J2T2',(2,0,0,0,2)),('J2C2',(0,2,0,0,2)),
       ('J2R',(0,0,0,1,2)),('J3T',(1,0,0,0,3)),('J2S',(0,0,1,0,2)))


def sha(path):return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def pair(value):return S.Rational(value[0])+S.I*S.Rational(value[1])
def decode(terms,variables):
    return S.Poly.from_dict({tuple(t['powers']):pair(t['coefficient']) for t in terms},variables)
def ordinary_count(n):return comb(n+4,4) if n>=0 else 0
def weighted_count(n):return sum(ordinary_count(n-3*j) for j in range(n//3+1)) if n>=0 else 0


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


def basis_sizes(exponents):
    d=sum(n*w for n,w in zip(exponents,FACTOR_DEGREES))
    result={'degree':d,'full_numerator':sum(weighted_count(d+w-2) for w in WEIGHTS),
            'full_Koszul':sum(weighted_count(d+WEIGHTS[i]+WEIGHTS[j]-8) for i in range(6) for j in range(i+1,6)),
            'quotient':weighted_count(2*d-8)}
    a=exponents[4]
    if a:
        epsilon=a%2;k=d-3*a;half=(a+1)//2;pure=not any(exponents[:4])
        xx=0 if pure else 10*ordinary_count(d-6-3*epsilon)
        xt=5*ordinary_count(d-7+3*epsilon)
        result.update(a=a,k=k,epsilon=epsilon,half=half,pure_J=pure,
                      compact_base_base=xx,compact_base_t=xt,compact_columns=xx+xt,
                      compact_degree=2*k+6*half-2,cancelled_Delta_power=a//2)
    return result


def check_data():
    producer=ROOT/'experiments/cyclic_fano_branch_products.py'
    helper=ROOT/'experiments/cyclic_fano_branch_compact.py'
    checker=ROOT/'experiments/check_cyclic_fano_branch_products.py'
    primary_path=INPUT/'validation.json';primary=load(primary_path)
    review_path=INPUT/'independent-validation.json';review=load(review_path)
    candidate_path=ROOT/'results/cyclic-fano-higher-unfolding/candidates.json';candidates=load(candidate_path)
    target_path=ROOT/'results/cyclic-fano-curve/target.json';target=load(target_path)
    raw=target_path.parent/'source/instance.rec'
    assert primary['status']==review['status']=='PASS'
    assert review['schema']=='cyclic-fano-branch-products-independent-v1'
    assert primary['producer_sha256']==sha(producer)
    assert review['checker_lf_sha256']==sha(checker)
    assert primary['source_instance_sha256']==review['source_instance_lf_sha256']==sha(raw)
    assert review['candidate_input_lf_sha256']==sha(candidate_path)
    bindings={p.relative_to(ROOT).as_posix():sha(p) for p in (producer,helper,checker,primary_path,review_path,candidate_path,target_path,raw)}
    for name,digest in review['independent_arithmetic_dependencies'].items():
        path=ROOT/'experiments'/name;assert sha(path)==digest
        bindings[path.relative_to(ROOT).as_posix()]=digest
    checked={c.get('attempt_id',c['id']):c for c in review['checks']}
    unresolved={c.get('attempt_id',c['id']):c for c in review['unresolved']}
    primary_checked={c['id']:c for c in primary['checks']}
    primary_unresolved={c['id']:c for c in primary['unresolved']}
    variables=S.symbols('X0 X1 Z Y0 Y1 Y2');X0,X1,Z,Y0,Y1,Y2=variables
    original=S.symbols('X0 X1 X2 Y0 Y1 Y2')
    F=parse_polynomial(target['target']['F'],original)
    terms={}
    for m,c in F.terms():
        assert m[2]%3==0
        n=list(m);n[2]//=3;terms[tuple(n)]=c
    G=S.Poly.from_dict(terms,variables)
    factors=[decode(c['quotient_denominator'],variables) for c in candidates['candidates']]
    factors.extend([S.Poly(X1**2+Y2**2,variables),G.diff(Z)])
    assert len(factors)==5
    rows=[]
    for identity,exponents in SPECS:
        attempt_path=INPUT/('attempt-'+identity+'.json');attempt=load(attempt_path)
        candidate=attempt['candidate'];sizes=basis_sizes(exponents)
        assert candidate['id']==identity and candidate['factor_order']==list(FACTOR_NAMES)
        assert candidate['exponents']==list(exponents) and candidate['degree']==sizes['degree']
        assert attempt['producer_sha256']==sha(producer)
        expected=S.Poly(1,variables)
        for f,n in zip(factors,exponents):expected*=f**n
        assert (decode(candidate['denominator'],variables)-expected).is_zero
        assert all(sum(w*n for w,n in zip(WEIGHTS,m))==sizes['degree'] for m in expected.monoms())
        item={'id':identity,'exponents':list(exponents),**sizes,'attempt_status':attempt['status'],
              'wall_clock_limit_seconds':attempt['time_limit_seconds'],'attempt_lf_sha256':sha(attempt_path)}
        bindings[attempt_path.relative_to(ROOT).as_posix()]=sha(attempt_path)
        if attempt['status']!='completed':
            assert attempt['status'] in ('timeout','error')
            assert identity in unresolved and identity in primary_unresolved
            assert unresolved[identity]['attempt_lf_sha256']==sha(attempt_path)
            item.update(status='unresolved',stage=None,dual_terms=None)
        else:
            assert attempt['returncode']==0 and identity in checked and identity in primary_checked
            path=INPUT/(identity+'.json');packet=load(path);audit=checked[identity]
            assert packet['schema']=='cyclic-fano-branch-products-v1' and packet['instance']=='cyclic-triple-fano'
            assert packet['candidate']==candidate and packet['producer_sha256']==sha(producer)
            assert packet['candidate_input_sha256']==sha(candidate_path) and packet['source_instance_sha256']==sha(raw)
            assert audit['packet_lf_sha256']==primary_checked[identity]['packet_sha256']==sha(path)
            assert packet['status']==audit['status']=='excluded'
            assert packet['obstruction_stage']==audit['stage']
            assert audit['degree']==sizes['degree'] and audit['exponents']==list(exponents)
            assert audit['all_physical_column_pairings_zero']
            assert packet['full_numerator_dimension']==sizes['full_numerator']
            assert packet['complete_Koszul_directions']==sizes['full_Koszul']
            assert packet['quotient_dimension_eliminated']==sizes['quotient']
            assert packet['exact_rank_claim'] is False
            for name,digest in packet['dependencies'].items():
                dependency=ROOT/'experiments'/name;assert sha(dependency)==digest
                bindings[dependency.relative_to(ROOT).as_posix()]=digest
            stage=packet['obstruction_stage'];last=packet['stages'][-1]
            if stage=='E1':
                assert exponents[4]==0 and last['columns']==sizes['full_numerator']
            else:
                assert stage=='E2_reflection_compact' and exponents[4]>0
                meta=packet['compact_metadata']
                assert meta['helper_sha256']==sha(helper)
                assert meta['columns']==last['columns']==sizes['compact_columns']
                assert meta['raw_Koszul_coefficients']==sizes['full_Koszul']
                assert meta['raw_E2_quotient_coefficients']==sizes['quotient']
                assert meta['quotient_eliminated_exactly'] and meta['reflection_projection_complete']
                assert meta['Koszul_coefficients_reduced_modulo_g']
                assert meta['coefficient_degree']==sizes['compact_degree']
                reduction=audit['compact_reduction']
                assert reduction['helper_lf_sha256']==sha(helper)
                assert reduction['raw_Koszul_directions_represented']==sizes['full_Koszul']
                assert reduction['raw_quotient_directions_eliminated']==sizes['quotient']
                assert reduction['base_base_columns']==sizes['compact_base_base']
                assert reduction['base_t_columns']==sizes['compact_base_t']
                assert reduction['cancelled_Delta_power']==sizes['cancelled_Delta_power']
                assert reduction['first_order_operator_coefficient_checks']==40
            assert audit['physical_columns_checked']==last['columns']
            assert len(packet['dual'])==audit['dual_terms']
            assert pair(audit['rhs_pairing'])==1
            item.update(status='excluded',stage=stage,dual_terms=len(packet['dual']),
                        operator_rows=last['rows'],operator_columns=last['columns'],packet_lf_sha256=sha(path))
            if 'reused_dual_packet' in packet:
                reused=packet['reused_dual_packet'];prior=INPUT/(reused['id']+'.json')
                assert reused['sha256']==sha(prior) and packet['dual']==load(prior)['dual']
                item['reused_dual_from']=reused['id']
            bindings[path.relative_to(ROOT).as_posix()]=sha(path)
        rows.append(item)
    assert len(rows)==26 and len({tuple(r['exponents']) for r in rows})==26
    controls=[]
    for name,audit in checked.items():
        if name not in dict(SPECS):
            assert name.startswith('raw-')
            path=INPUT/(name+'.json');attempt_path=INPUT/('attempt-'+name+'.json')
            assert audit['packet_lf_sha256']==primary_checked[name]['packet_sha256']==sha(path)
            controls.append({'id':name,'status':audit['status'],'stage':audit['stage']})
            bindings[path.relative_to(ROOT).as_posix()]=sha(path)
            bindings[attempt_path.relative_to(ROOT).as_posix()]=sha(attempt_path)
    counts=Counter('unresolved' if r['status']=='unresolved' else r['stage'] for r in rows)
    return {'schema':'cyclic-fano-branch-products-plot-v1','instance':'cyclic-triple-fano','discussion_number':112,
            'sha256_policy':'File bytes with CRLF normalized to LF','source_sha256':bindings,
            'plot_source_sha256':sha(Path(__file__)),'factor_order':list(FACTOR_NAMES),'factor_degrees':list(FACTOR_DEGREES),
            'products':rows,'outcomes':dict(counts),'raw_controls':controls,
            'scope':'Only 26 selected fixed products. No exhaustive degree search, arbitrary-power result, global support, certificate, phase transition or full-rank claim.'}


def product_label(exponents):
    return '$'+''.join(name+(f'^{{{n}}}' if n>1 else '') for name,n in zip(FACTOR_NAMES,exponents) if n)+'$'


def style(ax):
    ax.set_facecolor(PAPER)
    for side in ('top','right'):ax.spines[side].set_visible(False)
    for side in ('left','bottom'):ax.spines[side].set_color(GRAY)
    ax.tick_params(colors=MUTED,labelsize=10)


def draw(data):
    rows=data['products'];counts=data['outcomes']
    excluded=sum(r['status']=='excluded' for r in rows);open_count=len(rows)-excluded
    fig=plt.figure(figsize=(17,15),facecolor=PAPER)
    fig.text(.055,.96,'Selected branch products: exact coverage and smaller E2 maps',fontsize=23,weight='bold')
    fig.text(.055,.929,'cyclic-triple-fano · discussion #112   |   26 selected fixed denominators; degrees 2–12',fontsize=12,color=MUTED)
    fig.text(.055,.894,r'$E=T^aC^bS^cR^rJ^j,\qquad\deg(T,C,S,R,J)=(1,3,6,2,3),\qquad J=\partial G/\partial Z$',fontsize=18,color=TEAL)
    fig.text(.055,.867,'T, C and S come from local branch guesses; R is the tangent norm. Selection is finite, not exhaustive.',fontsize=11.5,color=MUTED)
    # The grid is a literal exponent table. Color is ordinal exponent size,
    # not a numerical residual, probability, spectrum or geometric distance.
    ax=fig.add_axes([.11,.208,.38,.58]);ax.set_facecolor(PAPER)
    cmap=LinearSegmentedColormap.from_list('exponent',['#F0F3ED','#ABD2CC',TEAL])
    exponents=np.array([r['exponents'] for r in rows])
    ax.imshow(exponents,cmap=cmap,vmin=0,vmax=8,aspect='auto',interpolation='nearest')
    for i,r in enumerate(rows):
        for j,n in enumerate(r['exponents']):
            ax.text(j,i,str(n) if n else '·',ha='center',va='center',fontsize=11,
                    color='white' if n>=6 else INK)
        ax.text(5.0,i,str(r['degree']),ha='center',va='center',fontsize=11,color=INK)
        status='?' if r['status']=='unresolved' else ('E1' if r['stage']=='E1' else 'E2')
        color=AMBER if status=='?' else (TEAL if status=='E1' else PURPLE)
        ax.text(6.1,i,status,ha='center',va='center',fontsize=10.5,weight='bold',color=color,
                bbox={'boxstyle':'round,pad=.21','facecolor':PAPER,'edgecolor':color,'linewidth':.9})
        ax.text(7.3,i,str(r['dual_terms']) if r['dual_terms'] is not None else '—',
                ha='center',va='center',fontsize=10.5,color=MUTED)
    ax.set_xticks([0,1,2,3,4,5,6.1,7.3],list(FACTOR_NAMES)+['degree','result','dual\nterms']);ax.xaxis.tick_top()
    ax.tick_params(axis='x',length=0,pad=9,labelsize=11)
    ax.set_yticks(range(len(rows)),[product_label(r['exponents']) for r in rows])
    ax.tick_params(axis='y',length=0,pad=10,labelsize=12)
    ax.set_xlim(-.5,7.9);ax.set_ylim(len(rows)-.5,-.5)
    for line in np.arange(.5,len(rows),1):ax.axhline(line,color='white',lw=1.2)
    ax.axhline(11.5,color=MUTED,lw=1.2)
    for spine in ax.spines.values():spine.set_visible(False)
    fig.text(.11,.827,'The tested exponent tuples',fontsize=16,weight='bold')
    fig.text(.11,.178,'E1: exact numerator obstruction   E2: exact correction obstruction',fontsize=10.5,color=MUTED)
    fig.text(.11,.158,'?: bounded unresolved attempt; no mathematical exclusion',fontsize=10.5,color=AMBER)
    s2=next(r for r in rows if r['id']=='S2')
    if s2['status']=='unresolved':
        fig.text(.11,.138,f"S²: {s2['wall_clock_limit_seconds']} s cutoff; no E1 solution established.",fontsize=10.5,color=AMBER)

    repaired=[r for r in rows if r['exponents'][4]]
    ax=fig.add_axes([.565,.455,.34,.343]);style(ax)
    for i,r in enumerate(repaired):
        raw,compact=r['full_Koszul'],r['compact_columns']
        ax.plot([compact,raw],[i,i],color=GRAY,lw=2,zorder=1)
        ax.scatter(raw,i,color=TEAL,s=33,zorder=3)
        ax.scatter(compact,i,color=PURPLE if r['status']=='excluded' else PAPER,
                   edgecolor=PURPLE,s=40,zorder=4)
        ax.text(1.05,i,f"{r['quotient']:,}",transform=ax.get_yaxis_transform(),va='center',fontsize=10,color=MUTED)
    ax.set_yticks(range(len(repaired)),[product_label(r['exponents']) for r in repaired]);ax.invert_yaxis()
    ax.set_xscale('symlog',linthresh=1);ax.set_xlim(-.1,max(r['full_Koszul'] for r in repaired)*1.5)
    ax.set_xticks([0,10,100,1000,10000]);ax.set_xticklabels(['0','10','100','1,000','10,000'])
    ax.set_xlabel('number of operator columns (log scale above 1)',fontsize=10.5,labelpad=7)
    ax.text(1.05,1.02,'quotient\ncoefficients',transform=ax.transAxes,fontsize=9.5,color=MUTED,va='center')
    fig.text(.565,.827,'Exact compression, with quotient freedom preserved',fontsize=16,weight='bold')
    handles=[Line2D([],[],marker='o',linestyle='',color=TEAL,label='Full Koszul directions'),
             Line2D([],[],marker='o',linestyle='',color=PURPLE,label='Reflection-reduced columns')]
    if any(r['status']=='unresolved' for r in repaired):
        handles.append(Line2D([],[],marker='o',linestyle='',color=PURPLE,markerfacecolor=PAPER,
                              label='Dimensions known; search unresolved'))
    ax.legend(handles=handles,
              loc='lower right',fontsize=9,frameon=False,bbox_to_anchor=(1.05,-.24),ncol=1)
    fig.text(.565,.350,r'$G=Z^2+QZ+H,\quad t=2Z+Q,\quad t^2=\Delta=Q^2-4H$',fontsize=15,color=TEAL)
    fig.text(.565,.319,'Monic division removes the quotient variables exactly.',fontsize=11.5)
    fig.text(.565,.295,'Reflection and Koszul reduction preserve fixed-E feasibility.',fontsize=11.5)
    fig.text(.565,.271,'The plotted counts are basis sizes, not matrix ranks.',fontsize=11.5,color=MUTED)
    reused=[r for r in repaired if 'reused_dual_from' in r]
    if reused:
        fig.text(.565,.228,'J³ and J⁴ share the same 630-column map.',fontsize=12,weight='bold')
        fig.text(.565,.204,'The J⁴ row rechecks J³’s dual; it is not a new independent search.',fontsize=10.5,color=MUTED)
    pure2=next(r for r in repaired if r['id']=='J2')
    if pure2['status']=='excluded':
        fig.text(.565,.165,'J²: no compact correction columns, but nonzero right-hand side.',fontsize=10.5,color=PURPLE)
    unresolved_label='product' if open_count==1 else 'products'
    fig.text(.055,.105,f"{excluded} checked exclusions · {open_count} unresolved {unresolved_label} · {len(data['raw_controls'])} additional raw-system controls",fontsize=17,weight='bold')
    fig.text(.055,.080,'Each accepted obstruction has ℓM = 0 and ℓrhs = 1. Timeouts and errors never count as exclusions.',fontsize=11.5)
    fig.text(.055,.051,'Arbitrary exponents, linear combinations, a global support divisor and a certificate remain outside this batch.',fontsize=12,color=CORAL)
    fig.text(.945,.023,'cyclic-triple-fano · discussion #112',ha='right',fontsize=10,color=TEAL)
    OUT.mkdir(parents=True,exist_ok=True);stem=OUT/'cyclic-fano-branch-products'
    fig.savefig(stem.with_suffix('.png'),dpi=160,facecolor=PAPER)
    svg=stem.with_suffix('.svg');fig.savefig(svg,facecolor=PAPER,metadata={'Date':None})
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8',newline='\n')
    plt.close(fig)


def main():
    if not __debug__:raise RuntimeError('Run without -O so validation remains active.')
    data=check_data()
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'text.color':INK,'axes.labelcolor':INK,
                         'svg.fonttype':'none','svg.hashsalt':'cyclic-fano-branch-products-v1'})
    draw(data)
    (OUT/'plot-data.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':'PASS','products':len(data['products']),'outcomes':data['outcomes'],'raw_controls':len(data['raw_controls'])}))


if __name__=='__main__':main()
