"""Exact, source-bound affine covariant jets; no Lean or existence-proof replay.

Only restricted arithmetic is parsed from the pinned Lean definitions. Native
FLINT expands full polynomials over Q, including all six cubic coefficients.
Every required identity raises on failure (also under python -O).
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

import flint
from flint import fmpq, fmpq_mpoly_ctx
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / 'results/covariant-jet-audit'
NAMES = ('c', 'a', 'b', 'd', 'e', 'f', 'x', 'y')
CTX = fmpq_mpoly_ctx.get(NAMES, ordering='lex')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def definition(text, name):
    m = re.search(r'^def ' + re.escape(name) + r'\b[^\n]*?:=\s*', text, re.M)
    require(m is not None, 'Missing definition: ' + name)
    return re.split(r'\n(?=(?:def|lemma|theorem|section|end|set_option|variable|/--|/-!|@\[))',
                    text[m.end():], 1)[0].strip()


class Dual:
    """A pair (v,n), representing v + epsilon*n/G for polynomial evaluation.

    The same product rules apply to abstract rational jets with G=1. Inversion
    is used only there, never to expand a giant multivariate rational function.
    """
    def __init__(self, value, delta):
        self.v, self.n = value, delta

    def coerce(self, other):
        return other if isinstance(other, Dual) else Dual(self.v*0+other, self.n*0)

    def __add__(self, other):
        other = self.coerce(other)
        return Dual(self.v+other.v, self.n+other.n)

    __radd__ = __add__

    def __neg__(self):
        return Dual(-self.v, -self.n)

    def __sub__(self, other):
        return self + -self.coerce(other)

    def __rsub__(self, other):
        return self.coerce(other) + -self

    def __mul__(self, other):
        other = self.coerce(other)
        return Dual(self.v*other.v, self.n*other.v+self.v*other.n)

    __rmul__ = __mul__

    def __truediv__(self, scalar):
        return Dual(self.v/scalar, self.n/scalar)

    def __pow__(self, exponent):
        require(type(exponent) is int and exponent >= 0, 'Dual exponent')
        if exponent == 0:
            return self.coerce(1)
        return Dual(self.v**exponent, exponent*self.v**(exponent-1)*self.n)

    def inverse(self):
        return Dual(1/self.v, -self.n/self.v**2)


def expression(text, env, rational=fmpq):
    text = re.sub(r':\s*(?:K|FunctionField)\b', '', text)
    text = re.sub(r'(\w+)⁻¹', r'inv(\1)', text).replace('^', '**')
    text = re.sub(r'\binl\s*\(', '(', text)

    def walk(n):
        if isinstance(n, ast.Constant) and type(n.value) is int:
            return n.value
        if isinstance(n, ast.Name) and n.id in env:
            return env[n.id]
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.USub, ast.UAdd)):
            return -walk(n.operand) if isinstance(n.op, ast.USub) else walk(n.operand)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'inv' and len(n.args)==1:
            v = walk(n.args[0])
            return v.inverse() if isinstance(v, Dual) else 1/v
        if isinstance(n, ast.BinOp):
            a, b = walk(n.left), walk(n.right)
            if isinstance(n.op, ast.Add): return a+b
            if isinstance(n.op, ast.Sub): return a-b
            if isinstance(n.op, ast.Mult): return a*b
            if isinstance(n.op, ast.Div):
                require(type(b) is int and b != 0, 'Only nonzero integer divisors')
                return a/rational(b)
            if isinstance(n.op, ast.Pow):
                require(type(b) is int and 0 <= b <= 30, 'Polynomial exponent')
                return a**b
        raise ValueError('Unsupported source arithmetic: '+ast.dump(n))

    return walk(ast.parse(' '.join(text.split()), mode='eval').body)


def sparse(poly):
    return [[list(map(int,mon)), str(coef)] for mon, coef in sorted(poly.to_dict().items())]


def polynomial_record(poly):
    rows = sparse(poly)
    return {'terms': len(rows), 'total_degree': max((sum(r[0]) for r in rows), default=-1),
            'sha256': sha(json.dumps(rows, separators=(',', ':')).encode('utf-8'))}


def run(perturb=None):
    started = time.monotonic()
    manifest = json.loads((PACKET/'inputs.json').read_text(encoding='utf-8'))
    sources = {}
    for rec in manifest['files']:
        raw = (ROOT/rec['local_path']).read_bytes()
        require(sha(raw)==rec['sha256'], 'SHA256 mismatch: '+rec['path'])
        blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        require(blob==rec['git_blob'], 'Git blob mismatch: '+rec['path'])
        sources[Path(rec['path']).name] = raw.decode('utf-8')
    for rec in manifest['reused_receipts']:
        # Git's historical JSON text files may be checked out with CRLF on
        # Windows. Pin their committed LF bytes without changing old files.
        raw = (ROOT/rec['path']).read_bytes().replace(b'\r\n',b'\n')
        require(sha(raw)==rec['sha256'], 'Reused receipt changed')

    checks = []
    def zero(label, residual):
        require(not residual, label+' failed')
        checks.append(label)

    def symbolic(label, residual):
        require(sp.cancel(residual)==0, label+' failed')
        checks.append(label)

    env = dict(zip(NAMES, CTX.gens()))
    env['z'] = CTX.constant(1)
    cubic, cov, jets = (sources[n] for n in ('Cubic.lean','Covariants.lean','PhysicalCubicJets.lean'))
    u = expression(definition(cubic,'cubic'),env)
    sn = expression(definition(cubic,'s4Numerator'),env)
    tn = expression(definition(cubic,'s6Numerator'),env)
    g, uy, x = u.derivative('x'), u.derivative('y'), env['x']
    P = lambda r: g*r.derivative('a')-x**3*r.derivative('x')
    L = lambda r: g*r.derivative('y')-uy*r.derivative('x')
    zero('P(U)=0', P(u))
    zero('L(U)=0', L(u))
    zero('U monic linear in c', u.derivative('c')-1)

    # Parse the actual eight input jet pairs; expected directions are checked
    # symbolically before transporting their common-G numerators to FLINT.
    symbols = dict(zip(NAMES,sp.symbols(' '.join(NAMES))))
    gs = sp.Symbol('G', nonzero=True)
    pair_env = {**symbols, 'cubicNormal':gs}
    pair_env.update({'coeff'+v.upper():symbols[v] for v in 'abcdef'})
    denv = {'z':Dual(env['z'],CTX.constant(0))}
    for v in 'abcdefxy':
        raw = definition(jets,v+'Jet')
        require(raw.startswith('(') and raw.endswith(')'), 'Input jet pair shape')
        parts = raw[1:-1].split(',')
        require(len(parts)==2, 'Input jet pair arity')
        # Only xJet divides by the named cubic normal. This conversion is
        # deliberately narrow and rejects any unreviewed change of syntax.
        delta = parts[1].replace('/cubicNormal','*ginv')
        val = expression(parts[0],pair_env,sp.Integer)
        dot = expression(delta,{**pair_env,'ginv':1/gs},sp.Integer)
        expected = 1 if v=='a' else (-symbols['x']**3/gs if v=='x' else 0)
        symbolic(v+'Jet value', val-symbols[v])
        symbolic(v+'Jet direction', dot-expected)
        numer = sp.cancel(gs*dot)
        poly = expression(str(numer),{**env,'G':g})
        if perturb=='cubic-path' and v=='x': poly = -poly
        denv[v] = Dual(env[v],poly)

    uj = expression(definition(cubic,'cubic'),denv)
    zero('actual cubic jet value',uj.v-u)
    zero('actual cubic jet tangent',uj.n)

    def table(name, values):
        matches = re.findall(r'^def '+name+r'Coeff(\d)(\d)(\d).*? := (.+)$',cov,re.M)
        require(matches, 'Missing coefficient table '+name)
        coeffs = {name+'Coeff'+i+j+k:expression(body,values) for i,j,k,body in matches}
        if perturb=='j-coefficient' and name=='J':
            key = sorted(coeffs)[0]
            coeffs[key] = coeffs[key]+1
        assembled = re.sub(r'('+name+r'Coeff\d\d\d) a b c d e f',r'\1',definition(cov,name))
        return expression(assembled,{**values,**coeffs})

    values = [table(n,env) for n in ('H','Theta','J')]
    duals = [table(n,denv) for n in ('H','Theta','J')]
    h,q,j = values
    for name,poly,dual in zip(('h','q','j'),values,duals):
        function = {'h':'H','q':'Theta','j':'J'}[name]
        require(' '.join(definition(jets,name+'Jet').split())==
            function+' aJet bJet cJet dJet eJet fJet xJet yJet 1', 'Covariant jet assembly')
        zero(name+'Jet value',dual.v-poly)
        zero(name+'Jet automatic first variation',dual.n-P(poly))
    snj = expression(definition(cubic,'s4Numerator'),denv)
    tnj = expression(definition(cubic,'s6Numerator'),denv)
    zero('SN automatic first variation',snj.n-P(sn))
    zero('TN automatic first variation',tnj.n-P(tn))
    zero('SN_a=0',sn.derivative('a'))
    zero('bDot formula',tn.derivative('a')-27*(54*env['a']*env['b']**2*env['c']**2+8*env['a']*env['c']*env['e']**3))
    input_jets = {v+'Jet':denv[v] for v in 'abcdefxy'}
    gj = expression(definition(jets,'gJet'),input_jets)
    zero('gJet value',gj.v-g)
    zero('gJet automatic first variation',gj.n-P(g))

    # Evaluate the actual inverse/quotient definitions on small abstract jets.
    # Their delta values are subsequently replaced by the full P(H,Q,J)/G.
    hs,qs,js,hd,qd,jd = sp.symbols('H Q J Hd Qd Jd', nonzero=True)
    abstract = {'hJet':Dual(hs,hd),'qJet':Dual(qs,qd),'jJet':Dual(js,jd)}
    abstract['half'] = Dual(sp.Rational(1,2),sp.Integer(0))
    symbolic('half source',expression(definition(jets,'half'),{},sp.Integer)-sp.Rational(1,2))
    xij = expression(definition(jets,'xiJet'),abstract,sp.Integer)
    etaj = expression(definition(jets,'etaJet'),abstract,sp.Integer)
    symbolic('xiJet quotient value',xij.v-qs/hs**2)
    symbolic('xiJet quotient variation',xij.n-(hs*qd-2*qs*hd)/hs**3)
    symbolic('etaJet quotient value',etaj.v+js/(2*hs**3))
    symbolic('etaJet quotient variation',etaj.n+(hs*jd-3*js*hd)/(2*hs**4))
    for name,numerator,scale in [('sJet','s4Numerator',3),('tJet','s6Numerator',27)]:
        body = definition(jets,name)
        body = body.replace('TransitiveCubic.'+numerator+' aJet bJet cJet dJet eJet fJet','N')
        ns,nds = sp.symbols('N Nd')
        parsed = expression(body,{'N':Dual(ns,nds)},sp.Integer)
        symbolic(name+' scale value',parsed.v-ns/scale)
        symbolic(name+' scale variation',parsed.n-nds/scale)
    ts,td = sp.symbols('t td')
    bj = expression(definition(jets,'bWeierstrassJet'),{**abstract,'tJet':Dual(ts,td)},sp.Integer)
    symbolic('bWeierstrassJet value',bj.v+ts/4)
    symbolic('bWeierstrassJet variation',bj.n+td/4)

    ph,pq,pj = (d.n for d in duals)
    nx = h*pq-2*q*ph
    ne = h*pj-3*j*ph
    kg = gj.n
    m = h*L(q)-2*q*L(h)
    c = 27*j**2-108*q**3-36*sn*q*h**4+tn*h**6
    nc = 54*j*ne-(324*q**2+36*sn*h**4)*nx-36*snj.n*q*h**5+tnj.n*h**7
    kd = g*h*L(nx)-h*nx*L(g)-3*g*nx*L(h)
    nd = kd+kg*h*m+3*g*ne
    nj = -j*kd+g*m*ne+3*j**2*kg*h
    nm = 54*kg*j**2+g**2*tn.derivative('a')*h**6-18*(g*j*L(nx)-nx*j*L(g)-nx*g*L(j))

    zero('curve variation chain rule',nc-(h*P(c)-6*c*ph))
    zero('differential variation chain rule',nd-g*(h*P(m+3*j)-3*(m+3*j)*ph))
    zero('source differential-jet conversion',nj-(-j*nd+(m+3*j)*(g*ne+kg*h*j)))
    zero('[P/G,L/G] numerator on x',
         -P(uy)*g+uy*P(g)+L(x**3)*g-x**3*L(g))

    # Read the actual ten-term RHS of full_syzygy, independently of division.
    syzygy = sources['Syzygy.lean'].split('theorem full_syzygy',1)[1].split(':= by',1)[0]
    factor = re.search(r'\bu\*\((.*?)\)\s*$',syzygy,re.S)
    require(factor is not None, 'Syzygy RHS shape')
    source_quotient = expression(factor.group(1),{'u':u,'h':h,'q':q,'j':j,'s':sn,'t':tn})
    zero('actual full_syzygy RHS',c-u*source_quotient)
    zero('relative differential RHS',m+3*j-u*(h.derivative('x')*q.derivative('y')-h.derivative('y')*q.derivative('x')))

    if perturb=='omit-gdot': nd = kd+3*g*ne
    numerators = {'curve':c,'curve_jet':nc,'differential':m+3*j,
        'differential_first_variation':nd,'source_differential_jet':nj,'moving_map':nm}
    denominators = {'curve':'108 H^6','curve_jet':'108 G H^7','differential':'H^3',
        'differential_first_variation':'G^2 H^4','source_differential_jet':'G H^7','moving_map':'54 G^2 J^2'}
    records = {}
    for name,poly in numerators.items():
        quotient,remainder = divmod(poly,u)
        zero(name+' division identity',poly-u*quotient-remainder)
        zero(name+' remainder',remainder)
        records[name] = {'clearing_denominator':denominators[name],
            'numerator':polynomial_record(poly),'quotient':polynomial_record(quotient),
            'remainder':polynomial_record(remainder)}

    receipt = {'status':'PASS','instance':'holdout-moving-branch',
        'upstream_source_commit':manifest['source_commit'],
        'current_source_blobs_unchanged_at':manifest['checked_current_upstream'],
        'notebook_base':manifest['notebook_base'],
        'ring':'Q[c,a,b,d,e,f,x,y], lex; affine z=1; all six coefficients retained',
        'monomial_order':list(NAMES),'localization':['G != 0','H != 0','J != 0 for moving quotient'],
        'input_files_hashed':len(manifest['files']), 'reused_receipts':manifest['reused_receipts'],
        'checks_passed':len(checks),'checks':checks,'identities':records,
        'covariant_terms':dict(zip(('H','Theta','J'),map(len,values))),
        'script_sha256':sha(Path(__file__).read_bytes()),'inputs_sha256':sha((PACKET/'inputs.json').read_bytes()),
        'versions':{'python':platform.python_version(),'python_flint':flint.__version__,'sympy':sp.__version__},
        'elapsed_seconds':round(time.monotonic()-started,6),
        'limits':['No Lean/kernel build','No trace or clearing replay','No new primitive-existence proof',
                  'No independent physical function-field nonvanishing or embedding proof'],
        'perturbation':perturb}
    return receipt


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--perturb',choices=['cubic-path','j-coefficient','omit-gdot'])
    ap.add_argument('--output',type=Path)
    args=ap.parse_args()
    try:
        result=run(args.perturb)
        require(args.perturb is None,'Deliberate error unexpectedly passed')
        output=args.output or PACKET/'replay.json'
        output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
        print(json.dumps({'status':'PASS','checks':result['checks_passed'],
            'zero_remainders':len(result['identities']),'elapsed_seconds':result['elapsed_seconds']}))
    except Exception as error:
        print('FAIL: '+str(error))
        raise SystemExit(1)
