#!/usr/bin/env python3
"""Draw the exact fixed-quartic coefficient obstruction for target #119.

The marks show coefficient support, not a metric or numerical singular-value
approximation. All 36 columns are reconstructed from the frozen target first.
"""
from __future__ import annotations

import ast
from fractions import Fraction as Q
import hashlib
import itertools
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import sympy as S

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'results'/'quadric-contact-pilot'
OUT=ROOT/'results'/'quadric-contact-pilot-figures'
TEAL,PURPLE,CORAL='#166A70','#7967AA','#CA584C'
INK,MUTED,PAPER,GRAY='#17323B','#53666D','#FAFAF5','#CBD3D0'
NAMES=('X0','X1','X2','Y0','Y1','Y2')
VARIABLES=S.symbols(' '.join(NAMES))


def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()


def load(path):return json.loads(path.read_text(encoding='utf-8'))


def polynomial(text):
    """Only accept the polynomial syntax used by frozen instance.rec files."""
    def visit(node):
        if isinstance(node,ast.Constant) and type(node.value) is int:return S.Integer(node.value)
        if isinstance(node,ast.Name) and node.id in NAMES:return VARIABLES[NAMES.index(node.id)]
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,ast.USub):return -visit(node.operand)
        if isinstance(node,ast.BinOp):
            left=visit(node.left)
            if isinstance(node.op,ast.Pow):
                assert isinstance(node.right,ast.Constant) and type(node.right.value) is int
                assert node.right.value>=0
                return left**node.right.value
            right=visit(node.right)
            if isinstance(node.op,ast.Add):return left+right
            if isinstance(node.op,ast.Sub):return left-right
            if isinstance(node.op,ast.Mult):return left*right
            if isinstance(node.op,ast.Div):
                assert right.is_Rational and right!=0
                return left/right
        raise ValueError('Unsupported polynomial syntax.')
    return S.expand(visit(ast.parse(text,mode='eval').body))


def coefficients(expression):
    return {powers:Q(str(value)) for powers,value in S.Poly(S.expand(expression),*VARIABLES).terms() if value}


def decode(terms):
    return {tuple(term['powers']):Q(term['coefficient']) for term in terms}


def expression(terms):
    return sum(S.Rational(term['coefficient'])*S.prod(x**e for x,e in zip(VARIABLES,term['powers'])) for term in terms)


def rank(matrix):
    rows=[[Q(value) for value in row] for row in matrix]
    pivots={}
    for row in rows:
        for col,old in sorted(pivots.items()):
            if row[col]:
                factor=row[col]
                row=[a-factor*b for a,b in zip(row,old)]
        pivot=next((j for j,value in enumerate(row) if value),None)
        if pivot is not None:
            scale=row[pivot]
            pivots[pivot]=[value/scale for value in row]
    return len(pivots)


