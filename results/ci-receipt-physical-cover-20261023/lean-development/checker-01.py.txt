"""Audit one conditional physical-cover binding; 120s/command, 600s total.

Run python3 -O check_skew_physical_cover.py after fetching the pinned cache.
Immutable inputs remain in results/skew-physical-cover. Every invocation gets
a fresh receipt directory, optionally selected by --output-dir. Source pins
are provenance; scripts/check_skew_physical_source.py checks literal binding.
No splitting, separability, descent, or physical differential normalization.
"""
from pathlib import Path
import datetime, hashlib, json, os, re, shlex, subprocess, sys, time
from check_skew_extension import require, digest
from fresh_receipts import fresh_output_dir

ROOT = Path(__file__).resolve().parent
HISTORY = ROOT / 'results/skew-physical-cover'
OUT = None
MODULE = 'HodgeLab.OneReflectionSkew.PhysicalCoverBinding'
DECLARATIONS = ['physicalPolynomial', 'lower_terms_degree_bound', 'physical_degree',
    'physical_monic', 'physical_leading_coefficient', 'physical_eq_split_cover',
    'physical_trace_last', 'physical_trace_slot_eleven']
NAMES = [MODULE + '.' + name for name in DECLARATIONS]
SOURCES = ['lean-toolchain', 'lakefile.toml', 'lake-manifest.json',
    'check_skew_extension.py', 'fresh_receipts.py', 'check_skew_physical_cover.py',
    'AuditSkewPhysicalCover.lean', 'ReplaySkewPhysicalCover.lean',
    MODULE.replace('.', '/') + '.lean']
RECORDS = []
START = time.monotonic()
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n',
                           encoding='utf-8', newline='\n')


def run(label, command, reject=False):
    remaining = 600 - (time.monotonic() - START)
    require(remaining > 1, '600-second budget exhausted')
    bound = min(120, int(remaining))
    execution = command
    if os.name == 'nt':
        wroot = '/mnt/' + ROOT.drive[0].lower() + ROOT.as_posix()[2:]
        execution = ['wsl.exe', '--cd', wroot, '-e', 'sh', '-lc',
                     'exec timeout ' + str(bound) + ' ' + shlex.join(command)]
    began = time.monotonic()
    try:
        completed = subprocess.run(execution, cwd=ROOT, capture_output=True,
                                   encoding='utf-8', timeout=bound)
        code, log = completed.returncode, completed.stdout + completed.stderr
    except subprocess.TimeoutExpired as error:
        def text(value):
            return value.decode('utf-8', errors='replace') if isinstance(value, bytes) else value or ''
        code, log = 124, text(error.stdout) + text(error.stderr)
    (OUT / (label + '.log')).write_text(log, encoding='utf-8', newline='\n')
    RECORDS.append(dict(label=label, command=command, execution_command=execution,
        bound_seconds=bound, exit_code=code, elapsed_seconds=time.monotonic()-began,
        expected_failure=reject, log=label+'.log', log_lf_sha256=digest(OUT/(label+'.log'))))
    write('commands.json', RECORDS)
    print(json.dumps({'label': label, 'exit_code': code,
                      'seconds': RECORDS[-1]['elapsed_seconds']}), flush=True)
    require(code != 124, label + ' timed out; no mathematical result')
    if reject:
        require(code != 0 and log.count('error:') == 1 and 'unsolved goals' in log and '⊢ False' in log,
                label + ' did not fail at the intended false mathematical goal: ' + log[:2000])
        require('failed to synthesize' not in log and 'unknown' not in log.lower(),
                'Unrelated control error: ' + label)
    else:
        require(code == 0, label + ' failed: ' + log[:2000])
    return log


