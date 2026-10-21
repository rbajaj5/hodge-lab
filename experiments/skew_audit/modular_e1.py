"""Independent bounded F_101 E1 rank replay, using only our independent parser."""
from check_exclusions import *
from math import comb

P=101
def rank_columns(columns):
 basis={};pivots=[];trace=hashlib.sha256()
 for j,col in enumerate(columns):
  v={m:c.numerator%P*pow(c.denominator,-1,P)%P for m,c in col.items()}
  v={m:c for m,c in v.items()if c}
  while v:
   m=min(v)
   if m not in basis:
    leading=v[m];inv=pow(leading,-1,P)
    basis[m]={n:c*inv%P for n,c in v.items()}
    pivots.append([j,list(m),leading]);trace.update(json.dumps(pivots[-1],separators=(',',':')).encode())
    break
   c=v[m]
   for n,a in basis[m].items():
    b=(v.get(n,0)-c*a)%P
    if b:v[n]=b
    else:v.pop(n,None)
 return len(basis),pivots,trace.hexdigest()

def main():
 start=time.perf_counter();rec=LIVE/'upstream/data/one-reflection-skew/instance.rec'
 fields={};key=None
 for line in rec.read_text().splitlines():
  if line and not line[0].isspace() and ':'in line:key,val=line.split(':',1);fields[key]=val.strip()
  elif key in ('F','A')and line.startswith('  '):fields[key]+=' '+line.strip()
 F,A=parse(fields['F']),parse(fields['A']);parts=[diff(F,i)for i in range(6)]
 expected=[37,132,357,812,1623,2928,4863];results=[]
 for d in range(7):
  begin=time.perf_counter();jac=[shift(g,m)for g in parts for m in monos(d+1)];ad=[shift(A,m)for m in monos(d)]
  rank,pivots,digest=rank_columns(jac+ad)
  assert rank==expected[d],(d,rank,expected[d])
  jr=6*comb(d+6,5)-(15*comb(d+1,5)if d>=4 else 0)
  ker_bound=len(ad)+jr-rank
  assert ker_bound==([0]*5+[6,36])[d]
  item={'degree':d,'rows':comb(d+11,5),'jacobian_columns':len(jac),'AD_columns':len(ad),'prime':P,'augmented_rank':rank,
   'gradient_regular_sequence_Jacobian_rank':jr,'char0_E1_kernel_upper_bound':ker_bound,
   'pivots':pivots,'pivot_trace_sha256':digest,'elapsed_seconds':time.perf_counter()-begin}
  results.append(item);print(json.dumps({k:v for k,v in item.items()if k not in ('pivots','pivot_trace_sha256')}),flush=True)
 out={'status':'PASS','schema':'independent-skew-E1-modular-rank-v1','source_sha256':sha(rec),'script_lf_sha256':sha(Path(__file__)),
  'parser_lf_sha256':sha(Path(__file__).with_name('check_exclusions.py')),'prime':P,'degrees':results,
  'justification':'Nonzero modular pivots give characteristic-zero augmented-rank lower bounds. The separately checked smoothness argument gives the regular gradient sequence and the exact Jacobian rank. Explicit natural E1 lifts attain the displayed kernel bounds (zero, six, thirty-six). No finite-field-only nonmembership transfer is used.',
  'elapsed_seconds':time.perf_counter()-start}
 (OUT/'modular-e1.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
if __name__=='__main__':main()
