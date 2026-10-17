#!/usr/bin/env python3
"""Independent physical substitution audit of the higher evaluation jets.

Reuses only the frozen independent checker's Fraction polynomial arithmetic.
It imports no producer or CAS. An invertible constant Jacobian and exact
substitution verify the unique formal jet without reusing discovery equations.
"""
from pathlib import Path
from fractions import Fraction as Q
import json
import re
import check_cyclic_fano_unfolding as I

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/cyclic-fano-higher-unfolding'
SOURCE=ROOT/'results/cyclic-fano-curve'
ZERO,ONE=I.ZERO,I.ONE
ca,cn,cm,ci=I.ca,I.cn,I.cm,I.ci
add,scale=I.add,I.scale

def truncate(poly,order):return {m:c for m,c in poly.items()if sum(m)<=order}
def derivative(poly,index):
    out={}
    for m,c in poly.items():
        if m[index]:
            n=list(m);n[index]-=1;out[tuple(n)]=cm(c,(Q(m[index]),Q(0)))
    return out
def substitute_b(poly,center,order):
    out={}
    for (a,b,c),coefficient in poly.items():
        assert c==0
        term=I.multiply({(0,b,0):coefficient},I.power(center,a,I.ZLOCAL,order),order)
        out=add(out,term)
    return out
def raw_G():
    values={};key=None
    for line in (SOURCE/'source/instance.rec').read_text(encoding='utf-8').splitlines():
        match=re.match(r'^(q|F|A):\s*(.*)$',line)
        if match:key=match[1];values[key]=match[2]
        elif key and line.startswith('  '):values[key]+=' '+line.strip()
        else:key=None
    assert I.sha(SOURCE/'source/instance.rec')=='d99d10c84d25dc5def72cd7a9a17e5d022e18f562660c8e33bf106675b4a418c'
    assert values==I.load(SOURCE/'target.json')['target']and values['q']=='1'
    G={}
    for mon,c in I.parse(values['F']).items():
        assert mon[2]%3==0;new=list(mon);new[2]//=3;G[tuple(new)]=c
    return G
def equations(G,b,U,unknown):
    z,k,l,m,C,E,h=unknown
    return I.coefficient_equations(G,b,U,h,z,[C,E,k,l,m])
def valuation(poly):return min((sum(m)for m in poly),default=None)
def pair_at(poly,n):return I.strings(poly.get((0,n,0),ZERO))

def decode_any(terms,n):
    out={}
    for term in terms:
        mon=tuple(term['powers']);coefficient=tuple(map(Q,term['coefficient']))
        assert len(mon)==n and all(type(x)is int and x>=0 for x in mon)
        assert len(coefficient)==2 and coefficient!=ZERO and mon not in out
        out[mon]=coefficient
    return out

def compose(poly,images,n):
    out={};zero=(0,)*n
    for mon,c in poly.items():
        term={zero:c}
        for exponent,p in zip(mon,images):term=I.multiply(term,I.power(p,exponent,zero))
        out=add(out,term)
    return out

