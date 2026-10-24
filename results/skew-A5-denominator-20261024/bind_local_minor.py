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
if sha(raw) != '63a48714c2f7a7ce3a20829540a8573607b5ced164b2203922604e60d9fa342e':
    raise RuntimeError('Delivered full-matrix SHA256 mismatch')
if sha(local) != '10dcc8f2d407fb8098eab61fa1f36eeed9ecfc495000f2eb79a99268f760c3b4':
    raise RuntimeError('Coordinator frozen NPY SHA256 mismatch')
full = np.fromfile(raw, dtype='<u2')
if full.size != 3860 * 3805:
    raise RuntimeError('Wrong full-matrix byte count')
full = full.reshape(3860, 3805)
minor = np.load(local, allow_pickle=False)
if minor.shape != (3805, 3805):
    raise RuntimeError('Wrong frozen minor dimensions')
if not np.array_equal(full[:3805], minor):
    raise RuntimeError('Decisive-entry binding failed')
receipt = {'status': 'PASS_IO_ONLY_FROZEN_MINOR_BINDING',
           'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'seconds': time.monotonic() - start, 'entries_compared': 3805 * 3805,
           'files': {str(raw): sha(raw), str(local): sha(local)},
           'script_sha256': sha(Path(__file__)), 'numpy': np.__version__,
           'new_mathematics_executed': False, 'determinant_rerun': False,
           'scope': 'Matrix entries only; coordinator independently binds delivered domain and basis records.'}
(out / 'validation.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
print(json.dumps(receipt, indent=2))
