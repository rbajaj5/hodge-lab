"""Exact modular CUDA rejection screen for a hodge.computer witness identity.

Run: python experiments/gpu_identity_screen.py
Reads sources/sextics and writes an input snapshot and report.
Install CuPy or set HODGE_CUDA_DEPS for an existing isolated CUDA installation.

This prototype screens a supplied candidate; it does not search for witnesses,
prove denominator admissibility, or replace the repository's protected Lean
acceptance pipeline. A nonzero modular residual rejects the rational polynomial
identity. Passing finitely many tests is not a proof of the complex certificate.
"""
import argparse
import ast
import datetime as dt
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time

VARIABLES=('X0','X1','X2','Y0','Y1','Y2')
ZERO=(0,)*6
P=65521


def source_sha256(path):
    """Hash source text consistently across Windows and Unix checkouts."""
    return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()

def add(a,b):
    out=a.copy()
    for k,c in b.items():
        out[k]=out.get(k,Fraction(0))+c
        if not out[k]:del out[k]
    return out
def scale(a,c):return {k:v*c for k,v in a.items() if v*c}
def mul(a,b):
    out={}
    for x,c in a.items():
        for y,d in b.items():
            k=tuple(i+j for i,j in zip(x,y))
            out[k]=out.get(k,Fraction(0))+c*d
    out={k:v for k,v in out.items() if v}
    if len(out)>100000:raise ValueError('Polynomial term safety bound exceeded')
    return out
def power(a,k):
    out={ZERO:Fraction(1)}
    for _ in range(k):out=mul(out,a)
    return out
def derivative(a,i):
    out={}
    for k,c in a.items():
        if k[i]:
            exp=list(k);exp[i]-=1;out[tuple(exp)]=c*k[i]
    return out

def parse_polynomial(text):
    """Whitelisted AST only: exact integers, six names, +-*/, integer powers."""
    if not isinstance(text,str) or len(text)>100000:raise ValueError('Bad expression length')
    tree=ast.parse(text,mode='eval')
    if sum(1 for _ in ast.walk(tree))>10000:raise ValueError('Expression too complex')
    def walk(n):
        if isinstance(n,ast.Constant) and type(n.value) is int:return {ZERO:Fraction(n.value)} if n.value else {}
        if isinstance(n,ast.Name) and n.id in VARIABLES:
            e=[0]*6;e[VARIABLES.index(n.id)]=1;return {tuple(e):Fraction(1)}
        if isinstance(n,ast.UnaryOp) and isinstance(n.op,(ast.UAdd,ast.USub)):
            return scale(walk(n.operand),-1 if isinstance(n.op,ast.USub) else 1)
        if isinstance(n,ast.BinOp):
            a=walk(n.left)
            if isinstance(n.op,ast.Pow):
                if not isinstance(n.right,ast.Constant) or type(n.right.value) is not int or not 0<=n.right.value<=32:
                    raise ValueError('Only bounded nonnegative integer powers are allowed')
                return power(a,n.right.value)
            b=walk(n.right)
            if isinstance(n.op,ast.Add):return add(a,b)
            if isinstance(n.op,ast.Sub):return add(a,scale(b,-1))
            if isinstance(n.op,ast.Mult):return mul(a,b)
            if isinstance(n.op,ast.Div) and set(b)=={ZERO} and b[ZERO]:return scale(a,1/b[ZERO])
        raise ValueError(f'Disallowed polynomial syntax: {type(n).__name__}')
    result=walk(tree.body)
    if any(max(e)>255 for e in result):raise ValueError('Exponent safety bound exceeded')
    return result

def load_target(folder):
    # These records use plain scalar F/A/q fields; fold their indented
    # continuation lines, then cross-check against the generated JSON.
    record=json.loads((folder/'record.json').read_text(encoding='utf-8'))
    raw={};current=None
    for line in (folder/'instance.rec').read_text(encoding='utf-8').splitlines():
        if line.startswith((' ', '\t')):
            if current is not None:raw[current]+=' '+line.strip()
            continue
        current=None
        for key in ['F','A','q']:
            if line.startswith(key+': '):
                current=key;raw[key]=line[len(key)+2:]
    if set(raw)!={'F','A','q'}:raise ValueError('Missing exact instance fields')
    F,A=parse_polynomial(raw['F']),parse_polynomial(raw['A'])
    q=int(raw['q'])
    if q not in (1,2):raise ValueError('This prototype supports the standing q=1,2 targets')
    if F!=parse_polynomial(record['F']['expression']) or A!=parse_polynomial(record['A']['expression']) or q!=record['q']:
        raise ValueError('Immutable instance and generated record disagree')
    return {'id':folder.name,'F':F,'A':A,'q':q,'raw':raw,'record_status':record.get('status')}

