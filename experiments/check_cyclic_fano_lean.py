#!/usr/bin/env python3
"""Independently reconstruct the polynomial rows of concrete Lean certificates.

Uses the earlier independent arithmetic, not the certificate exporter or
primary cubic producer. This checks the source-to-integer-matrix boundary;
Lean separately checks the finite matrix obstruction.
"""
from fractions import Fraction
from pathlib import Path
import ast
import copy
import hashlib
import json
import re
import time

import check_cyclic_fano_cubic_polars as C

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/cyclic-fano-lean'


def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def source_dependencies(path, seen=None):
    """Bind the local import closure, including the independent arithmetic."""
    seen = set() if seen is None else seen
    path = path.resolve()
    if path in seen:
        return seen
    seen.add(path)
    for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
        names = [n.name for n in node.names] if isinstance(node, ast.Import) else (
            [node.module] if isinstance(node, ast.ImportFrom) and node.module else [])
        for name in names:
            candidate = path.parent / (name.split('.')[0] + '.py')
            if candidate.is_file():
                source_dependencies(candidate, seen)
    return seen


def reconstruct(case, exact):
    index = case['case_index']
    assert isinstance(index, int) and index in range(16)
    kind, direction = C.fixed_cases()[index]
    assert case['kind'] == kind
    assert case['direction'] == [[i, str(c)] for i, c in sorted(direction.items())]
    denominator = C.A.total(C.times(exact['denominators'][i], c)
                            for i, c in direction.items())
    assert C.decode(case['denominator']) == denominator
    field = [C.A.total(C.times(exact['fields'][i][j], c)
                       for i, c in direction.items()) for j in range(6)]
    assert C.A.contraction(field, exact['G']) == C.A.mul(exact['beta'], denominator)
    columns = [C.apply_operator(operator, denominator) for operator in exact['operators']]
    rhs = C.times(C.A.B(denominator, field), -1)
    return columns, rhs


def validate(case, columns, rhs):
    assert case['schema'] == 'cyclic-fano-lean-row-certificate-v1'
    assert case['columns'] == len(columns) == 175
    rows, dual = case['rows'], case['dual']
    assert rows and len(rows) == len(dual)
    assert all(type(w) is int and w != 0 for w in dual)
    assert len({tuple(row['powers']) for row in rows}) == len(rows)
    sums = [0] * 175
    target = 0
    for row, weight in zip(rows, dual):
        powers = tuple(row['powers'])
        assert len(powers) == 6 and all(type(p) is int and p >= 0 for p in powers)
        assert powers[2] == 0 and sum(powers) == 14
        scale = Fraction(row['row_scale'])
        assert scale > 0
        sparse = {}
        for j, value in row['entries']:
            assert type(j) is int and 0 <= j < 175 and j not in sparse
            assert type(value) is int and value != 0
            sparse[j] = value
        assert type(row['target']) is int
        for j, polynomial in enumerate(columns + [rhs]):
            coefficient = polynomial.get(powers, C.ZERO)
            assert coefficient[1] == 0
            value = coefficient[0] * scale
            expected = row['target'] if j == 175 else sparse.get(j, 0)
            assert value == expected, (powers, j, value, expected)
        for j, value in sparse.items():
            sums[j] += weight * value
        target += weight * row['target']
    assert sums == [0] * 175
    assert type(case['target_pairing']) is int and target == case['target_pairing'] != 0
    return dict(case_index=case['case_index'], selected_rows=len(rows),
                physical_coefficients_checked=len(rows) * 176,
                columns_annihilated=len(sums), target_pairing=target,
                matrix_nonzero_entries=sum(len(r['entries']) for r in rows))


def negative_controls(case, columns, rhs):
    rejected = []
    for name in ['weight', 'target', 'entry', 'scale', 'monomial', 'column_count', 'missing_row']:
        bad = copy.deepcopy(case)
        if name == 'weight':
            bad['dual'][0] += 1
        elif name == 'target':
            bad['rows'][0]['target'] += 1
        elif name == 'entry':
            row = next((r for r in bad['rows'] if r['entries']), bad['rows'][0])
            if row['entries']:
                row['entries'][0][1] += 1
            else:
                row['entries'] = [[0, 1]]
        elif name == 'scale':
            bad['rows'][0]['row_scale'] = str(Fraction(bad['rows'][0]['row_scale']) * 2)
        elif name == 'monomial':
            bad['rows'][0]['powers'][2] += 1
        elif name == 'column_count':
            bad['columns'] -= 1
        else:
            bad['rows'].pop()
        try:
            validate(bad, columns, rhs)
        except (AssertionError, ValueError, KeyError):
            rejected.append(name)
        else:
            raise AssertionError('Altered input accepted: ' + name)
    return rejected


