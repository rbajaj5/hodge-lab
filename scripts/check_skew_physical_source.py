"""Literal source binding for the single conditional physical-cover lemma.

This checks provenance and exact text/target-field correspondence, not a new
chart substitution, separability proof, differential-source normalization, or
Lean replay. Outputs must use a new directory. Run from the repository root:
  python3 -O scripts/check_skew_physical_source.py --output-dir /new/output/path
The output path, like the Lean checkers' paths, is relative to formal/ unless
absolute. The five mutation controls alter only strings/bytes in memory.
"""
from pathlib import Path
import datetime
import hashlib
import json
import re
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'formal'))
from fresh_receipts import fresh_output_dir

MANIFEST = ROOT / 'formal/results/skew-physical-cover/inputs.json'
MODULE = ROOT / 'formal/HodgeLab/OneReflectionSkew/PhysicalCoverBinding.lean'
BATCH = ROOT / 'results/ci-receipt-physical-cover-20261023'
EXPECTED_DEFINITION = 'X ^ 18 + X ^ 12 + (C v * X - 1) ^ 6 - C a * X ^ 15'
EXPECTED_EQUATION = 'f(r)=r^{18}+r^{12}+(vr-1)^6-ar^{15}=0.'
COMMENT = BATCH / 'inputs/context/comment-19129985.json'
CURRENT = BATCH / 'inputs/upstream/data/one-reflection-skew/record.json'
HISTORICAL = ROOT / 'results/chi-target-source/inputs/data/one-reflection-skew/record.json'


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def digest(path):
    return digest_bytes(path.read_bytes())


def normalized(text):
    return re.sub(r'\s+', '', text)


def check_definition(source):
    match = re.search(r'^def physicalPolynomial \(a v : K\) : K\[X\] :=\n(.*?)\n\n',
                      source, re.MULTILINE | re.DOTALL)
    require(match is not None, 'Literal physicalPolynomial definition not found')
    require(normalized(match.group(1)) == normalized(EXPECTED_DEFINITION),
            'Literal physicalPolynomial definition differs from pinned source equation')


def main():
    began = time.monotonic()
    output = fresh_output_dir(ROOT / 'formal', 'skew-physical-source', [
        MANIFEST.parent, BATCH / 'inputs', HISTORICAL.parent])
    receipt = {'status': 'IN_PROGRESS', 'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'command': [sys.executable, '-O', str(Path(__file__).resolve()), *sys.argv[1:]],
               'scope': 'Literal equation, immutable source pins and protected F/A/q correspondence only.',
               'mutations': []}
    def save():
        (output / 'validation.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    save()
    try:
        inputs = json.loads(MANIFEST.read_text(encoding='utf-8'))
        paths = [MANIFEST, MODULE, Path(__file__).resolve(), ROOT / 'formal/fresh_receipts.py']
        paths += [ROOT / pin['path'] for pin in inputs['physical_source_pins']]
        hashes = {str(p.relative_to(ROOT)): digest(p) for p in paths}
        require(inputs['physical_source_pins'], 'Missing physical source pins')
        for pin in inputs['physical_source_pins']:
            require(digest(ROOT / pin['path']) == pin['sha256'], 'Physical source pin changed: ' + pin['path'])
        require(inputs['literal_definition_lean'] == EXPECTED_DEFINITION, 'Manifest definition changed')
        require(inputs['literal_equation_latex'] == EXPECTED_EQUATION, 'Manifest equation changed')
        comment = json.loads(COMMENT.read_text(encoding='utf-8'))
        require(comment['url'] == 'https://github.com/hodge-computer/sextics/discussions/127#discussioncomment-19129985', 'Wrong source comment')
        require(digest_bytes(comment['body'].encode('utf-8')) == inputs['comment_body_sha256'] == comment['body_sha256'], 'Comment body hash changed')
        blocks = re.findall(r'\$\$(.*?)\$\$', comment['body'], re.DOTALL)
        require(normalized(EXPECTED_EQUATION) in [normalized(b) for b in blocks], 'Literal equation absent from pinned comment')
        source = MODULE.read_text(encoding='utf-8')
        check_definition(source)
        current = json.loads(CURRENT.read_text(encoding='utf-8'))
        historical = json.loads(HISTORICAL.read_text(encoding='utf-8'))
        for field in ['F', 'A', 'q']:
            require(current[field] == historical[field], 'Protected target field changed: ' + field)
        require(current['id'] == historical['id'] == 'one-reflection-skew', 'Wrong target')
        for label, old, new in [
            ('lower-term-sign', '- C a * X ^ 15', '+ C a * X ^ 15'),
            ('lower-exponent', 'X ^ 12', 'X ^ 13'),
            ('parameter-slot', '(C v * X - 1)', '(C a * X - 1)'),
            ('leading-coefficient', 'X ^ 18 +', 'C 2 * X ^ 18 +')]:
            candidate = source.replace(old, new, 1)
            require(candidate != source, 'Mutation fixture failed: ' + label)
            try:
                check_definition(candidate)
            except RuntimeError as error:
                require(str(error).startswith('Literal physicalPolynomial definition differs'), 'Unrelated mutation rejection')
                receipt['mutations'].append({'label': label, 'result': 'REJECTED', 'error': str(error)})
            else:
                raise RuntimeError('Source mutation was accepted: ' + label)
        raw = COMMENT.read_bytes()
        pin = next(pin for pin in inputs['physical_source_pins'] if ROOT / pin['path'] == COMMENT)
        require(digest_bytes(raw + b' ') != pin['sha256'], 'Byte mutation did not break source pin')
        receipt['mutations'].append({'label': 'pinned-source-byte', 'result': 'REJECTED_BY_SHA256'})
        require(hashes == {str(p.relative_to(ROOT)): digest(p) for p in paths}, 'Inputs changed during source check')
        receipt.update(status='PASS', source_sha256=hashes,
                       protected_target_fields_equal=['F', 'A', 'q'],
                       upstream_commit=inputs['upstream_commit'],
                       comment_body_sha256=inputs['comment_body_sha256'],
                       literal_definition=EXPECTED_DEFINITION,
                       mathematical_hypotheses_verified_here=[],
                       limitations=['No new chart derivation or differential-source normalization',
                                    'No separability, splitting roots, descent, primitive or certificate',
                                    'The pinned comment is historical author-reported source; no live discussion refresh in this checker'])
    except Exception as error:
        receipt.update(status='FAIL', error=str(error))
        raise
    finally:
        receipt['elapsed_seconds'] = time.monotonic() - began
        receipt['completed_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        save()
    print('PASS: literal source binding, three protected target fields, five source mutation controls; no mathematical replay')


if __name__ == '__main__':
    main()
