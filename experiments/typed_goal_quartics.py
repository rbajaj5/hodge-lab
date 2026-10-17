"""Separate bounded quartic continuation using only the exact target type.

Retains the preceding full-map timeouts. Constructs the full list of rows
to check literal projection, but never computes its full rank. The graded
direct-sum argument, not a completed full elimination, preserves membership.
"""
import argparse, copy, json, subprocess, sys, time
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import typed_goal_powers as g

h=g.h
OUT=h.OUT/'goal-quartics'
LIMIT=60


def query(model,n):
    _,meta,eq,counts=g.setup(model,n)
    weights=meta['weights'];targets=meta['target_local_indices']
    chars={tuple(4*x%6 for x in weights[i]) for i in targets};assert len(chars)==1
    char=next(iter(chars))
    labels,rows,types,selected=g.maps(eq,weights,len(weights),4,char)
    member,_,rank=h.cert.reduce_span([rows[i] for i in selected])
    answers=[]
    for i in targets:
        target={(i,)*4:Q(1)};w=member(target);products=None
        if w is not None:
            products=[[labels[selected[j]][0],list(labels[selected[j]][1]),c] for j,c in w['equation_weights']]
            assert h.e.expand_products(eq,products)==target
            bad=copy.deepcopy(products);bad[0][2]=str(Q(bad[0][2])+1)
            assert h.e.expand_products(eq,bad)!=target
            counts['power_identities']+=1;counts['altered_powers_rejected']+=1
        answers.append({'raw':meta['system']['basis_indices'][i],'local':i,'power':4,
                        'found':w is not None,'products':products})
    record={'family':n,'metadata':meta,'degree':4,'target_character':list(char),
            'full_rows':len(rows),'typed_rows':len(selected),'typed_rank':rank,
            'full_rank':None,'full_elimination_performed':False,
            'full_nonzeros':sum(map(len,rows)),'typed_nonzeros':sum(len(rows[i]) for i in selected),
            'selected_indices':selected,'type_counts':[[list(t),c] for t,c in sorted(Counter(types).items())],
            'matrix_sha256':g.s.sha({'labels':[[j,list(m)] for j,m in labels],
                                  'rows':[h.cert.encode(p) for p in rows]}),'queries':answers}
    counts['exact_row_projections']+=len(rows)
    counts['coordinate_power_queries']+=len(answers)
    return record,counts


def produce(n):
    p=g.read(OUT/'plan.json');assert n in p['families']
    r,_=query(h.Model(),n)
    h.q.save(OUT/f'family-{n:03d}.json.gz',{'plan_sha256':g.s.sha(p),'record':r})
    print(n,r['full_rows'],'->',r['typed_rows'],'rank',r['typed_rank'],
          'powers',[(a['raw'],a['found']) for a in r['queries']],flush=True)


def run():
    assert not (OUT/'plan.json').exists(),'Preserve the first bounded attempt'
    source=g.read(g.OUT/'plan.json')
    plan={'families':source['families'],'preceding_plan_sha256':g.s.sha(source),
          'degree':4,'limit':LIMIT,'workers':1,
          'method':'Exact target-character projection; no full matrix elimination.',
          'scope':'Follow-up selected after a full quartic timeout; not a prospective runtime comparison.'}
    (OUT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    attempts=[]
    for n in plan['families']:
        started=time.perf_counter()
        try:
            p=subprocess.run([sys.executable,'-S',str(Path(__file__).resolve()),'--produce',str(n)],
                             capture_output=True,text=True,encoding='utf-8',timeout=LIMIT)
            code=p.returncode;status='completed' if code==0 else 'error';output=p.stdout+p.stderr
        except subprocess.TimeoutExpired as ex:
            dec=lambda v:v.decode('utf-8',errors='replace') if isinstance(v,bytes) else v or ''
            code=None;status='timeout';output=dec(ex.stdout)+dec(ex.stderr)
        a={'family':n,'limit':LIMIT,'status':status,'exit_code':code,'seconds':time.perf_counter()-started}
        attempts.append(a)
        (OUT/f'family-{n:03d}.log').write_text(output,encoding='utf-8')
        (OUT/'attempts.json').write_text(json.dumps(attempts,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(a),output,flush=True)


def check(independent=False):
    if independent:
        from check_degree7_triples import IndependentModel
        model=IndependentModel()
    else:model=h.Model()
    plan=g.read(OUT/'plan.json');source=g.read(g.OUT/'plan.json');attempts=g.read(OUT/'attempts.json')
    assert plan['families']==source['families'] and plan['preceding_plan_sha256']==g.s.sha(source)
    assert plan['degree']==4 and plan['limit']==LIMIT and plan['workers']==1
    assert [a['family'] for a in attempts]==plan['families']
    records=[];counts=Counter()
    for a in attempts:
        assert a['limit']==LIMIT and a['seconds']>=0
        assert a['status'] in ['completed','timeout','error']
        if a['status']=='completed':assert a['exit_code']==0
        elif a['status']=='timeout':assert a['exit_code'] is None
        else:assert isinstance(a['exit_code'],int) and a['exit_code']!=0
        path=OUT/f'family-{a["family"]:03d}.json.gz'
        if not path.exists():
            assert a['status']!='completed';records.append({'family':a['family'],'no_packet':True});continue
        p=h.q.load(path);assert p['plan_sha256']==g.s.sha(plan)
        r,cc=query(model,a['family']);assert r==p['record'];counts.update(cc);records.append(r)
    report={'status':'PASS','independent_physical_polynomials':independent,'records':records,
            'checks':dict(counts),'scope':'Projected quartic queries only. No full-rank computation or isolated timing comparison.'}
    (OUT/(('independent-' if independent else '')+'validation.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'PASS','checks':dict(counts),'queries':[(r['family'],r.get('queries')) for r in records]}),flush=True)


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    OUT.mkdir(parents=True,exist_ok=True)
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',action='store_true')
    p.add_argument('--produce',type=int);p.add_argument('--check',action='store_true');p.add_argument('--independent',action='store_true')
    a=p.parse_args()
    if a.run:run()
    elif a.produce is not None:produce(a.produce)
    elif a.check:check(a.independent)
