"""A bounded GOE-to-curve pilot, not a Hodge-certificate search.

The model is explicitly transcribed from the pinned GOE correction note.
Checks expose the distinction between an algebraic curve, its differential,
and the exponential weight. No probability quadrature or Hodge solve claimed.
"""
from pathlib import Path
import argparse
import hashlib
import json
import platform
import time
import sympy as sp

ROOT=Path(__file__).resolve().parents[1]
PACKET=ROOT/'results/chi-curve-bridge'


def require(ok,message):
    if not ok: raise ValueError(message)


def run(perturb=None):
    started=time.monotonic()
    pins=json.loads((PACKET/'inputs.json').read_text(encoding='utf-8'))
    raw=(ROOT/pins['goe_source']['local_path']).read_bytes()
    require(hashlib.sha256(raw).hexdigest()==pins['goe_source']['sha256'],'Input hash mismatch')
    require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==pins['goe_source']['git_blob'],'Input Git blob mismatch')
    s,y,t,u,v,z,U,V=sp.symbols('s y t u v z U V',nonzero=True)
    k,m=sp.symbols('k m',integer=True)
    checks=[]
    def exact(label,expression):
        require(sp.cancel(expression)==0,label+' failed')
        checks.append(label)
    relation=s**4+2*s**2*y**2-t**4
    chart={s:t*u,y:t*v/(2*u)}
    quartic=v**2-2*(1-u**4)
    exact('curve chart identity',2*relation.subs(chart,simultaneous=True)/t**4-quartic)
    exact('inverse s',chart[s].subs({u:s/t,v:2*s*y/t**2},simultaneous=True)-s)
    exact('inverse y',chart[y].subs({u:s/t,v:2*s*y/t**2},simultaneous=True)-y)
    g2=(t**4/s**2-s**2)/2
    exact('corrected g squared on curve',g2.subs(s,t*u)-t**2*(1-u**4)/(2*u**2))
    phi=t**2*(u**2+u**-2)/4
    exact('Gaussian exponent transport',(s**2+g2).subs(s,t*u)/2-phi)
    inverse_jac=t**3/(s**2*y)
    exact('implicit inverse Jacobian',sp.diff(relation,t)+sp.diff(relation,y)*inverse_jac)
    dPhi=sp.diff(phi,u)
    exact('quartic to conic',quartic-(v**2-2*(1-z**2)).subs(z,u**2))
    exact('squared-variable rational quotient',(U**2+2*U*V-t**4).subs(V,(t**4-U**2)/(2*U)))
    exact('branch polynomial squarefree',sp.gcd(2*(1-u**4),sp.diff(2*(1-u**4),u),domain=sp.QQ)-1)
    exact('rational point on quartic',quartic.subs({u:1,v:0}))
    plane=s**4+2*s**2*y**2-t**4*z**4
    for variable in (s,y,z):
        exact('plane model singular infinity '+str(variable),sp.diff(plane,variable).subs({s:0,y:1,z:0}))
    exact('generic primitive denominator is odd',sp.Mod(4*k-2*m+1,2)-1)
    examples=[]
    for n in range(1,9):
        coeff=2**(n-1)*(1-u**4)**(n-1)/u**(2*n)
        primitive=2**(n-1)*sum((-1)**i*sp.binomial(n-1,i)*u**(4*i-2*n+1)/sp.Integer(4*i-2*n+1) for i in range(n))
        actual=primitive if perturb!='primitive-sign' or n!=1 else -primitive
        exact(f'm={n} rational primitive',sp.diff(actual,u)-coeff)
        # Suppress the common Gamma(m)*sqrt(2*pi) in both prefactors.
        original=sp.Integer(2)**(2-n)*t**3*g2**(n-1)/s**2
        normalized=sp.Integer(2)**(4-3*n)*t**(2*n)*coeff
        actual_jac=t if perturb!='omit-ds' or n!=1 else 1
        exact(f'm={n} complete measure transport',original.subs(s,t*u)*actual_jac-normalized)
        exact(f'm={n} conic quotient sign',coeff.subs(u,-u)*(-1)+coeff)
        # The naive e^-phi times the unweighted primitive leaves this error.
        omitted_weight_residual=sp.cancel(-dPhi*primitive)
        require(omitted_weight_residual!=0,f'm={n} weight negative control vacuous')
        checks.append(f'm={n} exponential cannot be dropped')
        examples.append({'m':n,'algebraic_coefficient':str(sp.expand(coeff)),
                         'rational_primitive':str(sp.expand(primitive)),
                         'naive_weighted_residual':str(omitted_weight_residual)})
    return {'status':'PASS','scope':'Exact curve/density transport and algebraic primitive examples; no target Hodge correspondence',
        'checks_passed':len(checks),'checks':checks,'examples':examples,
        'general_argument':'For every integer m>=1, expand (1-u^4)^(m-1); exponents 4k-2m are even, so termwise primitives divide by odd nonzero 4k-2m+1.',
        'genus_argument':'Four simple branch points for the degree-two map to P1_u; Riemann-Hurwitz gives genus one for the smooth completion.',
        'coefficient_field':'Q(t), t nonzero; probability integral uses t>0, 0<u<1 and positive v',
        'isotrivial_after_scaling':True,'parameter_m_changes_curve':False,
        'hodge_target_map_constructed':False,'elapsed_seconds':round(time.monotonic()-started,6),
        'versions':{'python':platform.python_version(),'sympy':sp.__version__},
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'inputs_sha256':hashlib.sha256((PACKET/'inputs.json').read_bytes()).hexdigest()}


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--perturb',choices=['primitive-sign','omit-ds'])
    args=parser.parse_args()
    try:
        result=run(args.perturb)
        if not args.perturb:
            (PACKET/'replay.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
        print(json.dumps({'status':'PASS','checks':result['checks_passed'],'seconds':result['elapsed_seconds']}))
    except Exception as error:
        print('FAIL: '+str(error))
        raise SystemExit(1)
