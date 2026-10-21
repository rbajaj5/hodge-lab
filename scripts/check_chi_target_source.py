"""Source-bound relative-primitive pilot; not an ambient certificate exclusion."""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import platform
import re
import time
import sympy as s

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/chi-target-source'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def arithmetic(text, symbols):
    """Parse protected polynomial arithmetic without executing source text."""
    def walk(node):
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return s.Integer(node.value)
        if isinstance(node, ast.Name) and node.id in symbols:
            return symbols[node.id]
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            value = walk(node.operand)
            return -value if isinstance(node.op, ast.USub) else value
        if isinstance(node, ast.BinOp):
            left, right = walk(node.left), walk(node.right)
            if isinstance(node.op, ast.Add): return left + right
            if isinstance(node.op, ast.Sub): return left - right
            if isinstance(node.op, ast.Mult): return left * right
            if isinstance(node.op, ast.Div) and right.is_Rational and right != 0:
                return left / right
            if isinstance(node.op, ast.Pow) and right.is_Integer and right >= 0:
                return left ** right
        raise ValueError('Unsupported protected polynomial syntax')
    return walk(ast.parse(text, mode='eval').body)


def run(mutation=None):
    started = time.monotonic()
    checks = []
    def exact(name, value):
        require(s.cancel(value) == 0, name)
        checks.append(name)
    def condition(name, ok):
        require(ok, name)
        checks.append(name)
    pins = json.loads((OUT/'inputs.json').read_text(encoding='utf-8'))
    for item in pins['files']:
        data = (OUT/'inputs'/item['path']).read_bytes()
        require(hashlib.sha256(data).hexdigest() == item['sha256'], 'Input SHA256 mismatch')
        require(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == item['git_blob'], 'Input Git blob mismatch')
    folder = OUT/'inputs/data/one-reflection-skew'
    provenance = json.loads((folder/'provenance.json').read_text(encoding='utf-8'))
    names = ['X0', 'X1', 'X2', 'Y0', 'Y1', 'Y2']
    condition('protected variable order', provenance['variables'] == names)
    X = s.symbols(' '.join(names))
    raw = (folder/'instance.rec').read_text(encoding='utf-8')
    def field(label):
        match = re.search(r'^'+label+r': (.*(?:\n  [^\n]+)*)', raw, flags=re.M)
        require(match is not None, 'Missing protected '+label)
        return ' '.join(match.group(1).splitlines())
    F, A = (arithmetic(field(k), dict(zip(names, X))) for k in ['F', 'A'])
    q = int(field('q'))
    record = json.loads((folder/'record.json').read_text(encoding='utf-8'))
    for key, poly in [('F', F), ('A', A)]:
        structured = sum(s.Rational(c)*s.prod(v**e for v,e in zip(X, exps)) for c,exps in record[key]['terms'])
        exact('instance.rec matches structured '+key, poly-structured)
    condition('protected q=1', q == record['q'] == 1)
    catalogue = json.loads((OUT/'inputs/data/index.json').read_text(encoding='utf-8'))
    target = next(v for v in catalogue['records'] if v['id'] == 'one-reflection-skew')
    condition('pinned target is open', target['status'] == 'open' and not target['certificateAvailable'])
    r,w,t,x,z,U = s.symbols('r w t x z U')
    a,b,c,d = s.symbols('a b c d')
    mapping = dict(zip(X, (x,r*x,w*x,1,t,z)))
    transformed = s.expand(F.subs(mapping, simultaneous=True))
    even = s.Poly(transformed-z**6, x)
    condition('equation descends through x squared', all(e[0] % 2 == 0 for e,_ in even.terms()))
    physical_P = s.expand(sum(co*U**(e[0]//2) for e,co in even.terms()))
    coefficients = [s.expand(s.Poly(physical_P,U).coeff_monomial(U**j)) for j in [3,2,1,0]]
    expected = [1+r**6+w**6, t*(r+r**3*w), r*t*(1-t**2)/7, 1+t**6]
    if mutation == 'drop-skew': expected[2] = 0
    for label, got, want in zip('abcd',coefficients,expected):
        exact('protected coefficient '+label, got-want)
    exact('protected source maps to x cubed', A.subs(mapping,simultaneous=True)-x**3)
    jac = s.Matrix([x,r*x,w*x,t,z]).jacobian((x,r,w,t,z)).det()
    exact('physical five-coordinate Jacobian',jac-x**2)
    exact('full source descends through U=x squared',-x**3*jac/(2*x)+x**4/2)
    P = a*U**3+b*U**2+c*U+d
    G = z**6+P
    source_coefficient = -U**2/(2*G**2)
    primitive_fourform = U**2/(12*z**5*G)
    simple_pole = 5*U**2/(12*z**6*G)
    exact('signed pole reduction',source_coefficient-s.diff(primitive_fourform,z)-simple_pole)
    omega = 5*U**2/(72*z**11)
    exact('residue normalization 5/72',simple_pole*G/s.diff(G,z)-omega)
    B = s.Function('B')(U)
    derivative = s.diff(B/z**5,U)-s.diff(P,U)/(6*z**5)*s.diff(B/z**5,z)
    L = 5*s.diff(P,U)*B-6*P*s.diff(B,U)
    if mutation == 'drop-connection': L = -6*P*s.diff(B,U)
    exact('weighted derivative operator',s.expand(6*z**11*derivative-L).subs(z**6,-P))
    exact('source character-one representation',s.rem(s.fraction(s.cancel(omega-s.Rational(5,72)*U**2*z/P**2))[0],z**6+P,z))
    condition('matching source and primitive deck characters',(-11) % 6 == (-5) % 6 == 1)
    for j in range(6):
        f = s.Function('f'+str(j))(U)
        # 6*z^5 times the derivative is polynomial in z; reduce by z^6+P.
        residual = 6*z**5*s.diff(f*z**j,U)-s.diff(P,U)*s.diff(f*z**j,z)
        residual -= 6*z**5*(s.diff(f,U)+j*s.diff(P,U)*f/(6*P))*z**j
        numerator = s.fraction(s.cancel(residual))[0]
        exact('derivation preserves basis component '+str(j),s.rem(numerator,z**6+P,z))
    n,k = s.symbols('n k', integer=True)
    exact('polynomial leading factor never zero at integer degree',s.Mod(15-6*n,6)-3)
    exact('root-pole leading factor never zero at integer order',s.Mod(6*k+5,6)-5)
    positive_B = 1/(36*a)
    if mutation == 'primitive-sign': positive_B = -positive_B
    constant_residual = s.expand(5*s.diff(P,U)*positive_B-s.Rational(5,12)*U**2)
    exact('constant candidate residual',constant_residual-(5*b*U/(18*a)+5*c/(36*a)))
    exact('physical b factors',coefficients[1]-r*t*(1+r**2*w))
    exact('physical c factors',coefficients[2]-r*t*(1-t**2)/7)
    samples = []
    for label,point,should_solve in [('generic_sample',{r:1,w:1,t:2},False),('special_control',{r:0,w:1,t:2},True)]:
        Q = physical_P.subs(point)
        delta = s.discriminant(Q,U)
        condition(label+' squarefree cubic',s.degree(Q,U)==3 and delta != 0)
        sample = {'label':label,'point':{str(v):int(e) for v,e in point.items()},'P':str(Q),'discriminant':str(delta),'degree_tests':[]}
        rhs = s.Rational(5,12)*U**2
        for bound in [0,2,4,8]:
            columns = [s.Poly(s.expand(5*s.diff(Q,U)*U**j-6*Q*j*U**(j-1)) if j else 5*s.diff(Q,U),U) for j in range(bound+1)]
            matrix = s.Matrix([[p.coeff_monomial(U**i) for p in columns] for i in range(bound+3)])
            vector = s.Matrix([rhs.coeff(U,i) for i in range(bound+3)])
            rank, augmented = matrix.rank(), matrix.row_join(vector).rank()
            condition(label+' full column rank degree '+str(bound),rank==bound+1)
            condition(label+' expected consistency degree '+str(bound),(rank==augmented)==should_solve)
            item = {'B_degree_bound':bound,'matrix_shape':list(matrix.shape),'rank':rank,'augmented_rank':augmented}
            if not should_solve:
                dual = next(v for v in matrix.T.nullspace() if (v.T*vector)[0] != 0)
                dual = dual/(dual.T*vector)[0]
                condition(label+' exact left dual degree '+str(bound),dual.T*matrix==s.zeros(1,bound+1) and (dual.T*vector)[0]==1)
                item['coefficient_row_dual'] = [str(v) for v in dual]
                item['dual_convention'] = 'Rows U^0,...,U^(bound+2); lambda^T M=0, lambda^T rhs=1'
            else:
                solution = s.Matrix([1/(36*s.Poly(Q,U).LC())]+[0]*bound)
                condition(label+' exact primitive degree '+str(bound),matrix*solution==vector)
                item['B_coefficients']=[str(v) for v in solution]
            sample['degree_tests'].append(item)
        sample['constant_candidate_residual'] = str(s.factor((5*s.diff(P,U)/(36*a)-rhs).subs(dict(zip((a,b,c,d),[v.subs(point) for v in coefficients])))))
        samples.append(sample)
    exact('generic sample discriminant',s.Rational(samples[0]['discriminant'])+s.Rational(361978181,343))
    exact('special sample discriminant',s.Rational(samples[1]['discriminant'])+456300)
    # Exterior algebra sign: d(-r*dU/U wedge dw wedge dt)=+dU/U wedge dr wedge dw wedge dt.
    exact('base derivative counterexample coefficient',-s.diff(-r/U,r)-1/U)
    return {'status':'PASS','scope':'Actual protected source to relative genus-four differential; relative exactness criterion and bounded matrix checks, not an ambient Hodge exclusion',
            'input_manifest_sha256':hashlib.sha256((OUT/'inputs.json').read_bytes()).hexdigest(),
            'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'upstream_commit':pins['upstream_commit'],'variable_order':names,'q':q,'F':str(F),'A':str(A),
            'coefficient_field':'Q(r,w,t), characteristic zero; argument also over C(r,w,t)',
            'coefficients':dict(zip('abcd',map(str,coefficients))), 'relative_curve':'z^6=-P(U)',
            'relative_source':'5*U^2/(72*z^11) dU','operator':'5*Pprime*B-6*P*Bprime=5*U^2/12',
            'required_open':['a != 0','discriminant(P) != 0','x != 0 on square-coordinate chart','z != 0 on residue chart'],
            'general_proof':'Irreducibility and derivative-preserved degree-six basis reduce any relative primitive to B/z^5. Pole orders force B polynomial; coefficient a(15-6n) forces B constant. Exactness iff b=c=0, with B=1/(36a). See note for proof, not inferred from finite rank tests.',
            'genus_argument':{'cover_degree':6,'finite_branch_contribution':15,'infinity_branch_contribution':3,'two_genus_minus_two':6,'genus':4},
            'checks_passed':len(checks),'checks':checks,'samples':samples,
            'ambient_nonexistence_claimed':False,'hodge_certificate_constructed':False,
            'versions':{'python':platform.python_version(),'sympy':s.__version__},'elapsed_seconds':round(time.monotonic()-started,6)}


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--mutation',choices=['drop-skew','drop-connection','primitive-sign'])
    args=parser.parse_args()
    try:
        result=run(args.mutation)
        if not args.mutation:
            (OUT/'replay.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
        print(json.dumps({'status':'PASS','checks':result['checks_passed'],'seconds':result['elapsed_seconds']}))
    except Exception as error:
        print('FAIL: '+str(error))
        raise SystemExit(1)
