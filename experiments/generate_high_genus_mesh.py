"""Seeded random handlebody surface for a high-genus Hodge experiment.

This is the boundary of a thickened connected random subgraph of a jittered
4x4x4 lattice. It is not a uniform random triangulation, a random hyperbolic
surface, or a Weil-Petersson sample. Graph cycle rank predicts the genus; all
reported topology is checked on the actual exported triangle mesh.

Dependencies: NumPy, SciPy, scikit-image, fast-simplification, Matplotlib.
The run used scikit-image 0.26.0 and fast-simplification 0.2.0. Install the
workspace-only extras with:
  python -m pip install --target work/high_genus/deps --no-deps scikit-image==0.26.0 fast-simplification==0.2.0 lazy-loader==0.6
"""
from pathlib import Path
import sys
import argparse
import json
import numpy as np
from scipy.sparse import coo_matrix, csr_matrix
from scipy.sparse.csgraph import connected_components

ROOT = Path(__file__).resolve().parents[1]
DEPS = ROOT / 'work' / 'high_genus' / 'deps'
if DEPS.exists():
    sys.path.insert(0, str(DEPS))
from skimage.measure import marching_cubes
import fast_simplification


def random_graph(seed=20261016, genus=48):
    rng = np.random.default_rng(seed)
    grid = np.asarray([(x,y,z) for x in range(4) for y in range(4) for z in range(4)])
    edges = np.asarray([(i,j) for i in range(len(grid)) for j in range(i+1,len(grid))
                        if np.abs(grid[i]-grid[j]).sum() == 1], dtype=np.int32)
    parent = np.arange(len(grid))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    tree, others = [], []
    for idx in rng.permutation(len(edges)):
        u,v = edges[idx]
        a,b = find(u),find(v)
        if a != b:
            parent[a] = b
            tree.append(idx)
        else:
            others.append(idx)
    chosen = np.asarray(tree + list(rng.choice(others, size=genus, replace=False)))
    points = grid.astype(float)-1.5 + rng.uniform(-.105,.105,grid.shape)
    # Gentle coordinate deformation removes a rigid box silhouette without
    # bringing disjoint lattice edges close enough to change the handlebody.
    points[:,0] += .13*np.sin(1.3*points[:,1])
    points[:,2] += .12*np.cos(points[:,0]+points[:,1])
    radii = rng.uniform(.185,.225,len(points))
    return points, edges[chosen], radii


