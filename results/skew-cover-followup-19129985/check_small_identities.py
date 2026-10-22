from pathlib import Path
import datetime, json, time
import sympy as s

start=time.monotonic()
r,v,a,t,V=s.symbols('r v a t V')
w=(v*r-1)/r**2
A=r**3+r**-3+(v*r-1)**6/r**15
f=r**18+r**12+(v*r-1)**6-a*r**15
Ar=s.diff(A,r); Av=s.diff(A,v)
fr=s.diff(f,r); fra=s.cancel(fr.subs(a,A))
checks={}
def zero(name, value):
    residual=s.cancel(value)
    if residual!=0: raise ValueError(name+': '+str(residual))
    checks[name]='zero'
zero('cover_equals_r15_times_A_minus_a',f-r**15*(A-a))
zero('cover_derivative_on_cover',fra-r**15*Ar)
zero('cubic_V3_coefficient',(1+r**6+w**6)/r**3-A)
zero('cubic_V2_coefficient',(r+r**3*w)*t/r**2-t*v)
zero('cubic_V_coefficient',r*t*(1-t**2)/(7*r)-t*(1-t**2)/7)
zero('implicit_r_a',s.diff(f,a)+fr*r**15/fr)
zero('implicit_r_v',s.diff(f,v)+fr*(-6*r*(v*r-1)**5/fr))
zero('implicit_r_t',s.diff(f,t))
psi=r**-3
psir=s.diff(psi,r)
psiv=psir*(-Av/Ar)
psivv=s.diff(psiv,v)-Av/Ar*s.diff(psiv,r)
K=90*sum(s.binomial(4,k)*(-1)**(4-k)*v**k*r**(k-16)/s.Integer(k-16) for k in range(5))
H=psir*Av**2/Ar+K
zero('ordinary_H_r_equals_A_r_psi_vv',s.diff(H,r)-Ar*psivv)
controls={'wrong_sign_r_v':s.cancel(s.diff(f,v)+6*r*(v*r-1)**5),
          'omit_K_from_H':s.cancel(s.diff(H-K,r)-Ar*psivv)}
if any(x==0 for x in controls.values()): raise ValueError('undetected mutation')
result={'status':'PASS','retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'sympy_version':s.__version__,'seconds':time.monotonic()-start,
        'identities':checks,'negative_controls':{k:str(x) for k,x in controls.items()},
        'scope':'Exact rational identities over Q(r,v,a,t). Derivatives on the cover use f_r != 0; rational chart uses r != 0. psi_vv means fixed-a derivative partial_v - (A_v/A_r) partial_r. No connection, physical source transport, current, rank, pole-bound, Lean, or full packet replay.'}
Path(__file__).with_name('small-identities.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
