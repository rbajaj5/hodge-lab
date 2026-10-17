#!/usr/bin/env python3
"""Independent exact audit of seven fixed polar-denominator directions.

The source polynomial and all physical correction columns are rebuilt using
only standard-library arithmetic from the earlier independent checker.
The reflection-even remainder supplies an additional direct obstruction.
"""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations
import json
import check_cyclic_fano_guided_denominators as A

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/cyclic-fano-branch-polars'
SOURCE=ROOT/'results/cyclic-fano-curve'
BASE=(0,1,3,4,5)
ZERO,ONE=A.ZERO,A.ONE
ca,cn,cm=A.ca,A.cn,A.cm
add,mul,scale=A.add,A.mul,A.scale
derivative=A.derivative
EXPECTED_DIRECTIONS=[tuple(int(i==j)for i in range(5))for j in range(5)]+[(1,0,1,0,0),(0,1,0,1,0)]
NAMES=['polar_'+s for s in ('X0','X1','Y0','Y1','Y2','X0_plus_Y0','X1_plus_Y1')]
DEPS=('cyclic_fano_branch_products.py','cyclic_fano_guided_denominators.py','cyclic_fano_transfer.py','quadric_contact_pilot.py','cyclic_fano_branch_compact.py')

def directional(poly,direction):
    return A.total(scale(derivative(poly,i),(Q(v),Q(0)))for i,v in zip(BASE,direction)if v)

def split_G(G):
    assert G[(0,0,2,0,0,0)]==ONE
    assert all(m[2]<=2 for m in G)
    Qpoly={m[:2]+(0,)+m[3:]:c for m,c in G.items()if m[2]==1}
    H={m:c for m,c in G.items()if m[2]==0}
    Delta=add(mul(Qpoly,Qpoly),scale(H,(Q(-4),Q(0))))
    assert Delta and all(m[2]==0 and sum(m)==6 for m in Delta)
    return Qpoly,H,Delta

def even_projection(poly,Qpoly,H):
    pieces=[{}for _ in range(3)]
    for m,c in poly.items():
        assert m[2]<=2
        n=m[:2]+(0,)+m[3:];pieces[m[2]][n]=c
    quadratic=add(scale(mul(Qpoly,Qpoly),(Q(1,2),Q(0))),scale(H,cn(ONE)))
    return add(add(pieces[0],scale(mul(Qpoly,pieces[1]),(Q(-1,2),Q(0)))),mul(quadratic,pieces[2]))

def canonical_remainder(poly,Qpoly,H):
    pieces=[{}for _ in range(3)]
    for m,c in poly.items():
        assert m[2]<=2
        pieces[m[2]][m[:2]+(0,)+m[3:]]=c
    first=add(pieces[0],scale(mul(H,pieces[2]),cn(ONE)))
    linear=add(pieces[1],scale(mul(Qpoly,pieces[2]),cn(ONE)))
    Z={(0,0,1,0,0,0):ONE}
    return add(first,mul(Z,linear))

