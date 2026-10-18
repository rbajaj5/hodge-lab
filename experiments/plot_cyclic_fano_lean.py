#!/usr/bin/env python3
"""Visualize source-bound, concrete Lean row certificates for cyclic Fano.

Matrix pixels encode exact coefficient signs, never numerical magnitudes.
The plot distinguishes Lean's finite arithmetic from the independently checked
Python identification with polynomial coefficient rows.
"""
from __future__ import annotations

import hashlib
import json
import re
from fractions import Fraction
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/cyclic-fano-lean-figures'
INK,MUTED,PAPER='#17323B','#53666D','#FAFAF5'
TEAL,PURPLE,CORAL='#166A70','#7967AA','#B94D42'


def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def evidence():
    sources={}
    def bind(name):
        path=ROOT/name;sources[name]=sha(path);return path
    prefix='results/cyclic-fano-lean/'
    packet=load(bind(prefix+'packet.json'))
    primary=load(bind(prefix+'validation.json'))
    review=load(bind(prefix+'independent-validation.json'))
    assert packet['schema']=='cyclic-fano-lean-row-certificates-v1'
    assert packet['status']=='all16_exact_row_certificates'
    assert primary['status']==review['status']=='PASS'
    assert primary['packet_sha256']==sources[prefix+'packet.json']
    for mappings in [packet['source_bindings'],review['source_lf_sha256']]:
        for name,digest in mappings.items():assert sha(bind(name))==digest
    assert packet['columns']==175 and len(packet['cases'])==16
    assert packet['correction_labels'][119]=={'kind':'quadratic_base_pair',
            'pair':[3,4],'multiplier_powers':[0,0,0,0,0,2]}
    reviews={item['case_index']:item for item in review['cases']}
    cases=[];display=None;products=0;nonzeros=0
    for summary in packet['cases']:
        path=bind(prefix+summary['file']);assert sha(path)==summary['sha256']
        case=load(path);idx=case['case_index'];audit=reviews[idx]
        assert audit['certificate_lf_sha256']==sha(path)
        assert audit['lean_literal_data_match']
        assert sha(bind(f'formal/HodgeLab/CyclicFano/Case{idx:02d}.lean'))==audit['lean_source_lf_sha256']
        assert case['columns']==175 and case['validation']['status']=='PASS'
        assert audit['columns_annihilated']==175
        rows=case['rows'];weights=case['dual']
        assert len(rows)==len(weights)==summary['selected_rows']==audit['selected_rows']
        matrix=[[0]*175 for _ in rows];target=[row['target'] for row in rows]
        for i,row in enumerate(rows):
            assert len({j for j,c in row['entries']})==len(row['entries'])
            assert Fraction(row['row_scale'])!=0
            assert len(row['powers'])==6 and row['powers'][2]==0 and sum(row['powers'])==14
            for j,c in row['entries']:
                assert type(c) is int and c and 0<=j<175
                matrix[i][j]=c;nonzeros+=1
        assert all(sum(weights[i]*matrix[i][j] for i in range(len(rows)))==0 for j in range(175))
        pairing=sum(w*b for w,b in zip(weights,target))
        assert pairing==case['target_pairing']==audit['target_pairing'] and pairing!=0
        products+=len(rows)*176
        cases.append({'index':idx,'kind':case['kind'],'rows':len(rows),
                      'matrix_nonzeros':sum(bool(v) for row in matrix for v in row),
                      'target_pairing':pairing,'witness_lf_sha256':sha(path)})
        if idx==5:
            assert weights==[756,1] and pairing==-5
            assert rows[0]['entries']==[[119,1]] and rows[1]['entries']==[[119,-756]]
            assert target==[0,-5] and case['direction']==[[0,'1'],[69,'1']]
            display={'index':idx,'label':'mixed case 05','matrix':matrix,'target':target,
                     'weights':weights,'rhs_pairing':pairing,
                     'row_powers':[row['powers'] for row in rows],
                     'row_scales':[row['row_scale'] for row in rows]}
    assert nonzeros==611 and sum(case['rows'] for case in cases)==100
    assert primary['columns_checked']==2800 and primary['selected_rows']==100
    # Reconstruct the displayed physical rows, instead of trusting a plotted copy.
    import cyclic_fano_cubic_polars as model
    model_data=model.prepare()
    cols,rhs,metadata=model.fixed_columns({0:Fraction(1),69:Fraction(1)},model_data)
    assert metadata['correction_types']==175
    for i,(powers,scale) in enumerate(zip(display['row_powers'],display['row_scales'])):
        mon=tuple(powers);factor=Fraction(scale)
        assert [factor*column.get(mon,Fraction(0)) for column in cols]==display['matrix'][i]
        assert factor*rhs.get(mon,Fraction(0))==display['target'][i]
    assert model_data['basis'][0]=={'component':0,'cubic_powers':[3,0,0,0,0,0]}
    assert model_data['basis'][69]=={'component':1,'cubic_powers':[0,0,0,0,0,3]}
    formal=check_formal(bind,packet,cases)
    return {'schema':'cyclic-fano-concrete-lean-figure-v1','status':'PASS',
            'source_sha256':sources,'cases':cases,'display_case':display,
            'exact_integer_pairing_products':products,
            'display_physical_coefficients_checked':352,'formal':formal,
            'displayed_column_label':packet['correction_labels'][119],
            'scope':'Encoded integer systems are Lean checked over characteristic-zero fields; polynomial identification and correction completeness are independently Python checked.'}


