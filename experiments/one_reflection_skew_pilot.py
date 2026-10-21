#!/usr/bin/env python3
"""Exact E1/E2 baseline, Kramers/parity audit, and Nambu/Casimir obstruction for one-reflection-skew.

Writes:
  - results/one-reflection-skew-pilot/report.json
  - results/one-reflection-skew-pilot/one-reflection-skew-audit.png
  - results/one-reflection-skew-pilot/one-reflection-skew-audit.svg
"""

from __future__ import annotations

from fractions import Fraction as Q
import hashlib
import json
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import sympy as sp
from sympy.polys.matrices import DomainMatrix

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results" / "one-reflection-skew-pilot"
REPORT_PATH = OUT_DIR / "report.json"
PNG_PATH = OUT_DIR / "one-reflection-skew-audit.png"
SVG_PATH = OUT_DIR / "one-reflection-skew-audit.svg"

TEAL, CORAL, GOLD = "#166A70", "#CA584C", "#D5AB3E"
INK, MUTED, PAPER = "#17323B", "#53666D", "#FAFAF5"
NAMES = ("X0", "X1", "X2", "Y0", "Y1", "Y2")


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


def dot_vec(a: dict, b: dict) -> Q:
    if len(a) > len(b):
        a, b = b, a
    return sum((c * b.get(k, Q(0)) for k, c in a.items()), Q(0))


def reduce_vec(v: dict, basis: dict, combo: dict | None = None):
    v = dict(v)
    if combo is not None:
        combo = dict(combo)
    for p in sorted(basis):
        c = v.get(p)
        if c:
            b, src = basis[p]
            add_vec(v, b, -c)
            if combo is not None:
                add_vec(combo, src, -c)
    return v, combo


def col_basis(cols: list[dict], track: bool = False) -> dict:
    basis = {}
    for idx, col in enumerate(cols):
        v, combo = reduce_vec(col, basis, {idx: Q(1)} if track else None)
        if v:
            p = min(v)
            scale = v[p]
            basis[p] = (
                {k: c / scale for k, c in v.items()},
                {k: c / scale for k, c in combo.items()} if track else {},
            )
    return basis


def quotient_dual(weights: dict, jac_basis: dict) -> dict:
    dual = dict(weights)
    for p in sorted(jac_basis, reverse=True):
        c = dot_vec(dual, jac_basis[p][0])
        if c:
            add_vec(dual, {p: Q(1)}, -c)
    return dual


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

    # Complex exchange involution (Y0, Y1) -> (i*Y1, -i*Y0)
    I_sym = sp.I
    kramers = {Y0: I_sym * Y1, Y1: -I_sym * Y0}
    assert sp.expand(kramers[Y0].subs(kramers, simultaneous=True) - Y0) == 0
    assert sp.expand(kramers[Y1].subs(kramers, simultaneous=True) - Y1) == 0
    F_int = X0**3 * X1 * Y0 * Y1 + X1**3 * X2 * Y0 * Y1 + skew_term
    assert sp.expand(F_int.subs(kramers, simultaneous=True) - F_int) == 0
    assert sp.expand((Y0**6 + Y1**6).subs(kramers, simultaneous=True) + (Y0**6 + Y1**6)) == 0

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

    # 3. Three-passive-ratio binary cubic Hessian/Casimir identity and caustic audit
    r, w, beta, u, v = sp.symbols("r w beta u v")
    c0, c1, c2, c3 = sp.symbols("c0 c1 c2 c3")
    f_sym = c0 * u**3 + c1 * u**2 * v + c2 * u * v**2 + c3 * v**3
    h_sym = (3 * c0 * c2 - c1**2) * u**2 + (9 * c0 * c3 - c1 * c2) * u * v + (3 * c1 * c3 - c2**2) * v**2
    assert sp.expand(sp.det(sp.hessian(f_sym, (u, v))) - 4*h_sym) == 0
    fu_sym = sp.diff(f_sym, u)
    fv_sym = sp.diff(f_sym, v)
    disc_sym = sp.expand((9 * c0 * c3 - c1 * c2) ** 2 - 4 * (3 * c0 * c2 - c1**2) * (3 * c1 * c3 - c2**2))

    # Universal constant-coefficient Cramer identity on (fu, fv, h):
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
    assert res_beta_c1_c2 == 0  # common beta factor for every r,w, not a caustic locus
    boundary = {c0: 1, c1: 0, c2: 0, c3: 1}
    assert sp.expand(h_sym.subs(boundary) - 9*u*v) == 0
    assert disc_sym.subs(boundary) == 81
    assert L_h.subs(boundary) == 0
    h_vv_factored = sp.factor((3 * c1 * c3 - c2**2).subs({c1: c1_val, c2: c2_val, c3: c3_val}))

    return {
        "hiddenExchangeResidualPlus": str(diff_plus),
        "hiddenExchangeResidualMinus": str(diff_minus),
        "kramersComplexExchangePreservesInteraction": True,
        "complexExchangeOrder": 2,
        "complexExchangeIsFullSexticSymmetry": False,
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
            "hessian_determinant_equals": "4*h",
            "boundary_counterexample": {"r": 0, "w": 0, "beta": 0, "h": "9*u*v", "disc_h": 81, "L_h": 0},
            "scope": "L_h vanishing does not imply Hessian degeneracy or a transport obstruction",
        },
    }


