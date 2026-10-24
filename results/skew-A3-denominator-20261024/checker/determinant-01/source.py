"""Bounded Bareiss certificate after independently reconstructed A3 matrix.

This phase checks the binding to reconstruction output, then computes the new
determinant. It does not count file-hash binding as source reconstruction.
"""
from pathlib import Path
import datetime,hashlib,json,sys,time
import numpy as np

start=time.monotonic();out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
author=Path(sys.argv[2]).resolve();reconstruction=Path(sys.argv[3]).resolve()
r=json.loads((reconstruction/'validation.json').read_text(encoding='utf-8'))
if r['status']!='PASS_INDEPENDENT_A3_MATRIX_RECONSTRUCTION':raise RuntimeError('Reconstruction not passed')
for name,key in [('augmented-matrix.csv','matrix_sha256'),('inputs.json','inputs_sha256'),('validation.json','author_validation_sha256')]:
    if hashlib.sha256((author/name).read_bytes()).hexdigest()!=r[key]:raise RuntimeError('Reconstructed matrix binding changed')
a=json.loads((author/'validation.json').read_text(encoding='utf-8'));p=r['prime']
if p!=32003 or (a['rank_coefficient'],a['rank_augmented'])!=(2400,2401):raise RuntimeError('Full coefficient-rank gate failed')
B=np.loadtxt(author/'augmented-matrix.csv',delimiter=',',dtype=np.int64)
selected=a['pivot_source_rows']
if B.shape!=tuple(r['matrix_shape']) or B.shape[1]!=2401:raise RuntimeError('Shape gate failed')
if len(selected)!=2401 or len(set(selected))!=2401 or min(selected)<0 or max(selected)>=len(B):raise RuntimeError('Invalid minor rows')
H=B[selected,:].copy();previous=1;sign=1
if 2*(p-1)**3>=2**63:raise RuntimeError('Integer overflow guard failed')
for k in range(2400):
    nz=np.flatnonzero(H[k:,k])
    if not len(nz):raise RuntimeError('Claimed minor singular')
    j=k+int(nz[0])
    if j!=k:H[[k,j]]=H[[j,k]];sign=-sign
    pivot=int(H[k,k])
    H[k+1:,k+1:]=((pivot*H[k+1:,k+1:]-H[k+1:,k,None]*H[k,k+1:])*pow(previous,-1,p))%p
    H[k+1:,k]=0;previous=pivot
det=sign*int(H[-1,-1])%p
if not det:raise RuntimeError('Zero augmented determinant')
inversions=sum(selected[i]>selected[j] for i in range(len(selected)) for j in range(i+1,len(selected)))
first=set(selected)==set(range(len(selected)))
original_det=((-1 if inversions%2 else 1)*det)%p if first else None
result={'status':'PASS_EXACT_QQ_A3_SUM_FINITE_FAMILY_EXCLUSION','executor':'a3_denominator_checker AI worker','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seconds':time.monotonic()-start,'python':sys.version,'numpy':np.__version__,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'reconstruction_receipt_sha256':hashlib.sha256((reconstruction/'validation.json').read_bytes()).hexdigest(),'matrix_sha256':r['matrix_sha256'],'matrix_shape':list(B.shape),'prime':p,'rank_coefficient':2400,'rank_augmented':2401,'independent_augmented_minor_det_mod_prime':det,'are_first_rows_as_set':first,'permutation_inversions':inversions,'first_rows_original_order_det_mod_prime':original_det,'scope':'New mathematical Bareiss determinant on already independently reconstructed matrix. Hashes bind phases but are not additional mathematical reconstruction. Full2401 minor excludes2400 necessary parameters over QQ; original2808 family uses imported highest-pole/support theorem, including for homogeneous kernels. No lower tangency or earlier A2 projection assumed. No general rational-current exclusion or primitive.'}
(out/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
(out/'minor-row-order.json').write_text(json.dumps({'selected_rows':selected,'are_first_rows_as_set':first,'permutation_inversions':inversions,'first_rows_original_order_det_mod_prime':original_det},indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
