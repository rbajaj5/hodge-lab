#!/usr/bin/env python3
"""Bounded exact degree-eight polars from cubic base-vector directions."""
from pathlib import Path
from fractions import Fraction as Q
import argparse
import copy
import gzip
import hashlib
import itertools
import json
import subprocess
import sys
import time
import cyclic_fano_linear_polars as arithmetic

base=arithmetic.base;poly=base.poly
BASE=arithmetic.BASE;NAMES=arithmetic.NAMES;ZERO=(0,)*6
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/cyclic-fano-cubic-polars'
encode=arithmetic.encode


def save(name,value):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')


def base_monomials(degree):return [m for m in base.monomials(degree)if m[2]==0]


def prepare():
    F,A,G,beta=base.target()
    q={m[:2]+(0,)+m[3:]:c for m,c in G.items()if m[2]==1}
    h={m:c for m,c in G.items()if not m[2]}
    delta=poly.add(poly.mul(q,q),h,-4)
    grad=[poly.derivative(G,i)for i in range(6)]
    dd=[poly.derivative(delta,i)for i in range(6)]
    Es=[];Ps=[];basis=[]
    for i in BASE:
        for m in base_monomials(3):
            mult={m:Q(1)};E=poly.mul(mult,dd[i]);P=[{}for _ in range(6)]
            P[i]=poly.scale(poly.mul(beta,mult),-4)
            P[2]=poly.scale(poly.mul(poly.mul(beta,mult),poly.derivative(q,i)),2)
            assert base.contraction(P,G)==poly.mul(beta,E)
            assert base.contraction(base.lift(P),F)==poly.mul(A,base.pullback(E))
            Es.append(E);Ps.append(P);basis.append({'component':i,'cubic_powers':list(m)})
    assert len(Es)==175 and len(base_monomials(3))==35
    correction_labels=[]
    for i,j in itertools.combinations(BASE,2):
        for m in base_monomials(2):correction_labels.append({'kind':'quadratic_base_pair','pair':[i,j],'multiplier_powers':list(m)})
    for i in BASE:
        for k in BASE:correction_labels.append({'kind':'linear_t_mixed','coordinate':i,'linear_coordinate':k})
    assert len(correction_labels)==175
    return locals()


def correction_columns(E,data):
    dd=data['dd'];delta=data['delta'];ed=[poly.derivative(E,i)for i in range(6)];cols=[]
    for label in data['correction_labels']:
        if label['kind']=='quadratic_base_pair':
            i,j=label['pair'];h={tuple(label['multiplier_powers']):Q(1)}
            W=poly.add(poly.mul(dd[i],ed[j]),poly.mul(dd[j],ed[i]),-1)
            Wh=poly.add(poly.mul(dd[i],poly.derivative(h,j)),poly.mul(dd[j],poly.derivative(h,i)),-1)
            C=poly.add(poly.mul(E,Wh),poly.mul(h,W),-1)
        else:
            i=label['coordinate'];k=label['linear_coordinate'];h={tuple(int(l==k)for l in range(6)):Q(1)}
            C=poly.mul(h,poly.add(poly.mul(E,dd[i]),poly.mul(delta,ed[i]),-2))
            if i==k:C=poly.add(C,poly.mul(E,delta),2)
        assert all(m[2]==0 and sum(m)==14 for m in C)
        cols.append(C)
    return cols


def fixed_columns(direction,data=None):
    data=prepare()if data is None else data
    direction={int(i):Q(c)for i,c in direction.items()if c}
    assert direction and all(0<=i<175 for i in direction)
    E=base.total(poly.scale(data['Es'][i],c)for i,c in direction.items())
    P=[base.total(poly.scale(data['Ps'][i][j],c)for i,c in direction.items())for j in range(6)]
    assert E and base.contraction(P,data['G'])==poly.mul(data['beta'],E)
    cols=correction_columns(E,data);rhs=poly.scale(base.B(E,P),-1)
    return cols,rhs,{'direction':[[i,str(c)]for i,c in sorted(direction.items())],
                     'denominator':encode(E),'correction_types':175,'quotient_directions':636,
                     'scope':'Complete reflection-even necessary E2 system for this fixed admissible degree-eight polar.'}


