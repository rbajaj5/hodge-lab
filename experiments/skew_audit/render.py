"""Draw audited coefficient maps, not an inference from visual similarity."""
from pathlib import Path
from fractions import Fraction
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results/one-reflection-skew-audit-20261021'


def monos(d,n):
    if n==1:return [(d,)]
    return [(i,)+r for i in range(d+1) for r in monos(d-i,n-1)]


def main():
    line=json.loads((OUT/'line-audit.json').read_text())
    diagonal=json.loads((OUT/'diagonal-review.json').read_text())['diagonal']
    low=json.loads((OUT/'low-and-odd.json').read_text())
    fig,axs=plt.subplots(2,2,figsize=(16,12),gridspec_kw={'height_ratios':[1,1.1]})
    fig.patch.set_facecolor('#fafaf5')
    plt.subplots_adjust(top=.86,bottom=.09,left=.07,right=.95,hspace=.48,wspace=.3)
    fig.suptitle('One reflection · skew coupling | what the maps establish',
                 fontsize=24,x=.07,ha='left',y=.97,color='#17323b',weight='bold')
    fig.text(.07,.925,'Independent audit • protected target 78632dda • exact arithmetic • 21 October 2026',
             fontsize=12,color='#53666d')
    for ax,key,title,detail in [
        (axs[0,0],'ordinary_incidence','Ordinary line incidence: rank 7 of 7',
         '8 Grassmann-chart parameters → 7 sextic coefficients\nFirst-seven-column minor: 6 for F; 3 for 7F (mod 11).'),
        (axs[0,1],'fixed_endpoint','Fixed endpoint: rank 4, with two forced gauges',
         '6 slope parameters → 6 nonconstant coefficients\nKernel = span(a,b); no nontrivial tangent after quotient.')]:
        matrix=np.array(line[key]['matrix'])
        ax.imshow(matrix,cmap='viridis',vmin=0,vmax=10,aspect='auto')
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                ax.text(j,i,str(matrix[i,j]),ha='center',va='center',fontsize=12,
                        color='white' if matrix[i,j]<6 else '#142a30')
        ax.set_xticks(range(matrix.shape[1]),range(matrix.shape[1]))
        ax.set_yticks(range(matrix.shape[0]),range(matrix.shape[0]))
        ax.set_title(title,fontsize=14,loc='left',pad=43,color='#17323b',weight='bold')
        ax.text(0,1.035,detail,transform=ax.transAxes,fontsize=10,color='#53666d')
        ax.set_xlabel('Column index; displayed entries in F₁₁')
        ax.set_ylabel('Coefficient row')
    ax=axs[1,0]
    rows=monos(3,5);idx={m:i for i,m in enumerate(rows)}
    matrix=np.zeros((35,45))
    for qi,q in enumerate(diagonal['necessary_quadrics']):
        for vi,unit in enumerate(monos(1,5)):
            for mon,c in q:
                matrix[idx[tuple(a+b for a,b in zip(mon,unit))],5*qi+vi]=float(Fraction(c))
    display=np.sign(matrix)*np.log1p(abs(matrix))
    lim=float(abs(display).max())
    ax.imshow(display,cmap='PuOr',norm=TwoSlopeNorm(vmin=-lim,vcenter=0,vmax=lim),aspect='auto')
    ax.set_title('Nine quadrics × five variables: 35 × 45 map',fontsize=14,
                 loc='left',color='#17323b',weight='bold',pad=38)
    ax.text(0,1.035,'Rank 35 over Q. Selected 35-column minor = 15 mod 101.\nColors: sign × log(1 + absolute coefficient).',
            transform=ax.transAxes,fontsize=10,color='#53666d')
    ax.set_xlabel('45 product columns; nine blocks of five')
    ax.set_ylabel('35 degree-three monomials')
    for j in range(5,45,5):ax.axvline(j-.5,color='#ffffff',lw=.7)
    ax=axs[1,1];ax.axis('off')
    cards=[
        ('CORRECTED',f"Degree-five Hessian rank {low['degree5']['quotient_quadratic_rank']}, not 16.\nSix square witnesses still exclude the family.",'#946a17'),
        ('REPLAYED','All denominators through degree 6 excluded.\nFour pure odd degree-7 characters excluded.','#166a70'),
        ('MIXTURES DIFFER','A mixed cross-term survives modulo J + F.\nPure-character exclusions cannot be added.','#7059a1'),
        ('IDENTITIES ≠ PRIMITIVE','Companion pullback/trace formulas pass.\nThe rational primitive remains to be constructed.','#7059a1'),
    ]
    for i,(label,body,color) in enumerate(cards):
        y=.96-i*.245
        ax.text(0,y,label,fontsize=11,weight='bold',color=color,va='top')
        ax.text(0,y-.065,body,fontsize=11.5,color='#17323b',va='top',linespacing=1.45)
    fig.text(.07,.035,'A local line, a bounded exclusion, and a transport identity are different results. No certificate or Lean acceptance is claimed.',
             fontsize=12,color='#17323b')
    fig.savefig(OUT/'audit-map.png',dpi=125,facecolor=fig.get_facecolor())
    fig.savefig(OUT/'audit-map.svg',facecolor=fig.get_facecolor(),metadata={'Date':None})
    svg=OUT/'audit-map.svg'
    svg.write_text('\n'.join(x.rstrip() for x in svg.read_text(encoding="utf-8").splitlines())+'\n',encoding='utf-8',newline='\n')
    plt.close(fig)
    print('PASS: visualization drawn from line, degree-five and degree-six audit receipts')


if __name__=='__main__':main()
