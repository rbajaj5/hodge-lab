"""Render actual genus-48 fields and short piecewise-flat integral curves."""
from pathlib import Path
import argparse, json, time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from high_genus_flow import OUT, CHI, phase_prediction
from high_genus_complex import build_incidence
from gpu_identity_screen import load_cupy
from high_genus_raster import CODE

LINE=r'''
extern "C" __global__ void lines(const float* s,int count,const unsigned long long* hit,
 unsigned int* mask,int w,int h,float cut){
 int k=blockIdx.x*blockDim.x+threadIdx.x;if(k>=count)return;
 const float* a=s+6*k;float dx=a[3]-a[0],dy=a[4]-a[1],dd=a[5]-a[2];
 float len=dx*dx+dy*dy;if(len<1e-6f)return;
 int x0=max(0,(int)floorf(fminf(a[0],a[3])-1)),x1=min(w-1,(int)ceilf(fmaxf(a[0],a[3])+1));
 int y0=max(0,(int)floorf(fminf(a[1],a[4])-1)),y1=min(h-1,(int)ceilf(fmaxf(a[1],a[4])+1));
 for(int y=y0;y<=y1;y++)for(int x=x0;x<=x1;x++){
  float t=fminf(1,fmaxf(0,((x+.5f-a[0])*dx+(y+.5f-a[1])*dy)/len));
  float xx=x+.5f-a[0]-t*dx,yy=y+.5f-a[1]-t*dy,depth=a[2]+t*dd;
  if(xx*xx+yy*yy>1.1f||depth<cut)continue;
  unsigned long long id=hit[y*w+x];if(id==0xffffffffffffffffULL)continue;
  float front=__uint_as_float((unsigned int)(id>>32));
  if(fabsf(depth-front)<.018f)atomicExch(mask+y*w+x,1);
 }
}
'''

def geometry(v,f,harmonic):
    topo=build_incidence(v,f);ab=v[f[:,1]]-v[f[:,0]];ac=v[f[:,2]]-v[f[:,0]]
    normals=np.cross(ab,ac);areas=np.linalg.norm(normals,axis=1)/2;normals/=2*areas[:,None]
    gram=np.stack([np.stack([(ab*ab).sum(1),(ab*ac).sum(1)],axis=1),
                   np.stack([(ab*ac).sum(1),(ac*ac).sum(1)],axis=1)],axis=1)
    inverse=np.linalg.inv(gram)
    signed=harmonic[topo['face_edges']]*topo['face_signs']
    coordinates=np.einsum('fij,fj->fi',inverse,np.c_[signed[:,0],-signed[:,2]])
    reference=coordinates[:,0,None]*ab+coordinates[:,1,None]*ac
    err=max(np.max(abs((reference*ab).sum(1)-signed[:,0])),np.max(abs((reference*ac).sum(1)+signed[:,2])))
    assert err<1e-10
    vn=np.zeros_like(v)
    for j in range(3):np.add.at(vn,f[:,j],normals*areas[:,None])
    vn/=np.linalg.norm(vn,axis=1)[:,None]
    return topo,ab,ac,inverse,normals,areas,reference,vn

def trace(v,f,geo,field,k,seed=202610164802,count=1600):
    topo,ab,ac,inverse,normals,areas,reference,vn=geo
    length=np.linalg.norm(reference,axis=1);unit=reference/np.maximum(length[:,None],1e-20)
    stagnation_cutoff=1e-5*np.quantile(length,.95)
    phase=field[f].mean(axis=1)/(CHI*np.sqrt(k))
    direction=np.cos(phase)[:,None]*unit+np.sin(phase)[:,None]*np.cross(normals,unit)
    velocity=np.einsum('fij,fj->fi',inverse,np.c_[(direction*ab).sum(1),(direction*ac).sum(1)])
    db=np.c_[-velocity.sum(axis=1),velocity]
    neighbors=topo['dual_neighbors'].reshape(-1,3)
    rng=np.random.default_rng(seed);seeds=rng.choice(len(f),count,p=areas/areas.sum())
    bary=rng.dirichlet([1,1,1],count);segments=[];stopped=0
    for face,b in zip(seeds,bary):
        travelled=0.;previous=-1
        for _ in range(70):
            if length[face]<stagnation_cutoff:break
            d=db[face];dist=np.full(3,np.inf);mask=d<-1e-12;dist[mask]=-b[mask]/d[mask]
            opposite=int(np.argmin(dist));step=min(float(dist[opposite]),.045,1.7-travelled)
            if step<1e-8:stopped+=1;break
            p=b@v[f[face]];q=p+step*direction[face];segments.append([p,q]);travelled+=step
            if travelled>=1.7-1e-10:break
            if step>=dist[opposite]-1e-9:
                new=int(neighbors[face,(opposite+1)%3])
                if new==previous:stopped+=1;break
                previous,face=int(face),new;offset=q-v[f[face,0]]
                uv=inverse[face]@np.array([offset@ab[face],offset@ac[face]])
                b=np.array([1-uv.sum(),uv[0],uv[1]])
                b=np.maximum(b,0);b=(b+1e-8)/(b.sum()+3e-8)
            else:b+=step*d
    return np.array(segments),{'seeded_paths':count,'segments':len(segments),'edge_stops':stopped,
        'max_steps':70,'max_arclength':1.7,'method':'Piecewise constant rotated tangent field; terminate at immediate edge reversal. Drawing only, not an SLE sampler.'}

