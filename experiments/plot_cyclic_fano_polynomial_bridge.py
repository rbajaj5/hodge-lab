#!/usr/bin/env python3
"""Source-bound polynomial-to-coefficient bridge for cyclic-Fano case 05.

This figure follows exact polynomial operations and coefficient extraction.
The completeness of the correction space is a separate mathematical boundary.
"""
from __future__ import annotations

import hashlib
import json
import re
from fractions import Fraction as Q
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/cyclic-fano-polynomial-bridge-figures'
CI_RUN='39089131101'
INK,MUTED,PAPER='#17323B','#53666D','#FAFAF5'
TEAL,PURPLE,CORAL='#166A70','#7967AA','#B94D42'


def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def physical_evidence(bind):
    import cyclic_fano_cubic_polars as model
    packet=load(bind('results/cyclic-fano-lean/packet.json'))
    review=load(bind('results/cyclic-fano-lean/independent-validation.json'))
    assert review['status']=='PASS'
    for mapping in [packet['source_bindings'],review['source_lf_sha256']]:
        for name,digest in mapping.items():assert sha(bind(name))==digest
    summary=next(item for item in packet['cases'] if item['case_index']==5)
    case_path=bind('results/cyclic-fano-lean/'+summary['file'])
    assert sha(case_path)==summary['sha256']
    case=load(case_path)
    audit=next(item for item in review['cases'] if item['case_index']==5)
    assert audit['certificate_lf_sha256']==sha(case_path)
    assert audit['lean_literal_data_match']
    data=model.prepare();poly=model.poly;base=model.base
    direction={0:Q(1),69:Q(1)}
    columns,rhs,metadata=model.fixed_columns(direction,data)
    assert metadata['correction_types']==175
    assert metadata['denominator']==case['denominator']
    E=base.total(data['Es'][index] for index in direction)
    v=[{} for _ in range(6)]
    v[0]={(3,0,0,0,0,0):Q(1)}
    v[1]={(0,0,0,0,0,3):Q(1)}
    assert E==base.contraction(v,data['delta'])
    direct_column=poly.mul({(0,0,0,0,0,2):Q(1)},poly.add(
        poly.mul(data['dd'][4],poly.derivative(E,3)),
        poly.mul(data['dd'][3],poly.derivative(E,4)),-1))
    direct_rhs=poly.scale(poly.add(poly.mul(poly.add(
        base.contraction(v,data['beta']),poly.mul(data['beta'],base.div(v))),E),
        poly.mul(data['beta'],base.contraction(v,E)),-1),4)
    assert direct_column==columns[119] and direct_rhs==rhs
    expected_powers=[(0,1,0,7,1,5),(1,0,0,5,2,6)]
    expected_scales=[Q(49,2400),Q(147,40)]
    raw=[]
    for index,(row,monomial,scale) in enumerate(zip(case['rows'],expected_powers,expected_scales)):
        assert row['powers']==list(monomial) and Q(row['row_scale'])==scale
        values=[column.get(monomial,Q(0)) for column in columns]
        assert all(not value for j,value in enumerate(values) if j!=119)
        assert values[119]==[Q(2400,49),Q(-1440,7)][index]
        target=rhs.get(monomial,Q(0))
        assert target==[Q(0),Q(-200,147)][index]
        assert [[j,int(scale*value)] for j,value in enumerate(values) if value]==row['entries']
        assert scale*target==row['target']
        raw.append({'powers':list(monomial),'column119':str(values[119]),
                    'target':str(target),'scale':str(scale),
                    'scaled_column119':int(scale*values[119]),'scaled_target':int(scale*target)})
    assert case['dual']==[756,1] and case['target_pairing']==-5
    assert 756*raw[0]['scaled_column119']+raw[1]['scaled_column119']==0
    assert 756*raw[0]['scaled_target']+raw[1]['scaled_target']==-5
    return {'physical_coefficients_checked':352,'rows':raw,'dual':[756,1],
            'target_pairing':-5,'correction_columns':175,
            'operator119_label':packet['correction_labels'][119],
            'polynomials':{name:model.encode(value) for name,value in {
                'Q':data['q'],'H':data['h'],'Delta':data['delta'],'beta':data['beta'],
                'E':E,'column119':columns[119],'rhs':rhs}.items()},
            'term_counts':{'Delta':len(data['delta']),'E':len(E),
                           'column119':len(columns[119]),'rhs':len(rhs)}}


