"""Small independent algebra check; not a Lean or generic-separability proof."""
import json
import pathlib
import platform
import sys
import time

import sympy as s


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


start = time.monotonic()
x, a, v, t = s.symbols("x a v t")
f = x**18 + x**12 + (v*x - 1)**6 - a*x**15
computed = s.Poly(s.expand(x*s.diff(f, x) - 15*f), x, a, v, t)
claimed = s.Poly(3*x**18 - 3*x**12 + (v*x - 1)**5*(15 - 9*v*x), x, a, v, t)
require(computed == claimed, "Repeated-root elimination identity failed")
require(a not in computed.as_expr().free_symbols, "Parameter a failed to cancel")
require(computed.as_expr().subs(x, 0) == -15, "Constant coefficient mismatch")
mutant = s.Poly(s.expand(x*s.diff(f, x) + 15*f), x, a, v, t)
require(mutant != claimed and a in mutant.as_expr().free_symbols,
        "Sign mutation was not detected")
receipt = {
    "scope": "Coordinator exact algebra check only; not a Lean proof of algebraicity transfer or root enumeration",
    "python": platform.python_version(), "sympy": s.__version__,
    "coefficient_ring": "Q[x,a,v,t]",
    "checks": {"elimination_identity": True, "a_eliminated": True,
               "nonzero_constant_minus_15": True, "wrong_sign_mutation_detected": True},
    "expanded_D": str(computed.as_expr()), "seconds": time.monotonic() - start,
}
output = json.dumps(receipt, indent=2) + "\n"
if len(sys.argv) > 1:
    pathlib.Path(sys.argv[1]).write_bytes(output.encode("utf-8"))
print(output, end="")
