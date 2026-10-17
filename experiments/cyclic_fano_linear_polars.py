#!/usr/bin/env python3
"""Exact degree-six polars from linear vector fields; bounded coefficient probes."""
from pathlib import Path
from fractions import Fraction as Q
import argparse
import copy
import json
import subprocess
import sys
import time
import cyclic_fano_transfer as base

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/cyclic-fano-linear-polars'
poly=base.poly
BASE=(0,1,3,4,5)
NAMES=('X0','X1','Y0','Y1','Y2')
ZERO=(0,)*6


def encode(p):return [{'powers':list(m),'coefficient':str(c)}for m,c in sorted(p.items())]


def even(p,q,h):
    if not p:return {}
    parts=[{}for _ in range(1+max(m[2]for m in p))]
    for m,c in p.items():
        parts[m[2]][m[:2]+(0,)+m[3:]]=c
    powers=[{ZERO:Q(1)},poly.scale(q,Q(-1,2))]
    for n in range(2,len(parts)):
        powers.append(poly.add(poly.scale(poly.mul(q,powers[-1]),-1),poly.mul(h,powers[-2]),-1))
    return base.total(poly.mul(v,powers[n])for n,v in enumerate(parts))


def system():
    F,A,G,beta=base.target()
    q={m[:2]+(0,)+m[3:]:c for m,c in G.items()if m[2]==1}
    h={m:c for m,c in G.items()if not m[2]}
    delta=poly.add(poly.mul(q,q),h,-4)
    grad=[poly.derivative(G,i)for i in range(6)]
    Es=[];Ps=[];basis=[]
    for i in BASE:
        for j in BASE:
            m=tuple(int(k==j)for k in range(6));xj={m:Q(1)}
            E=poly.mul(xj,poly.derivative(delta,i));P=[{}for _ in range(6)]
            P[i]=poly.scale(poly.mul(beta,xj),-4)
            P[2]=poly.scale(poly.mul(poly.mul(beta,xj),poly.derivative(q,i)),2)
            assert base.contraction(P,G)==poly.mul(beta,E)
            assert base.contraction(base.lift(P),F)==poly.mul(A,base.pullback(E))
            Es.append(E);Ps.append(P)
            basis.append({'matrix_indices':[BASE.index(i),BASE.index(j)],'E':encode(E),'particular':[encode(v)for v in P]})
    residuals=[];labels=[]
    for i in range(25):
        for j in range(i,25):
            R=base.B(Es[i],Ps[j])
            if i!=j:R=poly.add(R,base.B(Es[j],Ps[i]))
            assert even(R,q,h)==R and all(sum(m)==10 for m in R)
            residuals.append(R);labels.append({'kind':'M*M','indices':[i,j]})
    correction_fields=[];pairs=[]
    for i in BASE:
        for j in BASE:
            if i<j:
                field=[{}for _ in range(6)];field[i]=grad[j];field[j]=poly.scale(grad[i],-1)
                correction_fields.append(field);pairs.append([i,j])
    mixed=[]
    for i,E in enumerate(Es):
        for k,field in enumerate(correction_fields):
            C=even(base.B(E,field),q,h)
            a,b=pairs[k]
            W=poly.add(poly.mul(poly.derivative(delta,a),poly.derivative(E,b)),
                       poly.mul(poly.derivative(delta,b),poly.derivative(E,a)),-1)
            assert C==poly.scale(W,Q(-1,4))
            mixed.append(C);labels.append({'kind':'M*c','indices':[i,k]})
    columns=residuals+mixed
    rows={}
    for j,col in enumerate(columns):
        for m,c in col.items():rows.setdefault(m,{})[j]=c
    return locals()


def modq(c,p):return c.numerator*pow(c.denominator,-1,p)%p


def mod_reduce(v,pivots,p):
    v={k:c%p for k,c in v.items()if c%p}
    while v:
        j=min(v)
        if j not in pivots:break
        r=pivots[j];a=v[j]
        for k,c in r.items():
            z=(v.get(k,0)-a*c)%p
            if z:v[k]=z
            else:v.pop(k,None)
    return v


