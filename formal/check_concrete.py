"""Compile and kernel-replay concrete integer coefficient obstructions.

This keeps the previous generic rank-gap source and receipt untouched.
The separate Python source audit establishes the polynomial meaning of rows.
"""

from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import shlex
import subprocess
import time

import generate_concrete

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
OUT = ROOT / "results" / "concrete"
ALLOWED = {"propext", "Classical.choice", "Quot.sound"}
FINGERPRINT = None
RESUME = False
MAX_NEW_COMMANDS = 0
NEW_COMMANDS = 0


class PauseAudit(Exception):
    pass


def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def artifact(command):
    if command[:2] == ["lake", "build"] or command[:3] == ["lake", "env", "leanchecker"]:
        return ROOT / ".lake/build/lib/lean" / (command[-1].replace(".", "/") + ".olean")
    return None


def run(label, command, bound=600, expect_failure=False):
    global NEW_COMMANDS
    checkpoint = OUT / (label + ".json")
    compiled = artifact(command)
    if RESUME and label != "version" and checkpoint.exists():
        saved = json.loads(checkpoint.read_text(encoding="utf-8"))
        log = ROOT / saved["log"]
        if (saved.get("source_fingerprint") == FINGERPRINT
                and saved["command"] == command
                and saved["expected_failure"] == expect_failure
                and log.exists() and saved["log_lf_sha256"] == sha(log)
                and (compiled is None or (compiled.exists() and
                     saved.get("artifact_sha256") == hashlib.sha256(compiled.read_bytes()).hexdigest()))
                and ((saved["exit_code"] != 0) if expect_failure else
                     (saved["exit_code"] == 0))):
            output = log.read_text(encoding="utf-8")
            if not expect_failure or "error:" in output:
                return output, saved
    if MAX_NEW_COMMANDS and NEW_COMMANDS >= MAX_NEW_COMMANDS:
        raise PauseAudit
    NEW_COMMANDS += 1
    start = time.perf_counter()
    execution_command = command
    if os.name == "nt":
        drive = ROOT.drive[0].lower()
        wsl_root = "/mnt/" + drive + ROOT.as_posix()[2:]
        execution_command = ["wsl.exe", "-e", "sh", "-lc",
                             "cd " + shlex.quote(wsl_root) + " && " + shlex.join(command)]
    result = subprocess.run(execution_command, cwd=ROOT, capture_output=True, text=True,
                            encoding="utf-8", timeout=bound)
    output = result.stdout + result.stderr
    log = OUT / (label + ".log")
    log.write_text(output, encoding="utf-8", newline="\n")
    if expect_failure:
        assert result.returncode != 0 and "error:" in output, output
    elif result.returncode != 0:
        raise RuntimeError(f"{label} failed: {output}")
    record = {"command": command, "execution_command": execution_command,
                    "source_fingerprint": FINGERPRINT,
                    "exit_code": result.returncode,
                    "elapsed_seconds": round(time.perf_counter() - start, 3),
                    "bound_seconds": bound, "log": log.relative_to(ROOT).as_posix(),
                    "log_lf_sha256": sha(log), "expected_failure": expect_failure}
    if compiled is not None:
        record["artifact_file"] = compiled.relative_to(ROOT).as_posix()
        record["artifact_sha256"] = hashlib.sha256(compiled.read_bytes()).hexdigest()
    checkpoint.write_text(json.dumps(record, indent=2) + "\n",
                                         encoding="utf-8", newline="\n")
    print(json.dumps({"stage": label, "exit_code": result.returncode,
                      "elapsed_seconds": record["elapsed_seconds"]}), flush=True)
    return output, record


