"""Sample the actual exported mainland triangles for settlement grounding."""
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
S=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource');cache=S/'civilization_terrain29_full.npz'
if not cache.exists() or cache.stat().st_mtime<(S/'SM_IV_PuzzleContinent_v29.obj').stat().st_mtime:
 v=[];faces=[]
 for line in (S/'SM_IV_PuzzleContinent_v29.obj').open():
  if line.startswith('v '):
   x,y,z=map(float,line.split()[1:]);v.append((x/100,-y/100,z/100))
  elif line.startswith('f '):faces.append([int(q.split('/')[0])-1 for q in line.split()[1:]])
 v=np.asarray(v);f=np.asarray(faces);t=v[f];c=t[:,:,:2].mean(1);keep=np.arange(len(t))>=262912;t=t[keep];np.savez(cache,tri=t.astype('float32'))
T=np.load(cache)['tri'].astype(float);C=T[:,:,:2].mean(1);tree=cKDTree(C)
def ground(x,y):
 p=np.array([x,y])
 for count in [16,96,384]:
  _,ids=tree.query(p,k=count);q=T[ids];a=q[:,0,:2];b=q[:,1,:2]-a;c=q[:,2,:2]-a;v=p-a;den=b[:,0]*c[:,1]-b[:,1]*c[:,0];safe=np.abs(den)>1e-8
  u=np.divide(v[:,0]*c[:,1]-v[:,1]*c[:,0],den,out=np.zeros_like(den),where=safe);w=np.divide(b[:,0]*v[:,1]-b[:,1]*v[:,0],den,out=np.zeros_like(den),where=safe);legal=safe&(u>=-1e-7)&(w>=-1e-7)&(u+w<=1.0000001)
  if legal.any():i=np.where(legal)[0][0];return float(q[i,0,2]+u[i]*(q[i,1,2]-q[i,0,2])+w[i]*(q[i,2,2]-q[i,0,2]))
 raise ValueError(('terrain lookup failed',x,y))
