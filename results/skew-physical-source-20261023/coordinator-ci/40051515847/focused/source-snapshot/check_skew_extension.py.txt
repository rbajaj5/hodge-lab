"""Bounded new-module audit, reusing the pinned checkpoint-120 coefficient proof.

Run python3 -O check_skew_extension.py from formal. No network/cache fetch.
120 seconds per command, 600 seconds total; required tests use explicit failures.
"""
from pathlib import Path
from fractions import Fraction
import ast, datetime, hashlib, json, os, re, shlex, subprocess, sys, time

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results/skew-extension'
PREFIX='HodgeLab.OneReflectionSkew.'
MODULES=[PREFIX+'DegreeFour',PREFIX+'CoordinateComparison']
DEGREE_NAMES=['monomial_injective','exponent_monomial_injective','support_degree_four_coverage',
 'degree_four_expansion','componentOperator_basis','componentOperator_C_mul','componentOperator_sum',
 'componentOperator_degree_four','fullOperator_degree_four','no_degree_four_solution']
COORD_NAMES=['mixed_flip0','mixed_flip1','mixed_flip2','skew_flip0_defect','skew_flip1',
 'skew_flip2_defect','source_flip0','source_flip1','source_flip2','coordinates_flip0',
 'seed_chart','seed_values','no_pointwise_factorization']
NAMES=[PREFIX+x for x in DEGREE_NAMES]+[PREFIX+'CoordinateComparison.'+x for x in COORD_NAMES]
SOURCES=['lean-toolchain','lakefile.toml','lake-manifest.json','check_skew_extension.py',
 'AuditSkewExtension.lean','ReplaySkewExtension.lean']+[m.replace('.','/')+'.lean' for m in MODULES]
START=time.monotonic(); RECORDS=[]
if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
def require(c,m):
 if not c:raise RuntimeError(m)
