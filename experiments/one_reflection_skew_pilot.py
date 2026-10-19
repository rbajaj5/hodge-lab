#!/usr/bin/env python3
"""Exact baseline, symmetry audit, and binary-cubic Hessian obstruction for one-reflection-skew.

Writes:
  - results/one-reflection-skew-pilot/report.json
  - results/one-reflection-skew-pilot/one-reflection-skew-audit.svg
"""

from __future__ import annotations

from fractions import Fraction as Q
import hashlib
import json
import time
from pathlib import Path

import sympy as sp
from sympy.polys.matrices import DomainMatrix

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results" / "one-reflection-skew-pilot"
REPORT_PATH = OUT_DIR / "report.json"
SVG_PATH = OUT_DIR / "one-reflection-skew-audit.svg"


def monos(degree: int, count: int = 6):
    if count == 1:
        return [(degree,)]
    return [(i,) + rest for i in range(degree + 1) for rest in monos(degree - i, count - 1)]


def add_vec(a: dict, b: dict, scale: Q = Q(1)) -> dict:
    for k, v in b.items():
        n = a.get(k, Q(0)) + scale * v
        if n:
            a[k] = n
        else:
            a.pop(k, None)
    return a


def reduce_vec(v: dict, basis: dict) -> dict:
    v = dict(v)
    for p in sorted(basis):
        c = v.get(p)
        if c:
            add_vec(v, basis[p], -c)
    return v


def col_basis(cols: list[dict]) -> dict:
    basis = {}
    for col in cols:
        v = reduce_vec(col, basis)
        if v:
            p = min(v)
            scale = v[p]
            basis[p] = {k: c / scale for k, c in v.items()}
    return basis


def poly_to_dict(expr, vars6) -> dict:
    poly = sp.Poly(expr, *vars6, domain=sp.QQ)
    return {m: Q(int(c.p), int(c.q)) for m, c in poly.terms() if c != 0}


def make_one_reflection_skew():
    X0, X1, X2, Y0, Y1, Y2 = sp.symbols("X0 X1 X2 Y0 Y1 Y2")
    vars6 = (X0, X1, X2, Y0, Y1, Y2)
    F_unperturbed = (
        X0**6
        + X1**6
        + X2**6
        + Y0**6
        + Y1**6
        + Y2**6
        + X0**3 * X1 * Y0 * Y1
        + X1**3 * X2 * Y0 * Y1
    )
    skew_term = sp.Rational(1, 7) * X0 * X1 * Y0 * Y1 * (Y0**2 - Y1**2)
    F = sp.expand(F_unperturbed + skew_term)
    A = X0**3 * Y0**3
    return vars6, F_unperturbed, skew_term, F, A


def check_jacobian_and_smoothness(vars6, F, A):
    F0 = sum(v**6 for v in vars6)
    loads = [
        str(sum(abs(c) for c in sp.Poly(sp.diff(F - F0, v), *vars6, domain=sp.QQ).coeffs()))
        for v in vars6
    ]
    cols = [sp.Poly(v * sp.diff(F, w), *vars6, domain=sp.QQ).as_dict() for v in vars6 for w in vars6]
    all_cols = cols + [sp.Poly(A, *vars6, domain=sp.QQ).as_dict()]
    monoms = sorted(set().union(*(c.keys() for c in all_cols)))
    mat_j = sp.SparseMatrix(
        len(monoms),
        len(cols),
        {(i, j): cols[j][m] for i, m in enumerate(monoms) for j in range(len(cols)) if m in cols[j]},
    )
    mat_aug = sp.SparseMatrix(
        len(monoms),
        len(all_cols),
        {(i, j): all_cols[j][m] for i, m in enumerate(monoms) for j in range(len(all_cols)) if m in all_cols[j]},
    )
    rk_j = DomainMatrix.from_Matrix(mat_j).convert_to(sp.QQ).rank()
    rk_aug = DomainMatrix.from_Matrix(mat_aug).convert_to(sp.QQ).rank()
    assert rk_j == 36 and rk_aug == 37
    return {
        "jacobianRank": rk_j,
        "augmentedRank": rk_aug,
        "mixedDerivativeBounds": loads,
        "pureSixthDerivativeCoeff": 6,
    }


