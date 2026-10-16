from pathlib import Path
from fractions import Fraction as Q
import copy, sys, unittest

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'algebra'))
import degree7_character_search as search
import degree7_e1 as e1


class DegreeSevenChecks(unittest.TestCase):
    def test_complex_solution_is_not_rejected_as_a_sum_of_squares(self):
        equations=[{(0,0):Q(1),(1,1):Q(1)}]
        proof=search.prove_chart(equations,2,0)
        self.assertFalse(proof['excluded'])  # a=1, z=+/-i really solves it.
        self.assertIsNone(search.ideal_certificate(equations,2,proof))
        search.verify_chart(equations,2,proof)

    def test_polynomial_ideal_certificate_and_corruption(self):
        # On a=1: xy=1, xz=0, yz=1 is inconsistent over C.
        equations=[{(1,2):Q(1),(0,0):Q(-1)},
                   {(1,3):Q(1)}, {(2,3):Q(1),(0,0):Q(-1)}]
        proof=search.prove_chart(equations,4,0)
        self.assertFalse(proof['excluded'])
        certificate=search.ideal_certificate(equations,4,proof,max_degree=4)
        self.assertIsNotNone(certificate)
        proof.update(ideal_contradiction=certificate,excluded=True)
        search.verify_chart(equations,4,proof)
        broken=copy.deepcopy(proof)
        broken['ideal_contradiction']['products'][0][2]=str(2*Q(broken['ideal_contradiction']['products'][0][2]))
        with self.assertRaises(AssertionError):search.verify_chart(equations,4,broken)

    def test_single_character_constructor_rejects_mixed_denominators(self):
        data,pairs=e1.load();first,second=data['character_families'][:2]
        indices=[first['basis_indices'][0],second['basis_indices'][0]]
        with self.assertRaises(AssertionError):
            search.build_system(indices,pairs,[],[],tuple(first['character']))


if __name__=='__main__':unittest.main()
