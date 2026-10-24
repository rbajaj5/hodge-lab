#!/usr/bin/env python3
"""I/O-only binding to the frozen independently reconstructed A^4 minor (raw .u16.bin filename adaptation).

Reuses the A^3 binding method; supports CSV, CSV.gz, NPY, NPZ and raw uint16 without
re-evaluating any coefficient, derivative, operator or determinant.
"""
from pathlib import Path
import argparse,gzip,hashlib,io,json,os,subprocess,sys,threading,time
HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--child',action='store_true')
p.add_argument('--matrix',type=Path,required=True);p.add_argument('--inputs',type=Path,required=True)
p.add_argument('--matrix-sha256',required=True);p.add_argument('--inputs-sha256',required=True)
p.add_argument('--uncompressed-csv-sha256');p.add_argument('--matrix-key')
p.add_argument('--raw-rows',type=int);p.add_argument('--raw-columns',type=int)
args=p.parse_args()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,obj):path.write_bytes((json.dumps(obj,indent=2,ensure_ascii=False)+'\n').encode('utf-8'))
if not args.child:
    start=time.monotonic();outer_timeout=False
    command=[sys.executable,str(Path(__file__).resolve()),'--child','--matrix',str(args.matrix),'--inputs',str(args.inputs),'--matrix-sha256',args.matrix_sha256,'--inputs-sha256',args.inputs_sha256]
    if args.uncompressed_csv_sha256:command+=['--uncompressed-csv-sha256',args.uncompressed_csv_sha256]
    if args.matrix_key:command+=['--matrix-key',args.matrix_key]
    if args.raw_rows is not None:command+=['--raw-rows',str(args.raw_rows)]
    if args.raw_columns is not None:command+=['--raw-columns',str(args.raw_columns)]
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
matrix_bytes=args.matrix.read_bytes()
assert hashlib.sha256(matrix_bytes).hexdigest()==args.matrix_sha256.lower()
assert sha(args.inputs)==args.inputs_sha256.lower()
assert sha(HERE/'regenerated-minor.npy')=='8a79cf56d9f01acd1e09e14a8e6b0d7a40db6f945288fb04a0a89008be54efc3'
assert sha(HERE/'regenerated-inputs.json')=='4f74073f8b69930cb46ecf2a4f787d33876edca3c778dbdd7ed276d9b17da893'
assert sha(HERE/'A4-minor.json')=='c39d7b4ee6207b1ca65f0c545bfd7925d7fc847a1b9ea7cf987d008e9dadb36d'
encoding=args.matrix.suffix.lower();csv_hash=None;array_key=None
if args.matrix.name.lower().endswith('.u16.bin'):encoding='.u16'
if encoding in ('.csv','.gz'):
    csv_bytes=gzip.decompress(matrix_bytes) if encoding=='.gz' else matrix_bytes
    csv_hash=hashlib.sha256(csv_bytes).hexdigest()
    if args.uncompressed_csv_sha256:assert csv_hash==args.uncompressed_csv_sha256.lower()
    remote=np.loadtxt(io.BytesIO(csv_bytes),delimiter=',',dtype=np.int64)
elif encoding=='.npy':
    remote=np.load(io.BytesIO(matrix_bytes),allow_pickle=False)
elif encoding=='.npz':
    with np.load(io.BytesIO(matrix_bytes),allow_pickle=False) as archive:
        if args.matrix_key:array_key=args.matrix_key
        else:
            assert len(archive.files)==1,'Specify --matrix-key for an archive with multiple arrays'
            array_key=archive.files[0]
        remote=archive[array_key]
elif encoding=='.u16':
    assert args.raw_rows and args.raw_columns,'Raw uint16 requires explicit --raw-rows and --raw-columns'
    assert args.raw_rows>0 and args.raw_columns>0
    assert len(matrix_bytes)==2*args.raw_rows*args.raw_columns
    remote=np.frombuffer(matrix_bytes,dtype='<u2').reshape(args.raw_rows,args.raw_columns)
else:raise ValueError('Supported formats: CSV, CSV.gz, NPY, NPZ, raw .u16')
assert np.issubdtype(remote.dtype,np.integer)
delivered=json.loads(args.inputs.read_bytes().decode('utf-8'))
local=json.loads((HERE/'regenerated-inputs.json').read_bytes().decode('utf-8'))
assert delivered['prime']==local['prime']==65521
assert delivered['seed']==local['seed']==2026102469
assert delivered['basis']==local['basis'] and len(local['basis'])==3102
assert len(delivered['samples'])==1580 and len(local['samples'])==1552
assert delivered['samples'][:1552]==local['samples']
assert local['excluded_points']==[]
assert delivered['matrix_shape']==[3160,3103] and local['matrix_shape']==[3103,3103]
minor=np.load(HERE/'regenerated-minor.npy',allow_pickle=False)
assert remote.shape in ((3160,3103),(3103,3103)) and minor.shape==(3103,3103)
assert minor.dtype==np.dtype('<u2')
assert np.array_equal(remote[:3103,:],minor)
print('PASS: delivered first3103 rows equal all9628609 frozen regenerated entries',flush=True)
print('PASS: all3102 basis labels and first1552 sample/domain records match exactly',flush=True)
report={
 'status':'PASS_IO_BINDING_ONLY','script_sha256':sha(Path(__file__)),
 'delivered_matrix_file_sha256':hashlib.sha256(matrix_bytes).hexdigest(),
 'delivered_matrix_encoding':encoding,'npz_array_key':array_key,
 'raw_storage':{'order':'row-major','dtype':'little-endian uint16','rows':args.raw_rows,'columns':args.raw_columns} if encoding=='.u16' else None,
 'delivered_uncompressed_csv_sha256':csv_hash,'delivered_inputs_sha256':sha(args.inputs),
 'frozen_minor_sha256':sha(HERE/'regenerated-minor.npy'),'frozen_inputs_sha256':sha(HERE/'regenerated-inputs.json'),
 'frozen_mathematical_report_sha256':sha(HERE/'A4-minor.json'),
 'prime':65521,'seed':2026102469,'basis_entries_compared':3102,'sample_domain_records_compared':1552,
 'matrix_entries_compared':9628609,'author_declared_full_matrix_shape':[3160,3103],
 'delivered_array_shape':list(remote.shape),'compared_minor_shape':[3103,3103],
 'author_rows_not_compared':57,'sample_domain_records_not_compared':28,
 'source_binding':'Frozen independent report pins connection SHA a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d. This binding does not evaluate the source again.',
 'scope':'Exact I/O equality and cryptographic binding only. No differentiation, matrix reconstruction, elimination, determinant, or search rerun. Locally checked3103 rows; no claim to independently reconstruct the other57 author rows.',
 'python':sys.version,'numpy':np.__version__}
save(HERE/'packet-binding.json',report)
watch.cancel()
