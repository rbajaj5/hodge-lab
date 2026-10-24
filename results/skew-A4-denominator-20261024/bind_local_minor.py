"""IO-only handoff check; no coefficient construction or determinant execution.

Usage: python -O bind_local_minor.py FULL_UINT16_BIN COORDINATOR_MINOR_NPY FRESH_DIR
"""
from pathlib import Path
import datetime, hashlib, json, sys, time
import numpy as np

start = time.monotonic()
raw, local, out = map(Path, sys.argv[1:4])
out.mkdir(parents=True, exist_ok=False)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
if sha(raw) != 'e5822b368f62ac144256f9c3ff933c9ef6fd4002853f7f4fd084c67fb013322c':
    raise RuntimeError('Delivered full-matrix SHA256 mismatch')
if sha(local) != '8a79cf56d9f01acd1e09e14a8e6b0d7a40db6f945288fb04a0a89008be54efc3':
    raise RuntimeError('Coordinator frozen NPY SHA256 mismatch')
full = np.fromfile(raw, dtype='<u2')
if full.size != 3160 * 3103:
    raise RuntimeError('Wrong full-matrix byte count')
full = full.reshape(3160, 3103)
minor = np.load(local, allow_pickle=False)
if minor.shape != (3103, 3103):
    raise RuntimeError('Wrong frozen minor dimensions')
if not np.array_equal(full[:3103], minor):
    raise RuntimeError('Decisive-entry binding failed')
receipt = {'status': 'PASS_IO_ONLY_FROZEN_MINOR_BINDING',
           'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'seconds': time.monotonic() - start, 'entries_compared': 3103 * 3103,
           'files': {str(raw): sha(raw), str(local): sha(local)},
           'script_sha256': sha(Path(__file__)), 'numpy': np.__version__,
           'new_mathematics_executed': False, 'determinant_rerun': False}
(out / 'validation.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
print(json.dumps(receipt, indent=2))