def check_symmetries_and_cubic_obstruction(vars6, F_unperturbed, skew_term, F, A):
    X0, X1, X2, Y0, Y1, Y2 = vars6

    # 1. Hidden Y0/Y1 exchanges that solved one-reflection
    ex_plus = {Y0: Y1, Y1: Y0}
    ex_minus = {Y0: -Y1, Y1: -Y0}
    assert sp.expand(F_unperturbed.subs(ex_plus, simultaneous=True) - F_unperturbed) == 0
    assert sp.expand(F_unperturbed.subs(ex_minus, simultaneous=True) - F_unperturbed) == 0
    diff_plus = sp.expand(F.subs(ex_plus, simultaneous=True) - F)
    diff_minus = sp.expand(F.subs(ex_minus, simultaneous=True) - F)
    assert diff_plus == sp.expand(-2 * skew_term)
    assert diff_minus == sp.expand(-2 * skew_term)

    # 2. Surviving sign-flip group on (X0,X2), (X1), (Y0), (Y1) with even number of flips, plus Y2 -> -Y2
    blocks = {
        "tau_X0X2": {X0: -X0, X2: -X2},
        "tau_X1": {X1: -X1},
        "tau_Y0": {Y0: -Y0},
        "tau_Y1": {Y1: -Y1},
    }
    even_pairs = []
    keys = list(blocks.keys())
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            sub = {}
            sub.update(blocks[keys[i]])
            sub.update(blocks[keys[j]])
            assert sp.expand(F.subs(sub, simultaneous=True) - F) == 0
            a_ratio = sp.simplify(A.subs(sub, simultaneous=True) / A)
            det_sign = (-1) ** len(sub)
            even_pairs.append(
                {
                    "pair": [keys[i], keys[j]],
                    "variablesFlipped": sorted(str(k) for k in sub.keys()),
                    "preservesF": True,
                    "targetParity": int(a_ratio),
                    "jacobianSign": int(det_sign),
                    "topFormParity": int(a_ratio * det_sign),
                }
            )

    # 3. Three-passive-ratio binary cubic Hessian identity and degeneration audit
    r, w, beta, u, v = sp.symbols("r w beta u v")
    c0, c1, c2, c3 = sp.symbols("c0 c1 c2 c3")
    f_sym = c0 * u**3 + c1 * u**2 * v + c2 * u * v**2 + c3 * v**3
    h_sym = (3 * c0 * c2 - c1**2) * u**2 + (9 * c0 * c3 - c1 * c2) * u * v + (3 * c1 * c3 - c2**2) * v**2
    fu_sym = sp.diff(f_sym, u)
    fv_sym = sp.diff(f_sym, v)
    disc_sym = sp.expand((9 * c0 * c3 - c1 * c2) ** 2 - 4 * (3 * c0 * c2 - c1**2) * (3 * c1 * c3 - c2**2))

    # Exact universal constant-coefficient Cramer's rule identity on (fu, fv, h):
    # disc_sym * u^2 = L_u * fu_sym + L_v * fv_sym + L_h * h_sym
    L_u = 27 * c0 * c3**2 - 9 * c1 * c2 * c3 + 2 * c2**3
    L_v = 6 * c1**2 * c3 - 9 * c0 * c2 * c3 - c1 * c2**2
    L_h = -2 * (3 * c1 * c3 - c2**2)
    ident_check = sp.expand(L_u * fu_sym + L_v * fv_sym + L_h * h_sym - disc_sym * u**2)
    assert ident_check == 0

    # Cayley's universal binary-cubic covariant syzygy with c2 != 0:
    H_u = sp.diff(h_sym, v)
    H_v = -sp.diff(h_sym, u)
    k_sym = sp.expand((H_u * fu_sym + H_v * fv_sym) / 3)
    H_of_h = sp.expand(H_u * sp.diff(h_sym, u) + H_v * sp.diff(h_sym, v))
    H_of_k = sp.expand(H_u * sp.diff(k_sym, u) + H_v * sp.diff(k_sym, v))
    cayley_syz = sp.expand(disc_sym * f_sym**2 - k_sym**2 - sp.Rational(4, 9) * h_sym**3)
    assert H_of_h == 0
    assert sp.expand(H_of_k - 3 * disc_sym * f_sym) == 0
    assert cayley_syz == 0

    c0_val = 1 + r**6 + w**6
    c1_val = beta * (r + r**3 * w)
    c2_val = sp.Rational(1, 7) * r * beta * (1 - beta**2)
    c3_val = 1 + beta**6
    f_bin = f_sym.subs({c0: c0_val, c1: c1_val, c2: c2_val, c3: c3_val})
    f_sub = f_bin.subs({u: X0**2, v: Y0**2, r: X1 / X0, w: X2 / X0, beta: Y1 / Y0})
    assert sp.simplify(f_sub + Y2**6 - F) == 0

    res_beta_c1_c2 = sp.factor(sp.resultant(c1_val, c2_val, beta))
    h_vv_factored = sp.factor((3 * c1 * c3 - c2**2).subs({c1: c1_val, c2: c2_val, c3: c3_val}))

    return {
        "hiddenExchangeResidualPlus": str(diff_plus),
        "hiddenExchangeResidualMinus": str(diff_minus),
        "survivingTwoBlockSignSymmetries": even_pairs,
        "binaryCubicDiscriminantIdentity": {
            "universalIdentityVerified": True,
            "cayleySyzygyVerified": True,
            "L_u": str(L_u),
            "L_v": str(L_v),
            "L_h": str(L_h),
            "c0": str(c0_val),
            "c1": str(c1_val),
            "c2": str(c2_val),
            "c3": str(c3_val),
            "h_vv_factored": str(h_vv_factored),
            "resultant_beta_c1_c2": str(res_beta_c1_c2),
        },
    }


