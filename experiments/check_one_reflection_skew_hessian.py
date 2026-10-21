"""Independent exact audit of the saved diagonal pure-Hessian rowspace.

No repository arithmetic is imported. Checks saved physical rows, canonical source, and a height certificate.
"""
from fractions import Fraction as Q
from pathlib import Path
from itertools import combinations, combinations_with_replacement
import ast
import hashlib
import json
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
OUT = REPO / "results/repository-audit-20261021"
INPUT = REPO / "results/one-reflection-skew-degree6/one-reflection-skew/degree-6-e2.json"

def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()

def add(a, b, scalar=Q(1)):
    out = dict(a)
    for k, v in b.items():
        out[k] = out.get(k, Q(0)) + scalar * v
        if not out[k]:
            del out[k]
    return out

def echelon(vectors, track=False):
    basis = {}
    for index, vector in enumerate(vectors):
        v, t = dict(vector), {index: Q(1)}
        for pivot, (b, bt) in sorted(basis.items()):
            if pivot in v:
                factor = v[pivot]
                v = add(v, b, -factor)
                if track:
                    t = add(t, bt, -factor)
        if v:
            pivot = min(v)
            scale = v[pivot]
            basis[pivot] = ({k: x / scale for k, x in v.items()},
                            {k: x / scale for k, x in t.items()} if track else {})
    return basis

def express(vector, basis):
    v, t = dict(vector), {}
    for pivot, (b, bt) in sorted(basis.items()):
        if pivot in v:
            factor = v[pivot]
            v = add(v, b, -factor)
            t = add(t, bt, factor)
    assert not v, ("not in span", v)
    return t

def encoded(poly):
    return [[list(m) if isinstance(m, tuple) else m, str(c)] for m, c in sorted(poly.items())]

def monomials(n, d):
    return list(combinations_with_replacement(range(n), d)) if d >= 0 else []

def graded_koszul(equations, n, degree):
    length = len(equations)
    bases = [[(wedge, mon) for wedge in combinations(range(length), k)
              for mon in monomials(n, degree - 2*k)] for k in range(length + 1)]
    indices = [{v: j for j, v in enumerate(b)} for b in bases]
    differentials = {0: []}
    for k in range(1, length + 1):
        cols = []
        for wedge, mon in bases[k]:
            col = {}
            for pos, generator in enumerate(wedge):
                rest = wedge[:pos] + wedge[pos+1:]
                for term, coefficient in equations[generator].items():
                    row = indices[k-1][rest, tuple(sorted(mon + term))]
                    col = add(col, {row: coefficient}, Q((-1)**pos))
            cols.append(col)
        differentials[k] = cols
    compositions = 0
    for k in range(2, length + 1):
        for col in differentials[k]:
            image = {}
            for j, c in col.items():
                image = add(image, differentials[k-1][j], c)
            assert not image, (degree, k, image)
            compositions += 1
    ranks = [0] + [len(echelon(differentials[k])) for k in range(1, length + 1)] + [0]
    homology = [len(bases[k]) - ranks[k] - ranks[k+1] for k in range(length + 1)]
    assert all(h >= 0 for h in homology)
    return {"degree": degree, "complex_dimensions_K0_to_K4": [len(b) for b in bases],
            "differential_ranks_d1_to_d4": ranks[1:-1], "homology_H0_to_H4": homology,
            "kernel_d1_dimension": len(bases[1]) - ranks[1],
            "d_squared_zero_columns": compositions}

def residue(x, p):
    return x.numerator % p * pow(x.denominator, -1, p) % p

def modular_independent_columns(columns, p):
    basis, chosen = {}, []
    for j, column in enumerate(columns):
        v = {r: residue(c, p) for r, c in column.items() if residue(c, p)}
        for pivot, b in sorted(basis.items()):
            if pivot in v:
                factor = v[pivot]
                for row, c in b.items():
                    v[row] = (v.get(row, 0) - factor*c) % p
                    if not v[row]:
                        del v[row]
        if v:
            pivot = min(v)
            inv = pow(v[pivot], -1, p)
            basis[pivot] = {r: c*inv % p for r, c in v.items()}
            chosen.append(j)
    return chosen

