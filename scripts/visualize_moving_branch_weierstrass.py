"""Plot actual finite-field matrices from the independent audit receipt."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm

root=Path(__file__).resolve().parents[1]
receipt=json.loads((root/'results/moving-branch-weierstrass-audit/replay.json').read_text(encoding='utf-8'))
if receipt['status']!='PASS':
    raise ValueError('A passing audit is required')
plt.rcParams.update({'font.family':'DejaVu Sans','svg.hashsalt':'moving-branch-audit-v1','font.size':11})
fig=plt.figure(figsize=(15,9),facecolor='#fafaf7')
grid=fig.add_gridspec(1,2,left=.07,right=.94,bottom=.25,top=.79,width_ratios=[13,5],wspace=.45)
colors=['#eef1ef','#9bc4c1','#509997','#b99b69','#355563']
cmap=ListedColormap(colors);norm=BoundaryNorm([-.5,.5,1.5,2.5,3.5,4.5],5)

def panel(ax,values,xlabels,ylabels,title):
    im=ax.imshow(values,cmap=cmap,norm=norm,aspect='equal')
    ax.set_xticks(range(len(xlabels)),xlabels,rotation=45,ha='right')
    ax.set_yticks(range(len(ylabels)),ylabels)
    ax.set_title(title,pad=15,fontweight='bold',color='#183b43')
    for i,row in enumerate(values):
        for j,value in enumerate(row):
            ax.text(j,i,str(value),ha='center',va='center',fontsize=8,color='white' if value in [2,4] else '#183b43')
    ax.spines[:].set_visible(False)
    return im

left=fig.add_subplot(grid[0,0]);right=fig.add_subplot(grid[0,1])
panel(left,receipt['matrix_mod5'],receipt['coefficient_order'],receipt['equation_order'],
      'Coefficient incidence J over F₅ · rank 13')
panel(right,receipt['tangent_lift_mod5'],receipt['external_parameter_order'],receipt['coefficient_order'],
      'Four parameter lifts L')
fig.text(.06,.94,'Moving branch: independent Weierstrass audit',fontsize=24,fontweight='bold',color='#183b43')
fig.text(.06,.895,'169 reconstructed entries match · det(J) = 1 for 111132V, and 3 for V · J L + B = 0',fontsize=14,color='#3f626b')
fig.text(.06,.85,'Residues 0–4 are field elements, not real-valued magnitudes. Fixed endpoint coordinates: R₀ and X₀.',fontsize=11,color='#53676c')
fig.text(.06,.17,'Geometric normalization (exact over ℚ)',fontsize=14,fontweight='bold',color='#183b43')
fig.text(.06,.12,r'$H=\frac{3}{8}\det\operatorname{Hess}(U),\quad \Theta=\Theta_{\rm raw}-9s_4UH,\quad J_{\rm cov}=\frac{1}{9}\det\operatorname{Jac}(U,H,\Theta)$',fontsize=19,color='#183b43')
fig.text(.06,.073,'The ambient correction vanishes on U = 0. The covariant J and incidence matrix J are different objects.',fontsize=11,color='#53676c')
fig.text(.06,.035,'Pinned source: '+receipt['upstream_commit'][:12]+' · Exact bounded checks; no full Lean or certificate replay.',fontsize=11,color='#53676c')
out=root/'visualizations';out.mkdir(exist_ok=True)
fig.savefig(out/'moving-branch-weierstrass-audit.svg',metadata={'Date':None})
svg=out/'moving-branch-weierstrass-audit.svg'
svg.write_bytes(('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n').encode('utf-8'))
fig.savefig(out/'moving-branch-weierstrass-audit.png',dpi=140)
plt.close(fig)
print('Saved SVG and PNG; matplotlib',matplotlib.__version__)