def modular_probe(data,p=1009):
    active=set(range(25));stages=[]
    for iteration in range(5):
        kept=[j for j,label in enumerate(data['labels'])
              if label['indices'][0]in active and (label['kind']=='M*c' or label['indices'][1]in active)]
        pivots={}
        for m,row in sorted(data['rows'].items(),key=lambda z:(len(z[1]),z[0])):
            v=mod_reduce({j:modq(c,p)for j,c in row.items()if j in kept},pivots,p)
            if v:
                j=min(v);z=pow(v[j],-1,p);pivots[j]={k:c*z%p for k,c in v.items()}
        squares=[]
        for i in sorted(active):
            j=next(j for j,label in enumerate(data['labels'])if label['kind']=='M*M' and label['indices']==[i,i])
            if not mod_reduce({j:1},pivots,p):squares.append(i)
        stages.append({'active_parameters':sorted(active),'columns':len(kept),'rank_mod_prime':len(pivots),'forced_square_indices_mod_prime':squares})
        if not squares:break
        active-=set(squares)
    return {'prime':p,'stages':stages,'remaining_parameters':sorted(active)}


def exact_reduce(v,pivots,track=None):
    v=v.copy();track={}if track is None else track.copy()
    while v:
        j=min(v)
        if j not in pivots:break
        r,t=pivots[j];a=v[j]
        v=poly.add(v,r,-a);track=poly.add(track,t,-a)
    return v,track


def exact_row_basis(rows):
    pivots={}
    for m,row in sorted(rows.items(),key=lambda z:(len(z[1]),z[0])):
        v,track=exact_reduce(row,pivots,{m:Q(1)})
        if v:
            j=min(v);z=1/v[j];pivots[j]=(poly.scale(v,z),poly.scale(track,z))
    return pivots


def exact_probe(data):
    pivots=exact_row_basis(data['rows']);square_duals=[]
    for i in range(25):
        if i//5==i%5:continue
        j=next(j for j,label in enumerate(data['labels'])if label['kind']=='M*M' and label['indices']==[i,i])
        rem,track=exact_reduce({j:Q(1)},pivots)
        assert not rem
        dual=poly.scale(track,-1)
        assert base.total(poly.scale(data['rows'][m],c)for m,c in dual.items())=={j:Q(1)}
        square_duals.append({'parameter_index':i,'dual':encode(dual)})
    active=[0,6,12,18,24]
    # Put mixed variables first: rows whose first nonzero coordinate is a pure
    # quadratic are necessary equations independent of every correction.
    pure=[j for j,l in enumerate(data['labels'])if l['kind']=='M*M' and all(i in active for i in l['indices'])]
    mixed=[j for j,l in enumerate(data['labels'])if l['kind']=='M*c' and l['indices'][0]in active]
    order=mixed+pure;lookup={j:k for k,j in enumerate(order)}
    rows={m:{lookup[j]:c for j,c in row.items()if j in lookup}for m,row in data['rows'].items()}
    diag=exact_row_basis(rows);equations=[]
    for j,(row,track)in sorted(diag.items()):
        if j<len(mixed):continue
        assert base.total(poly.scale(rows[m],c)for m,c in track.items())==row
        polynomial={}
        for k,c in row.items():
            inds=data['labels'][order[k]]['indices']
            power=tuple(sum(i==a for i in inds)for a in active)
            polynomial[power]=c
        equations.append({'polynomial':encode(polynomial),'dual':encode(track)})
    return {'full_rank':len(pivots),'off_diagonal_square_duals':square_duals,
            'diagonal_parameter_indices':active,'diagonal_columns':len(order),
            'diagonal_rank':len(diag),'diagonal_mixed_rank':sum(j<len(mixed)for j in diag),
            'diagonal_equations':equations}


def decode(p):return {tuple(t['powers']):Q(t['coefficient'])for t in p}


def cubic_identities(equations):
    qs=[decode(v['polynomial'])for v in equations];rows={}
    for i,q in enumerate(qs):
        for k in range(5):
            m=tuple(int(j==k)for j in range(5))
            rows[(i,k)]=poly.mul(q,{m:Q(1)})
    pivots=exact_row_basis(rows);assert len(pivots)==35
    identities=[]
    for k in range(5):
        m=tuple(3*int(j==k)for j in range(5));target={m:Q(1)}
        remainder,track=exact_reduce(target,pivots);assert not remainder
        track=poly.scale(track,-1)
        assert base.total(poly.scale(rows[j],c)for j,c in track.items())==target
        identities.append({'diagonal_variable':k,'power':3,'target':encode(target),
                           'multipliers':[{'equation_index':i,'variable':j,'coefficient':str(c)}
                                          for (i,j),c in sorted(track.items())]})
    return {'degree':3,'rows':35,'columns':60,'rank':35,'identities':identities}


