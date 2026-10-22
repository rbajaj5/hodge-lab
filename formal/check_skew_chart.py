"""Bounded source-bound Lean replay of the protected sextic/chart substitution.

Run python3 -O check_skew_chart.py from formal. Reuses earlier proof sources;
no network or dependency fetch. 120 seconds per command, 600 seconds total.
"""
from fractions import Fraction
from pathlib import Path
import datetime, hashlib, json, re, sys, time
import check_skew_extension as util

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'results/skew-chart'
PREFIX = 'HodgeLab.OneReflectionSkew.ChartSubstitution.'
MODULE = 'HodgeLab.OneReflectionSkew.ChartSubstitution'
NAMES = [PREFIX + name for name in ['eval_a', 'eval_aOver', 'eval_p7', 'protected_substitution',
         'protected_source_substitution', 'protected_substitution_p7',
         'eval_p7Over', 'protected_substitution_p7Over']]
SOURCES = ['lean-toolchain', 'lakefile.toml', 'lake-manifest.json',
           'check_skew_chart.py', 'check_skew_extension.py',
           'AuditSkewChart.lean', 'ReplaySkewChart.lean', MODULE.replace('.', '/') + '.lean']
require, digest = util.require, util.digest


def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def terms_json(p):
    return [[str(c), list(e)] for e, c in sorted(p.items()) if c]


