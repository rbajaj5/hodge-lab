"""Exact source characters, broken symmetries, and a mixed-parameter control.

The mixed control satisfies one displayed necessary equation, not a certificate.
"""
from pathlib import Path
import hashlib
import json
import time
import sympy as s

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/one-reflection-skew-audit-20261021'
RECORD = OUT / 'inputs/live/upstream/data/one-reflection-skew/record.json'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    started = time.perf_counter()
    record = json.loads(RECORD.read_text(encoding='utf-8'))
    Z = s.symbols('X0 X1 X2 Y0 Y1 Y2')
    F, A = [s.Add(*(s.Rational(c) * s.prod(z**e for z, e in zip(Z, m))
                    for c, m in record[key]['terms'])) for key in ('F', 'A')]
    require(record['q'] == 1, 'q')
    weights = [(1, 1, 1, 0), (1, 0, 0, 0), (1, 1, 1, 0),
               (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)]
    character = lambda mon: [sum(e*w[k] for e, w in zip(mon, weights)) % 2
                             for k in range(4)]
    require(all(character(m) == [0]*4 for c, m in record['F']['terms']), 'F invariant')
    require({tuple(character(m)) for c, m in record['A']['terms']} == {(1, 0, 1, 0)}, 'A character')
    omega = [sum(w[k] for w in weights) % 2 for k in range(4)]
    form = [(a+b) % 2 for a, b in zip((1, 0, 1, 0), omega)]
    require(omega == [1]*4 and form == [0, 1, 0, 1], 'Differential character')
    require(all(sum(w) % 2 == 1 for w in weights), 'central -I element')
    actions = {}
    for name, image in [
        ('Y2_reflection', (*Z[:5], -Z[5])),
        ('Y0_Y1_exchange', (*Z[:3], Z[4], Z[3], Z[5])),
        ('negative_Y0_Y1_exchange', (*Z[:3], -Z[4], -Z[3], Z[5])),
        ('complex_interaction_involution', (*Z[:3], s.I*Z[4], -s.I*Z[3], Z[5])),
        ('simultaneous_X_negation', (-Z[0], -Z[1], -Z[2], *Z[3:])),
    ]:
        difference = s.expand(F.subs(dict(zip(Z, image)), simultaneous=True) - F)
        determinant = s.Matrix(image).jacobian(Z).det()
        source_image = s.expand(A.subs(dict(zip(Z, image)), simultaneous=True))
        actions[name] = {'F_preserved': difference == 0, 'F_difference': str(difference),
                         'determinant': str(determinant), 'A_image': str(source_image),
                         'A_Omega_image_coefficient': str(s.expand(determinant*source_image))}
    require(actions['Y2_reflection']['F_preserved'], 'reflection symmetry')
    require(actions['simultaneous_X_negation']['F_preserved'], 'X-negation symmetry')
    require(all(not actions[name]['F_preserved'] for name in
                ('Y0_Y1_exchange', 'negative_Y0_Y1_exchange', 'complex_interaction_involution')),
            'Do not promote interaction symmetries to full-sextic symmetries')
    require(s.sympify(actions['complex_interaction_involution']['F_difference']) ==
            -2*(Z[3]**6+Z[4]**6), 'complex exchange defect')

    alpha, y, T = s.symbols('alpha y T')
    skew = alpha*Z[0]*Z[1]*y*T*(alpha**2*T**2-y**2)/7
    swapped = skew.subs({y:T, T:y}, simultaneous=True)
    defect = s.factor(swapped-skew)
    expected = alpha*Z[0]*Z[1]*(alpha**2+1)*y*T*(y**2-T**2)/7
    require(s.expand(defect-expected) == 0 and defect != 0, 'cover exchange defect')
    require([(5*3+1) % 6, (5+3) % 6] == [4, 2], 'skew monomial weights')

    # Real cross-family cancellation over Q(i), exactly as in the later addendum.
    # f=F|Y2=0; c=lambda e_X2 and R2=i lambda X2^2.
    f = F.subs(Z[5], 0)
    lam = s.symbols('lambda')
    hessian_term = lam**2*s.diff(f, Z[2], 2)
    square_term = 30*(s.I*lam*Z[2]**2)**2
    require(s.expand(hessian_term+square_term) == 0, 'mixed cancellation')
    require(hessian_term != 0 and square_term != 0, 'both summands really present')
    altered = 30*(2*s.I*lam*Z[2]**2)**2
    require(s.expand(hessian_term+altered) != 0, 'perturbation must break cancellation')
    D = Z[5]**2*s.diff(f, Z[2]) + 6*s.I*Z[5]**5*Z[2]**2
    N = [s.Integer(0)]*6
    N[2] = A*Z[5]**2
    N[5] = s.I*A*Z[2]**2
    require(s.expand(sum(N[i]*s.diff(F, Z[i]) for i in range(6))-A*D) == 0,
            'explicit mixed candidate solves E1')
    mixed_B = s.expand(D*sum(s.diff(N[i], Z[i]) for i in range(6)) -
                       sum(N[i]*s.diff(D, Z[i]) for i in range(6)))
    require(mixed_B != 0, 'not a strict E2 solution')
    # For this particular lift, divisibility by monic F can be checked directly.
    remainder = s.rem(mixed_B, F, Z[5])
    require(remainder != 0, 'particular lift is not a certificate')
    # AX2^2 has a nonzero coefficient inaccessible to any f_i times a polynomial.
    obstruction_monomial = (3, 0, 2, 3, 0)
    gradient_monomials = [m for i in range(5) for m, c in s.Poly(s.diff(f, Z[i]), *Z[:5]).terms()]
    require(all(not all(a <= b for a, b in zip(m, obstruction_monomial))
                for m in gradient_monomials), 'monomial nonmembership in J(f)')
    result = {'status':'PASS', 'record_sha256':hashlib.sha256(RECORD.read_bytes()).hexdigest(),
              'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'coordinate_characters':weights, 'A_character':[1,0,1,0],
              'Omega_character':omega, 'A_Omega_character':form,
              'odd_degree_characters':'Affine coset (torsor), not ordinary characters of G/{+I,-I} without a twist.',
              'actions':actions, 'cover_exchange_defect':str(defect),
              'mixed_control':{'field':'Q(i)', 'hessian_term':str(hessian_term),
                 'square_term':str(square_term), 'D':str(D), 'E1_residual':'0',
                 'B_remainder_mod_F':str(s.factor(remainder)), 'altered_R2_rejected':True,
                 'AX2_squared_not_in_Jf_by_monomial_support':True,
                 'scope':'One necessary mixed equation cancels. This particular lift fails E2. No exclusion of all Koszul-corrected lifts is inferred.'},
              'seconds':time.perf_counter()-started, 'sympy':s.__version__}
    (OUT/'characters.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':'PASS','mixed_cancellation':True,'particular_lift_fails':True}))


if __name__ == '__main__':
    main()
