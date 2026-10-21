"""Plot the actual quartic and distinguish its measure from its geometry."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]


def main():
    receipt=json.loads((ROOT/'results/chi-curve-bridge/replay.json').read_text(encoding='utf-8'))
    if receipt['status']!='PASS': raise ValueError('Passing receipt required')
    plt.rcParams.update({'font.family':'DejaVu Sans','svg.hashsalt':'chi-curve-bridge-v1'})
    fig=plt.figure(figsize=(14,8),facecolor='#f8f7f3')
    fig.text(.055,.925,'A chi-variable curve: geometry and the form carried on it',fontsize=22,weight='bold',color='#18343d')
    fig.text(.055,.87,'Exact pilot from the corrected GOE density  •  no Hodge-target correspondence constructed',fontsize=12,color='#48616b')
    ax=fig.add_axes([.07,.32,.39,.46],facecolor='#f8f7f3')
    u=np.linspace(-1,1,801); v=np.sqrt(np.maximum(0,2*(1-u**4)))
    ax.plot(u,v,color='#a7b8b9',lw=2); ax.plot(u,-v,color='#a7b8b9',lw=2)
    pos=u[u>=0]
    ax.plot(pos,np.sqrt(2*(1-pos**4)),color='#13837d',lw=4,label='Probability arc: 0 < u < 1, v > 0')
    ax.scatter([0,1],[np.sqrt(2),0],s=55,facecolors='#f8f7f3',edgecolors='#13837d',zorder=4)
    ax.axhline(0,color='#d0d4cf',lw=1);ax.axvline(0,color='#d0d4cf',lw=1)
    ax.set(xlabel='u = s / t',ylabel='v = 2sy / t²',title='Real affine locus: v² = 2(1 − u⁴)')
    ax.set_xlim(-1.15,1.15);ax.set_ylim(-1.6,1.75)
    ax.spines[['top','right']].set_visible(False)
    ax.legend(loc='lower center',bbox_to_anchor=(.5,-.32),frameon=False,fontsize=10)
    fig.text(.52,.735,'THE CURVE',fontsize=11,weight='bold',color='#13837d')
    fig.text(.52,.66,'Four simple branch points → genus one.\nScaling t removes it from the curve; m changes the weight.',fontsize=13,linespacing=1.6,color='#18343d')
    fig.text(.52,.565,'THE ALGEBRAIC DIFFERENTIAL',fontsize=11,weight='bold',color='#13837d')
    fig.text(.52,.49,'For integer m ≥ 1, the differential has a rational primitive.\nExample m = 1:  du / u² = d(−1/u).',fontsize=13,linespacing=1.6,color='#18343d')
    fig.text(.52,.395,'THE EXPONENTIAL WEIGHT',fontsize=11,weight='bold',color='#a27422')
    fig.text(.52,.32,'Multiplying by exp[−t²(u² + u⁻²)/4] changes the equation.\nThe weighted primitive needs its derivative correction.',fontsize=13,linespacing=1.6,color='#18343d')
    fig.text(.055,.155,'Lesson for Hodge work: track the target form, Jacobian, branches and correspondence—not just the curve.',fontsize=13,weight='bold',color='#18343d')
    fig.text(.055,.105,'The drawing is only a real affine slice. Genus refers to the smooth complex projective completion.',fontsize=11,color='#48616b')
    fig.text(.055,.065,'Exact formulas, integer-m argument, failure controls and limitations: notes/chi-curve-bridge.md',fontsize=11,color='#48616b')
    out=ROOT/'visualizations/chi-curve-bridge'
    fig.savefig(out.with_suffix('.png'),dpi=170)
    fig.savefig(out.with_suffix('.svg'),metadata={'Date':None})
    p=out.with_suffix('.svg')
    p.write_text('\n'.join(x.rstrip() for x in p.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8',newline='\n')
    plt.close(fig)


if __name__=='__main__': main()
