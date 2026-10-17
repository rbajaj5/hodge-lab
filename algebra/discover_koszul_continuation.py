"""Bounded discovery for the archived rank/Koszul continuation.

Uses python-flint; exact replay in degree7_koszul_continuation.py needs only
the standard library. Choose a fresh output path; existing files are refused.
The supervisor kills its worker at --timeout and retains completed checkpoints.
"""
from pathlib import Path
import argparse
import json
import subprocess
import sys
import time
import degree7_koszul_continuation as k

rank, s, c = k.rank, k.s, k.c


def prepare(model, family, pivot, stage):
    if stage == 'rank-leaf':
        desc, rows = k.leaf_equations(model, family, pivot)
        return rows, {'family':family, 'pivot':pivot, 'system':desc}
    desc, rows, _ = rank.seed(model, family, pivot)
    linear = json.loads((k.OUT/'global-linear-identities.json').read_text())[0 if family == 16 else 1]
    rank.check_global(model, linear)
    changes = rank.zero_map(c.decode(linear['linear']),18)
    data = {'family':family, 'pivot':pivot, 'system':desc}
    if family == 137:
        k.verify_global137(model)
        changes.update({1:{}, 9:{}})
    if stage == 'refined':
        prior = 11 if family == 16 else 13
        assert pivot != prior
        packet = rank.rb.read(k.OUT/f'koszul-{family}-{prior}.json.gz')
        if family == 16:
            k.verify_first(model, packet)
        else:
            assert k.verify137(model,packet,set())[0]
        changes[prior] = {}
        data['dependency_closed_chart'] = prior
    data['initial_changes'] = rank.rb.encode_maps(changes)
    return [c.substitute(p,changes) for p in rows], data


def worker(args):
    import syzygy_accelerated as fast
    start = time.perf_counter()
    rows, data = prepare(s.triples.Model(),args.family,args.pivot,args.stage)
    c.reduce_span = fast.reduce_span
    if args.stage != 'rank-leaf':
        nv = 18 + len(data['system']['Koszul_indices'])
        proof = c.prove_chart(rows,nv,args.pivot)
        c.verify_chart(rows,nv,proof)
        data['affine_chart'] = proof
        maps = s.chart_maps(nv,args.pivot,proof)
        rows = [c.substitute(p,maps) for p in rows]
    data['rows'] = [c.encode(p) for p in rows]
    s.shared.save(args.output,data)
    if data.get('affine_chart',{}).get('excluded'):
        print('Excluded by checked physical affine closure.',flush=True)
        return
    variables = sorted({i for p in rows for m in p for i in m if i < 18})
    data['variables'] = variables
    multipliers = [()] + [(i,) for i in variables]

    def checkpoint(relations, expanded_rank, count):
        data.update(relations=relations, expanded_rank=expanded_rank,
                    multipliers_processed=count,
                    complete_multiplier_space=count==len(multipliers),
                    seconds=time.perf_counter()-start)
        s.shared.save(args.output,data)

    relations, expanded_rank = fast.eliminate(rows,18,multipliers,checkpoint=checkpoint)
    checkpoint(relations,expanded_rank,len(multipliers))
    data['baseline'], _ = fast.eliminate(rows,18,[()],progress=False)
    _, data['selected_new'], _ = s.select_new(data['baseline'],relations,variables)
    s.shared.save(args.output,data)
    necessary = data['baseline'] + [relations[j] for j in data['selected_new']]
    proof = c.prove_chart([c.decode(p['polynomial']) for p in necessary],18,args.pivot)
    if proof['excluded']:
        data['denominator_contradiction'] = proof
    else:
        data['continuation'] = s.continue_search(rows,data,max_degree=args.max_degree)
    excluded, counts = k.verify_relations(rows,data)
    s.shared.save(args.output,data)
    print(json.dumps({'excluded':excluded, **counts}),flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--family',type=int,choices=[16,137],required=True)
    parser.add_argument('--pivot',type=int,required=True)
    parser.add_argument('--stage',choices=['rank-leaf','reduced','refined'],required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--timeout',type=float,default=150)
    parser.add_argument('--max-degree',type=int,choices=[3,4,5],default=4)
    parser.add_argument('--worker',action='store_true',help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.timeout <= 0:parser.error('--timeout must be positive')
    if args.worker:
        worker(args)
        return
    log = args.output.with_suffix('.log')
    report = args.output.with_suffix('.attempt.json')
    if any(p.exists() for p in [args.output,log,report]):
        parser.error('Choose a fresh output path; existing artifacts are not overwritten.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    start = time.perf_counter()
    with log.open('w',encoding='utf-8') as stream:
        try:
            proc = subprocess.run([sys.executable,__file__,*sys.argv[1:],'--worker'],
                                  stdout=stream,stderr=subprocess.STDOUT,timeout=args.timeout)
            status = 'completed' if proc.returncode == 0 else 'error'
            code = proc.returncode
        except subprocess.TimeoutExpired:
            status, code = 'timeout', None
    result = {'family':args.family,'pivot':args.pivot,'stage':args.stage,
              'status':status,'returncode':code,'timeout_seconds':args.timeout,
              'seconds':time.perf_counter()-start,'log':log.read_text(encoding='utf-8')}
    report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
    if status == 'error':raise SystemExit(code)


if __name__ == '__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    main()
