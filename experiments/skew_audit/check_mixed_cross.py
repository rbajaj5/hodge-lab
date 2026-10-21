"""One exact cross-character E2 class, independently of repository arithmetic."""
from check_low_and_odd import *

def main():
 start=time.perf_counter();prior=json.loads((OUT/'diagonal-review.json').read_text());example=prior['cross_character_examples'][0]
 ep=json.loads((REPO/'results/one-reflection-skew-degree6/one-reflection-skew/degree-6.json').read_text())
 F,A=parse(ep['target']['F']),parse(ep['target']['A']);parts=[diff(F,i)for i in range(6)]
 def build(spec):
  i,m,ch=spec;D=shift(parts[i],tuple(m));N=[shift(A,tuple(m))if j==i else {}for j in range(6)]
  assert not add(mul(A,D),mul(parts[i],N[i]),-1)and {chi(k)for k in D}=={tuple(ch)}
  return D,N
 D,N=build(example['left']);E,P=build(example['right']);cross=add(B(D,P),B(E,N));assert pack(cross)==example['polynomial']
 ch=tuple(example['output_character'])
 jac=[shift(g,m)for g in parts for m in monos(9)if chi(tuple(x+y for x,y in zip(next(iter(g)),m)))==ch]
 fcols=[shift(F,m)for m in monos(8)if chi(m)==ch]
 basis=basis_of(jac+fcols);rem=reduce(cross,basis)[0]
 assert rem, "Required nonzero cross-character quotient class vanished"
 out={'status':'PASS','scope':'One cross-character term of two valid natural E1 directions; not an existence or global mixed-family result.',
  'input_diagonal_receipt_sha256':sha(OUT/'diagonal-review.json'),'script_lf_sha256':sha(Path(__file__)),'left':example['left'],'right':example['right'],'output_character':list(ch),
  'cross_polynomial':pack(cross),'J14_columns':len(jac),'FS8_columns':len(fcols),'correction_rank':len(basis),'quotient_remainder':pack(rem),'nonzero_modulo_J_plus_F':bool(rem)}
 if rem:
  row=min(rem);dual=pullback({row:Q(1)},basis);pairing=dot(dual,cross)
  assert pairing==rem[row]!=0 and all(dot(dual,c)==0 for c in jac+fcols)
  bad={m:2*c for m,c in dual.items()}
  assert dot(bad,cross)!=pairing, 'Altered dual pairing was not rejected'
  out['altered_dual_pairing_rejected']=True
  out.update({'separating_dual':pack(dual),'pairing':str(pairing),'checked_correction_pairings':len(jac)+len(fcols)})
 out['elapsed_seconds']=time.perf_counter()-start
 (OUT/'mixed-cross.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
 print(json.dumps({k:out[k]for k in ('status','nonzero_modulo_J_plus_F','elapsed_seconds')}))
if __name__=='__main__':main()