def render(cp,v,f,geo,field,k,cut=0,name='genus48-flow'):
    start=time.perf_counter();segments,report=trace(v,f,geo,field,k)
    c,s,ct,st=np.cos(.52),np.sin(.52),np.cos(.65),np.sin(.65)
    R=np.array([[c,-s,0],[ct*s,ct*c,-st],[st*s,st*c,ct]])
    camera=v@R.T;w,h=1800,1600;span=np.ptp(camera[:,:2],axis=0);scale=min(w/span[0],h/span[1])*.91
    center=(camera[:,:2].min(axis=0)+camera[:,:2].max(axis=0))/2
    def project(points):
        cam=points@R.T
        return np.concatenate([(cam[...,:1]-center[0])*scale+w/2,
            -(cam[...,1:2]-center[1])*scale+h/2,10-cam[...,2:3]],axis=-1).astype(np.float32)
    points=cp.asarray(project(v));faces=cp.asarray(f)
    normals=cp.asarray(geo[-1]@R.T,dtype=cp.float32)
    values=cp.asarray(field/(CHI*np.sqrt(k)),dtype=cp.float32)
    hit=cp.full((h,w),np.uint64(0xffffffffffffffff),dtype=cp.uint64)
    rgb=cp.empty((h,w,3),dtype=cp.uint8);mask=cp.zeros((h,w),dtype=cp.uint32)
    cutoff=10-camera[:,2].max()+np.ptp(camera[:,2])*cut
    code=CODE.replace('.5f+.5f*tanhf(value*1.25f)','.5f+.5f*sinf(value)')
    code=code.replace('float bands=expf(-powf(sinf(value*13),2)*150);','float bands=0;')
    raster=cp.RawKernel(code,'raster');shade=cp.RawKernel(code,'shade');lines=cp.RawKernel(LINE,'lines')
    raster(((len(f)+127)//128,),(128,),(points,faces,hit,np.int32(len(f)),np.int32(w),np.int32(h),np.float32(cutoff)))
    shade(((w*h+255)//256,),(256,),(points,faces,normals,values,hit,rgb,np.int32(w),np.int32(h),np.float32(1)))
    lines(((len(segments)+127)//128,),(128,),(cp.asarray(project(segments)),np.int32(len(segments)),hit,mask,np.int32(w),np.int32(h),np.float32(cutoff)))
    rgb=cp.where(mask[:,:,None]>0,(.55*rgb+.45*cp.array([218,244,239])).astype(cp.uint8),rgb)
    image=Image.fromarray(cp.asnumpy(rgb));image.save(OUT/(name+'.png'))
    report.update(stiffness=k,cutaway=cut,seconds=time.perf_counter()-start,renderer='CUDA depth raster, shading and curve visibility')
    return image,report

def plot_phase():
    data=np.load(OUT/'fields.npz');report=json.loads((OUT/'report.json').read_text())
    fig,axs=plt.subplots(1,2,figsize=(12.8,4.7),layout='constrained');k=data['stiffness']
    colors=['#af4774','#267c8b','#ad732b']
    for i,a in enumerate(data['anisotropy']):
        prediction,response=phase_prediction(data['covariances'][i],k)
        axs[0].semilogx(k,prediction,color=colors[i],lw=2,label=f'a = {a:g}')
        axs[0].fill_between(k,data['mc_mean'][i]-2*data['mc_se'][i],data['mc_mean'][i]+2*data['mc_se'][i],color=colors[i],alpha=.12)
        axs[0].plot(k[::5],data['mc_mean'][i,::5],'.',color=colors[i],ms=4)
        axs[1].semilogx(k,response,color=colors[i],lw=2)
    axs[0].set(xlabel='Stiffness K (chosen graph units)',ylabel='Expected relative-phase coherence |m|²',ylim=(0,1.02),title='Analytic curves; GPU samples with ±2 SE bands')
    axs[0].legend(frameon=False)
    axs[1].set(xlabel='Stiffness K (chosen graph units)',ylabel='d E|m|² / d log K',title='Broad response, not a phase transition')
    for ax in axs:ax.spines[['top','right']].set_visible(False)
    fig.suptitle('48 handles · 256 independent samples per weight · 96 fixed observation vertices',fontsize=14)
    fig.savefig(OUT/'phase-response.png',dpi=180);plt.close(fig)

def main(args):
    cp,handles=load_cupy(args.deps);mesh=np.load(OUT/'surface.npz');data=np.load(OUT/'fields.npz')
    v=mesh['vertices'].astype(float);f=mesh['faces'].astype(np.int32);geo=geometry(v,f,data['harmonic'])
    reports=[];images=[]
    for k in [.03,.2,2.]:
        im,r=render(cp,v,f,geo,data['fields'][1],k,name=f'genus48-K-{k:g}');reports.append(r);images.append(im)
    canvas=Image.new('RGB',(2400,800),(4,8,17));draw=ImageDraw.Draw(canvas)
    font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',30) if Path('C:/Windows/Fonts/segoeui.ttf').exists() else ImageFont.load_default(size=30)
    for i,(im,k) in enumerate(zip(images,[.03,.2,2.])):
        canvas.paste(im.resize((800,711)),(800*i,60));draw.text((800*i+30,15),f'K = {k:g}',font=font,fill=(226,236,240))
    canvas.save(OUT/'stiffness-triptych.png')
    (OUT/'render-report.json').write_text(json.dumps(reports,indent=2)+'\n',encoding='utf-8')
    plot_phase();print(json.dumps(reports,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--deps',type=Path)
    main(parser.parse_args())