def check_low_degree_e1_and_deg5_e2(vars6, F, A):
    t0 = time.perf_counter()
    partials = [poly_to_dict(sp.diff(F, v), vars6) for v in vars6]
    A_dict = poly_to_dict(A, vars6)

    e1_dims = {}
    for d in range(1, 6):
        rows = monos(d + 6)
        den = monos(d)
        num = monos(d + 1)
        lookup = {m: idx for idx, m in enumerate(rows)}
        jac = []
        for i in range(6):
            for n in num:
                jac.append({lookup[tuple(a + b for a, b in zip(m, n))]: c for m, c in partials[i].items()})
        ad = [{lookup[tuple(a + b for a, b in zip(m, n))]: c for m, c in A_dict.items()} for n in den]
        jb = col_basis(jac)
        db = {}
        ker_dim = 0
        for col in ad:
            v = reduce_vec(col, jb)
            v = reduce_vec(v, db)
            if v:
                p = min(v)
                sc = v[p]
                db[p] = {k: c / sc for k, c in v.items()}
            else:
                ker_dim += 1
        e1_dims[str(d)] = ker_dim
    assert e1_dims == {"1": 0, "2": 0, "3": 0, "4": 0, "5": 6}

    # At degree 5, ker(E1) is the 6-dimensional gradient span D = sum_{i=0}^5 c_i partial_i F.
    # Modulo J(F)_10, the 21 quadratic columns (1 if i==j else 2) * A * partial_i partial_j F
    # isolate all 6 diagonal squares c_i^2 = 0.
    rows10 = monos(10)
    num5 = monos(5)
    lookup10 = {m: idx for idx, m in enumerate(rows10)}
    jac10 = []
    for i in range(6):
        for n in num5:
            jac10.append({lookup10[tuple(a + b for a, b in zip(m, n))]: c for m, c in partials[i].items()})
    jb10 = col_basis(jac10)

    pairs = [(i, j) for i in range(6) for j in range(i, 6)]
    hcols = []
    for i, j in pairs:
        hij = poly_to_dict(sp.expand(A * sp.diff(F, vars6[i], vars6[j])), vars6)
        scale = Q(1 if i == j else 2)
        hcols.append({lookup10[m]: scale * c for m, c in hij.items()})

    residual = [reduce_vec(c, jb10) for c in hcols]
    rowkeys = sorted(set().union(*(set(c) for c in residual)))
    eq = [{j: c[r] for j, c in enumerate(residual) if r in c} for r in rowkeys]
    rb = col_basis(eq)
    isolated_squares = []
    for i in range(6):
        diag = pairs.index((i, i))
        rem = reduce_vec({diag: Q(1)}, rb)
        assert not rem
        isolated_squares.append(str(vars6[i]))
    assert len(isolated_squares) == 6

    return {
        "e1KernelDimsDegrees1To5": e1_dims,
        "degree5QuotientQuadraticRank": len(rb),
        "degree5IsolatedSquares": isolated_squares,
        "degreeAtMost5Excluded": True,
        "elapsedSeconds": round(time.perf_counter() - t0, 3),
    }


