#!/usr/bin/env python3
"""Show support reuse, historical searches, and theorem-dependent deductions."""
from __future__ import annotations
from collections import defaultdict
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import sympy as S

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'results/cyclic-fano-support-audit'
OUT=ROOT/'results/cyclic-fano-support-audit-figures'
FACTORS=('T','C','S','R','J');DEGREES=(1,3,6,2,3)
INK,MUTED,PAPER='#17323B','#53666D','#FAFAF5'
TEAL,PURPLE,AMBER,CORAL='#166A70','#7967AA','#A56A12','#CA584C'


def sha(path):return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def decode(terms,variables):
    def value(c):return S.Rational(c) if isinstance(c,str) else S.Rational(c[0])+S.I*S.Rational(c[1])
    return S.Poly.from_dict({tuple(t['powers']):value(t['coefficient']) for t in terms},variables)


def check_data():
    path=INPUT/'packet.json';packet=load(path)
    assert packet['schema']=='cyclic-fano-support-audit-v1' and packet['status']=='PASS'
    assert packet['instance']=='cyclic-triple-fano' and packet['q']==1
    bindings={path.relative_to(ROOT).as_posix():sha(path)}
    def bind(record):
        p=ROOT/record['path'];digest=sha(p)
        assert digest==record['lf_sha256'];bindings[record['path']]=digest
        return p
    for record in (packet['source'],packet['producer'],*packet['dependencies']):bind(record)
    assert '\nq: 1\n' in ('\n'+(ROOT/packet['source']['path']).read_text(encoding='utf-8').replace('\r\n','\n'))
    product_review_path=ROOT/'results/cyclic-fano-branch-products/independent-validation.json'
    guided_review_path=ROOT/'results/cyclic-fano-guided-denominators/independent-validation.json'
    family_review_path=ROOT/'results/cyclic-fano-polar-family/independent-validation.json'
    reviews=[]
    for p in (product_review_path,guided_review_path,family_review_path):
        receipt=load(p);assert receipt['status']=='PASS';reviews.append(receipt)
        bindings[p.relative_to(ROOT).as_posix()]=sha(p)
        assert receipt['source_instance_lf_sha256']==packet['source']['lf_sha256']
        dependencies=receipt.get('independent_arithmetic_dependencies',{})
        if 'independent_arithmetic_dependency_lf_sha256' in receipt:
            dependencies={'check_cyclic_fano_unfolding.py':receipt['independent_arithmetic_dependency_lf_sha256']}
        for name,digest in dependencies.items():
            bind({'path':'experiments/'+name,'lf_sha256':digest})
    product_review,guided_review,family_review=reviews
    product_checks={c.get('attempt_id',c['id']):c for c in product_review['checks']}
    for name,receipt in (('check_cyclic_fano_branch_products.py',product_review),
                         ('check_cyclic_fano_guided_denominators.py',guided_review),
                         ('check_cyclic_fano_polar_family.py',family_review)):
        bind({'path':'experiments/'+name,'lf_sha256':receipt['checker_lf_sha256']})
    family_path=bind(packet['constant_polar_family_extension']['proof_packet']);family=load(family_path)
    assert family['status']=='PASS' and family_review['packet_lf_sha256']==sha(family_path)
    assert family_review['nonzero_parameter_implies_nonzero_denominator']
    candidate_path=ROOT/'results/cyclic-fano-higher-unfolding/candidates.json';candidates=load(candidate_path)
    assert product_review['candidate_input_lf_sha256']==sha(candidate_path)
    bindings[candidate_path.relative_to(ROOT).as_posix()]=sha(candidate_path)
    x=S.symbols('X0 X1 Z Y0 Y1 Y2')
    factors=[decode(c['quotient_denominator'],x) for c in candidates['candidates']]
    factors.extend([S.Poly(x[1]**2+x[5]**2,x),S.Poly(2*x[2],x)+decode(family['Q'],x)])
    assert len(factors)==5
    def product(exponents):
        p=S.Poly(1,x)
        for f,n in zip(factors,exponents):p*=f**n
        return p
    records=packet['records'];assert len(records)==26
    seen=set();stages=defaultdict(int)
    for r in records:
        assert r['id'] not in seen;seen.add(r['id'])
        exponents=r['exponents'];cover=r['cover_exponents']
        assert len(exponents)==len(cover)==5 and all(type(n)is int and n>=0 for n in exponents+cover)
        assert r['factor_order']==list(FACTORS)
        assert r['formal_factor_set']==[f for f,n in zip(FACTORS,exponents) if n]
        assert r['degree']==sum(n*d for n,d in zip(exponents,DEGREES))
        assert r['current_status']=='excluded_using_prescribed_support_theorem'
        for a,b,field in ((exponents,cover,'support_containment'),(cover,exponents,'same_support_reverse')):
            certificate=r[field];k=certificate['power_of_cover'];cofactor=certificate['cofactor_exponents']
            assert type(k)is int and k>0 and len(cofactor)==5 and all(type(n)is int and n>=0 for n in cofactor)
            assert [a[i]+cofactor[i] for i in range(5)]==[k*b[i] for i in range(5)]
        witness_path=bind(r['prior_obstruction']);witness=load(witness_path)
        attempt_path=ROOT/'results/cyclic-fano-branch-products'/('attempt-'+r['id']+'.json');attempt=load(attempt_path)
        bindings[attempt_path.relative_to(ROOT).as_posix()]=sha(attempt_path)
        candidate=attempt['candidate']
        assert candidate['id']==r['id'] and candidate['exponents']==exponents and candidate['degree']==r['degree']
        assert (decode(candidate['denominator'],x)-product(exponents)).is_zero
        if r['id']=='S2':
            assert r['direct_status']==attempt['status']=='timeout' and r['direct_stage']is None
            assert r['cover_id']=='S' and cover==[0,0,1,0,0]
            assert (product(exponents)-factors[2]*factors[2]).is_zero
            assert witness['status']=='excluded'
            assert r['prior_obstruction']['lf_sha256']==packet['S_fresh_independent_replay']['packet_lf_sha256']
        else:
            assert r['direct_status']==witness['status']=='excluded' and attempt['status']=='completed'
            check=product_checks[r['id']]
            assert check['packet_lf_sha256']==sha(witness_path)
            assert check['stage']==r['direct_stage'] and check['exponents']==exponents
            assert check['all_physical_column_pairings_zero']
            assert witness['candidate']==candidate
        stages[r['direct_stage']]+=1
    assert dict(stages)=={'E1':11,None:1,'E2_reflection_compact':14}
    assert len({tuple(r['formal_factor_set']) for r in records})==packet['formal_factor_set_count']==16
    assert packet['direct_exclusions_before']==25 and packet['historical_timeouts']==1
    assert packet['covered_candidates_after_theorem']==26
    history=packet['S2_history'];attempt=load(bind(history))
    assert history['status']==attempt['status']=='timeout' and history['new_degree12_dual_generated']is False
    assert history['seconds']==attempt['elapsed_seconds'] and history['time_limit_seconds']==attempt['time_limit_seconds']==120
    assert 120<history['seconds']<121
    sreplay=packet['S_fresh_independent_replay']
    assert sreplay==next(c for c in guided_review['checks'] if c['id']==sreplay['id'])
    assert sreplay['matrix_shape']==[2539,1185] and sreplay['all_column_pairings_zero']
    assert sreplay['full_numerator_coefficients']==1110 and sreplay['quotient_columns']==75
    assert sreplay['rhs_pairing']==['1','0'] and sreplay['dual_terms']==1 and sreplay['negative_controls_rejected']==2
    assert packet['controls_rejecting_new_support']==2
    for a,b in (([1,1,0,0,0],[1,0,0,0,0]),([0,1,0,0,1],[0,1,0,0,0])):
        assert any(ai>0 and bi==0 for ai,bi in zip(a,b))
    expected_url='https://github.com/hodge-computer/sextics/blob/'+packet['source_commit']+'/docs/01-certificates.md#prescribed-support-and-pole-multiplicity'
    assert packet['theorem_url']==expected_url
    return {'schema':'cyclic-fano-support-audit-plot-v1','instance':'cyclic-triple-fano','discussion_number':112,
            'sha256_policy':'File bytes with CRLF normalized to LF','source_sha256':bindings,'plot_source_sha256':sha(Path(__file__)),
            'records':records,'theorem_url':packet['theorem_url'],'theorem_dependency':packet['theorem_dependency'],
            'historical_S2_timeout_seconds':history['seconds'],'S_fixed_denominator_columns_replayed':1185,
            'formal_factor_set_count':16,'scope':packet['limits']}