def system(active,data=None):
    data=prepare()if data is None else data;active=list(active);columns=[];labels=[]
    for i,j in itertools.combinations_with_replacement(active,2):
        R=base.B(data['Es'][i],data['Ps'][j])
        if i!=j:R=poly.add(R,base.B(data['Es'][j],data['Ps'][i]))
        assert all(m[2]==0 and sum(m)==14 for m in R)
        columns.append(R);labels.append({'kind':'a*a','indices':[i,j]})
    for i in active:
        for k,C in enumerate(correction_columns(data['Es'][i],data)):
            columns.append(C);labels.append({'kind':'a*c','indices':[i,k]})
    rows={}
    for j,column in enumerate(columns):
        for m,c in column.items():rows.setdefault(m,{})[j]=c
    return {'active_raw_parameter_indices':active,'columns':columns,'labels':labels,'rows':rows}


def restrict(system,active):
    active=set(active)
    kept={j for j,label in enumerate(system['labels'])if label['indices'][0]in active and(label['kind']=='a*c'or label['indices'][1]in active)}
    rows={m:{j:c for j,c in row.items()if j in kept}for m,row in system['rows'].items()}
    return {m:r for m,r in rows.items()if r},kept


def component(component,data=None):
    data=prepare()if data is None else data
    active=list(range(35*component,35*(component+1)));s=system(active,data);stages=[]
    for round_index in range(5):
        rows,kept=restrict(s,active);pivots=arithmetic.exact_row_basis(rows);duals=[]
        for i in active:
            j=next(j for j,label in enumerate(s['labels'])if label['kind']=='a*a'and label['indices']==[i,i])
            rem,track=arithmetic.exact_reduce({j:Q(1)},pivots)
            if rem:continue
            dual=poly.scale(track,-1)
            assert base.total(poly.scale(rows[m],c)for m,c in dual.items())=={j:Q(1)}
            duals.append({'raw_parameter_index':i,'dual':encode(dual)})
        stages.append({'active_raw_parameter_indices':active,'rows':len(rows),'columns':len(kept),'rank':len(pivots),'square_duals':duals})
        print(json.dumps({'component':component,'round':round_index,'n':len(active),'rank':len(pivots),'squares':len(duals)}),flush=True)
        active=[i for i in active if i not in {d['raw_parameter_index']for d in duals}]
        if not active or not duals:break
    return {'status':'completed','component':BASE[component],'component_index':component,
            'scope':'All other vector components are identically zero; cubic multiplier in this component is arbitrary.',
            'stages':stages,'remaining_raw_parameter_indices':active,
            'conclusion':'excluded'if not active else'unresolved'}


def necessary(component_index,active=None):
    active=list(range(35*component_index,35*(component_index+1)))if active is None else list(active);data=system(active)
    pure_count=len(active)*(len(active)+1)//2
    pure=list(range(pure_count));mixed=list(range(pure_count,len(data['columns'])));order=mixed+pure;lookup={j:k for k,j in enumerate(order)}
    rows={m:{lookup[j]:c for j,c in row.items()}for m,row in data['rows'].items()}
    pivots=arithmetic.exact_row_basis(rows);equations=[]
    for j,(row,track)in sorted(pivots.items()):
        if j<len(mixed):continue
        assert base.total(poly.scale(rows[m],c)for m,c in track.items())==row
        terms=[]
        for k,c in sorted(row.items()):
            a,b=data['labels'][order[k]]['indices'];terms.append([active.index(a),active.index(b),str(c)])
        equations.append({'terms':terms,'dual':encode(track)})
    return {'active_raw_parameter_indices':active,'rows':len(rows),'columns':len(order),'rank':len(pivots),
            'mixed_rank':sum(j<len(mixed)for j in pivots),'equations':equations}