def symbolic_residual(case):
    F,A,D,N,Q,q=(case[k] for k in ['F','A','D','N','Q','q'])
    nf={};div={};nd={}
    for i in range(6):
        nf=add(nf,mul(N[i],derivative(F,i)))
        div=add(div,derivative(N[i],i))
        nd=add(nd,mul(N[i],derivative(D,i)))
    return add(add(mul(A,mul(D,D)),scale(mul(D,nf),-q)),
               add(mul(F,add(mul(D,div),scale(nd,-1))),scale(mul(power(F,q+1),Q),-1)))

def modcoeff(c):
    den=c.denominator%P
    if den==0:raise ValueError('Prime divides a rational coefficient denominator')
    return c.numerator%P*pow(den,-1,P)%P

def cpu_eval(poly,point):
    total=0
    for exp,coefficient in poly.items():
        v=modcoeff(coefficient)
        for x,k in zip(point,exp):v=v*pow(int(x),k,P)%P
        total=(total+v)%P
    return total

def case_polys(case):
    F,A,D,N,Q=(case[k] for k in ['F','A','D','N','Q'])
    return [A,F,D,Q]+N+[derivative(F,i) for i in range(6)]+[derivative(N[i],i) for i in range(6)]+[derivative(D,i) for i in range(6)]

CUDA=r'''
const long long PRIME=65521;
__device__ long long poly(const int k,const int* offsets,const long long* coeff,
 const unsigned char* exponents,const long long* x){
 long long total=0;
 for(int j=offsets[k];j<offsets[k+1];j++){
  long long v=coeff[j];
  for(int d=0;d<6;d++)for(int r=0;r<exponents[6*j+d];r++)v=(v*x[d])%PRIME;
  total=(total+v)%PRIME;
 }
 return total;
}
extern "C" __global__ void residuals(const int n,const int cases,const long long* points,
 const int* offsets,const long long* coeff,const unsigned char* exponents,const int* q,long long* out){
 int id=blockDim.x*blockIdx.x+threadIdx.x;
 if(id>=n*cases)return;
 int c=id/n,s=id%n,base=28*c;
 const long long* x=points+6*s;
 long long a=poly(base,offsets,coeff,exponents,x);
 long long f=poly(base+1,offsets,coeff,exponents,x);
 long long d=poly(base+2,offsets,coeff,exponents,x);
 long long quotient=poly(base+3,offsets,coeff,exponents,x);
 long long nf=0,div=0,nd=0;
 for(int i=0;i<6;i++){
  long long ni=poly(base+4+i,offsets,coeff,exponents,x);
  nf=(nf+ni*poly(base+10+i,offsets,coeff,exponents,x)%PRIME)%PRIME;
  div=(div+poly(base+16+i,offsets,coeff,exponents,x))%PRIME;
  nd=(nd+ni*poly(base+22+i,offsets,coeff,exponents,x)%PRIME)%PRIME;
 }
 long long t1=((a*d)%PRIME*d)%PRIME;
 long long t2=(((q[c]%PRIME)*d)%PRIME*nf)%PRIME;
 long long t3=f*((d*div)%PRIME+PRIME-nd)%PRIME;
 long long fp=1;for(int r=0;r<q[c]+1;r++)fp=fp*f%PRIME;
 long long t4=fp*quotient%PRIME;
 out[id]=(t1+PRIME-t2+t3+PRIME-t4)%PRIME;
}
'''

def load_cupy(deps=None):
    """Use the active CuPy environment, or an explicit isolated dependency tree."""
    handles=[]
    configured=deps or os.environ.get('HODGE_CUDA_DEPS')
    if configured:
        deps=Path(configured).resolve()
        if not deps.is_dir():raise FileNotFoundError(deps)
        sys.path.insert(0,str(deps))
        runtime=deps/'nvidia/cuda_runtime'
        if runtime.is_dir():os.environ['CUDA_PATH']=str(runtime)
        os.environ.setdefault('CUPY_CACHE_DIR',str(deps.parent/'cupy_cache'))
        bins=[p.resolve() for p in (deps/'nvidia').glob('*/bin')]
        if os.name=='nt':handles=[os.add_dll_directory(str(p)) for p in bins]
        os.environ['PATH']=os.pathsep.join(map(str,bins))+os.pathsep+os.environ['PATH']
    import cupy as cp
    return cp,handles

