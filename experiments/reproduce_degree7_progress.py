"""Fetch and replay fqlx's pinned degree-seven partial-results package.

--audit-existing only checks the hashes and consistency of existing result
records. Omit it to execute the complete upstream pipeline before auditing.
The default work directory is ignored by Git; upstream source is not vendored.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT/'references/fqlx-degree7.json'


def run(source_dir, fetch=False, audit_existing=False):
    manifest = json.loads(MANIFEST.read_text())
    source_dir = source_dir.resolve()
    source_dir.mkdir(parents=True, exist_ok=True)
    if fetch:
        request = urllib.request.Request(manifest['api_url'], headers={'User-Agent': 'hodge-lab-reproduction'})
        with urllib.request.urlopen(request, timeout=60) as response:
            remote = json.load(response)
        for filename, digest in manifest['files'].items():
            assert Path(filename).name == filename
            entry = remote['files'][filename]
            assert not entry.get('truncated')
            raw = entry['content'].encode('utf-8')
            assert hashlib.sha256(raw).hexdigest() == digest
            (source_dir/filename).write_bytes(raw)
    for filename, digest in manifest['files'].items():
        assert Path(filename).name == filename
        assert hashlib.sha256((source_dir/filename).read_bytes()).hexdigest() == digest
    if not audit_existing:
        environment = dict(os.environ, PYTHONUTF8='1')
        subprocess.run([sys.executable, '-S', '-u', 'run_all.py', '--output-dir', 'reproduced'],
                       cwd=source_dir, env=environment, check=True)
    output = source_dir/'reproduced'
    names = ['eigen/degree7-eigen-verification.json', 'module.json', 'global.json',
             'pairs/degree7-two-character-verification.json', 'actual/degree7-actual-pairs-verification.json',
             'cyclic.json', 'cosets.json', 'tangent.json']
    eigen, module, global_result, pairs, actual, cyclic, cosets, tangent = [
        json.loads((output/name).read_text()) for name in names]
    assert len(eigen['sectors']) == 138 and all(s['excluded'] for s in eigen['sectors'])
    assert module['degreeSevenLowerGeneratorRank'] == 293
    assert module['directE2Duals']['J14ColumnsChecked'] == 12012
    assert module['directE2Duals']['rawSymmetricPairsChecked'] == 43660
    assert global_result['rawRelationRank'] == 7 and global_result['remainingGaugeComplementParameters'] == 282
    assert pairs['familiesTested'] == 9453
    assert (pairs['excludedByNecessaryTest'], pairs['residualSingleCharacter'], pairs['remainingMixed']) == (8644, 774, 35)
    assert pairs['allTracesSha256'] == '4183805aece9f61cf38e691fd95de76e5158f6fff6645e4f68fe371b57b927ea'
    assert actual['excluded'] == 32 and actual['remainingFamilyIndices'] == [13, 22, 30]
    assert len(cyclic['results']) == 6 and all(r['excluded'] for r in cyclic['results'])
    assert cosets['familiesTested'] == 180 and cosets['excludedBeforeActualClosure'] == 179
    assert cosets['soleNecessarySurvivorClosure']['coveredUsingEigenTheorem']
    assert tangent['factorGaugeComplementDimension'] == 6 and tangent['kernelCorrections'] == 68
    report = {'attribution': 'fqlx; all results in this record are upstream reproductions.',
              'discussion': manifest['discussion'], 'gist_revision': manifest['gist_revision'],
              'recorded_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'mode': 'existing_result_record_audit' if audit_existing else 'full_upstream_replay',
              'source_hashes_checked': len(manifest['files']),
              'result_hashes': {name: hashlib.sha256((output/name).read_bytes()).hexdigest() for name in names},
              'single_character_families_excluded': 138, 'two_character_families_excluded': 9450,
              'two_character_families_unresolved': 3, 'remaining_upstream_family_indices': [13, 22, 30],
              'global_radical_linear_restrictions': 7, 'coordinate_kernel_families_excluded': 180,
              'tangent_factor_family_excluded': True,
              'scope': 'These are the upstream results before the Hodge Lab Y0/X1 continuation. No HasCertificate proof.'}
    destination = ROOT/'results/upstream-degree7'
    destination.mkdir(parents=True, exist_ok=True)
    (destination/'replay.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('Assertions must remain enabled.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, default=ROOT/'work/upstream-degree7')
    parser.add_argument('--fetch', action='store_true')
    parser.add_argument('--audit-existing', action='store_true')
    args = parser.parse_args()
    run(args.source_dir, args.fetch, args.audit_existing)
