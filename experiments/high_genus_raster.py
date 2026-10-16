"""CUDA mesh depth raster and display-only lighting, reused from our earlier gallery."""
CODE = r'''
__device__ float edge(float ax,float ay,float bx,float by,float x,float y){return (x-ax)*(by-ay)-(y-ay)*(bx-ax);}
extern "C" __global__ void raster(const float* p,const int* f,unsigned long long* hit,int nf,int w,int h,float cut){
 int t=blockIdx.x*blockDim.x+threadIdx.x;if(t>=nf)return;
 int a=f[3*t]*3,b=f[3*t+1]*3,c=f[3*t+2]*3;
 float ax=p[a],ay=p[a+1],bx=p[b],by=p[b+1],cx=p[c],cy=p[c+1];
 float area=edge(ax,ay,bx,by,cx,cy);if(fabsf(area)<1e-7f)return;
 int x0=max(0,(int)floorf(fminf(ax,fminf(bx,cx)))),x1=min(w-1,(int)ceilf(fmaxf(ax,fmaxf(bx,cx))));
 int y0=max(0,(int)floorf(fminf(ay,fminf(by,cy)))),y1=min(h-1,(int)ceilf(fmaxf(ay,fmaxf(by,cy))));
 for(int y=y0;y<=y1;y++)for(int x=x0;x<=x1;x++){
  float u=edge(bx,by,cx,cy,x+.5f,y+.5f)/area,v=edge(cx,cy,ax,ay,x+.5f,y+.5f)/area,z=1-u-v;
  if(u<-.00001f||v<-.00001f||z<-.00001f)continue;
  float depth=u*p[a+2]+v*p[b+2]+z*p[c+2];if(depth<cut)continue;
  unsigned long long packed=((unsigned long long)__float_as_uint(depth)<<32)|(unsigned int)t;
  atomicMin(&hit[y*w+x],packed);
 }
}
extern "C" __global__ void shade(const float* p,const int* f,const float* normals,const float* field,
 const unsigned long long* hit,unsigned char* out,int w,int h,float spread){
 int k=blockDim.x*blockIdx.x+threadIdx.x;if(k>=w*h)return;int x=k%w,y=k/w;
 float xx=(x-w*.5f)/w,yy=(y-h*.5f)/h;
 float halo=expf(-5*(xx*xx+yy*yy));
 float r=.012f+.014f*halo,g=.021f+.027f*halo,b=.043f+.05f*halo;
 unsigned long long id=hit[k];
 if(id!=0xffffffffffffffffULL){
  int t=(unsigned int)id,a=f[3*t],bb=f[3*t+1],c=f[3*t+2];
  float area=edge(p[3*a],p[3*a+1],p[3*bb],p[3*bb+1],p[3*c],p[3*c+1]);
  float u=edge(p[3*bb],p[3*bb+1],p[3*c],p[3*c+1],x+.5f,y+.5f)/area;
  float v=edge(p[3*c],p[3*c+1],p[3*a],p[3*a+1],x+.5f,y+.5f)/area,q=1-u-v;
  float nx=u*normals[3*a]+v*normals[3*bb]+q*normals[3*c];
  float ny=u*normals[3*a+1]+v*normals[3*bb+1]+q*normals[3*c+1];
  float nz=u*normals[3*a+2]+v*normals[3*bb+2]+q*normals[3*c+2];
  float norm=sqrtf(nx*nx+ny*ny+nz*nz)+1e-9f;nx/=norm;ny/=norm;nz/=norm;
  if(nz<0){nx=-nx;ny=-ny;nz=-nz;}
  float value=(u*field[a]+v*field[bb]+q*field[c])/spread;
  float color=.5f+.5f*tanhf(value*1.25f);
  float cr=.9f*(1-color)+.035f*color,cg=.49f*(1-color)+.57f*color,cb=.14f*(1-color)+.76f*color;
  float light=.24f+.76f*fmaxf(0,-.43f*nx+.50f*ny+.75f*nz);
  float rim=powf(1-nz,3),spec=powf(fmaxf(0,-.24f*nx+.25f*ny+.94f*nz),55);
  float bands=expf(-powf(sinf(value*13),2)*150);
  float occlusion=0,depth=__uint_as_float((unsigned int)(id>>32));
  for(int j=0;j<12;j++){
   float angle=j*2.399963f;int radius=5+(j%4)*9;
   int sx=x+(int)(radius*cosf(angle)),sy=y+(int)(radius*sinf(angle));
   if(sx>=0&&sx<w&&sy>=0&&sy<h){
    unsigned long long near=hit[sy*w+sx];if(near!=0xffffffffffffffffULL){
     float delta=depth-__uint_as_float((unsigned int)(near>>32));
     if(delta>.025f&&delta<1.2f)occlusion+=expf(-delta*1.5f);
    }
   }
  }
  light*=1-.38f*occlusion/12;
  r=cr*light+.45f*spec+.12f*rim+.09f*bands;
  g=cg*light+.55f*spec+.25f*rim+.10f*bands;
  b=cb*light+.62f*spec+.32f*rim+.08f*bands;
 }
 out[k*3]=(unsigned char)(255*powf(fminf(1,fmaxf(0,r)),.85f));
 out[k*3+1]=(unsigned char)(255*powf(fminf(1,fmaxf(0,g)),.85f));
 out[k*3+2]=(unsigned char)(255*powf(fminf(1,fmaxf(0,b)),.85f));
}
'''