def reduce_quadrics(stage):
    rows=[{(i,j):Q(c)for i,j,c in e['terms']}for e in stage['equations']]
    pivots=arithmetic.exact_row_basis(dict(enumerate(rows)));reduced={}
    for key,(row,track)in sorted(pivots.items(),reverse=True):
        row=row.copy();track=track.copy()
        for pivot,(old,oldtrack)in sorted(reduced.items()):
            c=row.get(pivot,Q(0))
            if c:row=poly.add(row,old,-c);track=poly.add(track,oldtrack,-c)
        assert base.total(poly.scale(rows[i],c)for i,c in track.items())==row
        reduced[key]=(row,track)
    return {'active_raw_parameter_indices':stage['active_raw_parameter_indices'],
            'equations':[{'terms':[[i,j,str(c)]for(i,j),c in sorted(row.items())],'combination':[[i,str(c)]for i,c in sorted(track.items())]}for _,(row,track)in sorted(reduced.items())]}


def cubic_search(stage,threshold):
    n=len(stage['active_raw_parameter_indices']);rows={};indices=[]
    for qi,e in enumerate(stage['equations']):
        if len(e['terms'])>threshold:continue
        indices.append(qi)
        for k in range(n):rows[(qi,k)]={tuple(sorted((i,j,k))):Q(c)for i,j,c in e['terms']}
    pivots=arithmetic.exact_row_basis(rows);proofs=[]
    for i in range(n):
        rem,track=arithmetic.exact_reduce({(i,i,i):Q(1)},pivots)
        if rem:continue
        track=poly.scale(track,-1)
        assert base.total(poly.scale(rows[j],c)for j,c in track.items())=={(i,i,i):Q(1)}
        proofs.append({'parameter_index':i,'power':3,'multipliers':[{'equation_index':q,'linear_variable':k,'coefficient':str(c)}for(q,k),c in sorted(track.items())]})
    return {'status':'completed','active_raw_parameter_indices':stage['active_raw_parameter_indices'],'term_threshold':threshold,
            'equation_indices':indices,'rank':len(pivots),'columns':len(rows),'identities':proofs}


def stage_prefix(component,round_index):return f'component-{component}-'+(f'round-{round_index:02d}-'if round_index else'')


def raw_sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_compressed(name):return json.loads(gzip.decompress((OUT/name).read_bytes()))


def rebuild_diagnostic(old,new):
    oldactive=old['active_raw_parameter_indices'];newactive=new['active_raw_parameter_indices']
    keep={oldactive.index(raw):i for i,raw in enumerate(newactive)};restricted=[]
    for e in old['equations']:
        restricted.append({(keep[a],keep[b]):Q(c)for a,b,c in e['terms']if a in keep and b in keep})
    newrows=[{(a,b):Q(c)for a,b,c in e['terms']}for e in new['equations']]
    newbasis=rational_basis(newrows);oldrank=len(rational_basis(restricted))
    assert all(not rational_remainder(r,newbasis)for r in restricted)
    return {'restricted_old_rank':oldrank,'fresh_rebuilt_rank':len(newbasis),
            'additional_independent_quadrics':len(newbasis)-oldrank,'span_inclusion':True}


