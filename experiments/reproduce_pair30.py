"""Fetch and replay fqlx's immutable, attributed family-30 proof packet."""
from pathlib import Path
import argparse, hashlib, json, os, shutil, subprocess, sys, tempfile, time, urllib.request

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'references/fqlx-pair30.json'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch',action='store_true')
    parser.add_argument('--directory',type=Path,default=ROOT/'work/upstream-pair30')
    args=parser.parse_args();manifest=json.loads(MANIFEST.read_text());directory=args.directory.resolve()
    if args.fetch:
        request=urllib.request.Request('https://api.github.com/gists/'+manifest['gist']+'/'+manifest['revision'],
            headers={'User-Agent':'Hodge-Lab-reproduction'})
        data=json.load(urllib.request.urlopen(request,timeout=60))
        directory.mkdir(parents=True,exist_ok=True)
        for name,digest in manifest['sha256'].items():
            assert Path(name).name==name
            item=data['files'][name]
            raw=(urllib.request.urlopen(item['raw_url'],timeout=60).read() if item.get('truncated')
                 else item['content'].encode('utf-8'))
            assert hashlib.sha256(raw).hexdigest()==digest,name
            (directory/name).write_bytes(raw)
    for name,digest in manifest['sha256'].items():
        assert hashlib.sha256((directory/name).read_bytes()).hexdigest()==digest,name
    out=ROOT/'results/upstream-pair30';out.mkdir(parents=True,exist_ok=True)
    records=[];env=dict(os.environ,PYTHONUTF8='1')
    # The independent audit rewrites a JSON report. Run on a disposable copy
    # so that downloaded source/artifact hashes remain stable for later replay.
    with tempfile.TemporaryDirectory(prefix='hodge-pair30-') as temporary:
        for name in manifest['sha256']:shutil.copyfile(directory/name,Path(temporary)/name)
        for script in ['verify_pair30.py','audit_pair30_independent.py']:
            start=time.perf_counter()
            result=subprocess.run([sys.executable,'-S',script],cwd=temporary,env=env,
                capture_output=True,text=True,encoding='utf-8',timeout=120)
            log=result.stdout+result.stderr
            (out/(Path(script).stem+'.log')).write_text(log,encoding='utf-8')
            records.append({'script':script,'exit_code':result.returncode,'seconds':time.perf_counter()-start})
            print(log,flush=True)
            if result.returncode:raise RuntimeError('Upstream replay failed: '+script)
    report={'author':manifest['author'],'revision':manifest['revision'],'source':manifest['url'],
        'source_files_hash_checked':len(manifest['sha256']),'runs':records,'status':'PASS',
        'scope':'Reproduction of fqlx\'s existing pair30 exclusion; no claim of original discovery or Lean verification.'}
    (out/'replay.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    main()
