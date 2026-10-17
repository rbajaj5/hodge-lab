#!/usr/bin/env python3
"""Independent exact audit of the entire constant-direction first-polar family."""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations
import copy
import json
import check_cyclic_fano_branch_polars as C

A=C.A
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/cyclic-fano-polar-family'
ZERO,ONE=A.ZERO,A.ONE
PAIRS=tuple((i,j)for i in range(5)for j in range(i,5))
ROWS=((1,4,0,3,0,0),(1,0,0,3,4,0),(1,0,0,3,0,4),
      (5,0,0,3,0,0),(1,0,0,7,0,0))


def decode(terms,n):
    result={}
    for term in terms:
        m=tuple(term['powers']);c=(Q(term['coefficient']),Q(0))
        assert len(m)==n and all(isinstance(e,int)and e>=0 for e in m)
        assert m not in result and c!=ZERO
        result[m]=c
    return result


def pair_powers(i,j):
    return tuple(int(k==i)+int(k==j)for k in range(5))


def derive():
    F,original_A,G,beta=A.target()
    q,h,Delta=C.split_G(G)
    gradient=[A.derivative(G,i)for i in range(6)]
    E=[A.derivative(Delta,i)for i in C.BASE]
    beta_derivatives=[A.derivative(beta,i)for i in C.BASE]
    fields=[]
    for k,i in enumerate(C.BASE):
        p=[{}for _ in range(6)]
        p[i]=A.scale(beta,(Q(-4),Q(0)))
        p[2]=A.scale(A.mul(beta,A.derivative(q,i)),(Q(2),Q(0)))
        assert A.contraction(p,G)==A.mul(beta,E[k])
        assert A.contraction(A.lift(p),F)==A.mul(original_A,A.pullback(E[k]))
        fields.append(p)
    euler_checks=0
    for m in A.monomials(3):
        R={m:ONE};normalizer=[]
        for i,w in enumerate(A.WEIGHTS):
            n=list(m);n[i]+=1
            normalizer.append({tuple(n):(Q(w,6),Q(0))})
        assert A.contraction(normalizer,G)==A.mul(R,G)
        for e in E:
            assert A.B(e,normalizer)==A.mul(e,R)
            euler_checks+=1
    assert euler_checks==180
    residuals={}
    for i,j in PAIRS:
        first=A.scale(A.mul(beta,A.derivative(E[i],C.BASE[j])),(Q(1 if i==j else 2),Q(0)))
        second=A.mul(beta_derivatives[i],E[j])
        physical=A.B(E[i],fields[j])
        if i!=j:
            second=A.add(second,A.mul(beta_derivatives[j],E[i]))
            physical=A.add(physical,A.B(E[j],fields[i]))
        residual=A.scale(A.add(first,A.scale(second,A.cn(ONE))),(Q(4),Q(0)))
        assert residual==physical
        assert all(m[2]==0 and sum(m)==8 for m in residual)
        residuals[i,j]=residual
    rows=[{pair:p[row]for pair,p in residuals.items()if row in p}for row in ROWS]
    assert rows==[{(1,1):(Q(-160),Q(0))},{(3,3):(Q(-160),Q(0))},
                  {(4,4):(Q(-160),Q(0))},
                  {(0,0):(Q(-5472,49),Q(0)),(3,4):(Q(400,147),Q(0))},
                  {(2,2):(Q(-64),Q(0))}]
    # E_v=0 implies v=0 by the five pure fifth-power coefficients.
    pure_rows=[]
    for i in C.BASE:
        powers=tuple(5 if j==i else 0 for j in range(6))
        pure_rows.append([p.get(powers,ZERO)for p in E])
    expected=[Q(-1026,49),Q(-24),Q(-24),Q(-24),Q(-24)]
    assert pure_rows==[[(a,Q(0))if j==i else ZERO for j in range(5)]for i,a in enumerate(expected)]
    # Verify the explicit smooth reduction needed for regular-sequence
    # completeness. All rational denominators are units at 5.
    fermat={tuple(6 if i==j else 0 for j in range(6)):1 for i in range(6)}
    reduced={}
    for m,(real,imag)in F.items():
        assert imag==0 and real.denominator%5
        value=(real.numerator*pow(real.denominator,-1,5))%5
        if value:reduced[m]=value
    assert reduced==fermat
    corrections=[];labels=[]
    for i,j in combinations(range(6),2):
        for m in A.monomials(5+A.WEIGHTS[i]+A.WEIGHTS[j]-8):
            p=[{}for _ in range(6)]
            p[i]=A.mul({m:ONE},gradient[j]);p[j]=A.scale(A.mul({m:ONE},gradient[i]),A.cn(ONE))
            assert not A.contraction(p,G)
            corrections.append(p);labels.append((i,j,m))
    assert len(corrections)==25
    correction_columns=[]
    for e in E:
        columns=[A.B(e,p)for p in corrections]
        assert all(not C.even_projection(p,q,h)for p in columns)
        correction_columns.append(columns)
    quotient_monomials=A.monomials(2)
    quotient_columns=[A.mul(G,{m:ONE})for m in quotient_monomials]
    assert len(quotient_columns)==15
    assert all(not C.even_projection(p,q,h)for p in quotient_columns)
    assert all(C.even_projection(p,q,h)==p for p in residuals.values())
    return {'F':F,'G':G,'beta':beta,'Delta':Delta,'Q':q,'H':h,'E':E,'fields':fields,
            'parameter_residuals':residuals,'five_rows':rows,'pure_coefficient_matrix':pure_rows,
            'correction_labels':labels,'correction_columns':correction_columns,
            'quotient_monomials':quotient_monomials,'quotient_columns':quotient_columns,
            'smooth_reduction_mod5':reduced,'Euler_normalization_checks':euler_checks}