def manifest():
    data=prepare();families=[];attempts=[]
    for i in range(5):
        stages=[]
        for r in range(2):
            pref=stage_prefix(i,r);names=[pref+'necessary.json.gz',pref+'reduced.json.gz',pref+'cubic-64.json']
            physical=load_compressed(names[0]);proof=json.loads((OUT/names[2]).read_text())
            stages.append({'round':r,'physical_file':names[0],'physical_sha256':raw_sha(OUT/names[0]),
                           'reduced_file':names[1],'reduced_sha256':raw_sha(OUT/names[1]),
                           'cubic_file':names[2],'cubic_sha256':poly.sha(OUT/names[2]),
                           'parameters':len(physical['active_raw_parameter_indices']),
                           'physical_rows':physical['rows'],'physical_columns':physical['columns'],
                           'rank':physical['rank'],'mixed_rank':physical['mixed_rank'],
                           'necessary_quadrics':len(physical['equations']),
                           'forced_raw_parameters':[physical['active_raw_parameter_indices'][v['parameter_index']]for v in proof['identities']]})
        gain=rebuild_diagnostic(load_compressed(stages[0]['physical_file']),load_compressed(stages[1]['physical_file']))
        families.append({'component_index':i,'component':BASE[i],'base_name':NAMES[i],'stages':stages,'rebuild_diagnostic':gain,
                         'remaining_raw_parameter_indices':[],'conclusion':'excluded conditionally on the other four vector components being zero'})
    for f in sorted(OUT.glob('*.json')):
        if f.name in ('packet.json','validation.json','independent-validation.json'):continue
        a=json.loads(f.read_text());attempts.append({'file':f.name,'sha256':poly.sha(f),'status':a.get('status','completed')})
    return {'schema':'cyclic-fano-cubic-polars-v1','status':'five_component_families_excluded_full_family_open',
            'instance':'cyclic-triple-fano','q':1,'degree':8,'source_commit':'d96911d725077e66a8f10848908be01a643b1714',
            'source_instance_sha256':poly.sha(base.SOURCE/'source/instance.rec'),'producer_sha256':poly.sha(Path(__file__)),
            'dependencies':{Path(m.__file__).name:poly.sha(Path(m.__file__))for m in (arithmetic,base,poly)},
            'spatial_variables':['X0','X1','Z','Y0','Y1','Y2'],'base_variables':list(NAMES),
            'parameter_basis':[{**b,'E':encode(E),'particular':[encode(p)for p in P]}for b,E,P in zip(data['basis'],data['Es'],data['Ps'])],
            'Delta':encode(data['delta']),'Q':encode(data['q']),'H':encode(data['h']),'beta':encode(data['beta']),
            'projection':projection_checks(data),'component_families':families,'attempts':attempts,
            'full_family_dimensions':{'parameters':175,'potential_rows':3060,'pure_quadratic_columns':15400,'mixed_columns':30625,'formal_columns':46025,'full_map_constructed':False},
            'bounds':{'individual_discovery_seconds':120,'aggregate_primary_verify_seconds':600},
            'conclusion':'For each fixed base coordinate i, every nonzero homogeneous cubic f gives an excluded degree-eight denominator E=f*partial_i(Delta), with all compatible numerator corrections allowed.',
            'limits':'The five conditional35-parameter exclusions do not exclude the full175-parameter mixed-component family, sums of different component directions, or arbitrary degree-eight denominators. No certificate or Lean proof is claimed. The full46025-column map was not constructed in this bounded batch.'}


def rational_basis(rows):
    pivots={}
    for row in sorted(rows,key=len):
        row=row.copy()
        while row:
            k=min(row)
            if k not in pivots:pivots[k]=poly.scale(row,1/row[k]);break
            row=poly.add(row,pivots[k],-row[k])
    return pivots


def rational_remainder(row,basis):
    row=row.copy()
    while row:
        k=min(row)
        if k not in basis:break
        row=poly.add(row,basis[k],-row[k])
    return row