def main():
    import numpy as np
    workspace=Path(__file__).resolve().parents[1]
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',type=Path,default=workspace/'sources/sextics')
    parser.add_argument('--deps',type=Path,default=None)
    parser.add_argument('--output',type=Path,default=workspace/'results/gpu-identity-screen')
    parser.add_argument('--points',type=int,default=4096)
    parser.add_argument('--seed',type=int,default=2026101665521)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    accepted=args.repo/'data/fermat-pair-rational-d4-strict'
    holdout=args.repo/'data/holdout'
    target=load_target(accepted);other=load_target(holdout)
    witness=json.loads((accepted/'witness.json').read_text())
    D=parse_polynomial(witness['D']);N=[parse_polynomial(s) for s in witness['N']];Q=parse_polynomial(witness['Q'])
    if len(N)!=6:raise ValueError('Need six numerator components')
    mutation='X0**4*Y0/6'
    altered=N.copy();altered[0]=add(altered[0],parse_polynomial(mutation))
    cases=[{**target,'label':'accepted_fermat_baseline','D':D,'N':N,'Q':Q},
           {**target,'label':'perturbed_numerator','D':D,'N':altered,'Q':Q},
           {**other,'label':'fermat_witness_on_holdout','D':D,'N':N,'Q':Q}]
    # Verify the parser has no execution path through calls/attributes/etc.
    rejected=0
    for bad in ["__import__('os')","X0.__class__","[X0]","X0[0]","X0**-1","0.5*X0"]:
        try:parse_polynomial(bad)
        except ValueError:rejected+=1
        else:raise AssertionError('Unsafe syntax was accepted')
    exact=[symbolic_residual(c) for c in cases]
    assert not exact[0] and exact[1] and exact[2]
    allpolys=[p for case in cases for p in case_polys(case)]
    offsets=[0];coeff=[];exp=[]
    for poly in allpolys:
        for e,c in sorted(poly.items()):coeff.append(modcoeff(c));exp.append(e)
        offsets.append(len(coeff))
    rng=np.random.default_rng(args.seed)
    points=rng.integers(0,P,size=(args.points,6),dtype=np.int64)
    cp,dll_handles=load_cupy(args.deps)
    gpu_points=cp.asarray(points);gpu_offsets=cp.asarray(offsets,dtype=cp.int32)
    gpu_coeff=cp.asarray(coeff,dtype=cp.int64);gpu_exp=cp.asarray(exp,dtype=cp.uint8)
    gpu_q=cp.asarray([c['q'] for c in cases],dtype=cp.int32)
    result=cp.empty((len(cases),args.points),dtype=cp.int64)
    kernel=cp.RawKernel(CUDA,'residuals')
    def launch():kernel(((result.size+127)//128,),(128,),
        (np.int32(args.points),np.int32(len(cases)),gpu_points,gpu_offsets,gpu_coeff,gpu_exp,gpu_q,result))
    for _ in range(3):launch()
    cp.cuda.Device().synchronize()
    timings=[]
    for _ in range(9):
        cp.cuda.Device().synchronize();start=time.perf_counter();launch();cp.cuda.Device().synchronize()
        timings.append((time.perf_counter()-start)*1000)
    values=cp.asnumpy(result)
    reports=[]
    spot_indices=np.unique(np.r_[np.arange(min(24,args.points)),rng.choice(args.points,min(40,args.points),replace=False)])
    for i,(case,residual) in enumerate(zip(cases,exact)):
        # Independent CPU path evaluates expanded rational residual using Python big ints.
        for j in spot_indices:assert int(values[i,j])==cpu_eval(residual,points[j])
        bad=np.flatnonzero(values[i])
        degree=max((sum(e) for e in residual),default=0)
        nonzero_modp=any(modcoeff(c) for c in residual.values())
        example=None
        if len(bad):
            j=int(bad[0]);example={'point_index':j,'point':points[j].tolist(),'residue':int(values[i,j])}
        sampleterms=[{'coefficient':str(c),'exponents':list(e)} for e,c in sorted(residual.items())[:3]]
        reports.append({'label':case['label'],'target_instance':case['id'],
            'nonzero_residual_count':int(len(bad)),'zero_residual_count':int(args.points-len(bad)),
            'gpu_result':'rejected' if len(bad) else 'passed sampled identity checks',
            'exact_QQ_residual_is_zero':not bool(residual),'exact_QQ_residual_term_count':len(residual),
            'residual_total_degree':degree,'residual_nonzero_mod_p':nonzero_modp,
            'first_modular_counterexample':example,'first_exact_nonzero_terms':sampleterms,
            'cpu_spotchecks':len(spot_indices),'all_cpu_spotchecks_match':True,
            'conditional_single_point_false_pass_bound':degree/P if nonzero_modp else None,
            'conditional_all_points_false_pass_log10_bound':args.points*math.log10(degree/P) if nonzero_modp and degree else None})
    assert reports[0]['nonzero_residual_count']==0
    assert reports[1]['nonzero_residual_count']>0 and reports[2]['nonzero_residual_count']>0
    commit=subprocess.check_output(['git','-C',str(args.repo),'rev-parse','HEAD'],text=True).strip()
    sources={}
    for folder in [accepted,holdout]:
        for filename in ['instance.rec','record.json','witness.json','acceptance.json']:
            path=folder/filename
            if path.exists():sources[path.relative_to(args.repo).as_posix()]=source_sha256(path)
    snapshot={'repository':'https://github.com/hodge-computer/sextics','commit':commit,
        'variables':VARIABLES,'accepted_target':target['raw'],'holdout_target':other['raw'],
        'accepted_witness':witness,'mutation':{'component':'N[0]','added_term':mutation},'sha256':sources}
    (args.output/'input-snapshot.json').write_text(json.dumps(snapshot,indent=2))
    props=cp.cuda.runtime.getDeviceProperties(0)
    report={'schema_version':1,'created_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
        'experiment':'CUDA exact finite-field witness identity rejection baseline',
        'repository':snapshot['repository'],'repository_commit':commit,'input_sha256':sources,
        'identity':'A D^2 - q D sum_i N_i F_i + F(D sum_i partial_i N_i - sum_i N_i D_i) - F^(q+1) Q',
        'prime':P,'point_count_per_case':args.points,'point_seed':args.seed,
        'sampling':'Independent uniform samples from F_p^6 generated by NumPy PCG64, shared across candidate comparisons.',
        'arithmetic':'Exact rational parsing; coefficients reduced by modular inverses; signed int64 CUDA arithmetic reduced after every multiply. Largest raw modular product <2*p^2 <2^34, safely below 2^63.',
        'hardware':{'gpu':props['name'].decode(),'cupy':cp.__version__,'cuda_runtime_version':cp.cuda.runtime.runtimeGetVersion()},
        'timing':{'gpu_all_cases_median_ms':statistics.median(timings),'gpu_samples_ms':timings,
            'case_point_evaluations_per_run':len(cases)*args.points,
            'scope':'One fused kernel evaluates all 3 candidates at 4096 points each; synchronized wall-clock median of 9 warmed runs. Excludes parsing, symbolic expansion, compilation, transfers, point generation and reporting. No CPU speedup claim.'},
        'parser_rejection_checks_passed':rejected,'cases':reports,
        'probability_scope':'Schwartz-Zippel bounds require a nonzero reduced polynomial and iid uniform points. A bad prime may erase rational information; passing samples is not proof. CPU rational expansion independently proves only the displayed cleared polynomial identity or its failure.',
        'limitations':['Candidate rejection baseline, not a search for a new witness or certificate.',
            'Does not check complex coprimality of D and F, homogeneous side conditions, or the full formal statement.',
            'Accepted baseline reuses the repository witness and credits its source; no new result claimed.',
            'No Lean build or protected verifier run; no repository changes or posts.']}
    (args.output/'screen-report.json').write_text(json.dumps(report,indent=2,allow_nan=False))
    np.savez_compressed(args.output/'screen-residues.npz',points=points,residues=values,
                        labels=np.array([c['label'] for c in cases]),prime=np.array(P))
    print(json.dumps({'commit':commit,'gpu':report['hardware']['gpu'],'median_ms':statistics.median(timings),
        'cases':[{'label':r['label'],'nonzero':r['nonzero_residual_count'],'QQ_terms':r['exact_QQ_residual_term_count']} for r in reports]},indent=2))

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O; verification assertions are required.')
    main()
