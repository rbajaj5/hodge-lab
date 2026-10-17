#!/usr/bin/env python3
"""Bounded exact degree-seven polars from homogeneous quadratic directions."""
from pathlib import Path
from fractions import Fraction as Q
import argparse
import copy
import hashlib
import json
import subprocess
import sys
import time
import cyclic_fano_linear_polars as arithmetic

base=arithmetic.base;poly=base.poly
BASE=arithmetic.BASE;NAMES=arithmetic.NAMES;ZERO=(0,)*6
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/cyclic-fano-quadratic-polars'
encode=arithmetic.encode


def system():
    F,A,G,beta=base.target()
    q={m[:2]+(0,)+m[3:]:c for m,c in G.items()if m[2]==1}
    h={m:c for m,c in G.items()if not m[2]}
    delta=poly.add(poly.mul(q,q),h,-4)
    grad=[poly.derivative(G,i)for i in range(6)]
    dd=[poly.derivative(delta,i)for i in range(6)]
    Es=[];Ps=[];basis=[]
    for i in BASE:
        for m in base.monomials(2):
            mult={m:Q(1)};E=poly.mul(mult,dd[i]);P=[{}for _ in range(6)]
            P[i]=poly.scale(poly.mul(beta,mult),-4)
            P[2]=poly.scale(poly.mul(poly.mul(beta,mult),poly.derivative(q,i)),2)
            assert base.contraction(P,G)==poly.mul(beta,E)
            assert base.contraction(base.lift(P),F)==poly.mul(A,base.pullback(E))
            Es.append(E);Ps.append(P)
            basis.append({'component':i,'quadratic_powers':list(m),'E':encode(E),'particular':[encode(v)for v in P]})
    assert len(Es)==75
    residuals=[];labels=[]
    for i in range(75):
        for j in range(i,75):
            R=base.B(Es[i],Ps[j])
            if i!=j:R=poly.add(R,base.B(Es[j],Ps[i]))
            assert all(m[2]==0 and sum(m)==12 for m in R)
            residuals.append(R);labels.append({'kind':'a*a','indices':[i,j]})
    correction_labels=[];mixed=[]
    for i in BASE:
        for j in BASE:
            if i<j:
                for k in BASE:correction_labels.append({'kind':'linear_base_pair','pair':[i,j],'linear_coordinate':k})
    for i in BASE:correction_labels.append({'kind':'t_mixed','coordinate':i})
    for e,E in enumerate(Es):
        ed=[poly.derivative(E,i)for i in range(6)]
        for n,label in enumerate(correction_labels):
            if label['kind']=='linear_base_pair':
                i,j=label['pair'];k=label['linear_coordinate']
                x={tuple(int(l==k)for l in range(6)):Q(1)}
                W=poly.add(poly.mul(dd[i],ed[j]),poly.mul(dd[j],ed[i]),-1)
                Wh=dd[i]if k==j else poly.scale(dd[j],-1)if k==i else {}
                C=poly.add(poly.mul(E,Wh),poly.mul(x,W),-1)
            else:
                i=label['coordinate'];C=poly.add(poly.mul(E,dd[i]),poly.mul(delta,ed[i]),-2)
            mixed.append(C);labels.append({'kind':'a*c','indices':[e,n]})
    columns=residuals+mixed;rows={}
    for j,col in enumerate(columns):
        for m,c in col.items():rows.setdefault(m,{})[j]=c
    return locals()


def modular_probe(data,p=1009):
    active=set(range(75));stages=[]
    for iteration in range(4):
        kept={j for j,label in enumerate(data['labels'])
              if label['indices'][0]in active and (label['kind']=='a*c' or label['indices'][1]in active)}
        pivots={};started=time.perf_counter()
        for m,row in sorted(data['rows'].items(),key=lambda z:(len(z[1]),z[0])):
            v=arithmetic.mod_reduce({j:arithmetic.modq(c,p)for j,c in row.items()if j in kept},pivots,p)
            if v:
                j=min(v);z=pow(v[j],-1,p);pivots[j]={k:c*z%p for k,c in v.items()}
        squares=[]
        for i in sorted(active):
            j=next(j for j,label in enumerate(data['labels'])if label['kind']=='a*a' and label['indices']==[i,i])
            if not arithmetic.mod_reduce({j:1},pivots,p):squares.append(i)
        stages.append({'active_parameters':sorted(active),'columns':len(kept),'rank_mod_prime':len(pivots),'forced_square_indices_mod_prime':squares,
                       'seconds':time.perf_counter()-started})
        print(json.dumps({'stage':iteration,**stages[-1]}),flush=True)
        if not squares:break
        active-=set(squares)
    return {'prime':p,'stages':stages,'remaining_parameters':sorted(active)}


