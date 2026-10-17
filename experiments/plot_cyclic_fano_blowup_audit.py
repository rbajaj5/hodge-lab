#!/usr/bin/env python3
"""Plot checked blowup-chart equations; numerical root samples are display only."""
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
INPUT=ROOT/'results/cyclic-fano-blowup-audit'
OUT=ROOT/'results/cyclic-fano-blowup-audit-figures'
INK,MUTED,PAPER='#17323B','#53666D','#FAFAF5'
TEAL,PURPLE,CORAL='#166A70','#7967AA','#CA584C'


def sha(path):return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def value(c):return S.Rational(c) if isinstance(c,str) else S.Rational(c[0])+S.I*S.Rational(c[1])
def decode(terms,variables):return S.Poly.from_dict({tuple(t['powers']):value(t['coefficient']) for t in terms},variables)
def encode(poly):return [{'powers':list(m),'coefficient':str(c)} for m,c in poly.terms() if c]


def root_samples(E,H):
    """Bisection samples of exact polynomials, not a certified analytic radius."""
    u,y,z,r,t=S.symbols('u y z r t')
    ef=S.lambdify((y,z),E.as_expr().subs(u,1),'numpy')
    hf=S.lambdify((r,t),H.as_expr().subs(u,1),'numpy')
    result=[]
    for ri in np.linspace(-.1,.1,201):
        lo,hi=-.01,.01
        assert hf(ri,lo)<0<hf(ri,hi)
        for _ in range(60):
            mid=(lo+hi)/2
            if hf(ri,mid)<0:lo=mid
            else:hi=mid
        ti=(lo+hi)/2;yi=ri*ti
        result.append([float(ri),float(ti),float(yi),float(hf(ri,ti)),float(ef(yi,ri))])
    assert max(abs(row[3]) for row in result)<1e-13
    assert max(abs(row[4]) for row in result)<1e-13
    return {'u':1,'columns':['r=z','t','y=r*t','strict_factor_residual','original_E_residual'],
            'samples':result,'algorithm':'60 bisection steps from t in [-0.01,0.01] at 201 r samples in [-0.1,0.1]',
            'scope':'Floating-point display samples of exact equations, not a certified neighborhood or all real/complex branches.'}