def validate(packet,exact):
    assert packet['schema']=='cyclic-fano-constant-polar-family-v1'and packet['status']=='PASS'
    assert packet['instance']=='cyclic-triple-fano'and packet['degree']==5
    assert packet['source_commit']=='d96911d725077e66a8f10848908be01a643b1714'
    assert packet['source_instance_sha256']==A.I.sha(C.SOURCE/'source/instance.rec')
    assert packet['producer_sha256']==A.I.sha(ROOT/'experiments/cyclic_fano_polar_family.py')
    assert packet['dependencies']=={name:A.I.sha(ROOT/'experiments'/name)for name in ('cyclic_fano_transfer.py','quadric_contact_pilot.py')}
    assert packet['spatial_variables']==['X0','X1','Z','Y0','Y1','Y2']
    assert packet['parameter_variables']==['v_X0','v_X1','v_Y0','v_Y1','v_Y2']
    for key in ('Delta','Q','H','beta'):
        assert decode(packet[key],6)==exact[key]
    assert len(packet['basis'])==5
    seen=set()
    for entry in packet['basis']:
        i=entry['parameter'];assert i in range(5)and i not in seen;seen.add(i)
        assert entry['name']==['X0','X1','Y0','Y1','Y2'][i]
        assert decode(entry['E'],6)==exact['E'][i]
        assert [decode(p,6)for p in entry['particular']]==exact['fields'][i]
    assert seen==set(range(5))
    expected_residuals={pair_powers(*pair):p for pair,p in exact['parameter_residuals'].items()}
    assert len(packet['quadratic_residual_basis'])==15
    seen=set()
    for entry in packet['quadratic_residual_basis']:
        m=tuple(entry['parameter_powers']);assert m in expected_residuals and m not in seen;seen.add(m)
        assert decode(entry['spatial_polynomial'],6)==expected_residuals[m]
    assert seen==set(expected_residuals)
    expected_corrections={}
    for basis,columns in enumerate(exact['correction_columns']):
        for label,column in zip(exact['correction_labels'],columns):
            i,j,m=label;expected_corrections[basis,i,j,m]=column
    assert len(packet['koszul_projection_checks'])==125
    seen=set()
    for entry in packet['koszul_projection_checks']:
        i,j=entry['pair'];key=(entry['E_basis_index'],i,j,tuple(entry['multiplier_powers']))
        assert key in expected_corrections and key not in seen;seen.add(key)
        assert decode(entry['raw_image'],6)==expected_corrections[key]
        assert decode(entry['even_projection'],6)==C.even_projection(expected_corrections[key],exact['Q'],exact['H'])=={}
    assert seen==set(expected_corrections)
    expected_quotients=dict(zip(exact['quotient_monomials'],exact['quotient_columns']))
    assert len(packet['quotient_projection_checks'])==15
    seen=set()
    for entry in packet['quotient_projection_checks']:
        m=tuple(entry['multiplier_powers']);assert m in expected_quotients and m not in seen;seen.add(m)
        assert decode(entry['raw_image'],6)==expected_quotients[m]
        assert decode(entry['even_projection'],6)==C.even_projection(expected_quotients[m],exact['Q'],exact['H'])=={}
    assert seen==set(expected_quotients)
    assert packet['complete_corrections_per_E']==25 and packet['basis_directions_checked']==5
    assert packet['quotient_dimension']==15
    expected_equations=[{pair_powers(*pair):c for pair,c in row.items()}for row in exact['five_rows']]
    assert len(packet['coefficient_equations'])==5
    for i,entry in enumerate(packet['coefficient_equations']):
        assert tuple(entry['spatial_powers'])==ROWS[i]
        assert decode(entry['parameter_polynomial'],5)==expected_equations[i]
    # These exact ideal-membership identities certify every parameter is zero
    # in any field of characteristic zero; numerical sampling is unnecessary.
    expected_powers={0:4,1:2,2:2,3:2,4:2};seen=set()
    assert len(packet['coordinate_power_identities'])==5
    for identity in packet['coordinate_power_identities']:
        variable=identity['variable'];assert variable in expected_powers and variable not in seen;seen.add(variable)
        power=identity['power'];assert power==expected_powers[variable]
        target={tuple(power if j==variable else 0 for j in range(5)):ONE}
        assert decode(identity['target'],5)==target
        result={};seen_equations=set()
        for term in identity['multipliers']:
            i=term['equation_index'];assert i in range(5)and i not in seen_equations;seen_equations.add(i)
            multiplier=decode(term['polynomial'],5)
            result=A.add(result,A.mul(multiplier,expected_equations[i]))
        assert result==target
    assert seen==set(range(5))
    injection=packet['injectivity']
    assert injection['spatial_rows']==[list(tuple(5 if j==i else 0 for j in range(6)))for i in C.BASE]
    assert [[(Q(c),Q(0))for c in row]for row in injection['matrix']]==exact['pure_coefficient_matrix']
    determinant=Q(1)
    for i in range(5):determinant*=exact['pure_coefficient_matrix'][i][i][0]
    assert Q(injection['determinant'])==determinant and determinant!=0