def lean_literals(case):
    """Parse literal match clauses independently of their code generator."""
    path = ROOT / f"formal/HodgeLab/CyclicFano/Case{case['case_index']:02d}.lean"
    source = path.read_text(encoding='utf-8')
    count = len(case['rows'])
    assert f'namespace HodgeLab.CyclicFano.Case{case["case_index"]:02d}' in source
    assert not re.search(r'\b(sorry|admit|axiom|native_decide|unsafe)\b', source)
    matrix = re.search(r'def matrix \(row : Fin (\d+)\) \(column : Fin (\d+)\) : ℤ :=\s*'
                       r'match row.val, column.val with\s*(.*?)\n\ndef target', source, re.S)
    assert matrix and tuple(map(int, matrix.group(1, 2))) == (count, 175)
    lines = matrix.group(3).strip().splitlines()
    assert lines[-1].strip() == '| _, _ => 0'
    actual = {}
    for line in lines[:-1]:
        match = re.fullmatch(r'\s*\| (\d+), (\d+) => (-?\d+)\s*', line)
        assert match, line
        i, j, value = map(int, match.groups())
        assert (i, j) not in actual and i in range(count) and j in range(175)
        actual[i, j] = value
    expected = {(i, j): value for i, row in enumerate(case['rows']) for j, value in row['entries']}
    assert actual == expected
    for name, expected in [('target', [r['target'] for r in case['rows']]), ('dual', case['dual'])]:
        match = re.search(r'def ' + name + r' \(row : Fin (\d+)\) : ℤ :=\s*'
                          r'match row.val with\s*(.*?)(?=\n\n)', source, re.S)
        assert match and int(match.group(1)) == count
        lines = match.group(2).strip().splitlines()
        assert lines[-1].strip() == '| _ => 0'
        values = {}
        for line in lines[:-1]:
            entry = re.fullmatch(r'\s*\| (\d+) => (-?\d+)\s*', line)
            assert entry, line
            i, value = map(int, entry.groups())
            assert i not in values
            values[i] = value
        assert values == dict(enumerate(expected))
    return path


def main():
    assert __debug__
    started = time.perf_counter()
    exact = C.derive()
    paths = sorted(OUT.glob('case-??.json'))
    assert [p.name for p in paths] == [f'case-{i:02d}.json' for i in range(16)]
    packet_path = OUT / 'packet.json'
    packet = json.loads(packet_path.read_text(encoding='utf-8'))
    for name, digest in packet['source_bindings'].items():
        assert sha(ROOT / name) == digest
    cases = []
    lean_sources = []
    for path in paths:
        case = json.loads(path.read_text(encoding='utf-8'))
        assert path.name == f"case-{case['case_index']:02d}.json"
        columns, rhs = reconstruct(case, exact)
        result = validate(case, columns, rhs)
        result['altered_inputs_rejected'] = negative_controls(case, columns, rhs)
        result['certificate_lf_sha256'] = sha(path)
        lean_path = lean_literals(case)
        lean_sources.append(lean_path)
        result['lean_literal_data_match'] = True
        result['lean_source_lf_sha256'] = sha(lean_path)
        cases.append(result)
        print(json.dumps(result), flush=True)
    dependencies = source_dependencies(Path(__file__))
    dependencies.add(ROOT / 'results/cyclic-fano-curve/source/instance.rec')
    dependencies.update(lean_sources)
    dependencies.add(packet_path)
    result = dict(schema='cyclic-fano-lean-independent-v1', status='PASS', cases=cases,
                  source_lf_sha256={p.relative_to(ROOT).as_posix(): sha(p)
                                   for p in sorted(dependencies)},
                  elapsed_seconds=round(time.perf_counter() - started, 3),
                  scope='Independent polynomial reconstruction of selected integer rows and exact dual cancellations. This script is not a Lean checker or a HasCertificate proof.')
    (OUT / 'independent-validation.json').write_text(json.dumps(result, indent=2) + '\n',
                                                    encoding='utf-8', newline='\n')
    print(json.dumps(dict(status='PASS', cases=len(cases),
                         altered_inputs_rejected=sum(len(c['altered_inputs_rejected']) for c in cases),
                         elapsed_seconds=result['elapsed_seconds'])))


if __name__ == '__main__':
    main()
