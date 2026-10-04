from pathlib import Path
import numpy as np,json
from scipy.sparse import coo_matrix
S=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource')
v=[];uv=[];faces=[]
for line in (S/'SM_IV_JoinedMountain_v13.obj').open():
 if line.startswith('v '):v.append(list(map(float,line.split()[1:])))
 elif line.startswith('vt '):uv.append(list(map(float,line.split()[1:])))
 elif line.startswith('f '):faces.append([int(x.split('/')[0])-1 for x in line.split()[1:]])
v=np.array(v);original=v.copy();faces=np.array(faces)
ij=np.concatenate([faces[:,[0,1]],faces[:,[1,2]],faces[:,[2,0]]]);ij=np.unique(np.concatenate([ij,ij[:,::-1]]),axis=0)
adj=coo_matrix((np.ones(len(ij)),(ij[:,0],ij[:,1])),shape=(len(v),len(v))).tocsr();deg=np.maximum(np.asarray(adj.sum(axis=1)),1)
# Lock the complete overlapping landscape join; relax only internal rock faces.
weight=np.ones((len(v),1));weight[:8192]=0;weight[-1]=0
for start,count,w in [(8192,2048,.05),(10240,1024,.20),(11264,512,.45),(11776,256,.65)]:weight[start:start+count]=w
for _ in range(24):
 for strength in [.43,-.45]:v+=strength*weight*(adj@v/deg-v)
assert np.array_equal(v[:8192],original[:8192])
# Smooth area-weighted normals on the same refined paired geometry.
norm=np.zeros_like(v);cross=np.cross(v[faces[:,1]]-v[faces[:,0]],v[faces[:,2]]-v[faces[:,0]])
for k in range(3):np.add.at(norm,faces[:,k],cross)
norm/=np.maximum(np.linalg.norm(norm,axis=1,keepdims=True),1e-12)
with (S/'SM_IV_JoinedMountain_v21.obj').open('w') as f:
 f.write('o SM_IV_JoinedMountain_v21\n')
 for row in v:f.write('v '+' '.join(f'{x:.5f}' for x in row)+'\n')
 for row in uv:f.write('vt '+' '.join(f'{x:.6f}' for x in row)+'\n')
 for row in norm:f.write('vn '+' '.join(f'{x:.7f}' for x in row)+'\n')
 for face in faces:f.write('f '+' '.join(f'{i+1}/{i+1}/{i+1}' for i in face)+'\n')
report={'join_vertices_locked':8192,'max_internal_adjustment_m':float(np.linalg.norm(v-original,axis=1).max()/100),'rms_adjustment_m':float(np.sqrt(np.mean(np.sum((v-original)**2,axis=1)))/100),'playable_landscape_unchanged':True}
(S/'paired_refinement_v21.json').write_text(json.dumps(report,indent=2));print(report)
