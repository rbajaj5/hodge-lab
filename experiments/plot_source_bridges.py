"""Render the saved scientific experiment outputs, with no resimulation."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.collections import LineCollection
from matplotlib.patches import Rectangle

HERE=Path(__file__).resolve().parent
OUT=HERE.parent/'results/source-bridges'
BG='#0d1523';FG='#e8edf7';MUTED='#9aacbf';GOLD='#f5cd75';CYAN='#6bd7dc'
plt.rcParams.update({'figure.facecolor':BG,'axes.facecolor':BG,'text.color':FG,'axes.labelcolor':MUTED,
                     'xtick.color':MUTED,'ytick.color':MUTED,'axes.edgecolor':'#3e5066','font.family':'DejaVu Sans',
                     'font.size':11,'savefig.facecolor':BG})
colors=['#6bd7dc','#f5cd75','#a797e8','#f08b94','#80caa5','#7da9ee','#e2a777','#d39ad1','#e4df9b','#88bac2','#c6aff2','#e7bbc0']

def braids():
    d=np.load(OUT/'ginibre-loop.npz');z=d['path'];t=np.linspace(0,1,len(z))
    fig=plt.figure(figsize=(14,8),layout='constrained')
    gs=fig.add_gridspec(2,3,width_ratios=[1.1,1.1,1],height_ratios=[1,1])
    ax=fig.add_subplot(gs[:,:2],projection='3d')
    for j in range(z.shape[1]):
        ax.plot(z[::8,j].real,z[::8,j].imag,t[::8],color=colors[j],lw=2,alpha=.95)
        ax.scatter(z[0,j].real,z[0,j].imag,0,color=colors[j],s=22)
    ax.set(xlabel='Real eigenvalue',ylabel='Imaginary eigenvalue',zlabel='Time around the loop')
    ax.view_init(elev=19,azim=-56);ax.set_box_aspect((1,1,1.5));ax.grid(False)
    for axis in [ax.xaxis,ax.yaxis,ax.zaxis]:axis.set_pane_color((.05,.085,.14,0))
    ax.set_title('Twelve eigenvalue strands',loc='left',color=FG,pad=12)
    a=fig.add_subplot(gs[0,2]);a.plot(t,d['discriminant_turns'],color=GOLD,lw=2)
    a.axhline(-11,color=MUTED,lw=.8,ls=':');a.set(xlabel='Time',ylabel='Cumulative turns',title='Discriminant winding = −11')
    a.spines[['top','right']].set_visible(False)
    b=fig.add_subplot(gs[1,2]);b.plot(t,d['condition'],color=CYAN,lw=1.3)
    b.set(xlabel='Time',ylabel='Eigenvector condition number',title='Sensitivity near close encounters')
    b.spines[['top','right']].set_visible(False)
    fig.suptitle('A random matrix loop, seen through topology',fontsize=22,x=.04,ha='left')
    fig.text(.04,-.035,'Smooth Gaussian matrix loop with Ginibre marginals • 16,384 time steps • winding agrees across refinements\nCUDA matrix construction and winding; CPU eigensolvers. Numerical noncollision evidence, not an interval-certified braid.',color=MUTED,fontsize=10)
    fig.savefig(OUT/'ginibre-braid.png',dpi=160,bbox_inches='tight');plt.close(fig)

def fields():
    d=np.load(OUT/'fractional-field-meshes.npz');fig,axs=plt.subplots(1,3,figsize=(14,5.3),layout='constrained')
    cm=LinearSegmentedColormap.from_list('field',['#345cb5','#182a42','#e9c863'])
    allh=[d['field_'+str(h)] for h in [.15,.5,.85]];lim=max(np.max(abs(x)) for x in allh)
    for ax,H,h in zip(axs,[.15,.5,.85],allh):
        diag=d['diagonals_'+str(H)];c=d['colors_'+str(H)];n=h.shape[0]
        ax.imshow(h,cmap=cm,vmin=-lim,vmax=lim,origin='lower',extent=(-.5,n-.5,-.5,n-.5),interpolation='bilinear')
        lines=[]
        for r in range(n):
            for col in range(n-1):lines.append([(col,r),(col+1,r)])
        for r in range(n-1):
            for col in range(n):lines.append([(col,r),(col,r+1)])
        for r in range(n-1):
            for col in range(n-1):lines.append([(col,r),(col+1,r+1)] if diag[r,col] else [(col+1,r),(col,r+1)])
        ax.add_collection(LineCollection(lines,color='#e8edf7',alpha=.35,linewidth=.5))
        yy,xx=np.mgrid[:n,:n];palette=np.array([CYAN,GOLD,'#a797e8','#f08b94'])
        ax.scatter(xx.ravel(),yy.ravel(),c=palette[c[:-1]],s=15,edgecolors=BG,linewidths=.3)
        ax.set_title(f'H = {H:.2f}',loc='left',fontsize=16);ax.set(xticks=[],yticks=[])
    fig.suptitle('One noise sample, three degrees of roughness',fontsize=21,x=.04,ha='left')
    fig.text(.04,-.035,'Background: cutoff fractional Gaussian field. Edges: curvature-selected triangulation. Dots: verified four-coloring.\nEach boundary is capped by one exterior vertex (not drawn), giving a sphere with no harmonic 1-forms.',fontsize=10,color=MUTED)
    fig.savefig(OUT/'fractional-fields-and-colors.png',dpi=160,bbox_inches='tight');plt.close(fig)

def periods():
    data=json.loads((HERE.parent/'results/period-congruence/report.json').read_text());fig,axs=plt.subplots(1,2,figsize=(11.4,5),layout='constrained')
    cm=LinearSegmentedColormap.from_list('valuations',['#12213a','#3567a0','#6bc9ce','#f5d178'])
    for ax,key,title in zip(axs,['fermat_valuation','holdout_valuation'],['Fermat sextic','Holdout sextic · coupling terms included']):
        array=np.array([r[key] for r in data['cases']]).reshape(6,4)
        ax.imshow(array,vmin=0,vmax=12,cmap=cm,aspect='auto')
        ax.set_yticks(range(6),['p = '+str(p) for p in [2,3,5,7,11,13]])
        ax.set_xticks(range(4),['n=1, r=1','n=1, r=2','n=2, r=1','n=2, r=2']);ax.set_title(title,loc='left',pad=13)
        for i in range(6):
            for j in range(4):
                ax.text(j,i,str(array[i,j]),ha='center',va='center',color=BG if array[i,j]>=8 else FG,fontsize=14)
                if key=='holdout_valuation' and i>=2 and array[i,j]<3*(1+j%2):
                    ax.add_patch(Rectangle((j-.48,i-.47),.96,.94,fill=False,edgecolor='#f78888',lw=2))
    fig.suptitle('How many powers of p divide the period difference?',fontsize=20,x=.04,ha='left')
    fig.text(.04,-.045,'Each cell is the exact valuation of C(npʳ) − C(npʳ⁻¹). Red outlines fall below the cubic benchmark 3r (p ≥ 5).\n24 exact cases per sequence. The coupling terms destroy the naive cubic extension; this is not a Hodge certificate.',fontsize=10,color=MUTED)
    fig.savefig(OUT/'period-divisibility.png',dpi=160,bbox_inches='tight');plt.close(fig)

if __name__=='__main__':
    braids();fields();periods()
    print('Saved ginibre-braid.png, fractional-fields-and-colors.png, period-divisibility.png')