def check_formal(bind,packet,cases):
    compilation_path=bind('formal/results/concrete-compilation-validation.json')
    receipt=load(compilation_path)
    assert receipt['schema']=='hodge-lab-concrete-compilation-v1' and receipt['status']=='PASS'
    for name,digest in receipt['sources'].items():
        assert sha(bind('formal/'+name))==digest
        if name.endswith('.lean'):
            text=(ROOT/'formal'/name).read_text(encoding='utf-8')
            assert not re.search(r'\b(sorry|admit|axiom|native_decide)\b',text)
    for name,digest in receipt['inputs'].items():assert sha(bind(name))==digest
    assert len(receipt['inputs'])==16
    export_path=bind('formal/results/concrete-export.json')
    assert sha(export_path)==receipt['export']
    binding={key:receipt[key] for key in ['sources','inputs','export']}
    assert hashlib.sha256(json.dumps(binding,sort_keys=True).encode()).hexdigest()==receipt['source_fingerprint']
    export=load(export_path)
    assert export['generator_lf_sha256']==sha(ROOT/'formal/generate_concrete.py')
    modules=['HodgeLab.RowCertificate']
    for item in export['cases']:
        idx=item['case_index'];case=next(c for c in cases if c['index']==idx)
        assert item['input_lf_sha256']==case['witness_lf_sha256']
        assert sha(bind('formal/'+item['lean_file']))==item['lean_lf_sha256']
        assert item['module']==f'HodgeLab.CyclicFano.Case{idx:02d}'
        modules.append(item['module'])
    commands=receipt['commands']
    audits=[r for r in commands if r['command']==['lake','env','lean','AuditConcrete.lean']]
    builds=[r for r in commands if r['command'][:2]==['lake','build']]
    assert len(audits)==1 and len(builds)==17 and len(commands)==18
    assert sorted(module for record in builds for module in record['command'][2:])==sorted(modules)
    for record in commands:
        assert record['exit_code']==0 and not record['expected_failure']
        assert record['source_fingerprint']==receipt['source_fingerprint']
        assert sha(bind('formal/'+record['log']))==record['log_lf_sha256']
    names={'HodgeLab.no_solution_of_row_certificate',
           'HodgeLab.no_solution_of_integer_row_certificate'}
    for module in modules[1:]:
        names.update(module+'.'+name for name in ['annihilates','separates','no_solution'])
    assert set(receipt['theorem_axioms'])==names and len(names)==50
    assert all(set(axioms)<={'propext','Classical.choice','Quot.sound'}
               for axioms in receipt['theorem_axioms'].values())
    text=(ROOT/'formal/HodgeLab/CyclicFano/Case05.lean').read_text(encoding='utf-8')
    fragments=['| 0, 119 => 1','| 1, 119 => -756','| 0 => 756','| 1 => -5',
               '(row : Fin 2) (column : Fin 175) : ℤ',
               'theorem no_solution {K : Type*} [Field K] [CharZero K]',
               'no_solution_of_integer_row_certificate matrix target dual annihilates separates']
    assert all(fragment in text for fragment in fragments)
    replay=load(bind('formal/results/concrete-direct-replay-validation.json'))
    assert replay['schema']=='hodge-lab-direct-official-replay-v1'
    assert replay['status'] in ['PASS','INCOMPLETE']
    assert 'version 4.31.0,' in replay['compiler']
    assert replay['compilation_receipt_lf_sha256']==sha(compilation_path)
    executed=bind('formal/'+replay.get('executed_runner_file','ReplayConcrete.lean'))
    assert sha(executed)==replay['runner_lf_sha256']
    if 'current_runner_lf_sha256' in replay:
        current=bind('formal/'+replay['current_runner_file'])
        assert sha(current)==replay['current_runner_lf_sha256']
        without_comments=lambda path:re.sub(r'/-.*?-/', '',path.read_text(encoding='utf-8'),flags=re.S).strip()
        assert without_comments(executed)==without_comments(current)
    assert sha(bind('formal/check_concrete_native.py'))==replay['driver_lf_sha256']
    assert sha(bind('formal/'+replay['log']))==replay['log_lf_sha256']
    assert replay['expected_modules']==modules and replay['artifacts']==receipt['artifacts']
    assert replay['replayed_modules']==modules[:len(replay['replayed_modules'])]
    complete=replay['exit_code']==0 and replay['replayed_modules']==modules
    assert (replay['status']=='PASS')==complete
    if complete:assert not replay['timed_out']
    return {'concrete_case_indices':list(range(16)),'declarations':50,
            'compilation':'PASS','direct_replay':replay['status'],
            'replayed_modules':len(replay['replayed_modules']),
            'replay_scope':'Official default replayFromImports; imported declarations trusted, not fresh mode.',
            'display_theorem':'HodgeLab.CyclicFano.Case05.no_solution',
            'scope':receipt['scope']}