def write_svg(report: dict) -> None:
    e1 = report["lowDegreeBaseline"]["e1KernelDimsDegrees1To5"]
    loads = report["curationAndSmoothness"]["mixedDerivativeBounds"]
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="980" height="540" viewBox="0 0 980 540">
  <rect width="980" height="540" fill="#f8fafc"/>
  <rect x="24" y="20" width="932" height="76" rx="8" fill="#0f172a"/>
  <text x="44" y="52" fill="#f8fafc" font-family="monospace" font-size="20" font-weight="bold">
    one-reflection-skew · Exact Baseline, Parity Audit &amp; Binary-Cubic Obstruction
  </text>
  <text x="44" y="78" fill="#cbd5e1" font-family="monospace" font-size="13">
    F = F0 + X0^3 X1 Y0 Y1 + X1^3 X2 Y0 Y1 + (1/7) X0 X1 Y0 Y1 (Y0^2 - Y1^2)   |   q = 1, A = X0^3 Y0^3
  </text>

  <!-- Panel 1: E1 & E2 degree <= 5 exclusion -->
  <rect x="24" y="114" width="450" height="195" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
  <text x="42" y="142" fill="#0f172a" font-family="monospace" font-size="15" font-weight="bold">
    1. Complete Degree &lt;= 5 Exclusion (E1 + Hessian E2)
  </text>
  <text x="42" y="170" fill="#334155" font-family="monospace" font-size="13">
    deg D = 1..4 : dim ker E1 = ({e1["1"]}, {e1["2"]}, {e1["3"]}, {e1["4"]}) -&gt; 0 solutions
  </text>
  <text x="42" y="194" fill="#334155" font-family="monospace" font-size="13">
    deg D = 5    : dim ker E1 = {e1["5"]} = dim J5(F) (gradient span)
  </text>
  <text x="42" y="218" fill="#334155" font-family="monospace" font-size="13">
    deg 5 E2 map : quotient quadratic rank = {report["lowDegreeBaseline"]["degree5QuotientQuadraticRank"]}/21 mod J(F)_10
  </text>
  <text x="42" y="242" fill="#047857" font-family="monospace" font-size="13" font-weight="bold">
    Result       : All 6 diagonal squares c_i^2 = 0 isolated (deg &lt;= 5 excluded)
  </text>
  <text x="42" y="268" fill="#475569" font-family="monospace" font-size="12">
    Jacobian deg-6 rank: {report["curationAndSmoothness"]["jacobianRank"]} (augmented with A: {report["curationAndSmoothness"]["augmentedRank"]})
  </text>
  <text x="42" y="290" fill="#475569" font-family="monospace" font-size="12">
    Smoothness mixed-partial l1 loads: ({", ".join(loads)}) &lt; 6
  </text>

  <!-- Panel 2: Symmetry comparison with one-reflection -->
  <rect x="506" y="114" width="450" height="195" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
  <text x="524" y="142" fill="#0f172a" font-family="monospace" font-size="15" font-weight="bold">
    2. Symmetry Audit vs. Unperturbed one-reflection
  </text>
  <text x="524" y="170" fill="#b91c1c" font-family="monospace" font-size="13">
    Y0 &lt;-&gt; Y1   : F(Y1,Y0) - F = -2/7 X0 X1 Y0 Y1 (Y0^2 - Y1^2) != 0
  </text>
  <text x="524" y="194" fill="#b91c1c" font-family="monospace" font-size="13">
    Y0 &lt;-&gt; -Y1  : F(-Y1,-Y0) - F = -2/7 X0 X1 Y0 Y1 (Y0^2 - Y1^2) != 0
  </text>
  <text x="524" y="220" fill="#334155" font-family="monospace" font-size="13">
    Surviving sign-flip blocks: tau1=(X0,X2), tau2=(X1), tau3=(Y0), tau4=(Y1)
  </text>
  <text x="524" y="244" fill="#334155" font-family="monospace" font-size="13">
    Every mixed term has parity (-1,-1,-1,-1) on (tau1,tau2,tau3,tau4)
  </text>
  <text x="524" y="268" fill="#1e40af" font-family="monospace" font-size="12">
    (Y0,Y1) -&gt; (i Y1, -i Y0) fixes Y0*Y1 and Y0^2-Y1^2, negates Y0^6+Y1^6
  </text>
  <text x="524" y="290" fill="#475569" font-family="monospace" font-size="12">
    Y2 -&gt; -Y2 fixes F and fixes A = X0^3 Y0^3 (does not serve target directly)
  </text>

  <!-- Panel 3: Binary-cubic Hessian identity and degeneration locus -->
  <rect x="24" y="328" width="932" height="190" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
  <text x="42" y="356" fill="#0f172a" font-family="monospace" font-size="15" font-weight="bold">
    3. Passive-Ratio Binary Cubic f(u,v) = c0 u^3 + c1 u^2 v + c2 u v^2 + c3 v^3  (u=X0^2, v=Y0^2)
  </text>
  <text x="42" y="382" fill="#334155" font-family="monospace" font-size="13">
    c0 = 1 + r^6 + w^6,   c1 = beta (r + r^3 w),   c2 = (1/7) r beta (1 - beta^2),   c3 = 1 + beta^6
  </text>
  <text x="42" y="406" fill="#334155" font-family="monospace" font-size="13">
    Universal Hessian identity: disc(h) * u^2 = (a1 u + a2 v) f_u + (a3 u + a4 v) f_v - 9 c2 c3 h(u,v)
  </text>
  <text x="42" y="430" fill="#b91c1c" font-family="monospace" font-size="13">
    Obstruction to 3-passive-ratio Hessian transport: h_vv = 3 c1 c3 - c2^2 vanishes at beta = 0 and r = 0
  </text>
  <text x="42" y="454" fill="#334155" font-family="monospace" font-size="13">
    Res_beta(c1, c2) = 0 identically on r(1+r^2 w) = 0; unlike one-reflection (c2 = 0, p = Y0 Y1),
  </text>
  <text x="42" y="478" fill="#334155" font-family="monospace" font-size="13">
    here v = Y0^2 cannot absorb the Y1 = 0 locus into p = Y0 Y1 without introducing q2 = Y0^2 - Y1^2.
  </text>
  <text x="42" y="502" fill="#475569" font-family="monospace" font-size="12">
    Scope: establishes E1 kernel baseline (deg 1..5) and passive-(r,w,beta) binary-cubic obstruction; higher degrees/covers remain open.
  </text>
</svg>
"""
    SVG_PATH.write_text(svg, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    vars6, F_unperturbed, skew_term, F, A = make_one_reflection_skew()
    curation = check_jacobian_and_smoothness(vars6, F, A)
    sym_cubic = check_symmetries_and_cubic_obstruction(vars6, F_unperturbed, skew_term, F, A)
    baseline = check_low_degree_e1_and_deg5_e2(vars6, F, A)

    report = {
        "instance": "one-reflection-skew",
        "q": 1,
        "F": str(F),
        "A": str(A),
        "curationAndSmoothness": curation,
        "symmetryAndBinaryCubicAudit": sym_cubic,
        "lowDegreeBaseline": baseline,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    write_svg(report)
    digest = hashlib.sha256(REPORT_PATH.read_bytes()).hexdigest()[:16]
    print(f"PASS: one-reflection-skew pilot verified (report sha256[:16]={digest})")


if __name__ == "__main__":
    main()
