"""Check an exact exclusion of the degree-seven {chi_X0, chi_Y0} family.

Reconstructs the equations using pinned local Hodge Lab dependencies.
The verifier itself needs only Python's standard library, not Singular/SymPy.
This is an exclusion theorem, not the holdout's Lean existence certificate.
"""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations_with_replacement, product
import argparse, copy, gzip, hashlib, json, sys, time

PARSER=argparse.ArgumentParser(description=__doc__)
PARSER.add_argument('--check', action='store_true', help='Replay the archived exact certificate (default).')
PARSER.add_argument('--assemble', type=Path, help='Research scratch directory containing pair-0/radical-0/double-charts-0 JSON')
ARGS=PARSER.parse_args()
ROOT=Path(__file__).resolve().parents[1]
LAB=ROOT
manifest=json.loads((ROOT/'references/degree7-x0-y0-dependencies.json').read_text())
for relative,expected in manifest['sha256'].items():
    dependency=(LAB/relative).read_bytes()
    if not relative.endswith('.gz'):dependency=dependency.replace(b'\r\n',b'\n')
    if hashlib.sha256(dependency).hexdigest()!=expected:
        raise RuntimeError(f'Public dependency differs from pinned source: {relative}')
sys.path.insert(0,str(LAB/'algebra'))
import degree6_e1 as base
import degree7_e1 as e1
import degree7_character_search as cert
import degree7_y0_x1 as reference
from degree6_e2_model import modF
from degree6_quadratic_structure import B

OUT=ROOT/'results/degree7-x0-y0'
CHARACTERS=((0,0,1),(1,2,3))
PIN='dc2756300cbfa7a54d4735c60b852cd38ca8725e'


def construct():
    data,lifts=e1.load();fields,_=e1.koszul_fields()
    alpha=e1.character(next(iter(base.A)));w,z=CHARACTERS
    delta=tuple((b-a)%6 for a,b in zip(w,z))
    cyclic={tuple(k*a%6 for a in delta) for k in range(6)}
    group=list(product(range(6),repeat=3))
    subgroup=[g for g in group if sum(a*b for a,b in zip(g,delta))%6==0]
    annihilator={c for c in group if all(sum(a*b for a,b in zip(c,g))%6==0 for g in subgroup)}
    assert annihilator==cyclic and len(subgroup)==36
    wanted={tuple((a+b+c)%6 for a,b,c in zip(alpha,w,s)) for s in cyclic}
    ids=[i for f in data['character_families'] if tuple(f['character']) in CHARACTERS for i in f['basis_indices']]
    ks=[k for k,K in enumerate(fields) if e1.field_characters(K)<=wanted]
    assert len(ids)==13 and len(ks)==58
    physical={}
    def append(p,key):
        for m,c in modF(p).items():physical.setdefault(m,{})[key]=c
    for i,j in combinations_with_replacement(range(len(ids)),2):
        D,N=lifts[ids[i]];E,P=lifts[ids[j]]
        value=B(D,P)
        if i!=j:value=base.padd(value,B(E,N))
        append(value,(i,j))
    for i,index in enumerate(ids):
        for k,original in enumerate(ks):append(B(lifts[index][0],fields[original]),(i,len(ids)+k))
    monomials=sorted(physical);equations=[physical[m] for m in monomials]
    description={'basis_sha256':hashlib.sha256(e1.BASIS.read_bytes()).hexdigest(),
        'characters':[list(c) for c in CHARACTERS], 'denominator_basis_indices':ids,
        'Koszul_indices':ks,'subgroup_order':36,'physical_monomials':[list(m) for m in monomials],
        'equations':[cert.encode(p) for p in equations]}
    return description,equations


def necessary_with_witness(rows,nD):
    monomials=sorted({m for p in rows for m in p},key=lambda m:(0 if any(i>=nD for i in m) else 1,m))
    lookup={m:i for i,m in enumerate(monomials)};span=base.Elimination()
    for i,p in enumerate(rows):span.insert({lookup[m]:c for m,c in p.items()},{i:Q(1)})
    return [{'polynomial':cert.encode({monomials[j]:c for j,c in row.items()}),
             'weights':[[j,str(c)] for j,c in sorted(track.items())]}
            for pivot,(row,track) in span.basis.items() if all(i<nD for i in monomials[pivot])]


