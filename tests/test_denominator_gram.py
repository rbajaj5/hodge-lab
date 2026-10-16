"""Independent checks of the geometry-to-denominator experiment."""
from pathlib import Path
from fractions import Fraction as Q
import json, sys, unittest
import numpy as np
from scipy.linalg import lstsq

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'experiments'))
import denominator_gram_search as search


class DenominatorGramChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=search.exact.load_model()
        cls.numerical=search.NumericalE2(cls.model)
        cls.Cbar=search.basis_data()[1]

    def test_covariance_matches_scalar_variance_and_constant_shift(self):
        rng=np.random.default_rng(1234);psi=rng.normal(size=(31,7))
        weights=np.exp(np.linspace(-3,0,31));weights/=weights.sum()
        G=search.covariance(psi,weights)
        direction=rng.normal(size=7);scalar=psi@direction
        variance=np.average((scalar-np.average(scalar,weights=weights))**2,weights=weights)
        self.assertAlmostEqual(float(direction@G@direction),variance,places=12)
        np.testing.assert_allclose(G,search.covariance(psi+np.arange(7),weights),atol=2e-15)

    def test_numerical_tensor_contraction_against_exact_arithmetic(self):
        # Includes one coordinate omitted from the candidate sampler: the
        # scorer must still implement the full tensor, not a hidden reduction.
        coefficients={0:Q(1,3),7:Q(-2),42:Q(5,7),105:Q(4,9)}
        a=np.zeros(108)
        for i,c in coefficients.items():a[i]=float(c)
        b,columns=search.exact.specialize(self.model,coefficients)
        bn,M=self.numerical.specialize(a);expected=np.zeros_like(bn)
        for i,c in b.items():expected[i]=float(c)
        np.testing.assert_allclose(bn,expected,atol=1e-12)
        expected_M=np.zeros(M.shape)
        for j,col in enumerate(columns):
            for i,c in col.items():expected_M[i,j]=float(c)
        np.testing.assert_allclose(M.toarray(),expected_M,atol=1e-12)

    def test_sparse_fit_against_dense_rank_revealing_factorization(self):
        pool=search.candidates(search.basis_data()[3])
        a=search.unit_coefficients([pool[0],pool[search.PER_SUPPORT]],self.Cbar)
        for direction in a:
            b,M=self.numerical.specialize(direction)
            nonzero_rows=(np.diff(M.indptr)>0)|(b!=0)
            dense=M[nonzero_rows].toarray();rhs=b[nonzero_rows]
            z,_,_,_=lstsq(dense,-rhs,cond=1e-12,lapack_driver='gelsy')
            reference=np.linalg.norm(rhs+dense@z)
            observed=self.numerical.residual(direction)['E2_residual']
            self.assertAlmostEqual(reference,observed,places=10)

    def test_saved_scores_are_projective_and_use_actual_denominators(self):
        report=json.loads((search.OUT/'report.json').read_text())
        matrices=np.load(search.OUT/'grams.npz')
        for run in [report,*report['replications']]:
            pool=[{i:Q(c) for i,c in row['denominator_coordinates']} for row in run['candidates']]
            a=search.unit_coefficients(pool,self.Cbar)
            np.testing.assert_allclose(np.linalg.norm(a@self.Cbar.T,axis=1),1,atol=1e-14)
            for method in ['anisotropic','uniform']:
                predicted=np.einsum('ij,jk,ik->i',a,matrices[method],a)
                recorded=[row[method+'_score'] for row in run['candidates']]
                np.testing.assert_allclose(predicted,recorded,rtol=1e-10,atol=1e-18)
        # The polynomial coefficient representative is orthogonal to F.
        F=search.basis_data()[2]
        np.testing.assert_allclose(F@self.Cbar,0,atol=1e-13)


if __name__=='__main__':unittest.main()
