from pathlib import Path
import numpy as np
from scipy.sparse import coo_matrix
p=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource/SM_IV_PuzzleContinent_v26.obj');v=[];norm=[];faces=[]
for line in p.open():
 if line.startswith('v '):v.append([float(q) for q in line.split()[1:4]])
 elif line.startswith('vn '):norm.append([float(q) for q in line.split()[1:4]])
 elif line.startswith('f '):faces.append([int(q.split('/')[0])-1 for q in line.split()[1:4]])
v=np.asarray(v);n=np.asarray(norm);f=np.asarray(faces);edges=np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]);edges=np.concatenate([edges,edges[:,::-1]])
dots=np.einsum('ij,ij->i',n[edges[:,0]],n[edges[:,1]]);w=np.clip((dots-.55)/.45,0,1)**2;a=coo_matrix((w,(edges[:,0],edges[:,1])),shape=(len(n),len(n))).tocsr();deg=np.maximum(np.asarray(a.sum(axis=1)),1e-8);mask=np.linalg.norm(v[:,:2],axis=1)>1900000
original=n.copy()
for _ in range(5):
 avg=a@n/deg;n[mask]=.35*n[mask]+.65*avg[mask];n/=np.maximum(np.linalg.norm(n,axis=1,keepdims=True),1e-10)
n[~mask]=original[~mask]
tmp=p.with_suffix('.polished.obj');i=0
with tmp.open('w') as out:
 for line in p.open():
  if line.startswith('vn '):out.write('vn '+' '.join(f'{x:.7f}' for x in n[i])+'\n');i+=1
  else:out.write(line)
tmp.replace(p);print({'scenic_normals_smoothed':int(mask.sum()),'geometry_changed':False,'cavity_normals_unchanged':True})
