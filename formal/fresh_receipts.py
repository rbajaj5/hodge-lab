"""Allocate fresh verification outputs without touching historical evidence.

Historical input manifests and receipts remain in their original directories.
By default each invocation gets a unique directory under results/runs. An
explicit --output-dir is relative to formal (or absolute), must not exist, and
must not be inside an immutable input directory, including through symlinks.
"""
from pathlib import Path
import argparse
import datetime
import uuid


def fresh_output_dir(root, label, protected_roots, argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path,
                        help='new output directory; relative paths are relative to formal')
    args = parser.parse_args(argv)
    if args.output_dir is None:
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        output = root / 'results/runs' / (label + '-' + stamp + '-' + uuid.uuid4().hex[:12])
    else:
        output = root / args.output_dir
    output = output.resolve()
    for historical in protected_roots:
        historical = historical.resolve()
        if output == historical or historical in output.parents:
            raise RuntimeError('Output overlaps immutable input directory: ' + str(historical))
    # Exclusive creation also rejects an existing PASS/FAIL receipt directory.
    # Callers assign OUT only after this succeeds, so a rejected path cannot
    # receive an exception-handler FAIL write.
    output.mkdir(parents=True, exist_ok=False)
    return output