def formal_evidence(bind,physical):
    assert CI_RUN.isdigit(), 'Final rendering requires a reviewed, archived CI run.'
    prefix='formal/results/polynomial-bridge-ci/'+CI_RUN+'/'
    archive=load(bind(prefix+'metadata.json'))
    assert archive['schema']=='hodge-lab-polynomial-bridge-ci-archive-v1'
    assert archive['status']=='PASS'
    run=archive['run']
    assert run['status']=='completed' and run['conclusion']=='success'
    for name,digest in archive['archived_files_raw_sha256'].items():
        # Archived logs/JSON were written with LF. Canonical LF also survives
        # a text-mode checkout without claiming a new binary artifact audit.
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert sha(bind(prefix+name))==digest
    manifest=load(bind('formal/results/polynomial-bridge-export.json'))
    audit=load(ROOT/prefix/'independent-validation.json')
    receipt=load(ROOT/prefix/'validation.json')
    assert manifest['schema']=='hodge-lab-case05-polynomial-export-v1'
    assert audit['schema']=='cyclic-fano-polynomial-bridge-independent-v1'
    assert receipt['schema']=='hodge-lab-polynomial-bridge-lean-v1'
    assert audit['status']==receipt['status']=='PASS'
    assert str(receipt['github_run_id'])==CI_RUN and receipt['github_sha']==run['headSha']
    for source_map in [manifest['source_lf_sha256'],audit['source_lf_sha256'],receipt['source_lf_sha256']]:
        for name,digest in source_map.items():assert sha(bind(name))==digest
    assert manifest['variable_order']==['X0','X1','Y0','Y1','Y2']
    assert manifest['direction']==[[0,'1'],[69,'1']]
    assert manifest['correction_count']==physical['correction_columns']==175
    assert manifest['coefficient_checks']==physical['physical_coefficients_checked']==352
    assert manifest['selected_rows']==[row['powers'][:2]+row['powers'][3:] for row in physical['rows']]
    assert manifest['row_scales']==[row['scale'] for row in physical['rows']]
    assert audit['formal_export_manifest_audit']['modules']==manifest['modules']
    assert audit['formal_export_manifest_audit']['theorem_names']==manifest['theorem_names']
    assert audit['field_extension_audit']['status']=='PASS'
    theorem='HodgeLab.CyclicFano.Case05Polynomial.no_polynomial_solution_over'
    assert audit['field_extension_audit']['theorem']==theorem
    assert theorem in manifest['theorem_names']
    assert receipt['modules']==manifest['modules']
    assert 'version 4.31.0,' in receipt['lean_version']
    commands=receipt['commands'];by_label={record['label']:record for record in commands}
    assert len(by_label)==len(commands)
    log_paths=archive['command_log_archive_paths']
    assert set(log_paths)=={record['log'] for record in commands}
    def command_text(record):
        return (ROOT/prefix/log_paths[record['log']]).read_text(encoding='utf-8')
    for record in commands:
        assert record['status']=='PASS'
        assert sha(ROOT/prefix/log_paths[record['log']])==record['log_lf_sha256']
        if record['expected_failure']:
            assert record['exit_code']!=0
        else:
            assert record['exit_code']==0
    for index,module in enumerate(manifest['modules']):
        build=by_label[f'build-{index:02d}'];kernel=by_label[f'kernel-{index:02d}']
        assert build['command']==['lake','build',module]
        assert kernel['command']==['lake','env','leanchecker',module]
        assert build['artifact_raw_sha256']==kernel['artifact_raw_sha256']
    log=command_text(by_label['axioms'])
    matches=re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]",log)
    parsed={name:[a.strip() for a in values.split(',') if a.strip()] for name,values in matches}
    assert len(matches)==len(manifest['theorem_names'])
    assert set(parsed)==set(manifest['theorem_names'])
    assert parsed==receipt['theorem_axioms']
    assert all(set(values)<={'propext','Classical.choice','Quot.sound'} for values in parsed.values())
    controls=receipt['negative_controls']
    assert [control['label'] for control in controls]==[control['label'] for control in manifest['negative_controls']]
    false_goals={
        'scale':'rowScale (0 : Fin 2) * coefficient (rowExponent 0) (columnSparse 119) ≠ (Case05.matrix 0 119 : ℚ)',
        'density':'rowScale (1 : Fin 2) * coefficient (rowExponent 1) rhsSparse ≠ (Case05.target 1 : ℚ)'}
    for control,definition in zip(controls,manifest['negative_controls']):
        assert control['rejected_mutated_source'] and control['false_goal_compiled']
        record=by_label['negative-'+control['label']]
        assert record['expected_failure'] and control['log']==record['log']
        text=command_text(record)
        assert 'error:' in text and 'decide' in text
        original=(ROOT/definition['file']).read_text(encoding='utf-8')
        assert original.count(definition['before'])==1
        changed=original.replace(definition['before'],definition['after'],1)
        assert hashlib.sha256(changed.encode('utf-8')).hexdigest()==control['mutated_source_lf_sha256']
        assert control['false_goal']==false_goals[control['label']]
        probe_prefix,separator,_=changed.partition('set_option maxRecDepth')
        assert separator and 'theorem computed_column_coefficients' not in probe_prefix
        name='mutation_'+control['label']+'_is_false'
        expected=probe_prefix+'set_option maxRecDepth 100000 in\nset_option maxHeartbeats 4000000 in\n'
        expected+='theorem '+name+' :\n    '+control['false_goal']+' := by\n  decide +kernel\n'
        expected+='#print axioms '+name+'\nend HodgeLab.CyclicFano.Case05Polynomial\n'
        assert control['false_goal_proof_source']==expected
        assert hashlib.sha256(expected.encode('utf-8')).hexdigest()==control['false_goal_proof_lf_sha256']
        proof=by_label['negative-proof-'+control['label']]
        assert proof['exit_code']==0 and not proof['expected_failure']
        assert proof['log']==control['false_goal_proof_log']
        reports=re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]",command_text(proof))
        assert len(reports)==1 and reports[0][0]=='HodgeLab.CyclicFano.Case05Polynomial.'+name
        assert {a.strip() for a in reports[0][1].split(',') if a.strip()}<={'propext','Classical.choice','Quot.sound'}
    return {'status':'PASS','theorem':theorem,'ci_run_id':CI_RUN,
            'tested_commit':receipt['github_sha'],'modules':len(manifest['modules']),
            'declarations':len(parsed),'rejected_Lean_controls':len(controls),
            'python_mutation_controls':len(audit['altered_inputs_rejected']),
            'recorded_build_replay_digest_pairs':len(manifest['modules']),
            'binary_artifacts_independently_audited':False,
            'caption':'Lean: explicit polynomial operators → coefficient extraction → contradiction over every characteristic-zero field.',
            'evidence_caption':f"{len(manifest['modules'])} modules replayed · {len(parsed)} declarations audited · {len(controls)} altered inputs rejected · 352 coefficients independently reconstructed.",
            'scope':receipt['scope'],'replay_scope':receipt['replay_scope']}