def check_axis(path,G):
    packet=I.load(path);order=packet['jet_total_order'];direction=packet['parameter_direction']
    assert packet['schema']=='cyclic-fano-higher-unfolding-v1'and direction in('X0','Y0')
    assert packet['instance']=='cyclic-triple-fano'and packet['source_commit']=='d96911d725077e66a8f10848908be01a643b1714'
    assert packet['producer_sha256']==I.sha(ROOT/'experiments/cyclic_fano_higher_unfolding.py')
    assert packet['arithmetic_dependency_sha256']==I.sha(ROOT/'experiments/cyclic_fano_unfolding.py')
    assert packet['fixed_target_manifest_sha256']==I.sha(SOURCE/'target.json')
    assert packet['jet_variables']==['b','U','unused']and packet['unknown_order']==['z','k','l','m','C','E','h']
    assert (direction,order)in(('X0',12),('Y0',8))
    I.ORDER=order;I.DIRECTION=0 if direction=='X0'else 3
    b={(1,0,0):ONE};U={(0,1,0):ONE}
    unknown=[I.decode(p)for p in packet['unknown_jets']]
    assert len(unknown)==7 and all(m[2]==0 and sum(m)>0 for poly in unknown for m in poly)
    residual=equations(G,b,U,unknown)
    assert len(residual)==7 and all(not p for p in residual)
    columns=[]
    for j in range(7):
        probe=[{}for _ in range(7)];probe[j]=b
        columns.append([p.get((1,0,0),ZERO)for p in equations(G,{},{},probe)])
    jac=[list(row)for row in zip(*columns)];_,det=I.inverse(jac)
    assert [[I.strings(x)for x in row]for row in jac]==packet['constant_implicit_jacobian']
    assert I.strings(det)==packet['constant_implicit_jacobian_determinant']==['-135000/2401','0']
    assert [s['degree']for s in packet['hensel_stages']]==list(range(1,order+1))
    for stage in packet['hensel_stages']:
        assert len(stage['corrections'])==7
        for poly,correction in zip(unknown,stage['corrections']):assert I.decode(correction)==I.homogeneous(poly,stage['degree'])
    H=unknown[-1];assert H==I.decode(packet['evaluation_graph_h'])
    assert valuation(H)==3
    alpha=H[(3,0,0)];assert alpha==(Q(5,6),Q(8,35))
    Hb=derivative(H,0);Hbb=derivative(Hb,0);Hbbb=derivative(Hbb,0)
    center={};pivot=cm((Q(6),Q(0)),alpha)
    for n in range(1,order-1):
        residual=I.homogeneous(substitute_b(Hbb,center,order),n)
        center=add(center,scale(residual,cn(ci(pivot))))
    assert center==I.decode(packet['inflection_center_b'])and packet['inflection_center_order']==order-2
    assert not truncate(substitute_b(Hbb,center,order),order-2)
    height=truncate(substitute_b(H,center,order),order)
    linear=truncate(substitute_b(Hb,center,order),order-1)
    cubic=scale(truncate(substitute_b(Hbbb,center,order),order-3),(Q(1,6),Q(0)))
    assert packet['center_height_valid_order']==order and height==I.decode(packet['center_height'])
    assert packet['centered_linear_valid_order']==order-1 and linear==I.decode(packet['centered_linear_coefficient'])
    assert packet['centered_cubic_valid_order']==order-3 and cubic==I.decode(packet['centered_cubic_coefficient'])
    assert all(sum(m)>=2 for m in linear)
    # H starts in degree3. Therefore Hb at the true center starts in degree2,
    # validating height through order n despite the center being known to n-2.
    negative=0
    bad=[p.copy()for p in unknown];bad[-1]=add(bad[-1],b)
    negative+=I.rejects(lambda:I.check_equal(equations(G,b,U,bad),[{}for _ in range(7)]))
    bad_center=add(center,U)
    negative+=I.rejects(lambda:I.check_equal(truncate(substitute_b(Hbb,bad_center,order),order-2),{}))
    negative+=I.rejects(lambda:I.check_equal(add(linear,{(0,2,0):ONE}),truncate(substitute_b(Hb,center,order),order-1)))
    receipt={'parameter_direction':direction,'packet_lf_sha256':I.sha(path),'jet_order':order,
             'all_seven_physical_incidence_equations_zero':True,'constant_implicit_jacobian_determinant':I.strings(det),
             'jet_uniqueness':'The nonsingular constant7x7 Jacobian and exact truncated substitution identify the unique implicit formal solution through this order.',
             'inflection_center':I.sparse(center),'center_valid_order':order-2,
             'center_height':I.sparse(height),'height_valid_order':order,
             'centered_linear':I.sparse(linear),'linear_valid_order':order-1,
             'centered_cubic':I.sparse(cubic),'cubic_valid_order':order-3,
             'precision_argument':'If the true inflection center differs by O(U^(n-1)), stationarity of Hb makes its centered value accurate through n-1. Since H has no terms below degree3, Hb at the center is O(U^2), so the height error begins at n+1. Three derivatives of H give its cubic coefficient only through n-3.',
             'negative_controls_rejected':negative}
    if direction=='X0':
        assert not height and not linear
        receipt['conclusion']='Centered height vanishes through12 and linear coefficient through11. These finite vanishings do not establish exact persistent ramification or a branch/support equation.'
    else:
        # Verify the leading cubic and its discriminant by direct coefficient
        # identities. This is a weighted leading model, not a Weierstrass claim.
        H3=I.homogeneous(H,3)
        a=H3.get((3,0,0),ZERO);d=H3.get((2,1,0),ZERO)
        e=H3.get((1,2,0),ZERO);f=H3.get((0,3,0),ZERO)
        s1=cn(cm(d,ci(cm((Q(3),Q(0)),a))))
        lam=ca(e,cn(cm(cm(d,d),ci(cm((Q(3),Q(0)),a)))))
        mu=ca(ca(f,cn(cm(cm(d,e),ci(cm((Q(3),Q(0)),a))))),
              cm((Q(2,27),Q(0)),cm(cm(cm(d,d),d),cm(ci(a),ci(a)))))
        assert center.get((0,1,0),ZERO)==s1
        assert linear.get((0,2,0),ZERO)==lam!=(Q(0),Q(0))
        assert height.get((0,3,0),ZERO)==mu
        assert lam==(Q(28225,592722),Q(4955,461006))
        assert mu==(Q(3866303375,1229617792494),Q(-341757500,29276614107))
        critical_discriminant=cn(cm((Q(12),Q(0)),cm(a,lam)))
        assert critical_discriminant!=ZERO
        # Coefficients in monomials (h^2,h*U^3,U^6) after clearing a^3.
        model_disc=[cn(cm((Q(27),Q(0)),a)),cm((Q(54),Q(0)),cm(a,mu)),
                    cn(ca(cm((Q(4),Q(0)),cm(cm(lam,lam),lam)),cm((Q(27),Q(0)),cm(a,cm(mu,mu)))))]
        receipt['leading_cubic']={'H3':I.sparse(H3),'a':I.strings(a),'centering_slope':I.strings(s1),
            'lambda2':I.strings(lam),'mu3':I.strings(mu),
            'model_discriminant_monomials':['h^2','h*U^3','U^6'],'model_discriminant_coefficients':list(map(I.strings,model_disc)),
            'equation':'-27*a*(h-mu3*U^3)^2-4*lambda2^3*U^6',
            'critical_quadratic_discriminant':I.strings(critical_discriminant)}
        receipt['local_geometric_consequence']='Put b=U*t. The critical equation Hb/U^2 has two simple roots at U=0, since lambda2 is nonzero. The implicit function theorem gives two actual analytic critical branches. Their target images are h=c_plus*U^3+O(U^4) and h=c_minus*U^3+O(U^4), with c_plus!=c_minus, hence contact order3. This conclusion concerns the selected local Y0 surface.'
        receipt['limits']='The displayed discriminant is only the leading weighted branch equation. Its extension/homogenization off this target surface is a candidate construction, not a proof of global support.'
    return receipt

