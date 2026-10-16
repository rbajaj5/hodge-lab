from pathlib import Path
from fractions import Fraction
import copy, hashlib, json, math, subprocess, sys, unittest
import numpy as np

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'experiments'))
import gpu_identity_screen as algebra
import check_transfer_packet as replay
import period_congruence_probe as period
import source_bridge_lab as lab
import anisotropic_flow as flow
import response_hodge as response
import gram_discrimination as discrimination


class ExactChecks(unittest.TestCase):
    def test_pinned_sources(self):
        for name,source in json.loads((ROOT/'sources.json').read_text()).items():
            with self.subTest(source=name):
                head=subprocess.check_output(['git','-C',str(ROOT/'sources'/name),'rev-parse','HEAD'],text=True).strip()
                self.assertEqual(head,source['commit'])

    def test_parser_and_exact_derivative(self):
        for expression in ['X0.__class__','__import__("os")','X0[0]','X0**-1','0.5*X0']:
            with self.assertRaises(ValueError):algebra.parse_polynomial(expression)
        p=algebra.parse_polynomial('(X0+Y0)**3/3')
        self.assertEqual(algebra.derivative(p,0),algebra.parse_polynomial('(X0+Y0)**2'))

    def test_symbolic_control_and_mutation(self):
        folder=ROOT/'sources/sextics/data/fermat-pair-rational-d4-strict'
        case=algebra.load_target(folder);w=json.loads((folder/'witness.json').read_text())
        case.update(D=algebra.parse_polynomial(w['D']),N=[algebra.parse_polynomial(n) for n in w['N']],Q=algebra.parse_polynomial(w['Q']))
        self.assertFalse(algebra.symbolic_residual(case))
        case['N'][0]=algebra.add(case['N'][0],algebra.parse_polynomial('X0**4*Y0/6'))
        self.assertTrue(algebra.symbolic_residual(case))

    def test_transfer_packet_negative_control(self):
        packet=json.loads(replay.PACKET.read_text())
        row=next(r for r in packet['cases'] if not r['accepted_control'])
        replay.check_row(row)
        broken=copy.deepcopy(row);broken['counterexample']['base_term']+=1
        with self.assertRaises(AssertionError):replay.check_row(broken)

    def test_period_independent_expansion(self):
        F=algebra.load_target(ROOT/'sources/sextics/data/holdout')['F']
        for n in [0,1,6,12,18]:
            self.assertEqual(period.direct_coefficient(F,n),period.period(n//6) if n%6==0 else 0)
        delta=period.period(49)-period.period(7)
        self.assertEqual(period.vp(delta,7),4)
        self.assertEqual(delta%7**6,7203)

    def test_all_published_period_cases(self):
        report=json.loads((ROOT/'results/period-congruence/report.json').read_text())
        for row in report['cases']:
            p,n,r=(row[k] for k in ['p','n','r'])
            observed=period.vp(period.period(n*p**r)-period.period(n*p**(r-1)),p)
            self.assertEqual(observed,row['holdout_valuation'])

    def test_hodge_ranking_against_exhaustive_kemeny(self):
        actual=lab.ranking_experiment()
        published=json.loads((ROOT/'results/source-bridges/report.json').read_text())['ranking']
        self.assertEqual(actual['counts'],published['counts'])
        self.assertEqual(actual['example']['hodge_cost'],4)
        self.assertEqual(actual['example']['kemeny_cost'],3)

    def test_braid_abelianization_loses_order(self):
        a,b=(1,1,2,2),(2,2,1,1)
        self.assertEqual(lab.braid_stats.pure_pair_winding_vector(a),lab.braid_stats.pure_pair_winding_vector(b))
        self.assertNotEqual(lab.braid_stats.reduced_burau_minus_one(a),lab.braid_stats.reduced_burau_minus_one(b))

    def test_saved_colorings(self):
        with np.load(ROOT/'results/source-bridges/fractional-field-meshes.npz') as saved:
            for H in [.15,.5,.85]:
                adj=lab.four.compactified_triangulation_adjacency(saved['diagonals_'+str(H)])
                colors=saved['colors_'+str(H)]
                self.assertTrue(lab.four.coloring_is_proper(adj,colors))
                # Direct edge check independent of the source's verifier.
                self.assertTrue(all(colors[i]!=colors[j] for i,neighbors in enumerate(adj) for j in neighbors))
                self.assertEqual((len(adj),sum(map(len,adj))//2),(290,864))


class NumericalChecks(unittest.TestCase):
    def test_thermal_response_against_exact_gaussian_moments(self):
        x=np.linspace(-8,8,8193)
        psi=np.stack([x,x*x],axis=1)
        covariance,_,_=response.thermal(psi,np.array([0.,-.5]),.2)
        np.testing.assert_allclose(covariance,np.diag([1.,.4]),atol=1e-12)

    def test_probe_matches_original_polynomial(self):
        probe=response.Probe();t=np.array([.12,.91,1.73,2.88])
        z=probe.plane@np.array([np.cos(t),np.sin(t)])
        direct=np.array([np.prod(z**np.array(e)[:,None],axis=0) for e in probe.exponents]).T
        np.testing.assert_allclose(probe.features(t),direct,atol=1e-14)
        np.testing.assert_allclose(probe.features(t+np.pi),direct,atol=1e-14)

    def test_gaussian_proxy_symmetry_and_repetition(self):
        v=np.array([.8,1.,1.4])
        self.assertEqual(discrimination.scalar_proxy(np.ones(3)),0.)
        p=discrimination.scalar_proxy(v,nodes=256)
        self.assertAlmostEqual(p,discrimination.scalar_proxy(1/v,nodes=256),places=12)
        self.assertGreater(discrimination.scalar_proxy(v,repeats=8,nodes=256),p)

    def test_covariance_comparison_is_congruence_invariant(self):
        A=np.array([[2.,.4],[.4,1.]])
        B=np.array([[1.,-.2],[-.2,3.]])
        S=np.array([[1.,2.],[0.,1.]])
        np.testing.assert_allclose(discrimination.relative_variances(A,B),
                                   discrimination.relative_variances(S@A@S.T,S@B@S.T),atol=1e-12)

    def test_walsh_diagonalizes_cube_laplacian(self):
        d=4;n=2**d
        L=d*np.eye(n)
        for i in range(n):
            for bit in range(d):L[i,i^(1<<bit)]=-1
        W=lab.fwht(np.eye(n),np)
        np.testing.assert_allclose(W@W,np.eye(n),atol=1e-14)
        np.testing.assert_allclose(W@L@W,np.diag([2*i.bit_count() for i in range(n)]),atol=1e-14)

    def test_zero_residual_does_not_imply_good_conditioning(self):
        V=np.array([[1.,1.],[0.,1e-10]])
        A=V@np.diag([1.,2.])@np.linalg.inv(V)
        self.assertLess(np.linalg.norm(A@V-V@np.diag([1.,2.])),1e-12)
        self.assertFalse(lab.analyze_design_matrix(V,standardize=False,condition_limit=1000).accepted)

    def test_saved_discriminant_winding(self):
        with np.load(ROOT/'results/source-bridges/ginibre-loop.npz') as saved:
            z=saved['path'];i,j=np.triu_indices(z.shape[1],1)
            delta=z[:,i]-z[:,j]
            disc=np.prod((delta/np.abs(delta))**2,axis=1)
            winding=np.sum(np.angle(disc[1:]/disc[:-1]))/(2*np.pi)
            self.assertAlmostEqual(winding,-11,places=10)

    def test_anisotropy_and_stationary_wulff_shape(self):
        theta,plane,f,phi,a,h,eps,exact=flow.setup(64)
        np.testing.assert_allclose(plane.T@plane,np.eye(2),atol=1e-14)
        self.assertGreaterEqual(exact.min(),.65-1e-12)
        np.testing.assert_allclose(phi,np.roll(phi,32),atol=1e-14)
        equilibrium=1.4*phi[None,:]
        frames,_=flow.evolve_cpu(equilibrium,phi,1e-4,20,20)
        np.testing.assert_allclose(frames[-1],equilibrium,atol=1e-12)

    def test_flow_area_and_perimeter(self):
        theta,plane,f,phi,a,h,eps,exact=flow.setup(64)
        frames,_=flow.evolve_cpu(h,phi,2e-4,100,10)
        m=flow.metrics(frames,phi)
        self.assertLess(np.max(np.abs(m['area']/m['area'][0]-1)),1e-12)
        self.assertLess(np.max(np.diff(m['perimeter'],axis=0)),1e-10)
        self.assertGreater(m['rho'].min(),0)


if __name__=='__main__':unittest.main()
