from pathlib import Path
import hashlib,json,re
R=Path(__file__).resolve().parents[3]; F=R/'formal'
module='HodgeLab.OneReflectionSkew.GenericDistinctRoots'
s=(F/(module.replace('.','/')+'.lean')).read_text()
decls=re.findall(r'^(?:def|abbrev|theorem) (\w+)',s,re.M)
(F/'AuditSkewDistinctRoots.lean').write_text('import '+module+'\n\n'+'\n'.join('#print axioms '+module+'.'+n for n in decls)+'\n',encoding='utf-8')
(F/'ReplaySkewDistinctRoots.lean').write_text('''import LeanChecker

-- Replay only the new generic distinct-root module; prior proofs are reused.
#eval do
  Lean.initSearchPath (← Lean.findSysroot)
  replayFromImports `HodgeLab.OneReflectionSkew.GenericDistinctRoots
  IO.println "PASS HodgeLab.OneReflectionSkew.GenericDistinctRoots"
  (← IO.getStdout).flush
''',encoding='utf-8')
H=F/'results/skew-distinct-roots'; H.mkdir(exist_ok=True)
def digest(p): return hashlib.sha256(p.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
context=['formal/results/skew-trace-basis/validation.json','formal/results/skew-physical-cover/inputs.json','results/ci-receipt-physical-cover-20261023/lean-development/checker-01/validation.json']
source_path='results/skew-distinct-roots-20261023/source-pins.json'
pins=json.loads((R/source_path).read_text())
inputs={'notebook_parent':pins['notebook_parent'],'upstream_commit':pins['upstream_commit'],
 'context_receipt_lf_sha256':{p:digest(R/p) for p in context},
 'physical_source_pins':pins['pins'],
 'source_pins_manifest':{'path':source_path,'sha256':hashlib.sha256((R/source_path).read_bytes()).hexdigest()},
 'previous_physical_receipt':context[-1],
 'literal_definition_lean':'X ^ 18 + X ^ 12 + (C v * X - 1) ^ 6 - C a * X ^ 15',
 'mathematical_scope':{'base_field':'Q(v)(t)(a), explicit iterated RatFunc tower',
 'v':'RatFunc.X in Q(v), embedded into Q(v)(t)(a)',
 't':'RatFunc.X in Q(v)(t), embedded into Q(v)(t)(a)',
 'a':'RatFunc.X in Q(v)(t)(a), transcendental over Q(v)(t)',
 'extension':'genericPolynomial.SplittingField, with canonical injective field embeddings',
 'new_hypothesis_closed':'generic separability and an injective Fin 18 root tuple with all root equations',
 'specialization_limit':'a=2,v=1 over Q has repeated root1; generic distinctness is not universal',
 'excluded':['unsplit descent','physical differential source normalization','primitive','HasCertificate','target solve']}}
(H/'inputs.json').write_text(json.dumps(inputs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'public_declarations':len(decls),'declarations':decls},indent=2))
