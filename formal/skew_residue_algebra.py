"""Independent exact rational normal-coefficient reconstruction from protected F.

No Lean computation or saved residue values are used as reconstruction inputs.
Sparse polynomial arithmetic and determinants reuse checkpoint125's generic code.
"""
from pathlib import Path
from fractions import Fraction as Q
import hashlib, json
import check_skew_volume as p

ROOT=Path(__file__).resolve().parent
require=p.require

def rat(n,d=None):return (n,p.ONE if d is None else d)
def radd(a,b):return (p.add(p.mul(a[0],b[1]),p.mul(b[0],a[1])),p.mul(a[1],b[1]))
def rscale(a,c):return (p.scale(a[0],c),a[1])
def rmul(a,b):return (p.mul(a[0],b[0]),p.mul(a[1],b[1]))
def req(a,b):return p.mul(a[0],b[1])==p.mul(b[0],a[1])
def rderivative(a,j):
    return (p.add(p.mul(p.deriv(a[0],j),a[1]),p.scale(p.mul(a[0],p.deriv(a[1],j)),-1)),p.power(a[1],2))
def rv(a,point):
    d=p.value(a[1],point);require(d!=0,'Undefined rational evaluation')
    return p.value(a[0],point)/d
def show(a):return {'numerator':p.terms(a[0]),'denominator':p.terms(a[1])}

def reconstruct(out):
    pins=json.loads((out/'inputs.json').read_text(encoding='utf-8'))['pins'];saved={}
    for pin in pins:
        raw=(ROOT.parent/pin['path']).read_bytes().replace(b'\r\n',b'\n')
        require(hashlib.sha256(raw).hexdigest()==pin['sha256'],'Input SHA mismatch')
        require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==pin['git_blob'],'Input blob mismatch')
        if pin['upstream_path'].endswith('.json'):saved[Path(pin['upstream_path']).name]=json.loads(raw)
    record=saved['record.json']
    require(record['q']==1,'Wrong pole order')
    require(saved['provenance.json']['variables']==['X0','X1','X2','Y0','Y1','Y2'],'Wrong protected order')
    xs=[{tuple(int(i==j) for i in range(5)):Q(1)} for j in range(5)]
    U,r,w,t,z=xs
    # Substitute (x,rx,wx,1,t,z); all x exponents must be even to use U=x².
    G={}
    for c,e in record['F']['terms']:
        ex=e[0]+e[1]+e[2]
        require(ex%2==0,'Protected polynomial does not descend through this square coordinate')
        k=(ex//2,e[1],e[2],e[4],e[5]);G=p.add(G,{k:Q(c)})
    gradients=[p.deriv(G,j) for j in range(5)]
    normal=gradients[4]
    require(normal==p.scale(p.power(z,5),6),'Actual normal derivative mismatch')
    eye=[[p.ONE if i==j else {} for j in range(5)] for i in range(4)]
    require(p.det([gradients,*eye])==normal,'dG wedge alpha orientation mismatch')
    require(p.det([*eye,gradients])==normal,'alpha wedge dG orientation mismatch')
    require(p.det([xs,*eye])==z,'Arbitrary covector wedge cancellation failed')
    beta=rat(p.power(U,2),p.scale(p.mul(p.power(z,5),G),12))
    derivatives=[rderivative(beta,j) for j in range(5)]
    psi=rat(p.scale(p.power(U,2),-1),p.scale(p.power(G,2),2))
    pole_numerator=rat(p.scale(p.power(U,2),5),p.scale(p.power(z,6),12))
    simple=rmul(pole_numerator,rat(p.ONE,G))
    require(req(psi,radd(derivatives[4],simple)),'Double-pole reduction identity failed')
    residue=rat(pole_numerator[0],p.mul(pole_numerator[1],normal))
    canonical=rat(p.scale(p.power(U,2),5),p.scale(p.power(z,11),72))
    require(req(residue,canonical),'Normal coefficient 5/72 failed')
    require(req(rmul(rat(normal,G),residue),simple),'Simple-pole factorization failed')
    sample=[1,0,0,0,1]
    values={'G':str(p.value(G,sample)),'psi':str(rv(psi,sample)),
            'beta_z':str(rv(derivatives[4],sample)),'simple_pole':str(rv(simple,sample)),
            'residue_coefficient':str(rv(residue,sample))}
    require(values=={'G':'3','psi':'-1/18','beta_z':'-7/36','simple_pole':'5/36','residue_coefficient':'5/72'},'Point controls differ')
    base_sample=[1,1,0,0,1]
    require(rv(derivatives[1],base_sample)==Q(-1,32),'Base partial witness failed')
    on_divisor=[-1,1,0,0,1]
    require(p.value(G,on_divisor)==0 and p.value(normal,on_divisor)==6,'Divisor chart point invalid')
    require(rv(residue,on_divisor)==Q(5,72),'Residue specialization failed')
    # These are full rational-polynomial comparisons, not sampled ranks.
    mutations={
      'reversed_reduction_sign':not req(psi,radd(derivatives[4],rscale(simple,-1))),
      'omit_z_power_derivative':not req(psi,radd(psi,simple)),
      'missing_normal_factor_six':not req(residue,rat(pole_numerator[0],p.mul(pole_numerator[1],p.power(z,5)))),
      'wrong_residue_sign':not req(residue,rscale(canonical,-1)),
      'normal_vanishes_at_z_zero':p.value(normal,[1,0,0,0,0])==0,
      'base_partial_is_not_zero':derivatives[1][0]!={}}
    require(all(mutations.values()),'A deliberate error escaped detection')
    result={'status':'PASS','method':'Exact rational sparse polynomials and quotient-rule derivatives; no floating point',
      'variables':['U','r','w','t','z'],'protected_chart_polynomial':p.terms(G),
      'all_five_G_partials':[p.terms(a) for a in gradients],
      'all_five_beta_partials':[show(a) for a in derivatives],
      'beta':show(beta),'psi':show(psi),'simple_pole':show(simple),'residue':show(canonical),
      'normal_first_determinant':p.terms(p.det([gradients,*eye])),
      'normal_last_determinant':p.terms(p.det([*eye,gradients])),
      'control_point':sample,'control_values':values,
      'nonzero_base_partial':{'point':base_sample,'direction':'r','value':'-1/32','wedge_contribution':0},
      'divisor_control':{'point':on_divisor,'G':'0','normal':'6','residue':'5/72'},
      'mutations_detected':mutations,
      'scope':'Local normal-coefficient reduction under Res((dG/G) wedge theta)=theta; no general residue map, global descent or primitive'}
    (out/'independent.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    return result
