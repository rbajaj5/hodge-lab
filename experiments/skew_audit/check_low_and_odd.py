"""Independent necessary-equation replay for d5 and pure odd d7; no repo imports."""
from check_exclusions import *
from modular_e1 import rank_columns

def reduce(v,basis,track=False):
 v=dict(v);combo={}
 for p,(b,bc)in sorted(basis.items()):
  if p in v:
   c=v[p];v=add(v,b,-c)
   if track:combo=add(combo,bc,-c)
 return v,combo
def basis_of(cols,track=False):
 basis={}
 for j,col in enumerate(cols):
  v,combo=reduce(col,basis,track)
  if v:
   p=min(v);s=v[p]
   if track:combo=add(combo,{j:Q(1)})
   basis[p]=({k:c/s for k,c in v.items()},{k:c/s for k,c in combo.items()})
 return basis
def pullback(raw,basis):
 dual=dict(raw)
 for p,(b,_)in sorted(basis.items(),reverse=True):
  dual=add(dual,{p:-dot(dual,b)})
 return dual
def equations(cols,corrections):
 basis=basis_of(corrections);res=[reduce(c,basis)[0]for c in cols]
 rows=sorted(set().union(*(set(c)for c in res)))
 eq=[{j:c[r]for j,c in enumerate(res)if r in c}for r in rows]
 return basis,res,rows,eq
def squares(cols,corrections,pairs,allowed):
 basis,res,rows,eq=equations(cols,corrections)
 active=[j for j,(a,b)in enumerate(pairs)if a in allowed and b in allowed]
 eq=[{j:c for j,c in q.items()if j in active}for q in eq]
 rb=basis_of(eq,True);witness=[]
 for i in allowed:
  target=pairs.index((i,i));rem,combo=reduce({target:Q(1)},rb,True)
  if not rem:
   dual=pullback({rows[j]:-c for j,c in combo.items()},basis)
   assert all(dot(dual,c)==0 for c in corrections)
   assert all(dot(dual,cols[j])==int(j==target)for j in active)
   witness.append({'parameter':i,'dual':pack(dual)})
 return witness,len(rb)

