#!/usr/bin/env python3
"""Audit support reuse; the infinite-power conclusion uses a cited theorem.

This script does not formalize that theorem. It replays the fixed-S obstruction,
checks all saved product polynomials and records exact support-containment
certificates using nonnegative exponent differences. Old attempts are read only.
"""
import argparse
import json
from pathlib import Path
import cyclic_fano_branch_products as P
import check_cyclic_fano_guided_denominators as independent

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/cyclic-fano-support-audit'
FACTORS = ['T', 'C', 'S', 'R', 'J']
PIN = 'd96911d725077e66a8f10848908be01a643b1714'
THEOREM = f'https://github.com/hodge-computer/sextics/blob/{PIN}/docs/01-certificates.md#prescribed-support-and-pole-multiplicity'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def binding(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'lf_sha256': P.poly.sha(path)}


def formal_support(exponents):
    return [name for name, value in zip(FACTORS, exponents) if value]


def containment(a, b):
    """If support(a) <= support(b), certify product(a) divides product(b)^k."""
    assert len(a) == len(b) == 5
    assert all(type(n) is int and n >= 0 for n in a + b)
    assert any(a) and any(b)
    assert all(not n or m for n, m in zip(a, b)), 'New support component'
    k = max((n + m - 1) // m for n, m in zip(a, b) if n)
    cofactor = [k * m - n for n, m in zip(a, b)]
    assert min(cofactor) >= 0
    assert [n + h for n, h in zip(a, cofactor)] == [k * m for m in b]
    return {'power_of_cover': k, 'cofactor_exponents': cofactor}


def calculate():
    source = P.base.SOURCE / 'source/instance.rec'
    assert '\nq: 1\n' in ('\n' + source.read_text(encoding='utf-8').replace('\r\n', '\n'))
    F, A, G, beta = independent.target()
    expected = independent.candidate_data(G)
    spath = independent.OUT / 'Y0-leading-branch-sextic.json'
    # A fresh independent replay, not just a previously stored PASS label.
    sreplay = independent.check_packet(spath, expected, F, G, beta)
    # The producer and independent candidate generators are compared via packet checks.
    guided = list(P.old.candidates())
    s_candidate = next(c for c in guided if c['id'] == 'Y0-leading-branch-sextic')
    assert independent.decode(s_candidate['quotient_denominator']) == expected['Y0-leading-branch-sextic'][1]
    S_primary = P.old.decode(s_candidate['quotient_denominator'])
    candidates = list(P.candidates())
    attempt = read(P.OUT / 'attempt-S2.json')
    assert attempt['status'] == 'timeout'
    s2 = next(c for c in candidates if c['id'] == 'S2')
    assert attempt['candidate'] == s2
    assert P.old.decode(s2['denominator']) == P.poly.mul(S_primary, S_primary)
    assert independent.decode(s2['denominator']) == independent.mul(independent.decode(s_candidate['quotient_denominator']), independent.decode(s_candidate['quotient_denominator']))
    records = []
    for candidate in candidates:
        name = candidate['id']
        exponents = candidate['exponents']
        if name == 'S2':
            status = 'timeout'
            stage = None
            witness = spath
            cover = [0, 0, 1, 0, 0]
            cover_name = 'S'
        else:
            path = P.OUT / (name + '.json')
            packet = read(path)
            assert packet['candidate'] == candidate and packet['status'] == 'excluded'
            status = 'excluded'
            stage = packet['obstruction_stage'] if 'obstruction_stage' in packet else packet.get('stage')
            if stage is None:
                stage = packet['stages'][-1]['stage']
            witness = path
            cover = exponents
            cover_name = name
        records.append({
            'id': name, 'degree': candidate['degree'], 'factor_order': FACTORS,
            'exponents': exponents, 'formal_factor_set': formal_support(exponents),
            'direct_status': status, 'direct_stage': stage,
            'current_status': 'excluded_using_prescribed_support_theorem',
            'cover_id': cover_name, 'cover_exponents': cover,
            'support_containment': containment(exponents, cover),
            'same_support_reverse': containment(cover, exponents),
            'prior_obstruction': binding(witness),
            'conclusion': 'No certificate with poles contained in this support; every positive power is excluded using the cited q=1 theorem.'
        })
    assert len(records) == 26
    assert sum(r['direct_status'] == 'excluded' for r in records) == 25
    controls = 0
    for a, b in [([1,1,0,0,0], [1,0,0,0,0]), ([0,1,0,0,1], [0,1,0,0,0])]:
        try:
            containment(a, b)
        except AssertionError:
            controls += 1
        else:
            raise AssertionError('New support was incorrectly pruned')
    return {
        'schema': 'cyclic-fano-support-audit-v1', 'status': 'PASS',
        'instance': 'cyclic-triple-fano', 'q': 1, 'source_commit': PIN,
        'source': binding(source), 'producer': binding(Path(__file__)),
        'dependencies': [binding(Path(module.__file__)) for module in
                         (P, P.old, P.base, P.poly, independent, independent.I)],
        'theorem_url': THEOREM,
        'theorem_dependency': 'Mathematical application of the repository prescribed-support theorem; not a machine-checked proof of that theorem.',
        'discussion_motivation': 'https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18989248',
        'direct_exclusions_before': 25, 'historical_timeouts': 1,
        'covered_candidates_after_theorem': 26,
        'formal_factor_set_count': len({tuple(r['formal_factor_set']) for r in records}),
        'records': records, 'S_fresh_independent_replay': sreplay,
        'S2_history': {**binding(P.OUT / 'attempt-S2.json'), 'status': 'timeout',
                       'seconds': attempt['elapsed_seconds'], 'time_limit_seconds': attempt['time_limit_seconds'],
                       'new_degree12_dual_generated': False},
        'controls_rejecting_new_support': controls,
        'constant_polar_family_extension': {
            'proof_packet': binding(ROOT / 'results/cyclic-fano-polar-family/packet.json'),
            'conclusion': 'For every fixed nonzero constant v, all positive powers of E_v are excluded by that family proof and the same q=1 theorem.'
        },
        'limits': [
            'Formal factor labels are not irreducible factors; distinct label sets need not define distinct geometric supports.',
            'Separate failures on two supports do not exclude their union.',
            'No new degree12 dual, successful timed-out search, certificate, Lean proof, or solve is claimed.',
            'The other 25 stored exclusions are bound and their candidate polynomials checked; their full dual checks are recorded in the unchanged prior validation packets.'
        ]
    }


def main():
    assert __debug__, 'Run without -O'
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['run', 'verify'])
    args = parser.parse_args()
    result = calculate()
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / 'packet.json'
    if args.command == 'run':
        path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    else:
        assert read(path) == result
    print(json.dumps({'status': 'PASS', 'candidates': 26, 'historical_direct_exclusions': 25,
                      'new_theorem_covered_timeout': 'S2', 'S_columns_replayed': result['S_fresh_independent_replay']['matrix_shape'][1]}))


if __name__ == '__main__':
    main()
