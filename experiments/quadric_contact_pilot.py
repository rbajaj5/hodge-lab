#!/usr/bin/env python3
"""Complete exact fixed-quartic pilot for quadric-contact-broken.

All arithmetic and verification use Python's standard-library Fraction. The
target stays fixed. A failed test excludes this denominator, not all quartics.
"""
from __future__ import annotations
import argparse
import ast
import copy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

REPO=Path(__file__).resolve().parents[1]
OUT=REPO/'results'/'quadric-contact-pilot'
FRESH=REPO.parents[1]/'work'/'sextics-atlas-2026-10-17'
INSTANCE='quadric-contact-broken'
SOURCE_COMMIT='d96911d725077e66a8f10848908be01a643b1714'
TRIAGED_MAIN='4e920b85e0d45046a9cec2a929502aec0e56679c'
NAMES=('X0','X1','X2','Y0','Y1','Y2')
ZERO=(0,)*6


def sha(path):return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()


def save(name,value):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')


def add(a,b,scale=Q(1)):
    out=dict(a)
    for m,c in b.items():
        out[m]=out.get(m,Q(0))+scale*c
        if not out[m]:del out[m]
    return out


def mul(a,b):
    out={}
    for m,c in a.items():
        for n,d in b.items():
            power=tuple(x+y for x,y in zip(m,n));out[power]=out.get(power,Q(0))+c*d
            if not out[power]:del out[power]
    return out


def scale(a,c):return {m:v*c for m,v in a.items()if v*c}


def derivative(a,i):
    out={}
    for m,c in a.items():
        if m[i]:
            n=list(m);n[i]-=1;out[tuple(n)]=c*m[i]
    return out


def parse(text):
    def visit(node):
        if isinstance(node,ast.Constant)and type(node.value)is int:return {ZERO:Q(node.value)}if node.value else{}
        if isinstance(node,ast.Name)and node.id in NAMES:return {tuple(int(j==NAMES.index(node.id))for j in range(6)):Q(1)}
        if isinstance(node,ast.UnaryOp)and isinstance(node.op,ast.USub):return scale(visit(node.operand),-1)
        if isinstance(node,ast.BinOp):
            a=visit(node.left)
            if isinstance(node.op,ast.Pow):
                assert isinstance(node.right,ast.Constant)and type(node.right.value)is int and node.right.value>=0
                out={ZERO:Q(1)}
                for _ in range(node.right.value):out=mul(out,a)
                return out
            b=visit(node.right)
            if isinstance(node.op,ast.Add):return add(a,b)
            if isinstance(node.op,ast.Sub):return add(a,b,-1)
            if isinstance(node.op,ast.Mult):return mul(a,b)
            if isinstance(node.op,ast.Div):
                assert set(b)=={ZERO}and b[ZERO]
                return scale(a,1/b[ZERO])
        raise ValueError('Unsupported polynomial syntax: '+ast.dump(node))
    return visit(ast.parse(text,mode='eval').body)


def fields(path):
    result={};active=None
    for line in path.read_text(encoding='utf-8').splitlines():
        matched=False
        for key in ('F','A','q'):
            if line.startswith(key+': '):result[key]=line[len(key)+2:];active=key;matched=True;break
        if matched:continue
        if active in ('F','A')and line.startswith('  '):result[active]+=' '+line.strip()
        else:active=None
    return result


def encode(poly):return [{'powers':list(m),'coefficient':str(c)}for m,c in sorted(poly.items(),reverse=True)]
def decode(terms):return {tuple(t['powers']):Q(t['coefficient'])for t in terms}


def monomials(degree,n=6):
    if n==1:return [(degree,)]
    return [(a,)+tail for a in range(degree,-1,-1)for tail in monomials(degree-a,n-1)]


def freeze():
    directory=OUT/'source';directory.mkdir(parents=True,exist_ok=True)
    for name in ('instance.rec','why.md','provenance.json'):
        source=FRESH/'data'/INSTANCE/name;dest=directory/name
        if dest.exists():assert dest.read_bytes()==source.read_bytes()
        else:dest.write_bytes(source.read_bytes())
    manifest={'instance':INSTANCE,'source_snapshot_commit':SOURCE_COMMIT,'triaged_main_commit':TRIAGED_MAIN,
              'source_note':'Bytes copied from the d96911d checkout. Parent triage compared upstream through4e920b8 and found only UI/server changes, with no target or policy changes. This snapshot does not claim a fresh network fetch at4e920b8.',
              'target':fields(directory/'instance.rec'),'variables':list(NAMES),
              'source_sha256':{name:sha(directory/name)for name in ('instance.rec','why.md','provenance.json')},
              'source_urls':{name:f'https://github.com/hodge-computer/sextics/blob/{SOURCE_COMMIT}/data/{INSTANCE}/{name}'
                             for name in ('instance.rec','why.md','provenance.json')}}
    save('target.json',manifest)


