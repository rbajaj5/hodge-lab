"""Soundness controls for exceptional-rank branches, without optional FLINT."""
import copy
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'algebra'))
import degree7_rank_strata as r


class RankStrataTests(unittest.TestCase):
    def test_rank_one_patch_and_zero_branch(self):
        # a*z+1=0 and a*z=0 are impossible even at the exceptional point a=0.
        physical = [{(0, 1): Q(1), (): Q(1)}, {(0, 1): Q(1)}]
        tree = {'unit_pivots': [], 'status': 'split',
                'claim': {'kind': 'minor', 'rows': [0, 1], 'column': 1,
                          'polynomial': [[[0], '-1']], 'scalar': '-1',
                          'factors': [{'linear': [[[0], '1']], 'power': 1}]},
                'children': [{'unit_pivots': [], 'status': 'excluded',
                              'claim': {'kind': 'row', 'rows': [0], 'polynomial': [[[], '1']],
                                        'scalar': '1', 'factors': []}}]}
        counts = Counter()
        self.assertTrue(r.verify_tree(physical, 1, 2, 0, tree, counts))
        self.assertEqual(counts['excluded_leaves'], 1)
        broken = copy.deepcopy(tree)
        broken['children'] = []
        with self.assertRaises(AssertionError):
            r.verify_tree(physical, 1, 2, 0, broken, Counter())

    def test_nonconstant_pivot_requires_its_exceptional_branch(self):
        rows = {0: {1: {(0,): Q(1)}, -1: {(): Q(1)}}}
        with self.assertRaises(AssertionError):
            r.row_eliminate(rows, 0, 1)

    def test_two_correction_columns_and_augmented_minor(self):
        # det [[a,0,1],[0,b,1],[1,1,0]] = -a-b.
        physical = [{(0, 2): Q(1), (): Q(1)},
                    {(1, 3): Q(1), (): Q(1)},
                    {(2,): Q(1), (3,): Q(1)}]
        claim = {'kind': 'minor', 'rows': [0, 1, 2], 'columns': [2, 3]}
        self.assertEqual(r.minor(r.split(physical, 2), claim), {(0,): Q(-1), (1,): Q(-1)})
        # An omitted third correction would invalidate the submatrix obstruction.
        physical[2][(4,)] = Q(1)
        with self.assertRaises(AssertionError):
            r.minor(r.split(physical, 2), claim)


if __name__ == '__main__':
    unittest.main()
