"""Static scientific companion to the denominator sweep; no rendering inference."""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap,BoundaryNorm

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/koszul-map-sweep'
def sha(p):
 raw=p.read_bytes()
 if p.suffix in {'.json','.svg'}:raw=raw.replace(b'\r\n',b'\n')
 return hashlib.sha256(raw).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
 if args.check:
  report=json.loads((OUT/'figure-validation.json').read_text())
  assert all(sha(OUT/name)==digest for name,digest in report['sha256'].items())
  print('PASS: static figure and source hashes');return
 d=json.loads((OUT/'sweep.json').read_text());fig=plt.figure(figsize=(12,10),layout='constrained')
 fig.suptitle('A rank drop is not a certificate',fontsize=21,weight='normal')
 blue='#226ab3';orange='#cd7a23';green='#368664'
 for index,(s,t,rank) in enumerate([(1,0,720),(0,1,713)]):
  ax=fig.add_subplot(2,2,index+1,projection='3d');angles=np.linspace(0,2*np.pi,257)
  for radius in [.25,.5,.75,1]:ax.plot(radius*s*np.cos(angles),radius*t/3*np.sin(angles),np.zeros_like(angles),color=blue,lw=2 if radius==1 else 1,alpha=1 if radius==1 else .35)
  ax.plot([0,0],[0,0],[0,1],color=orange,ls='--');ax.scatter([0],[0],[1],marker='D',color=green,s=40)
  ax.text(0,0,1.1,'Target',ha='center');ax.set(xlim=(-1.2,1.2),ylim=(-.5,.5),zlim=(0,1.2),
   xlabel='Coefficient response 1',ylabel='Coefficient response 2',zlabel='Exact syzygy height')
  ax.set_xticks([-1,0,1]);ax.set_yticks([-.33,0,.33]);ax.set_zticks([0,1]);ax.view_init(22,-62)
  ax.set_title(f's = {s}, t = {t}: full rank {rank}\nProjected rank 1 in both pictures',fontsize=12,pad=14)
  for axis in [ax.xaxis,ax.yaxis,ax.zaxis]:axis.pane.fill=False
 ax=fig.add_subplot(2,2,3);grid=np.array([[next(v['rank'] for v in d['samples'] if v['s']==s and v['t']==t) for s in d['grid']] for t in d['grid']])
 cmap=ListedColormap(['#d0e2f4','#80b0dc',blue]);norm=BoundaryNorm([680,700,717,725],3)
 im=ax.imshow(grid,origin='lower',extent=(-2.25,2.25,-2.25,2.25),cmap=cmap,norm=norm,aspect='auto')
 for s,t in [(0,0),(0,1),(1,1)]:
  val=next(v['rank'] for v in d['samples'] if v['s']==s and v['t']==t)
  ax.text(s,t,str(val),ha='center',va='center',fontsize=11,color='#17232f' if val<720 else '#ffffff',bbox={'facecolor':cmap(norm(val)),'edgecolor':'none','pad':2})
 ax.set(xlabel='s',ylabel='t',title='81 full ranks over Q; modular cross-checks agree',xticks=[-2,-1,0,1,2],yticks=[-2,-1,0,1,2])
 ax=fig.add_subplot(2,2,4);rows=[v for v in d['samples'] if v['t']==1]
 ax.plot([v['s'] for v in rows],[v['trackedRatio'] for v in rows],'-o',color=blue,ms=5)
 ax.set(xlabel='s, with t = 1',ylabel=r'$\sigma_{720} / \sigma_1$',title='Tracked singular value, t = 1\nZero at the sampled rank drop')
 ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0));ax.grid(alpha=.18)
 fig.text(.5,.004,'Fixed target (F, q = 1, A). The same exact obstruction rejects every denominator in this plane.\nFull family 4 remains unresolved; these finite algebraic rank changes do not establish a statistical phase transition.',ha='center',fontsize=10)
 fig.get_layout_engine().set(rect=(0,.055,1,.93),hspace=.18)
 for ext in ['png','svg']:fig.savefig(OUT/f'rank-sweep.{ext}',dpi=180)
 plt.close(fig)
 svg=OUT/'rank-sweep.svg'
 svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8',newline='\n')
 names=['sweep.json','rank-sweep.png','rank-sweep.svg']
 (OUT/'figure-validation.json').write_text(json.dumps({'status':'PASS','sha256':{name:sha(OUT/name) for name in names}},indent=2)+'\n')
 print('PASS: rendered PNG and SVG')
if __name__=='__main__':main()
