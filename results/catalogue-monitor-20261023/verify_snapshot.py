"""Read-only, bounded Git-data comparison; no mathematical or Lean replay.

Usage: python -X utf8 verify_snapshot.py PATH_TO_SEXTICS OUTPUT_JSON
Requires both pinned commits in the local clone. Uses only Python stdlib.
"""
import ast
import collections
import hashlib
import json
import platform
from pathlib import Path
import re
import subprocess
import sys
import time

OLD = "554757eca1aebecdd1d21f3452d3c71ffa601b19"
NEW = "4a8e09b6002d250094cb1c1152a6026c55030ead"
repo, output = Path(sys.argv[1]), Path(sys.argv[2])
started = time.monotonic()
commands = []


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def git(*args, input_data=None):
    remaining = 60 - (time.monotonic() - started)
    require(remaining > 0, "60-second total bound exhausted")
    command = ["git", "-C", str(repo), *args]
    p = subprocess.run(command, input=input_data, capture_output=True,
                       timeout=min(20, remaining))
    commands.append({"args": list(args), "exit_code": p.returncode})
    require(p.returncode == 0, p.stderr.decode("utf-8", errors="replace"))
    return p.stdout


def tree(revision):
    result = {}
    for entry in git("ls-tree", "-rz", revision).split(b"\0"):
        if not entry:
            continue
        metadata, name = entry.split(b"\t", 1)
        _, kind, sha = metadata.split()
        if kind == b"blob":
            result[name.decode("utf-8")] = sha.decode("ascii")
    return result


def blobs(revision, paths):
    payload = "".join(revision + ":" + p + "\n" for p in paths).encode("utf-8")
    data = git("cat-file", "--batch", input_data=payload)
    cursor, result = 0, {}
    for path in paths:
        end = data.index(b"\n", cursor)
        sha, kind, size = data[cursor:end].split()
        require(kind == b"blob", "Not a blob: " + path)
        size = int(size)
        body = data[end + 1:end + 1 + size]
        actual = hashlib.sha1(b"blob " + str(size).encode() + b"\0" + body).hexdigest()
        require(actual == sha.decode(), "Git blob hash mismatch: " + path)
        result[path] = body
        cursor = end + 2 + size
    require(cursor == len(data), "Unexpected cat-file output")
    return result


def target_fields(body):
    # Extract top-level scalar fields and indented continuations. This is a
    # literal source comparison, not a general YAML parser or polynomial parser.
    lines = body.decode("utf-8").splitlines()
    result = {}
    for key in ("id", "F", "q", "A"):
        matches = [i for i, line in enumerate(lines) if line.startswith(key + ":")]
        require(len(matches) == 1, "Missing/duplicate field " + key)
        i = matches[0]
        parts = [lines[i].split(":", 1)[1].strip()]
        for line in lines[i + 1:]:
            if not line.startswith((" ", "\t")):
                break
            parts.append(line.strip())
        result[key] = " ".join(parts)
    return result


before, after = tree(OLD), tree(NEW)
paths = sorted(p for p in before if p.startswith("data/") and p.endswith("/instance.rec"))
require(paths == sorted(p for p in after if p.startswith("data/") and p.endswith("/instance.rec")),
        "Target set changed")
require(len(paths) == 82, "Expected 82 pinned targets")
old_records, new_records = blobs(OLD, paths), blobs(NEW, paths)
targets = []
for path in paths:
    old_fields, new_fields = target_fields(old_records[path]), target_fields(new_records[path])
    require(old_fields == new_fields, "Protected scalar fields changed: " + path)
    targets.append({"path": path, "before_blob": before[path], "after_blob": after[path],
                    "before_sha256": hashlib.sha256(old_records[path]).hexdigest(),
                    "after_sha256": hashlib.sha256(new_records[path]).hexdigest(),
                    "fields": new_fields, "literal_fields_equal": True})

preserved = {}
for name in ("acceptance.json", "proof.json", "provenance.json", "why.md"):
    left = {p: s for p, s in before.items() if p.startswith("data/") and p.endswith("/" + name)}
    right = {p: s for p, s in after.items() if p.startswith("data/") and p.endswith("/" + name)}
    require(left == right, "Changed authoritative source set or bytes: " + name)
    preserved[name] = left
require(len(preserved["acceptance.json"]) == 66, "Expected 66 acceptance receipts")
acceptance_bodies = blobs(NEW, sorted(preserved["acceptance.json"]))
accepted = []
for path, body in acceptance_bodies.items():
    receipt = json.loads(body.decode("utf-8"))
    require(receipt["formalAcceptance"] is True, "Receipt not published: " + path)
    accepted.append({"id": receipt["instanceId"], "githubLogin": receipt["githubLogin"],
                     "acceptedAt": receipt["acceptedAt"], "blob": after[path]})
open_ids = sorted(t["fields"]["id"] for t in targets
                  if t["fields"]["id"] not in {r["id"] for r in accepted})
require(len(open_ids) == 16, "Expected 16 targets without acceptance")
require("one-reflection-skew" in open_ids and "four-plus-two-residual" in open_ids,
        "Focus target acceptance changed")

code_path = "scripts/proposals/acceptance.py"
old_code = blobs(OLD, [code_path])[code_path]
new_code = blobs(NEW, [code_path])[code_path]
def function_ast(source, name):
    functions = [n for n in ast.parse(source.decode("utf-8")).body
                 if isinstance(n, ast.FunctionDef) and n.name == name]
    require(len(functions) == 1, "Missing/duplicate function " + name)
    return ast.dump(functions[0], include_attributes=False)
require(function_ast(old_code, "read_acceptance") == function_ast(new_code, "read_acceptance"),
        "read_acceptance implementation changed")

changed = sorted(p for p in before.keys() | after.keys() if before.get(p) != after.get(p))
git_diff = git("diff", "--no-renames", "--name-status", OLD, NEW).decode("utf-8")
require(len(git_diff.splitlines()) == len(changed), "Incomplete Git comparison")
require(not [p for p in changed if p.startswith("formal/")], "Formal source changed")
result = {
    "status": "passed", "old": OLD, "new": NEW,
    "python": platform.python_version(), "git": git("--version").decode("utf-8").strip(),
    "limits": {"per_process_seconds": 20, "total_seconds": 60},
    "elapsed_seconds": round(time.monotonic() - started, 3), "commands": commands,
    "targets": targets, "preserved_blobs": preserved, "accepted": accepted, "open_ids": open_ids,
    "read_acceptance_ast_unchanged": True, "formal_source_changes": [],
    "complete_changed_path_count_no_rename_detection": len(changed), "complete_diff": git_diff.splitlines(),
    "changed_basename_counts": dict(collections.Counter(Path(p).name for p in changed)),
    "scope": "Literal F/q/A/id and byte preservation; published receipt flags inspected. No polynomial identity, receipt validator, protected verification, Lean build, website build, or discussion mathematics replay."
}
output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": result["status"], "targets": len(targets), "accepted": len(accepted),
                  "open": len(open_ids), "changed_paths": len(changed), "elapsed_seconds": result["elapsed_seconds"]}))