def main():
 start=time.perf_counter();rec=LIVE/'upstream/data/one-reflection-skew/instance.rec';fields={};key=None
 for line in rec.read_text().splitlines():
  if line and not line[0].isspace()and ':'in line:key,val=line.split(':',1);fields[key]=val.strip()
  elif key in ('F','A')and line.startswith('  '):fields[key]+=' '+line.strip()
 F,A=parse(fields['F']),parse(fields['A']);parts=[diff(F,i)for i in range(6)]
 pairs=[(i,j)for i in range(6)for j in range(i,6)]
 j10=[shift(g,m)for g in parts for m in monos(5)]
 h10=[{m:c*(1 if i==j else 2)for m,c in mul(A,diff(parts[i],j)).items()}for i,j in pairs]
 sw,r=squares(h10,j10,pairs,list(range(6)));assert len(sw)==6
 pilotpath=REPO/'results/one-reflection-skew-pilot/report.json';pilot=json.loads(pilotpath.read_text())['lowDegreeBaseline']
 j10basis=basis_of(j10);r10=monos(10);l10={m:i for i,m in enumerate(r10)}
 entries=[[l10[m],j,str(c)]for j,p in enumerate(h10)for m,c in sorted(reduce(p,j10basis)[0].items())]
 assert entries==pilot['degree5E2Plot']['residual_entries']and r==pilot['degree5QuotientQuadraticRank']==15
 zero_pairs=[list(pairs[i])for i,c in enumerate(h10)if not c];assert len(zero_pairs)==6
 mutation_count=0
 for item in sw:
  dual={tuple(m):Q(c)for m,c in item['dual']};bad=add(dual,{min(dual):Q(1)})
  target=pairs.index((item['parameter'],item['parameter']))
  assert any(dot(bad,c)for c in j10)or any(dot(bad,c)!=int(j==target)for j,c in enumerate(h10));mutation_count+=1
 low={'degree':5,'quotient_quadratic_rank':r,'square_witnesses':sw,'correction_columns':len(j10),'zero_Hessian_pairs':zero_pairs,
  'matches_all_saved_residual_entries':True,'active_rows':len({x[0]for x in entries}),'nonzero_columns':len({x[1]for x in entries}),'saved_packet_lf_sha256':sha(pilotpath),
  'scope':'All Hessian quadratic terms retained modulo the full J10; every compatible numerator correction and F quotient lies in J10. Rank15 agrees with the computed packet; the rank16 prose/plot claim is false.'}
 print(json.dumps({'degree5':'PASS','rank':r,'six_squares':len(sw),'elapsed_seconds':time.perf_counter()-start}),flush=True)
 chA=chi(next(iter(A)));zero=(0,0,0,0)
 assert {chi(m)for m in F}=={zero}and {chi(m)for m in A}=={chA}
 rows14=[m for m in monos(14)if chi(m)==chA];lookup={m:i for i,m in enumerate(rows14)}
 def vec(p):
  assert all(m in lookup for m in p)
  return {lookup[m]:c for m,c in p.items()}
 j14=[vec(shift(g,m))for g in parts for m in monos(9)if chi(tuple(x+y for x,y in zip(next(iter(g)),m)))==chA]
 jb14=basis_of(j14);assert len(rows14)-len(jb14)==213
 odd=[];units=[tuple(int(j==i)for j in range(6))for i in range(6)]
 for ch in sorted({chi(m)for m in monos(7)if m[5]%2}):
  begin=time.perf_counter();outch=tuple(a^b for a,b in zip(ch,chA))
  jac=[shift(g,m)for g in parts for m in monos(8)if chi(tuple(x+y for x,y in zip(next(iter(g)),m)))==outch]
  ads=[shift(A,m)for m in monos(7)if chi(m)==ch]
  rank,_,_=rank_columns(jac+ads)
  kfields=[]
  for i,j in combinations(range(6),2):
   for m in monos(3):
    if chi(tuple(x+y+z for x,y,z in zip(next(iter(parts[i])),next(iter(parts[j])),m)))==outch:
     K=[{}for _ in range(6)];K[i]=shift(parts[j],m);K[j]=shift(parts[i],m,-1);kfields.append(K)
  jrank=len(jac)-len(kfields);bound=len(ads)+jrank-rank
  natural=[]
  for i,g in enumerate(parts):
   for m in monos(2):
    D=shift(g,m)
    if chi(next(iter(D)))==ch:natural.append((i,m,D,[shift(A,m)if k==i else {}for k in range(6)]))
  assert len(natural)==bound and len(basis_of([x[2]for x in natural]))==bound
  # Euler gauge fixes the Fi=FY2 coefficient of Y2^2 in the single coordinate sector.
  gauge=[k for k,u in enumerate(units)if chi(u)==ch]
  dropped={(5,tuple(x+y for x,y in zip(units[k],units[5])))for k in gauge}
  gens=[x for x in natural if x[:2]not in dropped]
  gp=[(i,j)for i in range(len(gens))for j in range(i,len(gens))]
  cols=[vec(B(gens[i][2],gens[j][3])if i==j else add(B(gens[i][2],gens[j][3]),B(gens[j][2],gens[i][3])))for i,j in gp]
  allowed=list(range(len(gens)));steps=[]
  # Use already built quotient to retain exact full mixed terms within this character.
  while allowed:
   res=[reduce(c,jb14)[0]for c in cols];active=[j for j,(a,b)in enumerate(gp)if a in allowed and b in allowed]
   rk=sorted(set().union(*(set(res[j])for j in active)))
   eq=[{j:res[j][r]for j in active if r in res[j]}for r in rk];rb=basis_of(eq,True);w=[]
   for i in allowed:
    target=gp.index((i,i));rem,combo=reduce({target:Q(1)},rb,True)
    if not rem:
     dual=pullback({rk[j]:-c for j,c in combo.items()},jb14)
     assert all(dot(dual,c)==0 for c in j14)
     assert all(dot(dual,cols[j])==int(j==target)for j in active)
     w.append({'parameter':i,'dual':pack(dual)})
   steps.append({'allowed':allowed,'equation_rank':len(rb),'square_witnesses':w})
   if not w:break
   allowed=[i for i in allowed if i not in {x['parameter']for x in w}]
  item={'character':list(ch),'E1_augmented_rank_mod101':rank,'E1_Jacobian_rank_from_regular_sequence':jrank,'E1_kernel_dimension':bound,'Koszul_fields':len(kfields),'gauge_parameters':gauge,'generators':[[i,list(m)]for i,m,_,_ in gens],'steps':steps,'remaining':[ [gens[i][0],list(gens[i][1])]for i in allowed]}
  if ch==(0,0,0,1):
   assert len(allowed)==5 and set((gens[i][0],gens[i][1])for i in allowed)=={(i,tuple(x+y for x,y in zip(units[i],units[5])))for i in range(5)}
   dens=[shift(parts[i],tuple(x+y for x,y in zip(units[i],units[5])))for i in range(6)]
   nums=[[shift(A,tuple(x+y for x,y in zip(units[i],units[5])))if k==i else {}for k in range(6)]for i in range(6)]
   corrections=[vec(shift(F,m))for m in monos(8)if chi(m)==chA]+[vec(B(d,K))for d in dens for K in kfields]
   dcols=[vec(B(dens[i],nums[j])if i==j else add(B(dens[i],nums[j]),B(dens[j],nums[i])))for i,j in pairs]
   cb,res,rr,eq=equations(dcols,corrections);rb=basis_of(eq,True);assert len(rb)==9
   eqs=[];duals=[]
   for _,(q,combination)in sorted(rb.items()):
    du=pullback({rr[j]:c for j,c in combination.items()},cb)
    assert all(dot(du,c)==0 for c in corrections)and all(dot(du,c)==q.get(j,0)for j,c in enumerate(dcols))
    duals.append(pack(du));poly={}
    for j,c in q.items():
     a,b=pairs[j]
     if max(a,b)<5:
      m=[0]*5;m[a]+=1;m[b]+=1;poly[tuple(m)]=c
    eqs.append(poly)
   cm=monos(3,5);cidx={m:i for i,m in enumerate(cm)}
   cubes=[{cidx[tuple(x+y for x,y in zip(m,n))]:c for m,c in q.items()}for q in eqs for n in monos(1,5)]
   assert len(basis_of(cubes))==35
   columns,det=selected_minor(cubes,101)
   old=json.loads((OUT/'diagonal-review.json').read_text())['diagonal']['necessary_quadrics']
   old=[{tuple(m):Q(c)for m,c in q}for q in old]
   same_span=all(not reduce(q,basis_of(old))[0]for q in eqs)and all(not reduce(q,basis_of(eqs))[0]for q in old)
   assert same_span
   assert eqs==old
   item['diagonal']={'correction_columns':len(corrections),'correction_rank':len(cb),'necessary_rank':9,'quadrics':[pack(q)for q in eqs],'duals':duals,'degree6_same_quadric_span':same_span,'degree6_same_ordered_equations':eqs==old,'cubic_rank':35,'selected_minor_columns':columns,'selected_minor_mod101':det}
  else:assert not allowed
  item['excluded_as_pure_character']=True;item['elapsed_seconds']=time.perf_counter()-begin;odd.append(item)
  print(json.dumps({'degree7pure':ch,'E1dim':bound,'remaining_after_squares':len(allowed),'elapsed_seconds':item['elapsed_seconds']}),flush=True)
 out={'status':'PASS','source_sha256':sha(rec),'script_lf_sha256':sha(Path(__file__)),'helper_lf_sha256':sha(Path(__file__).with_name('check_exclusions.py')),'modular_helper_lf_sha256':sha(Path(__file__).with_name('modular_e1.py')),'degree5':low,'degree7_pure_odd':odd,'negative_controls_rejected':mutation_count,'scope':'All four pure odd characters only. Cross-character B terms and sums of diagonal character outputs are not included; no full mixed-family exclusion.','elapsed_seconds':time.perf_counter()-start}
 (OUT/'low-and-odd.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
if __name__=='__main__':main()