def determinant_mod(matrix, p):
    matrix = [[x % p for x in row] for row in matrix]
    det = 1
    for j in range(len(matrix)):
        pivot = next((i for i in range(j, len(matrix)) if matrix[i][j]), None)
        if pivot is None:
            return 0
        if pivot != j:
            matrix[pivot], matrix[j] = matrix[j], matrix[pivot]
            det = -det
        d = matrix[j][j]
        det = det*d % p
        inv = pow(d, -1, p)
        for i in range(j+1, len(matrix)):
            factor = matrix[i][j]*inv % p
            for k in range(j, len(matrix)):
                matrix[i][k] = (matrix[i][k] - factor*matrix[j][k]) % p
    return det % p

def main():
    if not __debug__:
        raise RuntimeError("Do not run with -O.")
    start = time.perf_counter()
    packet = json.loads(INPUT.read_text(encoding="utf-8"))
    remaining = packet["remaining_parameters"]
    assert remaining == [0, 7, 14, 21, 28]
    local = {raw: i for i, raw in enumerate(remaining)}
    pairs = packet["quadratic_column_pairs"]
    physical = {}
    for row, col, coefficient in packet["matrix_plot"]["residual_entries"]:
        i, j = pairs[col]
        if i in local and j in local:
            key = tuple(sorted((local[i], local[j])))
            physical[row] = add(physical.get(row, {}), {key: Q(coefficient)})
    physical = {r: q for r, q in physical.items() if q}
    rows = sorted(physical)
    actual = [physical[r] for r in rows]
    actual_basis = echelon(actual, True)
    assert len(actual_basis) == 4
    node = {(1,1): Q(1), (1,2): Q(-2,3), (1,3): Q(-2,3), (1,4): Q(-2,3),
            (2,2): Q(5,9), (3,3): Q(5,9), (4,4): Q(5,9),
            (2,3): Q(-2,9), (2,4): Q(-2,9), (3,4): Q(-2,9)}
    kramers = {(0,3): Q(1), (0,4): Q(-1), (1,3): Q(1), (1,4): Q(-1),
               (3,3): Q(-1), (4,4): Q(1)}
    bridge = {(0,0): Q(1), (0,1): Q(-1), (0,4): Q(-1), (1,3): Q(1),
              (3,3): Q(-1), (3,4): Q(1)}
    anchor = {(0,1): Q(1), (0,4): Q(-1), (1,2): Q(10,9), (1,3): Q(-5,9),
              (1,4): Q(-14,9), (2,2): Q(-25,27), (2,3): Q(10,27),
              (2,4): Q(10,27), (3,3): Q(47,27), (3,4): Q(-89,27), (4,4): Q(74,27)}
    generators = [node, kramers, bridge, anchor]
    canonical_path = REPO / "experiments/one_reflection_skew_koszul_homology.py"
    tree = ast.parse(canonical_path.read_text(encoding="utf-8"))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "canonical_quadrics")
    namespace = {"Q": Q}
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(canonical_path), "exec"), namespace)
    declared = namespace["canonical_quadrics"]()
    assert declared["P_Hess"] == generators, "Canonical Hessian generators changed"
    # Regression: the old full-E2 Q3 must not silently replace Q_anchor.
    old_q3 = declared["P_full"][2]
    try:
        express(old_q3, actual_basis)
    except AssertionError:
        pass
    else:
        raise AssertionError("Expected Q3 to lie outside physical Hessian rowspace")
    assert sum(old_q3.values()) == Q(5,4)
    assert all(sum(q.values()) == 0 for q in actual)

    candidate_basis = echelon(generators, True)
    assert len(candidate_basis) == 4
    forward = [express(q, actual_basis) for q in generators]
    reverse = [express(q, candidate_basis) for q in actual]
    for q, weights in zip(generators, forward):
        rebuild = {}
        for i, c in weights.items():
            rebuild = add(rebuild, actual[i], c)
        assert rebuild == q
    for q, weights in zip(actual, reverse):
        rebuild = {}
        for i, c in weights.items():
            rebuild = add(rebuild, generators[i], c)
        assert rebuild == q
    complexes = [graded_koszul(generators, 5, d) for d in range(2, 7)]
    assert [c["homology_H0_to_H4"][0] for c in complexes] == [11, 15, 16, 16, 16]
    assert all(c["homology_H0_to_H4"][1:] == [0,0,0,0] for c in complexes)

    # Independent finite certificate for height4, not an extrapolation from H1 samples.
    restricted = [{m: c for m,c in q.items() if 4 not in m} for q in generators]
    target_mon = monomials(4, 5)
    row_index = {m:i for i,m in enumerate(target_mon)}
    labels, columns = [], []
    for i, q in enumerate(restricted):
        for multiplier in monomials(4, 3):
            labels.append([i, list(multiplier)])
            columns.append({row_index[tuple(sorted(multiplier + m))]: c for m,c in q.items()})
    prime = 101
    chosen = modular_independent_columns(columns, prime)
    rational_rank = len(echelon(columns))
    assert len(chosen) == rational_rank == len(target_mon) == 56
    selected = [[residue(columns[j].get(i, Q(0)), prime) for j in chosen] for i in range(56)]
    determinant = determinant_mod(selected, prime)
    assert determinant != 0
    assert all(sum(q.values()) == 0 for q in generators)  # all-ones projective point
    report = {
        "status": "PASS",
        "audited_commit": "09539bb5151f918f73ec9fd4b9faba781959c436",
        "source_lf_sha256": {INPUT.relative_to(REPO).as_posix(): sha(INPUT), canonical_path.relative_to(REPO).as_posix(): sha(canonical_path)},
        "regression_counterexample": {"point": [1,1,1,1,1], "physical_rows_zero": True, "rejected_Q3_value": "5/4"},
        "review_script_lf_sha256": sha(Path(__file__)),
        "parameter_order": ["a0", "a1", "a2", "a3", "a4"],
        "monomial_encoding": "sorted tuples of parameter indices, with repetition",
        "physical_residual_row_labels": rows,
        "physical_nonzero_row_count": len(rows),
        "physical_rank": len(actual_basis),
        "generators": [{"name": name, "polynomial": encoded(q),
                        "physical_row_combination": [[rows[i], str(c)] for i,c in sorted(weights.items())]}
                       for name,q,weights in zip(["Q_node/9", "Q_Kramers", "Q_bridge", "Q_anchor"], generators, forward)],
        "physical_rows_in_generators": [[row, encoded(w)] for row,w in zip(rows,reverse)],
        "koszul_complexes": complexes,
        "regular_sequence_certificate": {
            "hyperplane": "a4=0", "field": "Q; nonzero minor reduced modulo101",
            "degree": 5, "row_monomials": [list(m) for m in target_mon],
            "column_labels_generator_and_degree3_multiplier": labels,
            "matrix_shape": [56,80], "rational_rank": rational_rank,
            "prime": prime, "selected_column_indices": chosen,
            "selected_minor_determinant_mod_prime": determinant,
            "denominators_prime_units": all(c.denominator % prime for q in restricted for c in q.values()),
            "argument": [
                "The nonzero56-minor proves every degree5 monomial in Q[a0,a1,a2,a3] lies in the restricted ideal.",
                "Thus radical(I+(a4))=(a0,a1,a2,a3,a4), so height(I+(a4))=5.",
                "The principal ideal height bound gives height(I)>=4; four generators give height(I)<=4.",
                "In the Cohen-Macaulay polynomial ring, these four homogeneous generators of a height4 ideal form a regular sequence.",
                "Consequently all positive Koszul homology vanishes in every degree, and Hilbert series is (1+t)^4/(1-t).",
                "These conclusions persist under field extension to C; projective scheme length is16, with no reducedness claim."
            ],
            "scope": "The finite H1 profile alone was not used as an all-degree criterion; this separate height certificate supplies the missing argument."
        },
        "elapsed_seconds": time.perf_counter()-start
    }
    OUT.mkdir(parents=True, exist_ok=True)
    destination = OUT / "corrected-hessian-validation.json"
    destination.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status":"PASS", "physical_rows":len(rows), "rank":4,
                      "homology":[c["homology_H0_to_H4"] for c in complexes],
                      "slice_shape":[56,80], "slice_rank":rational_rank,
                      "minor_mod101":determinant, "elapsed_seconds":report["elapsed_seconds"]}))

if __name__ == "__main__":
    main()