def restricted_rows(data,active):
    kept={j for j,label in enumerate(data['labels'])
          if label['indices'][0]in active and (label['kind']=='a*c' or label['indices'][1]in active)}
    rows={m:{j:c for j,c in row.items()if j in kept}for m,row in data['rows'].items()}
    return {m:row for m,row in rows.items()if row},kept


def exact_components(data):
    results=[]
    for component in range(5):
        active=set(range(15*component,15*component+15));stages=[]
        for iteration in range(2):
            rows,kept=restricted_rows(data,active);pivots=arithmetic.exact_row_basis(rows);duals=[]
            for i in sorted(active):
                j=next(j for j,label in enumerate(data['labels'])if label['kind']=='a*a' and label['indices']==[i,i])
                rem,track=arithmetic.exact_reduce({j:Q(1)},pivots)
                if rem:continue
                dual=poly.scale(track,-1)
                assert base.total(poly.scale(rows[m],c)for m,c in dual.items())=={j:Q(1)}
                duals.append({'parameter_index':i,'dual':encode(dual)})
            assert len(duals)==(5 if iteration==0 else 10)
            stages.append({'active_parameters':sorted(active),'active_rows':len(rows),'columns':len(kept),'rank':len(pivots),'square_duals':duals})
            active-={d['parameter_index']for d in duals}
        assert not active
        results.append({'component':BASE[component],'base_name':NAMES[component],'stages':stages,'remaining_parameters':[]})
    return results


def map_digest(data):
    digest=hashlib.sha256()
    for label,column in zip(data['labels'],data['columns']):
        digest.update((json.dumps({'label':label,'polynomial':encode(column)},sort_keys=True,separators=(',',':'))+'\n').encode())
    return digest.hexdigest()


def modular_subset(data,active,p=1009):
    rows,kept=restricted_rows(data,set(active));pivots={}
    for m,row in sorted(rows.items(),key=lambda z:(len(z[1]),z[0])):
        v=arithmetic.mod_reduce({j:arithmetic.modq(c,p)for j,c in row.items()},pivots,p)
        if v:
            j=min(v);scale=pow(v[j],-1,p);pivots[j]={k:c*scale%p for k,c in v.items()}
    squares=[]
    for i in active:
        j=next(j for j,l in enumerate(data['labels'])if l['kind']=='a*a'and l['indices']==[i,i])
        if not arithmetic.mod_reduce({j:1},pivots,p):squares.append(i)
    return {'prime':p,'active_parameters':list(active),'active_rows':len(rows),'columns':len(kept),
            'rank_mod_prime':len(pivots),'isolated_square_indices_mod_prime':squares}


def projection_checks(data):
    fields=[];checks=0
    for i in range(6):
        for j in range(i+1,6):
            for m in base.monomials(7+base.WEIGHTS[i]+base.WEIGHTS[j]-8):
                field=[{}for _ in range(6)];mult={m:Q(1)}
                field[i]=poly.mul(mult,data['grad'][j]);field[j]=poly.scale(poly.mul(mult,data['grad'][i]),-1)
                assert not base.contraction(field,data['G'])
                index=None;scale=Q(0)
                if i in BASE and j in BASE:
                    k=next(k for k in BASE if m[k])
                    index=data['correction_labels'].index({'kind':'linear_base_pair','pair':[i,j],'linear_coordinate':k});scale=Q(1,4)
                elif m[2]:
                    k=j if i==2 else i
                    index=data['correction_labels'].index({'kind':'t_mixed','coordinate':k});scale=Q(-1,4)if i==2 else Q(1,4)
                for e,E in enumerate(data['Es']):
                    projected=arithmetic.even(base.B(E,field),data['q'],data['h'])
                    expected={}if index is None else poly.scale(data['mixed'][55*e+index],scale)
                    assert projected==expected;checks+=1
                fields.append({'pair':[i,j],'multiplier_powers':list(m),'compact_generator_index':index,'compact_scale':str(scale)})
    quotient=[]
    for m in base.monomials(6):
        assert not arithmetic.even(poly.mul({m:Q(1)},data['G']),data['q'],data['h'])
        quotient.append(list(m))
    assert len(fields)==230 and checks==17250 and len(quotient)==246
    return {'raw_field_labels':fields,'raw_field_count':230,'raw_projection_identities':checks,
            'quotient_monomials':quotient,'quotient_projection_identities':246,
            'compact_generators':data['correction_labels'],'compact_generator_count':55,
            'compact_physical_fields':'4*x_k*(G_j*d_i-G_i*d_j); 2*(2Z+Q)*(G_Z*d_i-G_i*d_Z)',
            'compact_images':'E*W_ij(x_k)-x_k*W_ij(E); E*Delta_i-2*Delta*E_i'}


