#!/usr/bin/env python3
"""Exact obstruction for the two remaining mixed degree-six diagonal points.

Discovery uses Q[t]/(5t^2-8t+8); verification only multiplies rational pairs.
This packet depends mathematically on the complete mixed-family reductions.
It does not itself prove those reductions or exclude higher degrees.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import json
from pathlib import Path
import subprocess
import sys
import time
import fresh_instance_e1 as e
import fresh_instance_degree6 as d6

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results' / 'mixed-degree6-extra'


class K:
    """a+b*t, with t^2=(8*t-8)/5; no floating-point arithmetic."""
    __slots__ = ('a', 'b')

    def __init__(self, a=0, b=0):
        if isinstance(a, K):
            self.a, self.b = a.a, a.b
        else:
            self.a, self.b = Q(a), Q(b)

    def __bool__(self):
        return bool(self.a or self.b)

    def __eq__(self, other):
        other = K(other)
        return self.a == other.a and self.b == other.b

    def __add__(self, other):
        other = K(other)
        return K(self.a + other.a, self.b + other.b)

    __radd__ = __add__

    def __neg__(self):
        return K(-self.a, -self.b)

    def __sub__(self, other):
        return self + -K(other)

    def __rsub__(self, other):
        return K(other) + -self

    def __mul__(self, other):
        other = K(other)
        product = self.b * other.b
        return K(self.a * other.a - Q(8, 5) * product,
                 self.a * other.b + self.b * other.a + Q(8, 5) * product)

    __rmul__ = __mul__

    def inverse(self):
        norm = self.a**2 + Q(8, 5)*self.a*self.b + Q(8, 5)*self.b**2
        if not norm:
            raise ZeroDivisionError('Zero in the quadratic field')
        return K((self.a + Q(8, 5)*self.b)/norm, -self.b/norm)

    def __truediv__(self, other):
        return self * K(other).inverse()

    def __rtruediv__(self, other):
        return K(other) * self.inverse()


def packed(vector):
    return [[i, str(c.a), str(c.b)] for i, c in sorted(vector.items()) if c]


def unpacked(records):
    assert len({int(i) for i, a, b in records}) == len(records)
    result = {int(i): K(a, b) for i, a, b in records}
    assert all(result.values())
    return result


def physical_maps():
    F, A, target, bindings = e.target('mixed-biweight')
    rows = e.monos(12)
    lookup = {m: i for i, m in enumerate(rows)}
    parts = [e.derivative(F, i) for i in range(6)]
    units = [tuple(int(i == j) for j in range(6)) for i in range(6)]
    coordinates = [K(1), K(1), K(0, 1), K(1), K(1), K(0)]
    D, N = {}, [{} for _ in range(6)]
    for i, c in enumerate(coordinates):
        e.add(D, d6.shift(parts[i], units[i]), c)
        e.add(N[i], d6.shift(A, units[i]), c)
    koszul = []
    for i in range(6):
        for j in range(i+1, 6):
            for mon in e.monos(2):
                field = [{} for _ in range(6)]
                field[i] = d6.shift(parts[j], mon)
                field[j] = d6.shift(parts[i], mon, -1)
                koszul.append(field)
    def vector(poly):
        return {lookup[m]: K(c) for m, c in poly.items() if c}
    columns = [vector(d6.shift(F, mon)) for mon in e.monos(6)]
    columns += [vector(d6.B(D, field)) for field in koszul]
    rhs = vector(d6.B(D, N))
    nf = {}
    for component, part in zip(N, parts):
        e.add(nf, e.multiply(component, part))
    assert nf == e.multiply(A, D)
    assert len(columns) == 777 and len(koszul) == 315
    return rows, columns, rhs, target, bindings


def check_functional(dual, columns, rhs, row_count):
    assert all(0 <= i < row_count for i in dual)
    assert all(e.dot(dual, col) == K(0) for col in columns)
    assert e.dot(dual, rhs) == K(1)


def discover():
    start = time.perf_counter()
    rows, columns, rhs, target, bindings = physical_maps()
    basis = e.column_basis(columns, track=False)
    remainder, _ = e.reduce_vector(rhs, basis)
    assert remainder
    pivot = min(remainder)
    dual = e.quotient_dual({pivot: K(1)/remainder[pivot]}, basis)
    check_functional(dual, columns, rhs, len(rows))
    packet = {
        'schema': 'mixed-degree6-quadratic-field-v1',
        'instance': 'mixed-biweight', 'degree': 6,
        'target': target, 'source_sha256': bindings,
        'experiment_source_sha256': {name: e.sha(ROOT/name) for name in (
            'experiments/mixed_degree6_quadratic_field.py',
            'experiments/fresh_instance_e1.py', 'experiments/fresh_instance_degree6.py')},
        'sha256_policy': 'UTF-8 bytes with CRLF normalized to LF',
        'field': {'minimal_polynomial_ascending': ['8', '-8', '5'],
                  'basis': ['1', 't'], 'rule': 't^2=(-8+8*t)/5',
                  'complex_roots': '(4+2*sqrt(-6))/5 and (4-2*sqrt(-6))/5'},
        'diagonal_coordinates': [['1','0'],['1','0'],['0','1'],['1','0'],['1','0'],['0','0']],
        'column_order': 'F times degree-six monomials, then B_D(K) for all315 quadratic Koszul fields, in the original ascending monomial order.',
        'dimensions': {'coefficient_rows': len(rows), 'correction_columns': len(columns),
                       'correction_rank_over_quadratic_field': len(basis),
                       'augmented_rank_over_quadratic_field': len(basis)+1},
        'functional': packed(dual), 'target_value': ['1','0'],
        'residual': packed(remainder),
        'matrix_plot': {'correction_entries': [[r,c,str(v.a),str(v.b)] for c,col in enumerate(columns) for r,v in sorted(col.items())],
                        'rhs_entries': packed(rhs)},
        'scope': 'Both complex conjugate normalized diagonal candidates fail the full shared315-correction equation. Complete-family and lower-degree reductions are separate dependencies.',
        'elapsed_seconds': time.perf_counter()-start,
    }
    e.write_json(OUT/'field-obstruction.json', packet)
    print(json.dumps({'status':'complete','dimensions':packet['dimensions'],
                      'functional_terms':len(dual),'residual_terms':len(remainder),
                      'seconds':packet['elapsed_seconds']}), flush=True)


def verify():
    if not __debug__:
        raise RuntimeError('Run without -O: verification uses assertions.')
    start = time.perf_counter()
    path = OUT/'field-obstruction.json'
    packet = json.loads(path.read_text(encoding='utf-8'))
    rows, columns, rhs, target, bindings = physical_maps()
    assert packet['schema']=='mixed-degree6-quadratic-field-v1'
    assert packet['target']==target and packet['source_sha256']==bindings
    for name,digest in packet['experiment_source_sha256'].items():
        assert e.sha(ROOT/name)==digest
    assert packet['field']['minimal_polynomial_ascending']==['8','-8','5']
    assert packet['diagonal_coordinates']==[['1','0'],['1','0'],['0','1'],['1','0'],['1','0'],['0','0']]
    dual = unpacked(packet['functional'])
    check_functional(dual, columns, rhs, len(rows))
    assert packet['target_value']==['1','0']
    assert packet['matrix_plot']['correction_entries']==[[r,c,str(v.a),str(v.b)] for c,col in enumerate(columns) for r,v in sorted(col.items())]
    assert packet['matrix_plot']['rhs_entries']==packed(rhs)
    basis = e.column_basis(columns, track=False)
    assert packet['dimensions']=={'coefficient_rows':len(rows),'correction_columns':len(columns),
                                  'correction_rank_over_quadratic_field':len(basis),
                                  'augmented_rank_over_quadratic_field':len(basis)+1}
    assert packet['residual']==packed(e.reduce_vector(rhs,basis)[0])
    rejected=0
    for change in (K(1),K(0,1)):
        damaged=dict(dual);e.add(damaged,{min(dual):change})
        try:check_functional(damaged,columns,rhs,len(rows))
        except AssertionError:rejected+=1
        else:raise AssertionError('Altered field functional accepted')
    result={'status':'PASS','instance':'mixed-biweight','stage':'shared-correction quadratic-field obstruction',
            'packet_sha256':e.sha(path),'correction_pairings':len(columns),
            'target_value':['1','0'],'functional_terms':len(dual),'mutations_rejected':rejected,
            'seconds':time.perf_counter()-start}
    e.write_json(OUT/'field-validation.json',result)
    print(json.dumps(result),flush=True)


def main():
    if not __debug__:
        raise RuntimeError('Run without -O: checks use assertions.')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['run','worker','verify'])
    parser.add_argument('--timeout',type=float,default=120)
    args=parser.parse_args()
    if args.command=='worker':discover()
    elif args.command=='verify':verify()
    else:
        start=time.perf_counter()
        try:
            result=subprocess.run([sys.executable,'-S',str(Path(__file__).resolve()),'worker'],
                                  capture_output=True,text=True,timeout=args.timeout)
            attempt={'status':'complete' if result.returncode==0 else 'error',
                     'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr}
        except subprocess.TimeoutExpired:
            attempt={'status':'timeout'}
        attempt.update(stage='quadratic-field discovery',time_limit_seconds=args.timeout,
                       elapsed_seconds=time.perf_counter()-start)
        path=OUT/'field-attempts.json'
        history=json.loads(path.read_text()) if path.exists() else []
        history.append(attempt);e.write_json(path,history)
        print(json.dumps(attempt),flush=True)
        if attempt['status']!='complete':raise SystemExit(1)


if __name__=='__main__':main()
