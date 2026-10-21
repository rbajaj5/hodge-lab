"""Bounded, fail-closed replay of the focused audit. Run from any directory.

Usage: python experiments/skew_audit/run.py [--companion-zip /path/to/archive.zip]
Without that option the small public archive is downloaded and hash checked.
No GitHub credentials, mutations, or large search exports are used.
"""
from pathlib import Path, PurePosixPath
import argparse
import datetime
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile

if not __debug__:
    raise RuntimeError('Run without -O; archived checkers use assertions')
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'results/one-reflection-skew-audit-20261021'
ZIP_URL = 'https://github.com/user-attachments/files/33736319/one_reflection_skew_twisted_companions.zip'
ZIP_SHA = '3901f358ec9f1f46b6f4900cba80aa82160dd50d28e86e766aae826e39a960be'


def require(ok, label):
    if not ok:
        raise ValueError(label)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--companion-zip', type=Path)
    args = parser.parse_args()
    receipt = {'status':'RUNNING', 'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'python':sys.version, 'platform':platform.platform(), 'optimize':sys.flags.optimize,
               'versions':{p:importlib.metadata.version(p) for p in ('sympy','numpy','matplotlib')},
               'timeout_seconds_per_command':120, 'memory_limit':'No extra process memory cap imposed',
               'executions':[], 'limits':['No Lean build or HasCertificate proof.',
                 'No replay of the 76 MB round-four packets or the unattached large degree-seven export.',
                 'No upstream publication or changes.']}
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8')
    env.pop('PYTHONOPTIMIZE', None)

    def command(label, command_args, cwd=ROOT, rejection=False):
        start = time.perf_counter()
        item = {'label':label, 'command':['python', *command_args], 'timeout_seconds':120,
                'expected':'nonzero exit' if rejection else 'zero exit'}
        try:
            p = subprocess.run([sys.executable, *command_args], cwd=cwd, env=env,
                               capture_output=True, text=True, encoding='utf-8', timeout=120)
            # Logs use relative placeholders for transient and machine-specific paths.
            clean = lambda text:text.replace(str(cwd), '<run-directory>').replace(str(ROOT), '<repository>')
            item.update(returncode=p.returncode, stdout=clean(p.stdout), stderr=clean(p.stderr),
                        elapsed_seconds=time.perf_counter()-start)
            receipt['executions'].append(item)
            require((p.returncode != 0) if rejection else (p.returncode == 0), label)
            return p.stdout
        except subprocess.TimeoutExpired:
            item.update(timed_out=True, elapsed_seconds=time.perf_counter()-start)
            receipt['executions'].append(item)
            raise

    try:
        for row in json.loads((OUT/'input-manifest.json').read_text(encoding='utf-8')):
            require(hashlib.sha256((OUT/row['path']).read_bytes()).hexdigest()==row['sha256'], row['path'])
        packet_pins=json.loads((OUT/'packet-pins.json').read_text(encoding='utf-8'))
        for row in packet_pins['packets']:
            raw=(ROOT/row['path']).read_bytes().replace(b'\r\n',b'\n')
            require(hashlib.sha256(raw).hexdigest()==row['current_lf_sha256'], row['path'])
        receipt['input_bindings']='PASS: all vendored inputs and six existing packets'
        for name, extra in [('line.py',[]),('check_exclusions.py',['--full-e1']),
                            ('modular_e1.py',[]),('check_low_and_odd.py',[]),('check_mixed_cross.py',[])]:
            command(name, ['-B','-S',f'experiments/skew_audit/{name}',*extra])
        text=command('independent displayed transport', ['-B','experiments/skew_audit/transport.py'])
        (OUT/'transport.json').write_text(text,encoding='utf-8',newline='\n')
        command('characters and mixed cancellation', ['-B','experiments/skew_audit/characters.py'])
        for old, new, label in [('-5*U**2/(72*z**11)','-5*U**2/(71*z**11)','wrong residue coefficient'),
                               ('Ttrace[i,j]-(6 if i==j else 0)','Ttrace[i,j]-(12 if i==j else 0)','wrong trace factor')]:
            code=('from pathlib import Path; p=Path("experiments/skew_audit/transport.py").resolve(); '
                  f's=p.read_text(); old={old!r}; new={new!r}; '
                  'assert s.count(old)==1; exec(compile(s.replace(old,new),str(p),"exec"),'
                  '{"__file__":str(p),"__name__":"__main__"})')
            command(label,['-B','-c',code],rejection=True)
        command('optimization guard',['-O','-S','experiments/skew_audit/check_exclusions.py'],rejection=True)

        # Validate the corrected production checks against an actual bad input.
        code='''import sys,json
sys.path.insert(0,'experiments')
import one_reflection_skew_degree7 as d7
import one_reflection_skew_pilot as pilot
packet=json.load(open('results/one-reflection-skew-degree6/one-reflection-skew/degree-6-diagonal.json'))
eq=[{int(j):d7.e1.Q(c) for j,c in row} for row in packet['gauged_equations']]
pairs=[tuple(p) for p in packet['gauged_column_pairs']]
assert d7.require_degree6_equations(eq,pairs)
bad=[dict(q) for q in eq]; bad[0][0]+=1
try:d7.require_degree6_equations(bad,pairs)
except ValueError:pass
else:raise RuntimeError('altered equation accepted')
Z,F0,skew,F,A=pilot.make_one_reflection_skew()
pilot.check_jacobian_and_smoothness(Z,F,A)
try:pilot.check_jacobian_and_smoothness(Z,F+100*Z[0]**5*Z[1],A)
except ValueError:pass
else:raise RuntimeError('invalid smoothness bound accepted')
pilot.render_figures(json.load(open('results/one-reflection-skew-pilot/report.json')))
print('PASS: equation comparison, strict smoothness bound, both perturbations, and data-derived pilot figure')
'''
        command('production enforcement and corrected pilot figure',['-B','-c',code])

        with tempfile.TemporaryDirectory(prefix='skew-audit-') as tmp:
            tmp=Path(tmp)
            if args.companion_zip:
                raw=args.companion_zip.read_bytes()
            else:
                with urllib.request.urlopen(ZIP_URL,timeout=60) as response:
                    raw=response.read(1_000_001)
                require(len(raw)<=1_000_000,'Unexpected archive size')
            require(hashlib.sha256(raw).hexdigest()==ZIP_SHA,'Companion archive pin')
            archive=tmp/'packet.zip';archive.write_bytes(raw)
            with zipfile.ZipFile(archive) as zf:
                require(sum(x.file_size for x in zf.infolist())<2_000_000,'Archive size bound')
                for item in zf.infolist():
                    p=PurePosixPath(item.filename)
                    require(not p.is_absolute() and '..' not in p.parts and ':' not in item.filename,'Archive path')
                zf.extractall(tmp)
            packet=tmp/'one_reflection_skew_twisted_companions'
            for row in (packet/'SHA256SUMS').read_text().splitlines():
                expected, filename=row.split(maxsplit=1)
                require(hashlib.sha256((packet/filename.strip().lstrip('*')).read_bytes()).hexdigest()==expected,filename)
            files=['rank2/rank2_primitive_system.json','rank2/rank2_primitive_system_Y0.json','rank2/gauge_scalar_repair.json']
            before={f:json.loads((packet/f).read_text()) for f in files}
            for script in ['verify_twisted_companion.py','check_serving_twist.py',
                           'rank2/rank2_primitive_system.py','rank2/gauge_scalar_repair.py']:
                command('archived '+script,['-B',script],cwd=packet)
            for f in files:
                require(json.loads((packet/f).read_text())==before[f],'Regenerated packet '+f)
            receipt['companion']={'url':ZIP_URL,'sha256':ZIP_SHA,'bytes':len(raw),
                'SHA256SUMS_entries_checked':25,'positive_checkers_replayed':4,
                'three_regenerated_JSONs_equal_archive':True,'search_scripts_run':False}
        command('audit visualization',['-B','experiments/skew_audit/render.py'])
        receipt['status']='PASS'
    except Exception as exc:
        receipt.update(status='FAIL',error=repr(exc))
        raise
    finally:
        receipt['checker_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.glob('*.py'))}
        receipt['additional_input_sha256']={rel:hashlib.sha256((ROOT/rel).read_bytes()).hexdigest() for rel in [
            'experiments/one_reflection_skew_pilot.py','experiments/one_reflection_skew_degree7.py',
            'results/one-reflection-skew-audit-20261021/input-manifest.json',
            'results/one-reflection-skew-audit-20261021/packet-pins.json']}
        receipt['completed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
        (OUT/'validation.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('PASS: focused audit; see results/one-reflection-skew-audit-20261021/validation.json')


if __name__ == '__main__':
    main()
