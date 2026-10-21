"""Independent polynomial fiber reduction; no connection or rank-search replay."""
from pathlib import Path
import json, time, sys, sympy as s
started = time.monotonic()
U,a,b,c,d,r,w,t=s.symbols('U a b c d r w t')
P=a*U**3+b*U**2+c*U+d
# d_U(Q z) = -(P Q' + P' Q/6) dU/z^5.
red=[s.Integer(1),U]
exact=[s.Integer(0),s.Integer(0)]
checks=[]
for k in range(2,5):
    m=k-2
    lead=a*(s.Rational(1,2)+m)
    lower=s.expand((P*s.diff(U**m,U)+s.diff(P,U)*U**m/6)-lead*U**k)
    replacement=sum(lower.coeff(U,j)*red[j] for j in range(k))
    correction=sum(lower.coeff(U,j)*exact[j] for j in range(k))
    red.append(s.factor(-replacement/lead))
    exact.append(s.factor(-(U**m+correction)/lead))
for k in range(5):
    residual=s.cancel(U**k-red[k]+P*s.diff(exact[k],U)+s.diff(P,U)*exact[k]/6)
    if residual != 0: raise RuntimeError(f'reduction k={k} failed: {residual}')
    checks.append({'k':k,'remainder':[str(s.factor(s.expand(red[k]).coeff(U,j))) for j in range(2)],'exact_Q':str(exact[k]),'identity_residual':str(residual)})
physical={a:1+r**6+w**6,b:r*t*(1+r**2*w),c:r*t*(1-t**2)/7,d:1+t**6}
# Horizontal N=U^2, D=a gives coefficients with a^2 poles.
f0=s.factor(red[2].coeff(U,0)/a)
# red[2] is factored, so expand before coeff.
f0=s.factor(s.expand(red[2]).coeff(U,0)/a)
f1=s.factor(s.expand(red[2]).coeff(U,1)/a)
D=physical[a]
cphys=physical[c]
quotient,remainder=s.div(s.Poly(cphys,r,w,t,domain=s.QQ),s.Poly(D,r,w,t,domain=s.QQ))
if remainder.is_zero: raise RuntimeError('expected nondivisibility a does not divide c')
# Match archive's basis, physical coefficients and column convention; no execution of its checks.
root=Path(__file__).resolve().parents[1]
archive=root/'results/skew-small-obstruction/inputs/fqlx'
source=json.loads((archive/'rank2_primitive_system_Y0.json').read_text(encoding='utf-8'))
if source['basis'] != ['dU/v^5','U*dU/v^5']: raise RuntimeError('basis mismatch')
physical_archive={s.Symbol(key):s.sympify(value,locals={str(q):q for q in [a,b,c,d,r,w,t]}) for key,value in source['physical_coefficients'].items()}
for key in [a,b,c,d]:
    if s.expand(physical_archive[key].subs(s.Symbol('alpha'),t)-physical[key]) != 0:
        raise RuntimeError(f'physical coefficient mismatch {key}')
report={'scope':'5 exact universal horizontal reductions only; source transport, connection, rank screens not rerun','sympy':s.__version__,'python':sys.version,'reduction_identity':'U^k omega0 = remainder*omega0 + d_U(Q z)','checks':checks,'N_r_U2_D_a_example':{'f0':str(f0),'f1':str(f1),'correction':str(s.factor(exact[2]/a)),'a_divides_c':False,'nonzero_polynomial_remainder':str(remainder.as_expr())},'archive_bindings':['basis','four Y0 physical coefficients'],'denominator_bound':'Each reduced horizontal component N_i/a, deg_total N_i<=4, lies in a^-4 Q[r,w,t]^2; this is only a common-denominator upper bound. No inclusion in degree-six polynomial or H/a screens follows.','seconds':time.monotonic()-started}
(root/'results/skew-small-obstruction/horizontal-reduction.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
