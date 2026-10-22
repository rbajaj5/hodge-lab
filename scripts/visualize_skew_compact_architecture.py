"""Reproduce the evidence-labelled architecture map; not a proof diagram."""
from pathlib import Path
import hashlib,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
R=Path(__file__).resolve().parents[1];O=R/'results/skew-compact-architecture'
data=json.loads((O/'architecture.json').read_text(encoding='utf-8'))
receipt=json.loads((O/'packet-integrity.json').read_text(encoding='utf-8'))
if receipt['status']!='PASS' or receipt['file_count']!=40 or receipt['packet_scripts_executed']!=0:
    raise RuntimeError('Expected integrity-only receipt')
if hashlib.sha256((R/'scripts/check_rank17_packet_inventory.py').read_bytes().replace(b'\r\n',b'\n')).hexdigest()!=receipt['checker_lf_sha256']:
    raise RuntimeError('Integrity checker changed')
if [(x['id'],x['status']) for x in data['layers']]!=[
 ('ambient','Our Lean proofs; physical pullback/residue incomplete'),
 ('compact','fqlx packet; not replayed here'),
 ('correction','Author reports exact identity; remainder nonzero'),
 ('rank17','Author reports compact equivalence; integration unsolved'),
 ('return','No primitive or certificate supplied')]:raise RuntimeError('Update evidence labels')
plt.rcParams['svg.hashsalt']='skew-compact-architecture'
fig=plt.figure(figsize=(16,10),facecolor='#faf9f4');ax=fig.add_axes([0,0,1,1]);ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
ax.text(.045,.94,'Reuse the architecture; preserve the proof boundaries',fontsize=25,weight='bold',color='#17333b')
ax.text(.045,.89,'one-reflection-skew  •  fqlx packet + Hodge Lab formalization  •  22 October 2026',fontsize=13,color='#53696e')
def box(x,y,w,h,title,lines,colour):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.008',facecolor=colour,edgecolor='#53696e'))
    ax.text(x+.015,y+h-.04,title,fontsize=16,weight='bold',color='#17333b')
    ax.text(x+.015,y+h-.08,lines,fontsize=12,color='#17333b',va='top',linespacing=1.5)
def arrow(x,y,xx,yy,label=None):
    ax.annotate('',xy=(xx,yy),xytext=(x,y),arrowprops={'arrowstyle':'->','color':'#53696e','lw':1.8})
    if label:ax.text((x+xx)/2,(y+yy)/2+.015,label,ha='center',fontsize=11,color='#53696e')
box(.045,.66,.39,.17,'Protected source and ambient forms','Our completed Lean proofs\nActual exterior products; positive 5/72 term\nPhysical pullback and residue map still needed','#e3efe9')
box(.565,.66,.39,.17,'Full two-row compact source','Source S + connection M + moving base\nAttribution: fqlx and declared AI assistance\nPacket mathematics not replayed in this pass','#f7ecd8')
arrow(.445,.745,.555,.745,'interface')
box(.045,.36,.39,.18,'Route A: physical correction','source = covariant derivative of Xi + R\nKeep both rows and every transverse term\nAuthor reports: R remains nonzero','#f7ecd8')
box(.565,.36,.39,.18,'Route B: trace-free rank 17','Three total derivatives + all 17 channels\nSource slot 11; unrestricted rational fluxes\nAuthor reports: compact equivalence','#f7ecd8')
arrow(.68,.65,.28,.55)
arrow(.79,.65,.79,.55)
box(.26,.13,.48,.14,'Still missing: rational integration','Then full-component trace (reported factor 1/864),\nphysical transport, homogenization and clearing','#f3e8e4')
arrow(.24,.35,.38,.28)
arrow(.76,.35,.62,.28)
ax.text(.045,.104,'Parallel routes; their composition requires a separate source-map check.',fontsize=11.5,color='#53696e')
ax.text(.045,.066,'Next proposed Lean unit: codifferent basis + trace kernel, retaining the nonmonic leading coefficient.',fontsize=12,color='#14737a',weight='bold')
ax.text(.045,.027,'Executed here: 40 file hashes and target-byte match. No packet mathematical replay, new Lean proof or primitive.',fontsize=11,color='#53696e')
for ext in ['png','svg']:
    fig.savefig(R/'visualizations'/('skew-compact-architecture.'+ext),dpi=160,facecolor=fig.get_facecolor(),metadata={'Date':None} if ext=='svg' else None)
p=R/'visualizations/skew-compact-architecture.svg'
p.write_text('\n'.join(x.rstrip() for x in p.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8',newline='\n')
print('PASS: evidence-labelled architecture map rendered')
