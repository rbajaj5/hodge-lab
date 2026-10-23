"""Read-only audit of saved distinct-root evidence; no Lean or math is rerun.

Run from the notebook root. The output path must be new and under this review
directory. The substantive mathematical assessment records the AI review of
the exact source; hash checks alone are not a mathematical proof.
"""
from pathlib import Path
import argparse
import ast
import datetime
import hashlib
import json
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FORMAL = ROOT / 'formal'
BATCH = HERE.parent
CHECK = BATCH / 'lean-development/checker-02'
MODULE = 'HodgeLab.OneReflectionSkew.GenericDistinctRoots'


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(path, lf=False):
    raw = path.read_bytes()
    if lf:
        raw = raw.replace(b'\r\n', b'\n')
    return hashlib.sha256(raw).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='final-review.json')
    args = parser.parse_args()
    output = (HERE / args.output).resolve()
    require(output.parent == HERE, 'Write only a new review receipt in source-review')
    require(not output.exists(), 'Existing review receipt is immutable')
    validation = load(CHECK / 'validation.json')
    require(validation['status'] == 'PASS', 'Focused checker is not PASS')
    checked = {}

    def check(path, expected, lf=False):
        actual = digest(path, lf)
        require(actual == expected, 'Hash mismatch: ' + str(path.relative_to(ROOT)))
        checked[path.relative_to(ROOT).as_posix()] = digest(path)

    for name, expected in validation['source_lf_sha256'].items():
        path = FORMAL / name
        path.read_text(encoding='utf-8')
        check(path, expected, True)
        snapshot = CHECK / 'source-snapshot' / (name + '.txt')
        check(snapshot, expected, True)
        require(path.read_bytes() == snapshot.read_bytes(), 'Source snapshot differs byte-for-byte')
    for name, expected in validation['reused_source_lf_sha256'].items():
        check(FORMAL / name, expected, True)
    for name, expected in validation['historical_context_lf_sha256'].items():
        check(ROOT / name, expected, True)
    for name, expected in validation['physical_source_sha256'].items():
        check(ROOT / name, expected)
    check(FORMAL / 'results/skew-distinct-roots/inputs.json', validation['inputs_lf_sha256'], True)
    check(CHECK / 'source-snapshot/inputs.json.txt', validation['inputs_lf_sha256'], True)
    pin = validation['source_pins_manifest']
    check(ROOT / pin['path'], pin['sha256'])

    commands = validation['commands']
    require(commands == load(CHECK / 'commands.json'), 'Command records disagree')
    for command in commands:
        check(CHECK / command['stdout'], command['stdout_sha256'])
        check(CHECK / command['stderr'], command['stderr_sha256'])
        check(CHECK / command['log'], command['log_lf_sha256'], True)
        require((CHECK / command['log']).read_bytes() ==
                (CHECK / command['stdout']).read_bytes() + (CHECK / command['stderr']).read_bytes(),
                'Combined log is not the saved stdout plus stderr')
        require(command['elapsed_seconds'] < command['bound_seconds'] <= 120,
                'A saved command exceeded its bound')
        if command['expected_failure']:
            log = (CHECK / command['log']).read_text(encoding='utf-8')
            require(command['exit_code'] == 1 and log.count('error:') == 1 and
                    'unsolved goals' in log and '⊢ False' in log,
                    'Negative control did not fail at the intended false goal')
        else:
            require(command['exit_code'] == 0, 'Positive command did not exit zero')
    require(validation['elapsed_seconds'] < validation['total_budget_seconds'] == 600,
            'Focused checker exceeded total bound')
    axioms_text = (CHECK / 'axioms.log').read_text(encoding='utf-8')
    axioms = {name: [a.strip() for a in values.split(',') if a.strip()]
              for name, values in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]", axioms_text)}
    for name in re.findall(r"'([^']+)' does not depend on any axioms", axioms_text):
        axioms[name] = []
    require(axioms == validation['declaration_axioms'], 'Parsed axiom log disagrees')
    require(all(set(values) <= {'propext', 'Classical.choice', 'Quot.sound'} for values in axioms.values()),
            'Unexpected axiom dependency')
    source = (FORMAL / MODULE.replace('.', '/')).with_suffix('.lean').read_text(encoding='utf-8')
    declarations = re.findall(r'^(?:def|abbrev|theorem) (\w+)', source, re.M)
    require({MODULE + '.' + name for name in declarations} == set(axioms), 'Public declarations differ from audit')
    require(not re.search(r'\b(sorry|admit|axiom|native_decide)\b', source), 'Unproved source token')
    checker_ast = ast.parse((FORMAL / 'check_skew_distinct_roots.py').read_text(encoding='utf-8'))
    listed = next(ast.literal_eval(node.value) for node in checker_ast.body
                  if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'DECLARATIONS'
                                                         for t in node.targets))
    require(declarations == listed, 'Checker declaration ordering/list differs')
    require('PASS ' + MODULE in (CHECK / 'kernel-replay.log').read_text(encoding='utf-8'),
            'Named new-module replay marker missing')
    positive = (CHECK / 'positive-controls.lean.txt').read_text(encoding='utf-8')
    require(len(re.findall(r'^example', positive, re.M)) == validation['positive_controls'] == 9,
            'Positive control count differs')
    require(sum(c['expected_failure'] for c in commands) == validation['negative_controls'] == 3,
            'Negative control count differs')
    check(FORMAL / '.lake/build/lib/lean' / (MODULE.replace('.', '/') + '.olean'),
          validation['artifact_sha256'][MODULE])
    exact = BATCH / 'math-review/exact-01'
    exact_receipt = load(exact / 'receipt.json')
    require(exact_receipt['status'] == 'PASS' and exact_receipt['exit_code'] == 0,
            'Separate mathematical identity receipt is not PASS')
    check(exact / 'stdout.json', exact_receipt['stdout_sha256'])
    check(exact / 'stderr.log', exact_receipt['stderr_sha256'])
    check(BATCH / 'math-review/check_elimination.py', exact_receipt['source_sha256'])
    check(BATCH / 'math-review/run_exact_review.py', exact_receipt['runner_sha256'])
    source_receipt = load(BATCH / 'source-check/validation.json')
    require(source_receipt['status'] == 'PASS', 'Separate source receipt is not PASS')
    for name, expected in source_receipt['source_sha256'].items():
        check(ROOT / name, expected)
    attempts = []
    for path in sorted((BATCH / 'lean-development').glob('*/attempt.json')):
        attempt = load(path)
        if 'source_sha256' in attempt:
            check(path.parent / 'GenericDistinctRoots.lean', attempt['source_sha256'])
        for suffix in ('stdout.log', 'stderr.log'):
            (path.parent / suffix).read_text(encoding='utf-8')
            checked[(path.parent / suffix).relative_to(ROOT).as_posix()] = digest(path.parent / suffix)
        attempts.append({k: attempt[k] for k in ('label', 'exit_code', 'elapsed_seconds',
                                               'timeout_seconds', 'source_sha256') if k in attempt})
    documentation_hashes = {}
    for name in ('notes/skew-generic-distinct-roots.md', 'README.md', '.github/workflows/lean.yml'):
        path = ROOT / name
        path.read_text(encoding='utf-8')
        documentation_hashes[name] = digest(path)
    review = {
        'status': 'PASS_READ_ONLY_AI_REVIEW_GENERIC_DISTINCT_ROOT_DEPENDENCY_CLOSED',
        'completed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'reviewer': 'distinct_review, separate adversarial AI specialist; not human review',
        'review_command': [sys.executable, '-O', str(Path(__file__).relative_to(ROOT)), '--output', args.output],
        'review_script_sha256': digest(Path(__file__)),
        'parent': 'bf0c69287865ba00d3e651cdbc4d0f881deba4db',
        'upstream': 'b790130d43b49ec0ddc6865d0bdc949eeeee2319',
        'execution_attribution': 'This reviewer executed only literal-source/hash/log audits. Lean build, axioms, replay and controls were executed by distinct_lean; exact integer computation by distinct_derivation; source gate by Pro root. No Lean, prior checker, prior mathematics, CI or remote write was executed by this reviewer.',
        'verified_saved_lean_receipt': {'path': (CHECK / 'validation.json').relative_to(ROOT).as_posix(),
            'sha256': digest(CHECK / 'validation.json'), 'status': validation['status'],
            'worker': validation['worker'], 'elapsed_seconds': validation['elapsed_seconds'],
            'lean_version': validation['lean_version'], 'mathlib_commit': validation['mathlib_commit'],
            'public_declarations': len(axioms), 'new_module_replays': 1,
            'grouped_positive_controls': 9, 'intended_false_goal_controls': 3},
        'mathematical_assessment': {
            'abstract_hypotheses': 'k is a characteristic-zero field; K is a field with an Algebra k K; v is in k and a is transcendental over k.',
            'argument': 'D=X*f_prime-15*f is a nonzero polynomial over k with D(0)=-15. A common root is algebraic over k and f(0)=1 makes it nonzero. IsAlgebraic.of_mul applied to r^15*a=P(r) forces a algebraic. The injective algebraMap transports transcendence to AlgebraicClosure K, giving the contradiction used by the coprimality/separability API.',
            'concrete_base': 'V=RatFunc Q, k=RatFunc V, K=RatFunc k, with successive independent indeterminates v,t,a and constants embeddings. Stagewise transcendence is formally proved; this is the explicitly chosen Q(v)(t)(a) presentation.',
            'extension': 'L=genericPolynomial.SplittingField is the full splitting field. k-to-K, K-to-L and k-to-L embeddings are named, injective and compatible. Characteristic zero is checked in the positive controls.',
            'tuple': 'generic_root_card proves card(rootSet L)=18 from proved separability, splitting and existing degree18. rootEquiv is an equivalence to Fin18; roots is its inverse followed by subtype value. roots_injective and roots_eval therefore give all required root data without distinctness or separability assumptions.',
            'binding': 'physical_polynomial_map identifies the mapped polynomial with the literal prior physicalPolynomial at the embedded parameters. generic_eq_split_cover and both generic trace corollaries instantiate the old conditional theorems using the constructed tuple.',
            'closed_dependency': 'Generic distinct-root data sufficient for the existing conditional physical-cover binding and two split trace corollaries.',
            'remaining_conditional_assumptions_for_chosen_concrete_theorems': [],
            'not_formalized_or_claimed': ['No separate isomorphism to a particular multivariate fraction-field implementation',
                'No universal-specialization distinctness; a=2,v=1 is formally nonseparable',
                'No unsplit descent or trace-compatible scalar-extension comparison',
                'No physical differential-source normalization, chart rederivation, rational primitive, clearing, HasCertificate or solve'],
            'smallest_future_bridge': 'If pursuing an unsplit result, compare the scalar extension of K[X]/(f) with the split L quotient and prove trace compatibility in a separate unit.'},
        'checker_assessment': ['Fresh-output allocator preserves historical paths and rejects existing outputs.',
            'Explicit require checks remain active under python -O.',
            'Saved inputs, immutable prior proofs and source pins are checked before and after verification.',
            'Current source bytes match saved snapshots and successful receipt hashes.',
            'Public axiom logs contain only propext, Classical.choice and Quot.sound.',
            'Only the new GenericDistinctRoots module is explicitly kernel-replayed.',
            'All three negative controls fail at a single intended False goal, not a missing API or typeclass.',
            'Root review found hardcoded executor provenance and scratch names keyed only by output basename in checker-01; both delivery issues were corrected and checker-02 was executed. The first successful receipt remains unchanged.',
            'No timeout was observed; development failures remain saved and are not mathematical results.'],
        'source_correspondence': load(HERE / 'preliminary-review.json')['source_correspondence'],
        'scoped_documentation_and_ci_review': {
            'raw_sha256': documentation_hashes,
            'note_and_readme': 'Read and found the claims consistent with the compiled source: generic Q(v)(t)(a) field presentation, stagewise independence, explicit embeddings, full splitting field, exact eighteen roots, old split-trace instantiations, preserved repeated specialization, and no unsplit/source-normalization/solve claim. AI execution/review and reused prior CI are distinguished.',
            'ci': 'The sole added lean.yml step invokes the focused checker after the old binding step, writes to new formal/results/runs/ci-skew-distinct-roots, and is covered by the existing artifact upload glob. Earlier CI steps are unchanged; no new remote run was observed.',
            'publication': 'Documentation correctly labels this as a local handoff for coordinator publication; no remote commit or push by this reviewer.'},
        'review_audit_failure': {'receipt': 'audit-01-failure.json', 'sha256': digest(HERE / 'audit-01-failure.json'),
            'reason': 'First file-audit script assumed all attempt receipts had a per-source hash. Checker launch receipts use a different schema. Corrected schema handling; failed script/stdout/stderr retained. No Lean or mathematical calculation was involved.'},
        'development_attempts_observed': attempts,
        'checked_artifact_raw_sha256': checked,
        'limits': ['This is a source and saved-evidence review, not an additional Lean execution.',
            'Coordinator-reported SymPy support is supporting testimony, not a computation executed by this reviewer or counted here.',
            'The prior remote CI is reused; no new remote CI result exists for this unpublished unit.',
            'Final ledger preservation, handoff archive and publication remain the integration coordinator responsibility.']}
    with output.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(review, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    print(json.dumps({'status': review['status'], 'receipt': output.relative_to(ROOT).as_posix(),
                      'sha256': digest(output), 'checked_artifacts': len(checked)}))


if __name__ == '__main__':
    main()
