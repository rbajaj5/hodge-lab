"""CUDA finite-field screen of the new cyclic-Fano power identities.

This evaluates the saved factored identities, not their already cancelled
coefficient residuals. Exact rational replay remains the proof. Install CuPy
or pass --deps for an existing isolated installation. CPU CI needs no CUDA.
"""
import argparse
import datetime as dt
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import time

from gpu_identity_screen import load_cupy

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'results/cyclic-fano-remaining66-multipliers'

CUDA = r'''
extern "C" __global__ void quadrics(
 const int count, const int samples, const long long prime,
 const long long* x, const int* offsets, const int* u, const int* v,
 const long long* coefficients, long long* values) {
 int id=blockIdx.x*blockDim.x+threadIdx.x;
 if(id>=count*samples)return;
 int q=id/samples, s=id%samples; long long total=0;
 for(int t=offsets[q];t<offsets[q+1];t++) {
   long long z=(coefficients[t]*x[s*75+u[t]])%prime;
   z=(z*x[s*75+v[t]])%prime; total=(total+z)%prime;
 }
 values[id]=total;
}
extern "C" __global__ void powers(
 const int count, const int samples, const long long prime,
 const long long* x, const long long* quadrics, const int* offsets,
 const int* equation, const int* u, const int* v,
 const long long* coefficients, const int* target, const int* degree,
 long long* good, long long* altered) {
 int id=blockIdx.x*blockDim.x+threadIdx.x;
 if(id>=count*samples)return;
 int k=id/samples, s=id%samples; long long total=0, mutation=0;
 for(int t=offsets[k];t<offsets[k+1];t++) {
   long long z=x[s*75+u[t]];
   if(v[t]>=0)z=(z*x[s*75+v[t]])%prime;
   z=(z*quadrics[equation[t]*samples+s])%prime;
   total=(total+coefficients[t]*z)%prime;
   if(t==offsets[k])mutation=z;
 }
 long long rhs=1;
 for(int r=0;r<degree[k];r++)rhs=(rhs*x[s*75+target[k]])%prime;
 good[id]=(total+prime-rhs)%prime;
 altered[id]=(good[id]+mutation)%prime;
}
'''


def sha(path):
    data = path.read_bytes()
    if path.suffix != '.gz':
        data = data.replace(b'\r\n', b'\n')
    return hashlib.sha256(data).hexdigest()


def load_identities():
    packet_path = SOURCE / 'packet.json'
    packet = json.loads(packet_path.read_text())
    bindings = {str(packet_path.relative_to(ROOT)): sha(packet_path)}
    equations, identities, labels = [], [], []
    for stage in packet['stages']:
        reduced_path = SOURCE / stage['reduced_file']
        proof_path = SOURCE / stage['power_proof_file']
        assert hashlib.sha256(reduced_path.read_bytes()).hexdigest() == stage['reduced_sha256']
        assert hashlib.sha256(proof_path.read_bytes()).hexdigest() == stage['power_proof_sha256']
        reduced = json.loads(gzip.decompress(reduced_path.read_bytes()))
        proof = json.loads(proof_path.read_text())
        active = reduced['active_raw_parameter_indices']
        assert active == proof['active_raw_parameter_indices']
        bindings[str(reduced_path.relative_to(ROOT))] = sha(reduced_path)
        bindings[str(proof_path.relative_to(ROOT))] = sha(proof_path)
        used = sorted({m['equation_index'] for identity in proof['identities']
                       for m in identity['multipliers']})
        mapping = {q: len(equations) + i for i, q in enumerate(used)}
        for q in used:
            equations.append([(active[u], active[v], Fraction(c))
                              for u, v, c in reduced['equations'][q]['terms']])
        for identity in proof['identities']:
            target = active[identity['parameter_index']]
            terms = []
            for m in identity['multipliers']:
                variables = ([m['linear_variable']] if identity['power'] == 3
                             else m['quadratic_variables'])
                terms.append((mapping[m['equation_index']], active[variables[0]],
                              active[variables[1]] if len(variables) == 2 else -1,
                              Fraction(m['coefficient'])))
            identities.append((target, identity['power'], terms))
            labels.append({'stage': stage['index'], 'raw_parameter': target,
                           'power': identity['power'], 'multiplier_terms': len(terms)})
    assert identities and len({x['raw_parameter'] for x in labels}) == len(labels)
    return equations, identities, labels, bindings


def mod(c, prime):
    assert c.denominator % prime, 'Prime divides a coefficient denominator'
    return c.numerator % prime * pow(c.denominator, -1, prime) % prime


def cpu_sample(equations, identities, points, prime):
    good, altered = [], []
    for point in points:
        values = [sum(mod(c, prime) * int(point[u]) * int(point[v])
                      for u, v, c in q) % prime for q in equations]
        gs, bad = [], []
        for target, degree, terms in identities:
            total, mutation = 0, None
            for q, u, v, c in terms:
                z = int(point[u]) * (int(point[v]) if v >= 0 else 1) * values[q] % prime
                total = (total + mod(c, prime) * z) % prime
                if mutation is None:
                    mutation = z
            residual = (total - pow(int(point[target]), degree, prime)) % prime
            gs.append(residual)
            bad.append((residual + mutation) % prime)
        good.append(gs)
        altered.append(bad)
    return good, altered