def determinant(matrix):
    a=[row[:]for row in matrix];det=Q(1)
    for j in range(len(a)):
        k=next(k for k in range(j,len(a))if a[k][j])
        if k!=j:a[j],a[k]=a[k],a[j];det=-det
        c=a[j][j];det*=c
        for k in range(j+1,len(a)):
            z=a[k][j]/c
            if z:
                for l in range(j,len(a)):a[k][l]-=z*a[j][l]
    return det


def complete_projection(data):
    fields=[];count=0;projected=0
    for i in range(6):
        for j in range(i+1,6):
            for m in base.monomials(6+base.WEIGHTS[i]+base.WEIGHTS[j]-8):
                mult={m:Q(1)};field=[{}for _ in range(6)]
                field[i]=poly.mul(mult,data['grad'][j]);field[j]=poly.scale(poly.mul(mult,data['grad'][i]),-1)
                assert not base.contraction(field,data['G'])
                surviving=data['pairs'].index([i,j])if i in BASE and j in BASE else None
                fields.append({'pair':[i,j],'multiplier_powers':list(m),
                               'surviving_constant_pair':surviving,'field':[encode(p)for p in field]})
                for e,E in enumerate(data['Es']):
                    image=even(base.B(E,field),data['q'],data['h'])
                    expected={}if surviving is None else data['mixed'][10*e+surviving]
                    assert image==expected;count+=1;projected+=bool(image)
    quotients=[]
    for m in base.monomials(4):
        assert not even(poly.mul({m:Q(1)},data['G']),data['q'],data['h'])
        quotients.append(list(m))
    assert len(fields)==85 and count==2125 and len(quotients)==75
    return {'raw_fields':fields,'raw_fields_per_denominator':85,'raw_projection_identities':count,
            'surviving_constant_base_pairs':data['pairs'],'mixed_images_nonzero':projected,
            'quotient_multiplier_powers':quotients,'quotient_projection_identities':len(quotients)}


def calculate():
    data=system();screen=modular_probe(data);proof=exact_probe(data)
    projection=complete_projection(data);cubic=cubic_identities(proof['diagonal_equations'])
    pure_rows=[]
    for i in BASE:
        for j in BASE:
            pure_rows.append(tuple(5*int(k==i)+int(k==j)for k in range(6)))
    minor=[[E.get(m,Q(0))for E in data['Es']]for m in pure_rows]
    det=determinant(minor);assert det
    # G mod5 is weighted Fermat, with its six partials the coordinate powers.
    Gmod={m:modq(c,5)for m,c in data['G'].items()if modq(c,5)}
    expected={tuple((2 if j==2 else 6)*int(k==j)for k in range(6)):1 for j in range(6)}
    assert Gmod==expected
    active=set(proof['diagonal_parameter_indices'])
    diag_rows={m for m,row in data['rows'].items()if any(
        data['labels'][j]['indices'][0]in active and
        (data['labels'][j]['kind']=='M*c' or data['labels'][j]['indices'][1]in active)for j in row)}
    return {'schema':'cyclic-fano-linear-polars-v1','status':'PASS',
            'source_commit':'d96911d725077e66a8f10848908be01a643b1714',
            'source_instance_sha256':poly.sha(base.SOURCE/'source/instance.rec'),
            'producer_sha256':poly.sha(Path(__file__)),
            'dependencies':{'cyclic_fano_transfer.py':poly.sha(Path(base.__file__)),
                            'quadric_contact_pilot.py':poly.sha(Path(poly.__file__))},
            'instance':'cyclic-triple-fano','q':1,'spatial_variables':['X0','X1','Z','Y0','Y1','Y2'],
            'base_variables':list(NAMES),'matrix_parameter_order':'row-major M_ij, v_i=sum_j M_ij*x_j',
            'degree':6,'Delta':encode(data['delta']),'Q':encode(data['q']),'H':encode(data['h']),
            'beta':encode(data['beta']),'basis':data['basis'],
            'residual_formula':'4*(beta*L(L(Delta))-(L(beta)+beta*trace(M))*L(Delta))',
            'quadratic_residual_basis':[{'matrix_indices':label['indices'],'polynomial':encode(p)}
                                        for label,p in zip(data['labels'][:325],data['residuals'])],
            'mixed_correction_basis':[{'matrix_index':i,'constant_pair_index':k,
                                       'polynomial':encode(data['mixed'][10*i+k])}for i in range(25)for k in range(10)],
            'full_map':{'potential_rows':1001,'active_rows':len(data['rows']),'columns':575,
                        'quadratic_columns':325,'mixed_columns':250,'rank':proof['full_rank']},
            'projection':projection,
            'modular_discovery':screen,
            'off_diagonal_square_duals':proof['off_diagonal_square_duals'],
            'diagonal_stage':{'parameter_indices':proof['diagonal_parameter_indices'],
                              'active_rows':len(diag_rows),'columns':65,'rank':proof['diagonal_rank'],
                              'mixed_rank':proof['diagonal_mixed_rank'],'equations':proof['diagonal_equations']},
            'cubic_macaulay':cubic,
            'injectivity':{'rows':[list(m)for m in pure_rows],'matrix':[[str(c)for c in row]for row in minor],
                           'determinant':str(det)},
            'regular_sequence_control':{'prime':5,'G_mod5':[{'powers':list(m),'coefficient':c}for m,c in sorted(Gmod.items())],
                                        'description':'The weighted gradient reduces to nonzero scalar multiples of X0^5,X1^5,Z,Y0^5,Y1^5,Y2^5.'},
            'conclusion':'All nonzero degree-six linear polars E_M=(Mx).grad(Delta), M constant over C, are excluded for the fixed target.',
            'limits':'This is a complete algebraic family exclusion, not a certificate, a formal Lean proof or an exclusion of other degree-six denominators.',
            'attempts':[{'stage':'full_quadratic_screen','bound_seconds':120,'result':'20 off-diagonal squares; exact duals exported'},
                        {'stage':'diagonal_degree_two','bound_seconds':120,'result':'No individual diagonal square in the coefficient rowspace'},
                        {'stage':'diagonal_degree_three','bound_seconds':120,'result':'All35 cubic monomials spanned; five coordinate-cube identities exported'},
                        {'stage':'initial_projection_implementation','result':'The initial Z-degree<=2 helper rejected five valid Z*x_i quotient multipliers. Corrected to the arbitrary-power monic recurrence; all75 quotient directions are retained and checked.'}]}


