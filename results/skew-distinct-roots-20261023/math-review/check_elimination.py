#!/usr/bin/env python3
"""Exact sparse Z[a,v,x] controls for the selected elimination argument.

This script checks an identity and controlled mutations, not generic
separability itself. The latter needs the accompanying field argument/Lean
proof. It emits deterministic JSON and never changes existing receipts.
"""

import json


ONE = {(0, 0, 0): 1}
A = {(1, 0, 0): 1}
V = {(0, 1, 0): 1}
X = {(0, 0, 1): 1}


def add(p, q):
    out = dict(p)
    for exponent, coefficient in q.items():
        out[exponent] = out.get(exponent, 0) + coefficient
    return {exponent: coefficient for exponent, coefficient in out.items() if coefficient}


def scale(c, p):
    return {exponent: c * coefficient for exponent, coefficient in p.items() if c * coefficient}


def sub(p, q):
    return add(p, scale(-1, q))


def mul(p, q):
    out = {}
    for ep, cp in p.items():
        for eq, cq in q.items():
            exponent = tuple(ep[i] + eq[i] for i in range(3))
            out[exponent] = out.get(exponent, 0) + cp * cq
    return {exponent: coefficient for exponent, coefficient in out.items() if coefficient}


def power(p, n):
    out = ONE
    for _ in range(n):
        out = mul(out, p)
    return out


def derivative_x(p):
    return {
        (ea, ev, ex - 1): coefficient * ex
        for (ea, ev, ex), coefficient in p.items()
        if ex
    }


def at_x_zero(p):
    return {exponent: coefficient for exponent, coefficient in p.items() if exponent[2] == 0}


def terms(p):
    return [
        {"a_power": e[0], "v_power": e[1], "x_power": e[2], "coefficient": c}
        for e, c in sorted(p.items(), key=lambda ec: (ec[0][2], ec[0][1], ec[0][0]), reverse=True)
    ]


def require(condition, message):
    # Deliberately independent of Python assertions so python3 -O is safe.
    if not condition:
        raise RuntimeError(message)


vx = mul(V, X)
vx_minus_one = sub(vx, ONE)
P = add(add(power(X, 18), power(X, 12)), power(vx_minus_one, 6))
f = sub(P, mul(A, power(X, 15)))
D_computed = sub(mul(X, derivative_x(f)), scale(15, f))
D_factored = add(
    sub(scale(3, power(X, 18)), scale(3, power(X, 12))),
    mul(power(vx_minus_one, 5), sub(scale(15, ONE), scale(9, vx))),
)
D_expected = {
    (0, 0, 18): 3,
    (0, 0, 12): -3,
    (0, 6, 6): -9,
    (0, 5, 5): 60,
    (0, 4, 4): -165,
    (0, 3, 3): 240,
    (0, 2, 2): -195,
    (0, 1, 1): 84,
    (0, 0, 0): -15,
}
require(D_computed == D_factored, "Elimination/factored identity differs")
require(D_computed == D_expected, "Elimination coefficient table differs")
require(all(e[0] == 0 for e in D_computed), "Parameter a was not eliminated")
require(at_x_zero(D_computed) == scale(-15, ONE), "D(0) is not -15")
require(at_x_zero(f) == ONE, "f(0) is not 1")
require(add(f, mul(A, power(X, 15))) == P, "Root recovery identity differs")

wrong_multiplier = sub(mul(X, derivative_x(f)), scale(14, f))
require(wrong_multiplier.get((1, 0, 15)) == -1, "Multiplier mutation escaped detection")
wrong_exponent_f = sub(P, mul(A, power(X, 14)))
wrong_exponent_D = sub(mul(X, derivative_x(wrong_exponent_f)), scale(15, wrong_exponent_f))
require(wrong_exponent_D.get((1, 0, 14)) == 1, "Exponent mutation escaped detection")
wrong_sign_D = add(
    sub(scale(3, power(X, 18)), scale(3, power(X, 12))),
    mul(power(vx_minus_one, 5), add(scale(15, ONE), scale(9, vx))),
)
wrong_sign_residual = sub(wrong_sign_D, D_computed)
require(wrong_sign_residual == scale(18, mul(vx, power(vx_minus_one, 5))),
        "Sign mutation residual was not the claimed exact polynomial")
require(bool(wrong_sign_residual), "Sign mutation escaped detection")

result = {
    "status": "PASS_EXACT_IDENTITY_AND_THREE_MUTATION_CONTROLS",
    "arithmetic": "Exact integers in the sparse polynomial ring Z[a,v,x]; no floats or CAS dependency",
    "physical_polynomial": "x^18+x^12+(v*x-1)^6-a*x^15",
    "elimination_identity": "x*f'(x)-15*f(x)=3*x^18-3*x^12+(v*x-1)^5*(15-9*v*x)",
    "D_terms": terms(D_computed),
    "D_constant_term": -15,
    "f_constant_term": 1,
    "a_eliminated": True,
    "root_recovery_identity": "f(x)+a*x^15=x^18+x^12+(v*x-1)^6",
    "mutation_controls": [
        {
            "mutation": "Replace multiplier 15 by 14 in x*f'-15*f",
            "expected_obstruction": "The coefficient of a*x^15 is -1, so a is not eliminated",
            "residual_a_terms": terms({e: c for e, c in wrong_multiplier.items() if e[0]}),
        },
        {
            "mutation": "Change physical term -a*x^15 to -a*x^14 but retain multiplier 15",
            "expected_obstruction": "The coefficient of a*x^14 is 1, so a is not eliminated",
            "residual_a_terms": terms({e: c for e, c in wrong_exponent_D.items() if e[0]}),
        },
        {
            "mutation": "Change (15-9*v*x) to (15+9*v*x) in the claimed eliminant",
            "expected_obstruction": "The claimed identity differs by nonzero 18*v*x*(v*x-1)^5",
            "residual_terms": terms(wrong_sign_residual),
        },
    ],
    "limits": [
        "This exact identity computation is not a Lean proof or a separability transfer argument",
        "Generic distinctness additionally uses characteristic zero and a transcendental over the coefficient field containing v",
        "The prior a=2,v=1 double-root control is reused by hash; it is not rerun here",
        "No source normalization, unsplit descent, primitive, HasCertificate, or solve claim",
    ],
}
print(json.dumps(result, indent=2, sort_keys=True))
