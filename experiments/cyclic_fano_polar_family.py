#!/usr/bin/env python3
"""Exact exclusion of every nonzero constant first polar of the branch sextic."""
from pathlib import Path
from fractions import Fraction as Q
import argparse
import copy
import json
import time
import cyclic_fano_transfer as base

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/cyclic-fano-polar-family'
poly=base.poly
BASE=(0,1,3,4,5)
NAMES=('X0','X1','Y0','Y1','Y2')
ZERO=(0,)*6;VZERO=(0,)*5


def encode(p):return [{'powers':list(m),'coefficient':str(c)}for m,c in sorted(p.items())]


def mon(n,i,power=1):
    m=[0]*n;m[i]=power;return tuple(m)


def even_projection(p,q,h):
    parts=[{}for _ in range(3)]
    for m,c in p.items():
        assert m[2]<=2
        parts[m[2]][m[:2]+(0,)+m[3:]]=c
    square=poly.add(poly.scale(poly.mul(q,q),Q(1,2)),h,-1)
    return poly.add(poly.add(parts[0],poly.mul(q,parts[1]),Q(-1,2)),poly.mul(square,parts[2]))


def calculate():
    F,A,G,beta=base.target()
    q={m[:2]+(0,)+m[3:]:c for m,c in G.items()if m[2]==1}
    h={m:c for m,c in G.items()if not m[2]}
    Delta=poly.add(poly.mul(q,q),h,-4);J=poly.derivative(G,2)
    Es=[];Ps=[];basis=[]
    for index,j in enumerate(BASE):
        E=poly.derivative(Delta,j);P=[{}for _ in range(6)]
        P[j]=poly.scale(beta,-4);P[2]=poly.scale(poly.mul(beta,poly.derivative(q,j)),2)
        assert E==poly.add(poly.scale(poly.mul(J,poly.derivative(q,j)),2),poly.derivative(G,j),-4)
        assert base.contraction(P,G)==poly.mul(beta,E)
        assert base.contraction(base.lift(P),F)==poly.mul(A,base.pullback(E))
        assert E and all(m[2]==0 and sum(m)==5 for m in E)
        Es.append(E);Ps.append(P)
        basis.append({'parameter':index,'name':NAMES[index],'E':encode(E),'particular':[encode(p)for p in P]})
    # These five pure monomial coefficients form a diagonal, invertible minor.
    pure_rows=[mon(6,j,5)for j in BASE]
    injectivity=[[E.get(m,Q(0))for E in Es]for m in pure_rows]
    expected_diagonal=[Q(-1026,49),Q(-24),Q(-24),Q(-24),Q(-24)]
    assert injectivity==[[expected_diagonal[i]if i==j else Q(0)for j in range(5)]for i in range(5)]
    determinant=Q(1)
    for c in expected_diagonal:determinant*=c
    assert determinant
    # The complete quadratic residual, with its 15 independent parameter monomials.
    residuals={};residual_basis=[]
    for i in range(5):
        for j in range(i,5):
            power=tuple(int(k==i)+int(k==j)for k in range(5))
            R=base.B(Es[i],Ps[j])
            if i!=j:R=poly.add(R,base.B(Es[j],Ps[i]))
            assert all(m[2]==0 and sum(m)==8 for m in R)
            assert even_projection(R,q,h)==R
            residuals[power]=R
            residual_basis.append({'parameter_powers':list(power),'spatial_polynomial':encode(R)})
    # Retain every degree-five correction, not a subspace selected by the answer.
    grad=[poly.derivative(G,i)for i in range(6)]
    koszul=[]
    for eindex,E in enumerate(Es):
        count=0
        for i in range(6):
            for j in range(i+1,6):
                for m in base.monomials(5+base.WEIGHTS[i]+base.WEIGHTS[j]-8):
                    field=[{}for _ in range(6)];multiplier={m:Q(1)}
                    field[i]=poly.mul(multiplier,grad[j]);field[j]=poly.scale(poly.mul(multiplier,grad[i]),-1)
                    assert not base.contraction(field,G)
                    image=base.B(E,field)
                    assert not even_projection(image,q,h)
                    koszul.append({'E_basis_index':eindex,'pair':[i,j],'multiplier_powers':list(m),
                                   'raw_image':encode(image),'even_projection':[]})
                    count+=1
        assert count==25
    quotients=[]
    for m in base.monomials(2):
        image=poly.mul({m:Q(1)},G);assert not even_projection(image,q,h)
        quotients.append({'multiplier_powers':list(m),'raw_image':encode(image),'even_projection':[]})
    assert len(koszul)==125 and len(quotients)==15
    row_specs=[('v_X1_square',(1,4,0,3,0,0)),('v_Y1_square',(1,0,0,3,4,0)),
               ('v_Y2_square',(1,0,0,3,0,4)),('v_X0_square_after_Y1_Y2',(5,0,0,3,0,0)),
               ('v_Y0_square',(1,0,0,7,0,0))]
    equations=[];qs=[]
    for name,m in row_specs:
        equation={power:R[m]for power,R in residuals.items()if R.get(m)}
        qs.append(equation)
        equations.append({'id':name,'spatial_powers':list(m),'parameter_polynomial':encode(equation)})
    cross=tuple(int(i in (3,4))for i in range(5))
    assert qs==[{mon(5,1,2):Q(-160)},{mon(5,3,2):Q(-160)},
                {mon(5,4,2):Q(-160)},{mon(5,0,2):Q(-5472,49),cross:Q(400,147)},
                {mon(5,2,2):Q(-64)}]
    # Portable ideal identities certify powers of all five coordinates vanish.
    identities=[]
    for variable,row,coefficient in [(1,0,Q(-160)),(3,1,Q(-160)),(4,2,Q(-160)),(2,4,Q(-64))]:
        target={mon(5,variable,2):Q(1)};multiplier={VZERO:1/coefficient}
        assert poly.mul(multiplier,qs[row])==target
        identities.append({'variable':variable,'power':2,'target':encode(target),
                           'multipliers':[{'equation_index':row,'polynomial':encode(multiplier)}]})
    a=Q(5472,49);b=Q(400,147)
    c0=poly.scale(poly.add(qs[3],{cross:2*b},-1),1/(a*a))
    c1=poly.scale(qs[2],b*b/(a*a*160*160))
    target={mon(5,0,4):Q(1)}
    assert poly.add(poly.mul(c0,qs[3]),poly.mul(c1,qs[1]))==target
    identities.append({'variable':0,'power':4,'target':encode(target),
                       'multipliers':[{'equation_index':3,'polynomial':encode(c0)},
                                      {'equation_index':1,'polynomial':encode(c1)}]})
    return {'schema':'cyclic-fano-constant-polar-family-v1','status':'PASS',
            'instance':'cyclic-triple-fano','source_commit':'d96911d725077e66a8f10848908be01a643b1714',
            'source_instance_sha256':poly.sha(base.SOURCE/'source/instance.rec'),
            'producer_sha256':poly.sha(Path(__file__)),
            'dependencies':{'cyclic_fano_transfer.py':poly.sha(Path(base.__file__)),
                            'quadric_contact_pilot.py':poly.sha(Path(poly.__file__))},
            'spatial_variables':['X0','X1','Z','Y0','Y1','Y2'],
            'parameter_variables':['v_'+name for name in NAMES],
            'family':'E_v=sum_i v_i*partial_i(Delta), v in C^5 constant and nonzero',
            'degree':5,'Delta':encode(Delta),'Q':encode(q),'H':encode(h),'beta':encode(beta),
            'basis':basis,'quadratic_residual_basis':residual_basis,
            'projection_rule':'For p=f0+Z*f1+Z^2*f2, even(p)=f0-Q*f1/2+(Q^2/2-H)*f2; coefficients are independent of Z.',
            'koszul_projection_checks':koszul,'quotient_projection_checks':quotients,
            'complete_corrections_per_E':25,'basis_directions_checked':5,'quotient_dimension':15,
            'projection_completeness':'E2 is linear in E for each correction field; five basis checks cover every constant v. All25 degree-five Koszul multipliers and15 quotient multipliers are present.',
            'coefficient_equations':equations,'coordinate_power_identities':identities,
            'injectivity':{'spatial_rows':[list(m)for m in pure_rows],
                           'matrix':[[str(c)for c in row]for row in injectivity],
                           'determinant':str(determinant),
                           'consequence':'Every nonzero parameter vector yields a nonzero base polynomial E_v and hence a nonzero monic remainder modulo G.'},
            'conclusion':'Every nonzero constant first polar E_v of Delta is excluded as a degree-five denominator for this fixed target, over C.',
            'limits':'No exclusion of polynomial-direction polars, products, higher powers, arbitrary degree-five denominators or other supports. No HasCertificate proof or solved instance.'}


