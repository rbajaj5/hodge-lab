"""Read-only provenance checks; no symbolic computation."""
import argparse,hashlib,json,pathlib
p=argparse.ArgumentParser();p.add_argument('--pro-root',required=True,type=pathlib.Path);args=p.parse_args()
root=pathlib.Path(__file__).resolve().parent;batch=args.pro_root/'results/skew-mixed-construction-20261024'
sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest();read=lambda x:json.loads(x.read_text(encoding='utf-8'))
checks=[]
def match(name,actual,expected):
 if actual!=expected:raise ValueError(name)
 checks.append({'name':name,'status':'pass','sha256':actual if isinstance(actual,str) and len(actual)==64 else None})
structure=read(batch/'alternate/first-jet-cert-02/validation.json')
author=read(batch/'alternate/first-jet-result-01/validation.json')
checker=read(batch/'checker/first-jet-system-02/result/validation.json')
match('structure source to saved receipt',sha(batch/'alternate/certify_first_jet_structure.py'),structure['script_sha256'])
match('author system-builder source to saved receipt',sha(batch/'alternate/test_universal_first_jet.py'),author['script_sha256'])
match('Pro checker source to saved receipt',sha(batch/'checker/check_first_jet_system.py'),checker['script_sha256'])
match('author system to checker input binding',sha(batch/'alternate/first-jet-result-01/system.json'),checker['author_system_sha256'])
match('author validation to structure reused binding',sha(batch/'alternate/first-jet-result-01/validation.json'),structure['reused_system_validation_sha256'])
match('replayed checker bytes unchanged',sha(root/'replay-inputs/results/skew-mixed-construction-20261024/checker/check_first_jet_system.py'),sha(batch/'checker/check_first_jet_system.py'))
match('replay left-null certificate JSON equals Pro certificate JSON',read(root/'replay-01/result/left-null-certificate.json'),read(batch/'checker/first-jet-system-02/result/left-null-certificate.json'))
record={'status':'pass','scope':'source/hash/parsed-JSON comparison only; not a mathematical replay','checks':checks}
(root/'source-bindings-review.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print(json.dumps(record,indent=2))