def calculate():
    data=system();component_proofs=exact_components(data);projection=projection_checks(data)
    component_rescaling_checks=0
    pure_index={tuple(label['indices']):j for j,label in enumerate(data['labels'][:2850])}
    for c,i in enumerate(BASE):
        R0=poly.scale(poly.add(poly.mul(data['beta'],poly.derivative(data['dd'][i],i)),
                              poly.mul(poly.derivative(data['beta'],i),data['dd'][i]),-1),4)
        for j in range(15*c,15*c+15):
            for k in range(j,15*c+15):
                product={tuple(a+b for a,b in zip(data['basis'][j]['quadratic_powers'],data['basis'][k]['quadratic_powers'])):Q(1 if j==k else 2)}
                assert data['residuals'][pure_index[(j,k)]]==poly.mul(product,R0)
                component_rescaling_checks+=1
    assert component_rescaling_checks==600
    full=modular_subset(data,list(range(75)))
    divisible=[i for i,b in enumerate(data['basis'])if b['quadratic_powers'][b['component']]]
    divisible_screen=modular_subset(data,divisible)
    assert not full['isolated_square_indices_mod_prime'] and not divisible_screen['isolated_square_indices_mod_prime']
    minor_rows=[]
    for b in data['basis']:
        m=b['quadratic_powers'][:];m[b['component']]+=5;minor_rows.append(tuple(m))
    assert len(set(minor_rows))==75
    assert all(arithmetic.modq(E.get(m,Q(0)),5)==int(i==j)
               for i,m in enumerate(minor_rows)for j,E in enumerate(data['Es']))
    Gmod={m:arithmetic.modq(c,5)for m,c in data['G'].items()if arithmetic.modq(c,5)}
    assert Gmod=={tuple((2 if i==2 else 6)*int(k==i)for k in range(6)):1 for i in range(6)}
    squareterms=sum(len(d['dual'])for f in component_proofs for s in f['stages']for d in s['square_duals'])
    return {'schema':'cyclic-fano-quadratic-polars-v1','status':'PASS',
            'instance':'cyclic-triple-fano','q':1,'degree':7,
            'source_commit':'d96911d725077e66a8f10848908be01a643b1714',
            'source_instance_sha256':poly.sha(base.SOURCE/'source/instance.rec'),
            'producer_sha256':poly.sha(Path(__file__)),
            'dependencies':{'cyclic_fano_linear_polars.py':poly.sha(Path(arithmetic.__file__)),
                            'cyclic_fano_transfer.py':poly.sha(Path(base.__file__)),
                            'quadric_contact_pilot.py':poly.sha(Path(poly.__file__))},
            'spatial_variables':['X0','X1','Z','Y0','Y1','Y2'],'base_variables':list(NAMES),
            'Delta':encode(data['delta']),'Q':encode(data['q']),'H':encode(data['h']),'beta':encode(data['beta']),
            'parameter_basis':data['basis'],
            'residual_formula':'4*(beta*L(L(Delta))-(L(beta)+beta*div(v))*L(Delta))',
            'single_component_residual':'For v=f*d_i, R=4*f^2*(beta*Delta_ii-beta_i*Delta_i); all derivatives of f cancel.',
            'single_component_rescaling_checks':component_rescaling_checks,
            'column_order':'First (i,j) with 0<=i<=j<75: B(E_i,P_j)+B(E_j,P_i), omitting the second term if i=j. Then parameter i=0..74 outer, compact correction j=0..54 inner.',
            'full_map':{'potential_rows':1820,'active_rows':len(data['rows']),'columns':6975,
                        'pure_quadratic_columns':2850,'mixed_columns':4125,
                        'coefficient_sha256':map_digest(data),'serialization':'For every column in order, JSON {label,polynomial} with sorted keys and compact separators, followed by LF; coefficients are rational strings and monomials sorted lexicographically.'},
            'projection':projection,'full_modular_screen':full,'coordinate_divisible_modular_screen':divisible_screen,
            'component_family_exclusions':component_proofs,
            'square_dual_count':75,'square_dual_nonzero_terms':squareterms,
            'injectivity':{'prime':5,'coefficient_rows':[list(m)for m in minor_rows],
                           'matrix_mod_prime':'identity_75','determinant_mod_prime':1,
                           'consequence':'The75 polars are linearly independent over Q and C; every nonzero direction gives a nonzero base polynomial and hence a nonzero monic remainder modulo G.'},
            'regular_sequence_control':{'prime':5,'G_mod_prime':[{'powers':list(m),'coefficient':c}for m,c in sorted(Gmod.items())]},
            'attempts':[{'id':'full75','bound_seconds':120,'status':'unresolved','observation':'No individual coordinate square in rowspace modulo1009; no characteristic-zero exclusion inferred.'},
                        {'id':'coordinate_divisible25','bound_seconds':120,'status':'unresolved','observation':'v_i=x_i*l_i: no individual coordinate square in rowspace modulo1009.'},
                        {'id':'five_single_component_families','bound_seconds':120,'status':'exactly_excluded','observation':'Each v=f*d_i with arbitrary homogeneous quadratic f is excluded in two exact square-elimination rounds, retaining every correction.'}],
            'conclusion':'For each of the five base coordinates i, every nonzero quadratic f gives an excluded denominator E=f*partial_i(Delta).',
            'limits':'The full75-parameter family and its25-parameter coordinate-divisible subfamily remain unresolved. Five component-family exclusions do not exclude their sums, unions of supports, or arbitrary degree-seven denominators. No solution or Lean proof.'}


