"""Refine and terrace only Gosain capital triangles; preserve the rest exactly."""
from gosain37_geometry import *
import time
t0=time.time();v=[];uv=[];vn=[];f=[]
for line in (SRC/'SM_IV_PuzzleContinent_v30.obj').open():
    if line.startswith('v '):
        x,y,z=map(float,line.split()[1:]);v.append([x/100,-y/100,z/100])
    elif line.startswith('vt '):uv.append(list(map(float,line.split()[1:3])))
    elif line.startswith('vn '):
        x,y,z=map(float,line.split()[1:]);vn.append([x,-y,z])
    elif line.startswith('f '):f.append([int(s.split('/')[0])-1 for s in line.split()[1:]][::-1])
v=np.asarray(v);uv=np.asarray(uv);vn=np.asarray(vn);f=np.asarray(f,int)
assert len(v)==len(uv)==len(vn)
original=v.copy();nf=len(f);nv=len(v)
local=np.max(np.abs(v[:,:2]-CAP),axis=1)<1450
sel=local[f].any(axis=1);fixed=f[~sel];work=f[sel];original_work=work.copy()
for iteration in range(7):
    a=v[work];c=a[:,:,:2].mean(axis=1)
    lengths=np.linalg.norm(a[:,:,:2]-np.roll(a[:,:,:2],1,axis=1),axis=2).max(axis=1)
    mark=(np.max(np.abs(c-CAP),axis=1)<1170)&(lengths>9)
    if not mark.any():break
    edges=np.vstack([work[mark][:,[0,1]],work[mark][:,[1,2]],work[mark][:,[2,0]]]);edges=np.unique(np.sort(edges,axis=1),axis=0)
    ids=np.arange(len(v),len(v)+len(edges));lookup={tuple(e):int(i) for e,i in zip(edges,ids)}
    v=np.vstack([v,v[edges].mean(axis=1)]);uv=np.vstack([uv,uv[edges].mean(axis=1)]);nn=vn[edges].mean(axis=1);nn/=np.maximum(np.linalg.norm(nn,axis=1,keepdims=True),1e-8);vn=np.vstack([vn,nn])
    new=[]
    for face in work:
        poly=[];midpoints=[]
        for i,j in ((0,1),(1,2),(2,0)):
            poly.append(int(face[i]));mid=lookup.get(tuple(sorted((int(face[i]),int(face[j])))))
            midpoints.append(mid)
        n=sum(m is not None for m in midpoints);a,b,c=map(int,face);ab,bc,ca=midpoints
        if n==0:new.append([a,b,c])
        elif n==3:new.extend([[a,ab,ca],[ab,b,bc],[ca,bc,c],[ab,bc,ca]])
        elif n==1:
            i=next(i for i,m in enumerate(midpoints) if m is not None);aa=int(face[i]);bb=int(face[(i+1)%3]);cc=int(face[(i+2)%3]);mm=midpoints[i]
            new.extend([[aa,mm,cc],[mm,bb,cc]])
        else:
            # Rotate so the unsplit edge is A-B.
            i=next(i for i,m in enumerate(midpoints) if m is None);aa=int(face[i]);bb=int(face[(i+1)%3]);cc=int(face[(i+2)%3]);bc1=midpoints[(i+1)%3];ca1=midpoints[(i+2)%3]
            new.extend([[aa,bb,bc1],[aa,bc1,ca1],[ca1,bc1,cc]])
    work=np.array(new,int);print('refine',iteration,'local triangles',len(work),flush=True)

np.savez_compressed(OUT/'terrace_base.npz',vertices=v,uv=uv,normals=vn,fixed=fixed,work=work)
v[:,2]=planned_height(v[:,:2],v[:,2])
assert np.array_equal(v[:nv][~local],original[~local])
f=np.vstack([fixed,work]);cross=np.cross(v[work[:,1]]-v[work[:,0]],v[work[:,2]]-v[work[:,0]])
acc=np.zeros_like(v)
for i in range(3):np.add.at(acc,work[:,i],cross)
change=np.max(np.abs(v[:,:2]-CAP),axis=1)<1120
norm=np.linalg.norm(acc,axis=1);use=change&(norm>1e-8);vn[use]=acc[use]/norm[use,None]

def edge_counts(faces):
    e=np.sort(np.vstack([faces[:,[0,1]],faces[:,[1,2]],faces[:,[2,0]]]),axis=1);_,count=np.unique(e,axis=0,return_counts=True)
    return {'open':int((count==1).sum()),'nonmanifold':int((count>2).sum())}
# Local work boundary must not acquire cracks from adaptive refinement.
before=edge_counts(original_work);edges=edge_counts(work)
assert before==edges,(before,edges)
area=np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)
assert np.isfinite(v).all() and (area>1e-12).all()
name='SM_IV_Continent_GosainTerraces37'
with (OUT/(name+'.obj')).open('w') as o:
    o.write('o '+name+'\n')
    for x,y,z in v:o.write(f'v {x*100:.5f} {-y*100:.5f} {z*100:.5f}\n')
    for u,w in uv:o.write(f'vt {u:.6f} {w:.6f}\n')
    for x,y,z in vn:o.write(f'vn {x:.6f} {-y:.6f} {z:.6f}\n')
    for face in f:o.write('f '+' '.join(f'{i+1}/{i+1}/{i+1}' for i in face[::-1])+'\n')
report={'name':name,'original_vertices':nv,'vertices':len(v),'triangles':len(f),'local_triangles':len(work),'unchanged_outside_vertices':int((~local).sum()),'max_displacement_m':float(np.max(np.abs(v[:nv,2]-original[:,2]))),'local_edges':edges,'terrace_levels_relative_to_old_city_m':[1.5,7.5,14.5],'elapsed_s':time.time()-t0}
np.savez_compressed(OUT/'terrace_surface.npz',vertices=v,triangles=work)
(OUT/'terrain_report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
