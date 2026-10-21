"""Reproduce the verified coefficient map and its formalization boundary."""
from pathlib import Path
import hashlib, json, re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams['svg.hashsalt']='hodge-lab-skew-lean'

ROOT=Path(__file__).resolve().parents[1]
receipt=json.loads((ROOT/'formal/results/skew-lean/validation.json').read_text(encoding='utf-8'))
if receipt['status']!='PASS': raise RuntimeError('No passing Lean receipt')
name='HodgeLab/OneReflectionSkew/ThreeCoefficient.lean'
path=ROOT/'formal'/name
raw=path.read_bytes().replace(b'\r\n',b'\n')
if hashlib.sha256(raw).hexdigest()!=receipt['source_lf_sha256'][name]:
    raise RuntimeError('Lean source differs from the checked source')
src=raw.decode('utf-8')
vectors=re.findall(r'then !\[([-0-9,]+)\] r',src)
if len(vectors)!=2: raise RuntimeError('Expected two active matrix columns')
active=np.array([[int(x) for x in v.split(',')] for v in vectors]).T
matrix=np.column_stack((active,np.zeros(3,dtype=int)))
dual=np.array(receipt['integer_dual'])
target=np.array([0,35,0])
if np.any(dual@matrix) or int(dual@target)!=receipt['target_pairing']:
    raise RuntimeError('Displayed coefficient identity failed')
fig,(left,right)=plt.subplots(1,2,figsize=(14,6.5),gridspec_kw={'width_ratios':[1.05,1.1]})
fig.patch.set_facecolor('#faf9f4')
fig.suptitle('One-reflection-skew: an existing obstruction, now checked in Lean',fontsize=17,x=.5,y=.98)
left.imshow(matrix,cmap='BrBG',vmin=-1260,vmax=1260,aspect='auto')
left.set_xticks(range(3),['constant $N_U$','$t^2 N_U$','278 other columns'])
left.set_yticks(range(3),['$[rt^3]$','$[U^2w^{12}]$','$[U^2w^{12}t^2]$'])
for i in range(3):
    for j in range(3):
        left.text(j,i,str(matrix[i,j]),ha='center',va='center',fontsize=18,
                  color='white' if abs(matrix[i,j])>700 else '#17333b')
left.set_title('840 selected column coefficients + 3 source coefficients',fontsize=12,pad=18)
left.text(.5,-.20,'Dual (21, 1, −1) kills every column.\nIt pairs with source (0, 35, 0) to give 35 ≠ 0.',
          ha='center',va='top',transform=left.transAxes,fontsize=12,color='#17333b')
right.axis('off')
boxes=[(.88,'Defined in Lean','P7, a; all three differentiated operator terms'),
       (.65,'Finite space checked','70 monomials × 4 components; 625 exponent tuples'),
       (.42,'Polynomial → matrix → contradiction','Characteristic-zero scalar extension; kernel replay'),
       (.16,'Outside this theorem','Geometric source transport; arbitrary rational primitives;\n45 higher-U images versus fqlx’s 504-column space')]
for y,title,body in boxes:
    formal=y>.2
    right.text(.02,y,title+'\n'+body,ha='left',va='center',fontsize=11.5,linespacing=1.6,
               transform=right.transAxes,bbox={'boxstyle':'round,pad=.7','facecolor':'#e4f1ec' if formal else '#f4eadb',
               'edgecolor':'#14737a' if formal else '#9a743c'})
    if y>.42:
        right.annotate('',xy=(.48,y-.12),xytext=(.48,y-.075),xycoords='axes fraction',
                       arrowprops={'arrowstyle':'->','color':'#14737a'})
fig.text(.5,.025,'Bounded exclusion: D = 1 + r⁶ + w⁶, encoded numerators of total degree ≤ 4. No new solve or exclusion coverage.',
         ha='center',fontsize=11,color='#42555b')
fig.subplots_adjust(left=.13,right=.97,top=.86,bottom=.25,wspace=.3)
out=ROOT/'visualizations';out.mkdir(exist_ok=True)
for ext in ['svg','png']:
    fig.savefig(out/('skew-lean.'+ext),dpi=170,facecolor=fig.get_facecolor(),bbox_inches='tight',
                metadata={'Date':None} if ext=='svg' else None)
svg=out/'skew-lean.svg'
svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',
               encoding='utf-8',newline='\n')
print('PASS: coefficient figure verified against the Lean receipt and source')
