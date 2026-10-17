"""Draw the checked proof dependency chain and actual cancellation support."""
from pathlib import Path
import gzip, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/degree7-syzygy-rebuild'
with gzip.open(OUT / 'chart-115-10.json.gz', 'rt') as f:
    packet = json.load(f)
relations = packet['baseline'] + [packet['relations'][j] for j in packet['selected_new']]
assert len(packet['baseline']) == 9 and len(relations) == 22
support = np.zeros((22, packet['system']['equation_count']), dtype=int)
for i, relation in enumerate(relations):
    for j, mon, coefficient in relation['products']:
        support[i, j] += 1
assert len(packet['system']['Koszul_indices']) == 58
counts = [len(claim['products']) for stage in packet['continuation']['power_stages'] for claim in stage['claims']]
assert counts == [419, 430, 56]
bg, fg, muted = '#151a24', '#f1f4f8', '#abb8cc'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'text.color':fg,
    'axes.labelcolor':fg,'xtick.color':muted,'ytick.color':muted,'axes.edgecolor':muted,
    'figure.facecolor':bg,'axes.facecolor':bg,'savefig.facecolor':bg})
fig = plt.figure(figsize=(14, 8.5))
fig.text(.055,.945,'Syzygies turn cancellation into a proof',fontsize=23,weight='bold')
fig.text(.055,.9,'Holdout · family 115 · exact rational identities · fixed F, q = 1, A',color=muted,fontsize=12)
ax = fig.add_axes([.055,.13,.41,.7]);ax.set_xlim(0,1);ax.set_ylim(0,1);ax.axis('off')
labels = [
 ('Verified inherited zeros',r'$a_2=a_9=0$'),
 ('Rebuild the physical equations',r'$E(a,z)=R(a)z+b(a)$ · 58 corrections'),
 ('Cancel every numerator coordinate','22 relations: 9 constant + 13 affine syzygies'),
 ('Prove three powers vanish',r'$a_4^2=a_5^2=a_1^4=0$ · 905 multiplier terms'),
 (r'Chart $a_{10}=1$ is impossible',r'Therefore $a_{10}=0$ throughout this family'),
 (r'The remaining chart $a_0=1$ closes','Family 115 excluded; families 16 and 137 remain')]
ys=np.linspace(.91,.07,6)
for i, ((title, detail), y) in enumerate(zip(labels,ys)):
    ax.text(.02,y,title,weight='bold',fontsize=12,va='center')
    ax.text(.02,y-.046,detail,fontsize=10.4,color=muted,va='center')
    if i<5:
        ax.annotate('',xy=(.035,ys[i+1]+.04),xytext=(.035,y-.076),
                    arrowprops={'arrowstyle':'-|>','color':'#61d4be','lw':1.7})
heat = fig.add_axes([.57,.44,.37,.38])
cmap=ListedColormap([bg,'#285c70','#3c9ba3','#68d0bb','#dce28a'])
plot=heat.imshow(np.minimum(support,4),aspect='auto',interpolation='nearest',
                 cmap=cmap,norm=BoundaryNorm([-.5,.5,1.5,2.5,3.5,4.5],5))
heat.axhline(8.5,color=fg,lw=.8)
heat.set_yticks([0,8,9,21],['constant 1','constant 9','affine 1','affine 13'])
heat.set_xticks([0,50,100,150,200,254])
heat.set_xlabel('Original physical equation index (zero based)',labelpad=10)
heat.set_title('Where the cancellation identities draw their terms',fontsize=12,pad=15,loc='left')
for spine in heat.spines.values():spine.set_visible(False)
cbax=fig.add_axes([.57,.35,.37,.018]);cb=fig.colorbar(plot,cax=cbax,orientation='horizontal',ticks=range(5))
cb.ax.set_xticklabels(['0','1','2','3','4+']);cb.set_label('Multiplier monomials per equation; not coefficient magnitude',fontsize=9)
fig.text(.57,.26,r'$u(a)^T R(a)=0\quad\Longrightarrow\quad P(a)=u(a)^T b(a)=0$',fontsize=15)
fig.text(.57,.205,'A row combines many equations to cancel the same shared z.\nThe remaining polynomial constrains the denominator a.',color=muted,fontsize=11,linespacing=1.7)
fig.text(.055,.045,'Coverage: 134/136 fixed-pair extensions. This is a restricted nonexistence result, not a holdout solution.',fontsize=11,color=muted)
fig.savefig(OUT/'syzygy-proof-map.png',dpi=170)
fig.savefig(OUT/'syzygy-proof-map.svg')
plt.close(fig)
print('Saved proof map and cancellation-support heatmap.')