def check_data():
    path=INPUT/'packet.json';packet=load(path)
    validation_path=INPUT/'validation.json';validation=load(validation_path)
    review_path=INPUT/'independent-validation.json';review=load(review_path)
    producer=ROOT/'experiments/cyclic_fano_blowup_audit.py'
    checker=ROOT/'experiments/check_cyclic_fano_blowup_audit.py'
    raw=ROOT/'results/cyclic-fano-curve/source/instance.rec'
    assert packet['schema']=='cyclic-fano-blowup-audit-v1'
    assert validation['schema']=='cyclic-fano-blowup-audit-validation-v1'
    assert packet['instance']=='cyclic-triple-fano'
    assert packet['status']==validation['status']==review['status']=='PASS'
    assert packet['producer_sha256']==validation['producer_sha256']==sha(producer)
    assert validation['packet_sha256']==sha(path)
    assert packet['source_instance_sha256']==sha(raw)
    bindings={p.relative_to(ROOT).as_posix():sha(p) for p in (path,validation_path,review_path,producer,checker,raw)}
    for name,digest in packet['dependencies'].items():
        dep=ROOT/'experiments'/name;assert sha(dep)==digest
        bindings[dep.relative_to(ROOT).as_posix()]=digest
    for name,key in (('validation.json','prior_slice_packet_sha256'),
                     ('independent-validation.json','prior_slice_independent_receipt_sha256')):
        dep=ROOT/'results/cyclic-fano-slice-audit'/name
        assert sha(dep)==packet[key] and load(dep)['status']=='PASS'
        bindings[dep.relative_to(ROOT).as_posix()]=sha(dep)
    prior_path=ROOT/'results/cyclic-fano-branch-polars/polar_Y2.json';prior=load(prior_path)
    bindings[prior_path.relative_to(ROOT).as_posix()]=sha(prior_path)
    global_variables=S.symbols('X0 X1 Z Y0 Y1 Y2');X0,X1,Z,Y0,Y1,Y2=global_variables
    u,y,z,r,t=S.symbols('u y z r t');plane=(u,y,z);chart_variables=(u,r,t)
    global_E=decode(prior['denominator'],global_variables)
    assert global_E==decode(packet['global_denominator'],global_variables)
    substitution={X0:1,X1:u,Y0:1,Y1:y,Y2:z}
    E=S.Poly(global_E.as_expr().subs(substitution,simultaneous=True),plane)
    p=S.Poly(decode(prior['particular'][5],global_variables).as_expr().subs(substitution,simultaneous=True),plane)
    assert E==decode(packet['plane_denominator'],plane)
    expected=50*y/S.Integer(49)+50*u*y*y/S.Integer(49)-20*u*y**3/S.Integer(7)+50*y*y*z/S.Integer(49)-40*y*z/S.Integer(7)-24*z**5
    assert E==S.Poly(expected,plane)
    assert p==decode(packet['scalar_numerator'],plane)==S.Poly(-S.Rational(4,3),plane)
    assert E.diff(y).as_expr().subs({y:0,z:0})==S.Rational(50,49)
    assert packet['plane_divisor_smooth_at_origin']
    assert decode(packet['plane_derivative_E_y_at_origin'],plane)==S.Poly(S.Rational(50,49),plane)
    charts={}
    for name,sub in (('y',{y:r,z:r*t}),('z',{y:r*t,z:r})):
        c=packet['charts'][name]
        total=S.Poly(E.as_expr().subs(sub,simultaneous=True),chart_variables)
        strict,remainder=total.div(S.Poly(r,chart_variables));assert remainder.is_zero
        assert total==decode(c['total_transform'],chart_variables)
        assert strict==decode(c['strict_transform'],chart_variables)
        assert min(m[1] for m,coefficient in total.terms())==c['exceptional_multiplicity']==1
        restriction=S.Poly(strict.as_expr().subs(r,0),chart_variables)
        assert restriction==decode(c['restriction_to_exceptional'],chart_variables)
        assert decode(c['scalar_numerator'],chart_variables)==S.Poly(-S.Rational(4,3),chart_variables)
        charts[name]={'total':total,'strict':strict,'exceptional':restriction}
    A,H=charts['y']['strict'],charts['z']['strict']
    assert charts['y']['exceptional']==S.Poly(S.Rational(50,49),chart_variables)
    assert charts['z']['exceptional']==S.Poly(S.Rational(50,49)*t,chart_variables)
    assert S.expand(A.as_expr()-t*H.as_expr().subs({r:r*t,t:1/t},simultaneous=True))==0
    assert S.expand(H.as_expr()-t*A.as_expr().subs({r:r*t,t:1/t},simultaneous=True))==0
    assert H.diff(t).as_expr().subs({r:0,t:0})==S.Rational(50,49)
    assert H.diff(r).as_expr().subs({r:0,t:0})==0
    intersection=packet['exceptional_intersection']
    assert intersection['strict_transform_smooth'] and intersection['crossing_transverse']
    assert intersection['intersection_multiplicity']==1 and intersection['jacobian_r_H_at_origin']=='50/49'
    special=packet['special_axis'];axis=S.Poly(H.as_expr().subs(t,0),chart_variables)
    assert axis==decode(special['strict_transform_restriction'],chart_variables)==S.Poly(-24*r**4,chart_variables)
    assert special['strict_contact_order']==4 and special['exceptional_contact_order']==1
    assert special['total_denominator_order']==5
    lead=special['implicit_strict_branch_leading_term']
    assert lead=={'t_coefficient':'588/25','r_power':4,'error_order':5}
    remainder=S.Poly(H.as_expr().subs(t,S.Rational(588,25)*r**4),chart_variables)
    assert remainder==decode(special['leading_branch_substitution_remainder'],chart_variables)
    assert min(m[1] for m,coefficient in remainder.terms())==5
    for key in ('denominator_exceptional','denominator_strict_transform','scalar_pole_exceptional','scalar_pole_strict_transform'):
        assert packet['local_divisor_orders'][key]==1
    assert validation['negative_controls_rejected']==6 and validation['axis_orders']==[1,5]
    assert validation['both_chart_identities_checked'] and validation['overlap_checked']
    # The review's exact comparison and source bindings are checked below;
    # root samples only illustrate these algebraic conclusions.
    check_review(review,path,checker,raw,bindings,plane,chart_variables,E,p,charts)
    return {'schema':'cyclic-fano-blowup-audit-plot-v1','instance':'cyclic-triple-fano','discussion_number':112,
            'sha256_policy':'File bytes with CRLF normalized to LF','source_sha256':bindings,'plot_source_sha256':sha(Path(__file__)),
            'plane_variables':list(map(str,plane)),'plane_denominator':encode(E),'scalar_numerator':encode(p),
            'chart_variables':list(map(str,chart_variables)),
            'charts':{name:{key:encode(poly) for key,poly in items.items()} for name,items in charts.items()},
            'leading_strict_branch':lead,'display_roots':root_samples(E,H),
            'scope':'Exact normal-plane blowup and scalar p/E pullback only; not a transformed full vector field, certificate, full-fourfold blowup, pole removal or phase transition.'}