def replay_cubes(reduced,proof,check_rank=True):
    n=len(reduced['active_raw_parameter_indices']);assert proof['active_raw_parameter_indices']==reduced['active_raw_parameter_indices']
    indices=[i for i,e in enumerate(reduced['equations'])if len(e['terms'])<=proof['term_threshold']]
    assert indices==proof['equation_indices']and proof['columns']==len(indices)*n
    for identity in proof['identities']:
        out={}
        for term in identity['multipliers']:
            q=term['equation_index'];k=term['linear_variable'];assert q in indices and 0<=k<n
            out=poly.add(out,{tuple(sorted((a,b,k))):Q(c)*Q(term['coefficient'])for a,b,c in reduced['equations'][q]['terms']})
        i=identity['parameter_index'];assert identity['power']==3 and out=={(i,i,i):Q(1)}
    if check_rank:
        rows=[{tuple(sorted((a,b,k))):Q(c)for a,b,c in reduced['equations'][i]['terms']}for i in indices for k in range(n)]
        pivots=rational_basis(rows);assert len(pivots)==proof['rank']
        found=[i for i in range(n)if not rational_remainder({(i,i,i):Q(1)},pivots)]
        assert found==[i['parameter_index']for i in proof['identities']]


def replay_stage(physical,reduced,proof,data):
    active=physical['active_raw_parameter_indices'];s=system(active,data);n=len(active);pure=n*(n+1)//2
    assert(physical['rows'],physical['columns'])==(len(s['rows']),len(s['columns']))
    basis=rational_basis(s['rows'].values());assert len(basis)==physical['rank']
    mixed=rational_basis([{j:c for j,c in r.items()if j>=pure}for r in s['rows'].values()]);assert len(mixed)==physical['mixed_rank']
    square_queries=[]
    for i,raw in enumerate(active):
        j=next(j for j,l in enumerate(s['labels'])if l=={'kind':'a*a','indices':[raw,raw]})
        if not rational_remainder({j:Q(1)},basis):square_queries.append(raw)
    qs=[];pairings=0
    for e in physical['equations']:
        dual={tuple(t['powers']):Q(t['coefficient'])for t in e['dual']}
        result=base.total(poly.scale(s['rows'][m],c)for m,c in dual.items());expected={}
        for a,b,c in e['terms']:
            j=s['labels'].index({'kind':'a*a','indices':[active[a],active[b]]});expected[j]=Q(c)
        assert result==expected;pairings+=sum(len(s['rows'][m])for m in dual)
        qs.append({(a,b):Q(c)for a,b,c in e['terms']})
    assert len(qs)==physical['rank']-physical['mixed_rank']
    assert reduced['active_raw_parameter_indices']==active and len(reduced['equations'])==len(qs)
    reduced_rows=[]
    for e in reduced['equations']:
        row={(a,b):Q(c)for a,b,c in e['terms']}
        assert base.total(poly.scale(qs[i],Q(c))for i,c in e['combination'])==row
        reduced_rows.append(row)
    assert len(rational_basis(reduced_rows))==len(qs)
    replay_cubes(reduced,proof)
    return {'physical_duals':len(qs),'coefficient_pairings':pairings,'rank':len(basis),'mixed_rank':len(mixed),
            'square_query_hits':square_queries,'cube_identities':len(proof['identities']),
            'multiplier_terms':sum(len(i['multipliers'])for i in proof['identities'])}


