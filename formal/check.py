"""Build, audit, and kernel-replay the notebook's generic rank-gap lemmas.

Run from this directory with Python 3 after installing the pinned dependencies.
The exact experiment's matrix bounds are NOT established by this script.
"""

from pathlib import Path
import hashlib
import json
import re
import subprocess
import time

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results"
THEOREMS = [
    "HodgeLab.not_mem_of_finrank_gap",
    "HodgeLab.not_mem_of_finrank_150_151",
    "HodgeLab.no_correction_solution_of_finrank_gap",
]
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
SOURCES = [
    "lean-toolchain", "lakefile.toml", "lake-manifest.json", "HodgeLab.lean",
    "HodgeLab/RankGap.lean", "Audit.lean", "check.py",
]


def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def run(label, command, bound=300):
    started = time.perf_counter()
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                            encoding="utf-8", timeout=bound)
    output = result.stdout + result.stderr
    (OUT / (label + ".log")).write_text(output, encoding="utf-8", newline="\n")
    if result.returncode:
        raise RuntimeError(f"{label} failed: {output}")
    return output, {"command": command, "exit_code": result.returncode,
                    "elapsed_seconds": round(time.perf_counter() - started, 3),
                    "bound_seconds": bound, "log": label + ".log",
                    "log_lf_sha256": sha(OUT / (label + ".log"))}


def main():
    OUT.mkdir(exist_ok=True)
    for path in ROOT.rglob("*.lean"):
        if ".lake" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        if re.search(r"\b(sorry|admit|axiom)\b", text):
            raise AssertionError(f"Unproved declaration token in {path}")
    version, version_record = run("version", ["lake", "env", "lean", "--version"])
    assert "version 4.31.0," in version
    _, build_record = run("build", ["lake", "build"])
    audit, audit_record = run("axioms", ["lake", "env", "lean", "Audit.lean"])
    matches = re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]", audit)
    declarations = {name: [x.strip() for x in axioms.split(",") if x.strip()]
                    for name, axioms in matches}
    assert set(declarations) == set(THEOREMS)
    for axioms in declarations.values():
        assert set(axioms) <= ALLOWED_AXIOMS
    _, kernel_record = run("kernel", ["lake", "env", "leanchecker", "HodgeLab.RankGap"])
    manifest = json.loads((ROOT / "lake-manifest.json").read_text(encoding="utf-8"))
    mathlib = next(x for x in manifest["packages"] if x["name"] == "mathlib")
    receipt = {
        "schema": "hodge-lab-rank-gap-lean-v1", "status": "PASS",
        "lean_version": version.strip(), "mathlib_commit": mathlib["rev"],
        "source_lf_sha256": {name: sha(ROOT / name) for name in SOURCES},
        "commands": [version_record, build_record, audit_record, kernel_record],
        "theorem_axioms": declarations,
        "scope": "Generic rank-gap implication only; actual matrix bounds, modular-minor transfer, and HasCertificate are not formalized.",
    }
    (OUT / "rank-gap-validation.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": "PASS", "theorems": THEOREMS,
                      "kernel_replay": "PASS", "receipt": "results/rank-gap-validation.json"}))


if __name__ == "__main__":
    main()
