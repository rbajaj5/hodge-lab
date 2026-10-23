"""Non-Lean regression controls for the forms -> trace receipt lifecycle.

Run with ``python3 -O test_receipt_lifecycle.py`` (60-second external bound).
The real checker preflights run against copied inputs. A test hook stops at
the first Lean command: reaching that hook is NOT a proof replay or a PASS
receipt. Mutation and path controls must reject before the hook is reached.
"""
from pathlib import Path
import hashlib
import importlib
import json
import shutil
import subprocess
import sys
import tempfile

from fresh_receipts import fresh_output_dir

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def snapshot(paths):
    return {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


class BeforeLean(Exception):
    pass


def main():
    forms = importlib.import_module('check_skew_forms')
    trace = importlib.import_module('check_skew_trace_basis')
    with tempfile.TemporaryDirectory(prefix='receipt-lifecycle-') as temporary:
        repository = Path(temporary) / 'repository'
        formal = repository / 'formal'
        paths = set()
        for checker, directory in [(forms, 'skew-forms'), (trace, 'skew-trace-basis')]:
            paths.update(ROOT / p for p in checker.SOURCES)
            paths.update((ROOT / 'results' / directory).glob('*'))
        prior_path = ROOT / 'results/skew-ambient/validation.json'
        paths.add(prior_path)
        prior = json.loads(prior_path.read_text(encoding='utf-8'))
        paths.update(ROOT / p for p in prior['reused_source_lf_sha256'])
        paths.update(ROOT / p for p in prior['source_lf_sha256']
                     if p.startswith('HodgeLab/') and p.endswith('.lean'))
        manifest = json.loads((forms.HISTORY / 'inputs.json').read_text(encoding='utf-8'))
        paths.update(ROOT.parent / pin['path'] for pin in manifest['pins'])
        trace_manifest = json.loads((trace.HISTORY / 'inputs.json').read_text(encoding='utf-8'))
        paths.update(ROOT.parent / p for p in trace_manifest['context_receipt_lf_sha256'])
        for source in sorted(paths):
            if source.is_file():
                destination = repository / source.relative_to(ROOT.parent)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)
        historical = [repository / p.relative_to(ROOT.parent) for p in paths
                      if p.is_file() and 'results' in p.parts]
        before = snapshot(historical)
        calls = []

        def stop_before_lean(label, command, *args, **kwargs):
            calls.append((label, command))
            raise BeforeLean()

        for checker, directory in [(forms, 'skew-forms'), (trace, 'skew-trace-basis')]:
            checker.ROOT = formal
            checker.HISTORY = formal / 'results' / directory
            checker.run = stop_before_lean
            sys.argv = [str(formal / (checker.__name__ + '.py'))]
            try:
                checker.main()
            except BeforeLean:
                pass
            else:
                raise RuntimeError('Expected explicit stop before Lean')
            require(calls[-1][0] == 'version', 'Unexpected preflight boundary')
        require(snapshot(historical) == before, 'Sequential preflights altered historical bytes')
        require(forms.OUT != trace.OUT, 'Fresh outputs unexpectedly overlap')
        first_trace_output = trace.OUT
        sys.argv = [str(formal / 'check_skew_trace_basis.py')]
        try:
            trace.main()
        except BeforeLean:
            pass
        require(trace.OUT != first_trace_output, 'Repeat invocation reused an output directory')
        require(snapshot(historical) == before, 'Repeated invocation altered historical bytes')
        print('PASS sequential and repeated preflights; deliberately stopped before Lean')

        # Mutate an immutable receipt in the disposable fixture only. A new
        # runtime receipt must never make this mutation acceptable.
        pinned = formal / 'results/skew-forms/validation.json'
        pinned.write_bytes(pinned.read_bytes() + b' ')
        before_calls = len(calls)
        try:
            trace.main()
        except RuntimeError as error:
            require(str(error) == 'Historical context receipt changed: formal/results/skew-forms/validation.json',
                    'Historical mutation failed for an unrelated reason')
        else:
            raise RuntimeError('Historical mutation was accepted')
        require(len(calls) == before_calls, 'Historical mutation reached a Lean command')
        print('PASS immutable historical receipt mutation rejected before Lean')

        # Exercise the actual exception handler in a separate optimized-Python
        # process: rejected outputs must not replace a saved validation file.
        collision_before = snapshot(historical)
        for checker in ['check_skew_forms.py', 'check_skew_trace_basis.py']:
            output = 'results/' + ('skew-forms' if checker == 'check_skew_forms.py' else 'skew-trace-basis')
            completed = subprocess.run([sys.executable, '-O', str(formal / checker),
                                        '--output-dir', output], cwd=formal,
                                       capture_output=True, text=True, timeout=10)
            require(completed.returncode != 0 and 'Output overlaps immutable input directory' in completed.stderr,
                    'Historical output collision failed for an unrelated reason')
        require(snapshot(historical) == collision_before, 'FAIL handler overwrote historical evidence')

        occupied = formal / 'occupied-output'
        occupied.mkdir()
        saved_pass = occupied / 'validation.json'
        saved_pass.write_text('{"status":"PASS","fixture":true}\n', encoding='utf-8')
        occupied_before = saved_pass.read_bytes()
        for checker in ['check_skew_forms.py', 'check_skew_trace_basis.py']:
            completed = subprocess.run([sys.executable, '-O', str(formal / checker),
                                        '--output-dir', str(occupied)], cwd=formal,
                                       capture_output=True, text=True, timeout=10)
            require(completed.returncode != 0 and 'FileExistsError' in completed.stderr,
                    'Occupied output failed for an unrelated reason')
            require(saved_pass.read_bytes() == occupied_before, 'Existing PASS output was overwritten')

        protected = formal / 'results/skew-forms'
        alias = formal / 'history-alias'
        alias.symlink_to(protected, target_is_directory=True)
        for rejected in [protected / 'new-run', alias / 'new-run', forms.OUT]:
            try:
                fresh_output_dir(formal, 'control', [protected], ['--output-dir', str(rejected)])
            except (RuntimeError, FileExistsError):
                pass
            else:
                raise RuntimeError('Immutable descendant, alias or existing output accepted')
        require(snapshot(historical) == collision_before, 'Path controls altered historical evidence')
        print('PASS collision, descendant, symlink-alias and existing-output rejection')
    print('PASS receipt lifecycle controls only; no Lean compiler, theorem replay, or CI run was simulated')


if __name__ == '__main__':
    main()
