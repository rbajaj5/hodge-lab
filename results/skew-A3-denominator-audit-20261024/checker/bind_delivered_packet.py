#!/usr/bin/env python3
"""I/O-only binding of the frozen minor to the delivered Pro matrix.

No coefficient evaluation, differentiation, determinant, or search.
Accepts the CSV itself or its gzip encoding; hashes uncompressed CSV bytes.
"""
from pathlib import Path
import argparse,gzip,hashlib,io,json,os,subprocess,sys,threading,time
HERE=Path(__file__).resolve().parent
CSV_PIN='81a5ac8ee1b82bf1e5149e06fe0389c67c6371a058b70f59a84dbfbe256de17b'
INPUT_PIN='ffbb8171c6480c39960a60bb63e9d974fa4924999e8e536635061f1a512cec8a'
p=argparse.ArgumentParser();p.add_argument('--child',action='store_true')
p.add_argument('--result',type=Path,required=True);p.add_argument('--matrix',type=Path)
args=p.parse_args()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,obj):path.write_bytes((json.dumps(obj,indent=2,ensure_ascii=False)+'\n').encode('utf-8'))
if not args.child:
    start=time.monotonic();outer_timeout=False
    command=[sys.executable,str(Path(__file__).resolve()),'--child','--result',str(args.result)]
    if args.matrix:command+=['--matrix',str(args.matrix)]
    try:
        out=subprocess.run(command,capture_output=True,env=dict(os.environ,PYTHONUTF8='1',PYTHONIOENCODING='utf-8'),timeout=60)
        stdout,stderr,code=out.stdout,out.stderr,out.returncode
    except subprocess.TimeoutExpired as ex:
        stdout,stderr,code=ex.stdout or b'',ex.stderr or b'',124;outer_timeout=True
    for stream,data in [('stdout',stdout),('stderr',stderr)]:
        (HERE/('packet-binding.'+stream+'.log')).write_bytes(data)
    receipt={'exit_code':code,'outer_timeout':outer_timeout,'child_watchdog_exit':code==124 and not outer_timeout,
      'wall_seconds':time.monotonic()-start,'child_limit_seconds':60,'internal_watchdog_seconds':58,
      'scope':'I/O-only comparison; no mathematical computation replayed','command':command,
      'stream_encoding':'UTF-8 raw bytes','script_sha256':sha(Path(__file__)),
      'stdout_sha256':sha(HERE/'packet-binding.stdout.log'),'stderr_sha256':sha(HERE/'packet-binding.stderr.log')}
    if (HERE/'packet-binding.json').exists():receipt['report_sha256']=sha(HERE/'packet-binding.json')
    save(HERE/'packet-binding-receipt.json',receipt)
    sys.stdout.buffer.write(stdout);sys.stderr.buffer.write(stderr);print(json.dumps(receipt));sys.exit(code)

watch=threading.Timer(58,lambda:os._exit(124));watch.daemon=True;watch.start()
import numpy as np
matrix_path=args.matrix or args.result/'augmented-matrix.csv'
if not matrix_path.exists() and not args.matrix:matrix_path=args.result/'augmented-matrix.csv.gz'
inputs_path=args.result/'inputs.json'
matrix_file_bytes=matrix_path.read_bytes()
csv_bytes=gzip.decompress(matrix_file_bytes) if matrix_path.suffix=='.gz' else matrix_file_bytes
assert hashlib.sha256(csv_bytes).hexdigest()==CSV_PIN
assert sha(inputs_path)==INPUT_PIN
assert sha(HERE/'regenerated-minor.npy')=='4ac42e04498fa932c89b32a8e8b9943ae792ce6582a43b39dc5853f604e40298'
assert sha(HERE/'regenerated-inputs.json')=='5d895b4f58fd3293068e19b7b9a27a0411ea57d4d42d54d5e12c24e605a3f51a'
assert sha(HERE/'A3-minor.json')=='6c2ed5fc2d425e6c3121ffd481d21b742e335fad9c29754f7bb36f497fa57cfc'
delivered=json.loads(inputs_path.read_bytes().decode('utf-8'))
local=json.loads((HERE/'regenerated-inputs.json').read_bytes().decode('utf-8'))
assert delivered['prime']==local['prime']==32003
assert delivered['seed']==local['seed']==2026102458
assert delivered['basis']==local['basis'] and len(local['basis'])==2400
assert len(delivered['samples'])==1230 and len(local['samples'])==1201
assert delivered['samples'][:1201]==local['samples']
assert local['excluded_points']==[]
assert delivered['matrix_shape']==[2460,2401] and local['matrix_shape']==[2401,2401]
remote=np.loadtxt(io.BytesIO(csv_bytes),delimiter=',',dtype=np.int64)
minor=np.load(HERE/'regenerated-minor.npy',allow_pickle=False)
assert remote.shape==(2460,2401) and minor.shape==(2401,2401)
assert minor.dtype==np.dtype('<u2')
assert np.array_equal(remote[:2401,:],minor)
print('PASS: delivered first2401 CSV rows equal all5764801 frozen regenerated entries',flush=True)
print('PASS: all2400 basis labels and first1201 sample/domain records match exactly',flush=True)
report={
 'status':'PASS_IO_BINDING_ONLY','script_sha256':sha(Path(__file__)),
 'delivered_matrix_file_sha256':hashlib.sha256(matrix_file_bytes).hexdigest(),
 'delivered_matrix_encoding':'gzip' if matrix_path.suffix=='.gz' else 'uncompressed UTF-8 CSV',
 'delivered_uncompressed_matrix_csv_sha256':CSV_PIN,'delivered_inputs_sha256':INPUT_PIN,
 'frozen_minor_sha256':sha(HERE/'regenerated-minor.npy'),'frozen_inputs_sha256':sha(HERE/'regenerated-inputs.json'),
 'frozen_mathematical_report_sha256':sha(HERE/'A3-minor.json'),
 'prime':32003,'seed':2026102458,'basis_entries_compared':2400,'sample_domain_records_compared':1201,
 'matrix_entries_compared':5764801,'delivered_matrix_shape':[2460,2401],'compared_minor_shape':[2401,2401],
 'rows_not_compared':59,'sample_domain_records_not_compared':29,
 'source_binding':'The frozen independently generated report pins connection SHA a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d. This binding does not evaluate the source again.',
 'scope':'Exact I/O equality and cryptographic file binding only. No differentiation, matrix reconstruction, elimination, determinant, or exploratory search rerun. This local check covers2401 rows; no claim to have independently reconstructed the other59 rows.',
 'publication_note':'The frozen local regenerated-minor.npy may be omitted from the published payload to avoid duplicate matrix storage. The independent reconstruction script regenerates it; this report records its exact bytes hash.',
 'python':sys.version,'numpy':np.__version__}
save(HERE/'packet-binding.json',report)
watch.cancel()