def check_candidates(axes):
    path=OUT/'candidates.json';packet=I.load(path)
    assert packet['schema']=='cyclic-fano-higher-unfolding-candidates-v1'
    assert packet['producer_sha256']==I.sha(ROOT/'experiments/cyclic_fano_higher_unfolding.py')
    assert packet['arithmetic_dependency_sha256']==I.sha(ROOT/'experiments/cyclic_fano_unfolding.py')
    assert packet['source_jet_packet_sha256']=={x['parameter_direction']:x['packet_lf_sha256']for x in axes}
    assert packet['fixed_target_manifest_sha256']==I.sha(SOURCE/'target.json')
    prior_path=ROOT/'results/cyclic-fano-unfolding/unfolding.json'
    assert packet['prior_full_T1_packet_sha256']==I.sha(prior_path)
    prior=I.load(prior_path)
    t1=[[tuple(map(Q,c))for c in row]for row in prior['full_T1_matrix']]
    assert all(row[0]==row[1]==ZERO and row[2]==cm((Q(0),Q(-1)),row[3])for row in t1)
    assert any(row[3]!=ZERO for row in t1)
    assert packet['variables']==['X0','X1','Z','Y0','Y1','Y2']and packet['weights']==[1,1,3,1,1,1]
    lead=axes[1]['leading_cubic'];H3=decode_any(lead['H3'],3)
    h3={(m[0],m[1]):c for m,c in H3.items()}
    assert packet['leading_graph_variables']==['b','V']and decode_any(packet['leading_graph_cubic'],2)==h3
    a,d,e,f=[h3.get(m,ZERO)for m in ((3,0),(2,1),(1,2),(0,3))]
    assert packet['leading_graph_coefficient_order']==['b^3','b^2*V','b*V^2','V^3']
    assert packet['leading_graph_coefficients']==list(map(I.strings,[a,d,e,f]))
    lam=tuple(map(Q,lead['lambda2']));mu=tuple(map(Q,lead['mu3']))
    gamma=cm((Q(4,27),Q(0)),cm(cm(cm(lam,lam),lam),ci(a)))
    assert packet['inflection_shift_linear']==lead['centering_slope']
    assert packet['centered_linear_leading']==I.strings(lam)and packet['center_height_leading']==I.strings(mu)
    assert packet['leading_branch_gamma']==I.strings(gamma)and gamma!=ZERO
    # The ordinary cubic discriminant, normalized by -27*a^2, must equal
    # the proposed leading branch equation. This calculation uses H3 directly.
    z2=(0,0);A={z2:a};B={(1,0):d};C={(2,0):e};D=add({(3,0):f},{(0,1):cn(ONE)})
    mul=I.multiply
    disc=add(add(mul(mul(B,B),mul(C,C)),scale(mul(A,I.power(C,3,z2)),(Q(-4),Q(0)))),
             add(add(scale(mul(I.power(B,3,z2),D),(Q(-4),Q(0))),scale(mul(mul(A,A),mul(D,D)),(Q(-27),Q(0)))),
                 scale(mul(mul(A,B),mul(C,D)),(Q(18),Q(0)))))
    branch=add(I.power(add({(0,1):ONE},{(3,0):cn(mu)}),2,z2),{(6,0):gamma})
    assert scale(disc,ci(cm((Q(-27),Q(0)),cm(a,a))))==branch
    assert packet['leading_branch_variables']==['V','h']and decode_any(packet['leading_branch_equation'],2)==branch
    assert packet['local_branch_contact_order']==3 and packet['critical_value_leading_coefficients_are_distinct']is True
    negative=packet['X0_negative_result']
    assert negative['verified']is True and negative['center_height_zero_through_order']==12 and negative['centered_linear_zero_through_order']==11
    assert not axes[0]['center_height']and not axes[0]['centered_linear']
    z6=(0,)*6
    variables=[{tuple(int(i==j)for i in range(6)):ONE}for j in range(6)]
    X0,X1,Z,Y0,Y1,Y2=variables
    T=add(scale(Y2,(Q(0),Q(-1))),scale(X1,cn(ONE)))
    Vh=add(Y0,scale(X1,(Q(0),Q(-1))))
    cubic=add(mul(T,I.power(X1,2,z6)),scale(I.power(Vh,3,z6),cn(mu)))
    sextic=add(mul(cubic,cubic),scale(I.power(Vh,6,z6),gamma))
    expected=[T,cubic,sextic];degrees=[1,3,6]
    assert [x['id']for x in packet['candidates']]==['full-tangent-linear','Y0-center-cubic','Y0-leading-branch-sextic']
    assert len(packet['candidates'])==3
    # Restriction X1=1,Y0=i+V,Y1=1+h,Y2=i(1+h) gives exactly
    # h, h-mu*V^3 and the leading branch model, with no jet truncation.
    one={z2:ONE};V={(1,0):ONE};h={(0,1):ONE}
    images=[{},one,{},add({z2:I.II},V),add(one,h),scale(add(one,h),I.II)]
    restrictions=[h,add(h,{(3,0):cn(mu)}),branch]
    for candidate,want,degree,restriction in zip(packet['candidates'],expected,degrees,restrictions):
        actual=decode_any(candidate['quotient_denominator'],6)
        assert actual==want and candidate['degree']==degree
        assert all(sum(w*x for w,x in zip(packet['weights'],m))==degree for m in actual)
        assert compose(actual,images,2)==restriction
    # Full target tangent chart: Y2=i(1+h)+W gives T=h-iW.
    z3=(0,0,0);one3={z3:ONE};h3local={(0,1,0):ONE};W={(0,0,1):ONE};V3={(1,0,0):ONE}
    fullimages=[{},one3,{},add({z3:I.II},V3),add(one3,h3local),add(scale(add(one3,h3local),I.II),W)]
    assert compose(T,fullimages,3)==add(h3local,scale(W,(Q(0),Q(-1))))
    mutations=0
    mutations+=I.rejects(lambda:I.check_equal(add(branch,{(0,2):ONE}),scale(disc,ci(cm((Q(-27),Q(0)),cm(a,a))))))
    mutations+=I.rejects(lambda:I.check_equal(add(cubic,X1),expected[1]))
    mutations+=I.rejects(lambda:I.check_equal(compose(add(Y1,scale(X1,cn(ONE))),fullimages,3),compose(T,fullimages,3)))
    return {'packet_lf_sha256':I.sha(path),'prior_full_T1_packet_lf_sha256':I.sha(prior_path),
            'leading_graph_coefficients_checked':True,'ordinary_cubic_discriminant_reconstructed':True,
            'leading_branch_gamma':I.strings(gamma),'full_target_covector_checked':'h-iW',
            'homogeneous_candidate_degrees':degrees,'three_exact_surface_restrictions_checked':True,
            'negative_controls_rejected':mutations,
            'geometric_scope':'Two genuine analytic critical-value curves have contact order3 on the chosen target surface. The displayed polynomial is their leading weighted equation only. Off-surface extension and homogenization define guesses, not proved branch/support divisors.'}

def main():
    assert __debug__,'Run without -O'
    G=raw_G();axes=[check_axis(OUT/name,G)for name in ('unfolding-X0-order12.json','unfolding-Y0-order8.json')]
    candidates=check_candidates(axes)
    receipt={'schema':'cyclic-fano-higher-unfolding-independent-v1','status':'PASS',
             'checker_lf_sha256':I.sha(Path(__file__)),
             'independent_arithmetic_dependency_lf_sha256':I.sha(Path(I.__file__)),
             'source_instance_lf_sha256':I.sha(SOURCE/'source/instance.rec'),'axes':axes,'candidate_construction':candidates,
             'arithmetic':'Python standard-library Fraction pairs and independent raw-source physical composition; no producer or CAS import',
             'negative_controls_rejected':sum(a['negative_controls_rejected']for a in axes)+candidates['negative_controls_rejected'],
             'limits':'No exact global branch polynomial, support divisor, rational primitive or Lean certificate is established.'}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'independent-validation.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':'PASS','orders':[12,8],'physical_equations':14,'negative_controls':receipt['negative_controls_rejected']}))

if __name__=='__main__':main()