def check_review(review,path,checker,raw,bindings,plane,chart_variables,E,p,charts):
    assert review['schema']=='cyclic-fano-blowup-audit-independent-v1'
    assert review['packet_lf_sha256']==sha(path)
    assert review['primary_validation_lf_sha256']==sha(INPUT/'validation.json')
    assert review['checker_lf_sha256']==sha(checker)
    assert review['source_instance_lf_sha256']==sha(raw)
    for name,digest in review['independent_arithmetic_dependencies'].items():
        dep=ROOT/'experiments'/name;assert sha(dep)==digest
        bindings[dep.relative_to(ROOT).as_posix()]=digest
    for key in ('both_chart_factorizations_checked','both_overlap_identities_checked',
                'original_plane_divisor_smooth','strict_transform_transverse_to_exceptional'):
        assert review[key]
    assert review['exceptional_multiplicity']==1
    assert review['implicit_strict_branch_leading_coefficient']=='588/25'
    assert review['implicit_strict_branch_order']==4 and review['implicit_strict_branch_remainder_order']==5
    assert review['axis_scalar_pole_orders']==[1,5] and review['negative_controls_rejected']==8
    assert decode(review['scalar_numerator'],plane)==p
    u,r,t=chart_variables;H=charts['z']['strict']
    assert decode(review['strict_transform_at_special_axis'],chart_variables)==S.Poly(-24*r**4,chart_variables)
    unit=S.Poly(S.cancel((H.as_expr()+24*r**4)/t),chart_variables)
    assert decode(review['implicit_branch_unit'],chart_variables)==unit
    assert unit.as_expr().subs({r:0,t:0})==S.Rational(50,49)