def mesh_stats(vertices, faces):
    directed = np.concatenate([faces[:,[0,1]],faces[:,[1,2]],faces[:,[2,0]]])
    sorted_edges = np.sort(directed,axis=1)
    edges, inv, counts = np.unique(sorted_edges,axis=0,return_inverse=True,return_counts=True)
    signs = np.where(directed[:,0]<directed[:,1],1,-1)
    orientation = np.bincount(inv,weights=signs,minlength=len(edges))
    adj = coo_matrix((np.ones(2*len(edges)),
                    (np.r_[edges[:,0],edges[:,1]],np.r_[edges[:,1],edges[:,0]])),
                    shape=(len(vertices),len(vertices))).tocsr()
    nc,_ = connected_components(adj,directed=False)
    cross = np.cross(vertices[faces[:,1]]-vertices[faces[:,0]],vertices[faces[:,2]]-vertices[faces[:,0]])
    areas = np.linalg.norm(cross,axis=1)/2
    signed_volume = np.einsum('ij,ij->i',vertices[faces[:,0]],cross).sum()/6
    euler = len(vertices)-len(edges)+len(faces)
    # Every vertex link must be a single circle, excluding pinched vertices.
    links = [[] for _ in vertices]
    for a,b,c in faces:
        links[a].append((int(b),int(c)))
        links[b].append((int(c),int(a)))
        links[c].append((int(a),int(b)))
    bad_links = 0
    for pairs in links:
        neighbors = {}
        for a,b in pairs:
            neighbors.setdefault(a,[]).append(b)
            neighbors.setdefault(b,[]).append(a)
        seen=set()
        todo=[next(iter(neighbors))] if neighbors else []
        while todo:
            a=todo.pop()
            if a in seen: continue
            seen.add(a)
            todo.extend(b for b in neighbors[a] if b not in seen)
        if len(seen)!=len(neighbors) or any(len(v)!=2 for v in neighbors.values()):
            bad_links+=1
    return dict(vertices=len(vertices),edges=len(edges),faces=len(faces),
                euler_characteristic=euler,genus=int((2-euler)//2),
                connected_components=int(nc),boundary_edges=int((counts==1).sum()),
                nonmanifold_edges=int((counts!=2).sum()),inconsistent_oriented_edges=int((orientation!=0).sum()),
                nonmanifold_vertex_links=bad_links,
                min_triangle_area=float(areas.min()),surface_area=float(areas.sum()),
                signed_volume=float(signed_volume)), adj


def generate(seed, genus, resolution, target_vertices):
    points,gedges,radii=random_graph(seed,genus)
    margin=.42
    lower=points.min(axis=0)-margin
    upper=points.max(axis=0)+margin
    step=max(upper-lower)/(resolution-1)
    sizes=np.ceil((upper-lower)/step).astype(int)+1
    axes=[lower[i]+step*np.arange(sizes[i]) for i in range(3)]
    xyz=np.stack(np.meshgrid(*axes,indexing='ij'),axis=-1)
    sdf=np.full(tuple(sizes),1e6)
    for a,b in gedges:
        delta=points[b]-points[a]
        t=np.clip(np.einsum('...j,j->...',xyz-points[a],delta)/np.dot(delta,delta),0,1)
        nearest=points[a]+t[...,None]*delta
        radius=radii[a]+t*(radii[b]-radii[a])
        sdf=np.minimum(sdf,np.linalg.norm(xyz-nearest,axis=-1)-radius)
    vertices,faces,_,_=marching_cubes(sdf,level=0,spacing=(step,)*3,allow_degenerate=False)
    vertices=vertices.astype(float)+lower
    faces=faces.astype(np.int32)
    original,_=mesh_stats(vertices,faces)
    if original['genus']!=genus or original['nonmanifold_edges'] or original['nonmanifold_vertex_links']:
        raise RuntimeError(f'Unexpected marching-cubes topology: {original}')
    print('Marching-cubes topology',json.dumps(original),flush=True)
    stats,adj=mesh_stats(vertices,faces)
    # Taubin smoothing suppresses voxel stair steps with little shrinkage.
    degree=np.asarray(adj.sum(axis=1)).ravel()
    for _ in range(12):
        for rate in (.5,-.53):
            vertices+=rate*(adj@vertices/degree[:,None]-vertices)
    target_faces=2*target_vertices-4+4*genus
    if len(faces)>target_faces:
        vertices,faces=fast_simplification.simplify(vertices,faces,target_count=target_faces,agg=5)
        faces=faces.astype(np.int32)
    stats,adj=mesh_stats(vertices,faces)
    if stats['signed_volume']<0:
        faces=faces[:,[0,2,1]]
        stats,adj=mesh_stats(vertices,faces)
    assert stats['genus']==genus,stats
    assert stats['connected_components']==1 and stats['boundary_edges']==0,stats
    assert stats['nonmanifold_edges']==0 and stats['inconsistent_oriented_edges']==0,stats
    assert stats['nonmanifold_vertex_links']==0 and stats['min_triangle_area']>1e-12,stats
    return vertices,faces,points,gedges,radii,stats,original


def preview(vertices,faces,filename,genus):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    plt.rcParams.update({'font.family':'DejaVu Sans'})
    fig=plt.figure(figsize=(12,10),facecolor='#071626')
    ax=fig.add_axes([0,0,1,1],projection='3d',computed_zorder=False)
    ax.set_facecolor('#071626')
    center=vertices[faces].mean(axis=1)
    cross=np.cross(vertices[faces[:,1]]-vertices[faces[:,0]],vertices[faces[:,2]]-vertices[faces[:,0]])
    normals=cross/np.linalg.norm(cross,axis=1)[:,None]
    light=np.array([.4,-.5,.8]);light/=np.linalg.norm(light)
    shade=.35+.65*np.clip(normals@light,0,1)
    c=np.clip((center[:,2]+2)/4,0,1)
    base=np.stack([.16+.15*c,.56+.26*c,.70+.22*c],axis=-1)
    colors=base*shade[:,None]
    mesh=Poly3DCollection(vertices[faces],facecolors=colors,edgecolors='none',linewidths=0,rasterized=True)
    ax.add_collection3d(mesh)
    for fn in (ax.set_xlim,ax.set_ylim,ax.set_zlim):fn(-2.25,2.25)
    ax.set_box_aspect([1,1,1]); ax.view_init(elev=23,azim=-47);ax.set_proj_type('ortho');ax.set_axis_off()
    fig.text(.05,.94,f'{genus} handles, one connected surface',color='#eef7fc',fontsize=24,weight='bold')
    fig.text(.05,.9,'Seeded random lattice handlebody · closed orientable triangulation',color='#92afc0',fontsize=12)
    fig.savefig(filename,dpi=170,facecolor=fig.get_facecolor())
    plt.close(fig)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--seed',type=int,default=20261016)
    parser.add_argument('--genus',type=int,default=48)
    parser.add_argument('--resolution',type=int,default=72)
    parser.add_argument('--vertices',type=int,default=7200)
    parser.add_argument('--output',type=Path,default=ROOT/'work'/'regenerated-high-genus')
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    v,f,p,e,r,s,original=generate(args.seed,args.genus,args.resolution,args.vertices)
    np.savez_compressed(args.output/'surface.npz',vertices=v,faces=f,skeleton_vertices=p,
                        skeleton_edges=e,skeleton_radii=r,seed=np.int64(args.seed))
    meta={'model':'Boundary of a thickened seeded random connected subgraph of a jittered 4x4x4 lattice',
          'sampling':f'Randomized-Kruskal spanning tree plus {args.genus} randomly chosen remaining lattice edges; not a uniform triangulation or Weil-Petersson sample',
          'seed':args.seed,'skeleton_vertices':len(p),'skeleton_edges':len(e),
          'generator_parameters':{'lattice_dimensions':[4,4,4],'candidate_edges':144,
                                  'node_jitter':'Independent uniform[-0.105,0.105] per coordinate',
                                  'coordinate_warp':'x += 0.13 sin(1.3 y); z += 0.12 cos(x+y)',
                                  'node_radii':'Independent uniform[0.185,0.225], linearly interpolated along edges',
                                  'implicit_surface':'Zero level of the minimum signed capsule distance'},
          'skeleton_cycle_rank':len(e)-len(p)+1,'topology':s,'before_simplification':original,
          'resolution':args.resolution,'smoothing':'12 Taubin pairs (lambda=0.5, mu=-0.53)',
          'simplification':'Quadric edge collapse; topology checked afterward',
          'expected_real_harmonic_one_form_dimension':2*s['genus']}
    (args.output/'topology.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
    preview(v,f,args.output/'surface-preview.png',s['genus'])
    print(json.dumps(meta,indent=2),flush=True)

if __name__=='__main__':
    main()
