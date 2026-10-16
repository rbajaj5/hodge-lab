"""CUDA GFF/regularized-flow illustrations with paired angle/anisotropy views.

Uses a periodic weighted graph GFF, not the continuum GFF/SLE coupling.
The finite field has covariance L_c^+ before heat smoothing. No per-sample
normalization is used in the direction field. Color/LIC contrast is display.
"""
from pathlib import Path
import argparse, base64, json, time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gpu_identity_screen import load_cupy

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/imaginary-geometry'
SEED=2026101649
SOURCE=r'''
__device__ float sample(const float* a,float x,float y,int n){
 x=x-floorf(x/n)*n;y=y-floorf(y/n)*n;
 // Float subtraction can round a tiny negative position up to exactly n.
 if(x>=n)x=0;if(y>=n)y=0;if(x<0)x+=n;if(y<0)y+=n;
 int i=(int)x,j=(int)y,ii=(i+1)%n,jj=(j+1)%n;
 float u=x-i,v=y-j;
 return (1-v)*((1-u)*a[j*n+i]+u*a[j*n+ii])+v*((1-u)*a[jj*n+i]+u*a[jj*n+ii]);
}
extern "C" __global__ void lic(const float* vx,const float* vy,const float* noise,
 float* result,int n,int steps,float stride){
 int k=blockDim.x*blockIdx.x+threadIdx.x;if(k>=n*n)return;
 float total=noise[k],weight=1;
 for(int sign=-1;sign<=1;sign+=2){
  float x=k%n,y=k/n;
  for(int t=1;t<=steps;t++){
   float a=sample(vx,x,y,n),b=sample(vy,x,y,n),length=sqrtf(a*a+b*b)+1e-8f;
   float mx=x+sign*.5f*stride*a/length,my=y+sign*.5f*stride*b/length;
   a=sample(vx,mx,my,n);b=sample(vy,mx,my,n);length=sqrtf(a*a+b*b)+1e-8f;
   x+=sign*stride*a/length;y+=sign*stride*b/length;
   float w=.5f+.5f*cosf(3.14159265359f*t/(steps+1));
   total+=w*sample(noise,x,y,n);weight+=w;
  }
 }
 result[k]=total/weight;
}
'''