def source_binding():
    pins = json.loads((OUT / 'inputs.json').read_text(encoding='utf-8'))['pins']
    paths = {}
    for pin in pins:
        raw = (ROOT.parent / pin['path']).read_bytes().replace(b'\r\n', b'\n')
        require(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'Input SHA256 mismatch')
        require(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == pin['git_blob'], 'Input Git blob mismatch')
        paths[Path(pin['upstream_path']).name] = raw.decode('utf-8')
    record = json.loads(paths['record.json'])
    rec = paths['instance.rec']
    require(record['q'] == 1 and util.expression_from_rec(rec, 'q') == '1', 'Unexpected pole order')
    lean = (ROOT / 'HodgeLab/OneReflectionSkew/CoordinateComparison.lean').read_text(encoding='utf-8')
    polys, chart = {}, {}
    for key in ['F', 'A']:
        terms = record[key]['terms']
        expected = {tuple(e): Fraction(c) for c, e in terms}
        require(len(expected) == len(terms), 'Duplicate protected terms need summation')
        require(util.parse_expression(util.expression_from_rec(rec, key)) == expected, 'REC/JSON mismatch')
        require(util.parse_expression(record[key]['expression']) == expected, 'JSON expression mismatch')
        definition = f'def skew{key} (p : Fin 6 → K) : K :=\n  ' + util.lean_expression(terms)
        actual = lean.split(f'def skew{key} ', 1)[1].split('\ndef ', 1)[0].strip()
        require('def skew' + key + ' ' + actual == definition, 'Lean definition differs from protected input')
        polys[key] = expected
        out = {}
        # The chart substitutes (x, r*x, w*x, 1, t, z) in the REC variable order.
        for e, c in expected.items():
            k = (e[0] + e[1] + e[2], e[1], e[2], e[4], e[5])
            out[k] = out.get(k, Fraction(0)) + c
        chart[key] = {e: c for e, c in out.items() if c}
    require(chart['A'] == {(3, 0, 0, 0, 0): Fraction(1)}, 'Source did not substitute to x^3')
    zterm = (0, 0, 0, 0, 6)
    require(chart['F'].get(zterm) == 1, 'Missing monic z^6 term')
    cubic = {}
    for e, c in chart['F'].items():
        if e == zterm:
            continue
        require(e[0] % 2 == 0 and e[4] == 0, 'Cannot descend this monomial through U=x^2')
        cubic[(e[0] // 2, *e[1:4], 0)] = 7 * c
    # Read actual sparse data used by the pre-existing formal obstruction.
    text = (ROOT / 'HodgeLab/OneReflectionSkew/ThreeCoefficient.lean').read_text(encoding='utf-8')
    body = text.split('def p7Sparse : Sparse := [', 1)[1].split(']', 1)[0]
    rows = re.findall(r'\(exp\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+),\s*(-?\d+)\)', body)
    remainder = re.sub(r'\(exp\s+\d+\s+\d+\s+\d+\s+\d+,\s*-?\d+\)', '', body)
    require(not remainder.replace(',', '').strip(), 'Unparsed p7Sparse syntax')
    p7 = {tuple(map(int, row[:4])) + (0,): Fraction(row[4]) for row in rows}
    require(len(p7) == len(rows), 'Duplicate sparse terms need summation')
    require(cubic == p7, 'Protected equation does not reproduce the actual p7')
    # Independent exact checks at points which distinguish common transcription errors.
    def ev(poly, point):
        total = Fraction(0)
        for e, c in poly.items():
            term = c
            for v, n in zip(point, e):
                term *= Fraction(v) ** n
            total += term
        return total
    controls = [
        ('wrong-U=x', ev(chart['F'], (2, 0, 0, 0, 0)), ev(p7, (2, 0, 0, 0, 0))/7),
        ('wrong-skew-sign', ev(chart['F'], (1, 1, 0, 2, 0)), Fraction(489, 7)),
        ('wrong-source-power', ev(chart['A'], (2, 0, 0, 0, 0)), Fraction(4)),
    ]
    for name, correct, wrong in controls:
        require(correct != wrong, 'Mutation control undetected: ' + name)
    result = {'status': 'PASS', 'protected_variable_order': ['X0', 'X1', 'X2', 'Y0', 'Y1', 'Y2'],
              'chart_variable_order': ['x', 'r', 'w', 't', 'z'], 'p7_variable_order': ['U', 'r', 'w', 't', 'unused'],
              'coefficient_field': 'exact rational input; Lean extension to characteristic-zero fields', 'q': 1,
              'input_files_checked': len(pins), 'F_terms_checked': len(polys['F']), 'A_terms_checked': len(polys['A']),
              'p7_terms_checked': len(p7), 'substituted_F': terms_json(chart['F']), 'substituted_A': terms_json(chart['A']),
              'reconstructed_p7': terms_json(cubic), 'actual_Lean_p7': terms_json(p7),
              'mutation_witnesses': [{'name': n, 'correct': str(c), 'wrong': str(w), 'residual_correct_minus_wrong': str(c-w)} for n, c, w in controls],
              'limits': 'External exact parser binds files to Lean definitions. No proof of differential normalization or global chart coverage.'}
    write('source-binding.json', result)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    util.OUT, util.START, util.RECORDS = OUT, time.monotonic(), []
    write('validation.json', {'status': 'IN_PROGRESS'})
    require(NAMES, 'Audited declaration list must be explicit')
    source_hashes = {s: digest(ROOT / s) for s in SOURCES}
    input_hashes = {'inputs.json': digest(OUT / 'inputs.json')}
    for pin in json.loads((OUT / 'inputs.json').read_text(encoding='utf-8'))['pins']:
        input_hashes[pin['path']] = digest(ROOT.parent / pin['path'])
    for s in SOURCES:
        if s.endswith('.lean'):
            require(not re.search(r'\b(sorry|admit|axiom|native_decide)\b', (ROOT / s).read_text(encoding='utf-8')), 'Unproved token: ' + s)
    prior = json.loads((ROOT / 'results/skew-extension/validation.json').read_text(encoding='utf-8'))
    require(prior['status'] == 'PASS', 'Prior proof receipt missing')
    inherited = dict(prior['reused_source_lf_sha256'])
    inherited.update({n: h for n, h in prior['source_lf_sha256'].items() if n.endswith('.lean') and n.startswith('HodgeLab/')})
    for name, h in inherited.items():
        require(digest(ROOT / name) == h, 'Reused proof source changed: ' + name)
    source_binding()
    version = util.run('version', ['lake', 'env', 'lean', '--version'])
    require('version 4.31.0,' in version, 'Wrong Lean version')
    manifest = json.loads((ROOT / 'lake-manifest.json').read_text(encoding='utf-8'))
    rev = next(x['rev'] for x in manifest['packages'] if x['name'] == 'mathlib')
    require(util.run('mathlib-head', ['git', '-C', '.lake/packages/mathlib', 'rev-parse', 'HEAD']).strip() == rev, 'Mathlib mismatch')
    util.run('build', ['lake', 'build', MODULE])
    audit = util.run('axioms', ['lake', 'env', 'lean', 'AuditSkewChart.lean'])
    axioms = {n: [x.strip() for x in a.split(',') if x.strip()] for n, a in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]", audit)}
    for n in re.findall(r"'([^']+)' does not depend on any axioms", audit):
        axioms[n] = []
    require(set(axioms) == set(NAMES), 'Missing or unexpected theorem reports')
    require(all(set(xs) <= {'propext', 'Classical.choice', 'Quot.sound'} for xs in axioms.values()), 'Unexpected axiom')
    replay = util.run('kernel-replay', ['lake', 'env', 'lean', 'ReplaySkewChart.lean'])
    require('PASS ' + MODULE in replay, 'Replay marker missing')
    f_proof = 'rw [protected_substitution]\n    norm_num [cubic, aCoeff, bCoeff, cCoeff, dCoeff]'
    a_proof = 'rw [protected_source_substitution]\n    norm_num'
    negatives = {
        'wrong-U=x': ('skewF (physicalPoint (2 : ℚ) 0 0 0 0)', '65', '9', f_proof),
        'wrong-skew-sign': ('7 * skewF (physicalPoint (1 : ℚ) 1 0 2 0)', '477', '489', f_proof),
        'wrong-source-power': ('skewA (physicalPoint (2 : ℚ) 0 0 0 0)', '8', '4', a_proof),
    }
    scratch = ROOT / '.lake/skew-chart-negative'
    scratch.mkdir(parents=True, exist_ok=True)
    header = ('import HodgeLab.OneReflectionSkew.ChartSubstitution\n'
              'open HodgeLab.OneReflectionSkew.CoordinateComparison\n'
              'open HodgeLab.OneReflectionSkew.ChartSubstitution\n')
    positive = header + '\n'.join('example : ' + expression + ' = ' + correct + ' := by\n    ' + proof + '\n'
                                for expression, correct, _, proof in negatives.values())
    p = scratch / 'positive-evaluations.lean'
    p.write_text(positive, encoding='utf-8', newline='\n')
    (OUT / 'positive-evaluations.lean.txt').write_bytes(p.read_bytes())
    util.run('positive-evaluations', ['lake', 'env', 'lean', p.relative_to(ROOT).as_posix()])
    for name, (expression, correct, wrong, proof) in negatives.items():
        body = (header + 'example : ' + expression + ' = ' + wrong + ' := by\n'
                '  have checked : ' + expression + ' = ' + correct + ' := by\n    ' + proof + '\n'
                '  rw [checked]\n  decide +kernel\n')
        p = scratch / (name + '.lean')
        p.write_text(body, encoding='utf-8', newline='\n')
        (OUT / (name + '.lean.txt')).write_bytes(p.read_bytes())
        log = util.run(name, ['lake', 'env', 'lean', p.relative_to(ROOT).as_posix()], True)
        require(log.count('error:') == 1 and 'unsolved goals' not in log and 'did not reduce' not in log,
                'Negative control contains an unrelated error: ' + name)
    require(source_hashes == {s: digest(ROOT / s) for s in SOURCES}, 'Sources changed during run')
    for name, h in inherited.items():
        require(digest(ROOT / name) == h, 'Reused proof changed during run: ' + name)
    for name, h in input_hashes.items():
        require(digest(OUT / name if name == 'inputs.json' else ROOT.parent / name) == h,
                'Pinned input changed during run: ' + name)
    write('validation.json', {
        'status': 'PASS', 'completed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'lean_version': version.strip(), 'python_version': sys.version, 'mathlib_commit': rev,
        'source_lf_sha256': source_hashes, 'reused_source_lf_sha256': inherited,
        'input_lf_sha256': input_hashes,
        'artifact_sha256': {MODULE: hashlib.sha256((ROOT / '.lake/build/lib/lean' / (MODULE.replace('.', '/') + '.olean')).read_bytes()).hexdigest()},
        'input_manifest_lf_sha256': digest(OUT/'inputs.json'), 'binding_receipt_lf_sha256': digest(OUT/'source-binding.json'),
        'theorem_axioms': axioms, 'commands': util.RECORDS, 'elapsed_seconds': time.monotonic()-util.START,
        'total_budget_seconds': 600, 'new_theorems': len(NAMES), 'new_modules_replayed': 1,
        'positive_evaluation_controls': len(negatives), 'negative_controls': len(negatives),
        'scope': 'Protected F/A substitution and equality with the existing p7 polynomial, under stated field hypotheses.',
        'limits': ['Only the new module is kernel-replayed; imports and earlier coefficient proof are reused',
                   'External parser/hash checks bind protected files to Lean definitions; no Lean Git/JSON parser',
                   'No differential/Jacobian/residue normalization, rational primitive, trace or global clearing proof',
                   'No new denominator/degree coverage or 45-versus-504 comparison; target remains open']})
    print('PASS: chart theorem audits, new-module replay, exact source binding and three rejected false statements')


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        OUT.mkdir(parents=True, exist_ok=True)
        write('validation.json', {'status': 'FAIL', 'error': str(error), 'commands': util.RECORDS})
        raise