def evidence():
    sources={}
    def bind(name):
        path=(ROOT/name).resolve()
        assert path.is_relative_to(ROOT)
        sources[name]=sha(path)
        return path
    physical=physical_evidence(bind)
    formal=formal_evidence(bind,physical)
    return {'schema':'cyclic-fano-polynomial-bridge-figure-v1','status':'PASS',
            'source_sha256':sources,'physical':physical,'formal':formal}


def box(fig,x,y,w,h,color='#EEF2EC'):
    fig.add_artist(FancyBboxPatch((x,y),w,h,transform=fig.transFigure,
                   boxstyle='round,pad=.008,rounding_size=.008',
                   facecolor=color,edgecolor='#D2DBD3',linewidth=1))


def arrow(fig,start,end):
    fig.add_artist(FancyArrowPatch(start,end,transform=fig.transFigure,
                   arrowstyle='-|>',mutation_scale=17,linewidth=1.4,color=TEAL))


def fraction(value):
    value=Q(value)
    if value.denominator==1:return str(value.numerator)
    sign='-' if value<0 else ''
    return sign+r'\frac{'+str(abs(value.numerator))+'}{'+str(value.denominator)+'}'


def draw(data):
    fig=plt.figure(figsize=(17,13),facecolor=PAPER)
    fig.text(.05,.950,'From polynomials to a two-row contradiction',fontsize=28,weight='bold')
    fig.text(.05,.913,'cyclic-triple-fano · discussion #112  |  Existing Case05 obstruction  |  Degree 8 fixed denominator',
             fontsize=13.5,color=MUTED)

    box(fig,.05,.714,.9,.158)
    fig.text(.065,.845,'1  Exact five-variable polynomial model',fontsize=15,weight='bold',color=TEAL)
    fig.text(.065,.810,r'$Q=\frac{5}{7}(X_0^3+X_1Y_0Y_1+X_0Y_1Y_2),\qquad \Delta=Q^2-4H,\qquad \beta=\frac{1}{3}X_0Y_0^3$',
             fontsize=17)
    fig.text(.065,.774,r'$H=X_0^6+X_1^6+Y_0^6+Y_1^6+Y_2^6+\frac{5}{7}(X_0^3X_1Y_0Y_1+X_0^2Y_0Y_1Y_2^2+X_0X_1Y_1^3Y_2)$',
             fontsize=16)
    fig.text(.065,.738,r'$v=X_0^3\partial_{X_0}+Y_2^3\partial_{X_1},\qquad E=v(\Delta)$',fontsize=18,color=PURPLE)
    arrow(fig,(.50,.703),(.50,.681))

    box(fig,.05,.519,.435,.146)
    box(fig,.515,.519,.435,.146)
    fig.text(.065,.637,'2  Correction operator',fontsize=15,weight='bold',color=TEAL)
    fig.text(.065,.603,r'$C_{119}=Y_2^2(\Delta_{Y_1}E_{Y_0}-\Delta_{Y_0}E_{Y_1})$',fontsize=16)
    fig.text(.065,.569,'Column 119: pair (Y₀, Y₁), multiplier Y₂².',fontsize=12,color=MUTED)
    fig.text(.065,.541,'All 175 columns enter the coefficient check.',fontsize=12,color=MUTED)
    fig.text(.530,.637,'3  Target polynomial',fontsize=15,weight='bold',color=TEAL)
    fig.text(.530,.603,r'$b=4[(v(\beta)+\beta\,\mathrm{div}(v))E-\beta\,v(E)]$',fontsize=16)
    fig.text(.530,.569,'This is −B_E(P₀), before selecting coefficients.',fontsize=12,color=MUTED)
    fig.text(.530,.541,'Exact arithmetic over ℚ; no sampled evaluation.',fontsize=12,color=MUTED)
    arrow(fig,(.267,.507),(.267,.480));arrow(fig,(.733,.507),(.733,.480))

    fig.text(.05,.463,'4  Extract the two coefficients, then apply the recorded row scales',fontsize=15,weight='bold')
    ax=fig.add_axes([.05,.304,.9,.136]);ax.axis('off')
    rows=data['physical']['rows']
    labels=[r'$X_1Y_0^7Y_1Y_2^5$',r'$X_0Y_0^5Y_1^2Y_2^6$']
    table_data=[]
    for label,row in zip(labels,rows):
        table_data.append([label,'$'+fraction(row['column119'])+'$',
                           '$'+fraction(row['target'])+'$','$'+fraction(row['scale'])+'$',
                           '$('+str(row['scaled_column119'])+','+str(row['scaled_target'])+')$'])
    table=ax.table(cellText=table_data,colLabels=['Coefficient of','C₁₁₉','b','Row scale','Scaled (M₁₁₉, b)'],
                   cellLoc='center',colWidths=[.27,.17,.17,.17,.22],bbox=[0,0,1,1])
    table.auto_set_font_size(False);table.set_fontsize(14)
    for (row,column),cell in table.get_celld().items():
        cell.set_edgecolor('#D2DBD3');cell.set_facecolor('#EEF2EC' if row==0 else '#FFFFFF')
        if row==0:cell.set_text_props(weight='bold',color=INK,fontsize=12)
    fig.text(.05,.282,'Every other correction column has zero coefficient in both selected rows.',fontsize=12,color=MUTED)

    box(fig,.05,.170,.9,.084,'#EEEBF4')
    fig.text(.065,.226,r'$\lambda=(756,1):\qquad\lambda^TM=756\cdot1+1\cdot(-756)=0,\qquad\lambda^Tb=-5\ne0.$',
             fontsize=19,color=PURPLE)
    fig.text(.065,.190,r'No scalar coefficients $c\in K^{175}$ solve $\sum_j c_j C_j=b$ in characteristic zero.',
             fontsize=13.5,weight='bold')

    # Formal status is added from a source-bound receipt before final rendering.
    fig.text(.05,.130,data['formal']['caption'],fontsize=12.5,weight='bold',color=TEAL)
    fig.text(.05,.105,data['formal'].get('evidence_caption','Exact Python check: 350 correction coefficients + 2 target coefficients.'),
             fontsize=11.5,color=MUTED)
    fig.text(.05,.074,'Outside Lean: source-to-model identification and completeness/projection of normalized certificate numerators.',
             fontsize=12,color=MUTED)
    fig.text(.05,.042,'No new candidate excluded; no HasCertificate or instance solution. The full 175-parameter mixed family remains open.',
             fontsize=12,color=CORAL)
    OUT.mkdir(parents=True,exist_ok=True)
    fig.savefig(OUT/'polynomial-bridge.png',dpi=160,facecolor=PAPER)
    svg=OUT/'polynomial-bridge.svg'
    fig.savefig(svg,metadata={'Date':None},facecolor=PAPER)
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',
                   encoding='utf-8',newline='\n')
    plt.close(fig)


def main():
    assert __debug__, 'Run without -O so exact evidence checks remain enabled.'
    plt.rcParams.update({'font.family':'DejaVu Sans','text.color':INK,
                         'svg.fonttype':'none','svg.hashsalt':'cyclic-fano-polynomial-bridge-v1'})
    data=evidence();draw(data)
    data['renderer_lf_sha256']=sha(Path(__file__))
    (OUT/'plot-data.json').write_text(json.dumps(data,separators=(',',':'))+'\n',
                                     encoding='utf-8',newline='\n')
    assert all(sha(ROOT/name)==digest for name,digest in data['source_sha256'].items())
    print(json.dumps({'status':'PASS','source_bindings':len(data['source_sha256']),
                      'physical_coefficients':data['physical']['physical_coefficients_checked'],
                      'Lean_declarations':data['formal']['declarations'],
                      'Lean_replays':data['formal']['modules'],
                      'plot_data_bytes':(OUT/'plot-data.json').stat().st_size}))


if __name__=='__main__':
    main()
