"""Export exact selected-row data as transparent Lean integer literals.

This is a data exporter, not the independent source-coefficient verification.
"""

from pathlib import Path
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent


def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def source(data):
    index = data["case_index"]
    count = len(data["rows"])
    columns = data["columns"]
    matrix_lines = []
    for row, item in enumerate(data["rows"]):
        for column, value in item["entries"]:
            matrix_lines.append(f"  | {row}, {column} => {value}")
    target_lines = [f"  | {row} => {item['target']}" for row, item in enumerate(data["rows"])]
    dual_lines = [f"  | {row} => {value}" for row, value in enumerate(data["dual"])]
    return f'''import HodgeLab.RowCertificate
import Mathlib.Data.Fintype.BigOperators
import Mathlib.Tactic.FinCases

/-!
Exact integer selected-row data for cyclic-Fano fixed case {index:02d}.
All {columns} columns are included; unspecified entries are zero.
The correspondence to the polynomial coefficient rows is checked separately.
-/

open scoped BigOperators

namespace HodgeLab.CyclicFano.Case{index:02d}

def matrix (row : Fin {count}) (column : Fin {columns}) : ℤ :=
  match row.val, column.val with
{chr(10).join(matrix_lines)}
  | _, _ => 0

def target (row : Fin {count}) : ℤ :=
  match row.val with
{chr(10).join(target_lines)}
  | _ => 0

def dual (row : Fin {count}) : ℤ :=
  match row.val with
{chr(10).join(dual_lines)}
  | _ => 0

set_option maxRecDepth 100000 in
set_option maxHeartbeats 2000000 in
theorem annihilates : ∀ column : Fin {columns},
    ∑ row, dual row * matrix row column = 0 := by
  intro column
  fin_cases column <;> decide

set_option maxRecDepth 100000 in
set_option maxHeartbeats 2000000 in
theorem separates : ∑ row, dual row * target row ≠ 0 := by decide

/-- Inconsistency of the actual encoded integer rows over every
characteristic-zero field. Source-coefficient identification is external. -/
theorem no_solution {{K : Type*}} [Field K] [CharZero K] :
    ¬ ∃ coefficients : Fin {columns} → K,
      ∀ row : Fin {count}, ∑ column, (matrix row column : K) * coefficients column =
        (target row : K) :=
  HodgeLab.no_solution_of_integer_row_certificate matrix target dual annihilates separates

end HodgeLab.CyclicFano.Case{index:02d}
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cases", type=int, nargs="+", help="Fixed GPU case indices")
    args = parser.parse_args()
    out = ROOT / "HodgeLab" / "CyclicFano"
    out.mkdir(exist_ok=True)
    manifest = {"schema": "hodge-lab-concrete-lean-export-v1",
                "generator_lf_sha256": sha(Path(__file__)), "cases": []}
    audit_lines = []
    for index in sorted(set(args.cases)):
        input_file = REPO / "results" / "cyclic-fano-lean" / f"case-{index:02d}.json"
        data = json.loads(input_file.read_text(encoding="utf-8"))
        assert data["case_index"] == index
        assert data["columns"] == 175
        assert len(data["rows"]) == len(data["dual"])
        assert data["validation"]["status"] == "PASS"
        output_file = out / f"Case{index:02d}.lean"
        output_file.write_text(source(data), encoding="utf-8", newline="\n")
        module = f"HodgeLab.CyclicFano.Case{index:02d}"
        audit_lines.append(f"import {module}")
        manifest["cases"].append({
            "case_index": index, "input_file": input_file.relative_to(REPO).as_posix(),
            "input_lf_sha256": sha(input_file),
            "lean_file": output_file.relative_to(ROOT).as_posix(),
            "lean_lf_sha256": sha(output_file), "module": module,
            "selected_rows": len(data["rows"]), "columns": data["columns"],
            "target_pairing": data["target_pairing"],
        })
    audit_lines += ["", "#print axioms HodgeLab.no_solution_of_row_certificate",
                    "#print axioms HodgeLab.no_solution_of_integer_row_certificate"]
    for case in manifest["cases"]:
        for name in ("annihilates", "separates", "no_solution"):
            audit_lines.append(f"#print axioms {case['module']}.{name}")
    (ROOT / "AuditConcrete.lean").write_text("\n".join(audit_lines) + "\n",
                                            encoding="utf-8", newline="\n")
    (ROOT / "results" / "concrete-export.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": "EXPORTED", "cases": args.cases,
                      "limits": "Lean compilation and source-row verification are separate checks."}))


if __name__ == "__main__":
    main()