def check_low_degree_e1_and_deg5_e2(vars6, F, A):
    t0 = time.perf_counter()
    partials = [poly_to_dict(sp.diff(F, v), vars6) for v in vars6]
    A_dict = poly_to_dict(A, vars6)

    degree_table = []
    e1_dims = {}
    deg4_residual_entries = []
    deg4_active_rows = []

    for d in range(0, 6):
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
        reduced_ad = []
        for col in ad:
            v, _ = reduce_vec(col, jb)
            reduced_ad.append(dict(v))
            v, _ = reduce_vec(v, db)
            if v:
                p = min(v)
                sc = v[p]
                db[p] = ({k: c / sc for k, c in v.items()}, {})
            else:
                ker_dim += 1
        if d >= 1:
            e1_dims[str(d)] = ker_dim
        degree_table.append(
            {
                "degree": d,
                "coefficient_rows": len(rows),
                "denominator_columns": len(den),
                "numerator_columns": len(jac),
                "numerator_rank": len(jb),
                "augmented_rank": len(jb) + len(db),
                "denominator_image_rank": len(db),
                "denominator_kernel_dimension": ker_dim,
            }
        )
        if d == 4:
            for c_idx, col in enumerate(reduced_ad):
                for r_idx, val in sorted(col.items()):
                    deg4_residual_entries.append([r_idx, c_idx, str(val)])
            deg4_active_rows = sorted({r_idx for r_idx, _, _ in deg4_residual_entries})

    assert e1_dims == {"1": 0, "2": 0, "3": 0, "4": 0, "5": 6}

    # Degree-5 E2 Hessian quotient modulo J(F)_10:
    rows10 = monos(10)
    num5 = monos(5)
    lookup10 = {m: idx for idx, m in enumerate(rows10)}
    jac10 = []
    for i in range(6):
        for n in num5:
            jac10.append({lookup10[tuple(a + b for a, b in zip(m, n))]: c for m, c in partials[i].items()})
    jb10 = col_basis(jac10, track=False)

    pairs = [(i, j) for i in range(6) for j in range(i, 6)]
    hcols = []
    for i, j in pairs:
        hij = poly_to_dict(sp.expand(A * sp.diff(F, vars6[i], vars6[j])), vars6)
        scale = Q(1 if i == j else 2)
        hcols.append({lookup10[m]: scale * c for m, c in hij.items()})

    residual = [reduce_vec(c, jb10)[0] for c in hcols]
    e2_entries = []
    for c_idx, col in enumerate(residual):
        for r_idx, val in sorted(col.items()):
            e2_entries.append([r_idx, c_idx, str(val)])
    e2_active_rows = sorted({r_idx for r_idx, _, _ in e2_entries})

    rowkeys = sorted(set().union(*(set(c) for c in residual)))
    eq = [{j: c[r] for j, c in enumerate(residual) if r in c} for r in rowkeys]
    rb = col_basis(eq, track=True)

    square_witnesses = []
    isolated_squares = []
    for i in range(6):
        diag = pairs.index((i, i))
        rem, combo = reduce_vec({diag: Q(1)}, rb, {})
        assert not rem
        raw = {rowkeys[k]: -c for k, c in combo.items()}
        dual = quotient_dual(raw, jb10)
        assert all(dot_vec(dual, c) == 0 for c in jac10)
        assert [dot_vec(dual, c) for c in hcols] == [Q(int(j == diag)) for j in range(21)]
        isolated_squares.append(NAMES[i])
        square_witnesses.append(
            {
                "coordinate": NAMES[i],
                "quadratic_column": diag,
                "nonzero_terms": len(dual),
            }
        )
    assert len(isolated_squares) == 6

    return {
        "degreeTable": degree_table,
        "e1KernelDimsDegrees1To5": e1_dims,
        "degree4Plot": {
            "active_row_indices": deg4_active_rows,
            "residual_entries": deg4_residual_entries,
        },
        "degree5E2Plot": {
            "quadratic_column_pairs": [[NAMES[i], NAMES[j]] for i, j in pairs],
            "square_columns": [pairs.index((i, i)) for i in range(6)],
            "active_row_indices": e2_active_rows,
            "residual_entries": e2_entries,
        },
        "degree5QuotientQuadraticRank": len(rb),
        "degree5IsolatedSquares": isolated_squares,
        "degree5SquareWitnesses": square_witnesses,
        "degreeAtMost5Excluded": True,
        "elapsedSeconds": round(time.perf_counter() - t0, 3),
    }


