"""Independent polynomial reconstruction of the three-character proof packet.

Uses the pinned instance.rec, a second polynomial API, and the opposite order
of monic division. Shares the small identity replayer, not the producer's
B, modF, or numerator-field construction. No CAS or third-party modules.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import gzip, json, time

import degree7_verify_polynomials as audit
import degree7_triples as replay


class IndependentModel:
    def __init__(self):
        self.data = json.loads((replay.ROOT / 'algebra/degree7_e1_basis.json').read_text())
        target = audit.poly.load_target(replay.ROOT / 'sources/sextics/data/holdout')
        self.F, self.A = target['F'], target['A']
        assert target['q'] == 1
        assert audit.decode(self.data['F']) == self.F and audit.decode(self.data['A']) == self.A
        weights = self.data['character_generators']
        self.char = lambda m: tuple(sum(a*b for a, b in zip(w, m)) % 6 for w in weights)
        assert weights == [list(w) for w in replay.e1.WEIGHTS]
        assert {self.char(m) for m in self.F} == {(0, 0, 0)}
        self.alpha = self.char(next(iter(self.A)))
        self.pairs = [(audit.decode(p['D']), [audit.decode(n) for n in p['N']]) for p in self.data['basis']]
        DF = [audit.poly.derivative(self.F, i) for i in range(6)]
        self.groups = {}; self.dc = {}
        for i in self.data['retained_basis_indices']:
            D, N = self.pairs[i]; chars = {self.char(m) for m in D}
            assert len(chars) == 1
            c = chars.pop(); self.groups.setdefault(c, []).append(i); self.dc[i] = c
            vector_chars = {tuple((a-w[component]) % 6 for a, w in zip(self.char(m), weights))
                            for component, p in enumerate(N) for m in p}
            assert vector_chars == {tuple((a+b) % 6 for a, b in zip(self.alpha, c))}
            value = {}
            for p, d in zip(N, DF): value = audit.poly.add(value, audit.poly.mul(p, d))
            assert value == audit.poly.mul(self.A, D)
        expected, self.families = replay.selected_families(self.data)
        assert self.groups == expected
        self.fields = []; self.field_chars = []
        for i, j, mon in self.data['koszul_labels']:
            K = [{} for _ in range(6)]
            K[i] = audit.poly.mul({tuple(mon): Q(1)}, DF[j])
            K[j] = audit.poly.scale(audit.poly.mul({tuple(mon): Q(1)}, DF[i]), -1)
            chars = {tuple((a-w[component]) % 6 for a, w in zip(self.char(m), weights))
                     for component, p in enumerate(K) for m in p}
            assert len(chars) == 1
            self.fields.append(K); self.field_chars.append(chars.pop())
        assert len(self.fields) == 840
        self.columns = Counter()

    def target(self, i, j):
        return tuple((a+b+c) % 6 for a, b, c in zip(self.alpha, self.dc[i], self.dc[j]))

    @lru_cache(None)
    def quadratic(self, i, j):
        D, N = self.pairs[i]; E, P = self.pairs[j]
        p = audit.B(D, P)
        if i != j: p = audit.poly.add(p, audit.B(E, N))
        self.columns['quadratic_columns_reconstructed'] += 1
        result = audit.remainder(p, self.F)
        assert all(self.char(m) == self.target(i, j) for m in result)
        return result

    @lru_cache(None)
    def corrections(self, i, target):
        # Inspect all 840 fields, selecting by direct character addition.
        result = []
        for k, (K, c) in enumerate(zip(self.fields, self.field_chars)):
            if tuple((a+b) % 6 for a, b in zip(self.dc[i], c)) != target: continue
            p = audit.remainder(audit.B(self.pairs[i][0], K), self.F)
            assert all(self.char(m) == target for m in p)
            result.append((k, p))
            self.columns['correction_columns_reconstructed'] += 1
        return result


def run():
    start = time.perf_counter(); model = IndependentModel(); checks = Counter()
    with gzip.open(replay.OUT / 'certificates.json.gz', 'rt', encoding='utf-8') as f: packet = json.load(f)
    assert len(packet['families']) == 152
    for chars, row in zip(model.families, packet['families']):
        assert row['characters'] == [list(c) for c in chars]
        checks.update(replay.verify_family(model, row))
    print(json.dumps({'status': 'PASS', 'families': 152, **model.columns, **checks,
                      'opposite_division_order': True, 'target_read_from_instance_rec': True,
                      'seconds': time.perf_counter() - start}, indent=2), flush=True)


if __name__ == '__main__':
    if not __debug__: raise RuntimeError('Run without -O.')
    run()
