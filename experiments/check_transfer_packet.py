"""CPU-only independent replay of GPU-produced algebra rejection witnesses.

QRCert-inspired separation of candidate production and checking; this is Python,
not a Lean soundness proof. No CuPy import or GPU use occurs in this checker.
"""
from pathlib import Path
import copy, hashlib, json
import gpu_identity_screen as algebra

HERE=Path(__file__).resolve().parent
REPO=HERE.parent/'sources/sextics'
PACKET=HERE.parent/'results/leaderboard-experiments/report.json'
P=65521

def evaluate(case,point):
    def at(poly):return algebra.cpu_eval(poly,point)
    a,f,d,q=at(case['A']),at(case['F']),at(case['D']),at(case['Q'])
    nf=div=nd=0
    for i in range(6):
        ni=at(case['N'][i]);nf+=ni*at(algebra.derivative(case['F'],i))
        div+=at(algebra.derivative(case['N'][i],i));nd+=ni*at(algebra.derivative(case['D'],i))
    return a*d*d%P,(-case['q']*d*nf+f*(d*div-nd)-pow(f,case['q']+1,P)*q)%P

def check_row(row):
    source=REPO/'data'/row['source'];target=algebra.load_target(REPO/'data'/row['target'])
    witness=json.loads((source/'witness.json').read_text())
    target.update(D=algebra.parse_polynomial(witness['D']),N=[algebra.parse_polynomial(x) for x in witness['N']],Q=algebra.parse_polynomial(witness['Q']))
    a=row['scale_fitting_point'];b=row['counterexample']
    ba,wa=evaluate(target,a['point']);bb,wb=evaluate(target,b['point'])
    assert (ba,wa)==(a['base_term'],a['witness_term'])
    assert (bb,wb)==(b['base_term'],b['witness_term'])
    determinant=(ba*wb-bb*wa)%P
    assert determinant and determinant==row['nonzero_two_point_determinant_mod_p']
    assert (bb+row['fitted_modular_scale']*wb)%P==b['scaled_residual']
    assert b['scaled_residual']!=0

def main():
    packet=json.loads(PACKET.read_text());assert packet['prime']==P
    for rel,digest in packet['input_sha256'].items():
        assert algebra.source_sha256(REPO/rel)==digest
    rows=[r for r in packet['cases'] if not r['accepted_control']]
    for row in rows:check_row(row)
    altered=copy.deepcopy(rows[0]);altered['counterexample']['base_term']=(altered['counterexample']['base_term']+1)%P
    try:check_row(altered)
    except AssertionError:rejected=True
    else:rejected=False
    assert rejected
    result={'verified_transfer_rejections':len(rows),'source_hashes_verified':len(packet['input_sha256']),
            'corrupted_certificate_rejected':rejected,'gpu_used':False,
            'scope':'Finite exact rejection of these witnesses and their common scalar rescalings; not nonexistence of a Hodge certificate, and not Lean-verified.'}
    (PACKET.parent/'independent-replay.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O; verification assertions are required.')
    main()