def main():
    import numpy as np
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--deps', type=Path)
    parser.add_argument('--points', type=int, default=4096)
    parser.add_argument('--seed', type=int, default=20261017)
    parser.add_argument('--output', type=Path, default=ROOT / 'results/cyclic-fano-powers-gpu')
    args = parser.parse_args()
    assert args.points >= 8
    equations, identities, labels, bindings = load_identities()
    cp, handles = load_cupy(args.deps)
    qkernel, pkernel = cp.RawKernel(CUDA, 'quadrics'), cp.RawKernel(CUDA, 'powers')
    runs = []
    for prime in (65521, 65519):
        assert all(prime % k for k in range(2, int(prime ** .5) + 1))
        rng = np.random.default_rng(args.seed + prime)
        points = rng.integers(0, prime, (args.points, 75), dtype=np.int64)
        qo, qu, qv, qc = [0], [], [], []
        for q in equations:
            for u, v, c in q:
                qu.append(u); qv.append(v); qc.append(mod(c, prime))
            qo.append(len(qc))
        io, iq, iu, iv, ic, target, degrees = [0], [], [], [], [], [], []
        for t, d, terms in identities:
            target.append(t); degrees.append(d)
            for q, u, v, c in terms:
                iq.append(q); iu.append(u); iv.append(v); ic.append(mod(c, prime))
            io.append(len(ic))
        gpu_x = cp.asarray(points)
        qarrays = [cp.asarray(v, dtype=cp.int32) for v in (qo, qu, qv)]
        qcoef = cp.asarray(qc, dtype=cp.int64)
        iarrays = [cp.asarray(v, dtype=cp.int32) for v in (io, iq, iu, iv)]
        icoef = cp.asarray(ic, dtype=cp.int64)
        targets, powers = cp.asarray(target, dtype=cp.int32), cp.asarray(degrees, dtype=cp.int32)
        qvalues = cp.empty((len(equations), args.points), dtype=cp.int64)
        good = cp.empty((len(identities), args.points), dtype=cp.int64)
        bad = cp.empty_like(good)
        def launch():
            qkernel(((qvalues.size + 127)//128,), (128,),
                    (np.int32(len(equations)), np.int32(args.points), np.int64(prime),
                     gpu_x, *qarrays, qcoef, qvalues))
            pkernel(((good.size + 127)//128,), (128,),
                    (np.int32(len(identities)), np.int32(args.points), np.int64(prime),
                     gpu_x, qvalues, *iarrays, icoef, targets, powers, good, bad))
        launch(); cp.cuda.Device().synchronize()  # compile/warm up, excluded from timing
        start = time.perf_counter(); launch(); cp.cuda.Device().synchronize()
        elapsed = time.perf_counter() - start
        good_cpu, bad_cpu = cp.asnumpy(good), cp.asnumpy(bad)
        assert not np.any(good_cpu)
        detections = np.count_nonzero(bad_cpu, axis=1)
        assert np.all(detections > 0)
        expected, mutated = cpu_sample(equations, identities, points[:8], prime)
        assert np.array_equal(good_cpu[:, :8].T, np.asarray(expected))
        assert np.array_equal(bad_cpu[:, :8].T, np.asarray(mutated))
        runs.append({'prime': prime, 'samples_per_identity': args.points,
                     'valid_nonzero_residuals': int(np.count_nonzero(good_cpu)),
                     'altered_identities_detected': int(np.count_nonzero(detections)),
                     'mutation_failures_per_identity': detections.tolist(),
                     'cpu_crosscheck_points_per_identity': 8,
                     'gpu_compute_seconds_excluding_compile_and_transfer': elapsed})
    properties = cp.cuda.runtime.getDeviceProperties(0)
    report = {'status': 'PASS', 'created_at': dt.datetime.now(dt.timezone.utc).isoformat(),
              'device': properties['name'].decode(), 'cupy_version': cp.__version__,
              'cuda_runtime_version': cp.cuda.runtime.runtimeGetVersion(),
              'driver_version': cp.cuda.runtime.driverGetVersion(),
              'seed': args.seed, 'identity_count': len(identities),
              'referenced_quadrics': len(equations), 'identities': labels, 'runs': runs,
              'source_bindings': bindings, 'script_sha256': sha(Path(__file__)),
              'loader_sha256': sha(Path(__file__).with_name('gpu_identity_screen.py')),
              'coverage': 'Only the selected identities in this new reduction chain. The older nine vanishings and the inherited25-family closure are checked by the rational verifiers, not by this GPU run.',
              'mutation': 'Add one to the first multiplier coefficient in each identity.',
              'arithmetic': 'Integer modular products use signed64; each product is below prime squared. No floating-point rank test.',
              'limits': 'Finite evaluations are a supplementary error screen, not a proof over Q or C. The separately recorded rational coefficient checks prove the identities. No timing comparison or search speedup is claimed.'}
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output/'report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: report[k] for k in ('status', 'device', 'identity_count', 'referenced_quadrics')}))
    print(json.dumps(runs))


if __name__ == '__main__':
    main()
