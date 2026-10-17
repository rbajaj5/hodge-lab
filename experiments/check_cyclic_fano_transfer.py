#!/usr/bin/env python3
"""Independent stdlib audit of the cyclic-character fixed-denominator tests.

Generic sparse Fraction operations come from the independent quartic checker,
not from either producer. Its source hash is recorded in this audit receipt.
"""
from pathlib import Path
from fractions import Fraction as Q
from math import comb
import json
import re
import check_quadric_contact_pilot as independent

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/cyclic-fano-transfer'
SOURCE=ROOT/'results/cyclic-fano-curve'
WEIGHTS=(1,1,3,1,1,1)
SOURCE_HASH='d99d10c84d25dc5def72cd7a9a17e5d022e18f562660c8e33bf106675b4a418c'
add,mul,scale=independent.add,independent.mul,independent.scalar
derivative=independent.derivative

def monomials(n,weights):
    if len(weights)==1:
        return [(n//weights[0],)]if n>=0 and n%weights[0]==0 else []
    return [(k,)+m for k in range(n//weights[0]+1)for m in monomials(n-k*weights[0],weights[1:])]if n>=0 else []
def pullback(poly):
    out={}
    for mon,c in poly.items():
        new=list(mon);new[2]*=3;out[tuple(new)]=c
    return out
def lift(field):
    delta={(0,0,2,0,0,0):Q(3)}
    return [pullback(p)if i==2 else mul(delta,pullback(p))for i,p in enumerate(field)]
def entries(poly,index):return [[index[m],str(c)]for m,c in sorted(poly.items())]
def main():
    assert __debug__,'Run without -O'
    packet=independent.load(OUT/'packet.json')
    assert packet['schema']=='cyclic-fano-character-transfer-v1'and packet['instance']=='cyclic-triple-fano'
    assert packet['source_commit']=='d96911d725077e66a8f10848908be01a643b1714'
    assert packet['producer_sha256']==independent.sha(ROOT/'experiments/cyclic_fano_transfer.py')
    assert packet['arithmetic_dependency_sha256']==independent.sha(ROOT/'experiments/quadric_contact_pilot.py')
    assert packet['source_sha256']==SOURCE_HASH==independent.sha(SOURCE/'source/instance.rec')
    assert packet['weights']==list(WEIGHTS)
    values={};key=None
    for line in (SOURCE/'source/instance.rec').read_text(encoding='utf-8').splitlines():
        match=re.match(r'^(q|F|A):\s*(.*)$',line)
        if match:key=match[1];values[key]=match[2]
        elif key and line.startswith('  '):values[key]+=' '+line.strip()
        else:key=None
    assert values==independent.load(SOURCE/'target.json')['target']and values['q']=='1'
    F,A=map(independent.parse,(values['F'],values['A']))
    G={};density={}
    for mon,c in F.items():
        assert mon[2]%3==0;new=list(mon);new[2]//=3;G[tuple(new)]=c
    for mon,c in A.items():
        assert mon[2]%3==2;new=list(mon);new[2]=(new[2]-2)//3;density[tuple(new)]=c/3
    assert independent.decode(packet['weighted_G'])==G and independent.decode(packet['weighted_density'])==density
    assert density=={(1,0,0,3,0,0):Q(1,3)}
    delta={(0,0,2,0,0,0):Q(3)}
    assert F==pullback(G)and A==mul(delta,pullback(density))
    fermat={tuple(6*int(i==j)for i in range(6)):1 for j in range(6)}
    assert independent.mod5(F)==fermat
    for j in range(6):assert independent.mod5(derivative(F,j))=={tuple(5*int(i==j)for i in range(6)):1}
    expected_candidates={'cyclic_branch_Z':{(0,0,1,0,0,0):Q(1)},
                         'quadratic_branch_2Z_plus_Q':derivative(G,2),
                         'omitted_section_X1_cubed':{(0,3,0,0,0,0):Q(1)}}
    assert {test['candidate']for test in packet['tests']}==set(expected_candidates)and len(packet['tests'])==3
    receipts=[];negative=0;transfer_checks=0
    for test in packet['tests']:
        E=independent.decode(test['weighted_denominator']);D=pullback(E)
        assert E==expected_candidates[test['candidate']]and test['degree']==3
        assert all(sum(w*a for w,a in zip(WEIGHTS,m))==3 for m in E)
        labels=test['numerator_labels']
        expected_labels={(i,m)for i,w in enumerate(WEIGHTS)for m in monomials(3+w-2,WEIGHTS)}
        assert len(labels)==len(expected_labels)==150
        assert {(x['coordinate'],tuple(x['quotient_monomial']))for x in labels}==expected_labels
        physical=[]
        for label in labels:
            i=label['coordinate'];mon=tuple(label['quotient_monomial'])
            field=[{}for _ in range(6)];field[i]={mon:Q(1)}
            numerator=lift(field)
            normal=independent.contraction(field,G);tangential=independent.B(E,field)
            assert independent.contraction(numerator,F)==mul(delta,pullback(normal))
            assert independent.divergence(numerator)==mul(delta,pullback(independent.divergence(field)))
            assert independent.B(D,numerator)==mul(delta,pullback(tangential))
            for coordinate,poly in enumerate(numerator):
                assert all(sum(m)==4 and m[2]%3==(0 if coordinate==2 else 2)for m in poly)
            physical.append({**{('E1',)+m:c for m,c in normal.items()},**{('E2',)+m:c for m,c in tangential.items()}})
            transfer_checks+=1
        rhs={('E1',)+m:c for m,c in mul(density,E).items()}
        rows=list(map(tuple,test['coefficient_rows']));index={m:i for i,m in enumerate(rows)}
        support=set(rhs)
        for column in physical:support.update(column)
        assert set(rows)==support and len(rows)==len(index)
        assert test['shape']==[len(rows),150]
        assert all(len(row)==7 and row[0]in('E1','E2')for row in rows)
        assert all(sum(w*a for w,a in zip(WEIGHTS,row[1:]))==(7 if row[0]=='E1'else 4)for row in rows)
        assert [entries(col,index)for col in physical]==test['columns']and entries(rhs,index)==test['rhs']
        rank=independent.qrank(physical);augmented=independent.qrank(physical+[rhs])
        assert rank==test['rank']==150 and augmented==test['augmented_rank']==151
        dual={rows[i]:Q(c)for i,c in test['dual']}
        assert len(dual)==len(test['dual'])and all(dual.values())
        def pairing(vector,functional=dual):return sum(c*vector.get(m,0)for m,c in functional.items())
        assert pairing(rhs)==1 and all(pairing(col)==0 for col in physical)
        assert test['complete_fixed_denominator_test']is True and test['consistent']is False
        assert test['piola_basis_vectors_checked']==150 and test['quotient_coefficients']==0
        assert monomials(2*3-8,WEIGHTS)==[]
        altered_dual={m:2*c for m,c in dual.items()}
        negative+=independent.rejects(lambda:independent.check_equal(pairing(rhs,altered_dual),1))
        nonzero_row=next(iter(dual));bad_column=add(physical[0],{nonzero_row:Q(1)})
        negative+=independent.rejects(lambda:independent.check_equal(pairing(bad_column),0))
        receipts.append({'candidate':test['candidate'],'shape':test['shape'],'rational_rank':rank,
                         'rational_augmented_rank':augmented,'exact_dual_terms':len(dual),
                         'dual_physical_rows':[{'equation':m[0],'powers':list(m[1:]),'coefficient':str(c)}for m,c in dual.items()],
                         'dual_rhs_pairing':'1','all_column_pairings_zero':True})
    dimension_receipts=[]
    for row in packet['character_dimensions']:
        d=row['denominator_degree'];upstairs=monomials(d+1,(1,)*6)
        full=6*len(upstairs);projected=sum(sum(mon[2]%3==(0 if i==2 else 2)for mon in upstairs)for i in range(6))
        weighted=sum(len(monomials(d+w-2,WEIGHTS))for w in WEIGHTS)
        assert full==6*comb(d+6,5)==row['all_upstairs_numerator_coefficients']
        assert projected==weighted==row['character_projected_coefficients']==row['weighted_coefficients']
        dimension_receipts.append(row)
    assert [row['denominator_degree']for row in dimension_receipts]==[3,4,6,7,9]
    assert transfer_checks==450
    receipt={'schema':'cyclic-fano-transfer-independent-v1','status':'PASS',
             'checker_lf_sha256':independent.sha(Path(__file__)),
             'independent_arithmetic_dependency_lf_sha256':independent.sha(Path(independent.__file__)),
             'packet_lf_sha256':independent.sha(OUT/'packet.json'),'source_instance_lf_sha256':SOURCE_HASH,
             'arithmetic':'Independent checker sparse Fraction polynomials and exact rational elimination; no producer or CAS import',
             'quotient_and_density_reconstructed_from_raw_source':True,
             'mod5_Fermat_smoothness_checked':True,'physical_Piola_basis_transfers':transfer_checks,
             'character_dimensions':dimension_receipts,'tests':receipts,
             'Euler_normalization':{'weighted_Euler_divergence':8,'R_weight':'d-2',
                 'identity':'If P(G)=beta*E+G*R, replace P by P-(R/6)*epsilon_weighted. The normal component changes by -G*R and E*div(P)-P(E) by -E*R, leaving the cleared expression unchanged.',
                 'complete_scope':'Character averaging preserves an arbitrary certificate at each fixed invariant D. All weighted numerator monomials of degrees d-1 and d+1 are included. At d=3, the second expression has weight4 and cannot contain a nonzero G-multiple of weight6.'},
             'conclusion':'Each of these three specific invariant cubic denominators is excluded over C, with complete homogeneous numerator freedom and no additional parity condition.',
             'limits':'No exclusion of their powers, products, other denominator equations or arbitrary degree; no global support, certificate or Lean proof.',
             'negative_controls_rejected':negative}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'independent-validation.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':'PASS','candidates':3,'basis_transfers':transfer_checks,'ranks':[[150,151]]*3,'negative_controls':negative}))

if __name__=='__main__':main()
