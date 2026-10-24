"""Independent bounded coefficient checks; no Lean or de Rham replay.

Read the pinned connection column and its exact correction from the public
packet. Parse only rational expressions, without evaluating source code.
Run externally with a 60-second process bound; outputs never replace inputs.
"""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import platform
import time
import sympy as s


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--connection', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), 'Refusing to replace an existing receipt')
    started = time.monotonic()
    content = args.connection.read_bytes()
    expected = 'a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
    require(hashlib.sha256(content).hexdigest() == expected, 'Pinned connection hash differs')
    raw = json.loads(content)
    a,b,c,d,U,V,r,w,v,t,z = s.symbols('a b c d U V r w v t z')
    names = {str(x):x for x in (a,b,c,d,U)}
    def parse(text):
        def visit(node):
            if isinstance(node, ast.Constant) and type(node.value) is int:
                return s.Integer(node.value)
            if isinstance(node, ast.Name) and node.id in names:
                return names[node.id]
            if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub,ast.UAdd)):
                value = visit(node.operand)
                return -value if isinstance(node.op,ast.USub) else value
            if isinstance(node,ast.BinOp):
                left,right = visit(node.left),visit(node.right)
                if isinstance(node.op,ast.Add): return left+right
                if isinstance(node.op,ast.Sub): return left-right
                if isinstance(node.op,ast.Mult): return left*right
                if isinstance(node.op,ast.Div): return left/right
                if isinstance(node.op,ast.Pow) and right.is_Integer and abs(int(right))<=30: return left**right
            raise ValueError('Non-rational expression in packet')
        return visit(ast.parse(text,mode='eval').body)
    m0 = parse(raw['connection']['b'][0][0])
    m1 = parse(raw['connection']['b'][1][0])
    correction = parse(raw['exact_corrections_R']['b'][0])
    P = a*U**3+b*U**2+c*U+d
    Delta = 27*a*a*d*d-18*a*b*c*d+4*a*c**3+4*b**3*d-b*b*c*c
    equalities,mutations = {},{}
    def zero(name,expr):
        residual = s.cancel(expr)
        require(residual==0, 'Nonzero required identity: '+name)
        equalities[name] = 'zero'
    def nonzero(name,expr):
        residual = s.cancel(expr)
        require(residual!=0, 'Undetected error control: '+name)
        mutations[name] = {'numerator':str(s.fraction(residual)[0]),'denominator':str(s.fraction(residual)[1])}
    exact_part = -P*s.diff(correction,U)+s.Rational(5,6)*s.diff(P,U)*correction
    basis_part = -P*(m0+m1*U)
    zero('b_column_zero_full_fibre_reduction', s.Rational(5,6)*U**2-basis_part-exact_part)
    zero('cleared_polynomial_reduction', s.expand(Delta*(s.Rational(5,6)*U**2-basis_part-exact_part)))
    Dbz = -U**2/(6*z**5)
    zero('implicit_cubic_b_variation',6*z**5*Dbz+U**2)
    zero('inverse_fifth_power_variation',-5*z**-6*Dbz-s.Rational(5,6)*U**2/z**11)
    zero('normalization_five_over_72_to_one_over_12',s.Rational(5,72)-s.Rational(1,12)*s.Rational(5,6))
    Aold = (1+r**6+w**6)/r**3
    vold = 1/r+r*w
    determinant = s.cancel(s.Matrix([r*U,Aold,vold,t]).jacobian([U,r,w,t]).det())
    A = r**3+r**-3+(v*r-1)**6/r**15
    Ar = s.diff(A,r)
    zero('ordered_coordinate_jacobian', determinant.subs(w,(v*r-1)/r**2)-r**2*Ar)
    f = r**18+r**12+(v*r-1)**6-a*r**15
    fr = s.diff(f,r)
    zero('cover_derivative_identity', fr.subs(a,A)-r**15*Ar)
    actual_density = s.Rational(5,72)*(V/r)**2/z**11/(r**2*Ar)
    cover_density = (r**11/fr)*(s.Rational(1,12)*s.Rational(5,6)*V**2/z**11)
    zero('complete_fibre_first_normalization',actual_density-cover_density.subs(a,A))
    permutation = [1,2,3,0]
    sign = (-1)**sum(permutation[i]>permutation[j] for i in range(4) for j in range(i+1,4))
    require(sign == -1, 'Fibre-to-base-first orientation changed')
    equalities['three_base_differentials_orientation'] = '-1'
    nonzero('omit_exact_fibre_correction',s.Rational(5,6)*U**2-basis_part)
    nonzero('reverse_compact_column_sign',s.Rational(5,6)*U**2+basis_part-exact_part)
    nonzero('drop_one_over_12',s.Rational(5,72)-s.Rational(5,6))
    nonzero('replace_slot11_by_slot14',(r**11-r**14)/fr)
    nonzero('omit_fibre_rescaling',(1-r**-3)*r**14/fr)
    nonzero('ignore_three_swap_sign',s.Integer(sign)-1)
    result = {
        'status':'PASS','executor':'Codex coordinator independent exact coefficient checks',
        'python':platform.python_version(),'sympy':s.__version__,
        'elapsed_seconds':time.monotonic()-started,'external_process_bound_seconds':60,
        'connection_sha256':expected,'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'equalities':equalities,'detected_mutations':mutations,
        'assumptions':['r != 0','z != 0','Delta != 0 for compact column','f_r != 0 for covering Jacobian','f=0 for derivative relation'],
        'orientation':'Positive 1/12 in fibre-first order; moving fibre differential past three base differentials gives a minus sign.',
        'limits':['Only b,column0 from the pinned packet is checked; no full connection/gauge/curvature replay.',
                  'No formal Kähler quotient or cohomology class map is constructed by this script.',
                  'No source primitive, trace-exactness, global clearing or certificate is proved.']
    }
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['detected_mutations','equalities']}))


if __name__=='__main__': main()
