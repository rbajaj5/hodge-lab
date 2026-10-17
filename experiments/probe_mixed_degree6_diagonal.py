#!/usr/bin/env python3
"""Retained exploratory diagonal tests; exact exclusion is verified elsewhere.

This reconstructs the relaxed diagonal ideal over Q and tests the two
normalized candidates modulo three primes. Finite-field inconsistency alone
is not used as a characteristic-zero proof.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
import sympy as s
import fresh_instance_e1 as e
import fresh_instance_degree6 as d6
import check_fresh_instance_degree6_independent as h

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'results'/'mixed-degree6-extra'


def worker():
    start=time.perf_counter()
    rows,cor,pairs,quad=d6.diagonal_maps('mixed-biweight')
    cb=e.column_basis(cor,track=False)
    residual=[e.reduce_vector(c,cb)[0] for c in quad]
    rowkeys=sorted(set().union(*map(set,residual)))
    equations=[{j:c[r] for j,c in enumerate(residual) if r in c} for r in rowkeys]
    basis=e.column_basis(equations,track=False)
    a=s.symbols('a0:5')+(s.Integer(0),)
    polys=[sum(s.Rational(v.numerator,v.denominator)*a[pairs[j][0]]*a[pairs[j][1]]
               for j,v in r.items()) for _,(r,_) in sorted(basis.items())]
    gb=s.groebner(polys,*a[:5],order='grevlex')
    differences=[]
    for i in (0,1,3):
        for degree in range(1,5):
            differences.append({'parameter':i,'power':degree,
                                'zero_remainder':gb.reduce((a[i]-a[4])**degree)[1]==0})
    F,A,target,bindings=e.target('mixed-biweight')
    units=[tuple(int(i==j) for j in range(6)) for i in range(6)]
    parts=[e.derivative(F,i) for i in range(6)]
    ds=[d6.shift(parts[i],units[i]) for i in range(6)]
    ns=[[d6.shift(A,units[i]) if j==i else {} for j in range(6)] for i in range(6)]
    kos=h.koszul_fields(parts)
    finite=[]
    for prime in (1009,1013,1019):
        h.P=prime
        for t in range(prime):
            if (5*t*t-8*t+8)%prime:continue
            D,N={},[{}for _ in range(6)]
            for i,c in enumerate((1,1,t,1,1,0)):
                e.add(D,ds[i],c)
                for j in range(6):e.add(N[j],ns[i][j],c)
            columns=[d6.shift(F,m)for m in e.monos(6)]+[d6.B(D,k)for k in kos]
            matrix=h.echelon(columns)
            rem=h.reduce_mod(d6.B(D,N),matrix)
            finite.append({'prime':prime,'root':t,'columns':len(columns),
                           'rank_mod_p':len(matrix),'consistent_mod_p':not rem,
                           'remainder_terms':len(rem)})
    data={'status':'completed_diagnostics','source_sha256':bindings,'target':target,
          'relaxed_diagonal_ideal':{'scope':'Five necessary diagonal equations after independent-product relaxation; not the full shared-correction equation.',
             'equations':list(map(str,polys)), 'groebner_order':'grevlex',
             'groebner_basis':list(map(lambda p:str(p.as_expr()),gb.polys)),
             'difference_power_attempts':differences,
             'normalized_roots':'(4 +/- 2*sqrt(-6))/5'},
          'fixed_denominator_modular_tests':finite,
          'scope':'Exploratory evidence. Rational exported polynomial identities and the quadratic-field functional provide the proof separately.',
          'seconds':time.perf_counter()-start}
    e.write_json(OUT/'diagnostic-probes.json',data)
    print(json.dumps({'status':data['status'],'difference_tests':len(differences),
                      'modular_tests':finite,'seconds':data['seconds']}),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker',action='store_true')
    parser.add_argument('--timeout',type=float,default=120)
    args=parser.parse_args()
    if args.worker:worker();return
    start=time.perf_counter()
    try:
        run=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--worker'],
                           capture_output=True,text=True,timeout=args.timeout)
        record={'status':'complete'if run.returncode==0 else'error',
                'returncode':run.returncode,'stdout':run.stdout,'stderr':run.stderr}
    except subprocess.TimeoutExpired:record={'status':'timeout'}
    record.update(time_limit_seconds=args.timeout,elapsed_seconds=time.perf_counter()-start)
    path=OUT/'diagnostic-attempts.json'
    history=json.loads(path.read_text())if path.exists()else[]
    history.append(record);e.write_json(path,history)
    print(json.dumps(record),flush=True)
    if record['status']!='complete':raise SystemExit(1)


if __name__=='__main__':main()
