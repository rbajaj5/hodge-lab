"""Plot the actual six-cycle ansatz and recorded exact-check counts."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT=Path(__file__).resolve().parents[1]/'results/dubedat-cycle'
report=json.loads((OUT/'report.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','text.color':'#edf2f7',
    'axes.labelcolor':'#edf2f7','xtick.color':'#c1c9d2','ytick.color':'#c1c9d2',
    'font.size':11})
fig=plt.figure(figsize=(14,6.5),facecolor='#101820')
fig.text(.045,.935,'A six-cycle becomes a denominator',fontsize=23,weight='bold')
fig.text(.045,.878,'Dubedat-inspired matrix ansatz  /  fixed holdout target  /  exact rational checks',color='#b1bdc8')
ax=fig.add_axes([.045,.19,.39,.61]);ax.set_aspect('equal');ax.axis('off')
angles=np.arange(6)*np.pi/3+np.pi/6
points=np.c_[np.cos(angles),np.sin(angles)]
labels=[r'$F_i$',r'$L_3$',r'$L_4$',r'$L_2$',r'$L_1$',r'$tF_j$']
for k in range(6):
    a,b=points[k],points[(k+1)%6]
    ax.plot([a[0],b[0]],[a[1],b[1]],color='#55d6be' if k%2==0 else '#d9a4ef',lw=3)
    midpoint=(a+b)/2*1.22
    ax.text(*midpoint,labels[k],ha='center',va='center',fontsize=15)
for k,point in enumerate(points):
    ax.scatter(*point,s=210,color='#edf2f7' if k%2 else '#101820',edgecolors='#edf2f7',linewidths=2,zorder=3)
ax.set_xlim(-1.6,1.6);ax.set_ylim(-1.55,1.45)
ax.text(0,-1.36,r'$D=F_iL_1L_4+tF_jL_2L_3$',ha='center',fontsize=17)
ax.text(0,-1.63,'Two perfect matchings. One relative cycle weight.',ha='center',fontsize=10,color='#b1bdc8')
right=fig.add_axes([.51,.29,.43,.43],facecolor='#101820')
y=np.arange(3);total=np.array([g['cases'] for g in report['groups']])
passed=np.array([g['cases']-g['rejected'] for g in report['groups']])
right.barh(y+.13,total,height=.22,color='#55d6be',label='First equation satisfied')
right.barh(y-.13,passed,height=.22,color='#d9a4ef',label='Full E2 test passed')
for k,(a,b) in enumerate(zip(total,passed)):
    right.text(a+.25,k+.13,str(a),va='center',fontsize=11)
    right.text(.25,k-.13,str(b),va='center',fontsize=11,color='#d9a4ef')
right.set_yticks(y,['Monomial edges','Mixed edges, t = 1','Mixed edges, t = -1'])
right.set_xlim(0,17);right.set_xticks([0,5,10,15]);right.set_xlabel('Number of candidate denominators')
right.invert_yaxis();right.spines[['top','right','left']].set_visible(False)
right.spines['bottom'].set_color('#50606d');right.tick_params(axis='y',length=0,pad=12)
right.legend(loc='lower left',bbox_to_anchor=(-.01,1.05),frameon=False,fontsize=10)
fig.text(.51,.16,'45 distinct directions checked; all rejected exactly.',fontsize=13,weight='bold')
fig.text(.51,.105,'30 directions use 7 or 8 characters. Every test allows\nall 840 numerator corrections. The full problem remains open.',fontsize=10,color='#b1bdc8')
fig.savefig(OUT/'cycle-search.png',dpi=170,facecolor=fig.get_facecolor())
fig.savefig(OUT/'cycle-search.svg',facecolor=fig.get_facecolor())