def physical(direction,G,beta):
    assert direction in EXPECTED_DIRECTIONS
    Qpoly,H,Delta=split_G(G)
    E=directional(Delta,direction);Qv=directional(Qpoly,direction)
    assert E and all(m[2]==0 and sum(m)==5 for m in E)
    J=derivative(G,2)
    assert E==add(scale(mul(J,Qv),(Q(2),Q(0))),scale(directional(G,direction),(Q(-4),Q(0))))
    field=[{}for _ in range(6)]
    for i,v in zip(BASE,direction):field[i]=scale(beta,(Q(-4*v),Q(0)))
    field[2]=scale(mul(beta,Qv),(Q(2),Q(0)))
    assert A.contraction(field,G)==mul(beta,E)
    pushed_t=add(scale(field[2],(Q(2),Q(0))),A.total(mul(derivative(Qpoly,i),field[i])for i in BASE))
    assert not pushed_t
    residual=A.B(E,field)
    residual_formula=scale(add(mul(beta,directional(E,direction)),scale(mul(directional(beta,direction),E),cn(ONE))),(Q(4),Q(0)))
    assert residual==residual_formula and residual
    assert all(m[2]==0 and sum(m)==8 for m in residual)
    columns=[];labels=[]
    grad=[derivative(G,i)for i in range(6)]
    for i,j in combinations(range(6),2):
        for m in A.monomials(5+A.WEIGHTS[i]+A.WEIGHTS[j]-8):
            correction=[{}for _ in range(6)]
            correction[i]=mul({m:ONE},grad[j]);correction[j]=scale(mul({m:ONE},grad[i]),cn(ONE))
            assert A.contraction(correction,G)=={}
            columns.append(A.B(E,correction));labels.append(('Koszul',i,j,m))
    assert len(columns)==25
    for m in A.monomials(2):
        columns.append(scale(mul(G,{m:ONE}),cn(ONE)));labels.append(('G_quotient',m))
    assert len(columns)==40
    assert all(not even_projection(p,Qpoly,H)for p in columns)
    rhs=scale(residual,cn(ONE))
    assert even_projection(rhs,Qpoly,H)==rhs
    # A separate explicit dual is obtained by selecting a nonzero coefficient
    # after the exact even projection. No matrix elimination is needed.
    row=max(rhs);normalization=A.I.ci(rhs[row])
    dual={}
    for m in A.monomials(8):
        p=even_projection({m:ONE},Qpoly,H);c=cm(normalization,p.get(row,ZERO))
        if c!=ZERO:dual[m]=c
    assert A.pairing(dual,rhs)==ONE and all(A.pairing(dual,p)==ZERO for p in columns)
    assert dual
    return {'direction':direction,'E':E,'field':field,'residual':residual,'rhs':rhs,
            'columns':columns,'labels':labels,'independent_even_dual':dual,
            'selected_even_coefficient':row,'Q':Qpoly,'H':H,'Delta':Delta}

def check_case(name,direction,F,Apoly,G,beta):
    path=OUT/(name+'.json');packet=A.I.load(path)
    bindings={'producer_sha256':A.I.sha(ROOT/'experiments/cyclic_fano_branch_polars.py'),
              'dependencies':{s:A.I.sha(ROOT/'experiments'/s)for s in DEPS},
              'source_instance_sha256':A.I.sha(SOURCE/'source/instance.rec'),
              'source_commit':'d96911d725077e66a8f10848908be01a643b1714'}
    assert packet['schema']=='cyclic-fano-branch-polars-v1'and packet['id']==name
    for k,v in bindings.items():assert packet[k]==v
    attempt_path=OUT/('attempt-'+name+'.json');attempt=A.I.load(attempt_path)
    assert attempt['id']==name and attempt['direction']==list(direction)and attempt['bindings']==bindings
    assert attempt['status']=='completed'and attempt['returncode']==0 and attempt['time_limit_seconds']==60
    assert packet['direction']==list(direction)and packet['degree']==5
    assert packet['direction_variables']==['X0','X1','Y0','Y1','Y2']
    assert packet['weighted_variables']==['X0','X1','Z','Y0','Y1','Y2']
    exact=physical(direction,G,beta)
    for key,poly in [('Delta',exact['Delta']),('denominator',exact['E']),('residual',exact['residual']),('rhs',exact['rhs'])]:
        assert A.decode(packet[key])==poly
    assert [A.decode(p)for p in packet['particular']]==exact['field']
    assert len(packet['columns'])==25
    physical_map={(label[1],label[2],label[3]):col for label,col in zip(exact['labels'][:25],exact['columns'][:25])}
    seen=set()
    for saved in packet['columns']:
        i,j=saved['label']['coordinates'];m=tuple(saved['label']['powers']);key=(i,j,m)
        assert key in physical_map and key not in seen;seen.add(key);column=physical_map[key]
        assert A.decode(saved['polynomial'])==canonical_remainder(column,exact['Q'],exact['H'])
    assert seen==set(physical_map)
    assert packet['complete_Koszul_directions']==25 and packet['quotient_dimension_eliminated']==15
    assert packet['full_projected_numerator_dimension']==sum(len(A.monomials(5+w-2))for w in A.WEIGHTS)==621
    active=set(exact['rhs'])
    for col in exact['columns'][:25]:active.update(canonical_remainder(col,exact['Q'],exact['H']))
    assert packet['active_rows']==len(active)
    assert packet['ambient_remainder_rows']==sum(m[2]<2 for m in A.monomials(8))==621
    dual=A.decode(packet['dual']);assert all(m[2]<2 and sum(w*x for w,x in zip(A.WEIGHTS,m))==8 for m in dual)
    assert A.pairing(dual,exact['rhs'])==ONE
    for col in exact['columns']:assert A.pairing(dual,canonical_remainder(col,exact['Q'],exact['H']))==ZERO
    lifted_dual={}
    for m in A.monomials(8):
        c=A.pairing(dual,canonical_remainder({m:ONE},exact['Q'],exact['H']))
        if c!=ZERO:lifted_dual[m]=c
    assert A.pairing(lifted_dual,exact['rhs'])==ONE
    assert all(A.pairing(lifted_dual,col)==ZERO for col in exact['columns'])
    assert packet['status']=='excluded'
    assert packet['corrected_field']is None and packet['quotient']is None and packet['correction_coefficients']is None
    # Verify both identities on the actual six ordinary coordinates upstairs.
    N=A.lift(exact['field']);D=A.pullback(exact['E'])
    delta={(0,0,2,0,0,0):(Q(3),Q(0))}
    assert A.contraction(N,F)==mul(Apoly,D)
    assert A.B(D,N)==mul(delta,A.pullback(exact['residual']))
    mutations=0
    mutations+=A.I.rejects(lambda:A.I.check_equal(A.pairing(lifted_dual,scale(exact['rhs'],(Q(2),Q(0)))),ONE))
    changed=exact['columns'][0].copy();row=next(iter(lifted_dual));changed[row]=ca(changed.get(row,ZERO),ONE)
    mutations+=A.I.rejects(lambda:A.I.check_equal(A.pairing(lifted_dual,changed),ZERO))
    badE=add(exact['E'],{(5,0,0,0,0,0):ONE})
    mutations+=A.I.rejects(lambda:A.I.check_equal(A.contraction(exact['field'],G),mul(beta,badE)))
    return {'id':name,'direction':list(direction),'packet_lf_sha256':A.I.sha(path),
            'attempt_lf_sha256':A.I.sha(attempt_path),'status':'excluded','degree':5,
            'E1_exact_lift_checked':True,'Piola_identities_checked_on_original_target':True,
            'particular_residual':A.I.sparse(exact['residual']),
            'raw_Koszul_columns_checked':25,'raw_quotient_columns_checked':15,
            'producer_remainder_dual_terms':len(dual),'producer_dual_on_full_physical_rows':A.I.sparse(lifted_dual),
            'independent_even_projection_dual':A.I.sparse(exact['independent_even_dual']),
            'selected_even_coefficient':list(exact['selected_even_coefficient']),
            'all_40_columns_have_zero_even_projection':True,'nonzero_even_residual_checked':True,
            'rhs_pairing':['1','0'],'negative_controls_rejected':mutations,
            'scope':'This fixed direction only; no claim about all projective polar directions.'}

