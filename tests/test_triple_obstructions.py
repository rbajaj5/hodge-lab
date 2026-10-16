"""Controls for the exact inference mechanisms used in the triple scan."""
from pathlib import Path
from fractions import Fraction as Q
import sys, unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'algebra'))
import degree7_triples as t


class TripleObstructionChecks(unittest.TestCase):
    def test_complex_conic_survives_coordinate_power_test(self):
        # x^2+y^2=0 has nonzero complex points. Positivity would be wrong.
        found, searched = t.power_witnesses([{(0, 0): Q(1), (1, 1): Q(1)}], [0, 1])
        self.assertEqual(found, [])
        self.assertEqual([s['degree'] for s in searched], [2, 3, 4])

    def test_cubic_consequence_without_quadratic_square(self):
        # x^2=yz and xy=0 imply x^3=0, while y and z need not vanish.
        found, _ = t.power_witnesses([{(0, 0): Q(1), (1, 2): Q(-1)},
                                    {(0, 1): Q(1)}], [0, 1, 2])
        self.assertEqual([(p['coordinate'], p['power']) for p in found], [(0, 3)])

    def test_dual_annihilates_corrections_and_recovers_quotient(self):
        span = t.base.Elimination()
        columns = [{0: Q(2), 1: Q(3), 3: Q(5)}, {1: Q(7), 2: Q(11)}]
        for column in columns: span.insert(dict(column))
        p = {0: Q(13), 1: Q(17), 2: Q(19), 3: Q(23)}
        reduced = t.normal(p, span)
        for m in (2, 3):
            dual = t.dual_for(m, span)
            self.assertTrue(all(t.dot(dual, c) == 0 for c in columns))
            self.assertEqual(t.dot(dual, p), reduced.get(m, 0))


if __name__ == '__main__': unittest.main()
