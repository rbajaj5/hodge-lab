#!/usr/bin/env python3
"""Bounded replay of byte-preserved Pro verifier, with passive matrix capture."""
from pathlib import Path
import argparse,hashlib,json,os,runpy,subprocess,sys,threading,time
HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--child',action='store_true')
p.add_argument('--connection',type=Path,default=Path(r'C:/Users/anaxe/Documents/Codex/hl-source-20261023/results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json'))
args=p.parse_args();target=HERE/'pro_reproduce_laurent.py'
if not args.child:
    began=time.monotonic()
    try:out=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--child','--connection',str(args.connection)],capture_output=True,text=True,encoding='utf-8',timeout=60)
    except subprocess.TimeoutExpired as ex:
        txt=lambda x:x.decode('utf-8',errors='replace') if isinstance(x,bytes) else (x or '')
        (HERE/'pro-replay-timeout.log').write_text(txt(ex.stdout)+txt(ex.stderr),encoding='utf-8');raise
    log=out.stdout+out.stderr;(HERE/'pro-replay.log').write_text(log,encoding='utf-8')
    receipt={'kind':'Replay of supplied Pro code, not an independently authored full reconstruction','exit_code':out.returncode,'wall_seconds':time.monotonic()-began,'child_limit_seconds':60,
             'wrapper_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'pro_verifier_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'connection_sha256':hashlib.sha256(args.connection.read_bytes()).hexdigest(),'log_sha256':hashlib.sha256(log.encode('utf-8')).hexdigest()}
    for f in ('augmented-minor.npy','capture.json'):
        if (HERE/f).exists():receipt[f+'_sha256']=hashlib.sha256((HERE/f).read_bytes()).hexdigest()
    (HERE/'pro-replay-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(out.stdout,end='');print(out.stderr,end='',file=sys.stderr);print(json.dumps(receipt));sys.exit(out.returncode)

import numpy as np
watch=threading.Timer(58,lambda:os._exit(124));watch.daemon=True;watch.start()
lines=target.read_text(encoding='utf-8').splitlines()
point_line=next(i+1 for i,x in enumerate(lines) if x.strip()=='rr = [[], []]')
capture_line=next(i+1 for i,x in enumerate(lines) if x.strip()=='previous, sign = 1, 1')
points=[];captured=False
target_path=str(target.resolve())
def observer(frame,event,arg):
    global captured
    if frame.f_code.co_filename!=target_path or frame.f_code.co_name!='<module>':return None
    if event=='line' and frame.f_lineno==point_line:
        points.append([int(frame.f_locals[x]) for x in ('r','v','t')])
    if event=='line' and frame.f_lineno==capture_line and not captured:
        mat=frame.f_locals['H'].copy()
        assert mat.shape==(703,703)
        np.save(HERE/'augmented-minor.npy',mat)
        meta={'points':points,'basis':frame.f_locals['basis'],'matrix_shape':list(mat.shape),'matrix_dtype':str(mat.dtype),'prime':int(frame.f_locals['p']),
              'source_sha256':hashlib.sha256(args.connection.read_bytes()).hexdigest(),'pro_verifier_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
              'capture':'Passive line observer copies H immediately after construction and before elimination; Pro source bytes unchanged.'}
        (HERE/'capture.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
        captured=True
    return observer
sys.argv=[str(target),str(args.connection)]
sys.settrace(observer)
try:runpy.run_path(target_path,run_name='__main__')
finally:sys.settrace(None)
assert captured
watch.cancel()
