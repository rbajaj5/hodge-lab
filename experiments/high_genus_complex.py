"""Combinatorial incidence and CUDA Poisson helpers for the saved genus-48 mesh.
Extracted from this project's earlier high-genus experiment. Identity cochain
metrics; not a cotangent discretization of a smooth surface.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import sys
import time
import numpy as np
from scipy.sparse import coo_matrix


def load_cupy(deps):
    handles=[]
    if deps.is_dir():
        sys.path.insert(0,str(deps.resolve()))
        os.environ['CUDA_PATH']=str((deps/'nvidia/cuda_runtime').resolve())
        os.environ['CUPY_CACHE_DIR']=str((deps.parent/'cupy_cache').resolve())
        bins=[p.resolve() for p in (deps/'nvidia').glob('*/bin')]
        if os.name=='nt':
            handles=[os.add_dll_directory(str(p)) for p in bins]
            os.environ['PATH']=os.pathsep.join(map(str,bins))+os.pathsep+os.environ['PATH']
    import cupy as cp
    if cp.cuda.runtime.getDeviceCount()<1:
        raise RuntimeError('Actual CUDA execution required; no GPU found.')
    return cp,handles


def build_incidence(vertices,faces):
    nv,nf=len(vertices),len(faces)
    oriented=np.stack((faces[:,[0,1]],faces[:,[1,2]],faces[:,[2,0]]),axis=1).reshape(-1,2)
    edges,inverse,counts=np.unique(np.sort(oriented,axis=1),axis=0,return_inverse=True,return_counts=True)
    if not np.all(counts==2):
        raise ValueError('Every mesh edge must have exactly two incident faces.')
    ne=len(edges)
    sign=np.where(oriented[:,0]==edges[inverse,0],1,-1).astype(np.int8)
    face_edges=inverse.reshape(nf,3).astype(np.int32)
    face_signs=sign.reshape(nf,3)
    order=np.argsort(inverse,kind='stable')
    edge_faces=np.repeat(np.arange(nf,dtype=np.int32),3)[order].reshape(ne,2)
    edge_signs=sign[order].reshape(ne,2)
    if np.any(edge_signs.sum(axis=1)):
        raise ValueError('Face orientation must be globally consistent.')
    row=np.repeat(np.arange(ne),2)
    d0=coo_matrix((np.tile(np.array([-1,1],dtype=np.int8),ne),(row,edges.ravel())),shape=(ne,nv)).tocsr()
    d1=coo_matrix((sign,(np.repeat(np.arange(nf),3),inverse)),shape=(nf,ne)).tocsr()
    boundary=d1@d0
    boundary.eliminate_zeros()
    if boundary.nnz:
        raise AssertionError('Incidence complex violated D1 D0 = 0.')
    d0t=d0.T.tocsr()
    adj=coo_matrix((np.ones(2*ne,dtype=np.int8),
        (np.r_[edges[:,0],edges[:,1]],np.r_[edges[:,1],edges[:,0]])),shape=(nv,nv)).tocsr()
    face_index=np.arange(nf)[:,None]
    adjacent=edge_faces[face_edges]
    dual_neighbors=np.where(adjacent[:,:,0]==face_index,adjacent[:,:,1],adjacent[:,:,0]).astype(np.int32)
    return dict(nv=nv,ne=ne,nf=nf,edges=edges.astype(np.int32),face_edges=face_edges,
        face_signs=face_signs,edge_faces=edge_faces,edge_signs=edge_signs,
        vertex_ptr=adj.indptr.astype(np.int32),vertex_neighbors=adj.indices.astype(np.int32),
        dual_ptr=np.arange(0,3*nf+1,3,dtype=np.int32),dual_neighbors=dual_neighbors.ravel(),
        d0t_ptr=d0t.indptr.astype(np.int32),d0t_edges=d0t.indices.astype(np.int32),
        d0t_signs=d0t.data.astype(np.int8),chain_product_nnz=boundary.nnz)


KERNELS=r'''
extern "C" __global__ void laplace(const int n, const int b, const int* ptr,
  const int* nbr, const double* x, double* out) {
  int id=blockDim.x*blockIdx.x+threadIdx.x;
  if(id>=n*b)return;
  int i=id/b, k=id%b;
  if(i==0){out[id]=x[id];return;}
  double v=(ptr[i+1]-ptr[i])*x[id];
  for(int j=ptr[i];j<ptr[i+1];j++)if(nbr[j]!=0)v-=x[nbr[j]*b+k];
  out[id]=v;
}
extern "C" __global__ void d0transpose(const int n, const int b, const int* ptr,
  const int* edge, const signed char* sign, const double* x, double* out) {
  int id=blockDim.x*blockIdx.x+threadIdx.x;
  if(id>=n*b)return;
  int i=id/b, k=id%b; double v=0;
  for(int j=ptr[i];j<ptr[i+1];j++)v+=sign[j]*x[edge[j]*b+k];
  out[id]=v;
}
'''


class GPUComplex:
    def __init__(self,cp,topo):
        self.cp,self.t=cp,topo
        self.a={key:cp.asarray(value) for key,value in topo.items() if isinstance(value,np.ndarray)}
        self.lap_kernel=cp.RawKernel(KERNELS,'laplace')
        self.d0t_kernel=cp.RawKernel(KERNELS,'d0transpose')
    def d0(self,x):
        e=self.a['edges'];return x[e[:,1]]-x[e[:,0]]
    def d0t(self,x):
        if x.ndim==1:x=x[:,None]
        n,b=self.t['nv'],x.shape[1]
        out=self.cp.empty((n,b),dtype=self.cp.float64)
        self.d0t_kernel(((n*b+255)//256,),(256,),
            (np.int32(n),np.int32(b),self.a['d0t_ptr'],self.a['d0t_edges'],self.a['d0t_signs'],x,out))
        return out
    def d1(self,x):
        if x.ndim==1:x=x[:,None]
        return self.cp.sum(self.a['face_signs'][:,:,None]*x[self.a['face_edges']],axis=1)
    def d1t(self,x):
        if x.ndim==1:x=x[:,None]
        return self.cp.sum(self.a['edge_signs'][:,:,None]*x[self.a['edge_faces']],axis=1)
    def lap(self,x,kind):
        n,b=x.shape
        out=self.cp.empty_like(x)
        self.lap_kernel(((n*b+255)//256,),(256,),
            (np.int32(n),np.int32(b),self.a[kind+'_ptr'],self.a[kind+'_neighbors'],x,out))
        return out
    def solve(self,rhs,kind,tol=2e-11,maxiter=6000):
        """Batched Jacobi PCG with a symmetric one-node Dirichlet gauge."""
        cp=self.cp
        rhs=rhs.copy();rhs[0]=0
        x=cp.zeros_like(rhs);r=rhs.copy()
        deg=cp.diff(self.a[kind+'_ptr']).astype(cp.float64);deg[0]=1
        norm=cp.sqrt(cp.sum(rhs*rhs,axis=0))
        if bool(cp.any(norm==0).get()):raise ValueError('Unexpected zero probe RHS')
        z=r/deg[:,None];p=z.copy();rz=cp.sum(r*z,axis=0)
        cp.cuda.Device().synchronize();start=time.perf_counter()
        true_rel=None;restarts=0
        for iteration in range(1,maxiter+1):
            ap=self.lap(p,kind)
            alpha=rz/cp.sum(p*ap,axis=0)
            x+=p*alpha[None,:];r-=ap*alpha[None,:]
            if iteration%20==0:
                rel=cp.sqrt(cp.sum(r*r,axis=0))/norm
                worst=float(cp.max(rel).get())
                if not np.isfinite(worst):raise ArithmeticError('Non-finite PCG residual')
                if worst<tol:
                    r=rhs-self.lap(x,kind)
                    true_rel=cp.sqrt(cp.sum(r*r,axis=0))/norm
                    if float(cp.max(true_rel).get())<tol*5:break
                    z=r/deg[:,None];p=z.copy();rz=cp.sum(r*z,axis=0);restarts+=1
                    continue
            z=r/deg[:,None]
            newrz=cp.sum(r*z,axis=0)
            p=z+p*(newrz/rz)[None,:];rz=newrz
        else:raise ArithmeticError(f'{kind} PCG did not converge in {maxiter} iterations')
        cp.cuda.Device().synchronize()
        elapsed=time.perf_counter()-start
        return x,{'iterations':iteration,'seconds':elapsed,'rhs_count':rhs.shape[1],
            'tolerance':tol,'max_true_relative_residual':float(cp.max(true_rel).get()),
            'true_relative_residuals':cp.asnumpy(true_rel).tolist(),'residual_restarts':restarts,
            'gauge':'node 0 fixed to zero; principal reduced graph Laplacian'}