def main():
    global OUT, START
    START = time.monotonic()
    OUT = fresh_output_dir(ROOT, 'skew-physical-cover', [HISTORY,
        ROOT/'results/skew-trace-basis', ROOT.parent/'results/chi-target-source',
        ROOT.parent/'results/ci-receipt-physical-cover-20261023/inputs'])
    print('Fresh receipts: ' + str(OUT), flush=True)
    write('validation.json', {'status': 'IN_PROGRESS'})
    inputs_hash = digest(HISTORY/'inputs.json')
    inputs = json.loads((HISTORY/'inputs.json').read_text(encoding='utf-8'))
    require(bool(inputs['context_receipt_lf_sha256']), 'Missing historical context pins')
    require(bool(inputs['physical_source_pins']), 'Missing physical source pins')
    for path, expected in inputs['context_receipt_lf_sha256'].items():
        require(digest(ROOT.parent/path) == expected, 'Historical context receipt changed: ' + path)
    physical_hashes = {}
    for pin in inputs['physical_source_pins']:
        path = (ROOT.parent/pin['path']).resolve()
        require(path.is_relative_to(ROOT.parent.resolve()), 'Source path escapes repository')
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        require(actual == pin['sha256'], 'Physical source pin changed: ' + pin['path'])
        physical_hashes[pin['path']] = actual
    prior = json.loads((ROOT/'results/skew-trace-basis/validation.json').read_text(encoding='utf-8'))
    require(prior['status'] == 'PASS', 'Completed split-basis historical receipt required')
    reused = {p:h for p,h in prior['source_lf_sha256'].items()
              if p.startswith('HodgeLab/') and p.endswith('.lean')}
    for path, expected in reused.items():
        require(digest(ROOT/path) == expected, 'Reused proof source changed: ' + path)
    hashes = {p:digest(ROOT/p) for p in SOURCES}
    for path in SOURCES:
        if path.endswith('.lean'):
            require(not re.search(r'\b(sorry|admit|axiom|native_decide)\b',
                                  (ROOT/path).read_text(encoding='utf-8')), 'Unproved token: ' + path)
    version = run('version', ['lake', 'env', 'lean', '--version'])
    require('version 4.31.0,' in version, 'Unexpected Lean version')
    manifest = json.loads((ROOT/'lake-manifest.json').read_text(encoding='utf-8'))
    revision = next(p['rev'] for p in manifest['packages'] if p['name'] == 'mathlib')
    require(run('mathlib-head', ['git', '-C', '.lake/packages/mathlib', 'rev-parse', 'HEAD']).strip()
            == revision, 'Mathlib mismatch')
    run('build', ['lake', 'build', MODULE])
    audit = run('axioms', ['lake', 'env', 'lean', 'AuditSkewPhysicalCover.lean'])
    axioms = {n:[a.strip() for a in values.split(',') if a.strip()]
              for n,values in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]", audit)}
    for name in re.findall(r"'([^']+)' does not depend on any axioms", audit):
        axioms[name] = []
    require(set(axioms) == set(NAMES), 'Missing or unexpected declaration audit')
    require(all(set(a) <= {'propext', 'Classical.choice', 'Quot.sound'} for a in axioms.values()),
            'Unexpected axiom')
    replay = run('kernel-replay', ['lake', 'env', 'lean', 'ReplaySkewPhysicalCover.lean'])
    require('PASS ' + MODULE in replay, 'Missing kernel replay marker')
    header = '''import HodgeLab.OneReflectionSkew.PhysicalCoverBinding
open Polynomial HodgeLab.OneReflectionSkew.PhysicalCoverBinding
open HodgeLab.OneReflectionSkew.TraceFreeBasis HodgeLab.OneReflectionSkew.SplitTraceQuotient
'''
    positive = '''
example {K : Type*} [Field K] (a v : K) : physicalPolynomial a v =
    X ^ 18 + X ^ 12 + (C v * X - 1) ^ 6 - C a * X ^ 15 := rfl
example : (physicalPolynomial (0 : ℚ) 0).natDegree = 18 := physical_degree 0 0
example : (physicalPolynomial (2 : ℚ) 1).leadingCoeff = 1 := physical_leading_coefficient 2 1
example : (physicalPolynomial (2 : ℚ) 1).eval 1 = 0 := by norm_num [physicalPolynomial]
example : (physicalPolynomial (2 : ℚ) 1).derivative.eval 1 = 0 := by
  norm_num [physicalPolynomial, derivative_pow]
example : (physicalPolynomial (2 : ℚ) 1).eval 2 = 200705 := by norm_num [physicalPolynomial]
example {K : Type*} [Field K] (a v : K) (roots : Fin 18 → K)
    (hr : Function.Injective roots) (hroot : ∀ j, (physicalPolynomial a v).eval (roots j) = 0) :
    physicalPolynomial a v = coverPolynomial 1 roots := physical_eq_split_cover a v roots hr hroot
example {K : Type*} [Field K] (a v : K) (roots : Fin 18 → K)
    (hr : Function.Injective roots) (hroot : ∀ j, (physicalPolynomial a v).eval (roots j) = 0) :
    Algebra.trace K (SplitAlgebra K)
      (fun j => roots j ^ 17 / (physicalPolynomial a v).derivative.eval (roots j)) = 1 :=
  physical_trace_last a v roots hr hroot
example {K : Type*} [Field K] (a v : K) (roots : Fin 18 → K)
    (hr : Function.Injective roots) (hroot : ∀ j, (physicalPolynomial a v).eval (roots j) = 0) :
    Algebra.trace K (SplitAlgebra K)
      (fun j => roots j ^ 11 / (physicalPolynomial a v).derivative.eval (roots j)) = 0 :=
  physical_trace_slot_eleven a v roots hr hroot
'''
    negatives = {
        'parameter-is-not-leading-coefficient': '''example : (physicalPolynomial (2 : ℚ) 1).leadingCoeff = 2 := by
  rw [physical_leading_coefficient]
  norm_num
''',
        'distinctness-cannot-be-dropped': '''example : physicalPolynomial (2 : ℚ) 1 =
    coverPolynomial 1 (fun _ : Fin 18 => (1 : ℚ)) := by
  have hne : physicalPolynomial (2 : ℚ) 1 ≠ coverPolynomial 1 (fun _ : Fin 18 => (1 : ℚ)) := by
    intro h
    have he := congrArg (fun p : ℚ[X] => p.eval 2) h
    norm_num [physicalPolynomial, coverPolynomial, Lagrange.eval_nodal] at he
  simp only [hne]
''',
        'root-membership-cannot-be-dropped': '''example : physicalPolynomial (0 : ℚ) 0 =
    coverPolynomial 1 (fun j : Fin 18 => (j.val : ℚ)) := by
  have hne : physicalPolynomial (0 : ℚ) 0 ≠ coverPolynomial 1 (fun j : Fin 18 => (j.val : ℚ)) := by
    intro h
    have he := congrArg (fun p : ℚ[X] => p.eval 0) h
    have hr := cover_eval_root (1 : ℚ) (fun j : Fin 18 => (j.val : ℚ)) (0 : Fin 18)
    norm_num only [Fin.val_zero, Nat.cast_zero] at hr
    rw [hr] at he
    norm_num [physicalPolynomial] at he
  simp only [hne]
''',
        'specializations-not-always-simple': '''example : (physicalPolynomial (2 : ℚ) 1).derivative.eval 1 ≠ 0 := by
  norm_num [physicalPolynomial, derivative_pow]
'''}
    scratch = ROOT/'.lake/skew-physical-cover-controls'
    scratch.mkdir(parents=True, exist_ok=True)
    for label, body, reject in [('positive-controls', positive, False)] + [
            (label, body, True) for label, body in negatives.items()]:
        path = scratch/(label+'.lean')
        path.write_text(header+body, encoding='utf-8', newline='\n')
        (OUT/(label+'.lean.txt')).write_bytes(path.read_bytes())
        run(label, ['lake', 'env', 'lean', path.relative_to(ROOT).as_posix()], reject)
    require(hashes == {p:digest(ROOT/p) for p in SOURCES}, 'Source changed during verification')
    require(inputs_hash == digest(HISTORY/'inputs.json'), 'Input manifest changed during verification')
    for path, expected in inputs['context_receipt_lf_sha256'].items():
        require(digest(ROOT.parent/path) == expected, 'Historical context changed during verification')
    for path, expected in reused.items():
        require(digest(ROOT/path) == expected, 'Reused proof changed during verification')
    for path, expected in physical_hashes.items():
        require(hashlib.sha256((ROOT.parent/path).read_bytes()).hexdigest() == expected,
                'Physical source changed during verification')
    write('validation.json', dict(status='PASS',
        completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        lean_version=version.strip(), python_version=sys.version, mathlib_commit=revision,
        source_lf_sha256=hashes, reused_source_lf_sha256=reused,
        inputs_lf_sha256=inputs_hash, physical_source_sha256=physical_hashes,
        historical_context_lf_sha256=inputs['context_receipt_lf_sha256'],
        declaration_axioms=axioms, commands=RECORDS, elapsed_seconds=time.monotonic()-START,
        total_budget_seconds=600, new_declarations_audited=len(NAMES), new_modules_replayed=1,
        positive_controls=9, negative_controls=len(negatives),
        artifact_sha256={MODULE:hashlib.sha256((ROOT/'.lake/build/lib/lean'/
                            (MODULE.replace('.', '/')+'.olean')).read_bytes()).hexdigest()},
        scope='One conditional literal-polynomial to full split-cover binding, degree/monicity helpers and reuse of two split trace formulas.',
        limits=['Arbitrary field K; parameters a,v; 18 explicitly distinct roots and root membership required',
                'No proof that root hypotheses hold over Q(a,v,t), or any specified splitting extension',
                'No separability, descent, physical differential source normalization, primitive or certificate',
                'Two trace corollaries reuse prior basis proofs; slot11 is not identified with the physical source',
                'Mathlib and prior proof imports are not newly kernel-replayed',
                'Physical file hashes are provenance only; the separate source checker binds the literal definition']))
    print('PASS: 8 declaration audits, one new-module kernel replay, nine positive and four negative controls')


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        if OUT is not None:
            write('validation.json', {'status':'FAIL', 'error':str(error), 'commands':RECORDS})
        raise
