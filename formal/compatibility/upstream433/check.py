"""Fresh, isolated validation of the two exact upstream proposal modules.

The copied upstream lakefile, manifest, and final 4.33.0 toolchain are fixed.
This checks compatibility, not the rest of the upstream repository.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
OUT = ROOT / "results"
HEAD = "84b1c1584b7615ec7189e896df2734a0833e84e1"
MATHLIB = "db584cd6d46c92f209a44c0f1c829460d327499d"
MODULES = ["HodgeTestbed.RowCertificate", "HodgeTestbed.RowCertificateExample"]
THEOREMS = [
    "HodgeTestbed.no_solution_of_row_certificate",
    "HodgeTestbed.no_solution_of_integer_row_certificate",
    "HodgeTestbed.RowCertificateExample.annihilates",
    "HodgeTestbed.RowCertificateExample.separates",
    "HodgeTestbed.RowCertificateExample.no_solution",
]
ALLOWED = {"propext", "Classical.choice", "Quot.sound"}
RECEIPT = {
    "schema": "hodge-lab-upstream-lean433-compatibility-v1",
    "status": "IN_PROGRESS", "upstream_proposal_head": HEAD,
    "modules": MODULES, "commands": [], "negative_controls": [],
    "scope": "Only the two exact proposed maintenance modules: generic finite-row obstruction and literal mixed case05 over characteristic-zero fields. No full-upstream build, polynomial-to-row formalization, or HasCertificate claim.",
    "replay_scope": "Official leanchecker default replay of each target module, sequentially; imported dependencies are trusted, not recursively replayed with --fresh.",
}


def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def checkpoint():
    save(OUT / "validation.json", RECEIPT)


def inputs():
    binding = json.loads((ROOT / "bindings.json").read_text(encoding="utf-8"))
    assert binding["upstream_head"] == HEAD
    assert binding["lean_toolchain"] == "leanprover/lean4:v4.33.0"
    assert binding["mathlib_commit"] == MATHLIB
    for name, expected in binding["copied_lf_sha256"].items():
        assert sha(ROOT / name) == expected, "Changed pinned input: " + name
    assert (ROOT / "lean-toolchain").read_text(encoding="utf-8").strip() == binding["lean_toolchain"]
    manifest = json.loads((ROOT / "lake-manifest.json").read_text(encoding="utf-8"))
    assert next(p for p in manifest["packages"] if p["name"] == "mathlib")["rev"] == MATHLIB
    source_inputs = {}
    for local, prior in binding["proposal_source_files"].items():
        assert sha(ROOT / local) == sha(REPO / prior), "Source differs from frozen proposal"
        source_inputs[prior] = sha(REPO / prior)
    for path in ROOT.rglob("*.lean"):
        if ".lake" not in path.parts:
            assert not re.search(r"\b(sorry|admit|axiom|native_decide)\b", path.read_text(encoding="utf-8")), path
    files = list(binding["copied_lf_sha256"]) + ["bindings.json", "Audit.lean", "check.py"]
    return binding, manifest, {name: sha(ROOT / name) for name in files}, source_inputs


def artifact_parts(module):
    stem = ROOT / ".lake/build/lib/lean" / module.replace(".", "/")
    result = {}
    for suffix in (".olean", ".olean.server", ".olean.private"):
        path = stem.with_name(stem.name + suffix)
        if path.exists():
            result[path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    assert stem.with_name(stem.name + ".olean").exists(), "Missing built module " + module
    return result


def run(label, command, bound=300, expected_failure=False):
    env = os.environ.copy()
    # Lake computes an isolated import path. Do not inherit a notebook path.
    for key in ("LEAN_PATH", "LEAN_SRC_PATH"):
        env.pop(key, None)
    record = {"label": label, "command": command, "cwd": ROOT.relative_to(REPO).as_posix(),
              "bound_seconds": bound, "expected_failure": expected_failure,
              "status": "RUNNING", "exit_code": None}
    RECEIPT["commands"].append(record)
    checkpoint()
    start = time.perf_counter()
    output = ""
    try:
        result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True,
                                text=True, encoding="utf-8", timeout=bound)
        output = result.stdout + result.stderr
        record["exit_code"] = result.returncode
        if expected_failure:
            assert result.returncode != 0 and "error:" in output and "decide" in output and "false" in output, output
        else:
            assert result.returncode == 0, output
        record["status"] = "PASS"
    except subprocess.TimeoutExpired as error:
        def decode(value):
            return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else (value or "")
        output = decode(error.stdout) + decode(error.stderr)
        record["status"] = "TIMEOUT"
        raise
    except BaseException:
        record["status"] = "FAIL"
        raise
    finally:
        path = OUT / (label + ".log")
        path.write_text(output, encoding="utf-8", newline="\n")
        record.update({"elapsed_seconds": round(time.perf_counter() - start, 3),
                       "log": path.relative_to(ROOT).as_posix(), "log_lf_sha256": sha(path)})
        checkpoint()
        print(json.dumps({"stage": label, "status": record["status"],
                          "elapsed_seconds": record["elapsed_seconds"]}), flush=True)
    return output, record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-inputs-only", action="store_true")
    parser.add_argument("--fetch-cache", action="store_true")
    args = parser.parse_args()
    binding, manifest, hashes, prior = inputs()
    if args.check_inputs_only:
        print(json.dumps({"status": "INPUTS_PASS", "copied_files": len(binding["copied_lf_sha256"]),
                          "modules": MODULES, "lean_executed": False}))
        return
    OUT.mkdir(parents=True, exist_ok=True)
    RECEIPT.update({"source_lf_sha256": hashes, "proposal_source_lf_sha256": prior,
                    "workflow_lf_sha256": sha(REPO / ".github/workflows/lean-upstream.yml"),
                    "github_run_id": os.environ.get("GITHUB_RUN_ID"),
                    "github_sha": os.environ.get("GITHUB_SHA")})
    checkpoint()
    # Never reuse notebook or previous compatibility target builds.
    for module in MODULES:
        target = ROOT / ".lake/build/lib/lean" / (module.replace(".", "/") + ".olean")
        assert not target.exists(), "Fresh build required; use a fresh checkout: " + str(target)
    version, _ = run("version", ["lake", "env", "lean", "--version"])
    assert re.search(r"\bversion 4\.33\.0,", version), "Expected final Lean4.33.0, not an RC"
    RECEIPT["lean_version"] = version.strip()
    if args.fetch_cache:
        run("dependency-cache", ["lake", "exe", "cache", "get"], bound=600)
    packages = {}
    for package in manifest["packages"]:
        directory = ROOT / ".lake/packages" / package["name"]
        head, _ = run("dependency-" + package["name"],
                      ["git", "-C", str(directory), "rev-parse", "HEAD"], bound=30)
        assert head.strip() == package["rev"], "Dependency revision mismatch: " + package["name"]
        packages[package["name"]] = head.strip()
    RECEIPT["dependency_commits"] = packages
    assert inputs()[2] == hashes, "Dependency setup changed pinned source/config"
    build_parts = {}
    for index, module in enumerate(MODULES):
        _, record = run(f"build-{index:02d}", ["lake", "build", module])
        build_parts[module] = artifact_parts(module)
        record["artifact_raw_sha256"] = build_parts[module]
        checkpoint()
    audit, _ = run("axioms", ["lake", "env", "lean", "Audit.lean"])
    matches = re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]", audit)
    declarations = {name: [x.strip() for x in values.split(",") if x.strip()] for name, values in matches}
    assert len(matches) == len(THEOREMS) and set(declarations) == set(THEOREMS)
    assert all(set(values) <= ALLOWED for values in declarations.values())
    RECEIPT["theorem_axioms"] = declarations
    for index, module in enumerate(MODULES):
        assert artifact_parts(module) == build_parts[module]
        _, record = run(f"kernel-{index:02d}", ["lake", "env", "leanchecker", module])
        assert artifact_parts(module) == build_parts[module]
        record["artifact_raw_sha256"] = build_parts[module]
        checkpoint()
    original = (ROOT / "HodgeTestbed/RowCertificateExample.lean").read_text(encoding="utf-8")
    scratch = ROOT / ".lake/compatibility-negative"
    scratch.mkdir(parents=True, exist_ok=True)
    for label, before, after in [
        ("entry", "| 1, 119 => -756", "| 1, 119 => -755"),
        ("target", "| 1 => -5", "| 1 => 0"),
    ]:
        assert original.count(before) == 1
        path = scratch / (label + ".lean")
        path.write_text(original.replace(before, after), encoding="utf-8", newline="\n")
        _, record = run("negative-" + label, ["lake", "env", "lean", path.relative_to(ROOT).as_posix()],
                        expected_failure=True)
        record["mutated_source_lf_sha256"] = sha(path)
        RECEIPT["negative_controls"].append({"label": label, "command_label": record["label"],
            "before": before, "after": after, "mutated_source_lf_sha256": sha(path)})
    assert inputs()[2] == hashes, "Inputs changed during validation"
    assert all(artifact_parts(module) == build_parts[module] for module in MODULES)
    RECEIPT.update({"status": "PASS", "kernel_replay": "PASS", "negative_control_count": 2,
                    "theorems_audited": len(THEOREMS)})
    checkpoint()
    print(json.dumps({"status": "PASS", "modules": MODULES, "theorems_audited": 5,
                      "negative_controls": 2, "receipt": "results/validation.json"}), flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        RECEIPT.update({"status": "FAIL", "error": type(error).__name__ + ": " + str(error)})
        checkpoint()
        print(json.dumps({"status": "FAIL", "error": RECEIPT["error"]}), file=sys.stderr, flush=True)
        raise