def digest(p):return hashlib.sha256(p.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
def write(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def run(label,command,negative=False):
 remaining=600-(time.monotonic()-START);require(remaining>1,'600-second budget exhausted')
 bound=min(120,int(remaining));execution=command
 if os.name=='nt':
  wroot='/mnt/'+ROOT.drive[0].lower()+ROOT.as_posix()[2:]
  execution=['wsl.exe','--cd',wroot,'-e','sh','-lc','exec timeout '+str(bound)+' '+shlex.join(command)]
 began=time.monotonic()
 try:
  q=subprocess.run(execution,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=bound+10)
  log=q.stdout+q.stderr;code=q.returncode
 except subprocess.TimeoutExpired as e:
  def txt(x):return x.decode('utf-8',errors='replace') if isinstance(x,bytes) else (x or '')
  log=txt(e.stdout)+txt(e.stderr);code=124
 (OUT/(label+'.log')).write_text(log,encoding='utf-8',newline='\n')
 RECORDS.append(dict(label=label,command=command,execution_command=execution,exit_code=code,
  bound_seconds=bound,elapsed_seconds=time.monotonic()-began,expected_failure=negative,
  log=label+'.log',log_lf_sha256=digest(OUT/(label+'.log'))))
 write('commands.json',RECORDS)
 print(json.dumps({'label':label,'exit_code':code,'seconds':RECORDS[-1]['elapsed_seconds']}),flush=True)
 require(code!=124,label+' timed out; not a mathematical result')
 if negative:require(code!=0 and 'error:' in log and 'is false' in log,label+' failed for the wrong reason')
 else:require(code==0,label+' failed: '+log[:1800])
 return log

ZERO=(0,)*6
def add(a,b):
 r=dict(a)
 for e,c in b.items():r[e]=r.get(e,Fraction(0))+c
 return {e:c for e,c in r.items() if c}
def mul(a,b):
 r={}
 for e,c in a.items():
  for f,d in b.items():
   k=tuple(x+y for x,y in zip(e,f));r[k]=r.get(k,Fraction(0))+c*d
 return {e:c for e,c in r.items() if c}
def parse_expression(text):
 def ev(n):
  if isinstance(n,ast.Constant) and isinstance(n.value,int):return {ZERO:Fraction(n.value)} if n.value else {}
  if isinstance(n,ast.Name):
   require(n.id in ['X0','X1','X2','Y0','Y1','Y2'],'Unknown variable')
   e=list(ZERO);e[['X0','X1','X2','Y0','Y1','Y2'].index(n.id)]=1;return {tuple(e):Fraction(1)}
  if isinstance(n,ast.UnaryOp) and isinstance(n.op,ast.USub):return {e:-c for e,c in ev(n.operand).items()}
  if isinstance(n,ast.BinOp):
   a=ev(n.left)
   if isinstance(n.op,ast.Pow):
    require(isinstance(n.right,ast.Constant) and isinstance(n.right.value,int) and 0<=n.right.value<=20,'Exponent invalid')
    r={ZERO:Fraction(1)}
    for _ in range(n.right.value):r=mul(r,a)
    return r
   b=ev(n.right)
   if isinstance(n.op,ast.Add):return add(a,b)
   if isinstance(n.op,ast.Sub):return add(a,{e:-c for e,c in b.items()})
   if isinstance(n.op,ast.Mult):return mul(a,b)
   if isinstance(n.op,ast.Div):
    require(set(b)=={ZERO} and b[ZERO]!=0,'Only nonzero scalar division allowed')
    return {e:c/b[ZERO] for e,c in a.items()}
  raise RuntimeError('Unsupported expression syntax')
 return ev(ast.parse(text,mode='eval').body)
def expression_from_rec(text,key):
 lines=text.splitlines();i=next(i for i,s in enumerate(lines) if s.startswith(key+':'))
 value=lines[i].split(':',1)[1].strip();i+=1
 while i<len(lines) and lines[i].startswith(' '):value+=' '+lines[i].strip();i+=1
 return value
def lean_expression(terms):
 out=[]
 for c,e in terms:
  q=Fraction(c);co=f'({q.numerator} : K)' if q.denominator==1 else f'(({q.numerator} : K) / {q.denominator})'
  factors=[f'p {i}'+(f' ^ {n}' if n>1 else '') for i,n in enumerate(e) if n]
  out.append(' * '.join([co]+factors))
 return ' +\n  '.join(out)
def bind_inputs():
 pins=json.loads((OUT/'inputs.json').read_text(encoding='utf-8'))['pins']
 for pin in pins:
  raw=(ROOT.parent/pin['path']).read_bytes().replace(b'\r\n',b'\n')
  require(hashlib.sha256(raw).hexdigest()==pin['sha256'],'Input SHA256 mismatch')
  require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==pin['git_blob'],'Input Git blob mismatch')
 source=(ROOT/'HodgeLab/OneReflectionSkew/CoordinateComparison.lean').read_text(encoding='utf-8')
 report=[]
 for target,name in [('one-reflection-skew','skew'),('mixed-polar','mixed')]:
  paths={Path(x['upstream_path']).name:ROOT.parent/x['path'] for x in pins if '/'+target+'/' in x['upstream_path']}
  record=json.loads(paths['record.json'].read_text(encoding='utf-8'));rec=paths['instance.rec'].read_text(encoding='utf-8')
  require(record['q']==1 and expression_from_rec(rec,'q')=='1','Unexpected pole order')
  for key in ['F','A']:
   terms=record[key]['terms'];expected={tuple(e):Fraction(c) for c,e in terms}
   require(len(expected)==len(terms),'Duplicate structured terms require explicit summation')
   require(parse_expression(expression_from_rec(rec,key))==expected,'REC/JSON polynomial mismatch')
   definition=f'def {name}{key} (p : Fin 6 → K) : K :=\n  '+lean_expression(terms)
   # Exact source segment equality, not merely an occurrence of the expected text.
   actual=source.split(f'def {name}{key} ',1)[1].split('\ndef ',1)[0].strip()
   require('def '+name+key+' '+actual==definition,'Lean polynomial differs from protected terms')
   report.append({'target':target,'polynomial':key,'terms':len(terms),'rec_json_lean_binding':'PASS'})
 write('source-binding.json',{'status':'PASS','variable_order':['X0','X1','X2','Y0','Y1','Y2'],
  'coefficient_field':'rational input; Lean statements over fields with indicated hypotheses',
  'files_hash_checked':len(pins),'polynomials':report,'limits':'Hash checks of accepted Lean files do not replay those files.'})

def main():
 OUT.mkdir(parents=True,exist_ok=True);write('validation.json',{'status':'IN_PROGRESS'})
 source_hashes={s:digest(ROOT/s) for s in SOURCES}
 for s in SOURCES:
  if s.endswith('.lean'):require(not re.search(r'\b(sorry|admit|axiom|native_decide)\b',(ROOT/s).read_text(encoding='utf-8')),'Unproved token '+s)
 bind_inputs()
 prior=json.loads((ROOT/'results/skew-lean/validation.json').read_text(encoding='utf-8'))
 require(prior['status']=='PASS','Prior coefficient proof receipt missing')
 reused={n:h for n,h in prior['source_lf_sha256'].items() if n.endswith('.lean') and not n.startswith(('Audit','Replay'))}
 for n,h in reused.items():require(digest(ROOT/n)==h,'Reused proof source changed '+n)
 version=run('version',['lake','env','lean','--version']);require('version 4.31.0,' in version,'Wrong Lean version')
 manifest=json.loads((ROOT/'lake-manifest.json').read_text(encoding='utf-8'))
 rev=next(x['rev'] for x in manifest['packages'] if x['name']=='mathlib')
 require(run('mathlib-head',['git','-C','.lake/packages/mathlib','rev-parse','HEAD']).strip()==rev,'Mathlib mismatch')
 run('build',['lake','build',*MODULES])
 audit=run('axioms',['lake','env','lean','AuditSkewExtension.lean'])
 axioms={n:[x.strip() for x in a.split(',') if x.strip()] for n,a in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]",audit)}
 for n in re.findall(r"'([^']+)' does not depend on any axioms",audit):axioms[n]=[]
 require(set(axioms)==set(NAMES),'Missing or unexpected theorem reports')
 require(all(set(xs)<={'propext','Classical.choice','Quot.sound'} for xs in axioms.values()),'Unexpected axiom')
 replay=run('kernel-replay',['lake','env','lean','ReplaySkewExtension.lean'])
 require(all('PASS '+m in replay for m in MODULES),'Replay marker missing')
 negatives={
  'wrong-skew-symmetry':'''import HodgeLab.OneReflectionSkew.CoordinateComparison
open HodgeLab.OneReflectionSkew.CoordinateComparison
example : skewF (flip0 seed : Fin 6 → ℚ) = skewF (seed : Fin 6 → ℚ) := by
  rw [(seed_values (K:=ℚ)).1, (seed_values (K:=ℚ)).2]
  decide +kernel
''',
  'degree-five-inclusion':'''import HodgeLab.OneReflectionSkew.DegreeFour
open HodgeLab.OneReflectionSkew
set_option maxRecDepth 100000 in
example : ∃ k : Fin 70, monomial k = exp 5 0 0 0 := by decide +kernel
''',
  'unused-variable-inclusion':'''import HodgeLab.OneReflectionSkew.DegreeFour
open HodgeLab.OneReflectionSkew
set_option maxRecDepth 100000 in
example : ∃ k : Fin 70, monomial k = ![0,0,0,0,1] := by decide +kernel
'''}
 scratch=ROOT/'.lake/skew-extension-negative';scratch.mkdir(parents=True,exist_ok=True)
 for name,body in negatives.items():
  p=scratch/(name+'.lean');p.write_text(body,encoding='utf-8',newline='\n')
  (OUT/(name+'.lean.txt')).write_bytes(p.read_bytes())
  run(name,['lake','env','lean',p.relative_to(ROOT).as_posix()],True)
 require(source_hashes=={s:digest(ROOT/s) for s in SOURCES},'Sources changed during run')
 artifacts={m:hashlib.sha256((ROOT/'.lake/build/lib/lean'/(m.replace('.','/')+'.olean')).read_bytes()).hexdigest() for m in MODULES}
 write('validation.json',{'status':'PASS','completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'lean_version':version.strip(),'mathlib_commit':rev,'source_lf_sha256':source_hashes,
  'reused_source_lf_sha256':reused,'artifact_sha256':artifacts,'theorem_axioms':axioms,
  'commands':RECORDS,'elapsed_seconds':time.monotonic()-START,'total_budget_seconds':600,
  'new_theorems':len(NAMES),'new_modules_replayed':len(MODULES),'negative_controls':len(negatives),
  'scope':'Arbitrary degree-four numerators with absent fifth coordinate; exact paired-sign comparison.',
  'limits':['Same fixed denominator a and prior bounded exclusion; no new search coverage',
   'No formal protected-source transport, rational primitive or HasCertificate',
   'Pointwise chart witness is off the hypersurface and does not exclude rational correspondences',
   'No replay of accepted mixed-polar proof or imported mathlib; existing coefficient proof reused',
   'No 45-versus-504 comparison']})
 print('PASS: 23 theorem audits, two new-module replays, three rejected false statements')

if __name__=='__main__':
 try:main()
 except Exception as error:
  OUT.mkdir(parents=True,exist_ok=True);write('validation.json',{'status':'FAIL','error':str(error),'commands':RECORDS})
  raise
