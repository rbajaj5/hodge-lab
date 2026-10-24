#!/usr/bin/env python3
"""Exact checks of the new combined chart normalization and ONE packet column.

This script does not replay the packet's full connection, currents, searches,
or exclusions. It uses explicit exceptions, including under Python -O.
"""
from pathlib import Path
import argparse
import ast
import datetime
import hashlib
import json
import platform
import sys
import time

import sympy as S

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json'
PIN = 'a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    began = datetime.datetime.now(datetime.timezone.utc).isoformat()
    checks, mutations = [], []
    require(sha(SOURCE) == PIN, 'Pinned connection bytes changed')
    data = json.loads(SOURCE.read_text(encoding='utf-8'))
    require(data['equation'] == 'v^6 = -(a*U^3+b*U^2+c*U+d)', 'Curve sign changed')
    require(data['basis'] == ['dU/v^5', 'U*dU/v^5'], 'Fibre basis changed')
    require(data['convention'] == 'columns index input basis; coefficient derivative is partial_t+M_t',
            'Connection convention changed')
    U, V, r, w, t, nu, a, b, c, d, v = S.symbols('U V r w t nu a b c d v')
    allowed = {str(q): q for q in (U, a, b, c, d)}

    def parse(expression):
        tree = ast.parse(expression, mode='eval')
        for node in ast.walk(tree):
            require(isinstance(node, (ast.Expression, ast.BinOp, ast.UnaryOp,
                    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.USub,
                    ast.UAdd, ast.Name, ast.Constant, ast.Load)), 'Unexpected expression syntax')
            if isinstance(node, ast.Name):
                require(node.id in allowed, 'Unexpected expression variable')
            if isinstance(node, ast.Constant):
                require(type(node.value) is int, 'Nonintegral literal')
        return S.sympify(expression, locals=allowed).subs(U, V)

    def zero(name, expression):
        require(S.cancel(expression) == 0, 'Failed exact identity: ' + name)
        checks.append(name)

    def reject(name, expression):
        require(S.cancel(expression) != 0, 'Mutation was not detected: ' + name)
        mutations.append(name)

    A = (1 + r**6 + w**6)/r**3
    vmap = 1/r + r*w
    mappedV = r*U
    f = r**18 + r**12 + (v*r-1)**6-a*r**15
    fr = S.diff(f, r).subs({a:A, v:vmap}, simultaneous=True)
    jac = S.Matrix([mappedV, A, vmap, t]).jacobian([U,r,w,t]).det()
    zero('combined four-coordinate Jacobian equals f_r/r^13', jac-fr/r**13)
    source = S.Rational(5,72)*U**2/nu**11
    transported = S.Rational(5,72)*mappedV**2*r**11/(nu**11*fr)
    zero('fibre-first source pullback with exact r^11 factor', source-transported*jac)
    reject('source sign reversal', source+transported*jac)
    reject('r^11 changed to r^10', source-transported/r*jac)

    nub = -V**2/(6*nu**5)
    zero('coefficient-direction derivative of nu^-5', S.diff(nu**-5,nu)*nub-S.Rational(5,6)*V**2/nu**11)
    zero('one-twelfth coefficient normalization', S.Rational(5,72)-S.Rational(1,12)*S.Rational(5,6))
    reject('unrelated one-over-864 factor', S.Rational(5,72)-S.Rational(1,864)*S.Rational(5,6))

    Delta = 27*a*a*d*d-18*a*b*c*d+4*a*c**3+4*b**3*d-b*b*c*c
    P = a*V**3+b*V**2+c*V+d
    N0 = 27*a*c*d-12*b*b*d+b*c*c
    N1 = a*(3*b*d-c*c)
    NR = 2*N1*V**2+(3*a*c*d+2*b*b*d-b*c*c)*V+(9*a*d*d-b*c*d)
    m0, m1, correction = parse(data['connection']['b'][0][0]), parse(data['connection']['b'][1][0]), parse(data['exact_corrections_R']['b'][0])
    zero('packet b column zero first row binding', m0-N0/(6*Delta))
    zero('packet b column zero second row binding', m1-N1/Delta)
    zero('packet b column zero exact correction binding', correction-NR/Delta)
    cleared = 5*Delta*V**2 + P*(N0+6*N1*V)+6*P*S.diff(NR,V)-5*S.diff(P,V)*NR
    zero('one-column cleared polynomial reduction', cleared)
    residual = S.Rational(5,6)*V**2+P*(m0+m1*V)+P*S.diff(correction,V)-S.Rational(5,6)*S.diff(P,V)*correction
    zero('one-column rational relative differential reduction', residual)
    wrong_m1 = parse(data['connection']['b'][0][1])
    reject('transpose/input-column mutation', residual+P*(wrong_m1-m1)*V)
    reject('drop the exact derivative correction', S.Rational(5,6)*V**2+P*(m0+m1*V))
    # Moving the fibre one-form past the ordered three base one-forms is odd.
    zero('fibre-first to base-first permutation sign', S.Matrix([[0,0,0,1],[1,0,0,0],[0,1,0,0],[0,0,1,0]]).det()+1)
    require(time.monotonic()-start < 600, 'Focused-checker budget exceeded')
    receipt = {'status':'PASS','executor':'Pro source_math AI reviewer',
               'started_utc':began,'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'elapsed_seconds':time.monotonic()-start,'budget_seconds':600,
               'python_version':sys.version,'sympy_version':S.__version__,
               'source_sha256':{str(SOURCE.relative_to(ROOT)):sha(SOURCE),
                   str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))},
               'checks':checks,'mutation_controls':mutations,
               'scope':'New combined chart normalization and only packet b column zero; no old full-packet replay, no Lean execution',
               'limits':['Rational coefficient identities require nonzero r,nu,f_r,Delta where divided',
                         'The matrix reduction identity is exact modulo a relative derivative; no de Rham quotient or Gauss-Manin connection constructed',
                         'Packet vector convention is opposite standard projective normal-last convention',
                         'No arbitrary source exactness, current search, primitive, certificate or solve']}
    (out/'validation.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt,indent=2))


if __name__ == '__main__':
    main()