def check_packet():
    packet_path=SOURCE/'pilot.json';target_path=SOURCE/'target.json'
    receipt_path=SOURCE/'validation.json';review_path=SOURCE/'independent-validation.json'
    producer=ROOT/'experiments'/'quadric_contact_pilot.py'
    checker=ROOT/'experiments'/'check_quadric_contact_pilot.py'
    packet,target,receipt,review=map(load,(packet_path,target_path,receipt_path,review_path))
    assert packet['schema']=='quadric-contact-quartic-pilot-v1'
    assert packet['instance']==target['instance']=='quadric-contact-broken'
    assert receipt['status']==review['status']=='PASS'
    assert receipt['packet_sha256']==sha(packet_path)
    assert packet['producer_sha256']==receipt['producer_sha256']==sha(producer)
    assert packet['frozen_target_sha256']==sha(target_path)
    for name,digest in target['source_sha256'].items():assert sha(SOURCE/'source'/name)==digest
    assert target['target']['q']=='1'
    assert review['schema']=='quadric-contact-pilot-independent-v1'
    assert review['pilot_lf_sha256']==sha(packet_path)
    assert review['target_lf_sha256']==sha(target_path)
    assert review['checker_lf_sha256']==sha(checker)
    assert review['instance_rec_lf_sha256']==sha(SOURCE/'source'/'instance.rec')
    assert review['complete_fixed_denominator_space']['Koszul_directions']==15
    assert review['complete_fixed_denominator_space']['quotient_monomials']==21
    assert review['smoothness']['prime']==5 and review['negative_controls_rejected']>=5

    F=polynomial(target['target']['F']);A=polynomial(target['target']['A'])
    reduced_F={powers:value.numerator*pow(value.denominator,-1,5)%5 for powers,value in coefficients(F).items()}
    reduced_F={powers:value for powers,value in reduced_F.items() if value}
    assert reduced_F=={tuple(6*int(i==j) for i in range(6)):1 for j in range(6)}
    D=polynomial('4*(X0**2+Y0**2)*X0*Y0+5*X1*Y1*(X2**2+2*Y2**2)/7')
    h=polynomial('X1**2*X0*Y0')
    N=[-h*VARIABLES[3],S.Integer(0),S.Integer(0),h*VARIABLES[0],S.Integer(0),S.Integer(0)]
    assert coefficients(D)==decode(packet['denominator'])
    assert all(coefficients(n)==decode(terms) for n,terms in zip(N,packet['initial_numerator']))
    Fd=[S.diff(F,x) for x in VARIABLES];Dd=[S.diff(D,x) for x in VARIABLES]
    assert S.expand(sum(n*f for n,f in zip(N,Fd))-A*D)==0
    B=S.expand(D*sum(S.diff(n,x) for n,x in zip(N,VARIABLES))-sum(n*d for n,d in zip(N,Dd)))
    assert coefficients(B)==decode(packet['E2_initial_residual'])
    assert B==polynomial('5*X1**3*Y1*(X2**2+2*Y2**2)*(X0**2-Y0**2)/7')

    rows=[tuple(row) for row in packet['coefficient_rows']]
    assert len(rows)==len(set(rows)) and all(sum(row)==8 for row in rows)
    exported=packet['matrix_columns'];columns=[]
    assert len(exported)==36
    pairs=list(itertools.combinations(range(6),2))
    quadratic_powers=[]
    for first in range(6):
        for second in range(first,6):
            powers=[0]*6;powers[first]+=1;powers[second]+=1
            quadratic_powers.append(tuple(powers))
    quadratic_powers.sort(reverse=True)
    for j,item in enumerate(exported):
        if j<15:
            i,k=pairs[j]
            assert item['kind']=='Koszul' and item['indices']==[i,k]
            physical=coefficients(Fd[i]*Dd[k]-Fd[k]*Dd[i])
        else:
            powers=quadratic_powers[j-15]
            assert item['kind']=='F_quotient' and tuple(item['multiplier_powers'])==powers and item['sign']==-1
            physical=coefficients(-F*S.prod(x**e for x,e in zip(VARIABLES,powers)))
        saved={rows[i]:Q(value) for i,value in item['entries']}
        assert len(saved)==len(item['entries']) and physical==saved
        columns.append([saved.get(row,Q(0)) for row in rows])
    rhs={rows[i]:Q(value) for i,value in packet['rhs_entries']}
    assert rhs==coefficients(-B)
    union=set(rhs)
    for column in exported:union.update(rows[i] for i,_ in column['entries'])
    assert union==set(rows)
    matrix=[list(row) for row in zip(*columns)]
    vector=[rhs.get(row,Q(0)) for row in rows]
    assert packet['matrix_shape']==[len(rows),36]==[487,36]
    assert packet['full_homogeneous_degree8_row_count']==1287
    assert rank(matrix)==packet['coefficient_rank']==36
    assert rank([row+[value] for row,value in zip(matrix,vector)])==packet['augmented_rank']==37
    assert not packet['consistent'] and not receipt['certificate_found']
    dual=dict((int(i),Q(c)) for i,c in packet['obstruction_functional'])
    assert len(dual)==1
    selected=next(iter(dual))
    assert rows[selected]==(2,3,2,0,1,0)
    assert dual[selected]==Q(-7,5) and vector[selected]==Q(-5,7)
    assert all(value==0 for value in matrix[selected])
    assert all(sum(dual.get(i,Q(0))*row[j] for i,row in enumerate(matrix))==0 for j in range(36))
    assert sum(dual.get(i,Q(0))*value for i,value in enumerate(vector))==1
    assert len(receipt['mutations_rejected'])>=3
    sources={str(path.relative_to(ROOT).as_posix()):sha(path) for path in
             (producer,checker,target_path,*[SOURCE/'source'/name for name in target['source_sha256']])}
    result={'schema':'quadric-contact-pilot-plot-v1','instance':'quadric-contact-broken','discussion_number':119,
            'sha256_policy':'UTF-8 bytes with CRLF normalized to LF','packet_sha256':sha(packet_path),
            'validation_sha256':sha(receipt_path),'independent_validation_sha256':sha(review_path),
            'source_sha256':sources,'plot_source_sha256':sha(Path(__file__)),
            'row_count':len(rows),'zero_rows_omitted':1287-len(rows),'column_counts':{'Koszul':15,'F_quotient':21},
            'matrix_nonzeros':sum(len(item['entries']) for item in exported),'rhs_nonzeros':len(rhs),
            'coefficient_rank':36,'augmented_rank':37,'smooth_fermat_reduction_mod5_checked':True,'obstruction_row_index':selected,
            'obstruction_monomial':list(rows[selected]),'dual_coefficient':'-7/5','rhs_coefficient':'-5/7',
            'row_order':rows,'column_labels':[{k:v for k,v in item.items() if k!='entries'} for item in exported],
            'scope':'Complete numerator correction space for one fixed quartic denominator: all 15 constant Koszul directions and all 21 quadratic F-quotient directions. Completeness uses the smooth reduction modulo 5 and the regular gradient sequence checked in the independent receipt. Other quartic denominators are not excluded.'}
    return result,np.array([[int(value!=0) for value in row] for row in matrix]),np.array([int(value!=0) for value in vector])


