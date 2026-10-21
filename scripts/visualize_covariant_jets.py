"""Visualize the actual replay's six exact divisions; no simulated data."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT=Path(__file__).resolve().parents[1]


def main():
    r=json.loads((ROOT/'results/covariant-jet-audit/replay.json').read_text(encoding='utf-8'))
    if r['status']!='PASS' or any(x['remainder']['terms'] for x in r['identities'].values()):
        raise ValueError('A passing exact receipt is required')
    plt.rcParams.update({'font.family':'DejaVu Sans','svg.hashsalt':'covariant-jets-v1'})
    fig=plt.figure(figsize=(14,9),facecolor='#f8f7f3')
    fig.text(.06,.94,'The moving map, with its actual first variations',fontsize=23,weight='bold',color='#17333c')
    fig.text(.06,.895,'holdout-moving-branch  •  exact arithmetic over Q  •  six polynomial remainders are zero',fontsize=12,color='#48616b')
    boxes=[(.06,'PINNED CUBIC + TABLES','U and all six coefficients\nH: 13 terms   Θ: 192   J: 873'),
           (.365,'EVALUATED DUAL NUMBERS','ȧ = 1,  ẋ = −x³/G\nActual Ḣ, Θ̇, J̇; quotient rules'),
           (.67,'CLEARED IDENTITIES','Build each residual N\nCheck N = U × quotient exactly')]
    for left,title,body in boxes:
        patch=FancyBboxPatch((left,.73),.27,.12,transform=fig.transFigure,
            boxstyle='round,pad=.012',linewidth=1.2,edgecolor='#398c89',facecolor='#e8f1ed')
        fig.patches.append(patch)
        fig.text(left+.012,.82,title,fontsize=10,weight='bold',color='#146b6e')
        fig.text(left+.012,.755,body,fontsize=12,linespacing=1.6,color='#17333c')
    fig.text(.337,.78,'→',fontsize=22,color='#146b6e')
    fig.text(.642,.78,'→',fontsize=22,color='#146b6e')
    ax=fig.add_axes([.25,.26,.68,.41],facecolor='#f8f7f3')
    names=['Curve syzygy','Curve first variation','Invariant differential','Differential first variation',
           'Source differential-jet form','Moving-map identity']
    records=list(r['identities'].values())
    y=list(range(6))
    bars=ax.barh(y,[v['numerator']['terms'] for v in records],height=.6,color='#318780')
    ax.invert_yaxis()
    ax.set_yticks(y,names,fontsize=11,color='#17333c')
    ax.set_xlim(0,63000)
    ax.set_xlabel('Expanded numerator monomials (a complexity measure, not independent proof obligations)',fontsize=10)
    ax.spines[['top','right','left']].set_visible(False)
    ax.tick_params(axis='y',length=0,pad=12)
    ax.grid(axis='x',alpha=.15)
    ax.set_axisbelow(True)
    for bar,rec in zip(bars,records):
        ax.text(bar.get_width()+700,bar.get_y()+bar.get_height()/2,
            f"{rec['numerator']['terms']:,}   →   0",va='center',fontsize=10,color='#17333c')
    fig.text(.06,.17,'CLOSED: the earlier transport audit’s covariant-first-variation dependency.',
             fontsize=14,weight='bold',color='#146b6e')
    fig.text(.06,.12,'Scope: affine z = 1, characteristic zero; G and H nonzero, and J nonzero for the moving quotient.',
             fontsize=11,color='#48616b')
    fig.text(.06,.08,'Not replayed: Lean kernel, physical field embeddings / nonvanishing, primitive existence, trace or clearing.',
             fontsize=11,color='#48616b')
    fig.text(.06,.035,'Source: results/covariant-jet-audit/replay.json  •  Bars encode exact expression sizes; the checker supplies the evidence.',
             fontsize=10,color='#48616b')
    out=ROOT/'visualizations/covariant-jet-audit'
    fig.savefig(out.with_suffix('.png'),dpi=170)
    fig.savefig(out.with_suffix('.svg'),metadata={'Date':None})
    svg=out.with_suffix('.svg')
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8',newline='\n')
    plt.close(fig)
    print('Saved covariant-jet-audit.png and .svg')


if __name__=='__main__':
    main()
