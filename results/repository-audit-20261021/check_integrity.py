"""Check this audit's saved file bindings and historical-entry preservation.

Run from any directory with Python 3.11+ and Git. No network or algebra replay.
This is a snapshot check: later mathematical edits require new receipts.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
BASE = '09539bb5151f918f73ec9fd4b9faba781959c436'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, timeout=30)


def sha(path, lf=True):
    data = path.read_bytes()
    if lf:
        data = data.replace(b'\r\n', b'\n')
    return hashlib.sha256(data).hexdigest()


def entries(text):
    text = text[text.index('## Research intuition and experiments'):]
    starts = list(re.finditer(r'(?m)^(\d+)\. \*\*', text))
    result = {}
    for index, match in enumerate(starts):
        end = starts[index+1].start() if index+1 < len(starts) else text.index('## Keeping this current', match.end())
        key = int(match.group(1))
        require(key not in result, f'Duplicate checkpoint {key}')
        result[key] = text[match.start():end].rstrip()
    return result


def main():
    validation = json.loads((OUT/'validation.json').read_text(encoding='utf-8'))
    require(validation['status'] == 'PASS', 'Focused validation did not pass')
    bindings = 0
    for group, lf in [('source_lf_sha256', True), ('output_lf_sha256', True), ('figure_raw_sha256', False)]:
        for file, expected in validation[group].items():
            require(sha(ROOT/file, lf) == expected, f'Changed receipt binding: {file}')
            bindings += 1
    for command in validation['commands']:
        require(command['status'] == 'PASS', f'Failed command: {command["label"]}')
        require(sha(OUT/command['log']) == command['log_lf_sha256'], f'Changed log: {command["log"]}')
        bindings += 1

    old_text = git('show', BASE+':LEDGER.md').decode('utf-8')
    new_text = (ROOT/'LEDGER.md').read_text(encoding='utf-8')
    old, new = entries(old_text), entries(new_text)
    require(len(old) == 105 and list(new) == list(range(1, 107)), 'Unexpected checkpoint inventory/order')
    require(all(old[k] == new[k] for k in old), 'A historical checkpoint changed')
    publication_block = lambda text: text[text.index('## Posts'):text.index('## Research intuition and experiments')]
    require(publication_block(old_text) == publication_block(new_text), 'Historical publication entries changed')
    preservation = json.loads((OUT/'ledger-preservation.json').read_text(encoding='utf-8'))
    require(sha(ROOT/'LEDGER.md') == preservation['new_ledger_lf_sha256'], 'Changed ledger preservation binding')

    pilot_path = 'results/one-reflection-skew-pilot/report.json'
    old_pilot = json.loads(git('show', BASE+':'+pilot_path))
    new_pilot = json.loads((ROOT/pilot_path).read_text(encoding='utf-8'))
    for key in ['lowDegreeBaseline', 'curationAndSmoothness']:
        require(old_pilot[key] == new_pilot[key], f'Inherited pilot result changed: {key}')

    files = sorted(set(git('ls-files', '-z').decode('utf-8').split('\0') + git('ls-files', '--others', '--exclude-standard', '-z').decode('utf-8').split('\0')) - {''})
    text_count = json_count = 0
    text_suffixes = {'.md', '.py', '.json', '.lean', '.yml', '.yaml', '.toml', '.txt', '.log', '.svg', '.html', '.css', '.js', '.sh', '.ps1', '.rec'}
    for file in files:
        path = ROOT/file
        if not path.is_file() or path.suffix not in text_suffixes:
            continue
        text = path.read_text(encoding='utf-8')
        require('\ufffd' not in text, f'Replacement character: {file}')
        text_count += 1
        if path.suffix == '.json':
            json.loads(text)
            json_count += 1

    changed = sorted(set(git('diff', BASE, '--name-only').decode('utf-8').splitlines() + git('ls-files', '--others', '--exclude-standard').decode('utf-8').splitlines()))
    links = 0
    for file in changed:
        path = ROOT/file
        if path.suffix != '.md' or not path.exists():
            continue
        for target in re.findall(r'\]\(([^\s()]+)', path.read_text(encoding='utf-8')):
            if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target) or target.startswith('#'):
                continue
            local = unquote(target.split('#')[0])
            if (path.parent/local).resolve() == OUT/'final-integrity.json':
                continue  # This run writes its own receipt only after all checks pass.
            require((path.parent/local).exists(), f'Missing local link: {file} -> {target}')
            links += 1

    controls = []
    for file in ['experiments/check_one_reflection_skew_hessian.py', 'experiments/check_repository_audit_20261021.py']:
        # Loading without __main__ prevents the driver's failure handler replacing its PASS receipt.
        code = f'import runpy; runpy.run_path({file!r})["main"]()'
        command = [sys.executable, '-O', '-c', code]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', timeout=30)
        require(result.returncode != 0 and 'RuntimeError:' in result.stderr, f'-O guard failed: {file}')
        controls.append({'command': command, 'bound_seconds': 30, 'expected_failure': True,
                         'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
    git('diff', '--check')
    git('diff', '--cached', '--check')
    report = {'status': 'PASS', 'base': BASE, 'python': sys.version,
              'git': git('--version').decode().strip(),
              'command': [sys.executable, str(Path(__file__).relative_to(ROOT))],
              'program_lf_sha256': sha(Path(__file__)),
              'receipt_bindings_checked': bindings,
              'historical_entries_preserved': 105, 'checkpoints_ordered': 106,
              'posts_and_pull_requests_block_unchanged': True,
              'inherited_pilot_sections_unchanged': ['lowDegreeBaseline', 'curationAndSmoothness'],
              'utf8_text_files_checked': text_count, 'json_files_parsed': json_count,
              'changed_markdown_local_links_checked': links, 'optimization_controls': controls,
              'diff_check': 'PASS', 'cached_diff_check': 'PASS',
              'scope': 'Saved bindings, file integrity and guard failures; no fresh mathematical or Lean replay'}
    (OUT/'final-integrity.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({key: value for key, value in report.items() if key != 'optimization_controls'}))


if __name__ == '__main__':
    main()