def verify(packet,description,equations):
    assert packet['system']==description
    nD=len(description['denominator_basis_indices']);nvars=nD+len(description['Koszul_indices'])
    maps={i:{(i,):Q(1)} for i in range(nvars)};free=set(range(nD));inferences=0
    assert [p['pivot'] for p in packet['initial_charts']]==list(range(nD))
    for proof in packet['initial_charts']:
        inferences+=cert.verify_chart(equations,nvars,proof)
        if proof['excluded']:maps[proof['pivot']]={};free.remove(proof['pivot'])
    assert sorted(set(range(nD))-free)==[1,8]
    square=packet['linear_square'];linear=cert.decode(square['linear'])
    assert linear=={(6,):Q(3),(7,):Q(-6),(9,):Q(1),(11,):Q(1),(12,):Q(1)}
    rows=[cert.substitute(p,maps) for p in equations];actual={}
    for j,c in square['witness']['equation_weights']:
        assert 0<=j<len(rows);actual=base.padd(actual,rows[j],Q(c))
    assert actual==cert.product(linear,linear)
    assert cert.decode(square['witness']['polynomial'])==actual
    change={6:{m:-c/3 for m,c in linear.items() if m!=(6,)}}
    maps={i:cert.substitute(p,change) for i,p in maps.items()};free.remove(6)
    rows=[cert.substitute(p,maps) for p in equations];necessities=[]
    for relation in packet['necessary_relations']:
        p=cert.decode(relation['polynomial']);actual={}
        for j,c in relation['weights']:
            assert 0<=j<len(rows);actual=base.padd(actual,rows[j],Q(c))
        assert p==actual and all(all(i in free for i in m) for m in p)
        necessities.append(p)
    left=packet['left'];right=packet['right']
    assert left==[0,2,3,4,5] and right==[7,9,10,11,12]
    assert set(left).isdisjoint(right) and sorted(left+right)==sorted(free)
    _,lifts=e1.load()
    for color,indices in zip(CHARACTERS,(left,right)):
        for i in indices:
            assert {e1.character(m) for m in lifts[description['denominator_basis_indices'][i]][0]}=={color}
    # Every necessary equation is bihomogeneous. Consequently each of the two
    # nonzero character components may be normalized separately for THIS test.
    # No independent scaling of a putative numerator is assumed.
    assert all(len({(sum(i in left for i in m),sum(i in right for i in m)) for m in p})==1 for p in necessities)
    charts=packet['double_charts']
    assert [p['pivots'] for p in charts]==[list(ij) for ij in product(left,right)]
    terms=0;max_degree=0
    for chart in charts:
        i,j=chart['pivots'];actual={}
        assert chart['excluded'] and len(chart['multipliers'])==len(necessities)
        for encoded,p in zip(chart['multipliers'],necessities):
            multiplier=cert.decode(encoded)
            assert all(all(k in free-{i,j} for k in mon) for mon in multiplier)
            reduced=cert.substitute(p,{i:{():Q(1)},j:{():Q(1)}})
            actual=base.padd(actual,cert.product(multiplier,reduced))
            terms+=len(multiplier)
            max_degree=max(max_degree,max(map(len,multiplier),default=0))
        assert actual=={():Q(1)},f'Invalid contradiction for chart {i},{j}'
    return {'initial_exact_inferences':inferences,'linear_square_checked':True,
            'necessary_relations_checked':len(necessities),'double_charts_checked':len(charts),
            'multiplier_terms':terms,'maximum_multiplier_degree':max_degree,
            'both_nonzero_characters_excluded':True,'single_character_theorem_required':True}


def assemble(source):
    description,equations=construct()
    initial=json.loads((source/'pair-0.json').read_text())
    radical=json.loads((source/'radical-0.json').read_text())
    doubles=json.loads((source/'double-charts-0.json').read_text())
    assert initial['equations']==description['equations']
    maps={int(i):cert.decode(p) for i,p in radical['maps'].items()}
    relations=necessary_with_witness([cert.substitute(p,maps) for p in equations],13)
    assert [p['polynomial'] for p in relations]==radical['necessary_equations']
    packet={'system':description,'initial_charts':initial['charts'],
        'linear_square':next(p for p in radical['history'] if p['kind']=='linear_square'),
        'necessary_relations':relations,'left':doubles['left'],'right':doubles['right'],
        'double_charts':doubles['charts'],'public_dependency_commit':PIN}
    result=verify(packet,description,equations)
    OUT.mkdir(parents=True,exist_ok=True)
    with gzip.open(OUT/'certificate.json.gz','wt',encoding='utf-8') as f:json.dump(packet,f,separators=(',',':'))
    print(json.dumps({'assembled':True,**result}),flush=True)


def check():
    start=time.perf_counter();description,equations=construct()
    with gzip.open(OUT/'certificate.json.gz','rt',encoding='utf-8') as f:packet=json.load(f)
    result=verify(packet,description,equations)
    # Reconstruct physical coefficients with the public lab's second polynomial
    # implementation, opposite division ordering, and independent H-selection.
    reference.CHARACTERS=CHARACTERS
    independent=reference.independent_equations(description)
    broken=copy.deepcopy(packet)
    first=next(p for p in broken['double_charts'][0]['multipliers'] if p)
    first[0][1]=str(Q(first[0][1])+1)
    try:verify(broken,description,equations)
    except AssertionError:pass
    else:raise AssertionError('A damaged chart certificate was accepted.')
    # This completes the proof after the mixed case has collapsed to a single
    # character; it replays all 138 existing single-character certificates.
    cert.check()
    report={'claim':'No admissible degree-seven denominator supported on chi_X0 and chi_Y0 modulo F*S1.',
        'degree':7,'denominator_coordinates':13,'Koszul_coordinates':58,'physical_equations':len(equations),
        **result,**independent,'corrupted_chart_rejected':True,'single_character_certificates_replayed':True,
        'certificate_sha256':hashlib.sha256((OUT/'certificate.json.gz').read_bytes()).hexdigest(),
        'public_dependency_commit':PIN,'seconds':time.perf_counter()-start,
        'limits':'Exact computational exclusion only; no Lean HasCertificate proof, no general degree-seven exclusion, no independent human review.'}
    if ARGS.assemble:(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2),flush=True)


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Do not use -O: assertions are verification checks.')
    if ARGS.assemble:assemble(ARGS.assemble)
    else:check()
