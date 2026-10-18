#!/usr/bin/env python3
"""Export small exact row-functional certificates for frozen cubic polar matrices.

This uses the frozen producer's physical columns. A separate independent
checker reconstructs their polynomial provenance. No older files are changed.
"""
from fractions import Fraction as Q
from pathlib import Path
from math import gcd, lcm
import argparse
import copy
import hashlib
import json
import subprocess
import sys
import time
import cyclic_fano_cubic_polars as model

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/cyclic-fano-lean'
REPORT = ROOT / 'results/cyclic-fano-cubic-gpu/report.json'


def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def add_scaled(row, other, scalar):
    for k, v in other.items():
        value = row.get(k, Q(0)) + scalar * v
        if value:
            row[k] = value
        else:
            row.pop(k, None)


def physical_rows(columns, rhs):
    rows = {}
    for j, p in enumerate(columns + [rhs]):
        for m, c in p.items():
            rows.setdefault(m, {})[j] = c
    return rows


def find_dual(rows, nonzero_rows_only, bound=90):
    started = time.perf_counter()
    chosen = [(m, row) for m, row in rows.items()
              if not nonzero_rows_only or any(j < 175 for j in row)]
    chosen.sort(key=lambda x: (sum(j < 175 for j in x[1]), len(x[1]), x[0]))
    pivots = {}
    processed = 0
    for m, original in chosen:
        if time.perf_counter() - started > bound:
            return None, dict(status='time_bound', rows_processed=processed, pivot_count=len(pivots),
                             bound_seconds=bound, nonzero_rows_only=nonzero_rows_only)
        row, combination = dict(original), {m: Q(1)}
        while row:
            pivot = min(row)
            if pivot == 175:
                factor = row[175]
                dual = {k: c/factor for k,c in combination.items()}
                return dual, dict(status='found', rows_processed=processed+1, pivot_count=len(pivots),
                                  nonzero_rows_only=nonzero_rows_only,
                                  elapsed_seconds=round(time.perf_counter()-started,6))
            if pivot not in pivots:
                factor = row[pivot]
                row = {k: c/factor for k,c in row.items()}
                combination = {k: c/factor for k,c in combination.items()}
                pivots[pivot] = row, combination
                break
            known, history = pivots[pivot]
            factor = row[pivot]
            add_scaled(row, known, -factor)
            add_scaled(combination, history, -factor)
        processed += 1
    return None, dict(status='no_obstruction_in_selected_rows', rows_processed=processed,
                     pivot_count=len(pivots), nonzero_rows_only=nonzero_rows_only,
                     elapsed_seconds=round(time.perf_counter()-started,6))