def physical_system():
    manifest=json.loads((OUT/'target.json').read_text(encoding='utf-8'))
    record=fields(OUT/'source'/'instance.rec')
    assert manifest['target']==record and record['q']=='1'
    for name,value in manifest['source_sha256'].items():assert sha(OUT/'source'/name)==value
    F=parse(record['F']);A=parse(record['A'])
    D=parse('4*(X0**2+Y0**2)*X0*Y0+5*X1*Y1*(X2**2+2*Y2**2)/7')
    h=parse('X1**2*X0*Y0');N=[{}, {}, {}, {}, {}, {}]
    N[0]=scale(mul(h,parse('Y0')),-1);N[3]=mul(h,parse('X0'))
    partials=[derivative(F,i)for i in range(6)];Dd=[derivative(D,i)for i in range(6)]
    normal={};divergence={};ND={}
    for i in range(6):
        normal=add(normal,mul(N[i],partials[i]));divergence=add(divergence,derivative(N[i],i));ND=add(ND,mul(N[i],Dd[i]))
    assert normal==mul(A,D)
    B=add(mul(D,divergence),ND,-1)
    assert B==parse('5*X1**3*Y1*(X2**2+2*Y2**2)*(X0**2-Y0**2)/7')
    columns=[];labels=[]
    for i in range(6):
        for j in range(i+1,6):
            columns.append(add(mul(partials[i],Dd[j]),mul(partials[j],Dd[i]),-1))
            labels.append({'kind':'Koszul','indices':[i,j],'convention':'K_i=F_j,K_j=-F_i; column=B_D(K)'})
    for mon in monomials(2):
        columns.append(scale(mul(F,{mon:Q(1)}),-1));labels.append({'kind':'F_quotient','multiplier_powers':list(mon),'sign':-1})
    rhs=scale(B,-1)
    assert len(columns)==36 and all(sum(m)==8 for col in columns for m in col)
    rows=sorted(set(rhs).union(*(set(col)for col in columns)),reverse=True)
    return F,A,D,N,B,rows,columns,labels,rhs


def solve(rows,columns,rhs):
    pivots={};dual=None
    for row,mon in enumerate(rows):
        vector={j:col[mon]for j,col in enumerate(columns)if mon in col};value=rhs.get(mon,Q(0));tracking={row:Q(1)}
        while vector:
            pivot=min(vector)
            if pivot not in pivots:
                coefficient=vector[pivot]
                vector=scale(vector,1/coefficient);tracking=scale(tracking,1/coefficient);value/=coefficient
                pivots[pivot]=(vector,value,tracking);break
            old,oldvalue,oldtracking=pivots[pivot];coefficient=vector[pivot]
            vector=add(vector,old,-coefficient);tracking=add(tracking,oldtracking,-coefficient);value-=coefficient*oldvalue
        if not vector and value and dual is None:dual=scale(tracking,1/value)
    solution=None
    if dual is None:
        solution=[Q(0)]*len(columns)
        for pivot in sorted(pivots,reverse=True):
            vector,value,_=pivots[pivot]
            solution[pivot]=value-sum(c*solution[j]for j,c in vector.items()if j!=pivot)
    return len(pivots),dual,solution


def verify_dual(packet):
    columns=packet['matrix_columns'];rhs={i:Q(c)for i,c in packet['rhs_entries']}
    dual={i:Q(c)for i,c in packet['obstruction_functional']}
    for col in columns:assert sum(dual.get(i,Q(0))*Q(c)for i,c in col['entries'])==0
    assert sum(c*rhs.get(i,Q(0))for i,c in dual.items())==1