def main():
    assert __debug__,'Run without -O'
    F,Apoly,G,beta=A.target()
    checks=[check_case(name,direction,F,Apoly,G,beta)for name,direction in zip(NAMES,EXPECTED_DIRECTIONS)]
    receipt={'schema':'cyclic-fano-branch-polars-independent-v1','status':'PASS',
             'checker_lf_sha256':A.I.sha(Path(__file__)),
             'independent_arithmetic_dependencies':{Path(p).name:A.I.sha(Path(p))for p in (A.__file__,A.I.__file__)},
             'source_instance_lf_sha256':A.I.sha(SOURCE/'source/instance.rec'),'checks':checks,
             'complete_scope':'Smooth Fermat reduction of the original F proves the weighted G gradient regular. At degree5 every normal-equation correction is generated by the25 linear-multiplier Koszul fields. All15 degree2 G quotient directions are checked; no numerator or quotient direction is discarded.',
             'reflection_explanation':'E=Delta_v and the particular residual are even in t=2Z+Q. The required even base/base Koszul multiplier would have degree-1. A matching mixed multiplier must be odd in t and would have base degree-2. Hence no compatible homogeneous correction survives reflection projection. Directly, for f=f0+Z*f1+Z^2*f2, the even remainder is f0-Q*f1/2+(Q^2/2-H)*f2. It annihilates every one of the40 physical columns, while each of the seven residuals has a nonzero coefficient.',
             'negative_controls_rejected':sum(c['negative_controls_rejected']for c in checks),
             'limits':'Seven fixed polar denominators are excluded over C. No statement about every polar direction, products/powers of polars, a global support divisor, certificate or Lean proof follows.'}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'independent-validation.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':'PASS','fixed_directions':7,'raw_Koszul_columns':175,'raw_quotient_columns':105,
                      'negative_controls':receipt['negative_controls_rejected']}))

if __name__=='__main__':main()
