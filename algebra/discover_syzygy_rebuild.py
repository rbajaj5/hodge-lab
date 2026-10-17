"""Reproduce bounded syzygy discovery without overwriting published packets.

Optional python-flint accelerates discovery; exact checks do not require it.
The supervisor retains the last completed multiplier checkpoint on timeout.
"""
import argparse, gzip, json, subprocess, sys, time
from pathlib import Path
from itertools import combinations_with_replacement
import degree7_syzygies as s
import degree7_syzygy_rebuild as rebuild

c = s.cert


def seed(model, family, pivot):
    desc, rows, _ = s.construct(model, family, pivot)
    nD = len(desc['basis_indices']); nv = nD + len(desc['Koszul_indices'])
    if family == 115:
        old = rebuild.read(s.OUT / f'chart-115-{pivot}.json.gz')
        s.verify(model, old)
        maps = rebuild.initial_maps(old)
    else:
        old = rebuild.read(s.shared.OUT / f'family-{family}.json.gz')
        proof = next(p for p in old['charts'] if p['pivot'] == pivot)
        c.verify_chart(rows, nv, proof)
        maps = s.chart_maps(nv, pivot, proof)
        assert all(all(j < nD for m in maps[i] for j in m) for i in range(nD))
    return desc, [c.substitute(p, maps) for p in rows], maps


def worker(args):
    import syzygy_accelerated as fast
    start = time.perf_counter()
    desc, rows, maps = seed(s.triples.Model(), args.family, args.pivot)
    nD = len(desc['basis_indices'])
    variables = sorted({i for p in rows for m in p for i in m if i < nD})
    multipliers = [m for d in range(args.degree + 1) for m in combinations_with_replacement(variables, d)]
    def checkpoint(relations, rank, count):
        packet = {'family': args.family, 'pivot': args.pivot, 'system': desc,
                  'maps': rebuild.encode_maps(maps), 'variables': variables,
                  'relations': relations, 'expanded_rank': rank,
                  'multiplier_degree_bound': args.degree,
                  'multipliers_processed': [list(m) for m in multipliers[:count]],
                  'complete_multiplier_space': count == len(multipliers),
                  'discovery_seconds': time.perf_counter() - start}
        s.shared.save(args.output, packet)
        return packet
    relations, rank = fast.eliminate(rows, nD, multipliers, checkpoint=checkpoint)
    packet = checkpoint(relations, rank, len(multipliers))
    packet['baseline'], packet['baseline_rank'] = s.necessary_relations(rows, nD, [()])
    if args.degree == 1:
        _, packet['selected_new'], _ = s.select_new(packet['baseline'], relations, variables)
    else:
        # Retain all quadratic-multiplier consequences; no misleading
        # independence comparison with just affine multiples of the baseline.
        packet['selected_new'] = list(range(len(relations)))
    c.reduce_span = fast.reduce_span
    packet['continuation'] = s.continue_search(rows, packet, max_degree=args.power_degree)
    s.verify_continuation(rows, packet)
    s.shared.save(args.output, packet)
    print(json.dumps({'excluded': packet['continuation']['excluded'],
                      'seconds': time.perf_counter() - start}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--family', type=int, choices=[16, 115, 137], required=True)
    parser.add_argument('--pivot', type=int, required=True)
    parser.add_argument('--degree', type=int, default=1, choices=[1, 2])
    parser.add_argument('--power-degree', type=int, default=4, choices=[3, 4, 5])
    parser.add_argument('--timeout', type=int, default=180)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        worker(args)
    else:
        if args.output.exists():
            parser.error('Choose a fresh output path; published packets are not overwritten.')
        args.output.parent.mkdir(parents=True, exist_ok=True)
        log = args.output.with_suffix('.log'); start = time.perf_counter()
        with log.open('w', encoding='utf-8') as stream:
            try:
                result = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                    *sys.argv[1:], '--worker'], stdout=stream, stderr=subprocess.STDOUT,
                    timeout=args.timeout)
                status = 'completed' if result.returncode == 0 else 'error'
                code = result.returncode
            except subprocess.TimeoutExpired:
                status = 'timeout'; code = None
        attempt = {'family': args.family, 'pivot': args.pivot, 'status': status,
                   'returncode': code, 'timeout_seconds': args.timeout,
                   'elapsed_seconds': time.perf_counter() - start,
                   'checkpoint_exists': args.output.exists(),
                   'log': log.read_text(encoding='utf-8')}
        args.output.with_suffix('.attempt.json').write_text(json.dumps(attempt, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(attempt, indent=2))
