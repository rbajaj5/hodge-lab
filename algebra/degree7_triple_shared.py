"""Bounded shared-numerator chart tests for surviving X0/Y0 extensions.

All fields allowed by the denominator's stabilizer are retained. Normalize
each remaining third-character denominator coefficient in turn. A complete
contradiction cover forces that component to vanish; the archived X0/Y0
theorem then applies. Timeouts and unresolved charts remain in the packet.
"""
from concurrent.futures import ThreadPoolExecutor
from itertools import product, combinations_with_replacement
from pathlib import Path
import argparse, copy, gzip, hashlib, json, subprocess, sys, time

import degree7_triples as triples
import degree7_character_search as cert

OUT = triples.OUT / 'shared'
ANCHOR = {(0, 0, 1), (1, 2, 3)}


def read_packet():
    with gzip.open(triples.OUT / 'certificates.json.gz', 'rt', encoding='utf-8') as f:
        return json.load(f)


def selected(rows):
    return [r for r in rows if r['status'] == 'unresolved_three_characters'
            and ANCHOR <= {tuple(c) for c in r['characters']}]


def construct(model, family):
    ids = family['remaining']; nD = len(ids)
    chars = sorted({model.dc[i] for i in ids}); w = chars[0]
    assert len(chars) == 3 and ANCHOR <= set(chars)
    group = list(product(range(6), repeat=3))
    H = [g for g in group if all(sum(a*b for a, b in zip(triples.minus(c, w), g)) % 6 == 0 for c in chars)]
    ann = [c for c in group if all(sum(a*b for a, b in zip(c, g)) % 6 == 0 for g in H)]
    generated = {triples.plus(tuple(k*x % 6 for x in triples.minus(chars[1], w)),
                              tuple(l*x % 6 for x in triples.minus(chars[2], w)))
                 for k in range(6) for l in range(6)}
    assert set(ann) == generated and len(H) * len(ann) == 216
    wanted = {triples.plus(triples.plus(model.alpha, w), c) for c in ann}
    field_chars = (model.field_chars if hasattr(model, 'field_chars') else
                   [next(iter(triples.e1.field_characters(K))) for K in model.fields])
    ks = [k for k, c in enumerate(field_chars) if c in wanted]
    lookup = {k: j for j, k in enumerate(ks)}
    physical = {}
    def add(p, mon):
        for m, c in p.items(): physical.setdefault(m, {})[mon] = c
    for i, j in combinations_with_replacement(range(nD), 2):
        add(model.quadratic(ids[i], ids[j]), (i, j))
    for i, index in enumerate(ids):
        for target in sorted({triples.plus(model.dc[index], c) for c in wanted}):
            for k, p in model.corrections(index, target):
                assert k in lookup
                add(p, (i, nD + lookup[k]))
    mons = sorted(physical); equations = [physical[m] for m in mons]
    third = set(chars) - ANCHOR
    pivots = [i for i, index in enumerate(ids) if model.dc[index] in third]
    encoded = {'physical': [list(m) for m in mons], 'equations': [cert.encode(p) for p in equations]}
    digest = hashlib.sha256(json.dumps(encoded, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    desc = {'family': family['number'], 'characters': family['characters'], 'basis_indices': ids,
            'Koszul_indices': ks, 'stabilizer_order': len(H), 'annihilator': [list(c) for c in ann],
            'equation_count': len(equations), 'equations_sha256': digest, 'pivots': pivots}
    return desc, equations


def save(path, packet):
    pending = path.with_suffix(path.suffix + '.tmp')
    with gzip.open(pending, 'wt', encoding='utf-8') as f: json.dump(packet, f, separators=(',', ':'))
    pending.replace(path)


def worker(number):
    start = time.perf_counter(); model = triples.Model()
    family = read_packet()['families'][number - 1]
    assert family in selected([family])
    desc, equations = construct(model, family)
    nvars = len(desc['basis_indices']) + len(desc['Koszul_indices'])
    record = {'system': desc, 'charts': [], 'completed': False}
    path = OUT / f'family-{number}.json.gz'; save(path, record)
    print('Built', number, 'D', len(desc['basis_indices']), 'K', len(desc['Koszul_indices']),
          'equations', len(equations), 'pivots', desc['pivots'], flush=True)
    for pivot in desc['pivots']:
        chart = cert.prove_chart(equations, nvars, pivot)
        if not chart['excluded'] and chart['remaining_variables'] <= 16:
            proof = cert.ideal_certificate(equations, nvars, chart, max_degree=3)
            if proof: chart['ideal_contradiction'] = proof; chart['excluded'] = True
        cert.verify_chart(equations, nvars, chart)
        record['charts'].append(chart); record['seconds'] = time.perf_counter() - start
        save(path, record)
        print('Chart', number, pivot, 'excluded', chart['excluded'],
              'remaining', chart['remaining_variables'], flush=True)
    record['completed'] = True; save(path, record)


def run(timeout, workers):
    OUT.mkdir(parents=True, exist_ok=True)
    families = selected(read_packet()['families']); records = []
    def one(family):
        number = family['number']; start = time.perf_counter()
        cmd = [sys.executable, '-S', str(Path(__file__).resolve()), '--family', str(number)]
        try:
            completed = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            code, stdout, stderr = completed.returncode, completed.stdout, completed.stderr
            status = 'completed' if code == 0 else 'error'
        except subprocess.TimeoutExpired as error:
            code = None; status = 'timeout'
            stdout = error.stdout.decode() if isinstance(error.stdout, bytes) else (error.stdout or '')
            stderr = error.stderr.decode() if isinstance(error.stderr, bytes) else (error.stderr or '')
        item = {'family': number, 'status': status, 'returncode': code,
                'seconds': time.perf_counter() - start, 'stdout': stdout, 'stderr': stderr}
        print(number, status, round(item['seconds'], 2), 's', flush=True)
        return item
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for item in pool.map(one, families):
            records.append(item)
            (OUT / 'attempts.json').write_text(json.dumps({'timeout_seconds_per_family': timeout,
                'workers': workers, 'attempts': records}, indent=2) + '\n', encoding='utf-8')
    print('Completed bounded shared-numerator pass.', flush=True)


def verify_record(model, family, record):
    desc, equations = construct(model, family)
    assert record['system'] == desc
    pivots = [c['pivot'] for c in record['charts']]
    assert pivots == desc['pivots'][:len(pivots)]
    if record['completed']: assert pivots == desc['pivots']
    nvars = len(desc['basis_indices']) + len(desc['Koszul_indices'])
    inferences = sum(cert.verify_chart(equations, nvars, chart) for chart in record['charts'])
    covered = record['completed'] and all(c['excluded'] for c in record['charts'])
    charts = len(pivots); excluded_charts = sum(c['excluded'] for c in record['charts'])
    previous = record
    for refinement in record.get('refinements', []):
        assert not covered and not refinement.get('refinements')
        removed = {previous['system']['basis_indices'][c['pivot']]
                   for c in previous['charts'] if c['excluded']}
        assert removed
        family = {**family, 'remaining': [i for i in previous['system']['basis_indices'] if i not in removed]}
        result = verify_record(model, family, refinement)
        covered = result['covered']; charts += result['charts']
        excluded_charts += result['excluded_charts']; inferences += result['inferences']
        previous = refinement
    return {'family': family['number'], 'covered': covered, 'charts': charts,
            'excluded_charts': excluded_charts, 'inferences': inferences}


def refine(number):
    """One additional pass after globally removing already excluded charts."""
    model = triples.Model(); family = read_packet()['families'][number - 1]
    path = OUT / f'family-{number}.json.gz'
    with gzip.open(path, 'rt', encoding='utf-8') as f: record = json.load(f)
    assert record['completed'] and not record.get('refinements')
    result = verify_record(model, family, record)
    assert not result['covered'] and result['excluded_charts']
    removed = {record['system']['basis_indices'][c['pivot']] for c in record['charts'] if c['excluded']}
    family = {**family, 'remaining': [i for i in family['remaining'] if i not in removed]}
    desc, equations = construct(model, family)
    nvars = len(desc['basis_indices']) + len(desc['Koszul_indices'])
    stage = {'system': desc, 'charts': [], 'completed': False}
    record['refinements'] = [stage]; save(path, record)
    for pivot in desc['pivots']:
        chart = cert.prove_chart(equations, nvars, pivot)
        if not chart['excluded'] and chart['remaining_variables'] <= 16:
            proof = cert.ideal_certificate(equations, nvars, chart, max_degree=3)
            if proof: chart['ideal_contradiction'] = proof; chart['excluded'] = True
        cert.verify_chart(equations, nvars, chart); stage['charts'].append(chart)
        save(path, record)
        print('Refined chart', number, pivot, 'excluded', chart['excluded'], flush=True)
    stage['completed'] = True; save(path, record)


def check(independent=False):
    start = time.perf_counter()
    if independent:
        from check_degree7_triples import IndependentModel
        model = IndependentModel()
    else: model = triples.Model()
    rows = read_packet()['families']; families = selected(rows)
    attempts = json.loads((OUT / 'attempts.json').read_text())
    assert [a['family'] for a in attempts['attempts']] == [f['number'] for f in families]
    results = []; corrupted = False
    for family, attempt in zip(families, attempts['attempts']):
        path = OUT / f"family-{family['number']}.json.gz"
        if not path.exists():
            assert attempt['status'] in ('timeout', 'error')
            results.append({'family': family['number'], 'covered': False, 'charts': 0,
                            'excluded_charts': 0, 'inferences': 0})
            continue
        with gzip.open(path, 'rt', encoding='utf-8') as f: record = json.load(f)
        assert record['completed'] == (attempt['status'] == 'completed')
        result = verify_record(model, family, record); results.append(result)
        if not independent and not corrupted and result['covered']:
            broken = copy.deepcopy(record)
            item = next(i for c in broken['charts'] for s in c['stages'] for i in s['inferences'])
            item['witness']['polynomial'] = [[[], '12345']]
            try: verify_record(model, family, broken)
            except AssertionError: corrupted = True
            else: raise AssertionError('Corrupted shared-numerator chart was accepted.')
    if not independent: assert corrupted
    coverage_path = triples.OUT / 'coverage.json'
    if coverage_path.exists():
        coverage = json.loads(coverage_path.read_text())
        proved = {r['family'] for r in results if r['covered']}
        assert len(coverage['families']) == len(rows) == 152
        for original, published in zip(rows, coverage['families']):
            expected = ('excluded_by_relaxed_duals' if original['status'] == 'reduced_to_at_most_two_characters'
                        else 'excluded_by_shared_charts' if original['number'] in proved else 'unresolved')
            assert published['number'] == original['number']
            assert published['characters'] == original['characters'] and published['status'] == expected
        excluded = sum(r['status'] != 'unresolved' for r in coverage['families'])
        assert coverage['excluded_families'] == coverage['excluded_anchor_extensions'] == excluded
        assert coverage['unresolved_families'] == 152 - excluded
        remaining = sorted([list(next(iter({tuple(c) for c in r['characters']} - ANCHOR)))
                            for r in coverage['families']
                            if r['status'] == 'unresolved' and ANCHOR <= {tuple(c) for c in r['characters']}])
        assert remaining == coverage['remaining_third_characters']
    report = {'status': 'PASS', 'independent_polynomials': independent, 'families_attempted': len(results),
              'families_covered': sum(r['covered'] for r in results),
              'charts': sum(r['charts'] for r in results),
              'excluded_charts': sum(r['excluded_charts'] for r in results),
              'inferences': sum(r['inferences'] for r in results), 'families': results,
              'seconds': time.perf_counter() - start,
              'scope': 'Third character vanishes in covered families; closure requires prior X0/Y0 exclusion. The relaxed pass must also be verified.'}
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    if not __debug__: raise RuntimeError('Run without -O.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--family', type=int)
    parser.add_argument('--refine-family', type=int, help='One additional pass; original proofs are retained.')
    parser.add_argument('--timeout', type=int, default=60)
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--independent', action='store_true')
    args = parser.parse_args()
    if args.refine_family is not None: refine(args.refine_family)
    elif args.family is not None: worker(args.family)
    elif args.check: check(args.independent)
    else: run(args.timeout, args.workers)
