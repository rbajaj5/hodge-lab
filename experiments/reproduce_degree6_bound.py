"""Replay fqlx's pinned upstream degree-six proof and opposite-pivot audit.

Use --fetch to obtain the publicly linked source revision. Every file is
verified against the committed hash manifest before the source is executed.
The upstream source and intermediate outputs stay in the chosen work folder;
the public result records attribution, the exact revision, and checked counts.
"""
from pathlib import Path
import argparse, datetime, hashlib, json, subprocess, sys, urllib.request

ROOT=Path(__file__).resolve().parent.parent
MANIFEST=ROOT/'references/fqlx-degree6.json'


def run(source_dir,fetch=False):
    manifest=json.loads(MANIFEST.read_text());source_dir=source_dir.resolve()
    source_dir.mkdir(parents=True,exist_ok=True)
    if fetch:
        request=urllib.request.Request(manifest['api_url'],headers={'User-Agent':'hodge-lab-reproduction'})
        with urllib.request.urlopen(request,timeout=60) as response:remote=json.load(response)
        for filename,digest in manifest['files'].items():
            assert Path(filename).name==filename
            entry=remote['files'][filename];assert not entry.get('truncated')
            raw=entry['content'].encode('utf-8')
            assert hashlib.sha256(raw).hexdigest()==digest
            (source_dir/filename).write_bytes(raw)
    for filename,digest in manifest['files'].items():
        assert Path(filename).name==filename
        assert hashlib.sha256((source_dir/filename).read_bytes()).hexdigest()==digest,filename
    output=source_dir/'reproduced';output.mkdir(exist_ok=True)
    commands=[['reconstruct_global_degree6.py','--output-dir','reproduced'],
              ['reduce_e2_opposite.py','reproduced/degree6-global-checkpoint.json','--output','reproduced/opposite-e2.json'],
              ['audit_full_e2.py','reproduced/opposite-e2.json']]
    for index,command in enumerate(commands):
        print('Running pinned upstream check:',command[0],flush=True)
        with (source_dir/f'replay-{index}.log').open('w',encoding='utf-8') as log:
            subprocess.run([sys.executable,*command],cwd=source_dir,stdout=log,stderr=subprocess.STDOUT,check=True)
    final=json.loads((output/'degree6-final-verification.json').read_text())
    opposite=json.loads((output/'independent-e2-audit.json').read_text())
    assert final['denominatorLowerBound']==7 and not final['actualE2']['remainingRaw']
    all_forced=set(final['actualE2']['forcedRaw'])
    assert {r['original_parameter'] for r in opposite if r['excluded']}==all_forced
    report={'attribution':'fqlx, upstream degree-six exclusion; reproduced here, not a new bound.',
        'discussion':manifest['discussion'],'gist_revision':manifest['gist_revision'],
        'reproduced_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'input_files_sha256_verified':len(manifest['files']),'commands':commands,
        'minimum_possible_denominator_degree':7,'all_final_denominator_coordinates_excluded':sorted(all_forced),
        'final_exclusion_rounds':[r['forcedRaw'] for r in final['actualE2']['stages']],
        'opposite_physical_and_parameter_pivots_reproduced':True,
        'scope':'The exact pinned holdout with complex coefficients and an unrestricted quotient; no denominator degree at most six. This upstream result is not a Lean theorem or an unrestricted nonexistence proof.'}
    destination=ROOT/'results/upstream-degree6';destination.mkdir(parents=True,exist_ok=True)
    (destination/'replay.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2),flush=True)


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O: upstream assertions are part of verification.')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir',type=Path,default=ROOT/'work/upstream-degree6')
    parser.add_argument('--fetch',action='store_true');args=parser.parse_args()
    run(args.source_dir,args.fetch)