def save(name,packet):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/name).write_text(json.dumps(packet,indent=2)+'\n',encoding='utf-8',newline='\n')


def main():
    assert __debug__,'Run without -O'
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('run','verify'));args=parser.parse_args()
    started=time.perf_counter();expected=calculate()
    if args.command=='run':save('packet.json',expected)
    else:
        actual=json.loads((OUT/'packet.json').read_text(encoding='utf-8'));assert actual==expected
        mutations=[]
        for section in ('basis','quadratic_residual_basis','koszul_projection_checks','quotient_projection_checks',
                        'coefficient_equations','coordinate_power_identities'):
            bad=copy.deepcopy(actual);bad[section]=bad[section][1:];mutations.append(bad)
        bad=copy.deepcopy(actual);bad['injectivity']['determinant']='0';mutations.append(bad)
        for bad in mutations:
            try:assert bad==calculate()
            except AssertionError:pass
            else:raise AssertionError('Mutated family proof was accepted')
        save('validation.json',{'schema':'cyclic-fano-constant-polar-family-validation-v1','status':'PASS',
                               'producer_sha256':poly.sha(Path(__file__)),'packet_sha256':poly.sha(OUT/'packet.json'),
                               'basis_lifts_checked':5,'quadratic_parameter_terms':15,'Koszul_images_checked':125,
                               'quotient_images_checked':15,'coefficient_rows_checked':5,
                               'coordinate_power_identities_checked':5,'negative_controls_rejected':len(mutations)})
    print(json.dumps({'status':'PASS','command':args.command,'packet_sha256':poly.sha(OUT/'packet.json'),
                      'seconds':time.perf_counter()-started}))


if __name__=='__main__':main()
