"""Exact local rank strata for the two remaining fixed-pair triple families.

Discovery uses optional FLINT. Replay uses Fraction and never assumes a
nonconstant pivot is invertible. A two-row block with only one correction
column has rank at most one: its augmented 2x2 minor must vanish. Factoring
that minor gives a complete (possibly overlapping) cover by linear branches.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from itertools import combinations, permutations
import argparse, copy, gzip, json, time
import degree7_syzygies as s
import degree7_syzygy_rebuild as rb
import check_family16_global_cubes as cubes

c = s.cert
OUT = s.triples.ROOT / 'results/degree7-rank-strata'


def seed(model, family, pivot):
    source = s.shared.read_packet()['families'][family - 1]
    first = s.triples.verify_family(model, source)
    desc, rows = s.shared.construct(model, source)
    assert pivot in desc['pivots']
    maps = {pivot: {(): Q(1)}}
    if family == 16:
        packet = json.loads(cubes.PATH.read_text(encoding='utf-8'))
        assert packet['system'] == desc
        cubes.verify(rows, packet['claims'])
        maps.update({1: {}, 9: {}})
    else:
        assert family == 137
    return desc, [c.substitute(p, maps) for p in rows], first


def split(rows, nD):
    result = {}
    for j, p in enumerate(rows):
        row = {}
        for mon, q in p.items():
            zs = [i for i in mon if i >= nD]
            assert len(zs) <= 1
            col = zs[0] if zs else -1
            a = tuple(i for i in mon if i < nD)
            cell = row.setdefault(col, {})
            cell[a] = cell.get(a, 0) + q
        result[j] = {k: v for k, v in row.items() if v}
    return result


def row_eliminate(rows, j, col):
    """A globally valid pivot: its coefficient must be a nonzero constant."""
    assert j in rows and col != -1 and col in rows[j]
    lead = rows[j][col]
    assert set(lead) == {()} and lead[()]
    pivot = {k: {m: q / lead[()] for m, q in v.items()}
             for k, v in rows.pop(j).items() if k != col}
    for row in rows.values():
        if col not in row:
            continue
        factor = row.pop(col)
        for k, p in pivot.items():
            value = s.triples.base.padd(row.get(k, {}), c.product(factor, p), -1)
            if value:
                row[k] = value
            else:
                row.pop(k, None)


def minor(rows, claim):
    ids = claim['rows']
    if claim['kind'] == 'row':
        assert len(ids) == 1 and set(rows[ids[0]]) == {-1}
        return rows[ids[0]][-1]
    assert claim['kind'] == 'minor'
    cols = claim.get('columns', [claim.get('column')])
    assert 1 <= len(cols) <= 2 and len(set(cols)) == len(cols) and all(k >= 0 for k in cols)
    assert len(ids) == len(cols) + 1 and len(set(ids)) == len(ids)
    assert all(set(rows[j]) <= set(cols) | {-1} for j in ids)
    cols = cols + [-1]; result = {}
    for perm in permutations(range(len(cols))):
        inversions = sum(perm[i] > perm[j] for i in range(len(perm)) for j in range(i+1,len(perm)))
        value = {(): Q((-1)**inversions)}
        for i, k in enumerate(perm):
            value = c.product(value, rows[ids[i]].get(cols[k], {}))
        result = s.triples.base.padd(result, value)
    return result


def zero_map(linear, nD):
    assert linear and all(len(m) <= 1 and all(i < nD for i in m) for m in linear)
    variables = [m[0] for m in linear if m]
    assert variables
    i = min(variables)
    return {i: {m: -q / linear[(i,)] for m, q in linear.items() if m != (i,)}}


def verify_tree(physical, nD, nv, pivot, node, counts):
    counts['nodes'] += 1
    if 'affine_chart' in node:
        proof = node['affine_chart']; assert proof['pivot'] == pivot
        counts['affine_inferences'] += c.verify_chart(physical, nv, proof)
        if proof['excluded']:
            assert node['status'] == 'affine_excluded' and not node['unit_pivots']
            assert not node.get('children') and not node.get('claim')
            counts['excluded_leaves'] += 1
            return True
        maps = s.chart_maps(nv, pivot, proof)
        assert all(all(j < nD for m in maps[i] for j in m) for i in range(nD))
        physical = [c.substitute(p, maps) for p in physical]
    # Only pivot rows and the claimed block can affect the checked identity.
    # Retain every correction column within those rows. Other rows are not
    # asserted redundant or discarded from the certificate problem.
    needed = {j for j, _ in node['unit_pivots']}
    needed.update(node.get('claim', {}).get('rows', []))
    rows = {j: row for j, row in split(physical, nD).items() if j in needed}
    for j, col in node['unit_pivots']:
        row_eliminate(rows, j, col)
        counts['constant_pivots'] += 1
    if node['status'] == 'unresolved':
        assert not node.get('claim') and not node.get('children')
        counts['unresolved_leaves'] += 1
        return False
    claim = node['claim']
    P = minor(rows, claim)
    assert P and c.encode(P) == claim['polynomial']
    value = {(): Q(claim['scalar'])}; assert value[()]
    for entry in claim['factors']:
        f = c.decode(entry['linear'])
        assert all(len(m) <= 1 for m in f) and any(m for m in f)
        assert isinstance(entry['power'], int) and entry['power'] >= 1
        zero_map(f, nD)
        for _ in range(entry['power']):
            value = c.product(value, f)
    assert value == P
    counts['checked_minors' if claim['kind'] == 'minor' else 'checked_rows'] += 1
    if not claim['factors']:
        assert node['status'] == 'excluded' and not node.get('children')
        counts['excluded_leaves'] += 1
        return True
    assert node['status'] == 'split'
    assert len(node['children']) == len(claim['factors'])
    results = []
    for entry, child in zip(claim['factors'], node['children']):
        change = zero_map(c.decode(entry['linear']), nD)
        results.append(verify_tree([c.substitute(p, change) for p in physical], nD, nv, pivot, child, counts))
    return all(results)


def check_packet(model, packet):
    desc, rows, first = seed(model, packet['family'], packet['pivot'])
    assert desc == packet['system']
    counts = Counter()
    nD = len(desc['basis_indices']); nv = nD + len(desc['Koszul_indices'])
    excluded = verify_tree(rows, nD, nv, packet['pivot'], packet['tree'], counts)
    assert excluded == packet['excluded']
    return {'family': packet['family'], 'pivot': packet['pivot'], 'excluded': excluded,
            **counts, 'first_pass': dict(first)}


def check_global(model, packet):
    """Check the simpler two-row square identity without chart assumptions."""
    source = s.shared.read_packet()['families'][packet['family']-1]
    first = s.triples.verify_family(model, source)
    desc, equations = s.shared.construct(model, source)
    assert packet['system'] == desc
    L = c.decode(packet['linear']); assert all(len(m) == 1 for m in L)
    square = c.product(L, L); actual = {}
    for j, coefficient in packet['square_identity']:
        assert 0 <= j < len(equations)
        actual = s.triples.base.padd(actual, equations[j], Q(coefficient))
    assert actual == square
    block = packet['block']; j, k = block['rows']; z = block['correction_coordinate']
    assert z >= len(desc['basis_indices'])
    Lz = c.product(L, {(z,): Q(1)})
    assert equations[j] == {m: 4*q for m, q in Lz.items()}
    assert equations[k] == s.triples.base.padd({m: Q(2,3)*q for m,q in Lz.items()}, square, -Q(1,27))
    return {'family':packet['family'], 'physical_rows':2, 'first_pass':dict(first),
            'scope':'Global linear vanishing after first-pass reduction; no normalization or family-16 cube dependency.'}


def check_all(independent=False):
    start = time.perf_counter()
    if independent:
        from check_degree7_triples import IndependentModel
        model = IndependentModel()
    else:
        model = s.triples.Model()
    globals_packet = json.loads((OUT/'global-linear-identities.json').read_text(encoding='utf-8'))
    global_checks = [check_global(model, p) for p in globals_packet]
    records=[]
    for family in [16,137]:
        _,_,_=seed(model,family,7 if family==16 else 8)
        for pivot in ([7,10,11,12,13] if family==16 else [8,11,13,16,17]):
            result=check_packet(model,rb.read(OUT/f'chart-{family}-{pivot}.json.gz'))
            records.append(result)
    bad=copy.deepcopy(globals_packet[0]);bad['square_identity'][0][1]='5'
    try: check_global(model,bad)
    except AssertionError: pass
    else: raise AssertionError('Corrupt square identity accepted.')
    # Nonconstant pivots cannot silently discard their vanishing branch.
    try: row_eliminate({0:{18:{(0,):Q(1)},-1:{():Q(1)}}},0,18)
    except AssertionError: pass
    else: raise AssertionError('Nonconstant pivot accepted as a unit.')
    # Require every factor branch, even if all remaining branches are closed.
    toy={ 'unit_pivots':[], 'status':'split',
          'claim':{'kind':'row','rows':[0],'polynomial':[[[0,1],'1']],
                   'scalar':'1','factors':[{'linear':[[[0],'1']],'power':1},
                                         {'linear':[[[1],'1']],'power':1}]},
          'children':[] }
    try: verify_tree([{(0,1):Q(1)}],2,2,0,toy,Counter())
    except AssertionError: pass
    else: raise AssertionError('Omitted factor branches accepted.')
    return {'status':'PASS','independent_polynomials':independent,
            'global_linear_checks':global_checks,'charts':records,
            'corrupt_identity_rejected':True,'nonconstant_pivot_rejected':True,
            'omitted_branch_rejected':True,'seconds':time.perf_counter()-start,
            'scope':'Two necessary linear vanishings and ten bounded local-rank searches; no family exclusion.'}


class Search:
    def __init__(self, nD, nv, pivot, max_nodes, branch_depth, seconds):
        from flint import fmpq_mpoly_ctx
        self.nD = nD
        self.nv = nv; self.pivot = pivot
        self.ctx = fmpq_mpoly_ctx.get(tuple('a'+str(i) for i in range(nD)), ordering='degrevlex')
        self.max_nodes = max_nodes; self.branch_depth = branch_depth
        self.deadline = time.perf_counter() + seconds
        self.nodes = 0

    def poly(self, p):
        from flint import fmpq
        return self.ctx.from_dict({tuple(m.count(i) for i in range(self.nD)):
                                  fmpq(q.numerator, q.denominator) for m, q in p.items()})

    def encode(self, p):
        return c.encode({tuple(i for i, e in enumerate(m) for _ in range(int(e))): Q(str(q))
                         for m, q in p.to_dict().items()})

    def eliminate(self, rows):
        steps = []
        while time.perf_counter() < self.deadline:
            incidence = {}
            for j, row in rows.items():
                for k in row:
                    if k != -1:
                        incidence.setdefault(k, []).append(j)
            choices = [((len(row)-1)*(len(incidence[k])-1), len(row), len(incidence[k]), j, k)
                       for j, row in rows.items() for k, p in row.items()
                       if k != -1 and p.is_constant()]
            if not choices:
                break
            *_, j, col = min(choices)
            prow = rows.pop(j); lead = prow[col].leading_coefficient()
            prow = {k: p / lead for k, p in prow.items() if k != col}
            for index in incidence[col]:
                if index == j:
                    continue
                row = rows[index]; factor = row.pop(col)
                for k, p in prow.items():
                    value = row.get(k, self.ctx.constant(0)) - factor*p
                    if value:
                        row[k] = value
                    else:
                        row.pop(k, None)
            steps.append([j, col])
        return steps

    def candidates(self, rows):
        groups = {}; output = []; seen = set()
        def consider(P, origin):
            if not P or P.total_degree() > 5 or len(P) > 300:
                return
            normalized = str(P / P.leading_coefficient())
            if normalized in seen:
                return
            seen.add(normalized)
            scalar, factors = P.factor()
            if not all(f.total_degree() == 1 for f, e in factors):
                return
            entries = [{'linear': self.encode(f), 'power': int(e)} for f, e in factors]
            score = (len(entries), sum(len(e['linear']) for e in entries), len(P))
            output.append((score, {**origin, 'polynomial': self.encode(P),
                                   'scalar': str(scalar), 'factors': entries}))
        for j, row in rows.items():
            cols = [k for k in row if k != -1]
            if not cols and -1 in row:
                consider(row[-1], {'kind': 'row', 'rows': [j]})
            elif len(cols) == 1:
                groups.setdefault(cols[0], []).append(j)
        for col, ids in groups.items():
            for offset, j in enumerate(ids):
                for k in ids[offset+1:]:
                    left, right = rows[j], rows[k]
                    P = left[col]*right.get(-1, self.ctx.constant(0)) - right[col]*left.get(-1, self.ctx.constant(0))
                    consider(P, {'kind': 'minor', 'rows': [j, k], 'column': col})
        if not any(score[0] <= 1 for score, _ in output):
            supports = {j: frozenset(k for k in row if k != -1) for j, row in rows.items()}
            pairs = sorted({tuple(sorted(v)) for v in supports.values() if len(v) == 2})
            tested = 0
            for cols in pairs:
                ids = [j for j, supp in supports.items() if supp and supp <= set(cols)]
                for rr in combinations(ids, 3):
                    if not any(-1 in rows[j] for j in rr):
                        continue
                    aa = [[rows[j].get(k, self.ctx.constant(0)) for k in (*cols, -1)] for j in rr]
                    P = (aa[0][0]*(aa[1][1]*aa[2][2]-aa[1][2]*aa[2][1])
                         -aa[0][1]*(aa[1][0]*aa[2][2]-aa[1][2]*aa[2][0])
                         +aa[0][2]*(aa[1][0]*aa[2][1]-aa[1][1]*aa[2][0]))
                    consider(P, {'kind':'minor', 'rows':list(rr), 'columns':list(cols)})
                    tested += 1
                    if tested >= 10000 or time.perf_counter() >= self.deadline:
                        break
                if tested >= 10000 or time.perf_counter() >= self.deadline:
                    break
        return sorted(output, key=lambda item: (item[0], item[1]['rows']))

    def search(self, physical, depth=0, linear_depth=0):
        self.nodes += 1
        node = {'unit_pivots': [], 'status': 'unresolved'}
        if self.nodes > self.max_nodes or time.perf_counter() >= self.deadline:
            node['reason'] = 'node_or_time_bound'
            return node, False
        proof = c.prove_chart(physical, self.nv, self.pivot)
        if proof['excluded']:
            node['affine_chart'] = proof; node['status'] = 'affine_excluded'
            return node, True
        maps = s.chart_maps(self.nv, self.pivot, proof)
        if not all(all(j < self.nD for m in maps[i] for j in m) for i in range(self.nD)):
            node['reason'] = 'mixed_denominator_affine_map_unsupported'
            return node, False
        node['affine_chart'] = proof
        physical = [c.substitute(p, maps) for p in physical]
        rows = {j: {k: self.poly(p) for k, p in row.items()} for j, row in split(physical, self.nD).items()}
        node['unit_pivots'] = self.eliminate(rows)
        choices = self.candidates(rows)
        node['diagnostics'] = {'remaining_correction_columns': len({k for row in rows.values() for k in row if k != -1}),
                               'factorable_candidates': len(choices)}
        if not choices:
            node['reason'] = 'no_factorable_local_rank_constraint'
            return node, False
        _, claim = choices[0]
        if len(claim['factors']) > 1 and depth >= self.branch_depth:
            node['reason'] = 'branch_depth_bound'
            node['unused_candidate'] = claim
            return node, False
        node['claim'] = claim
        if not claim['factors']:
            node['status'] = 'excluded'
            return node, True
        node['status'] = 'split'; node['children'] = []; closed = []
        print('node', self.nodes, 'branch_depth', depth, 'forced', linear_depth,
              'units', len(node['unit_pivots']), 'factors', [e['linear'] for e in claim['factors']], flush=True)
        for entry in claim['factors']:
            change = zero_map(c.decode(entry['linear']), self.nD)
            child, excluded = self.search([c.substitute(p, change) for p in physical],
                                          depth + (len(claim['factors']) > 1), linear_depth + 1)
            node['children'].append(child); closed.append(excluded)
        return node, all(closed)


def discover(args):
    import syzygy_accelerated as fast
    c.reduce_span = fast.reduce_span
    start = time.perf_counter()
    desc, rows, _ = seed(s.triples.Model(), args.family, args.pivot)
    nD = len(desc['basis_indices'])
    search = Search(nD, nD + len(desc['Koszul_indices']), args.pivot, args.nodes, args.depth, args.seconds)
    tree, excluded = search.search(rows)
    packet = {'family': args.family, 'pivot': args.pivot, 'system': desc,
              'limits': {'nodes': args.nodes, 'branch_depth': args.depth, 'seconds': args.seconds,
                         'factor_degree': 5, 'factor_terms': 300},
              'tree': tree, 'excluded': excluded, 'seconds': time.perf_counter()-start}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    s.shared.save(args.output, packet)
    print(json.dumps({'excluded': excluded, 'nodes': search.nodes, 'seconds': packet['seconds']}), flush=True)


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('Run without -O.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--family', type=int, choices=[16, 137])
    parser.add_argument('--pivot', type=int)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--seconds', type=int, default=120)
    parser.add_argument('--nodes', type=int, default=30)
    parser.add_argument('--depth', type=int, default=2)
    parser.add_argument('--check', type=Path)
    parser.add_argument('--check-all', action='store_true')
    parser.add_argument('--independent', action='store_true')
    args = parser.parse_args()
    if args.check_all:
        print(json.dumps(check_all(args.independent),indent=2),flush=True)
    elif args.check:
        if args.independent:
            from check_degree7_triples import IndependentModel
            model = IndependentModel()
        else:
            model = s.triples.Model()
        print(json.dumps(check_packet(model, rb.read(args.check)), indent=2))
    else:
        if args.family is None or args.pivot is None or args.output is None:
            parser.error('Discovery requires --family, --pivot and --output.')
        if args.output.exists():
            parser.error('Choose a fresh output path.')
        discover(args)
