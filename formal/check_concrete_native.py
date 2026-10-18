"""Bounded official direct replay; preserves an immutable compilation receipt.

LEAN_PATH must identify the same package cache and local build objects.
This optional host workaround does not replace the ordinary Linux CI driver.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import subprocess
import time

import check_concrete as check

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results/concrete"


def save(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lean", required=True)
    parser.add_argument("--bound", type=int, default=420)
    args = parser.parse_args()
    export = json.loads((ROOT / "results/concrete-export.json").read_text())
    sources = ["lean-toolchain", "lakefile.toml", "lake-manifest.json",
               "HodgeLab/RowCertificate.lean", "AuditConcrete.lean",
               "generate_concrete.py", "check_concrete.py"]
    sources += [item["lean_file"] for item in export["cases"]]
    inputs = {item["input_file"]: check.sha(ROOT.parent / item["input_file"])
              for item in export["cases"]}
    binding = {"sources": {name: check.sha(ROOT / name) for name in sources},
               "inputs": inputs, "export": check.sha(ROOT / "results/concrete-export.json")}
    fingerprint = hashlib.sha256(json.dumps(binding, sort_keys=True).encode()).hexdigest()
    modules = ["HodgeLab.RowCertificate"] + [item["module"] for item in export["cases"]]
    records = []
    artifacts = {}
    for index, module in enumerate(modules):
        record = json.loads((OUT / f"build-{index:02d}.json").read_text())
        assert record["command"] == ["lake", "build", module]
        assert record["source_fingerprint"] == fingerprint and record["exit_code"] == 0
        assert check.sha(ROOT / record["log"]) == record["log_lf_sha256"]
        artifact = ROOT / record["artifact_file"]
        assert hashlib.sha256(artifact.read_bytes()).hexdigest() == record["artifact_sha256"]
        parts = {record["artifact_file"]: record["artifact_sha256"]}
        for suffix in (".server", ".private"):
            part = Path(str(artifact) + suffix)
            if part.exists():
                parts[part.relative_to(ROOT).as_posix()] = hashlib.sha256(part.read_bytes()).hexdigest()
        artifacts[module] = parts
        records.append(record)
    audit = json.loads((OUT / "axioms.json").read_text())
    assert audit["source_fingerprint"] == fingerprint and audit["exit_code"] == 0
    assert check.sha(ROOT / audit["log"]) == audit["log_lf_sha256"]
    declarations = {name: [a.strip() for a in axioms.split(",") if a.strip()]
                    for name, axioms in re.findall(
                        r"'([^']+)' depends on axioms: \[([^\]]*)\]",
                        (ROOT / audit["log"]).read_text())}
    expected = ["HodgeLab.no_solution_of_row_certificate",
                "HodgeLab.no_solution_of_integer_row_certificate"]
    expected += [item["module"] + "." + theorem for item in export["cases"]
                 for theorem in ("annihilates", "separates", "no_solution")]
    assert set(declarations) == set(expected)
    assert all(set(axioms) <= check.ALLOWED for axioms in declarations.values())
    compilation = {"schema": "hodge-lab-concrete-compilation-v1", "status": "PASS",
                   "source_fingerprint": fingerprint, **binding,
                   "commands": records + [audit], "artifacts": artifacts,
                   "theorem_axioms": declarations,
                   "scope": "All16 case modules and generic helper compile;50 axiom reports checked. Standalone replay is recorded separately."}
    save(ROOT / "results/concrete-compilation-validation.json", compilation)
    print("PASS compilation receipt", flush=True)
    command = [args.lean, "ReplayConcrete.lean"]
    version = subprocess.run([args.lean, "--version"], capture_output=True, text=True, timeout=30)
    assert version.returncode == 0 and "version 4.31.0," in version.stdout
    start = time.perf_counter()
    with (OUT / "native-replay.log").open("w", encoding="utf-8", newline="\n") as log:
        try:
            result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                    timeout=args.bound)
            exit_code, timed_out = result.returncode, False
        except subprocess.TimeoutExpired:
            exit_code, timed_out = None, True
    replayed = re.findall(r"^PASS (\S+)\s*$", (OUT / "native-replay.log").read_text(), re.M)
    assert replayed == modules[:len(replayed)]
    complete = exit_code == 0 and replayed == modules
    receipt = {"schema": "hodge-lab-direct-official-replay-v1",
               "status": "PASS" if complete else "INCOMPLETE",
               "compiler": version.stdout.strip(), "command": command,
               "lean_path": os.environ.get("LEAN_PATH"),
               "lean_executable_sha256": hashlib.sha256(Path(args.lean).read_bytes()).hexdigest(),
               "runner_lf_sha256": check.sha(ROOT / "ReplayConcrete.lean"),
               "driver_lf_sha256": check.sha(Path(__file__)),
               "compilation_receipt_lf_sha256": check.sha(ROOT / "results/concrete-compilation-validation.json"),
               "bound_seconds": args.bound, "elapsed_seconds": round(time.perf_counter()-start, 3),
               "exit_code": exit_code, "timed_out": timed_out,
               "expected_modules": modules, "replayed_modules": replayed,
               "artifacts": artifacts, "log": "results/concrete/native-replay.log",
               "log_lf_sha256": check.sha(OUT / "native-replay.log"),
               "scope": "Official default replayFromImports; imported declarations trusted, not --fresh. No proof or integer data changed."}
    save(ROOT / "results/concrete-direct-replay-validation.json", receipt)
    print(json.dumps({"status": receipt["status"], "replayed_modules": len(replayed)}), flush=True)


if __name__ == "__main__":
    main()
