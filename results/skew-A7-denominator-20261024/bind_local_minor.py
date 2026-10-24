"""IO-only delivery binding; no mathematical reconstruction or determinant.

Usage: python -O bind_local_minor.py FULL_RAW_UINT16 FROZEN_ARRAY FRESH_DIR
The coordinator relay specifies a uint16 array hash, not its container format.
This script accepts that exact file as NPY (magic header) or raw uint16.
"""
from pathlib import Path
import datetime, hashlib, json, sys, time
import numpy as np

start = time.monotonic()
raw, local, out = map(Path, sys.argv[1:4])
out.mkdir(parents=True, exist_ok=False)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
if sha(raw) != '7ab80831f8757663bc208ecb4a391509ab18080b0a6f776d0a4b57695c9e2230':
    raise RuntimeError('Delivered full-matrix SHA256 mismatch')
if sha(local) != '8f4a48490018861c4599e08ae1e6da0e279b874c260e96d6350af74110f81b28':
    raise RuntimeError('Coordinator frozen array SHA256 mismatch')
full = np.fromfile(raw, dtype='<u2')
if full.size != 5280*5209: raise RuntimeError('Wrong full-matrix byte count')
full = full.reshape(5280,5209)
with local.open('rb') as f: magic = f.read(6)
if magic == b'\x93NUMPY':
    minor = np.load(local, allow_pickle=False)
    container = 'NPY'
else:
    minor = np.fromfile(local, dtype='<u2')
    if minor.size != 5209*5209: raise RuntimeError('Wrong raw minor size')
    minor = minor.reshape(5209,5209)
    container = 'raw little-endian uint16'
if minor.shape != (5209,5209): raise RuntimeError('Wrong frozen minor dimensions')
if minor.dtype.kind != 'u' or minor.dtype.itemsize != 2:
    raise RuntimeError('Frozen minor is not uint16')
if not np.array_equal(full[:5209],minor):
    raise RuntimeError('Decisive-entry binding failed')
receipt={'status':'PASS_IO_ONLY_FROZEN_MINOR_BINDING',
         'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'seconds':time.monotonic()-start,'entries_compared':5209*5209,
         'files':{str(raw):sha(raw),str(local):sha(local)},
         'script_sha256':sha(Path(__file__)),'numpy':np.__version__,
         'coordinator_array_container':container,
         'new_mathematics_executed':False,'determinant_rerun':False,
         'scope':'Matrix entries only; coordinator separately binds domain and basis records.'}
(out/'validation.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,indent=2))
