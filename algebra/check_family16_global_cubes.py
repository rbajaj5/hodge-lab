"""Small follow-up after the fifth-post packet: two global family-16 cubes.

No family exclusion. These identities apply to the unnormalized family after
the earlier first-pass reduction, rather than only the a13=1 chart.
"""
from pathlib import Path
import copy, json
import degree7_syzygies as s

PATH = s.triples.ROOT / 'results/degree7-syzygy-rebuild/family16-global-cubes.json'


def verify(rows, claims):
    products = 0
    assert [claim['coordinate'] for claim in claims] == [1, 9]
    for claim in claims:
        actual = {}; assert claim['power'] == 3
        for j, mon, coefficient in claim['products']:
            assert 0 <= j < len(rows) and len(mon) == 1 and 0 <= mon[0] < 18
            actual = s.triples.base.padd(actual, s.cert.product(rows[j], {tuple(mon): s.triples.Q(coefficient)}))
            products += 1
        assert actual == {(claim['coordinate'],) * 3: s.triples.Q(1)}
    return products


def check():
    from check_degree7_triples import IndependentModel
    packet = json.loads(PATH.read_text(encoding='utf-8'))
    assert packet['family'] == 16
    checks = []
    for model in (s.triples.Model(), IndependentModel()):
        family = s.shared.read_packet()['families'][15]
        inherited = s.triples.verify_family(model, family)
        desc, rows = s.shared.construct(model, family)
        assert desc == packet['system'] and len(desc['basis_indices']) == 18
        count = verify(rows, packet['claims'])
        broken = copy.deepcopy(packet['claims'])
        broken[0]['products'][0][2] = str(s.triples.Q(broken[0]['products'][0][2]) + 1)
        try:
            verify(rows, broken)
        except AssertionError:
            pass
        else:
            raise AssertionError('Damaged global cube accepted.')
        checks.append({'constructor': type(model).__name__, 'physical_products': count,
                       'first_pass_checks': dict(inherited), 'corruption_rejected': True})
    print(json.dumps({'status': 'PASS', 'checks': checks,
        'scope': 'Global a1=a9=0 after the first-pass family-16 reduction; family 16 remains unresolved. Not part of the immutable fifth-post packet.'}, indent=2))


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('Run without -O.')
    check()