def font(size):
    for name in ['C:/Windows/Fonts/segoeui.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
        if Path(name).exists():return ImageFont.truetype(name,size)
    return ImageFont.load_default(size=size)

def triptych(images,title,labels,subtitle,path):
    w=960;canvas=Image.new('RGB',(3*w+112,1160),(8,15,25));draw=ImageDraw.Draw(canvas)
    draw.text((28,22),title,font=font(43),fill=(235,242,247))
    draw.text((30,86),subtitle,font=font(24),fill=(170,190,205))
    for i,(im,label) in enumerate(zip(images,labels)):
        x=28+i*(w+28);canvas.paste(im.resize((w,w),Image.Resampling.LANCZOS),(x,142))
        draw.text((x,1110),label,font=font(25),fill=(235,242,247))
    canvas.save(path)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--deps',type=Path)
    args=parser.parse_args();cp,handles=load_cupy(args.deps);OUT.mkdir(parents=True,exist_ok=True)
    start=time.perf_counter();n=1280;smoothing=18.;chi=.62
    noise_cpu=np.random.default_rng(SEED).standard_normal((n,n))
    white=cp.asarray(noise_cpu);W=cp.fft.fft2(white);W[0,0]=0
    frequencies=cp.fft.fftfreq(n);lam=4*cp.sin(cp.pi*frequencies)**2
    isotropic=lam[:,None]+lam[None,:];smooth=cp.exp(-smoothing*isotropic)
    kernel=cp.RawKernel(SOURCE,'lic')
    texture_noise=cp.asarray(np.random.default_rng(SEED+1).random((n,n),dtype=np.float32))
    weights=[(1.,1.),(4.,.25),(.25,4.)];names=['Isotropic','Horizontal conductance','Vertical conductance']
    fields=[];errors=[];energies=[]
    for cx,cy in weights:
        eigen=cx*lam[None,:]+cy*lam[:,None];eigen[0,0]=1
        coefficients=W/cp.sqrt(eigen);coefficients[0,0]=0
        field=cp.fft.ifft2(coefficients*smooth).real
        cpu_lam=4*np.sin(np.pi*np.fft.fftfreq(n))**2
        denominator=cx*cpu_lam[None,:]+cy*cpu_lam[:,None];denominator[0,0]=1
        cpuW=np.fft.fft2(noise_cpu);cpuW[0,0]=0
        expected=np.fft.ifft2(cpuW/np.sqrt(denominator)*np.exp(-smoothing*(cpu_lam[:,None]+cpu_lam[None,:]))).real
        errors.append(float(cp.max(cp.abs(field-cp.asarray(expected)))))
        energy=float(cp.sum(cp.abs(coefficients)**2*eigen).real/(n*n))
        reference=float(np.sum((noise_cpu-noise_cpu.mean())**2))
        energies.append(abs(energy-reference)/reference)
        fields.append(field)
    assert max(errors)<1e-10 and max(energies)<1e-12
    palette=cp.asarray([[.025,.055,.13],[.055,.30,.42],[.12,.67,.66],[.96,.63,.31],[1.,.94,.74]])
    texture_stats=[]
    def render(h,theta):
        angle=h/chi+theta
        vx=cp.ascontiguousarray(cp.cos(angle),dtype=cp.float32)
        vy=cp.ascontiguousarray(cp.sin(angle),dtype=cp.float32)
        grain=cp.empty_like(texture_noise)
        kernel(((n*n+255)//256,),(256,),(vx,vy,texture_noise,grain,np.int32(n),np.int32(95),np.float32(.9)))
        assert bool(cp.all(cp.isfinite(grain)))
        # Fixed field color scale shared by every image; no phase normalization.
        t=cp.clip((h+2.4)/4.8,0,1)*4;i=cp.minimum(t.astype(cp.int32),3);a=(t-i)[...,None]
        color=palette[i]*(1-a)+palette[i+1]*a
        # Fixed LIC contrast shared by every image, independent of its variance.
        brightness=.20+.80/(1+cp.exp(-32*(grain-.5)))
        rgb=cp.clip(color*brightness[...,None],0,1)**.83
        texture_stats.append({'mean':float(cp.mean(grain)),'std':float(cp.std(grain))})
        return Image.fromarray(cp.asnumpy(cp.rint(rgb[::-1]*255).astype(cp.uint8)))
    angle_images=[render(fields[0],theta) for theta in [-np.pi/3,0,np.pi/3]]
    angle_images[1].save(OUT/'imaginary-currents.png')
    triptych(angle_images,'One field, three directions',
        ['Angle -60 degrees','Angle 0 degrees','Angle +60 degrees'],
        'Regularized GFF flow texture | Same field and display noise | Periodic square',OUT/'angle-triptych.png')
    anisotropic_images=[angle_images[1],render(fields[1],0),render(fields[2],0)]
    triptych(anisotropic_images,'Changing the cost of variation',
        ['Conductances (1, 1)','Conductances (4, 1/4)','Conductances (1/4, 4)'],
        'Same Gaussian coefficients | Same flow angle | Same smoothing and color scale',OUT/'anisotropy-triptych.png')
    # A coarser display field for the inline visual, smoothed before subsampling.
    # The extra filter is explicitly recorded; it is not the full-resolution PNG field.
    export=[]
    for h in fields:
        softened=cp.fft.ifft2(cp.fft.fft2(h)*cp.exp(-8*isotropic)).real
        export.append(cp.asnumpy(softened[::5,::5]))
    raw=np.array(export);quantized=np.rint(raw*4000).astype('<i2')
    assert np.max(np.abs(raw))<8
    payload={'n':256,'scale':4000,'data':base64.b64encode(quantized.tobytes()).decode(),
        'names':names,'weights':weights,'chi':chi,'heat_time_original_grid':26,
        'quantization_max_error':float(np.max(np.abs(raw-quantized/4000)))}
    (OUT/'display-fields.json').write_text(json.dumps(payload,separators=(',',':')))
    cp.cuda.Device().synchronize()
    report={'gpu':cp.cuda.runtime.getDeviceProperties(0)['name'].decode(),'grid':[n,n],
        'seed':SEED,'precision':'L_c = cx L_x + cy L_y on the periodic square grid',
        'covariance_before_smoothing':'L_c pseudoinverse on mean-zero functions',
        'weights':weights,'shared_gaussian_coefficients':True,'shared_LIC_noise':True,
        'phase':'h_smoothed / 0.62 + theta; no sample-dependent phase rescaling',
        'smoothing':'exp(-18 L_isotropic), fixed across conductances',
        'mean_zero_errors':[abs(float(cp.mean(h))) for h in fields],
        'CPU_GPU_max_errors':errors,'spectral_energy_relative_errors':energies,
        'LIC':'95 midpoint steps in each direction, stride 0.9 grid cells, periodic bilinear sampling',
        'LIC_statistics':texture_stats,'display_color_limits':[-2.4,2.4],
        'display_fields':'256x256, extra heat time 8 then stride-5 subsampling, int16 / 4000',
        'seconds':time.perf_counter()-start,
        'limits':'Finite heat-regularized GFF angle flows; no exact SLE sample, GFF/SLE coupling, or convergence claim. '
                 'The anisotropic variants are chosen weighted models. The periodic domain is genus one, not genus 48. '
                 'No holdout polynomial certificate follows from these images.',
        'references':['https://math.mit.edu/research/undergraduate/urop-plus/documents/2016/Sellke.pdf',
            'https://arxiv.org/abs/1201.1496','https://arxiv.org/abs/1110.2808']}
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