def product_label(exponents):
    terms=[]
    for name,n in zip(FACTORS,exponents):
        if n:terms.append(name if n==1 else name+'^{'+str(n)+'}')
    return '$'+''.join(terms)+'$'


def draw(data):
    fig=plt.figure(figsize=(16,12.5),facecolor=PAPER)
    fig.text(.055,.954,'A support audit separates new directions from repeated multiplicities',fontsize=23,weight='bold')
    fig.text(.055,.923,'cyclic-triple-fano · discussion #112   |   26 historical products; 25 direct exclusions plus one theorem-dependent deduction',fontsize=12,color=MUTED)
    fig.text(.055,.880,r'Cited prescribed-support theorem, $q=1$: a fixed-$D$ obstruction excludes certificates with poles confined to $V(D)$.',fontsize=15,color=TEAL)
    fig.text(.055,.848,r'Since $V(D^m)=V(D)$ for $m\geq1$, extra multiplicity cannot rescue that support. This step uses the cited theorem.',fontsize=13)
    ax=fig.add_axes([.22,.325,.70,.452],facecolor=PAPER)
    groups=defaultdict(list)
    for record in data['records']:groups[tuple(record['formal_factor_set'])].append(record)
    ordering=sorted(groups,key=lambda names:(len(names),tuple(FACTORS.index(name) for name in names)))
    colors={'E1':TEAL,'E2_reflection_compact':PURPLE,None:CORAL}
    for i,names in enumerate(ordering):
        ax.axhspan(i-.43,i+.43,color='#EAF0EC' if i%2==0 else PAPER,zorder=0)
        entries=groups[names]
        lo,hi=min(r['degree'] for r in entries),max(r['degree'] for r in entries)
        if hi>lo:ax.plot([lo,hi],[i,i],color=MUTED,lw=1,alpha=.35,zorder=1)
        for item in entries:
            y=i;degree=item['degree'];color=colors[item['direct_stage']]
            ax.scatter([degree],[y],color=color,s=55 if item['direct_status']=='excluded' else 95,
                       marker='o' if item['direct_status']=='excluded' else 'D',zorder=3)
            ax.annotate(product_label(item['exponents']),(degree,y),xytext=(0,7),textcoords='offset points',
                        ha='center',va='bottom',fontsize=12,color=color)
    ax.set_yticks(range(len(ordering)),['{'+', '.join(names)+'}' for names in ordering],fontsize=12)
    ax.set_xticks(range(2,13),list(map(str,range(2,13))),fontsize=11)
    ax.set(xlim=(1.5,12.5),ylim=(len(ordering)-.3,-.9),xlabel='Weighted degree of the tested denominator')
    ax.tick_params(axis='y',length=0,pad=12,colors=INK)
    ax.tick_params(axis='x',colors=MUTED)
    ax.set_ylabel('Formal factor labels present',fontsize=12,labelpad=22)
    ax.xaxis.grid(color=MUTED,alpha=.12);ax.set_axisbelow(True)
    for name in ('top','left','right'):ax.spines[name].set_visible(False)
    ax.spines['bottom'].set_color(MUTED)
    handles=[Line2D([],[],marker='o',ls='',color=TEAL,label='Direct E1 obstruction (11)'),
             Line2D([],[],marker='o',ls='',color=PURPLE,label='Direct compact E2 obstruction (14)'),
             Line2D([],[],marker='D',ls='',color=CORAL,label='Historical timeout; now theorem-excluded (1)')]
    fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.57,.817),ncol=3,frameon=False,fontsize=11)
    fig.text(.055,.263,'Rows group formal labels, not irreducible components: 16 label sets need not be 16 different geometric supports.',fontsize=12,color=MUTED)
    fig.text(.055,.223,r'$S$ excluded by an exact 1,185-column replay  $\Longrightarrow$  $V(S^2)=V(S)$  $\Longrightarrow$  $S^2$ excluded by the theorem.',fontsize=17,color=CORAL)
    fig.text(.055,.188,'The old S² search still records a 120.06-second timeout. No degree-12 dual or successful completion of that search was produced.',fontsize=11.5)
    fig.text(.055,.145,'Adding a factor may enlarge support and needs a new test. Separate failures for two supports do not exclude their union.',fontsize=13,weight='bold')
    fig.text(.055,.103,r'For constant polars $E_v=\partial_v\Delta$, the same theorem excludes all $E_v^m$ for each fixed $v\ne0$ and $m\geq1$.',fontsize=13)
    text=fig.text(.055,.063,'Theorem dependency: sextics/docs/01-certificates.md at d96911d… · prescribed support and pole multiplicity. Not a machine-checked theorem proof.',fontsize=10,color=MUTED)
    text.set_url(data['theorem_url'])
    fig.text(.945,.022,'Fixed target unchanged · no certificate or solved instance',ha='right',fontsize=10,color=TEAL)
    OUT.mkdir(parents=True,exist_ok=True);stem=OUT/'cyclic-fano-support-audit'
    fig.savefig(stem.with_suffix('.png'),dpi=160,facecolor=PAPER)
    svg=stem.with_suffix('.svg');fig.savefig(svg,facecolor=PAPER,metadata={'Date':None})
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8',newline='\n')
    plt.close(fig)


def main():
    if not __debug__:raise RuntimeError('Run without -O so exact checks remain active.')
    data=check_data()
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'text.color':INK,'axes.labelcolor':INK,
                         'svg.fonttype':'none','svg.hashsalt':'cyclic-fano-support-audit-v1'})
    draw(data)
    (OUT/'plot-data.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':'PASS','historical_candidates':26,'formal_label_sets':16,'theorem_covered_historical_timeouts':1}))


if __name__=='__main__':main()
