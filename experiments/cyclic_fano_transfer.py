#!/usr/bin/env python3
"""Exact cyclic-character/Piola reduction and three fixed-denominator tests.

Only standard-library rational polynomial arithmetic is used. Generic sparse
arithmetic and elimination are reused from the recorded quartic pilot; no
quadric-contact target or conclusion is imported into this experiment.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse
import copy
import json
import subprocess
import sys
import time

import quadric_contact_pilot as poly

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'results/cyclic-fano-curve'
OUT=ROOT/'results/cyclic-fano-transfer'
WEIGHTS=(1,1,3,1,1,1)
ZERO=(0,)*6


def save(name,value):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')


def monomials(degree,weights=WEIGHTS):
    if degree<0:return []
    if len(weights)==1:return [(degree//weights[0],)]if degree%weights[0]==0 else []
    return [(a,)+tail for a in range(degree//weights[0],-1,-1)
            for tail in monomials(degree-a*weights[0],weights[1:])]


def total(values):
    out={}
    for value in values:out=poly.add(out,value)
    return out


def contraction(field,f):return total(poly.mul(n,poly.derivative(f,i))for i,n in enumerate(field))
def div(field):return total(poly.derivative(n,i)for i,n in enumerate(field))
def B(D,field):return poly.add(poly.mul(D,div(field)),contraction(field,D),-1)


def pullback(f):
    out={}
    for m,c in f.items():
        n=list(m);n[2]*=3;out[tuple(n)]=c
    return out


def lift(field):
    delta={(0,0,2,0,0,0):Q(3)}
    return [pullback(n)if i==2 else poly.mul(delta,pullback(n))for i,n in enumerate(field)]


def target():
    record=poly.fields(SOURCE/'source/instance.rec')
    frozen=json.loads((SOURCE/'target.json').read_text(encoding='utf-8'))
    assert frozen['target']==record and record['q']=='1'
    assert poly.sha(SOURCE/'source/instance.rec')==frozen['upstream_source_sha256']['data/cyclic-triple-fano/instance.rec']
    F=poly.parse(record['F']);A=poly.parse(record['A']);G={}
    for m,c in F.items():
        assert m[2]%3==0
        n=list(m);n[2]//=3;G[tuple(n)]=c
    density={(1,0,0,3,0,0):Q(1,3)}
    assert pullback(G)==F
    assert poly.mul({(0,0,2,0,0,0):Q(3)},pullback(density))==A
    return F,A,G,density


def candidates(G):
    return {'cyclic_branch_Z':{(0,0,1,0,0,0):Q(1)},
            'quadratic_branch_2Z_plus_Q':poly.derivative(G,2),
            'omitted_section_X1_cubed':{(0,3,0,0,0,0):Q(1)}}


def system(E,F,A,G,density):
    degree=3;delta={(0,0,2,0,0,0):Q(3)}
    D=pullback(E);columns=[];labels=[];transfers=0
    rhs_poly=poly.mul(density,E)
    rhs={('E1',)+m:c for m,c in rhs_poly.items()}
    for i,w in enumerate(WEIGHTS):
        for mon in monomials(degree+w-2):
            field=[{}for _ in WEIGHTS];field[i]={mon:Q(1)}
            n=lift(field)
            e1=contraction(field,G);e2=B(E,field)
            assert contraction(n,F)==poly.mul(delta,pullback(e1))
            assert div(n)==poly.mul(delta,pullback(div(field)))
            assert B(D,n)==poly.mul(delta,pullback(e2))
            assert all(sum(m)==degree+1 for component in n for m in component)
            columns.append({**{('E1',)+m:c for m,c in e1.items()},
                            **{('E2',)+m:c for m,c in e2.items()}})
            labels.append({'coordinate':i,'quotient_monomial':list(mon)})
            transfers+=1
    # E2 has weight 2*d-2=4, so no nonzero G-multiple (weight6) is possible.
    assert monomials(2*degree-8)==[]
    assert len(columns)==150
    rows=sorted(set(rhs).union(*(set(c)for c in columns)))
    return rows,columns,rhs,labels,transfers


def verify_dual(packet):
    dual={i:Q(c)for i,c in packet['dual']};rhs={i:Q(c)for i,c in packet['rhs']}
    assert sum(c*rhs.get(i,Q(0))for i,c in dual.items())==1
    for column in packet['columns']:
        assert sum(dual.get(i,Q(0))*Q(c)for i,c in column)==0


def calculate():
    F,A,G,density=target();packets=[]
    for label,E in candidates(G).items():
        rows,columns,rhs,labels,transfers=system(E,F,A,G,density)
        rank,dual,solution=poly.solve(rows,columns,rhs);index={row:i for i,row in enumerate(rows)}
        assert dual is not None,'A consistent candidate requires separate witness handling'
        item={'candidate':label,'weighted_denominator':poly.encode(E),'degree':3,
              'shape':[len(rows),len(columns)],'rank':rank,'augmented_rank':rank+1,
              'numerator_labels':labels,'coefficient_rows':[list(r)for r in rows],
              'columns':[[[index[r],str(c)]for r,c in sorted(col.items())]for col in columns],
              'rhs':[[index[r],str(c)]for r,c in sorted(rhs.items())],
              'dual':[[i,str(c)]for i,c in sorted(dual.items())],
              'complete_fixed_denominator_test':True,'piola_basis_vectors_checked':transfers,
              'quotient_coefficients':0,'consistent':False}
        verify_dual(item);packets.append(item)
    # Full homogeneous upstairs component monomials split by x2 exponent mod3.
    dims=[]
    for d in (3,4,6,7,9):
        upstairs=poly.monomials(d+1)
        selected=sum(sum(m[2]%3==(0 if i==2 else 2)for m in upstairs)for i in range(6))
        weighted=sum(len(monomials(d+w-2))for w in WEIGHTS)
        assert selected==weighted
        dims.append({'denominator_degree':d,'all_upstairs_numerator_coefficients':6*len(upstairs),
                     'character_projected_coefficients':selected,'weighted_coefficients':weighted})
    return {'schema':'cyclic-fano-character-transfer-v1','instance':'cyclic-triple-fano',
            'source_commit':'d96911d725077e66a8f10848908be01a643b1714',
            'source_sha256':poly.sha(SOURCE/'source/instance.rec'),
            'producer_sha256':poly.sha(Path(__file__)),'arithmetic_dependency_sha256':poly.sha(Path(poly.__file__)),
            'weights':list(WEIGHTS),'weighted_G':poly.encode(G),'weighted_density':poly.encode(density),
            'character_dimensions':dims,'tests':packets,
            'scope':'Exact fixed invariant denominator tests. No exclusion of powers, products, other denominators, or arbitrary degree. No support or certificate found.'}


def verify():
    packet=json.loads((OUT/'packet.json').read_text(encoding='utf-8'))
    assert packet==calculate()
    rejected=[]
    for item in packet['tests']:
        bad=copy.deepcopy(item);bad['dual'][0][1]=str(Q(bad['dual'][0][1])+1)
        try:verify_dual(bad)
        except AssertionError:rejected.append(item['candidate'])
        else:raise AssertionError('Changed dual accepted')
    receipt={'status':'PASS','packet_sha256':poly.sha(OUT/'packet.json'),
             'source_sha256':packet['source_sha256'],'exact_fixed_denominators':3,
             'basis_vector_transfers':450,'mutation_controls_rejected':rejected,
             'ranks':[[p['rank'],p['augmented_rank']]for p in packet['tests']],
             'certificate_found':False}
    save('validation.json',receipt);print(json.dumps(receipt))


def main():
    assert __debug__,'Run without -O'
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['run','worker','verify']);args=parser.parse_args()
    if args.command=='worker':save('packet.json',calculate())
    elif args.command=='verify':verify()
    else:
        start=time.perf_counter()
        try:
            run=subprocess.run([sys.executable,'-S',str(Path(__file__)),'worker'],capture_output=True,text=True,timeout=120)
            result={'status':'completed'if run.returncode==0 else 'failed','wall_limit_seconds':120,
                    'elapsed_seconds':time.perf_counter()-start,'returncode':run.returncode,
                    'stdout':run.stdout,'stderr':run.stderr}
        except subprocess.TimeoutExpired:
            result={'status':'timeout','wall_limit_seconds':120,'elapsed_seconds':time.perf_counter()-start}
        save('attempt.json',result);print(json.dumps(result));assert result['status']=='completed'


if __name__=='__main__':main()