def calculate():
    start=time.perf_counter();F,A,D,N,B,rows,columns,labels,rhs=physical_system()
    rank,dual,solution=solve(rows,columns,rhs);rowindex={m:i for i,m in enumerate(rows)}
    packet={'schema':'quadric-contact-quartic-pilot-v1','instance':INSTANCE,
            'producer_sha256':sha(Path(__file__)),'frozen_target_sha256':sha(OUT/'target.json'),
            'denominator':encode(D),'initial_numerator':[encode(n)for n in N],
            'E1_identity_exact':True,'E2_initial_residual':encode(B),
            'coefficient_rows':[list(m)for m in rows],
            'matrix_columns':[dict(label,entries=[[rowindex[m],str(c)]for m,c in sorted(col.items(),reverse=True)])
                              for label,col in zip(labels,columns)],
            'rhs_entries':[[rowindex[m],str(c)]for m,c in sorted(rhs.items(),reverse=True)],
            'matrix_shape':[len(rows),len(columns)],'full_homogeneous_degree8_row_count':1287,
            'coefficient_rank':rank,'augmented_rank':rank+int(dual is not None),
            'consistent':dual is None,'obstruction_functional':[[i,str(c)]for i,c in sorted(dual.items())]if dual else None,
            'solution_coefficients':[str(c)for c in solution]if solution else None,
            'parity_note':'D is globally Y-odd; the general rational-field presentation is legal. A successful field could be rewritten over the even denominator D^2 by multiplying numerator and denominator by D. This test retains all15 constant Koszul corrections and all21 degree2 quotient monomials without narrowing by parity.',
            'scope':'Complete fixed-denominator test for this particular quarticD. It does not exclude every quartic denominator or every certificate for the target.',
            'seconds':time.perf_counter()-start}
    if dual:verify_dual(packet)
    else:
        residual={}
        for c,col in zip(solution,columns):residual=add(residual,col,c)
        assert residual==rhs
    return packet


def verify():
    packet=json.loads((OUT/'pilot.json').read_text(encoding='utf-8'));expected=calculate()
    for key in expected:
        if key!='seconds':assert packet[key]==expected[key],key
    rejected=[]
    if not packet['consistent']:
        for name in ('dual_coefficient','rhs_coefficient','matrix_coefficient'):
            bad=copy.deepcopy(packet);row=bad['obstruction_functional'][0][0]
            if name=='dual_coefficient':bad['obstruction_functional'][0][1]=str(Q(bad['obstruction_functional'][0][1])+1)
            elif name=='rhs_coefficient':bad['rhs_entries'].append([row,'1']) if row not in dict(bad['rhs_entries'])else None
            else:bad['matrix_columns'][0]['entries'].append([row,'1'])
            if name=='rhs_coefficient'and row in dict(packet['rhs_entries']):
                for entry in bad['rhs_entries']:
                    if entry[0]==row:entry[1]=str(Q(entry[1])+1);break
            try:verify_dual(bad)
            except AssertionError:rejected.append(name)
            else:raise AssertionError('Mutation accepted: '+name)
    result={'status':'PASS','packet_sha256':sha(OUT/'pilot.json'),'producer_sha256':sha(Path(__file__)),
            'standard_library_only':True,'coefficient_rank':packet['coefficient_rank'],
            'augmented_rank':packet['augmented_rank'],'consistent':packet['consistent'],
            'mutations_rejected':rejected,'certificate_found':packet['consistent']}
    save('validation.json',result);print(json.dumps(result),flush=True)


def main():
    if not __debug__:raise RuntimeError('Run without -O.')
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['freeze','run','worker','verify'])
    args=parser.parse_args()
    if args.command=='freeze':freeze();return
    if args.command=='verify':verify();return
    if args.command=='worker':
        packet=calculate();save('pilot.json',packet)
        print(json.dumps({'consistent':packet['consistent'],'rank':packet['coefficient_rank'],
                          'augmented_rank':packet['augmented_rank'],'seconds':packet['seconds']}),flush=True);return
    start=time.perf_counter()
    try:
        process=subprocess.run([sys.executable,'-S',str(Path(__file__).resolve()),'worker'],capture_output=True,text=True,timeout=120)
        result={'status':'complete'if process.returncode==0 else'error','returncode':process.returncode,'stdout':process.stdout,'stderr':process.stderr}
    except subprocess.TimeoutExpired:result={'status':'timeout','stop_reason':'120-second wall-clock bound'}
    result.update(time_limit_seconds=120,elapsed_seconds=time.perf_counter()-start)
    save('attempt.json',result);print(json.dumps(result),flush=True)
    if result['status']!='complete':raise SystemExit(1)


if __name__=='__main__':main()