def verify(expected):
    actual=json.loads((OUT/'packet.json').read_text(encoding='utf-8'));assert actual==expected
    changes=[]
    for key in ('parameter_basis','component_family_exclusions'):
        bad=copy.deepcopy(actual);bad[key]=bad[key][1:];changes.append(bad)
    bad=copy.deepcopy(actual);bad['projection']['raw_field_labels']=bad['projection']['raw_field_labels'][1:];changes.append(bad)
    bad=copy.deepcopy(actual);bad['projection']['quotient_monomials']=[];changes.append(bad)
    bad=copy.deepcopy(actual);bad['projection']['compact_generators']=bad['projection']['compact_generators'][:50];changes.append(bad)
    bad=copy.deepcopy(actual);bad['component_family_exclusions'][0]['stages'][0]['square_duals'][0]['dual'][0]['coefficient']='0';changes.append(bad)
    bad=copy.deepcopy(actual);bad['component_family_exclusions'][0]['stages'][1]['active_parameters']=[];changes.append(bad)
    bad=copy.deepcopy(actual);bad['full_map']['coefficient_sha256']='0'*64;changes.append(bad)
    bad=copy.deepcopy(actual);bad['injectivity']['determinant_mod_prime']=0;changes.append(bad)
    for bad in changes:
        try:assert bad==expected
        except AssertionError:pass
        else:raise AssertionError('Mutation accepted')
    save('validation.json',{'schema':'cyclic-fano-quadratic-polars-validation-v1','status':'PASS',
                           'producer_sha256':poly.sha(Path(__file__)),'packet_sha256':poly.sha(OUT/'packet.json'),
                           'E1_lifts':75,'residual_quadratic_columns':2850,'mixed_columns':4125,
                           'raw_projection_identities':17250,'quotient_identities':246,
                           'single_component_rescaling_identities':600,
                           'excluded_component_families':5,'exact_square_duals':75,
                           'negative_controls_rejected':len(changes)})


def save(name,data):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/name).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')


def main():
    assert __debug__,'Run without -O'
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['probe','_probe','exact-probe','_exact-probe','run','_run','verify','_verify']);args=parser.parse_args()
    if args.command in ('probe','exact-probe','run','verify'):
        try:r=subprocess.run([sys.executable,'-S',str(Path(__file__)),'_'+args.command],timeout=120)
        except subprocess.TimeoutExpired:
            save('probe-timeout.json',{'status':'timeout','bound_seconds':120});raise SystemExit(2)
        raise SystemExit(r.returncode)
    started=time.perf_counter()
    if args.command in ('_run','_verify'):
        result=calculate()
        if args.command=='_run':save('packet.json',result)
        else:verify(result)
        print(json.dumps({'status':'PASS','command':args.command,'seconds':time.perf_counter()-started,'packet_sha256':poly.sha(OUT/'packet.json')}));return
    data=system();print(json.dumps({'construction_seconds':time.perf_counter()-started,'rows':len(data['rows']),'columns':len(data['columns'])}),flush=True)
    result=modular_probe(data)if args.command=='_probe'else exact_components(data)
    save('probe.json'if args.command=='_probe'else'component-exact-probe.json',result)
    print(json.dumps({'seconds':time.perf_counter()-started,'status':'PASS'}))


if __name__=='__main__':main()
