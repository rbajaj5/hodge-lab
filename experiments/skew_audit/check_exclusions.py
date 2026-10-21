"""Independent read-only Fraction replay; no notebook arithmetic imports."""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations
import ast, hashlib, json, subprocess, sys, time
if not __debug__:raise RuntimeError('This review requires active assertions; do not use -O.')

REPO=Path(__file__).resolve().parents[2]
OUT=REPO/'results/one-reflection-skew-audit-20261021'
LIVE=OUT/'inputs/live'
NAMES=('X0','X1','X2','Y0','Y1','Y2')
ZERO=(0,)*6
def sha(p):return hashlib.sha256(p.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
def add(a,b,c=Q(1)):
 out=dict(a)
 for k,v in b.items():
  out[k]=out.get(k,Q(0))+c*v
  if not out[k]:del out[k]
 return out
def mul(a,b):
 out={}
 for m,c in a.items():
  for n,d in b.items():
   k=tuple(x+y for x,y in zip(m,n));out[k]=out.get(k,Q(0))+c*d
 return {k:v for k,v in out.items() if v}
def shift(a,m,c=Q(1)):return {tuple(x+y for x,y in zip(k,m)):v*c for k,v in a.items() if v*c}
def diff(a,i):
 out={}
 for m,c in a.items():
  if m[i]:
   n=list(m);n[i]-=1;out[tuple(n)]=c*m[i]
 return out
def parse(s):
 def visit(n):
  if isinstance(n,ast.Constant) and type(n.value)is int:return {ZERO:Q(n.value)} if n.value else {}
  if isinstance(n,ast.Name) and n.id in NAMES:return {tuple(int(k==NAMES.index(n.id))for k in range(6)):Q(1)}
  if isinstance(n,ast.UnaryOp) and isinstance(n.op,ast.USub):return {m:-c for m,c in visit(n.operand).items()}
  if isinstance(n,ast.BinOp):
   a=visit(n.left)
   if isinstance(n.op,ast.Pow):
    assert isinstance(n.right,ast.Constant) and type(n.right.value)is int and n.right.value>=0
    z={ZERO:Q(1)}
    for _ in range(n.right.value):z=mul(z,a)
    return z
   b=visit(n.right)
   if isinstance(n.op,ast.Add):return add(a,b)
   if isinstance(n.op,ast.Sub):return add(a,b,-1)
   if isinstance(n.op,ast.Mult):return mul(a,b)
   if isinstance(n.op,ast.Div):
    assert set(b)=={ZERO} and b[ZERO];return {m:c/b[ZERO]for m,c in a.items()}
  raise ValueError(ast.dump(n))
 return visit(ast.parse(s,mode='eval').body)
def monos(d,n=6):
 if n==1:return [(d,)]
 return [(i,)+r for i in range(d+1)for r in monos(d-i,n-1)]
def dot(a,b):
 if len(a)>len(b):a,b=b,a
 return sum((c*b[k]for k,c in a.items() if k in b),Q(0))
def span(vectors):
 basis={}
 for v in vectors:
  v=dict(v)
  for p,b in sorted(basis.items()):
   if p in v:v=add(v,b,-v[p])
  if v:
   p=min(v);basis[p]={j:c/v[p]for j,c in v.items()}
 return basis
def B(D,N):
 div={}
 for i,c in enumerate(N):div=add(div,diff(c,i))
 result=mul(D,div)
 for i,c in enumerate(N):result=add(result,mul(c,diff(D,i)),-1)
 return result
def chi(m):return ((m[0]+m[1]+m[2])%2,(m[0]+m[2]+m[3])%2,(m[0]+m[2]+m[4])%2,m[5]%2)
def pack(p):return [[list(m)if isinstance(m,tuple)else m,str(c)]for m,c in sorted(p.items())]
def unpack(p):return {i:Q(c)for i,c in p}
def selected_minor(columns,prime):
 basis={};selected=[]
 for j,col in enumerate(columns):
  v={i:c.numerator%prime*pow(c.denominator,-1,prime)%prime for i,c in col.items()}
  v={i:c for i,c in v.items()if c}
  for p,b in sorted(basis.items()):
   if p in v:
    c=v[p]
    for r,x in b.items():
     v[r]=(v.get(r,0)-c*x)%prime
     if not v[r]:del v[r]
  if v:
   p=min(v);c=pow(v[p],-1,prime);basis[p]={r:x*c%prime for r,x in v.items()};selected.append(j)
 n=len(basis);assert sorted(basis)==list(range(n))
 a=[[columns[j].get(i,Q(0)).numerator%prime*pow(columns[j].get(i,Q(0)).denominator,-1,prime)%prime for j in selected]for i in range(n)]
 det=1
 for j in range(n):
  k=next(i for i in range(j,n)if a[i][j])
  if j!=k:a[j],a[k]=a[k],a[j];det=-det
  d=a[j][j];det=det*d%prime;di=pow(d,-1,prime)
  for i in range(j+1,n):
   c=a[i][j]*di%prime
   for k in range(j,n):a[i][k]=(a[i][k]-c*a[j][k])%prime
 return selected,det%prime

def main(full_e1=False):
 start=time.perf_counter();sources=[]
 def read(rel):
  p=REPO/rel;sources.append(p);return json.loads(p.read_text(encoding='utf-8'))
 packet=read('results/one-reflection-skew-degree6/one-reflection-skew/degree-6-diagonal.json')
 summary=read('results/one-reflection-skew-degree6/summary.json')
 hess=read('results/one-reflection-skew-degree6/one-reflection-skew/degree-6-e2.json')
 e1=read('results/one-reflection-skew-degree6/one-reflection-skew/degree-6.json')
 rec=LIVE/'upstream/data/one-reflection-skew/instance.rec';raw=rec.read_text();fields={};key=None
 for line in raw.splitlines():
  if line and not line[0].isspace() and ':'in line:
   key,value=line.split(':',1);fields[key]=value.strip()
  elif key in ('F','A') and line.startswith('  '):fields[key]+=' '+line.strip()
 F,A=parse(fields['F']),parse(fields['A']);assert fields['q']=='1'
 assert all(parse(p['target']['F'])==F and parse(p['target']['A'])==A and p['target']['q']=='1'for p in (packet,hess,e1))
 source_manifest=json.loads((LIVE/'source-manifest.json').read_text())
 manifest_rec=next(x for x in source_manifest['files']if x['path']=='data/one-reflection-skew/instance.rec')
 assert hashlib.sha256(rec.read_bytes()).hexdigest()==manifest_rec['sha256']
 blob=hashlib.sha1(b'blob '+str(len(rec.read_bytes())).encode()+b'\0'+rec.read_bytes()).hexdigest();assert blob==manifest_rec['git_blob_sha1']
 parts=[diff(F,i)for i in range(6)];units=monos(1)
 units=[tuple(int(j==i)for j in range(6))for i in range(6)]
 fermat={tuple(6 if i==j else 0 for j in range(6)):Q(1)for i in range(6)}
 loads=[sum(map(abs,diff(add(F,fermat,-1),i).values()))for i in range(6)]
 assert all(x<6 for x in loads)
 rows=monos(12);index={m:i for i,m in enumerate(rows)}
 vector=lambda p:{index[m]:c for m,c in p.items()}
 dens=[shift(parts[i],units[i])for i in range(6)]
 nums=[[shift(A,units[i])if j==i else {}for j in range(6)]for i in range(6)]
 koszul=[]
 for i,j in combinations(range(6),2):
  for m in monos(2):
   field=[{}for _ in range(6)];field[i]=shift(parts[j],m);field[j]=shift(parts[i],m,-1)
   assert not add(mul(parts[i],field[i]),mul(parts[j],field[j]));koszul.append(field)
 assert len(koszul)==315
 corrections=[vector(shift(F,m))for m in monos(6)]
 corrections += [vector(B(D,K))for D in dens for K in koszul]
 pairs=list(combinations(range(6),2));pairs=[(i,j)for i in range(6)for j in range(i,6)]
 quads=[vector(add(B(dens[i],nums[j]),B(dens[j],nums[i]))if i!=j else B(dens[i],nums[i]))for i,j in pairs]
 assert len(corrections)==2352 and len(quads)==21
 assert packet['quadratic_column_pairs']==[list(p)for p in pairs]
 necessary=[];mutations=0
 for item in packet['consequences']:
  dual=unpack(item['functional']);values={j:dot(dual,c)for j,c in enumerate(quads)if dot(dual,c)}
  assert all(dot(dual,c)==0 for c in corrections)
  assert values==unpack(item['quadratic_coefficients']);necessary.append(values)
  bad=add(dual,{min(dual):Q(1)})
  assert any(dot(bad,c)!=0 for c in corrections)or any(dot(bad,c)!=values.get(j,0)for j,c in enumerate(quads));mutations+=1
 assert len(necessary)==len(span(necessary))==9
 active=[i for i,(a,b)in enumerate(pairs)if a<5 and b<5];gp=[pairs[i]for i in active];lookup={x:i for i,x in enumerate(active)}
 ge=[{lookup[i]:c for i,c in p.items()if i in lookup}for p in necessary]
 assert packet['gauged_column_pairs']==[list(p)for p in gp]and packet['gauged_equations']==[pack(q)for q in ge]
 polys=[]
 for q in ge:
  p={}
  for j,c in q.items():
   m=[0]*5;a,b=gp[j];m[a]+=1;m[b]+=1;p[tuple(m)]=c
  polys.append(p)
 cubic_rows=monos(3,5);cubic_index={m:i for i,m in enumerate(cubic_rows)}
 cubic=[{cubic_index[tuple(x+y for x,y in zip(m,n))]:c for m,c in q.items()}for q in polys for n in monos(1,5)]
 assert len(cubic)==45 and len(span(cubic))==35
 selected,det=selected_minor(cubic,101);assert len(selected)==35 and det
 cubes=summary['stage3_full_diagonal_e2']['cubic_macaulay']['identities']
 def power_check(item):
  result={}
  for i,mon,c in item['multipliers']:result=add(result,shift(polys[i],tuple(mon),Q(c)))
  assert result=={tuple(item['power']if j==item['parameter']else 0 for j in range(5)):Q(1)}
 for item in cubes+packet['quartic_search']['identities']:
  power_check(item);bad=json.loads(json.dumps(item));bad['multipliers'][0][2]=str(Q(bad['multipliers'][0][2])+1)
  try:power_check(bad)
  except AssertionError:mutations+=1
  else:raise AssertionError('mutated power accepted')
 assert sorted(x['parameter']for x in cubes)==list(range(5))
 full_e1_record=None
 if full_e1:
  e1start=time.perf_counter();den_mons=monos(6);num_mons=monos(7)
  jac=[vector(shift(part,m))for part in parts for m in num_mons]
  ad=[vector(shift(A,m))for m in den_mons]
  constraints=[]
  for item in e1['dual_obstructions']:
   dual=unpack(item['functional']);assert all(dot(dual,c)==0 for c in jac)
   constraint={j:dot(dual,c)for j,c in enumerate(ad)if dot(dual,c)}
   assert constraint==unpack(item['denominator_constraint']);constraints.append(constraint)
  kernels=[]
  for item in e1['kernel_lifts']:
   d,n=unpack(item['denominator']),unpack(item['numerator']);left={};right={}
   for j,c in d.items():left=add(left,ad[j],c)
   for j,c in n.items():right=add(right,jac[j],c)
   assert left==right;kernels.append(d)
  r,k=len(span(constraints)),len(span(kernels))
  assert r==len(constraints)==426 and k==len(kernels)==36 and r+k==len(den_mons)
  den_index={m:i for i,m in enumerate(den_mons)}
  j6=[{den_index[m]:c for m,c in shift(part,u).items()}for part in parts for u in units]
  assert len(span(j6))==36
  assert all(all(dot(c,d)==0 for c in constraints)for d in j6)
  # Replay conditional Hessian square consequences; all mixed terms among active parameters retained.
  parameters=[(i,j)for i in range(6)for j in range(6)if(i,j)!=(5,5)]
  hp=[(a,b)for a in range(35)for b in range(a,35)];hcols=[]
  for a,b in hp:
   i,u=parameters[a];j,v=parameters[b]
   hcols.append(vector(shift(shift(mul(A,diff(parts[i],j)),units[u]),units[v],1 if a==b else 2)))
  allowed=list(range(35));squares=0
  for step in hess['steps']:
   assert step['allowed_parameters']==allowed
   active=[j for j,(a,b)in enumerate(hp)if a in allowed and b in allowed]
   assert step['active_columns']==active
   forced=[]
   for item in step['forced_squares']:
    p=item['parameter'];assert p in allowed and item['square_column']==hp.index((p,p))
    dual=unpack(item['functional']);assert all(dot(dual,c)==0 for c in jac)
    assert all(dot(dual,hcols[j])==int(j==item['square_column'])for j in active)
    forced.append(p);squares+=1
   assert len(set(forced))==len(forced)
   allowed=[j for j in allowed if j not in forced];assert step['unresolved_parameters']==allowed
  assert allowed==hess['remaining_parameters']==[0,7,14,21,28] and squares==30
  full_e1_record={'complete_denominator_kernel_dimension':k,'independent_dual_constraints':r,
   'Jacobian_denominator_rank':36,'non_Jacobian_directions':0,
   'E1_kernel_lift_checks':36,'E1_dual_Jacobian_pairings':426*4752,
   'conditional_Hessian_square_identities':30,'Hessian_dual_Jacobian_pairings':30*4752,
   'after_F_gauge_parameters':35,'after_squares_parameters':allowed,
   'scope':'All six numerator components and all active mixed quadratic terms retained. Exact upper/lower kernel bounds establish completeness without rediscovering large Jacobian elimination.',
   'elapsed_seconds':time.perf_counter()-e1start}
  print(json.dumps({'full_E1_and_Hessian':'PASS','elapsed_seconds':full_e1_record['elapsed_seconds']}),flush=True)
 # Exact F-gauge identity on homogeneous E1 basis, for constants (d6) and linear h (d7).
 gauge_checks=0
 for multiplier_degree in (1,2):
  d=multiplier_degree+5
  for i in range(6):
   for m in monos(multiplier_degree):
    D=shift(parts[i],m);N=[shift(A,m)if j==i else {}for j in range(6)]
    for hmon in monos(d-6):
     h={hmon:Q(1)};hF=mul(h,F);hAE=[shift(mul(h,A),u)for u in units]
     Dnew=add(D,hF,-6);Nnew=[add(x,y,-1)for x,y in zip(N,hAE)]
     left=add(B(Dnew,Nnew),B(D,N),-1)
     # exact quotient difference: -6h divN+6N(h)+36h^2 A
     divN={}
     for j,c in enumerate(N):divN=add(divN,diff(c,j))
     Nh={}
     for j,c in enumerate(N):Nh=add(Nh,mul(c,diff(h,j)))
     rhs=add(mul(h,divN),Nh,-1);rhs={k:-6*c for k,c in rhs.items()}
     rhs=add(rhs,mul(mul(h,h),A),36)
     assert left==mul(F,rhs);gauge_checks+=1
 # Concrete cross-character terms, before any projection.
 cross_examples=[]
 natural=[]
 for i in range(6):
  for m in monos(2):
   D=shift(parts[i],m);N=[shift(A,m)if j==i else {}for j in range(6)]
   natural.append((i,m,chi(next(iter(D))),D,N))
 for ai in range(len(natural)):
  for bi in range(ai+1,len(natural)):
   i,m,ci,D,N=natural[ai];j,n,cj,E,P=natural[bi]
   if ci==cj:continue
   mixed=add(B(D,P),B(E,N))
   if mixed:
    expected=tuple((a+b+c)%2 for a,b,c in zip(ci,cj,(1,0,1,0)))
    assert {chi(x)for x in mixed}=={expected}
    cross_examples.append({'left':[i,list(m),list(ci)],'right':[j,list(n),list(cj)],'output_character':list(expected),'polynomial':pack(mixed),'scope':'Nonzero ambient cross-term; not claimed nonzero modulo J+F.'})
    break
  if cross_examples:break
 out={'status':'PASS','source_scope':'Reconstructed from live exact F/A; no repo arithmetic imported. Full E1 replay optional.',
      'upstream_head':source_manifest['upstream_head'],'live_target_sha256':manifest_rec['sha256'],'live_target_git_blob_sha1':blob,
      'source_lf_sha256':{p.relative_to(REPO).as_posix():sha(p)for p in sources},'script_lf_sha256':sha(Path(__file__)),
      'smoothness_derivative_l1_bounds':[str(x)for x in loads],'smoothness_argument':'At a nonzero complex point normalize max|zi|=1. A maximizing component has pure derivative magnitude6, strictly greater than the mixed derivative l1 bound. Hence no common projective gradient zero; six homogeneous gradients form a regular sequence.',
      'diagonal':{'components':6,'koszul_fields':315,'quotient_columns':462,'relaxed_Koszul_product_columns':1890,'correction_pairings':9*2352,'quadratic_pairings':9*21,'necessary_quadrics':[pack(p)for p in polys],
                  'cubic_shape':[35,45],'cubic_rank':35,'cubic_minor_prime':101,'cubic_minor_columns':selected,'cubic_minor_determinant':det,'cube_identities':5,'quartic_identities':5},
      'F_gauge_identity_checks':gauge_checks,'cross_character_examples':cross_examples,'negative_controls_rejected':mutations,
      'full_E1_and_Hessian':full_e1_record,
      'scope_limits':['No assertion that the full degree7 mixed-character family is excluded.','No exact diagonal correction-rank1486 replay is needed or claimed: all9 duals annihilate every full correction column.','The finite bounded exclusions do not construct an existence certificate.'],
      'elapsed_seconds':time.perf_counter()-start}
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'diagonal-review.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
 print(json.dumps({k:out[k]for k in ['status','F_gauge_identity_checks','negative_controls_rejected','elapsed_seconds']}),flush=True)

if __name__=='__main__':main('--full-e1'in sys.argv)