def draw(data):
    fig=plt.figure(figsize=(16,12),facecolor=PAPER)
    fig.text(.055,.954,'Blowing up the normal plane separates two sources of pole order',fontsize=23,weight='bold')
    fig.text(.055,.923,'cyclic-triple-fano · discussion #112   |   The same previously excluded Y₂ polar, on X₀ = Y₀ = 1 and X₁ = u',fontsize=12,color=MUTED)
    fig.text(.055,.878,r'$y=Y_1,\quad z=Y_2,\qquad E=\partial_{Y_2}\Delta,\qquad p=P^0_{Y_2}=-\frac{4}{3}$',fontsize=19,color=TEAL)
    fig.text(.055,.838,r'$E(y,z)=\frac{50}{49}y+\frac{50}{49}uy^2-\frac{20}{7}uy^3+\frac{50}{49}y^2z-\frac{40}{7}yz-24z^5$',fontsize=18)
    a=fig.add_axes([.075,.456,.38,.314],facecolor=PAPER)
    b=fig.add_axes([.57,.456,.365,.314],facecolor=PAPER)
    rows=np.array(data['display_roots']['samples']);r,t,y=rows[:,0],rows[:,1],rows[:,2]
    for ax in (a,b):
        ax.spines[['top','right']].set_visible(False)
        ax.spines[['left','bottom']].set_color(MUTED)
        ax.tick_params(colors=MUTED,labelsize=10)
        ax.grid(color=INK,alpha=.09)
    a.axhline(0,color=PURPLE,ls='--',lw=1.8,label='selected axis y = 0')
    a.axvline(0,color=MUTED,lw=1,alpha=.4)
    a.plot(r,y,color=TEAL,lw=2.8,label='E(y,z) = 0, numerical samples')
    a.scatter([0],[0],s=42,color=CORAL,zorder=5)
    a.set(xlabel='z',ylabel='y',xlim=(-.105,.105),ylim=(-.00065,.00065))
    a.set_title('Before blowup: a smooth divisor',loc='left',fontsize=16,color=INK,pad=12)
    a.ticklabel_format(axis='y',style='sci',scilimits=(0,0),useMathText=True)
    a.legend(loc='upper left',fontsize=10,frameon=False)
    a.text(.035,.23,r'$E_y(0,0)=50/49\ne0$',transform=a.transAxes,fontsize=13)
    a.text(.035,.11,r'$E(0,z)=-24z^5$',transform=a.transAxes,fontsize=14,color=PURPLE)
    b.axhline(0,color=PURPLE,ls='--',lw=1.8,label='selected axis t = 0')
    b.axvline(0,color=CORAL,lw=2.4,label='exceptional divisor r = 0')
    b.plot(r,t,color=TEAL,lw=2.8,label='strict transform H(r,t) = 0')
    b.scatter([0],[0],s=44,color=CORAL,zorder=6)
    b.scatter([0],[.0055],s=45,color=INK,zorder=5)
    b.annotate('generic exceptional point\nH(0,t) ≠ 0',xy=(0,.0055),xytext=(-.094,.0060),
               fontsize=10,color=INK,arrowprops={'arrowstyle':'-','color':INK})
    b.set(xlabel='r = z',ylabel='t = y/z',xlim=(-.105,.105),ylim=(-.001,.0075))
    b.set_title('After blowup: z = r, y = rt',loc='left',fontsize=16,color=INK,pad=12)
    b.ticklabel_format(axis='y',style='sci',scilimits=(0,0),useMathText=True)
    b.legend(loc='upper right',bbox_to_anchor=(1,1.0),fontsize=9.5,frameon=False)
    fig.text(.075,.405,'Both panels: u = 1; exact equations, floating-point root samples for display. Axes use different scales; no certified radius is claimed.',fontsize=11,color=MUTED)
    fig.text(.055,.358,'Two affine charts cover the exceptional projective line of directions [y : z]',fontsize=16,weight='bold')
    fig.text(.055,.316,r'$U_y:\ y=r,\ z=rt,\quad E=rA,\qquad A(0,t)=\frac{50}{49}$',fontsize=18)
    fig.text(.055,.275,r'$U_z:\ z=r,\ y=rt,\quad E=rH,\qquad H(0,t)=\frac{50}{49}t,\quad H(r,0)=-24r^4$',fontsize=18)
    fig.text(.055,.235,r'$H_t(0,0)=\frac{50}{49},\qquad t(r)=\frac{588}{25}r^4+O(r^5)$',fontsize=18,color=TEAL)
    fig.text(.055,.201,'H = 0 meets r = 0 transversely. The selected axis t = 0 instead has contact order 4 with H = 0.',fontsize=12)
    fig.text(.055,.157,r'Pulled-back scalar coefficient $p/E$: generic exceptional pole order $1$; selected axis order $1+4=5$.',fontsize=15,color=CORAL)
    fig.text(.055,.122,'These are orders of the scalar coefficient, not of a vector field rewritten in a blowup tangent basis.',fontsize=11.5,color=MUTED)
    fig.text(.055,.091,'A local lift to G = 0 requires Δ ≠ 0 at the chosen base point. The pole persists; no certificate or new global exclusion follows.',fontsize=11.5)
    fig.text(.055,.045,'Reading context: Shafarevich, Basic Algebraic Geometry 1, blowup charts; exact packets, independent checks, and sampled coordinates accompany this figure.',fontsize=10,color=MUTED)
    fig.text(.945,.019,'cyclic-triple-fano · discussion #112',ha='right',fontsize=10,color=TEAL)
    OUT.mkdir(parents=True,exist_ok=True);stem=OUT/'cyclic-fano-blowup-audit'
    fig.savefig(stem.with_suffix('.png'),dpi=160,facecolor=PAPER)
    svg=stem.with_suffix('.svg');fig.savefig(svg,facecolor=PAPER,metadata={'Date':None})
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8',newline='\n')
    plt.close(fig)


def main():
    if not __debug__:raise RuntimeError('Run without -O so exact checks remain active.')
    data=check_data()
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'text.color':INK,'axes.labelcolor':INK,
                         'svg.fonttype':'none','svg.hashsalt':'cyclic-fano-blowup-audit-v1'})
    draw(data)
    (OUT/'plot-data.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':'PASS','blowup_charts':2,'selected_scalar_pole_orders':[1,5]}))


if __name__=='__main__':main()