def style_axis(ax):
    ax.set_facecolor(PAPER)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color("#B8C2C0")
    ax.tick_params(colors=MUTED, labelsize=9.5)
    ax.xaxis.label.set_color(INK)
    ax.yaxis.label.set_color(INK)


def render_figures(report: dict) -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10.5,
            "text.color": INK,
            "axes.labelcolor": INK,
            "svg.fonttype": "none",
        }
    )
    fig, axes = plt.subplots(2, 2, figsize=(16, 11.2), gridspec_kw={"height_ratios": [1, 1.15]})
    fig.patch.set_facecolor(PAPER)
    fig.subplots_adjust(left=0.07, right=0.965, bottom=0.11, top=0.84, wspace=0.25, hspace=0.46)

    fig.text(
        0.07,
        0.952,
        "one-reflection-skew: exact degree-five exclusion & deformed Casimir flow",
        fontsize=21,
        weight="bold",
    )
    fig.text(
        0.07,
        0.916,
        r"$F = F_0 + (X_0^3 X_1 + X_1^3 X_2)Y_0 Y_1 + \frac{1}{7} X_0 X_1 Y_0 Y_1 (Y_0^2 - Y_1^2)$   |   $q = 1,\ A = X_0^3 Y_0^3$",
        fontsize=14,
        color=TEAL,
    )
    fig.text(
        0.07,
        0.885,
        "Complete E1/E2 rational elimination through degree 5  |  Binary-cubic identities and a Cramer-coefficient boundary",
        fontsize=10.5,
        color=MUTED,
    )

    # Panel (0, 0): E1 bar chart for degrees 0..5
    ax = axes[0, 0]
    style_axis(ax)
    deg_rows = report["lowDegreeBaseline"]["degreeTable"]
    x = np.arange(6)
    eliminated = np.array([r["denominator_image_rank"] for r in deg_rows])
    retained = np.array([r["denominator_kernel_dimension"] for r in deg_rows])
    total = eliminated + retained
    ax.bar(x, eliminated, color=TEAL, width=0.62, label="Eliminated by E1")
    ax.bar(x, retained, bottom=eliminated, color=GOLD, width=0.62, label="Retained by E1 (gradient span)")
    for i, n in enumerate(total):
        ax.text(i, n + 7, str(n), ha="center", fontsize=10, weight="bold")
    ax.annotate(
        "6 retained = J_5(F)\n(gradient span)",
        xy=(5, 249),
        xytext=(2.3, 200),
        fontsize=9.5,
        color=INK,
        arrowprops={"arrowstyle": "->", "color": MUTED},
        ha="center",
        va="center",
    )
    ax.set_title("1. Complete E1 filter: D -> [AD] in S_{d+6}/J_{d+6}", loc="left", fontsize=13, weight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xlabel("Denominator degree d")
    ax.set_ylabel("Denominator directions")
    ax.set_ylim(0, 285)
    ax.set_xlim(-0.55, 5.55)
    ax.yaxis.grid(True, color="#DDE3DF", linewidth=0.6)
    ax.set_axisbelow(True)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5)

    # Panel (0, 1): Degree-4 reduced AD map
    ax = axes[0, 1]
    style_axis(ax)
    d4 = report["lowDegreeBaseline"]["degree4Plot"]
    rows4 = d4["active_row_indices"]
    lookup4 = {r: i for i, r in enumerate(rows4)}
    entries4 = d4["residual_entries"]
    for pos, color, lbl in ((True, TEAL, "Positive"), (False, CORAL, "Negative")):
        pts = [(c, lookup4[r]) for r, c, v in entries4 if (Q(v) > 0) == pos]
        if pts:
            xx, yy = zip(*pts)
            ax.scatter(xx, yy, s=11, color=color, linewidths=0, marker="s", label=lbl)
    ax.set_xlim(-1, 126)
    ax.set_ylim(len(rows4), -1)
    ax.set_xlabel("Denominator monomial column (0-125; all 126 shown)")
    ax.set_ylabel("Active quotient rows\n(sorted by row index)")
    ax.set_title(
        f"2. Degree 4 E1 residual map: {len(entries4)} nonzeros in {len(rows4)} active rows",
        loc="left",
        fontsize=13,
        weight="bold",
        pad=12,
    )
    ax.text(0.0, 1.015, "Full map: 3,003 x 126  |  rank 126  |  kernel 0", transform=ax.transAxes, fontsize=9.5, color=MUTED)
    ax.legend(loc="upper right", frameon=False, fontsize=9.5)

    # Panel (1, 0): Degree-5 E2 Hessian quotient map
    ax = axes[1, 0]
    style_axis(ax)
    e2 = report["lowDegreeBaseline"]["degree5E2Plot"]
    rows5 = e2["active_row_indices"]
    lookup5 = {r: i for i, r in enumerate(rows5)}
    entries5 = e2["residual_entries"]
    for c in e2["square_columns"]:
        ax.axvspan(c - 0.42, c + 0.42, color=GOLD, alpha=0.22, linewidth=0, zorder=0)
    for pos, color in ((True, TEAL), (False, CORAL)):
        pts = [(c, lookup5[r]) for r, c, v in entries5 if (Q(v) > 0) == pos]
        if pts:
            xx, yy = zip(*pts)
            ax.scatter(xx, yy, s=30, color=color, linewidths=0, marker="s", zorder=2)
    ax.set_xlim(-0.65, 20.65)
    ax.set_ylim(len(rows5) - 0.4, -0.6)
    ax.set_title(
        f"3. Degree 5 E2 Hessian quotient: rank 16/21, all 6 squares isolated",
        loc="left",
        fontsize=13,
        weight="bold",
        pad=14,
    )
    ax.text(
        0.0,
        1.015,
        "5 mixed Y2 columns vanish identically; 6 rational duals force a_i^2 = 0",
        transform=ax.transAxes,
        fontsize=9.5,
        color=MUTED,
    )
    ax.set_ylabel("Active quotient rows\n(sorted by row index)")
    ax.set_xticks(range(21))
    labels = [
        fr"$a_{{{p[0]}}}^2$" if p[0] == p[1] else fr"$a_{{{p[0]}}}a_{{{p[1]}}}$"
        for p in e2["quadratic_column_pairs"]
    ]
    ax.set_xticklabels(labels, rotation=90, fontsize=8.5)
    ax.set_xlabel("Quadratic gradient parameters a_i a_j (gold = isolated diagonal squares)")

    # Panel (1, 1): Deformed Nambu/Casimir Hamiltonian flow H = h_v d_u - h_u d_v on fiber (r=1, w=1, beta=1/2)
    ax = axes[1, 1]
    style_axis(ax)
    r_num, w_num, b_num = 1.0, 1.0, 0.5
    c0_n = 1.0 + r_num**6 + w_num**6
    c1_n = b_num * (r_num + r_num**3 * w_num)
    c2_n = (1.0 / 7.0) * r_num * b_num * (1.0 - b_num**2)
    c3_n = 1.0 + b_num**6
    ug = np.linspace(-1.5, 1.5, 120)
    vg = np.linspace(-1.5, 1.5, 120)
    U, V = np.meshgrid(ug, vg)
    H_cas = (3 * c0_n * c2_n - c1_n**2) * U**2 + (9 * c0_n * c3_n - c1_n * c2_n) * U * V + (3 * c1_n * c3_n - c2_n**2) * V**2
    F_cub = c0_n * U**3 + c1_n * U**2 * V + c2_n * U * V**2 + c3_n * V**3
    Hu = (9 * c0_n * c3_n - c1_n * c2_n) * U + 2 * (3 * c1_n * c3_n - c2_n**2) * V
    Hv = -2 * (3 * c0_n * c2_n - c1_n**2) * U - (9 * c0_n * c3_n - c1_n * c2_n) * V
    ax.contour(U, V, H_cas, levels=10, colors=TEAL, linewidths=1.1, alpha=0.85)
    ax.contour(U, V, F_cub, levels=[-2.0, -0.5, 0.0, 0.5, 2.0], colors=CORAL, linestyles="--", linewidths=1.0, alpha=0.8)
    ax.streamplot(ug, vg, Hu, Hv, color=GOLD, density=0.85, linewidth=0.9, arrowsize=0.9)
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_xlabel("Active coordinate u = X0^2")
    ax.set_ylabel("Active coordinate v = Y0^2")
    ax.set_title(
        "4. Deformed Nambu/Casimir flow H(h)=0 at (r,w,beta)=(1,1,1/2)",
        loc="left",
        fontsize=13,
        weight="bold",
        pad=14,
    )
    ax.text(
        0.0,
        1.015,
        r"Teal: $h(u,v)$  |  Coral: $f(u,v)$  |  $L_h=0$ does not imply $\mathrm{disc}(h)=0$",
        transform=ax.transAxes,
        fontsize=9.2,
        color=MUTED,
    )

    fig.text(
        0.07,
        0.042,
        "Result: No certificate exists for deg D <= 5 over C. Cramer's identity disc(h) u^2 = L_u f_u + L_v f_v + L_h h holds universally,",
        fontsize=11,
        weight="bold",
    )
    fig.text(
        0.07,
        0.018,
        "On X1*Y1 = 0 the selected coefficient L_h vanishes; this does not imply Hessian degeneracy. Higher-degree certificates are outside this pilot.",
        fontsize=10,
        color=MUTED,
    )

    fig.savefig(PNG_PATH, dpi=110, facecolor=PAPER)
    fig.savefig(SVG_PATH, facecolor=PAPER)
    # Matplotlib path elements can carry trailing spaces; keep generated text clean.
    svg = SVG_PATH.read_text(encoding="utf-8")
    SVG_PATH.write_text("\n".join(line.rstrip() for line in svg.splitlines()) + "\n",
                        encoding="utf-8", newline="\n")
    plt.close(fig)


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
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    render_figures(report)
    digest = hashlib.sha256(REPORT_PATH.read_bytes()).hexdigest()[:16]
    print(f"PASS: one-reflection-skew pilot verified and figures rendered (report sha256[:16]={digest})")


if __name__ == "__main__":
    main()
