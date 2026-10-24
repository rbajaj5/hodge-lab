#!/usr/bin/env python3
"""I/O-only binding of the frozen regenerated minor to the delivered Pro CSV.

No coefficient evaluation, differentiation, elimination, determinant, or search.
"""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,threading,time
HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--child',action='store_true')
p.add_argument('--result',type=Path,required=True)
args=p.parse_args()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,obj):path.write_bytes((json.dumps(obj,indent=2,ensure_ascii=False)+'\n').encode('utf-8'))
if not args.child:
    start=time.monotonic();outer_timeout=False
    try:
        out=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--child','--result',str(args.result)],capture_output=True,env=dict(os.environ,PYTHONUTF8='1',PYTHONIOENCODING='utf-8'),timeout=60)
        stdout,stderr,code=out.stdout,out.stderr,out.returncode
    except subprocess.TimeoutExpired as ex:
        stdout,stderr,code=ex.stdout or b'',ex.stderr or b'',124;outer_timeout=True
    for stream,data in [('stdout',stdout),('stderr',stderr)]:
        (HERE/('packet-binding.'+stream+'.log')).write_bytes(data)
    receipt={'exit_code':code,'outer_timeout':outer_timeout,'child_watchdog_exit':code==124,
      'wall_seconds':time.monotonic()-start,'child_limit_seconds':60,'internal_watchdog_seconds':58,
      'scope':'I/O-only comparison; no mathematical computation replayed',
      'stream_encoding':'UTF-8 raw bytes','script_sha256':sha(Path(__file__)),
      'stdout_sha256':sha(HERE/'packet-binding.stdout.log'),'stderr_sha256':sha(HERE/'packet-binding.stderr.log')}
    if (HERE/'packet-binding.json').exists():receipt['report_sha256']=sha(HERE/'packet-binding.json')
    save(HERE/'packet-binding-receipt.json',receipt)
    sys.stdout.buffer.write(stdout);sys.stderr.buffer.write(stderr);print(json.dumps(receipt));sys.exit(code)

import numpy as np
watch=threading.Timer(58,lambda:os._exit(124));watch.daemon=True;watch.start()
matrix_path=args.result/'augmented-matrix.csv';inputs_path=args.result/'inputs.json'
assert sha(matrix_path)=='28ec91d22fb0008e1519f28864a0a50a706dbc74dbcd8411c9bc4dca6805a6e7'
assert sha(inputs_path)=='21d60f4a9cdd180722f6b1aca76b55b813407c195c9af1144049cfdc222280c5'
assert sha(HERE/'regenerated-minor.npy')=='7df9059c44de2ba802470f7388bad9d873783df942e4eda1a6d3d47e2bda7038'
assert sha(HERE/'regenerated-inputs.json')=='4fab5fc1d5aa57f120d3a772da05423dc93c094deefaa89c22c90f48e51002af'
assert sha(HERE/'A2-minor.json')=='8794831226bc8be8134c1cf1faa67d8a38b5cf976266700fe830bcb3c858e7a9'
delivered=json.loads(inputs_path.read_bytes().decode('utf-8'))
local=json.loads((HERE/'regenerated-inputs.json').read_bytes().decode('utf-8'))
assert delivered['prime']==local['prime']==32003
assert delivered['seed']==local['seed']==2026102432
assert delivered['basis']==local['basis'] and len(local['basis'])==1698
assert len(delivered['samples'])==879 and len(local['samples'])==850
assert delivered['samples'][:850]==local['samples']
assert delivered['excluded_points']==local['excluded_points']==[]
assert delivered['matrix_shape']==[1758,1699] and local['matrix_shape']==[1699,1699]
remote=np.loadtxt(matrix_path,delimiter=',',dtype=np.int64)
minor=np.load(HERE/'regenerated-minor.npy',allow_pickle=False)
assert remote.shape==(1758,1699) and minor.shape==(1699,1699)
assert minor.dtype==np.dtype('<u2')
assert np.array_equal(remote[:1699,:],minor)
print('PASS: delivered first1699 CSV rows equal all2886601 frozen regenerated entries',flush=True)
print('PASS: all1698 basis labels and first850 sample/domain records match exactly',flush=True)
report={
 'status':'PASS_IO_BINDING_ONLY','script_sha256':sha(Path(__file__)),
 'delivered_matrix_csv_sha256':sha(matrix_path),'delivered_inputs_sha256':sha(inputs_path),
 'frozen_minor_sha256':sha(HERE/'regenerated-minor.npy'),'frozen_inputs_sha256':sha(HERE/'regenerated-inputs.json'),
 'frozen_mathematical_report_sha256':sha(HERE/'A2-minor.json'),
 'prime':32003,'seed':2026102432,'basis_entries_compared':1698,'sample_domain_records_compared':850,
 'matrix_entries_compared':2886601,'delivered_matrix_shape':[1758,1699],'compared_minor_shape':[1699,1699],
 'rows_not_compared':59,'sample_domain_records_not_compared':29,
 'source_binding':'The frozen independently generated report pins connection SHA a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d. This binding does not evaluate the source again.',
 'scope':'Exact I/O equality and cryptographic file binding only. No differentiation, matrix reconstruction, Gaussian elimination, determinant, or exploratory search rerun. This local check covers1699 rows; Pro separately reports all1758 rows.',
 'python':sys.version,'numpy':np.__version__}
save(HERE/'packet-binding.json',report)
watch.cancel()
