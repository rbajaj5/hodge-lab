"""Controls for polynomial correction cancellation and its logical limits."""
from pathlib import Path
from fractions import Fraction as Q
import copy, sys, unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'algebra'))
import degree7_syzygies as s


class PolynomialSyzygyChecks(unittest.TestCase):
    def setUp(self):
        # E=(x*z+1,y*z+1). The polynomial left syzygy (y,-x)
        # eliminates z, giving y-x. No constant left syzygy does this.
        self.rows = [{(0, 2): Q(1), (): Q(1)}, {(1, 2): Q(1), (): Q(1)}]

    def test_linear_multiplier_finds_obstruction_absent_from_constant_test(self):
        baseline, _ = s.necessary_relations(self.rows, 2, [()])
        extended, _ = s.necessary_relations(self.rows, 2, [(), (0,), (1,)])
        self.assertEqual(baseline, [])
        self.assertEqual(len(extended), 1)
        self.assertEqual(s.cert.decode(extended[0]['polynomial']), {(0,): Q(1), (1,): Q(-1)})
        s.verify_relation(self.rows, 2, [0, 1], extended[0])

    def test_surviving_relation_does_not_establish_solvability_at_rank_drop(self):
        extended, _ = s.necessary_relations(self.rows, 2, [(), (0,), (1,)])
        self.assertEqual(s.cert.substitute(s.cert.decode(extended[0]['polynomial']), {0: {}, 1: {}}), {})
        self.assertEqual([s.cert.substitute(p, {0: {}, 1: {}}) for p in self.rows], [{(): Q(1)}, {(): Q(1)}])

    def test_corrupted_multiplier_is_rejected(self):
        relations, _ = s.necessary_relations(self.rows, 2, [(), (0,), (1,)])
        bad = copy.deepcopy(relations[0])
        bad['products'][0][2] = str(Q(bad['products'][0][2]) + 1)
        with self.assertRaises(AssertionError):
            s.verify_relation(self.rows, 2, [0, 1], bad)


if __name__ == '__main__':
    unittest.main()
