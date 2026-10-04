"""Fit road triangles to actual terrain creases, avoiding intermittent buried strips."""
from pathlib import Path
import numpy as np,json
from civilization_ground_v30 import ground,tree,T
S=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource');path=S/'Civilizations30/SM_Civ30_Roads.obj';v=[];f=[];mats=[];mat='path'
for l in path.open():
 if l.startswith('v '):x,y,z=map(float,l.split()[1:]);v.append([x/100,-y/100,z/100])
 elif l.startswith('usemtl '):mat=l.split()[1]
 elif l.startswith('f '):f.append([int(q.split('/')[0])-1 for q in l.split()[1:]]);mats.append(mat)
v=np.array(v);f=np.array(f);mats=np.array(mats)
def heights(points):
 out=[]
 for start in range(0,len(points),6000):
  p=points[start:start+6000];_,ids=tree.query(p,k=16);q=T[ids];a=q[:,:,0,:2];b=q[:,:,1,:2]-a;c=q[:,:,2,:2]-a;delta=p[:,None]-a;den=b[:,:,0]*c[:,:,1]-b[:,:,1]*c[:,:,0];safe=np.abs(den)>1e-8
  u=np.divide(delta[:,:,0]*c[:,:,1]-delta[:,:,1]*c[:,:,0],den,out=np.zeros_like(den),where=safe);w=np.divide(b[:,:,0]*delta[:,:,1]-b[:,:,1]*delta[:,:,0],den,out=np.zeros_like(den),where=safe);ok=safe&(u>=-1e-6)&(w>=-1e-6)&(u+w<=1.000001);ix=ok.argmax(1);ar=np.arange(len(p));z=q[ar,ix,0,2]+u[ar,ix]*(q[ar,ix,1,2]-q[ar,ix,0,2])+w[ar,ix]*(q[ar,ix,2,2]-q[ar,ix,0,2])
  for k in np.where(~ok.any(1))[0]:z[k]=ground(*p[k])
  out.extend(z)
 return np.array(out)
for iteration in range(8):
 ids=np.where(np.isin(mats,['path','conduit']))[0];q=v[f[ids]];checks=np.stack([(q[:,0]+q[:,1])*.5,(q[:,1]+q[:,2])*.5,(q[:,2]+q[:,0])*.5,q.mean(1)],axis=1);expected=heights(checks[:,:,:2].reshape(-1,2)).reshape(-1,4)+.35;error=np.max(np.abs(checks[:,:,2]-expected),axis=1);chosen=ids[error>.16]
 print({'road_refinement':iteration+1,'triangles_refined':len(chosen),'max_error_m':float(error.max())},flush=True)
 if not len(chosen):break
 extra=(v[f[chosen]][:,[0,1,2]]+v[f[chosen]][:,[1,2,0]])*.5;extra[:,:,2]=heights(extra[:,:,:2].reshape(-1,2)).reshape(-1,3)+.35;newids=np.arange(len(v),len(v)+len(chosen)*3).reshape(-1,3);old=f[chosen];a,b,c=old.T;ab,bc,ca=newids.T
 new=np.stack([np.column_stack([a,ab,ca]),np.column_stack([ab,b,bc]),np.column_stack([ca,bc,c]),np.column_stack([ab,bc,ca])],axis=1).reshape(-1,3);keep=np.ones(len(f),bool);keep[chosen]=False;v=np.vstack([v,extra.reshape(-1,3)]);f=np.vstack([f[keep],new]);mats=np.r_[mats[keep],np.repeat(mats[chosen],4)]
used=np.unique(f);lookup=np.full(len(v),-1);lookup[used]=np.arange(len(used));f=lookup[f];v=v[used];normal=np.zeros_like(v);cross=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]])
for k in range(3):np.add.at(normal,f[:,k],cross)
normal/=np.maximum(np.linalg.norm(normal,axis=1,keepdims=True),1e-9)
with path.open('w') as out:
 out.write('o SM_Civ30_Roads\n')
 for x,y,z in v:out.write(f'v {x*100:.5f} {-y*100:.5f} {z*100:.5f}\n')
 for x,y,z in v:out.write(f'vt {x/12:.6f} {z/12:.6f}\n')
 for x,y,z in normal:out.write(f'vn {x:.6f} {-y:.6f} {z:.6f}\n')
 last=None
 for face,mat in zip(f,mats):
  if mat!=last:out.write('usemtl '+mat+'\n');last=mat
  out.write('f '+' '.join(f'{i+1}/{i+1}/{i+1}' for i in face[::-1])+'\n')
manifest=json.loads((S/'Civilizations30/assets.json').read_text())
for q in manifest:
 if q['name']=='SM_Civ30_Roads':q.update(vertices=len(v),triangles=len(f),materials=sorted(set(mats.tolist())))
(S/'Civilizations30/assets.json').write_text(json.dumps(manifest,indent=2));print({'finished_road_vertices':len(v),'triangles':len(f)},flush=True)


