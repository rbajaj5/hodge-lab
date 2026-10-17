"""Static companion to the interactive, syzygy-preserving operator view."""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/koszul-geometry'


def digest(p):
    b=p.read_bytes()
    if p.suffix!='.png':b=b.replace(b'\r\n',b'\n')
    return hashlib.sha256(b).hexdigest()


def render():
    cases=json.loads((OUT/'geometry.json').read_text())['cases']
    bg,fg,muted='#141820','#edf2f7','#a1adbe';blue,gold,green='#7db9ef','#e7b67a','#7ed9b2'
    plt.rcParams.update({'figure.facecolor':bg,'axes.facecolor':bg,'savefig.facecolor':bg,
        'text.color':fg,'font.family':'DejaVu Sans','svg.fonttype':'none','svg.hashsalt':'koszul-geometric-map'})
    fig,axes=plt.subplots(1,3,figsize=(15,6.4))
    fig.subplots_adjust(left=.025,right=.975,bottom=.16,top=.79,wspace=.06)
    fig.text(.04,.94,'The target stays outside the correction image',fontsize=23)
    fig.text(.04,.88,'Three archived denominators · two response directions plus an exact syzygy coordinate',fontsize=12,color=muted)
    a=np.deg2rad(-24)
    def project(p):
        p=np.asarray(p);x,y,z=p.T
        return np.column_stack([np.cos(a)*x-np.sin(a)*y,.96*z-.48*(np.sin(a)*x+np.cos(a)*y)])
    for ax,c in zip(axes,cases):
        ax.set_aspect('equal');ax.set_xlim(-1.65,1.65);ax.set_ylim(-.85,1.55);ax.axis('off')
        ax.set_title(f"Family {c['family']} · {c['characters']} character{'s' if c['characters']!=1 else ''}",loc='center',fontsize=13,pad=14)
        for k in np.arange(-1,1.001,.25):
            for line in [[[k,-1.15,0],[k,1.15,0]],[[-1.15,k,0],[1.15,k,0]]]:
                p=project(line);ax.plot(*p.T,color=muted,alpha=.18,lw=.7)
        t=np.linspace(0,2*np.pi,257)
        for r in [.25,.5,.75,1]:
            p=project(np.column_stack([r*np.cos(t),r*c['axisRatio']*np.sin(t),t*0]))
            if r==1:ax.add_patch(Polygon(p,facecolor=blue,alpha=.10,edgecolor='none'))
            ax.plot(*p.T,color=blue,alpha=.9 if r==1 else .3,lw=1.4 if r==1 else .8)
        target=np.array(c['target']);target[:2]/=c['axes'][0]
        foot=target.copy();foot[2]=0
        p=project([foot,target]);ax.plot(*p.T,color=gold,ls='--',lw=1.8)
        ax.scatter(*p[1],marker='D',s=42,color=green,zorder=4)
        ax.scatter(*p[0],s=28,color=blue,zorder=4)
        ax.annotate('',xy=p[0],xytext=(0,0),arrowprops={'arrowstyle':'->','lw':1.8,'color':blue})
        ax.text(*[p[1,0],p[1,1]+.15],'Target −b',ha='center',fontsize=11)
        ax.text(p[0,0]+.13,np.mean(p[:,1]),'Gap 1',color=gold,fontsize=11,va='center')
        ax.text(0,-.78,f"Response axis ratio {c['axisRatio']:.3f}",ha='center',color=muted,fontsize=11)
    fig.text(.04,.10,'All 840 columns checked in each case: λR = 0 and λb = 1.',fontsize=12,color=green)
    fig.text(.04,.055,'Horizontal axes share a per-case scale; height is −λ(v). These pictures do not show full-map rank or Euclidean residual distance.',fontsize=10.5,color=muted)
    fig.savefig(OUT/'operator-geometry.png',dpi=170)
    fig.savefig(OUT/'operator-geometry.svg',metadata={'Date':None});plt.close(fig)
    p=OUT/'operator-geometry.svg';p.write_text('\n'.join(s.rstrip() for s in p.read_text().splitlines())+'\n',newline='\n')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args()
    if not a.check:render()
    record={'source_sha256':digest(OUT/'geometry.json'),
        'figures_sha256':{f:digest(OUT/f) for f in ['operator-geometry.png','operator-geometry.svg']}}
    if a.check:assert json.loads((OUT/'figure-validation.json').read_text())==record
    else:(OUT/'figure-validation.json').write_text(json.dumps(record,indent=2)+'\n',newline='\n')
    print('PASS: static geometry source and figure hashes')


if __name__=='__main__':main()