def style(ax):
    ax.set_facecolor(PAPER)
    for side in ('top','right'):ax.spines[side].set_visible(False)
    for side in ('left','bottom'):ax.spines[side].set_color(GRAY)
    ax.tick_params(colors=MUTED,labelsize=10)


def plot(data,matrix,rhs):
    fig=plt.figure(figsize=(16,11),facecolor=PAPER)
    fig.text(.055,.947,'One coefficient obstructs the tested quartic denominator',fontsize=23,weight='bold')
    fig.text(.055,.909,'quadric-contact-broken · discussion #119   |   Fixed target (F, q = 1, A)   |   Exact rational coefficients',fontsize=12,color=MUTED)
    fig.text(.055,.852,r'$D=4(X_0^2+Y_0^2)X_0Y_0+\frac{5}{7}X_1Y_1(X_2^2+2Y_2^2)$',fontsize=22,color=TEAL)
    fig.text(.055,.802,r'$N_0=X_1^2X_0Y_0\,(-Y_0,0,0,X_0,0,0),\qquad N_0(F)=AD$',fontsize=18)

    ax=fig.add_axes([.07,.282,.443,.451]);style(ax)
    for start,stop,color in ((0,15,TEAL),(15,36,PURPLE)):
        row,col=np.nonzero(matrix[:,start:stop])
        ax.scatter(col+start,row,s=6,marker='s',color=color,lw=0)
    row=np.flatnonzero(rhs);ax.scatter(np.full(len(row),37),row,s=25,marker='D',color=CORAL,lw=0)
    selected=data['obstruction_row_index']
    ax.axhline(selected,color=CORAL,lw=1.3,alpha=.9,zorder=0)
    ax.axvline(14.5,color=GRAY,lw=1);ax.axvline(35.8,color=GRAY,lw=1)
    ax.set_xlim(-.8,38);ax.set_ylim(data['row_count']-.5,-.5)
    ax.set_xticks([0,7,15,25,35,37],['0','7','15','25','35',r'$b$'])
    ax.set_yticks([0,selected,250,400,486]);ax.set_ylabel('active degree-eight coefficient row')
    ax.set_title('Actual support of [M | b]',loc='left',pad=16,fontsize=16,color=TEAL)
    fig.text(.07,.241,'Teal: 15 Koszul columns   ·   Purple: 21 quotient columns   ·   Coral: RHS',fontsize=10.5,color=MUTED)
    fig.text(.07,.217,'487 active rows; 800 all-zero rows omitted. Every correction column is retained.',fontsize=10.5,color=MUTED)

    x=.565
    fig.text(x,.728,'The E2 correction equation',fontsize=17,weight='bold')
    fig.text(x,.676,r'$Mx=b,\qquad b=-B_D(N_0)$',fontsize=20)
    fig.text(x,.628,r'$B_D(N)=D\,\mathrm{div}N-N(D)$',fontsize=18,color=MUTED)
    fig.text(x,.568,'The highlighted monomial is',fontsize=13)
    fig.text(x,.519,r'$m=X_0^2X_1^3X_2^2Y_1$',fontsize=23,color=CORAL)
    fig.text(x,.462,r'$[m]M_j=0\quad(0\leq j<36),\qquad [m]b=-\frac{5}{7}$',fontsize=18)
    fig.text(x,.398,r'$\lambda=-\frac{7}{5}[m]\;:\quad\lambda M=0,\quad\lambda b=1$',fontsize=19,color=CORAL)
    fig.text(x,.339,r'$\operatorname{rank}M=36\quad\longrightarrow\quad\operatorname{rank}[M\mid b]=37$',fontsize=18)
    fig.text(x,.286,'All degree-five numerator corrections and\nquadratic quotients miss this coefficient.',fontsize=13,color=MUTED)

    ax=fig.add_axes([.07,.152,.855,.038]);ax.set_xlim(-.5,37.8);ax.set_ylim(-.5,.5);ax.axis('off')
    for j in range(36):
        color=TEAL if j<15 else PURPLE
        ax.add_patch(plt.Rectangle((j-.42,-.4),.84,.8,facecolor=PAPER,edgecolor=color,lw=1))
        ax.text(j,0,'0',ha='center',va='center',fontsize=9,color=MUTED)
    ax.add_patch(plt.Rectangle((37-.42,-.4),.84,.8,facecolor=CORAL,edgecolor=CORAL))
    ax.text(37,0,'−5/7',ha='center',va='center',fontsize=9,color='white')
    fig.text(.07,.192,'Exact coefficient row [m]:',fontsize=11,color=CORAL)
    fig.text(.07,.109,'15 constant Koszul corrections + all 21 quadratic quotient monomials; no parity restriction was imposed.',fontsize=12,color=MUTED)
    fig.text(.07,.073,'This excludes every allowed numerator for the displayed D. Other quartic denominators remain untested here.',fontsize=12)
    fig.text(.07,.043,'Completeness uses the regular gradient sequence, certified by smooth reduction modulo 5.',fontsize=10.5,color=MUTED)
    fig.text(.945,.017,'quadric-contact-broken · discussion #119',ha='right',fontsize=10,color=TEAL)
    OUT.mkdir(parents=True,exist_ok=True)
    stem=OUT/'quadric-contact-obstruction'
    fig.savefig(stem.with_suffix('.png'),dpi=160,facecolor=PAPER)
    svg=stem.with_suffix('.svg');fig.savefig(svg,facecolor=PAPER,metadata={'Date':None})
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8',newline='\n')
    plt.close(fig)


def main():
    if not __debug__:raise RuntimeError('Run without -O so exact checks remain active.')
    data,matrix,rhs=check_packet()
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'text.color':INK,
        'axes.labelcolor':INK,'svg.fonttype':'none','svg.hashsalt':'quadric-contact-pilot-v1'})
    plot(data,matrix,rhs)
    (OUT/'plot-data.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':'PASS','instance':data['instance'],'shape':[data['row_count'],36],
                      'ranks':[36,37],'single_obstruction_row':data['obstruction_row_index']}))


if __name__=='__main__':main()
