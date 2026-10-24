#!/usr/bin/env python3
"""I/O-only binding to the frozen independently reconstructed A^8 minor (raw .u16.bin filename adaptation).

Reuses the A^7 binding method; supports CSV, CSV.gz, NPY, NPZ and raw uint16 without
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
assert sha(HERE/'regenerated-minor.npy')=='1c41301ad2a113d530bbd3b13c4ee004ac22fb55219b8bab99ae9850d46ac9e6'
assert sha(HERE/'regenerated-inputs.json')=='bfde47073da9b8c079222adfad49a989c493f73ffc1d2f28d4eb85542dcaafd0'
assert sha(HERE/'A8-minor.json')=='a9cbcfece3df8b8cd9c1813d685dbb0ad193838292b4212029f6c9c149fb92ff'
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
assert delivered['seed']==local['seed']==2026102508
assert delivered['basis']==local['basis'] and len(local['basis'])==5910
assert len(delivered['samples'])==3000 and len(local['samples'])==2956
assert delivered['samples'][:2956]==local['samples']
assert local['excluded_points']==[]
assert delivered['matrix_shape']==[6000,5911] and local['matrix_shape']==[5911,5911]
minor=np.load(HERE/'regenerated-minor.npy',allow_pickle=False)
assert remote.shape in ((6000,5911),(5911,5911)) and minor.shape==(5911,5911)
assert minor.dtype==np.dtype('<u2')
assert np.array_equal(remote[:5911,:],minor)
print('PASS: delivered first5911 rows equal all34939921 frozen regenerated entries',flush=True)
print('PASS: all5910 basis labels and first2956 sample/domain records match exactly',flush=True)
report={
 'status':'PASS_IO_BINDING_ONLY','script_sha256':sha(Path(__file__)),
 'delivered_matrix_file_sha256':hashlib.sha256(matrix_bytes).hexdigest(),
 'delivered_matrix_encoding':encoding,'npz_array_key':array_key,
 'raw_storage':{'order':'row-major','dtype':'little-endian uint16','rows':args.raw_rows,'columns':args.raw_columns} if encoding=='.u16' else None,
 'delivered_uncompressed_csv_sha256':csv_hash,'delivered_inputs_sha256':sha(args.inputs),
 'frozen_minor_sha256':sha(HERE/'regenerated-minor.npy'),'frozen_inputs_sha256':sha(HERE/'regenerated-inputs.json'),
 'frozen_mathematical_report_sha256':sha(HERE/'A8-minor.json'),
 'prime':65521,'seed':2026102508,'basis_entries_compared':5910,'sample_domain_records_compared':2956,
 'matrix_entries_compared':34939921,'author_declared_full_matrix_shape':[6000,5911],
 'delivered_array_shape':list(remote.shape),'compared_minor_shape':[5911,5911],
 'author_rows_not_compared':89,'sample_domain_records_not_compared':44,
 'source_binding':'Frozen independent report pins connection SHA a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d. This binding does not evaluate the source again.',
 'scope':'Exact I/O equality and cryptographic binding only. No differentiation, matrix reconstruction, elimination, determinant, or search rerun. Locally checked5911 rows; no claim to independently reconstruct the other89 author rows.',
 'python':sys.version,'numpy':np.__version__}
save(HERE/'packet-binding.json',report)
watch.cancel()