def save(name,data):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/name).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')


def verify(expected):
    actual=json.loads((OUT/'packet.json').read_text(encoding='utf-8'));assert actual==expected
    changes=[]
    for key in ('basis','quadratic_residual_basis','mixed_correction_basis','off_diagonal_square_duals'):
        bad=copy.deepcopy(actual);bad[key]=bad[key][1:];changes.append(bad)
    bad=copy.deepcopy(actual);bad['projection']['raw_fields']=bad['projection']['raw_fields'][1:];changes.append(bad)
    bad=copy.deepcopy(actual);bad['projection']['quotient_multiplier_powers']=[];changes.append(bad)
    bad=copy.deepcopy(actual);bad['diagonal_stage']['equations'][0]['polynomial'][0]['coefficient']='0';changes.append(bad)
    bad=copy.deepcopy(actual);bad['cubic_macaulay']['identities'][0]['multipliers'][0]['coefficient']='0';changes.append(bad)
    bad=copy.deepcopy(actual);bad['injectivity']['determinant']='0';changes.append(bad)
    for bad in changes:
        try:assert bad==expected
        except AssertionError:pass
        else:raise AssertionError('Mutation accepted')
    save('validation.json',{'schema':'cyclic-fano-linear-polars-validation-v1','status':'PASS',
                           'producer_sha256':poly.sha(Path(__file__)),'packet_sha256':poly.sha(OUT/'packet.json'),
                           'basis_lifts':25,'quadratic_residuals':325,'raw_projection_identities':2125,
                           'quotient_projection_identities':75,'off_diagonal_square_duals':20,
                           'diagonal_equations':12,'cubic_power_identities':5,'injectivity_rank':25,
                           'negative_controls_rejected':len(changes)})


def main():
    assert __debug__,'Run without -O'
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['probe','run','verify','_run','_verify']);args=parser.parse_args()
    if args.command in ('run','verify'):
        result=subprocess.run([sys.executable,'-S',str(Path(__file__)),'_'+args.command],timeout=120)
        raise SystemExit(result.returncode)
    started=time.perf_counter()
    if args.command=='probe':
        data=system();print(json.dumps(modular_probe(data)));return
    result=calculate()
    if args.command=='_run':save('packet.json',result)
    else:verify(result)
    print(json.dumps({'status':'PASS','command':args.command,'seconds':time.perf_counter()-started,
                      'packet_sha256':poly.sha(OUT/'packet.json')}))


if __name__=='__main__':main()
