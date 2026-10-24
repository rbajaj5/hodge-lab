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
if sha(raw) != '760a3e5cc7c7e0e941a482f2f554cf372f5145371ebf48ff5498300af20da9b3':
    raise RuntimeError('Delivered full-matrix SHA256 mismatch')
if sha(local) != '1c41301ad2a113d530bbd3b13c4ee004ac22fb55219b8bab99ae9850d46ac9e6':
    raise RuntimeError('Coordinator frozen NPY SHA256 mismatch')
full = np.fromfile(raw, dtype='<u2')
if full.size != 6000 * 5911:
    raise RuntimeError('Wrong full-matrix byte count')
full = full.reshape(6000, 5911)
minor = np.load(local, allow_pickle=False)
if minor.shape != (5911, 5911):
    raise RuntimeError('Wrong frozen minor dimensions')
if not np.array_equal(full[:5911], minor):
    raise RuntimeError('Decisive-entry binding failed')
receipt = {'status': 'PASS_IO_ONLY_FROZEN_MINOR_BINDING',
           'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'seconds': time.monotonic() - start, 'entries_compared': 5911 * 5911,
           'files': {str(raw): sha(raw), str(local): sha(local)},
           'script_sha256': sha(Path(__file__)), 'numpy': np.__version__,
           'new_mathematics_executed': False, 'determinant_rerun': False,
           'scope': 'Matrix entries only; coordinator independently binds delivered domain and basis records.'}
(out / 'validation.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
print(json.dumps(receipt, indent=2))
