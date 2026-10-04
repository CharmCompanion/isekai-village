from pathlib import Path
import numpy as np,json
from scipy.sparse import coo_matrix
S=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource');v=[];uv=[];f=[]
for line in (S/'SM_IV_JoinedMountain_v21.obj').open():
 if line.startswith('v '):v.append(list(map(float,line.split()[1:4])))
 elif line.startswith('vt '):uv.append(list(map(float,line.split()[1:3])))
 elif line.startswith('f '):f.append([int(q.split('/')[0])-1 for q in line.split()[1:4]])
v=np.array(v);uv=np.array(uv);f=np.array(f);old=v.copy();old_count=len(v)
weights=np.ones(len(v));weights[:8192]=0;weights[8192:10240]=.08;weights[10240:11264]=.30;weights[-1]=0
edges=np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]);edges.sort(axis=1);edges,inv=np.unique(edges,axis=0,return_inverse=True)
select=(weights[edges].max(axis=1)>0)&(edges.min(axis=1)>=8192)
ids=np.full(len(edges),-1,dtype=int);ids[select]=np.arange(select.sum())+len(v)
mid_v=v[edges[select]].mean(axis=1);mid_uv=uv[edges[select]].mean(axis=1);mid_w=weights[edges[select]].mean(axis=1)
fm=ids[inv].reshape(3,-1).T;changed=np.where((fm>=0).any(axis=1))[0];center_v=v[f[changed]].mean(axis=1);center_uv=uv[f[changed]].mean(axis=1);center_w=weights[f[changed]].mean(axis=1)
centerbase=len(v)+len(mid_v);lookup={int(i):j for j,i in enumerate(changed)};nf=[]
for i,face in enumerate(f):
 if i not in lookup:nf.append(face);continue
 boundary=[]
 for k in range(3):
  boundary.append(face[k])
  if fm[i,k]>=0:boundary.append(fm[i,k])
 c=centerbase+lookup[i]
 for k in range(len(boundary)):nf.append([boundary[k],boundary[(k+1)%len(boundary)],c])
v=np.concatenate([v,mid_v,center_v]);uv=np.concatenate([uv,mid_uv,center_uv]);weights=np.r_[weights,mid_w,center_w][:,None];f=np.array(nf);reference=v.copy()
edges=np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]);edges=np.unique(np.concatenate([edges,edges[:,::-1]]),axis=0);adj=coo_matrix((np.ones(len(edges)),(edges[:,0],edges[:,1])),shape=(len(v),len(v))).tocsr();deg=np.maximum(np.asarray(adj.sum(axis=1)),1)
for _ in range(22):
 for strength in [.48,-.49]:v+=strength*weights*(adj@v/deg-v)
# A few positive relaxation steps round former polygon junctions.
for _ in range(5):v+=.24*weights*(adj@v/deg-v)
assert np.array_equal(v[:8192],old[:8192])
n=np.zeros_like(v);cross=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]])
for k in range(3):np.add.at(n,f[:,k],cross)
n/=np.maximum(np.linalg.norm(n,axis=1,keepdims=True),1e-12)
with (S/'SM_IV_JoinedMountain_v28.obj').open('w') as out:
 out.write('o SM_IV_JoinedMountain_v28\n')
 for q in v:out.write('v '+' '.join(f'{x:.5f}' for x in q)+'\n')
 for q in uv:out.write('vt '+' '.join(f'{x:.7f}' for x in q)+'\n')
 for q in n:out.write('vn '+' '.join(f'{x:.7f}' for x in q)+'\n')
 for face in f:out.write('f '+' '.join(f'{i+1}/{i+1}/{i+1}' for i in face)+'\n')
report={'vertices':len(v),'triangles':len(f),'locked_join_vertices':8192,'landscape_unchanged':True,'maximum_surface_relaxation_m':float(np.linalg.norm(v-reference,axis=1).max()/100),'source_version':21}
(S/'paired_refinement_v28.json').write_text(json.dumps(report,indent=2));print(report)