def verify_packet(packet):
    expected=manifest();assert packet==expected;data=prepare();checks=[];controls=0
    for family in packet['component_families']:
        active=list(range(35*family['component_index'],35*(family['component_index']+1)));stages=[]
        for info in family['stages']:
            physical=load_compressed(info['physical_file']);reduced=load_compressed(info['reduced_file']);proof=json.loads((OUT/info['cubic_file']).read_text())
            assert physical['active_raw_parameter_indices']==active
            check=replay_stage(physical,reduced,proof,data);stages.append(check)
            if info['round']==0:
                probe=json.loads((OUT/f"component-{family['component_index']}-probe.json").read_text())
                assert not check['square_query_hits']and not probe['stages'][0]['square_duals']and probe['conclusion']=='unresolved'
                assert probe['stages'][0]['rank']==check['rank']
            bad=copy.deepcopy(proof);bad['identities'][0]['multipliers'][0]['coefficient']='0'
            try:replay_cubes(reduced,bad,False)
            except AssertionError:controls+=1
            else:raise AssertionError('Corrupt cube accepted')
            forced={i['parameter_index']for i in proof['identities']};active=[raw for i,raw in enumerate(active)if i not in forced]
            if info['round']==0:assert len(active)==10 and all(max(data['basis'][raw]['cubic_powers'])==1 for raw in active)
        assert not active;checks.append({'component':family['component'],'stages':stages,'remaining_parameters':active})
        print(json.dumps({'component':family['base_name'],'status':'PASS'}),flush=True)
    for key in ('producer_sha256','source_instance_sha256','projection','parameter_basis'):
        bad=copy.deepcopy(packet);bad[key]=None
        try:assert bad==expected
        except AssertionError:controls+=1
        else:raise AssertionError('Corrupt binding accepted')
    save('validation.json',{'status':'PASS','producer_sha256':poly.sha(Path(__file__)),'packet_sha256':poly.sha(OUT/'packet.json'),
                           'components':checks,'negative_controls_rejected':controls,'projection_operator_checks':3150,
                           'universal_correction_relations':25,'full_family_remaining_open':True})