def main():
    assert __debug__,'Run without -O'
    exact=derive()
    path=OUT/'packet.json';packet=A.I.load(path);validate(packet,exact)
    negative=[]
    altered=copy.deepcopy(packet);altered['basis'][0]['particular'][0]=[];negative.append(altered)
    altered=copy.deepcopy(packet);altered['quadratic_residual_basis'][1]['spatial_polynomial'][0]['coefficient']='1';negative.append(altered)
    altered=copy.deepcopy(packet);altered['koszul_projection_checks'][0]['raw_image'][0]['coefficient']='1';negative.append(altered)
    altered=copy.deepcopy(packet);altered['koszul_projection_checks'].pop();negative.append(altered)
    altered=copy.deepcopy(packet);altered['quotient_projection_checks'][0]['even_projection']=[{'powers':[8,0,0,0,0,0],'coefficient':'1'}];negative.append(altered)
    altered=copy.deepcopy(packet);altered['coefficient_equations'][3]['parameter_polynomial'].pop(0);negative.append(altered)
    altered=copy.deepcopy(packet);altered['coordinate_power_identities'][-1]['multipliers'][0]['polynomial'][0]['coefficient']='1';negative.append(altered)
    altered=copy.deepcopy(packet);altered['injectivity']['matrix'][0][0]='0';negative.append(altered)
    rejected=sum(A.I.rejects(lambda p=p:validate(p,exact))for p in negative)
    assert rejected==8
    primary=A.I.load(OUT/'validation.json')
    assert primary['status']=='PASS'and primary['packet_sha256']==A.I.sha(path)
    assert primary['producer_sha256']==packet['producer_sha256']
    receipt={'schema':'cyclic-fano-constant-polar-family-independent-v1','status':'PASS',
             'checker_lf_sha256':A.I.sha(Path(__file__)),
             'packet_lf_sha256':A.I.sha(path),'primary_validation_lf_sha256':A.I.sha(OUT/'validation.json'),
             'source_instance_lf_sha256':A.I.sha(C.SOURCE/'source/instance.rec'),
             'independent_arithmetic_dependencies':{Path(p).name:A.I.sha(Path(p))for p in (C.__file__,A.__file__,A.I.__file__)},
             'exact_E1_and_original_Piola_basis_lifts_checked':5,
             'Euler_normalization_basis_identities_checked':exact['Euler_normalization_checks'],
             'all_parameter_quadratic_terms_reconstructed':15,
             'complete_Koszul_fields_per_denominator':25,
             'basis_correction_columns_checked':125,'quotient_columns_checked':15,
             'all_corrections_have_zero_even_projection':True,
             'five_coefficient_equations':[{'spatial_powers':list(m),'parameter_polynomial':A.I.sparse({pair_powers(*pair):c for pair,c in row.items()})}for m,row in zip(ROWS,exact['five_rows'])],
             'coordinate_power_identities_checked':{'v_X0':4,'v_X1':2,'v_Y0':2,'v_Y1':2,'v_Y2':2},
             'nonzero_parameter_implies_nonzero_denominator':True,
             'pure_coefficient_matrix_determinant':packet['injectivity']['determinant'],
             'negative_controls_rejected':rejected,
             'regular_sequence_completeness':'The source F reduces to the smooth Fermat sextic modulo5, so its characteristic-zero projective hypersurface is smooth. A nonzero common gradient zero of weighted G would lift under X2^3=Z to one of F. Thus the six partials of G form a regular sequence, and every homogeneous E1 correction is Koszul. At degree5 the only allowed multipliers are the25 linear multipliers on base/Z pairs.',
             'all_parameter_scope':'Each correction image is linear in E_v, so all five basis images cover every constant complex v. All15 quadratic parameter coefficients of the particular residual are reconstructed, and the exact five coordinate-power identities force v=0. This is not inference from finitely sampled directions.',
             'conclusion':'Every nonzero constant-direction first polar of Delta is excluded as a degree-five denominator for the fixed target over C.',
             'limits':'No claim about polynomial-direction polars, products, powers, arbitrary degree-five denominators, other supports, Lean HasCertificate, or a solved instance.'}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'independent-validation.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':'PASS','all_parameter_quadratic_terms':15,'correction_columns':125,
                      'quotient_columns':15,'power_identities':5,'negative_controls_rejected':rejected,
                      'receipt_lf_sha256':A.I.sha(OUT/'independent-validation.json')}))


if __name__=='__main__':main()
