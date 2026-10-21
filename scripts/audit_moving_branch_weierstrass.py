"""Source-bound exact checks for one accepted moving-branch Weierstrass model.

This is not a Lean replay or a proof of the full certificate.  The input Lean
expressions are parsed as restricted arithmetic, never executed.  Incidence
derivatives are rebuilt from the model, not copied from the submitted matrix.
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

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / 'results/moving-branch-weierstrass-audit'
SOURCE = PACKET / 'inputs'
INSTANCE = 'data/holdout-moving-branch/'
LIB = 'formal/lean/HodgeComputer/Constructions/TransitiveCubic/'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return (SOURCE / path).read_text(encoding='utf-8')


def expression(text, symbols):
    """Parse integer/rational polynomial arithmetic from the pinned sources."""
    text = text.replace('^', '**').replace('c₁', 'c1').replace('c₂', 'c2').replace('α', 'alpha')
    text = re.sub(r':\s*K\b', '', text)
    tree = ast.parse(' '.join(text.split()), mode='eval')

    def walk(node):
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return sp.Integer(node.value)
        if isinstance(node, ast.Name) and node.id in symbols:
            return symbols[node.id]
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = walk(node.operand)
            return -value if isinstance(node.op, ast.USub) else value
        if isinstance(node, ast.BinOp):
            left, right = walk(node.left), walk(node.right)
            if isinstance(node.op, ast.Add): return left + right
            if isinstance(node.op, ast.Sub): return left - right
            if isinstance(node.op, ast.Mult): return left * right
            if isinstance(node.op, ast.Div):
                require(right.is_Integer and right != 0, 'Only nonzero integer divisors permitted')
                return left / right
            if isinstance(node.op, ast.Pow):
                require(right.is_Integer and 0 <= right <= 20, 'Unexpected exponent')
                return left ** right
        raise ValueError('Unsupported source arithmetic: ' + ast.dump(node))

    return walk(tree.body)


def definition(text, name):
    match = re.search(r'^def ' + re.escape(name) + r'\b[^\n]*?:=\s*', text, re.M)
    require(match is not None, 'Missing definition ' + name)
    tail = text[match.end():]
    return re.split(r'\n(?=(?:def|lemma|theorem|section|end|set_option|variable|/--|/-!))', tail, 1)[0].strip()


def matrix_definition(text, name):
    match = re.search(r'^def ' + name + r'\b.*?:= !\[(.*?)\n\]', text, re.M | re.S)
    require(match is not None, 'Missing matrix ' + name)
    rows = re.findall(r'!\[([0-9,\s]+)\]', match.group(1))
    result = [[int(x) for x in row.split(',')] for row in rows]
    require(len(result) == 13 and all(len(row) == 13 for row in result), 'Matrix shape')
    return sp.Matrix(result)


def mod5(value):
    n, d = sp.cancel(value).as_numer_denom()
    require(n.is_Integer and d.is_Integer and int(d) % 5, 'Illegal reduction mod 5')
    return int(n) * pow(int(d), -1, 5) % 5


def matrix_mod5(matrix):
    return matrix.applyfunc(mod5)


def rank_mod5(matrix):
    rows = [list(map(mod5, row)) for row in matrix.tolist()]
    rank = 0
    for col in range(matrix.cols):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][col]), None)
        if pivot is None: continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inv = pow(rows[rank][col], -1, 5)
        rows[rank] = [(v * inv) % 5 for v in rows[rank]]
        for i in range(len(rows)):
            if i != rank:
                factor = rows[i][col]
                rows[i] = [(a - factor*b) % 5 for a, b in zip(rows[i], rows[rank])]
        rank += 1
        if rank == len(rows): break
    return rank


def zero(poly, message):
    require(sp.expand(poly) == 0, message)


def geometric_dictionary(perturb):
    """Rebuild the covariants from Hessian/Jacobian determinants over Q."""
    a,b,c,d,e,f,x,y,z = generators = sp.symbols('a b c d e f x y z')
    symbols = {str(g):g for g in generators}
    U = expression(definition(read(LIB+'Cubic.lean'), 'cubic'), symbols)
    S = expression(definition(read(LIB+'Cubic.lean'), 's4Numerator'), symbols)
    text = read(LIB+'Covariants.lean')
    counts = {}
    def table(kind):
        terms = re.findall(r'^def '+kind+r'Coeff(\d)(\d)(\d).*? := (.+)$',text,re.M)
        require(bool(terms), 'No covariant coefficients: '+kind)
        require(len({(i,j,k) for i,j,k,_ in terms})==len(terms), 'Duplicate covariant coefficient')
        counts[kind]=len(terms)
        parsed={kind+'Coeff'+i+j+k:expression(value,symbols) for i,j,k,value in terms}
        polynomial=sp.Poly(sum(parsed[kind+'Coeff'+i+j+k]*x**int(i)*y**int(j)*z**int(k)
                              for i,j,k,_ in terms),generators)
        body=re.sub(r'('+kind+r'Coeff\d\d\d) a b c d e f',r'\1',definition(text,kind))
        require(sp.Poly(expression(body,dict(symbols,**parsed)),generators)==polynomial,
                'Actual covariant function does not assemble coefficient labels: '+kind)
        return polynomial
    H, Theta, J = [table(k) for k in ['H','Theta','J']]
    hessian = sp.hessian(U,(x,y,z))
    require(sp.Poly(sp.Rational(3,8)*hessian.det(),generators)==H, 'Hessian dictionary failed')
    grad_H = sp.Matrix([sp.diff(H.as_expr(),w) for w in (x,y,z)])
    theta_raw = -(grad_H.T*hessian.adjugate()*grad_H)[0]/36
    correction = 3*S*U*H.as_expr()
    expected_theta = sp.Poly(theta_raw-correction,generators)
    if perturb=='theta-raw': Theta=sp.Poly(theta_raw,generators)
    require(expected_theta==Theta, 'Normalized Theta dictionary failed')
    require(sp.Poly(correction,generators)!=sp.Poly(0,generators), 'Off-curve correction unexpectedly zero')
    jacobian = sp.Matrix([[sp.diff(value,w) for w in (x,y,z)]
                          for value in (U,H.as_expr(),Theta.as_expr())])
    require(sp.Poly(jacobian.det(method='domain-ge')/9,generators)==J, 'Jacobian dictionary failed')
    u,h,theta,j = [v.subs(z,1) for v in (U,H.as_expr(),Theta.as_expr(),J.as_expr())]
    cross = lambda p,q: sp.diff(p,x)*sp.diff(q,y)-sp.diff(p,y)*sp.diff(q,x)
    zero(h*cross(u,theta)-2*theta*cross(u,h)+3*j-u*cross(h,theta), 'Relative differential identity')
    point={g:1 for g in generators}
    return {'field':'Q[a,b,c,d,e,f,x,y,z]', 'coefficient_blocks':counts,
            'actual_function_assemblies_checked':['H','Theta','J'],
            'expanded_monomials':{'H':len(H.terms()),'Theta':len(Theta.terms()),'J':len(J.terms())},
            'H_identity':'H = (3/8) det Hess(U)',
            'Theta_identity':'Theta_raw = -(grad H)^T adj(Hess U) (grad H)/36; Theta = Theta_raw - 9*s4*U*H',
            'J_identity':'J = det Jac(U,H,Theta)/9',
            'relative_differential_identity':'H*(Ux*Theta_y-Uy*Theta_x)-2*Theta*(Ux*Hy-Uy*Hx)+3*J = U*(Hx*Theta_y-Hy*Theta_x)',
            'off_curve_example':{'all_nine_variables':1,'U':int(U.subs(point)),
                                 'Theta_raw_minus_Theta':int(correction.subs(point))},
            'scope':'Exact polynomial identities; on-curve differential consequence requires U=0 and nonzero Ux,H,J in characteristic0. Weierstrass syzygy not replayed.'}


def audit(perturb=None):
    started = time.monotonic()
    manifest = json.loads((PACKET / 'inputs.json').read_text(encoding='utf-8'))
    for item in manifest['files']:
        data = (SOURCE / item['path']).read_bytes()
        require(hashlib.sha256(data).hexdigest() == item['sha256'], 'Input hash mismatch: ' + item['path'])
        git_blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        require(git_blob == item['git_blob'], 'Git blob mismatch: ' + item['path'])

    covariant_dictionary=geometric_dictionary(perturb)

    X0, X1, X2, Y0, Y1, Y2 = physical = sp.symbols('X0 X1 X2 Y0 Y1 Y2')
    c1, c2, alpha, R, T, v, x, y, z, W = sp.symbols('c1 c2 alpha R T v x y z W')
    names = dict(zip(('X0','X1','X2','Y0','Y1','Y2'), physical))
    record = read(INSTANCE + 'instance.rec')
    fields = dict(re.findall(r'^(F|A|q): (.+)$', record, re.M))
    F, A, q = expression(fields['F'], names), expression(fields['A'], names), int(fields['q'])
    provenance = json.loads(read(INSTANCE + 'provenance.json'))
    require(provenance['variables'] == list(names), 'Physical variable order')
    require(q == 1, 'Pole order changed')
    physical_alpha = F + (alpha - 1) * X0**6
    paired = {Y0: v*X0, Y1: c1*v*X1, Y2: c2*v*X2}
    paired_F = sp.Poly(sp.expand(physical_alpha.subs(paired)), X0, X1, X2)
    cubic = sp.Integer(0)
    for powers, coefficient in paired_F.terms():
        require(all(e % 2 == 0 for e in powers) and sum(powers) == 6, 'Invalid paired-sign cubic term')
        cubic += coefficient * x**(powers[0]//2) * y**(powers[1]//2) * z**(powers[2]//2)
    C = sp.Poly(cubic, x, y, z)
    basis = [x**3, y**3, z**3, x*x*y, y*y*z, x*x*z]
    coefficients = [C.coeff_monomial(m) for m in basis]
    zero(cubic - sum(a*m for a, m in zip(coefficients, basis)), 'Unaccounted cubic terms')
    zero(physical_alpha.subs(paired) - cubic.subs({x:X0**2,y:X1**2,z:X2**2}), 'Source to cubic')
    zero(A.subs(paired) - v**3*X0**6, 'Protected source is not v^3 times alpha derivative')

    symbols = dict(zip('abcdef', coefficients))
    invariant_text = read(LIB + 'Cubic.lean')
    s4 = sp.expand(expression(definition(invariant_text, 's4Numerator'), symbols) / 3)
    s6 = sp.expand(expression(definition(invariant_text, 's6Numerator'), symbols) / 27)

    def homogenize(poly, weight):
        result = 0
        for (power,), coefficient in sp.Poly(poly, v).terms():
            require(power % 6 == 0 and power//6 <= weight, 'Not polynomial under T=R*v^6')
            result += coefficient * T**(power//6) * R**(weight-power//6)
        return sp.expand(result)

    A4, B6 = homogenize(s4, 4), homogenize(-s6/4, 6)
    environment = {'c1':c1,'c2':c2,'alpha':alpha,'r':R,'t':T,'x':x,'y':W}
    model_text = read(INSTANCE + 'JacobianModel.lean')
    a8 = expression(definition(model_text, 'a8'), environment)
    b256 = expression(definition(model_text, 'b256'), environment)
    eq_text = definition(model_text, 'equation')
    eq_text = eq_text.replace('a8 c₁ c₂ α r t', 'modelA').replace('b256 c₁ c₂ α r t', 'modelB')
    integral = expression(eq_text, dict(environment, modelA=a8, modelB=b256))
    model_scale = sp.expand(integral).coeff(W, 2)
    zero(a8 - 4116*A4, 'A4 invariant scale mismatch')
    zero(b256 - 111132*B6, 'B6 invariant scale mismatch')
    V = W**2 - x**3 - A4*x - B6
    zero(integral - model_scale*V, 'Integral equation is not its declared multiple of V')
    require(model_scale == 111132, 'Unexpected integral scale')

    source_text = read(INSTANCE + 'JacobianSource.lean')
    source_expression = definition(source_text, 'sourceNumerator')
    source_environment = {'R':R,'T':T,'c1':c1,'c2':c2,'X':x,'Y':W}
    for i, name in enumerate(['Y','T','c1','c2','R','X']):
        source_expression = re.sub(r'\bv '+str(i)+r'\b', name, source_expression)
    source_numerator = expression(source_expression, source_environment)
    require('MvPolynomial.C (1/576 : ℂ)*sourceNumerator' in definition(source_text, 'source'), 'Source scale changed')
    source = source_numerator / 576
    expected_source = sp.cancel(-sp.diff(V, alpha).subs(alpha, 1) / (144*R))
    require(sp.denom(expected_source).is_Integer, 'Alpha source is not polynomial')
    zero(source - expected_source, 'Alpha source normalization mismatch')
    zero(sp.diff(integral, alpha).subs(alpha,1) + 16003008*R*source, 'Integral alpha source scale')

    seed_text = read(INSTANCE + 'JacobianSeed.lean')
    seed = [expression(definition(seed_text, n), {'X':T}) for n in ['r','x','y']]
    fixed = {c1:1,c2:1,alpha:1}
    seed_substitution = {R:seed[0],x:seed[1],W:seed[2]}
    E = sp.expand(integral.subs(fixed))
    if perturb == 'coupling':
        E += R**4*x  # another degree-six term; seed must fail, not silently change the target
    restricted = sp.Poly(sp.expand(E.subs(seed_substitution)), T)
    require(restricted.degree() <= 12, 'Incidence degree exceeds 12')
    residual = [mod5(restricted.nth(i)) for i in range(13)]
    require(not any(residual), 'Seed incidence failed')
    gradient = [sp.Poly(sp.expand(sp.diff(E, variable).subs(seed_substitution)), T) for variable in [R,x,W]]
    slots = [(0,1),(0,2)] + [(1,k) for k in range(1,5)] + [(2,k) for k in range(7)]
    # All13 equations, coefficients T^0,...,T^12. Fixed endpoints are R0 and X0.
    J = sp.Matrix(13,13,lambda i,j: mod5(gradient[slots[j][0]].nth(i-slots[j][1])) if i >= slots[j][1] else 0)
    submitted_J = matrix_definition(seed_text, 'coefficientJacobian')
    inverse = matrix_definition(seed_text, 'inverseJacobian')
    if perturb == 'matrix': submitted_J[0,0] = (submitted_J[0,0]+1)%5
    require(J == submitted_J, 'Reconstructed Jacobian differs from submitted matrix')
    if perturb == 'inverse': inverse[0,0] = (inverse[0,0]+1)%5
    require(matrix_mod5(J*inverse) == sp.eye(13), 'Right inverse failed')
    require(matrix_mod5(inverse*J) == sp.eye(13), 'Left inverse failed')
    require(rank_mod5(J) == 13, 'Coefficient Jacobian is singular')

    # Four genuine external parameters c1,c2,R0,X0. Differentiate before specialization.
    external_polys = [sp.Poly(sp.expand(sp.diff(integral,c).subs(fixed).subs(seed_substitution)),T) for c in [c1,c2]] + gradient[:2]
    B = sp.Matrix(13,4,lambda i,j: mod5(external_polys[j].nth(i)))
    lift = matrix_mod5(-inverse*B)
    require(matrix_mod5(J*lift+B) == sp.zeros(13,4), 'External-parameter tangent lift failed')
    require(rank_mod5(J.row_join(B)) == 13, 'Full linearized incidence rank')

    # A polynomial normal: coefficient-Jacobian inverse applied to constant polynomial1.
    normal = [0,0,0]
    for j, (coordinate, degree) in enumerate(slots): normal[coordinate] += inverse[j,0]*T**degree
    normal_identity = sp.Poly(sp.expand(sum(g.as_expr()*n for g,n in zip(gradient,normal))-1),T)
    require(all(mod5(c)==0 for c in normal_identity.all_coeffs()), 'Polynomial normal identity failed')

    return {
        'status':'PASS', 'upstream_commit':manifest['commit'], 'instance':'holdout-moving-branch',
        'covariant_dictionary':covariant_dictionary,
        'field_exact':'Q for symbolic identities; F_5 for seed, matrix, tangent and normal checks',
        'q':q, 'variable_order':list(names), 'input_files_checked':len(manifest['files']),
        'cubic_coefficients':dict(zip('abcdef',map(str,coefficients))),
        'invariant_scales':{'a8_over_A4':4116,'b256_over_B6':111132,'integral_over_V':111132},
        'alpha_source':str(sp.factor(source)), 'alpha_source_scale':16003008,
        'seed':[str(s) for s in seed], 'incidence_coefficients_mod5':residual,
        'coefficient_order':['R1','R2','X1','X2','X3','X4']+['Y'+str(i) for i in range(7)],
        'equation_order':['T^'+str(i) for i in range(13)],
        'matrix_mod5':J.tolist(), 'rank':rank_mod5(J),'matched_matrix_entries':169,
        'integral_determinant_mod5':mod5(J.det()),
        'normalized_determinant_mod5':mod5(J.det()/model_scale**13),
        'inverse_products_checked':['J*inverse=I','inverse*J=I'],
        'external_parameter_order':['c1','c2','R0','X0'], 'external_matrix_mod5':B.tolist(),
        'tangent_lift_mod5':lift.tolist(), 'full_matrix_shape':[13,17], 'full_rank':13,
        'normal_polynomials_mod5':[str(sp.Poly(n,T,modulus=5).as_expr()) for n in normal],
        'normal_identity':'grad(integral_equation) dot normal = 1 in F_5[T]',
        'limits':['Not a Lean/kernel replay','No full moving-map, trace, dominance or clearing proof replay',
                  'Not a fresh certificate or acceptance result','Full Weierstrass covariant syzygy not independently replayed here'],
        'versions':{'python':platform.python_version(),'sympy':sp.__version__},
        'elapsed_seconds':round(time.monotonic()-started,3)}


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--perturb',choices=['coupling','matrix','inverse','theta-raw'])
    args=parser.parse_args()
    result=audit(args.perturb)
    encoded=json.dumps(result,indent=2,default=lambda n:int(n))+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(encoded,encoding='utf-8')
    print(encoded)
