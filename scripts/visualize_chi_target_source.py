"""Plot the source-bound operator and its two actual coefficient samples."""
from pathlib import Path
import json
import numpy as np
import sympy as s
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]


def main():
    receipt=json.loads((ROOT/'results/chi-target-source/replay.json').read_text(encoding='utf-8'))
    if receipt['status']!='PASS': raise ValueError('Passing receipt required')
    plt.rcParams.update({'font.family':'DejaVu Sans','svg.hashsalt':'chi-target-source-v1'})
    fig=plt.figure(figsize=(15,9),facecolor='#f8f7f3')
    dark='#18343d'; muted='#48616b'; teal='#13837d'; red='#aa4356'
    fig.text(.045,.94,'Chi-curve lesson applied to the protected skew source',fontsize=23,weight='bold',color=dark)
    fig.text(.045,.892,'one-reflection-skew  •  q = 1  •  exact rational arithmetic  •  no ambient certificate exclusion',fontsize=12,color=muted)
    fig.text(.045,.822,'SOURCE TRANSPORT',fontsize=11,weight='bold',color=teal)
    fig.text(.045,.775,'U = x²     G = z⁶ + P(U)     ω = 5U² dU / (72z¹¹)',fontsize=17,color=dark)
    fig.text(.045,.726,'P(U) = aU³ + bU² + cU + d;  a,b,c,d come from the protected sextic. Smooth generic completion: genus 4.',fontsize=12,color=muted)
    fig.text(.045,.671,'Try W = B(U)/z⁵:     5P′B − 6PB′ = 5U²/12',fontsize=18,weight='bold',color=dark)
    U=s.symbols('U')
    for index,(sample,left) in enumerate(zip(receipt['samples'],[.065,.34])):
        Q=s.sympify(sample['P'],locals={'U':U})
        matrix=np.array([[float(s.expand(5*s.diff(Q,U)*U**j-(6*Q*j*U**(j-1) if j else 0)).coeff(U,i)) for j in range(5)] for i in range(7)])
        ax=fig.add_axes([left,.255,.205,.315])
        compressed=np.sign(matrix)*np.log1p(np.abs(matrix))
        ax.imshow(compressed,cmap='RdBu_r',vmin=-9,vmax=9,aspect='auto')
        ax.set_xticks(range(5),[str(j) for j in range(5)])
        ax.set_yticks(range(7),[str(j) for j in range(7)])
        ax.set_xlabel('B coefficient degree');ax.set_ylabel('Equation coefficient degree')
        test=next(x for x in sample['degree_tests'] if x['B_degree_bound']==4)
        label='(r,w,t) = (1,1,2)' if index==0 else '(r,w,t) = (0,1,2)'
        ax.set_title(label+'\nrank M / rank [M | rhs] = '+str(test['rank'])+' / '+str(test['augmented_rank']),fontsize=12,color=dark)
    ax=fig.add_axes([.64,.265,.3,.28],facecolor='#f8f7f3')
    xs=np.linspace(0,2,201)
    for sample,color,label in zip(receipt['samples'],[red,teal],['Generic sample: nonzero','Special control: zero']):
        residual=s.sympify(sample['constant_candidate_residual'],locals={'U':U})
        ys=s.lambdify(U,residual,'numpy')(xs)
        if np.ndim(ys)==0:ys=np.full_like(xs,float(ys))
        ax.plot(xs,ys,lw=2.5,color=color,label=label)
    ax.set(xlabel='U',ylabel='Cleared residual',title='Constant primitive candidate')
    ax.spines[['top','right']].set_visible(False)
    ax.legend(fontsize=10,frameon=False)
    fig.text(.045,.173,'Matrices show signed log(1 + |coefficient|), not a numerical rank test. Exact ranks and duals are in the receipt.',fontsize=11,color=muted)
    fig.text(.045,.112,'General relative result: a ≠ 0, disc(P) ≠ 0  ⇒  rational primitive exists exactly when b = c = 0.',fontsize=14,weight='bold',color=dark)
    fig.text(.045,.065,'This rules out direct integration along the generic fiber. Base-parameter derivatives can still supply an absolute primitive.',fontsize=12,color=red)
    out=ROOT/'visualizations/chi-target-source'
    fig.savefig(out.with_suffix('.png'),dpi=170)
    fig.savefig(out.with_suffix('.svg'),metadata={'Date':None})
    p=out.with_suffix('.svg')
    p.write_text('\n'.join(line.rstrip() for line in p.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8',newline='\n')
    plt.close(fig)


if __name__=='__main__': main()
