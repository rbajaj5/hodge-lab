"""Independent exact denominator review; no covariant tables are expanded.

The inputs are independent symbols for values and polynomial directional
derivatives. This checks rational identities before imposing the curve or any
syzygy; it therefore audits denominator clearings without assuming the
residuals vanish. It is not a replay of the actual covariant identities.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import platform
import sys
import time

import sympy as sp


def main():
    started = time.monotonic()
    G,H,Q,J,SN,TN = values = sp.symbols('G H Q J SN TN')
    KG,PH,PQ,PJ,PSN,PTN = p_values = sp.symbols('KG PH PQ PJ PSN PTN')
    LG,LH,LQ,LJ = l_values = sp.symbols('LG LH LQ LJ')
    N,NE,LN,TNa = sp.symbols('N NE LN TNa')
    checks = []

    def require(condition, message):
        if not condition:
            raise RuntimeError(message)

    def exact(name, actual, expected):
        difference = sp.cancel(actual-expected)
        require(difference == 0, name + ': ' + str(difference))
        checks.append({'name': name, 'result': 'PASS'})

    def E(expression):
        return sum(sp.diff(expression, variable)*velocity/G
                   for variable,velocity in zip(values,p_values))

    def D(expression):
        mapping = [(G,LG),(H,LH),(Q,LQ),(J,LJ),(N,LN)]
        return sum(sp.diff(expression,variable)*velocity/G
                   for variable,velocity in mapping)

    xi = Q/H**2
    eta = -J/(2*H**3)
    sw = SN/3
    bw = -TN/108
    nxi = H*PQ-2*Q*PH
    neta = H*PJ-3*J*PH
    xidot = N/(G*H**3)
    etadot = -NE/(2*G*H**4)
    gdot = KG/G
    M = H*LQ-2*Q*LH
    Kd = G*H*LN-H*N*LG-3*G*N*LH

    exact('actual_xi_first_variation', E(xi), nxi/(G*H**3))
    exact('actual_eta_first_variation_Neta_sign', E(eta), -neta/(2*G*H**4))
    exact('relative_xi_derivative', D(xi), M/(G*H**3))
    exact('relative_xidot_derivative', D(xidot), Kd/(G**3*H**4))

    curve_residual = 2*eta*E(eta)-(3*xi**2+sw)*E(xi)-E(sw)*xi-E(bw)
    Nc = (54*J*neta-(324*Q**2+36*SN*H**4)*nxi
          -36*PSN*Q*H**5+PTN*H**7)
    exact('curve_jet_denominator_108_G_H7', curve_residual, Nc/(108*G*H**7))
    C = 27*J**2-108*Q**3-36*SN*Q*H**4+TN*H**6
    exact('curve_jet_numerator_product_rule', Nc, H*G*E(C)-6*C*PH)

    differential_residual = G*D(xidot)+gdot*D(xi)-6*etadot
    Nd = Kd+KG*H*M+3*G*NE
    exact('differential_jet_denominator_G2_H4', differential_residual, Nd/(G**2*H**4))

    source_differential_residual = G**2*(2*eta*D(xidot)-2*D(xi)*etadot)+12*eta**2*gdot
    Nj = -J*Kd+G*M*NE+3*J**2*KG*H
    exact('source_differential_jet_denominator_G_H7', source_differential_residual, Nj/(G*H**7))
    exact('source_differential_numerator_recombination', Nj,
          -J*Nd+(M+3*J)*(G*NE+KG*H*J))

    exact('moving_quotient_H_cancellation', xidot/(2*eta), -N/(G*J))
    adot = sp.Integer(0)
    bdot = -TNa/108
    moving_residual = gdot/G-(adot*xi+bdot)/(2*eta**2)+(G/3)*D(xidot/(2*eta))
    Nm = (54*KG*J**2+G**2*TNa*H**6
          -18*(G*J*LN-N*J*LG-N*G*LJ))
    exact('moving_map_denominator_54_G2_J2', moving_residual, Nm/(54*G**2*J**2))

    # These independent symbolic residuals must not vanish before the actual
    # covariant syzygies are used. Rejecting changed factors is meaningful.
    for name,residual,numerator,denominator in [
        ('curve',curve_residual,Nc,108*G*H**7),
        ('differential',differential_residual,Nd,G**2*H**4),
        ('source_differential',source_differential_residual,Nj,G*H**7),
        ('moving',moving_residual,Nm,54*G**2*J**2),
    ]:
        require(sp.cancel(residual) != 0, name + ': vacuous abstract residual')
        require(sp.cancel(residual-numerator/(2*denominator)) != 0,
                name + ': changed denominator not rejected')
        checks.append({'name':name+'_doubled_denominator_rejected','result':'PASS'})

    a,b,c,d,e,f,x,y = sp.symbols('a b c d e f x y')
    u = a*x**3+b*y**3+c+d*x**2*y+e*y**2+f*x**2
    g = sp.diff(u,x)
    beta = sp.diff(u,y)
    def auxiliary_E(expression):
        return sp.diff(expression,a)-x**3/g*sp.diff(expression,x)
    def relative_D(expression):
        return sp.diff(expression,y)-beta/g*sp.diff(expression,x)
    exact('auxiliary_tangency',auxiliary_E(u),0)
    exact('relative_tangency',relative_D(u),0)
    exact('E_D_x_commutator',auxiliary_E(relative_D(x))-relative_D(auxiliary_E(x)),0)
    exact('E_scaled_D_x_commutator',
          auxiliary_E(g*relative_D(x))-g*relative_D(auxiliary_E(x)),
          auxiliary_E(g)*relative_D(x))

    return {
        'status':'PASS',
        'check_count':len(checks),
        'checks':checks,
        'formulas':{
            'Nxi':'H*PQ - 2*Q*PH',
            'Neta':'H*PJ - 3*J*PH',
            'M':'H*LQ - 2*Q*LH',
            'Kd':'G*H*LN - H*N*LG - 3*G*N*LH',
            'curve_denominator':'108*G*H^7',
            'differential_denominator':'G^2*H^4',
            'source_differential_denominator':'G*H^7',
            'moving_denominator':'54*G^2*J^2',
            'curve_numerator':str(Nc),
            'differential_numerator':str(Nd),
            'source_differential_numerator':str(Nj),
            'moving_numerator':str(Nm),
        },
        'localization':['characteristic zero','G != 0','H != 0','J != 0 for moving quotient'],
        'scope':'Independent abstract rational denominator and sign audit. Does not prove actual covariant residuals vanish, replay a Lean kernel, or rerun seed checks.',
        'versions':{'python':platform.python_version(),'sympy':sp.__version__},
        'executable':sys.executable,
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'elapsed_seconds':round(time.monotonic()-started,6),
    }


if __name__ == '__main__':
    print(json.dumps(main(),indent=2))
