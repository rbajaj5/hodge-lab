"""Map the verified degree-seven single-character exclusions."""
from pathlib import Path
import gzip, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'results/degree7-characters'


def main():
    with gzip.open(OUT/'certificates.json.gz','rt') as f:packet=json.load(f)
    plt.style.use('dark_background')
    fig,axes=plt.subplots(2,3,figsize=(12,8))
    fig.patch.set_facecolor('#111820')
    colors={'affine':'#2b70a0','cubic':'#d6b65a','empty':'#202b35'}
    families={tuple(f['character']):f for f in packet['families']}
    for first,ax in enumerate(axes.flat):
        ax.set_facecolor('#111820')
        for second in range(6):
            for third in range(6):
                family=families.get((first,second,third))
                kind='empty' if family is None else 'cubic' if any(p.get('ideal_contradiction') for p in family['charts']) else 'affine'
                ax.add_patch(Rectangle((third-.45,second-.45),.9,.9,color=colors[kind]))
                if family:
                    assert not family['unresolved_pivots']
                    ax.text(third,second,str(len(family['denominator_basis_indices'])),ha='center',va='center',
                            fontsize=13,color='#101820' if kind=='cubic' else 'white')
        ax.set(xlim=(-.6,5.6),ylim=(5.6,-.6),xticks=range(6),yticks=range(6),aspect='equal',title=f'First character coordinate = {first}')
        if first>=3:ax.set_xlabel('Third coordinate (mod 6)')
        if first%3==0:ax.set_ylabel('Second coordinate (mod 6)')
        for spine in ax.spines.values():spine.set_visible(False)
    fig.suptitle('Degree seven: 138 symmetry families excluded exactly',fontsize=19,y=.975)
    fig.text(.5,.922,'Numbers count denominator coordinates in each family; all 289 nonzero-coordinate charts are excluded.',ha='center',fontsize=11,color='#c5d5e3')
    fig.legend(handles=[Patch(color=colors['affine'],label='Affine / square-zero proof'),
                        Patch(color=colors['cubic'],label='Cubic identity also needed'),
                        Patch(color=colors['empty'],label='No denominator class')],loc='lower center',bbox_to_anchor=(.5,.045),ncol=3,frameon=False,fontsize=11)
    fig.text(.5,.015,'Mixed-character denominators remain open. This is a restriction on a possible solution, not a solution of the holdout.',ha='center',fontsize=10,color='#c5d5e3')
    fig.subplots_adjust(left=.06,right=.97,bottom=.16,top=.86,hspace=.37,wspace=.30)
    fig.savefig(OUT/'character-map.png',dpi=160,facecolor=fig.get_facecolor());plt.close(fig)


if __name__=='__main__':main()
