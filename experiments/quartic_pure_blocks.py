"""Six small pure-character blocks suffice for the five triple exclusions.

Each block has six quadratics in five variables. Its degree-four Macaulay
map has rank 70 = dim S_4, so every quartic lies in its ideal.
"""
from fractions import Fraction as Q
import argparse,json
import eisenbud_quartic_strand as q
e=q.e


def discover():
    model=e.t.Model();blocks=[]
    for number,source in q.source().items():
        stage=source['stages'][-1];eq=[e.t.cert.decode(p['polynomial']) for p in stage['necessary']]
        for char in [(0,0,0),(1,0,0)]:
            ids=[i for i in stage['active'] if model.dc[i]==char]
            if not ids:continue
            selected=[j for j,p in enumerate(eq) if all(i in ids for mon in p for i in mon)]
            small=[eq[j] for j in selected];strands=[e.strand(small,ids,d) for d in [2,3,4]]
            blocks.append({'number':number,'character':list(char),'active':ids,'equation_indices':selected,'strands':strands})
    q.save(q.OUT/'pure-blocks.json.gz',{'source_sha256':q.source_sha(),'blocks':blocks})


def check():
    packet=q.load(q.OUT/'pure-blocks.json.gz');assert packet['source_sha256']==q.source_sha()
    model=e.t.Model();sources=q.source();summaries=[]
    assert [(b['number'],b['character']) for b in packet['blocks']]==[(6,[0,0,0]),(8,[0,0,0]),(8,[1,0,0]),(10,[0,0,0]),(149,[1,0,0]),(152,[1,0,0])]
    for b in packet['blocks']:
        stage=sources[b['number']]['stages'][-1];eq=[e.t.cert.decode(p['polynomial']) for p in stage['necessary']]
        assert b['active']==[i for i in stage['active'] if model.dc[i]==tuple(b['character'])]
        assert len(b['active'])==5 and len(b['equation_indices'])==6
        small=[eq[j] for j in b['equation_indices']]
        assert all(len(mon)==2 and all(i in b['active'] for i in mon) for p in small for mon in p)
        for r in b['strands']:
            e.check_strand(small,b['active'],r) if r['degree']<4 else q.check_quartic(small,b['active'],r)
        assert [r['rank'] for r in b['strands']]==[6,30,70]
        assert b['strands'][-1]['codomain']==70
        assert sorted(p['coordinate'] for p in b['strands'][-1]['vanishings'])==b['active']
        # Koszul boundaries among independent quadratics have dimension 15.
        layers=q.syzygy_layers(small,b['active'],b['strands'][1],b['strands'][2])
        assert layers['linear_multiple_rank']==0 and layers['koszul_boundary_dimension']==15
        assert layers['new_beyond_linear_and_koszul']==5
        summaries.append({'number':b['number'],'character':b['character'],'active':b['active'],
            'quadratic_indices':b['equation_indices'],'ranks':[6,30,70],
            'domains':[r['domain'] for r in b['strands']],'codomains':[r['codomain'] for r in b['strands']],
            'kernels':[r['kernel'] for r in b['strands']],
            'hilbert_function':[1,5,9,5,0],'layers':layers,
            'power_identity_terms':sum(len(p['products']) for p in b['strands'][2]['vanishings'])})
    report={'status':'PASS','blocks':summaries,'quartic_power_identities':30,
        'scope':'Small-ideal identities and ranks; full physical reductions and residual sectors are checked separately by check_quartic_exclusions.py.'}
    (q.OUT/'pure-blocks-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='blocks'},indent=2))


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args()
    if not a.check:discover()
    check()
