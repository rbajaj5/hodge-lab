"""Export an explicit Case05 polynomial model; no computed matrix assumptions."""
from pathlib import Path
from fractions import Fraction
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
sys.path.insert(0, str(REPO / "experiments"))
import check_cyclic_fano_cubic_polars as C
from check_cyclic_fano_lean import source_dependencies


def rational(value):
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"({value.numerator} / {value.denominator})"


def exp(powers):
    assert powers[2] == 0
    return "exp " + " ".join(str(powers[i]) for i in C.BASE)


def sparse(polynomial):
    terms = []
    for powers, coefficient in sorted(polynomial.items(), reverse=True):
        assert coefficient[1] == 0
        terms.append(f"({exp(powers)}, {rational(coefficient[0])})")
    return "[" + ",\n    ".join(terms) + "]"


def main():
    exact = C.derive()
    labels = exact["compact_labels"]
    specs = []
    for index, label in enumerate(labels):
        if label["kind"] == "quadratic_base_pair":
            i, j = (C.BASE.index(v) for v in label["pair"])
            value = f".base {i} {j} ({exp(label['multiplier_powers'])})"
        else:
            value = f".mixed {C.BASE.index(label['coordinate'])} {C.BASE.index(label['linear_coordinate'])}"
        specs.append(f"  | {index} => {value}")
    text = '''import HodgeLab.SparsePolynomial
import HodgeLab.CyclicFano.Case05
import Mathlib.Data.Fin.VecNotation

/-!
The explicit five-variable polynomial equation for mixed cubic case05.
Variable order is X0,X1,Y0,Y1,Y2. Source-to-model identification and
completeness of the projected correction space remain separate checks.
-/

open scoped BigOperators
namespace HodgeLab.CyclicFano.Case05Polynomial
open HodgeLab.SparsePolynomial

def exp (a b c d e : ℕ) : Exponent := ![a,b,c,d,e]
def qSparse : Sparse := __Q__
def hSparse : Sparse := __H__
def betaSparse : Sparse := __BETA__
def v0 : Sparse := [(exp 3 0 0 0 0, 1)]
def v1 : Sparse := [(exp 0 0 0 0 3, 1)]
def deltaSparse : Sparse := subtract (multiply qSparse qSparse) (scale 4 hSparse)
def denominatorSparse : Sparse :=
  multiply v0 (derivative 0 deltaSparse) ++ multiply v1 (derivative 1 deltaSparse)
def rhsSparse : Sparse := scale 4 (subtract
  (multiply (derivative 0 (multiply betaSparse v0) ++
             derivative 1 (multiply betaSparse v1)) denominatorSparse)
  (multiply betaSparse (multiply v0 (derivative 0 denominatorSparse) ++
                       multiply v1 (derivative 1 denominatorSparse))))

inductive Correction where
  | base (i j : Fin 5) (h : Exponent)
  | mixed (i k : Fin 5)

def correction (column : Fin 175) : Correction :=
  match column.val with
__SPECS__
  | _ => .base 0 1 (exp 2 0 0 0 0)

def xSparse (i : Fin 5) : Sparse := [(fun j => if j = i then 1 else 0, 1)]
def columnSparse (column : Fin 175) : Sparse :=
  match correction column with
  | .base i j h =>
    let f : Sparse := [(h, 1)]
    subtract
      (multiply denominatorSparse (subtract
        (multiply (derivative i deltaSparse) (derivative j f))
        (multiply (derivative j deltaSparse) (derivative i f))))
      (multiply f (subtract
        (multiply (derivative i deltaSparse) (derivative j denominatorSparse))
        (multiply (derivative j deltaSparse) (derivative i denominatorSparse))))
  | .mixed i k =>
    multiply (xSparse k) (subtract
      (multiply denominatorSparse (derivative i deltaSparse))
      (scale 2 (multiply deltaSparse (derivative i denominatorSparse)))) ++
    scale 2 (multiply (multiply deltaSparse denominatorSparse) (derivative i (xSparse k)))

noncomputable def delta : MvPolynomial (Fin 5) ℚ := eval deltaSparse
noncomputable def denominator : MvPolynomial (Fin 5) ℚ := eval denominatorSparse
noncomputable def rhs : MvPolynomial (Fin 5) ℚ := eval rhsSparse
noncomputable def column (j : Fin 175) : MvPolynomial (Fin 5) ℚ := eval (columnSparse j)

def rowExponent (row : Fin 2) : Exponent :=
  if row.val = 0 then exp 0 1 7 1 5 else exp 1 0 5 2 6
def rowScale (row : Fin 2) : ℚ := if row.val = 0 then 49 / 2400 else 147 / 40

set_option maxRecDepth 100000 in
set_option maxHeartbeats 4000000 in
theorem computed_column_coefficients : ∀ row : Fin 2, ∀ j : Fin 175,
    rowScale row * coefficient (rowExponent row) (columnSparse j) =
      (Case05.matrix row j : ℚ) := by
  intro row j
  fin_cases row <;> fin_cases j <;> decide +kernel

set_option maxRecDepth 100000 in
set_option maxHeartbeats 4000000 in
theorem computed_target_coefficients : ∀ row : Fin 2,
    rowScale row * coefficient (rowExponent row) rhsSparse = (Case05.target row : ℚ) := by
  intro row
  fin_cases row <;> decide +kernel

theorem column_coefficients (row : Fin 2) (j : Fin 175) :
    rowScale row * MvPolynomial.coeff (exponent (rowExponent row)) (column j) =
      (Case05.matrix row j : ℚ) := by
  exact (coefficient_eval (rowExponent row) (columnSparse j)).symm ▸
    computed_column_coefficients row j

theorem target_coefficients (row : Fin 2) :
    rowScale row * MvPolynomial.coeff (exponent (rowExponent row)) rhs =
      (Case05.target row : ℚ) := by
  exact (coefficient_eval (rowExponent row) rhsSparse).symm ▸ computed_target_coefficients row

theorem delta_formula : delta = eval qSparse * eval qSparse -
    MvPolynomial.C 4 * eval hSparse := by
  simp [delta, deltaSparse]

theorem denominator_formula : denominator =
    eval v0 * MvPolynomial.pderiv 0 delta + eval v1 * MvPolynomial.pderiv 1 delta := by
  simp [denominator, denominatorSparse, delta]

theorem rhs_formula : rhs = MvPolynomial.C 4 *
    ((MvPolynomial.pderiv 0 (eval betaSparse * eval v0) +
      MvPolynomial.pderiv 1 (eval betaSparse * eval v1)) * denominator -
     eval betaSparse * (eval v0 * MvPolynomial.pderiv 0 denominator +
                       eval v1 * MvPolynomial.pderiv 1 denominator)) := by
  simp [rhs, rhsSparse, denominator]

noncomputable def columnFormula (j : Fin 175) : MvPolynomial (Fin 5) ℚ :=
  match correction j with
  | .base i k h =>
    let f := eval [(h, 1)]
    denominator * (MvPolynomial.pderiv i delta * MvPolynomial.pderiv k f -
                   MvPolynomial.pderiv k delta * MvPolynomial.pderiv i f) -
    f * (MvPolynomial.pderiv i delta * MvPolynomial.pderiv k denominator -
         MvPolynomial.pderiv k delta * MvPolynomial.pderiv i denominator)
  | .mixed i k =>
    eval (xSparse k) * (denominator * MvPolynomial.pderiv i delta -
      MvPolynomial.C 2 * (delta * MvPolynomial.pderiv i denominator)) +
    MvPolynomial.C 2 * ((delta * denominator) * MvPolynomial.pderiv i (eval (xSparse k)))

theorem column_formula (j : Fin 175) : column j = columnFormula j := by
  cases h : correction j <;>
    simp [column, columnSparse, columnFormula, h, denominator, delta]

theorem polynomial_equation_implies_matrix (c : Fin 175 → ℚ)
    (equation : ∑ j, MvPolynomial.C (c j) * column j = rhs) :
    ∀ row : Fin 2, ∑ j, (Case05.matrix row j : ℚ) * c j = (Case05.target row : ℚ) := by
  intro row
  calc
    ∑ j, (Case05.matrix row j : ℚ) * c j =
        ∑ j, (rowScale row * MvPolynomial.coeff (exponent (rowExponent row)) (column j)) * c j := by
          simp only [column_coefficients]
    _ = rowScale row * MvPolynomial.coeff (exponent (rowExponent row))
          (∑ j, MvPolynomial.C (c j) * column j) := by
          simp only [MvPolynomial.coeff_sum, MvPolynomial.coeff_C_mul, Finset.mul_sum]
          apply Finset.sum_congr rfl
          intro j hj
          simp only [mul_assoc, mul_left_comm, mul_comm]
    _ = rowScale row * MvPolynomial.coeff (exponent (rowExponent row)) rhs := by rw [equation]
    _ = (Case05.target row : ℚ) := target_coefficients row

theorem no_polynomial_solution :
    ¬ ∃ c : Fin 175 → ℚ, ∑ j, MvPolynomial.C (c j) * column j = rhs := by
  rintro ⟨c, equation⟩
  exact Case05.no_solution (K := ℚ) ⟨c, polynomial_equation_implies_matrix c equation⟩

end HodgeLab.CyclicFano.Case05Polynomial
'''
    text = text.replace("__Q__", sparse(exact["Q"])).replace("__H__", sparse(exact["H"]))
    text = text.replace("__BETA__", sparse(exact["beta"])).replace("__SPECS__", "\n".join(specs))
    path = ROOT / "HodgeLab/CyclicFano/Case05Polynomial.lean"
    if not path.exists() or path.read_text(encoding="utf-8") != text:
        path.write_text(text, encoding="utf-8", newline="\n")
    modules = ["HodgeLab.RowCertificate", "HodgeLab.CyclicFano.Case05",
               "HodgeLab.SparsePolynomial", "HodgeLab.CyclicFano.Case05Polynomial",
               "HodgeLab.CyclicFano.Case05PolynomialField"]
    files = [ROOT / (module.replace(".", "/") + ".lean") for module in modules]
    names = []
    for module, file in zip(modules, files):
        namespace = "HodgeLab.CyclicFano.Case05Polynomial" if module.endswith("PolynomialField") else module
        if module == "HodgeLab.RowCertificate":
            namespace = "HodgeLab"
        names += [namespace + "." + name for name in re.findall(
            r"\btheorem\s+([A-Za-z_][A-Za-z0-9_]*)", file.read_text(encoding="utf-8"))]
    dependencies = source_dependencies(Path(__file__)) | set(files)
    dependencies |= source_dependencies(Path(C.__file__))
    dependencies.add(REPO / "experiments/check_cyclic_fano_lean.py")
    dependencies.update([REPO / "results/cyclic-fano-curve/source/instance.rec",
                         REPO / "results/cyclic-fano-lean/case-05.json"])
    def digest(file):
        return hashlib.sha256(file.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    exported = {
        "schema": "hodge-lab-case05-polynomial-export-v1", "modules": modules,
        "theorem_names": names,
        "source_lf_sha256": {p.relative_to(REPO).as_posix(): digest(p) for p in sorted(dependencies)},
        "variable_order": ["X0", "X1", "Y0", "Y1", "Y2"],
        "direction": [[0, "1"], [69, "1"]], "correction_count": 175,
        "selected_rows": [[0, 1, 7, 1, 5], [1, 0, 5, 2, 6]],
        "row_scales": ["49/2400", "147/40"], "coefficient_checks": 352,
        "negative_controls": [
            {"label": "scale", "file": "formal/HodgeLab/CyclicFano/Case05Polynomial.lean",
             "before": "then 49 / 2400 else", "after": "then 49 / 2401 else"},
            {"label": "density", "file": "formal/HodgeLab/CyclicFano/Case05Polynomial.lean",
             "before": "def betaSparse : Sparse := [(exp 1 0 3 0 0, (1 / 3))]",
             "after": "def betaSparse : Sparse := [(exp 1 0 3 0 0, (1 / 4))]"},
        ],
        "scope": "Specifies explicit Case05 rational polynomial operators, sparse MvPolynomial semantics and352 coefficient identities, with statements deriving the existing2x175 matrix equation and impossibility over every characteristic-zero field after mapping rational coefficients. Use the separate validation receipt for completed compilation and replay status. Identification with the fixed source record and completeness of the projected correction family remain external exact checks; no HasCertificate claim.",
    }
    (ROOT / "results/polynomial-bridge-export.json").write_text(
        json.dumps(exported, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"generated": str(path), "corrections": len(labels),
                      "scope": "explicit operator arithmetic; theorem compilation pending"}))


if __name__ == "__main__":
    main()
