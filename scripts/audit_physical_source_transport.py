"""Exact, source-bound local transport audit; not a full Lean/certificate replay.

Run from any directory with Python 3 and SymPy. All requirements use explicit
exceptions, so python -O cannot disable them. Inputs are pinned byte-for-byte.
The curve syzygy and its covariant first variation remain stated dependencies.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
from pathlib import Path
import platform
import re
import time
import sympy as s

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / 'results/physical-source-transport-audit'
BASE = 'data/holdout-moving-branch/'
LIB = 'formal/lean/HodgeComputer/Constructions/TransitiveCubic/'


def require(condition, label):
    if not condition:
        raise ValueError(label)


def definition(text, name):
    m = re.search(r'^def ' + re.escape(name) + r'\b[^\n]*?:=\s*', text, re.M)
    require(m is not None, 'Missing definition: ' + name)
    return re.split(r'\n(?=(?:def|lemma|theorem|section|end|set_option|variable|/--|/-!))',
                    text[m.end():], 1)[0].strip()


def arithmetic(text, env):
    """Only rational arithmetic and whitelisted symbols; no eval or Lean execution."""
    text = text.replace('^', '**').replace('c₁', 'c1').replace('c₂', 'c2').replace('α', 'alpha')
    text = re.sub(r':\s*K\b', '', text)
    for name in ('p', 'f', 'z', 'v', 'gradient'):
        text = re.sub(r'\b' + name + r' (\d)\b', name + r'\1', text)
    text = re.sub(r'\bhessian (\d) (\d)\b', r'hessian\1\2', text)

    def walk(n):
        if isinstance(n, ast.Constant) and type(n.value) is int:
            return s.Integer(n.value)
        if isinstance(n, ast.Name) and n.id in env:
            return env[n.id]
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.UAdd, ast.USub)):
            return walk(n.operand) * (-1 if isinstance(n.op, ast.USub) else 1)
        if isinstance(n, ast.BinOp):
            a, b = walk(n.left), walk(n.right)
            if isinstance(n.op, ast.Add): return a + b
            if isinstance(n.op, ast.Sub): return a - b
            if isinstance(n.op, ast.Mult): return a * b
            if isinstance(n.op, ast.Div):
                require(b != 0, 'Zero source divisor')
                return a / b
            if isinstance(n.op, ast.Pow):
                require(b.is_Integer and 0 <= b <= 20, 'Unexpected exponent')
                return a ** b
        raise ValueError('Unsupported arithmetic: ' + ast.dump(n))
    return walk(ast.parse(' '.join(text.split()), mode='eval').body)


def run(perturb=None):
    start = time.monotonic()
    manifest = json.loads((PACKET/'inputs.json').read_text(encoding='utf-8'))
    for item in manifest['files']:
        data = (PACKET/'inputs'/item['path']).read_bytes()
        require(hashlib.sha256(data).hexdigest() == item['sha256'], 'SHA256: '+item['path'])
        require(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == item['git_blob'],
                'Git blob: '+item['path'])
    def read(name): return (PACKET/'inputs'/name).read_text(encoding='utf-8')
    checks = []
    def eq(label, lhs, rhs=0):
        require(s.cancel(lhs-rhs) == 0, label)
        checks.append(label)
    def src(file, name, env): return arithmetic(definition(read(BASE+file+'.lean'), name), env)
    def vector(file, name, env):
        body = definition(read(BASE+file+'.lean'), name)
        require(body.startswith('![') and body.endswith(']'), 'Vector syntax: '+name)
        return [arithmetic(entry, env) for entry in body[2:-1].split(',')]

    names = ['X0','X1','X2','Y0','Y1','Y2']
    p = s.symbols('p0:6')
    fields = dict(re.findall(r'^(F|A|q): (.+)$', read(BASE+'instance.rec'), re.M))
    require(json.loads(read(BASE+'provenance.json'))['variables'] == names, 'Variable order')
    require(fields['q'] == '1', 'Pole order')
    F, A = [arithmetic(fields[k], dict(zip(names,p))) for k in ('F','A')]
    eq('protected source A', A, p[0]**3*p[3]**3)
    fg = [s.diff(F,w) for w in p]
    env = {f'p{i}':w for i,w in enumerate(p)}
    for name in ['radial','ratio','cOne','cTwo','x','y','t','parameterT',
                 'coeffA','coeffB','coeffC','coeffD','coeffE','coeffF']:
        env[name] = src('PhysicalCoordinates', name, env)
    R,v,x,y = [env[k] for k in ('radial','ratio','x','y')]
    env.update({f'gradient{i}':w for i,w in enumerate(fg)})
    env.update({f'hessian{i}{j}':s.diff(F,p[i],p[j]) for i in range(6) for j in range(6)})
    for name in ['pairedGradient','pairedHessian','cubicNormal','cubicSecondNormal',
                 'cubicNormalJet','correction']:
        env[name] = src('PhysicalNormalTransport',name,env)
    H,Q,G,Gx,Gdot,C = [env[k] for k in ['pairedGradient','pairedHessian','cubicNormal',
                                      'cubicSecondNormal','cubicNormalJet','correction']]
    require(definition(read(BASE+'PhysicalNormalTransport.lean'),'correctionVector') ==
            'Pi.single 2 correction', 'Normal correction tangent slot')
    U = arithmetic(definition(read(LIB+'Cubic.lean'),'cubic'),
                   dict(zip('abcdef',[env['coeff'+k] for k in 'ABCDEF']),x=x,y=y,z=s.Integer(1)))
    eq('protected F = R^3 U',F,R**3*U)
    eq('protected A = v^3 R^3 x^3',A,v**3*R**3*x**3)
    eq('paired gradient = 2 R^3 x G',H,2*R**3*x*G)
    eq('paired Hessian minus gradient',Q-H,4*R**3*x*x*Gx)

    # Generic normal change, specialized only after exact symbolic differentiation.
    pp,qq,ff,gg,fpp,fpq,fqq = s.symbols('pp qq ff gg fpp fpq fqq')
    HH = pp*ff+qq*gg
    CC = -pp**3*qq**4/HH
    dd = {pp:-gg/ff,qq:s.Integer(1),ff:fpq-gg/ff*fpp,gg:fqq-gg/ff*fpq}
    dCC = sum(s.diff(CC,w)*dw for w,dw in dd.items())
    generic_source = 3*pp**2*qq**3/ff-pp**3*qq**3*fpp/ff**2
    normal_div = dCC-CC*dd[ff]/ff
    eq('generic normal correction',generic_source,
       pp**3*qq**3*(7*HH-(pp**2*fpp+2*pp*qq*fpq+qq**2*fqq))/HH**2+normal_div)
    eq('source normal correction binding',C,CC.subs({pp:p[0],qq:p[3],ff:fg[0],gg:fg[3]}))
    eq('cubic normal source scaling',A*(7*H-Q)/H**2,v**3*Gdot/G)

    # Reconstruct the actual relative direction and all its passive coordinates.
    env['secondPairedGradient'] = src('PhysicalCubicTangent','secondPairedGradient',env)
    vel = vector('PhysicalCubicTangent','velocity',env)
    def D(w): return sum(s.diff(w,t)*vt for t,vt in zip(p,vel))
    eq('relative direction tangent to F', D(F))
    for n in ['radial','ratio','cOne','cTwo']:
        eq('D '+n+' = 0',D(env[n]))
    eq('D y = 1',D(y),1)
    Gy = src('PhysicalCubicTangent','cubicYNormal',env)
    eq('D x = -Uy/Ux',D(x),-Gy/G)

    # Generic gradient/symmetric Hessian: no reduction modulo F or numerical seed.
    f = s.symbols('f0:6')
    h = {(i,j):s.Symbol(f'h{i}{j}') for i in range(6) for j in range(i,6)}
    generic_env = dict(env)
    generic_env.update(pairedGradient=p[0]*f[0]+p[3]*f[3],
                       secondPairedGradient=p[1]*f[1]+p[4]*f[4])
    generic_env['weight'] = src('PhysicalCubicVolume','weight',generic_env)
    W = vector('PhysicalCubicVolume','volumeVector',generic_env)
    def partial(w,i):
        return s.diff(w,p[i])+sum(s.diff(w,f[j])*h[min(i,j),max(i,j)] for j in range(6))
    def tangent(w,i): return partial(w,i)-f[i]/f[0]*partial(w,0)
    eq('generic volume vector residue divergence',sum(tangent(w,i)-w*tangent(f[0],i)/f[0]
                                                   for i,w in enumerate(W,1)))
    for i,w in enumerate(W):
        eq(f'volume vector direction {i}',w.subs(dict(zip(f,fg))),v**3*G*vel[i+1])

    # Differentiate all five passive coordinates, retaining arbitrary tangent xi.
    z = s.symbols('z0:5'); xi = s.Symbol('xi')
    def tau(w,i): return s.diff(w,p[i])-f[i]/f[0]*s.diff(w,p[0])
    passive = [env['parameterT'],env['cOne'],env['cTwo'],R]
    matrix = s.Matrix([[tau(w,i) for i in range(1,6)] for w in passive]+
                      [[tau(R**2,i)*xi+R**2*z[i-1] for i in range(1,6)]])
    raw = definition(read(BASE+'PhysicalJacobianCoordinates.lean'),'rawMatrix')
    require(raw.startswith('!![') and raw.endswith(']'),'Matrix syntax')
    menv = dict(env,**{str(w):w for w in f+z},u=xi)
    submitted = s.Matrix([[arithmetic(e,menv) for e in row.split(',')] for row in raw[3:-1].split(';')])
    require(submitted.shape == (5,5),'Matrix shape')
    for i in range(5):
        for j in range(5): eq(f'coordinate matrix entry {i},{j}',matrix[i,j],submitted[i,j])
    # Sparse row R has a single nonzero; a 4x4 expansion keeps this bounded.
    determinant = s.cancel(2*p[2]*matrix.minor_submatrix(3,1).det(method='domain-ge'))
    direction = sum(w*zz for w,zz in zip(W,z))
    eq('direct determinant = -48 R^4 W(xi)/F0',f[0]*determinant,-48*R**4*direction)
    eta, radial, ratio, normal, dyxi = s.symbols('eta R v G Dxi', nonzero=True)
    density = (-48*radial**4*ratio**3*normal*dyxi/(2*radial**3*eta)).subs(dyxi,6*eta/normal)
    eq('residue density = -144 R v^3',density,-144*radial*ratio**3)

    # A second route through a small ambient coordinate chart tests orientation.
    c1,c2,xx,yy = s.symbols('c1 c2 x y')
    paired = s.Matrix([p[0],p[1],p[2],ratio*p[0],ratio*c1*p[1],ratio*c2*p[2]])
    det1 = paired.jacobian([p[0],p[1],p[2],ratio,c1,c2]).det()
    eq('paired coordinate determinant',det1,p[0]*p[1]*p[2]*ratio**2)
    det2 = s.Matrix([radial*xx,radial*yy,radial]).jacobian([xx,yy,radial]).det()
    eq('squared coordinate determinant',det2,radial**2)
    ambient_density = s.cancel(det1/(8*p[0]*p[1]*p[2])*det2)
    passive_jac = s.Matrix([[0,ratio**6,6*radial*ratio**5,0,0],[0,0,0,1,0],
                           [0,0,0,0,1],[0,1,0,0,0],
                           [radial**2*dyxi,*s.symbols('q1:5')]])
    target_density = passive_jac.det()/(2*radial**3*eta)
    eq('second chart residue density',
       (target_density/(ambient_density/(radial**3*normal))).subs(dyxi,6*eta/normal),density)

    # Bind the auxiliary source to parsed model and invariant formulas.
    alpha,T,X,Y = s.symbols('alpha T X Y')
    model_env = dict(c1=c1,c2=c2,alpha=alpha,r=radial,t=T,x=X,y=Y)
    model_text = read(BASE+'JacobianModel.lean')
    a8,b256 = [arithmetic(definition(model_text,n),model_env) for n in ['a8','b256']]
    equation = definition(model_text,'equation').replace('a8 c₁ c₂ α r t','AA').replace('b256 c₁ c₂ α r t','BB')
    integral = arithmetic(equation,dict(model_env,AA=a8,BB=b256))
    V = Y**2-X**3-a8*X/4116-b256/111132
    eq('integral model scale',integral,111132*V)
    source_env = {f'v{i}':w for i,w in enumerate([Y,T,c1,c2,radial,X])}
    Pnum = src('JacobianSource','sourceNumerator',source_env)
    require(definition(read(BASE+'JacobianSource.lean'),'source') ==
            'MvPolynomial.C (1/576 : ℂ)*sourceNumerator','Source scale')
    P = Pnum/576
    normalization = 143 if perturb == 'normalization' else 144
    eq('alpha-source normalization',P,-s.diff(V,alpha).subs(alpha,1)/(normalization*radial))
    eq('integral alpha-source identity',s.diff(integral,alpha).subs(alpha,1),-16003008*radial*P)
    eq('Jacobian source independent of Y',s.diff(P,Y))
    a,b,c,d,e,fff = coeffs = s.symbols('a b c d e f')
    inv_env = dict(zip('abcdef',coeffs))
    ct = read(LIB+'Cubic.lean')
    s4 = arithmetic(definition(ct,'s4Numerator'),inv_env)/3
    s6 = arithmetic(definition(ct,'s6Numerator'),inv_env)/27
    adot,bdot = s.diff(s4,a),s.diff(-s6/4,a)
    eq('aDot is zero',adot)
    eq('bDot formula',bdot,-(54*a*b*b*c*c+8*a*c*e**3)/4)
    cmap = {a:1+ratio**6,b:1+c1**6*ratio**6,c:1+c2**6*ratio**6,
            d:ratio**2*c1,e:ratio**2*c1*c2,fff:ratio**4*c2**2/7}
    Aalpha = dict(cmap); Aalpha[a] = alpha+ratio**6
    eq('model invariant A4 binding',a8.subs(T,radial*ratio**6)/4116,radial**4*s4.subs(Aalpha))
    eq('model invariant B6 binding',b256.subs(T,radial*ratio**6)/111132,-radial**6*s6.subs(Aalpha)/4)
    eq('mapped source R^5/144',P.subs(T,radial*ratio**6),radial**5*bdot.subs(cmap)/144)

    # First variations are algebraic jets, not a new derivation at alpha=1.
    x0,y0,eps = s.symbols('x0 y0 eps')
    uu = a*x0**3+b*y0**3+c+d*x0*x0*y0+e*y0*y0+fff*x0*x0
    g0 = s.diff(uu,x0); xdot = -x0**3/g0
    jenv = dict(zip(['coeff'+k for k in 'ABCDEF'],coeffs),x=x0,y=y0,cubicNormal=g0)
    jets = {}
    for name in ['aJet','bJet','cJet','dJet','eJet','fJet','xJet','yJet']:
        body = definition(read(BASE+'PhysicalCubicJets.lean'),name)
        require(body.startswith('(') and body.endswith(')'), 'Jet pair syntax: '+name)
        pair = body[1:-1].split(',')
        require(len(pair)==2, 'Jet pair length: '+name)
        value,dot = [arithmetic(w,jenv) for w in pair]
        jets[name] = value+eps*dot
    substituted = uu.subs(dict(zip([*coeffs,x0,y0],jets.values())), simultaneous=True)
    eq('source jet preserves cubic equation to first order',s.diff(substituted,eps).subs(eps,0))
    jet_normal = src('PhysicalCubicJets','gJet',jets)
    eq('source cubic normal jet value',jet_normal.subs(eps,0),g0)
    eq('source cubic normal jet variation',s.diff(jet_normal,eps).subs(eps,0),
       3*x0*x0-x0**3*s.diff(g0,x0)/g0)
    aw,aa,bb,xidot,gdot = s.symbols('aw adot bdot xidot gdot')
    dxi = 6*eta/normal
    deta = (3*xi**2+aw)*dxi/(2*eta)
    etadot = ((3*xi**2+aw)*xidot+aa*xi+bb)/(2*eta)
    dxidot = (6*etadot-gdot*dxi)/normal
    Dz = dxidot/(2*eta)-xidot*deta/(2*eta**2)
    eq('moving-map scalar identity given curve and jet identities',
       gdot/normal,(aa*xi+bb)/(2*eta**2)-normal*Dz/3)
    # Source and corrections use the same symbols; deliberate mutations fail here.
    N = s.Symbol('normalCorrectionDivergence')
    original = ratio**3*gdot/normal+N
    mapped_divergence = (aa*xi+bb)/(288*radial*eta**2)
    pulled_divergence = density*mapped_divergence
    moving_divergence = 0 if perturb == 'omit-moving' else ratio**3*normal*Dz/3
    normal_sign = 1 if perturb == 'normal-sign' else -1
    eq('physical three-term divergence = negative protected source',
       pulled_divergence+moving_divergence+normal_sign*N,-original)

    return {'status':'PASS','instance':'holdout-moving-branch','q':1,
            'upstream_commit':manifest['commit'],'notebook_base':manifest['notebook_base'],
            'field':'exact rational functions over Q; interpreted on the stated complex function-field chart',
            'variable_order':names,'target_order':['Y','T','c1','c2','R','X'],
            'input_files_hashed':len(manifest['files']),'checks_passed':len(checks),'checks':checks,
            'residue_density':'-144*R*v^3','alpha_source':'-V_alpha|alpha=1/(144*R)',
            'primitive_assembly':'pulled + (xiDot/(6*eta))*volumeVector - correctionVector',
            'reused':'prior exact covariant/differential audit; seed not rerun',
            'conditional_dependencies':['covariant curve and differential first variations; no full xiJet/etaJet evaluation',
                'function-field nonvanishing, embedding and Piola theorem',
                'accepted Jacobian primitive existence, trace and homogeneous clearing'],
            'not_executed':['Lean build/kernel replay','full syzygy expansion',
                'full xiJet/etaJet curve and differential first-variation evaluation','seed replay','trace/clearing replay'],
            'python':platform.python_version(),'sympy':s.__version__,
            'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'seconds':round(time.monotonic()-start,3)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--perturb',choices=['normalization','omit-moving','normal-sign'])
    args = parser.parse_args()
    result = run(args.perturb)
    text = json.dumps(result,indent=2,ensure_ascii=False)+'\n'
    if args.output: args.output.write_text(text,encoding='utf-8')
    print(text,end='')