def projection_checks(data):
    fields=[];checks=0
    for i,j in itertools.combinations(range(6),2):
        for m in base.monomials(8+base.WEIGHTS[i]+base.WEIGHTS[j]-8):
            mult={m:Q(1)};field=[{}for _ in range(6)]
            field[i]=poly.mul(mult,data['grad'][j]);field[j]=poly.scale(poly.mul(mult,data['grad'][i]),-1)
            assert not base.contraction(field,data['G'])
            index=None;scale=Q(0);components=[{}for _ in range(6)];div={}
            if i in BASE and j in BASE:
                label={'kind':'quadratic_base_pair','pair':[i,j],'multiplier_powers':list(m)}
                index=data['correction_labels'].index(label);scale=Q(1,4)
                components[i]=poly.scale(poly.mul(mult,data['dd'][j]),-1)
                components[j]=poly.mul(mult,data['dd'][i])
                div=poly.add(poly.mul(data['dd'][i],poly.derivative(mult,j)),poly.mul(data['dd'][j],poly.derivative(mult,i)),-1)
            elif m[2]:
                a=j if i==2 else i;k=next(k for k in BASE if m[k]);h={tuple(int(l==k)for l in range(6)):Q(1)}
                index=data['correction_labels'].index({'kind':'linear_t_mixed','coordinate':a,'linear_coordinate':k})
                scale=Q(-1,4)if i==2 else Q(1,4)
                components[a]=poly.scale(poly.mul(h,data['delta']),2)
                div=poly.mul(h,data['dd'][a])
                if a==k:div=poly.add(div,data['delta'],2)
            assert arithmetic.even(base.div(field),data['q'],data['h'])==poly.scale(div,scale);checks+=1
            for a in BASE:
                assert arithmetic.even(field[a],data['q'],data['h'])==poly.scale(components[a],scale);checks+=1
            fields.append({'pair':[i,j],'multiplier_powers':list(m),'compact_index':index,'compact_scale':str(scale)})
    quotients=base.monomials(8)
    for m in quotients:assert not arithmetic.even(poly.mul({m:Q(1)},data['G']),data['q'],data['h'])
    assert len(fields)==525 and checks==3150 and len(quotients)==636
    minor_rows=[]
    for b in data['basis']:
        m=b['cubic_powers'][:];m[b['component']]+=5;minor_rows.append(tuple(m))
    assert len(set(minor_rows))==175
    assert all(arithmetic.modq(E.get(m,Q(0)),5)==int(i==j)for i,m in enumerate(minor_rows)for j,E in enumerate(data['Es']))
    euler_checks=0
    for m in base.monomials(6):
        S={m:Q(1)};normalizer=[]
        for i,w in enumerate(base.WEIGHTS):
            power=list(m);power[i]+=1;normalizer.append({tuple(power):Q(w,6)})
        assert base.contraction(normalizer,data['G'])==poly.mul(S,data['G'])
        assert base.div(normalizer)==poly.scale(S,Q(7,3));euler_checks+=1
    for E in data['Es']:
        assert all(sum(w*a for w,a in zip(base.WEIGHTS,m))==8 for m in E)
    Gmod={m:arithmetic.modq(c,5)for m,c in data['G'].items()if arithmetic.modq(c,5)}
    assert Gmod=={tuple((2 if i==2 else 6)*int(k==i)for k in range(6)):1 for i in range(6)}
    relations=[]
    for i in BASE:
        for k in BASE:
            terms=[];constant={};coefficients={j:{}for j in BASE}
            for j in BASE:
                if i==j:continue
                m=tuple(int(l==j)+int(l==k)for l in range(6));h={m:Q(1)}
                a,b=sorted((i,j));sign=1 if i<j else-1
                index=data['correction_labels'].index({'kind':'quadratic_base_pair','pair':[a,b],'multiplier_powers':list(m)})
                terms.append([index,str(sign)])
                constant=poly.add(constant,poly.add(poly.mul(data['dd'][i],poly.derivative(h,j)),poly.mul(data['dd'][j],poly.derivative(h,i)),-1))
                coefficients[j]=poly.add(coefficients[j],poly.mul(h,data['dd'][i]),-1)
                coefficients[i]=poly.add(coefficients[i],poly.mul(h,data['dd'][j]))
            xk={tuple(int(l==k)for l in range(6)):Q(1)}
            mixed=data['correction_labels'].index({'kind':'linear_t_mixed','coordinate':i,'linear_coordinate':k});terms.append([mixed,'3'])
            constant=poly.add(constant,poly.mul(xk,data['dd'][i]),3)
            if i==k:constant=poly.add(constant,data['delta'],6)
            coefficients[i]=poly.add(coefficients[i],poly.mul(xk,data['delta']),-6)
            factor=poly.mul(xk,data['dd'][i]);assert constant==poly.scale(factor,8)
            for j in BASE:
                xj={tuple(int(l==j)for l in range(6)):Q(1)}
                assert coefficients[j]==poly.scale(poly.mul(factor,xj),-1)
            relations.append({'coordinate':i,'linear_coordinate':k,'terms':terms})
    return {'raw_field_labels':fields,'raw_field_count':525,'operator_coefficient_checks':checks,
            'compact_labels':data['correction_labels'],'compact_count':175,'quotient_monomials':[list(m)for m in quotients],
            'Euler_gauge_count':euler_checks,'denominator_homogeneity_checks':175,'Euler_identity_count_implied':175*euler_checks,
            'Euler_identity':'For S of weight6 and E of weight8, B_E(S*weightedEuler/6)=E*S.',
            'regular_sequence_mod5':'G reduces to Z^2+sum(base_coordinate^6); its gradient vanishes only at the origin.',
            'universal_correction_relations':relations,'correction_rank_upper_bound':150,
            'relation_operator_identity':'sum_j C_base(E,x_j*x_k*W_ij)+3*C_mixed_ik(E)=x_k*Delta_i*(8*E-baseEuler(E))=0 for homogeneous E of degree8.',
            'injectivity_rows_mod5':[list(m)for m in minor_rows],'injectivity_minor_mod5':'identity175',
            'scope':'Projected divergence and five base components determine B_E on every base denominator, so these operator identities cover all175 directions simultaneously.'}