def box(fig,x,y,w,h,color):
    fig.add_artist(FancyBboxPatch((x,y),w,h,transform=fig.transFigure,
                   boxstyle='round,pad=.008,rounding_size=.008',
                   facecolor=color,edgecolor='#D2DBD3',linewidth=1))


def arrow(fig,start,end,dashed=False):
    fig.add_artist(FancyArrowPatch(start,end,transform=fig.transFigure,
                   arrowstyle='-|>',mutation_scale=17,linewidth=1.4,
                   color=TEAL,linestyle='--' if dashed else '-'))


def monomial(powers):
    names=['X_0','X_1','Z','Y_0','Y_1','Y_2']
    terms=[]
    for name,power in zip(names,powers):
        if power:terms.append(name if power==1 else name+'^{'+str(power)+'}')
    return '$'+(''.join(terms) or '1')+'$'


def draw(data):
    fig=plt.figure(figsize=(17,12),facecolor=PAPER)
    fig.text(.05,.947,'Lean checks a concrete coefficient obstruction',fontsize=29,weight='bold')
    fig.text(.05,.906,'cyclic-triple-fano · discussion #112  |  Degree 8 fixed denominators  |  Exact integer row certificates',
             fontsize=13.5,color=MUTED)
    box(fig,.05,.778,.425,.083,'#EEF2EC')
    fig.text(.065,.833,'BEFORE · generic rank-gap theorem',fontsize=14,weight='bold',color=MUTED)
    fig.text(.065,.802,'Concrete dimension bounds remained assumptions.',fontsize=12.5)
    box(fig,.535,.778,.415,.083,'#EEEBF4')
    fig.text(.550,.833,'NOW · encoded finite arithmetic',fontsize=14,weight='bold',color=PURPLE)
    fig.text(.550,.802,'Lean verifies the row identities and the contradiction.',fontsize=12.5)
    arrow(fig,(.488,.819),(.520,.819))

    case=data['display_case']
    matrix=np.array([[int(np.sign(Fraction(c))) for c in row] for row in case['matrix']],dtype=int)
    target=np.array([int(np.sign(Fraction(c))) for c in case['target']],dtype=int).reshape(-1,1)
    rows=len(matrix)
    fig.text(.05,.732,r'Actual mixed case 05: $v=X_0^3\partial_{X_0}+Y_2^3\partial_{X_1}$ · 2 rows × 175 columns',
             fontsize=16,weight='bold')
    fig.text(.05,.701,'Every entry is exact after row scaling. Teal: positive; red: negative; white: zero.',
             fontsize=11.5,color=MUTED)
    ax=fig.add_axes([.12,.447,.57,.215])
    cmap=ListedColormap([CORAL,'#FFFFFF',TEAL])
    ax.imshow(matrix,aspect='auto',cmap=cmap,vmin=-1,vmax=1,interpolation='nearest')
    ax.axhline(.5,color='#D2DBD3',linewidth=.8)
    ax.set_xticks([0,49,99,119,149,174],['0','49','99','119','149','174'])
    ax.set_xlabel(r'175 projected correction columns; 119 uses $Y_2^2$ and the pair $(Y_0,Y_1)$',fontsize=10.8)
    ax.set_yticks(range(rows),[monomial(p) for p in case['row_powers']],fontsize=10 if rows<9 else 7)
    ax.set_ylabel('selected coefficient',fontsize=11)
    for i,row in enumerate(case['matrix']):
        for j,value in enumerate(row):
            if value:
                ax.text(j+4,i,str(value),va='center',fontsize=13,
                        color=TEAL if int(value)>0 else CORAL)
    for spine in ax.spines.values():spine.set_color('#D2DBD3')
    ax2=fig.add_axes([.710,.447,.025,.215])
    ax2.imshow(target,aspect='auto',cmap=cmap,vmin=-1,vmax=1,interpolation='nearest')
    ax2.set_xticks([0],['target']);ax2.set_yticks([])
    for i,value in enumerate(case['target']):
        ax2.text(0,i,str(value),ha='center',va='center',fontsize=12,
                 color=INK if int(value)==0 else 'white')
    for spine in ax2.spines.values():spine.set_color('#D2DBD3')
    box(fig,.775,.435,.175,.220,'#EEF2EC')
    fig.text(.790,.624,'Exact row functional',fontsize=13,weight='bold',color=TEAL)
    fig.text(.790,.580,r'$\lambda=(756,1)$',fontsize=22,color=PURPLE)
    fig.text(.790,.537,r'$\lambda^T M=0$',fontsize=23,color=TEAL)
    fig.text(.790,.482,r'$\lambda^T b='+str(case['rhs_pairing'])+r'\ne0$',fontsize=21,color=CORAL)
    fig.text(.12,.387,r'Column 119: $756\cdot1+1\cdot(-756)=0$.  All other 174 selected column entries are zero.',fontsize=12,color=MUTED)
    ax3=fig.add_axes([.12,.347,.57,.025])
    ax3.imshow(np.zeros((1,175)),aspect='auto',cmap=ListedColormap(['#E0EFEB']),interpolation='nearest')
    ax3.set_xticks([]);ax3.set_yticks([])
    for spine in ax3.spines.values():spine.set_color('#D2DBD3')
    ax3.text(87,0,'0 in all 175 columns',ha='center',va='center',fontsize=12,color=TEAL)
    fig.text(.755,.351,r'$0\ne'+str(case['rhs_pairing'])+'$',fontsize=21,color=CORAL)
    fig.text(.05,.302,r'If $Mx=b$, apply $\lambda^T$: the verified identities force $0=\lambda^Tb\ne0$.',
             fontsize=17,weight='bold')
    fig.text(.05,.273,'HodgeLab.CyclicFano.Case05.no_solution  ·  HodgeLab.no_solution_of_integer_row_certificate',
             fontsize=10.8,family='DejaVu Sans Mono',color=MUTED)

    box(fig,.05,.179,.9,.078,'#EEEBF4')
    fig.text(.065,.229,f"{len(data['cases'])} concrete finite systems compiled in Lean over any characteristic-zero field, including ℂ.",
             fontsize=13.5,weight='bold',color=PURPLE)
    replay=data['formal']
    replay_detail = '17 modules confirmed' if replay['direct_replay']=='PASS' else '420 s timeout'
    fig.text(.065,.198,'100 selected rows · 611 nonzero entries · 50 declarations · '
             f"Official default replay: {replay['direct_replay']} ({replay_detail}).",
             fontsize=11.5,color=TEAL if replay['direct_replay']=='PASS' else CORAL)
    fig.text(.05,.125,'Python source reconstruction',fontsize=14,weight='bold')
    fig.text(.407,.125,'Encoded integer rows',fontsize=14,weight='bold')
    fig.text(.730,.125,'Lean arithmetic + proof',fontsize=14,weight='bold')
    arrow(fig,(.300,.131),(.397,.131),True)
    arrow(fig,(.620,.131),(.720,.131))
    fig.text(.05,.075,'The polynomial-to-matrix identification remains an independently checked Python bridge.',
             fontsize=12.5,color=MUTED)
    fig.text(.05,.039,'No HodgeComputer.HasCertificate proof or instance solution is claimed. The full 175-parameter mixed family remains open.',
             fontsize=12,color=CORAL)
    OUT.mkdir(parents=True,exist_ok=True)
    fig.savefig(OUT/'concrete-lean.png',dpi=160,facecolor=PAPER)
    svg=OUT/'concrete-lean.svg'
    fig.savefig(svg,metadata={'Date':None},facecolor=PAPER)
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',
                   encoding='utf-8',newline='\n')
    plt.close(fig)


def main():
    assert __debug__, 'Run without -O so exact source checks remain enabled.'
    plt.rcParams.update({'font.family':'DejaVu Sans','text.color':INK,
                         'svg.fonttype':'none','svg.hashsalt':'cyclic-fano-lean-v1'})
    data=evidence();draw(data)
    data['renderer_lf_sha256']=sha(Path(__file__))
    (OUT/'plot-data.json').write_text(json.dumps(data,separators=(',',':'))+'\n',encoding='utf-8',newline='\n')
    assert all(sha(ROOT/name)==digest for name,digest in data['source_sha256'].items())
    print(json.dumps({'status':'PASS','source_bindings':len(data['source_sha256']),
                      'concrete_Lean_cases':len(data['cases']),
                      'separate_official_replay':data['formal']['direct_replay'],
                      'display_rows':len(data['display_case']['matrix']),
                      'plot_data_bytes':(OUT/'plot-data.json').stat().st_size}))


if __name__=='__main__':
    main()
