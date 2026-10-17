"""Plot the bounded optimization batch and summarize its recorded limitations."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import argparse,gzip,hashlib,json,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'algebra'))
import degree7_e1 as e1
from degree6_e2_model import modF
import degree6_e1 as base
OUT=ROOT/'results/koszul-parameter-optimization'


def summary():
    report=json.loads((OUT/'report.json').read_text(encoding='utf-8'))
    validation=json.loads((OUT/'numerical-validation.json').read_text(encoding='utf-8'))
    assert report['complete'] and validation['status']=='PASS'
    with gzip.open(OUT/'certificates.json.gz','rt',encoding='utf-8') as f:packet=json.load(f)
    _,pairs=e1.load();directions=set();chars={}
    for c in packet['cases']:
        coords=[(i,Q(v)) for i,v in c['coordinates'] if Q(v)]
        directions.add(tuple((i,str(v/coords[0][1])) for i,v in coords))
        D={}
        for i,v in coords:D=base.padd(D,pairs[i][0],v)
        chars[c['family'],c['method']]=len({e1.character(m) for m in modF(D)})
    rows=report['families'];ratios=[r['finalists']['optimized']['float_recheck']['score']/r['finalists']['random']['float_recheck']['score'] for r in rows]
    data={'families':len(rows),'optimizer_evaluations':sum(len(r['optimizer_evaluations']) for r in rows),
          'random_evaluations':sum(len(r['random_evaluations']) for r in rows),
          'optimized_beats_random':sum(v<1 for v in ratios),'median_score_reduction':float(1-np.median(ratios)),
          'relative_reduction_range':[float(1-max(ratios)),float(1-min(ratios))],
          'exact_cases':len(packet['cases']),'distinct_projective_directions':len(directions),
          'exact_rejected':sum(c['status']=='rejected' for c in packet['cases']),
          'optimizer_stopping_reasons':dict(Counter(run['message'] for r in rows for run in r['optimizer_runs'])),
          'rounded_optimized_character_counts':dict(Counter(str(chars[r['family'],'optimized']) for r in rows)),
          'optimized_winners_at_box_boundary':sum(any(abs(x)>=3.999999 for x in r['finalists']['optimized']['float_recheck']['x']) for r in rows),
          'gradient_checks':sum(len(r['gradient_checks']) for r in rows),
          'max_gradient_scaled_error':max(c['scaled_error'] for r in rows for c in r['gradient_checks']),
          'max_inner_normal_residual':max(c['normal_residual'] for r in rows for key in ['optimizer_evaluations','random_evaluations'] for c in r[key]),
          'independent_rounded_score_rechecks':len(validation['numerical_rechecks']),
          'max_independent_score_relative_difference':max(c['relative_score_difference'] for c in validation['numerical_rechecks']),
          'float_minimum_score':min(r['finalists']['optimized']['float_recheck']['score'] for r in rows),
          'source_sha256':{name:hashlib.sha256((OUT/name).read_bytes().replace(b'\r\n',b'\n') if name.endswith('.json') else (OUT/name).read_bytes()).hexdigest()
                           for name in ['report.json','certificates.json.gz','validation.json','independent-validation.json','numerical-validation.json']},
          'limits':'One fixed seed; bounded real charts; central optimizer starts versus full-box uniform random draws; equal evaluation counts, not a time comparison. Exact rejections apply to rounded fixed directions only.'}
    return report,chars,data


def render(report,chars,data):
    bg,fg,muted='#151a24','#f1f4f8','#abb8cc';teal,gold='#61d4be','#f4d67b'
    plt.rcParams.update({'font.family':'DejaVu Sans','text.color':fg,'axes.labelcolor':fg,
        'xtick.color':muted,'ytick.color':muted,'figure.facecolor':bg,'axes.facecolor':bg,
        'savefig.facecolor':bg,'svg.fonttype':'none','svg.hashsalt':'koszul-parameter-optimization'})
    fig=plt.figure(figsize=(14,9));rows=report['families']
    fig.text(.06,.94,'Optimizing the Koszul correction residual',fontsize=23,weight='bold')
    fig.text(.06,.89,f"{data['families']} unresolved triple spans · {data['optimizer_evaluations']:,} evaluations per method · fixed coefficient metric",fontsize=12,color=muted)
    ax=fig.add_axes([.09,.23,.40,.58]);yy=np.arange(len(rows))
    opt=[r['finalists']['optimized']['float_recheck']['score'] for r in rows]
    rand=[r['finalists']['random']['float_recheck']['score'] for r in rows]
    for y,a,b in zip(yy,opt,rand):ax.plot([a,b],[y,y],color=muted,lw=1,alpha=.55)
    ax.scatter(opt,yy,c=teal,s=45,label='L-BFGS-B: best seen',zorder=3)
    ax.scatter(rand,yy,c=gold,s=35,marker='x',label='Uniform random: best seen',zorder=3)
    ax.set_xscale('log');ax.set_yticks(yy,[str(r['family']) for r in rows]);ax.invert_yaxis()
    ax.set_xlim(.0018,.11);ax.set_xticks([.002,.005,.01,.02,.05,.1],['0.002','0.005','0.01','0.02','0.05','0.1']);ax.minorticks_off()
    ax.set_ylabel('Family number');ax.set_xlabel('Normalized squared residual (lower is better)',labelpad=12)
    ax.legend(loc='lower left',bbox_to_anchor=(-.03,1.015),ncol=2,fontsize=9,facecolor=bg,labelcolor=fg,edgecolor='none')
    ax2=fig.add_axes([.60,.43,.34,.34])
    for r in rows:
        values=np.minimum.accumulate([v['score'] for v in r['optimizer_evaluations']])
        ax2.semilogy(np.arange(1,len(values)+1),values/values[0],color=teal,alpha=.35,lw=1.3)
    ax2.set_title(f"Optimization histories: all {data['families']} families",loc='left',fontsize=12,pad=14)
    ax2.set_xlabel('Objective evaluations across both starts',labelpad=12)
    ax2.set_ylabel('Best score / first score')
    for a in [ax,ax2]:
        for spine in a.spines.values():spine.set_visible(False)
        a.tick_params(length=0)
    fig.text(.60,.32,f"{100*data['median_score_reduction']:.1f}% median lower score",fontsize=21,color=teal,weight='bold')
    fig.text(.60,.245,'Compared with equal-evaluation random search\nin these bounded charts and this recorded seed.',fontsize=11,color=muted,linespacing=1.7)
    reduced=sum(v for k,v in data['rounded_optimized_character_counts'].items() if int(k)<3)
    fig.text(.06,.13,f"Exact checks reject all {data['exact_cases']} shortlisted rational directions.",fontsize=15,color=gold)
    fig.text(.06,.085,f"{reduced}/16 rounded optimized candidates use fewer than three characters; {data['optimized_winners_at_box_boundary']}/16 float winners touch the parameter box boundary.",fontsize=11,color=muted)
    fig.text(.06,.045,'13 starts met relative-score tolerance; 19 hit evaluation/iteration limits. No global optimum or new family exclusion.',fontsize=11,color=muted)
    fig.text(.06,.015,'Optimizer starts sampled in [−1.5, 1.5]; random comparator sampled in [−4, 4], the full search box.',fontsize=10,color=muted)
    fig.savefig(OUT/'optimization-search.png',dpi=170)
    svg=OUT/'optimization-search.svg';fig.savefig(svg,metadata={'Date':None});plt.close(fig)
    svg.write_text('\n'.join(v.rstrip() for v in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8',newline='\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    report,chars,data=summary();path=OUT/'summary.json'
    if args.check:assert json.loads(path.read_text(encoding='utf-8'))==data
    else:
        render(report,chars,data);path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in data.items() if k not in ['source_sha256','limits']},indent=2))


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    main()