def integer_witness(rows, dual):
    selected=[]; weights=[]
    for m,c in sorted(dual.items()):
        row=rows[m];den=lcm(*(v.denominator for v in row.values()))
        entries={j:int(v*den) for j,v in row.items()}
        common=gcd(*entries.values());scale=Q(den,common)
        entries={j:v//common for j,v in entries.items()}
        selected.append(dict(powers=list(m),entries=[[j,v]for j,v in sorted(entries.items())if j<175],
                             target=entries.get(175,0),row_scale=str(scale)))
        weights.append(c/scale)
    den=lcm(*(c.denominator for c in weights));ints=[int(c*den)for c in weights]
    common=gcd(*ints);ints=[v//common for v in ints]
    if next(v for v in ints if v)<0:ints=[-v for v in ints]
    target=sum(c*row['target']for c,row in zip(ints,selected))
    assert target
    return selected,ints,target


def verify_data(certificate, rows):
    assert certificate['columns']==175 and isinstance(certificate['target_pairing'],int)
    selected=certificate['rows'];dual=certificate['dual']
    assert selected and len(selected)==len(dual) and all(isinstance(c,int)and c for c in dual)
    assert len({tuple(row['powers'])for row in selected})==len(selected)
    totals=[0]*175;target=0
    for record,c in zip(selected,dual):
        assert isinstance(record['target'],int)
        assert all(isinstance(j,int)and isinstance(v,int)for j,v in record['entries'])
        m=tuple(record['powers']);scale=Q(record['row_scale'])
        assert m in rows and scale>0
        actual={j:Q(v)*scale for j,v in rows[m].items()}
        assert all(v.denominator==1 for v in actual.values())
        expected={j:Q(v)for j,v in record['entries']}
        assert len(expected)==len(record['entries']) and all(j in range(175)and v for j,v in expected.items())
        if record['target']:expected[175]=Q(record['target'])
        assert actual==expected
        for j,v in record['entries']:totals[j]+=c*v
        target+=c*record['target']
    assert totals==[0]*175
    assert target==certificate['target_pairing'] and target!=0
    return dict(selected_rows=len(selected),matrix_nonzero_entries=sum(len(r['entries'])for r in selected),
                columns_checked=175,target_pairing=target,
                largest_integer_bits=max(abs(v).bit_length()for r in selected for j,v in r['entries'])if any(r['entries']for r in selected) else 0)


def negative_controls(result,rows):
    controls=[]
    for field in ['dual','target','entry']:
        bad=copy.deepcopy(result)
        if field=='dual':bad['dual'][0]+=1
        elif field=='target':bad['rows'][0]['target']+=1
        else:
            row=next((r for r in bad['rows']if r['entries']),bad['rows'][0])
            if row['entries']:row['entries'][0][1]+=1
            else:row['entries']=[[0,1]]
        try:verify_data(bad,rows)
        except (AssertionError,ValueError,KeyError):controls.append(field)
        else:raise AssertionError('Mutation accepted: '+field)
    return controls

def compute_case(index):
    report=json.loads(REPORT.read_text(encoding='utf-8'));entry=report['cases'][index]
    columns,rhs,meta=model.fixed_columns(dict(entry['direction']))
    assert meta['denominator']==entry['denominator'] and meta['direction']==entry['direction']
    rows=physical_rows(columns,rhs)
    attempts=[]
    dual,attempt=find_dual(rows,True);attempts.append(attempt)
    if dual is None:
        dual,attempt=find_dual(rows,False);attempts.append(attempt)
    assert dual is not None,'No bounded exact witness found'
    selected,weights,target=integer_witness(rows,dual)
    result=dict(schema='cyclic-fano-lean-row-certificate-v1',case_index=index,kind=entry['kind'],
                direction=entry['direction'],denominator=entry['denominator'],columns=175,
                rows=selected,dual=weights,target_pairing=target,attempts=attempts,
                row_definition='Each selected row equals row_scale times the coefficient row of the frozen polynomial map, including rhs=-B_E(P0).')
    stats=verify_data(result,rows)
    controls=negative_controls(result,rows)
    result['validation']=dict(status='PASS',**stats,altered_inputs_rejected=controls)
    return result


def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')


def main():
    assert __debug__
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['case','all','verify'])
    parser.add_argument('--case',type=int,default=5)
    args=parser.parse_args()
    if args.command=='case':
        started=time.perf_counter();result=compute_case(args.case)
        result['elapsed_seconds']=round(time.perf_counter()-started,6)
        save(OUT/f'case-{args.case:02d}.json',result)
        print(json.dumps(dict(case=args.case,**result['validation'],elapsed_seconds=result['elapsed_seconds'])),flush=True)
    elif args.command=='all':
        OUT.mkdir(parents=True,exist_ok=True)
        attempts=[]
        for index in [5,*range(6,16),*range(5)]:
            started=time.perf_counter()
            command=[sys.executable,'-B','-S',str(Path(__file__).resolve()),'case','--case',str(index)]
            try:
                result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=120)
                record=dict(case_index=index,status='completed'if result.returncode==0 else'failed',
                            returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,
                            bound_seconds=120,elapsed_seconds=round(time.perf_counter()-started,6))
            except subprocess.TimeoutExpired as error:
                record=dict(case_index=index,status='timeout',bound_seconds=120,
                            elapsed_seconds=round(time.perf_counter()-started,6),
                            stdout=str(error.stdout or''),stderr=str(error.stderr or''))
            attempts.append(record)
            print(json.dumps(record),flush=True)
        source_paths=[Path(__file__).resolve(),REPORT,
                      ROOT/'experiments/cyclic_fano_cubic_polars.py',
                      ROOT/'experiments/cyclic_fano_linear_polars.py',
                      ROOT/'experiments/cyclic_fano_transfer.py',
                      ROOT/'experiments/quadric_contact_pilot.py',
                      ROOT/'results/cyclic-fano-cubic-polars/packet.json',
                      ROOT/'results/cyclic-fano-curve/source/instance.rec']
        data=model.prepare()
        cases=[]
        for attempt in sorted(attempts,key=lambda a:a['case_index']):
            if attempt['status']!='completed':continue
            path=OUT/f"case-{attempt['case_index']:02d}.json"
            result=json.loads(path.read_text(encoding='utf-8'))
            cases.append(dict(case_index=result['case_index'],file=path.name,sha256=sha(path),
                              kind=result['kind'],**result['validation']))
        manifest=dict(schema='cyclic-fano-lean-row-certificates-v1',
                      status='all16_exact_row_certificates'if len(cases)==16 else'partial',
                      source_commit='d96911d725077e66a8f10848908be01a643b1714',
                      source_bindings={path.relative_to(ROOT).as_posix():sha(path)for path in source_paths},
                      spatial_variables=['X0','X1','Z','Y0','Y1','Y2'],
                      correction_labels=data['correction_labels'],columns=175,cases=cases,attempts=attempts,
                      scope='Exact row-functional exclusions for the frozen16 fixed denominators; no full175-parameter family exclusion or new rank computation.',
                      formalization_boundary='Selected integer matrices can be kernel-checked separately. Polynomial-to-matrix provenance and correction completeness remain external unless formalized.')
        save(OUT/'packet.json',manifest)
    else:
        packet=json.loads((OUT/'packet.json').read_text(encoding='utf-8'))
        for name,digest in packet['source_bindings'].items():assert sha(ROOT/name)==digest,name
        assert packet['columns']==175 and len(packet['attempts'])==16
        assert {a['case_index']for a in packet['attempts']}==set(range(16))
        assert packet['correction_labels']==model.prepare()['correction_labels']
        checked=[];mutations=0;report=json.loads(REPORT.read_text(encoding='utf-8'))
        for item in packet['cases']:
            path=OUT/item['file'];assert sha(path)==item['sha256']
            certificate=json.loads(path.read_text(encoding='utf-8'))
            index=certificate['case_index'];entry=report['cases'][index]
            assert item['case_index']==index and item['kind']==certificate['kind']
            assert certificate['kind']==entry['kind'] and certificate['direction']==entry['direction']
            columns,rhs,meta=model.fixed_columns(dict(certificate['direction']))
            assert certificate['denominator']==meta['denominator']==entry['denominator']
            rows=physical_rows(columns,rhs)
            stats=verify_data(certificate,rows)
            controls=negative_controls(certificate,rows)
            assert controls==certificate['validation']['altered_inputs_rejected']
            mutations+=len(controls)
            for key,value in stats.items():assert item[key]==value
            checked.append(dict(case_index=index,**stats))
        assert len(checked)==16 and {c['case_index']for c in checked}==set(range(16))
        assert packet['status']=='all16_exact_row_certificates'
        receipt=dict(status='PASS',schema='cyclic-fano-lean-row-validation-v1',
                     packet_sha256=sha(OUT/'packet.json'),exporter_sha256=sha(Path(__file__)),
                     cases=checked,columns_checked=16*175,
                     selected_rows=sum(c['selected_rows']for c in checked),
                     altered_inputs_rejected=mutations,
                     scope=packet['scope'])
        save(OUT/'validation.json',receipt)
        print(json.dumps(receipt),flush=True)


if __name__=='__main__':main()