def main():
    global FINGERPRINT, RESUME, MAX_NEW_COMMANDS
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", action="store_true",
                        help="Reuse successful checkpoints with identical complete source bindings")
    parser.add_argument("--max-new-commands", type=int, default=0,
                        help="Pause without a final receipt after this many new commands;0 means unlimited")
    args = parser.parse_args()
    assert args.max_new_commands >= 0
    RESUME, MAX_NEW_COMMANDS = args.resume, args.max_new_commands
    OUT.mkdir(exist_ok=True)
    export_file = ROOT / "results" / "concrete-export.json"
    export = json.loads(export_file.read_text(encoding="utf-8"))
    assert export["generator_lf_sha256"] == sha(ROOT / "generate_concrete.py")
    sources = ["lean-toolchain", "lakefile.toml", "lake-manifest.json",
               "HodgeLab/RowCertificate.lean", "AuditConcrete.lean",
               "generate_concrete.py", "check_concrete.py"]
    modules, theorem_names, inputs = ["HodgeLab.RowCertificate"], [
        "HodgeLab.no_solution_of_row_certificate",
        "HodgeLab.no_solution_of_integer_row_certificate"], {}
    for case in export["cases"]:
        input_file = REPO / case["input_file"]
        assert sha(input_file) == case["input_lf_sha256"]
        inputs[case["input_file"]] = sha(input_file)
        data = json.loads(input_file.read_text(encoding="utf-8"))
        output_file = ROOT / case["lean_file"]
        assert sha(output_file) == case["lean_lf_sha256"]
        assert output_file.read_text(encoding="utf-8") == generate_concrete.source(data)
        sources.append(case["lean_file"])
        modules.append(case["module"])
        theorem_names += [case["module"] + "." + name
                          for name in ("annihilates", "separates", "no_solution")]
    for name in sources:
        if name.endswith(".lean"):
            assert not re.search(r"\b(sorry|admit|axiom|native_decide)\b",
                                 (ROOT / name).read_text(encoding="utf-8"))
    FINGERPRINT = hashlib.sha256(json.dumps({
        "sources": {name: sha(ROOT / name) for name in sources},
        "inputs": inputs, "export": sha(export_file)
    }, sort_keys=True).encode()).hexdigest()
    version, version_record = run("version", ["lake", "env", "lean", "--version"])
    assert "version 4.31.0," in version
    build_records = []
    for index, module in enumerate(modules):
        _, record = run(f"build-{index:02d}", ["lake", "build", module])
        build_records.append(record)
    audit, audit_record = run("axioms", ["lake", "env", "lean", "AuditConcrete.lean"])
    declarations = {name: [a.strip() for a in axioms.split(",") if a.strip()]
                    for name, axioms in re.findall(
                        r"'([^']+)' depends on axioms: \[([^\]]*)\]", audit)}
    assert set(declarations) == set(theorem_names)
    assert all(set(axioms) <= ALLOWED for axioms in declarations.values())
    # leanchecker launches one task per supplied module. Keep replay sequential
    # so its imported environments do not multiply the resident memory demand.
    kernel_records = []
    for index, module in enumerate(modules):
        compiled = artifact(["lake", "build", module])
        assert hashlib.sha256(compiled.read_bytes()).hexdigest() == build_records[index]["artifact_sha256"]
        _, record = run(f"kernel-{index:02d}", ["lake", "env", "leanchecker", module])
        kernel_records.append(record)
    scratch = ROOT / ".lake" / "concrete-negative"
    scratch.mkdir(exist_ok=True)
    original = (ROOT / "HodgeLab/CyclicFano/Case05.lean").read_text(encoding="utf-8")
    mutations = [
        ("entry", original.replace("| 1, 119 => -756", "| 1, 119 => -755")),
        ("target", original.replace("| 1 => -5", "| 1 => 0")),
    ]
    controls = []
    for label, text in mutations:
        assert text != original
        path = scratch / (label + ".lean")
        path.write_text(text, encoding="utf-8", newline="\n")
        _, record = run("negative-" + label,
                        ["lake", "env", "lean", path.relative_to(ROOT).as_posix()],
                        expect_failure=True)
        controls.append(record)
    receipt = {
        "schema": "hodge-lab-concrete-coefficient-lean-v1", "status": "PASS",
        "lean_version": version.strip(),
        "mathlib_commit": "fabf563a7c95a166b8d7b6efca11c8b4dc9d911f",
        "export_lf_sha256": sha(export_file),
        "source_fingerprint": FINGERPRINT,
        "source_lf_sha256": {name: sha(ROOT / name) for name in sources},
        "input_lf_sha256": inputs,
        "commands": [version_record, *build_records, audit_record, *kernel_records],
        "theorem_axioms": declarations, "negative_controls": controls,
        "concrete_cases": [case["case_index"] for case in export["cases"]],
        "scope": "Inconsistency of the encoded selected coefficient rows over every characteristic-zero field. Identification with the full polynomial equations is independently checked in Python; no HasCertificate statement is formalized.",
    }
    path = ROOT / "results" / "concrete-coefficient-validation.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": "PASS", "concrete_cases": len(export["cases"]),
                      "theorems_audited": len(declarations), "negative_controls": len(controls),
                      "kernel_replay": "PASS", "receipt": path.relative_to(ROOT).as_posix()}))


if __name__ == "__main__":
    try:
        main()
    except PauseAudit:
        print(json.dumps({"status": "IN_PROGRESS", "new_commands": NEW_COMMANDS,
                          "final_receipt_written": False}), flush=True)