def main():
    assert __debug__
    p=argparse.ArgumentParser();p.add_argument('command',choices=['component','_component','projection','_projection','necessary','_necessary','cubic','_cubic','run','_run','verify','_verify']);p.add_argument('--component',type=int,default=0);p.add_argument('--round',type=int,default=0);p.add_argument('--bound',type=int,default=120);p.add_argument('--threshold',type=int,default=64);args=p.parse_args()
    assert 0<=args.component<5
    if not args.command.startswith('_'):
        started=time.perf_counter()
        if args.command in ('run','verify'):args.bound=600
        try:r=subprocess.run([sys.executable,'-S',str(Path(__file__)),'_'+args.command,'--component',str(args.component),'--threshold',str(args.threshold),'--round',str(args.round)],timeout=args.bound)
        except subprocess.TimeoutExpired:
            save(stage_prefix(args.component,args.round)+args.command+'-timeout.json',{'status':'timeout','bound_seconds':args.bound,'elapsed_seconds':time.perf_counter()-started,'limits':'No completed family exclusion or rank follows.'});raise SystemExit(2)
        raise SystemExit(r.returncode)
    started=time.perf_counter()
    if args.command in ('_run','_verify'):
        if args.command=='_run':save('packet.json',manifest())
        else:verify_packet(json.loads((OUT/'packet.json').read_text()))
        print(json.dumps({'status':'PASS','command':args.command[1:],'elapsed_seconds':time.perf_counter()-started,'packet_sha256':poly.sha(OUT/'packet.json')}));return
    if args.command=='_necessary':
        active=None
        if args.round:
            old=json.loads(gzip.decompress((OUT/(stage_prefix(args.component,args.round-1)+'reduced.json.gz')).read_bytes()))
            proof=json.loads((OUT/(stage_prefix(args.component,args.round-1)+f'cubic-{args.threshold}.json')).read_text())
            assert proof['active_raw_parameter_indices']==old['active_raw_parameter_indices']
            forced={p['parameter_index']for p in proof['identities']}
            active=[raw for i,raw in enumerate(old['active_raw_parameter_indices'])if i not in forced]
            assert active and len(active)<len(old['active_raw_parameter_indices'])
        result=necessary(args.component,active);reduced=reduce_quadrics(result)
        for name,value in [('necessary',result),('reduced',reduced)]:
            OUT.mkdir(parents=True,exist_ok=True);(OUT/(stage_prefix(args.component,args.round)+name+'.json.gz')).write_bytes(gzip.compress((json.dumps(value,separators=(',',':'))+'\n').encode(),mtime=0))
        summary={'status':'completed','component':args.component,'round':args.round,'parameters':len(result['active_raw_parameter_indices']),'rows':result['rows'],'columns':result['columns'],'rank':result['rank'],'mixed_rank':result['mixed_rank'],'quadrics':len(result['equations']),'elapsed_seconds':time.perf_counter()-started}
        save(stage_prefix(args.component,args.round)+'necessary-summary.json',summary);print(json.dumps(summary));return
    if args.command=='_cubic':
        stage=json.loads(gzip.decompress((OUT/(stage_prefix(args.component,args.round)+'reduced.json.gz')).read_bytes()))
        result=cubic_search(stage,args.threshold);result['elapsed_seconds']=time.perf_counter()-started
        save(stage_prefix(args.component,args.round)+f'cubic-{args.threshold}.json',result)
        print(json.dumps({'component':args.component,'threshold':args.threshold,'rank':result['rank'],'columns':result['columns'],'powers':[stage['active_raw_parameter_indices'][i['parameter_index']]for i in result['identities']],'elapsed_seconds':result['elapsed_seconds']}));return
    data=prepare()
    result=component(args.component,data)if args.command=='_component'else projection_checks(data)
    result['elapsed_seconds']=time.perf_counter()-started
    save('component-'+str(args.component)+'-probe.json'if args.command=='_component'else'projection-probe.json',result)
    print(json.dumps({k:v for k,v in result.items()if k not in ('stages','raw_field_labels','compact_labels','quotient_monomials','injectivity_rows_mod5')}))


if __name__=='__main__':main()
