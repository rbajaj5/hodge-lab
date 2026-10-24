"""Small exact controls for scalar extension; not a generic theorem proof.

Run with Python 3.11 and SymPy under an external 60-second limit.
The cubic quotient is reducible, so treating it as a field is invalid.
The degree-18 calculation is only the rational specialization a=v=0.
"""
from pathlib import Path
import argparse
import hashlib
import json
import platform
import time
import sympy as s


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    start = time.monotonic()
    x = s.Symbol('x')
    checks = {}
    mutations = {}

    def zero(name, value):
        simplified = s.simplify(value)
        assert simplified == 0, (name, simplified)
        checks[name] = 'zero'

    def nonzero(name, value):
        simplified = s.simplify(value)
        assert simplified != 0, (name, simplified)
        mutations[name] = str(simplified)

    def multiplication_matrix(f, p):
        n = s.degree(f, x)
        cols = []
        for j in range(n):
            r = s.Poly(s.rem(p * x**j, f, x), x)
            cols.append(s.Matrix([r.nth(i) for i in range(n)]))
        return s.Matrix.hstack(*cols)

    # E=Q[x]/((x-1)(x^2-2)); L=Q(sqrt(2)); all three sheets retained.
    f = (x - 1) * (x**2 - 2)
    roots = [s.Integer(1), s.sqrt(2), -s.sqrt(2)]
    beta = s.Matrix([[root**i for i in range(3)] for root in roots])
    companion = multiplication_matrix(f, x)
    assert s.simplify(beta.det()) != 0
    for i in range(3):
        for j in range(3):
            zero(f'beta_multiplication_{i}_{j}',
                 (beta * companion - s.diag(*roots) * beta)[i, j])
    c = s.symbols('c0:3')
    d = s.symbols('d0:3')
    coefficients = [c[i] + s.sqrt(2) * d[i] for i in range(3)]
    element = sum(coefficients[i] * x**i for i in range(3))
    matrix = multiplication_matrix(f, element)
    split_sum = sum(element.subs(x, root) for root in roots)
    zero('arbitrary_tensor_trace', s.trace(matrix) - split_sum)
    expected = 3*coefficients[0] + coefficients[1] + 5*coefficients[2]
    zero('explicit_trace_formula', s.trace(matrix) - expected)
    zero('trace_one_is_three', s.trace(s.eye(3)) - 3)
    zero('trace_scalar_two_is_six', s.trace(2*s.eye(3)) - 6)
    nonzero('incorrect_extension_degree_multiplier', s.trace(s.eye(3)) - 2*3)
    nonzero('incorrect_normalized_trace', s.trace(s.eye(3)) - 1)
    nonzero('dropped_tensor_scalar', s.trace(2*s.eye(3)) - 3)

    # Actual literal cover at a=v=0. This does not prove a generic identity.
    physical = x**18 + x**12 + 1
    derivative = s.diff(physical, x)
    derivative_inverse = s.invert(derivative, physical, x)
    zero('physical_derivative_inverse',
         s.rem(derivative * derivative_inverse - 1, physical, x))
    trace17 = s.trace(multiplication_matrix(physical, x**17 * derivative_inverse))
    trace11 = s.trace(multiplication_matrix(physical, x**11 * derivative_inverse))
    zero('physical_specialized_trace17', trace17 - 1)
    zero('physical_specialized_trace11', trace11)
    zero('physical_specialized_trace_one', s.trace(s.eye(18)) - 18)
    nonzero('physical_normalized_trace_mutation', s.trace(s.eye(18)) - 1)
    report = {
        'status': 'PASS', 'executor': 'Codex coordinator, separate exact examples',
        'python': platform.python_version(), 'sympy': s.__version__,
        'elapsed_seconds': time.monotonic() - start,
        'checker_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'cubic_quotient': '(x-1)(x^2-2)', 'extension': 'Q(sqrt(2))/Q',
        'evaluation_determinant': str(s.simplify(beta.det())),
        'generic_cubic_trace': str(s.expand(expected)),
        'physical_specialization': {'a': 0, 'v': 0, 'f': str(physical)},
        'derivative_inverse': str(derivative_inverse),
        'equalities': checks, 'detected_mutations': mutations,
        'limits': ['No generic scalar-extension theorem proved by these examples.',
                   'No physical source normalization, primitive or certificate.']}
    args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({'status':'PASS', 'equalities':len(checks),
                      'mutations':len(mutations),
                      'elapsed_seconds':report['elapsed_seconds']}))


if __name__ == '__main__':
    main()
