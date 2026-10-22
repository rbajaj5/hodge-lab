"""Authenticate fqlx's pinned packet bytes without executing its checkers.

Download bundle.json and payload-001.b64 from the pinned gist revision in
notes/skew-compact-architecture.md. Run with --packet-dir DIRECTORY.
This is an integrity check, not a mathematical replay or proof certificate.
"""
from pathlib import Path,PurePosixPath
import argparse,base64,datetime,hashlib,io,json,sys,tarfile,time

ARCHIVE='d067112d6a859e2fb83d8139eb4de9fe410982ab593d1c77fee77602e72df449'
TARGET='fc7e070e4f459a521e3515c3b0d7e85fe4a557e345839f9cdb324491c289063f'
ROOT=Path(__file__).resolve().parents[1]
def require(ok,msg):
    if not ok:raise RuntimeError(msg)
def sha(raw):return hashlib.sha256(raw).hexdigest()

def inspect(packet):
    mraw=(packet/'bundle.json').read_bytes()
    require(len(mraw)<100000,'Manifest too large')
    m=json.loads(mraw.decode('utf-8'))
    require(m['format']=='sextics-paused-results-v1','Wrong packet format')
    require(len(m['chunks'])==1 and m['chunks'][0]['name']=='payload-001.b64','Unexpected chunks')
    encoded=(packet/'payload-001.b64').read_bytes()
    require(len(encoded)==128105,'Encoded size mismatch')
    blob=base64.b64decode(b''.join(encoded.split()),validate=True)
    require(len(blob)==96076 and sha(blob)==ARCHIVE,'Pinned archive mismatch')
    require(m['archive_sha256']==ARCHIVE and m['archive_bytes']==len(blob),'Manifest archive mismatch')
    require(len(m['files'])==40 and m['uncompressed_file_bytes']==436183,'Manifest extent mismatch')
    members={};target_raw=None
    with tarfile.open(fileobj=io.BytesIO(blob),mode='r:gz') as archive:
        for entry in archive:
            path=PurePosixPath(entry.name)
            require(entry.isfile() and not path.is_absolute() and '..' not in path.parts
                    and '\\' not in entry.name and ':' not in entry.name,'Unsafe member')
            require(entry.name not in members,'Duplicate member')
            spec=m['files'].get(entry.name)
            require(spec and entry.size==spec['bytes'] and entry.size<=1000000,'Unexpected member')
            handle=archive.extractfile(entry)
            require(handle is not None,'Unreadable member')
            raw=handle.read(entry.size+1)
            require(len(raw)==entry.size and sha(raw)==spec['sha256'],'Member mismatch: '+entry.name)
            members[entry.name]={'bytes':len(raw),'sha256':sha(raw)}
            if entry.name=='data/one-reflection-skew/instance.rec':target_raw=raw
    require(set(members)==set(m['files']),'Missing members')
    require(sum(x['bytes'] for x in members.values())==436183,'Total size mismatch')
    require(target_raw is not None and sha(target_raw)==TARGET,'Protected target mismatch')
    ours=(ROOT/'results/chi-target-source/inputs/data/one-reflection-skew/instance.rec').read_bytes().replace(b'\r\n',b'\n')
    require(ours==target_raw,'Packet target differs from notebook pin')
    return {'archive_sha256':ARCHIVE,'archive_bytes':len(blob),'files':members,
            'file_count':len(members),'total_file_bytes':436183,'protected_target_sha256':TARGET,
            'target_matches_notebook':True,'manifest_sha256':sha(mraw),
            'payload_sha256':sha(encoded),'packet_scripts_executed':0,
            'scope':'Archive/member integrity and protected-target byte match only. No mathematical replay.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packet-dir',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();began=time.monotonic()
    try:
        result=inspect(args.packet_dir)
        result.update(status='PASS',completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                      elapsed_seconds=time.monotonic()-began,python_version=sys.version,
                      checker_lf_sha256=sha(Path(__file__).read_bytes().replace(b'\r\n',b'\n')))
    except Exception as error:
        result={'status':'FAIL','error':str(error),'elapsed_seconds':time.monotonic()-began}
        raise
    finally:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2))
if __name__=='__main__':main()
