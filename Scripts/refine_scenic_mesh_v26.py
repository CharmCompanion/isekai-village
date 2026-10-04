import numpy as np
from scipy.ndimage import map_coordinates
from pathlib import Path

def refine(V,F,outside):
 data=np.load(Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource/world_reference_v26.npz'))
 cx=float(data['cx']);cy=float(data['cy']);m=float(data['mpp'])
 V=np.asarray(V,dtype=float);F=np.asarray(F,dtype=np.int64)
 for pass_index in range(2):
  edges=np.concatenate([F[:,[0,1]],F[:,[1,2]],F[:,[2,0]]]);edges.sort(axis=1)
  edges,inverse=np.unique(edges,axis=0,return_inverse=True)
  mid=(V[edges[:,0],:2]+V[edges[:,1],:2])*.5
  lengths=np.linalg.norm(V[edges[:,0],:2]-V[edges[:,1],:2],axis=1)
  coords=[cy-mid[:,1]/m,cx-mid[:,0]/m]
  coast=map_coordinates(data['coast'],coords,order=1,mode='constant',cval=-100000.)
  cliff=map_coordinates(data['cliff'],coords,order=1,mode='constant')
  mountain=map_coordinates(data['mountain'],coords,order=1,mode='constant')
  chosen=(np.linalg.norm(mid,axis=1)>19000)&(((np.abs(coast)<(850+lengths*.5))&(lengths>180))|((cliff>.08)&(lengths>120))|((mountain>.3)&(lengths>380)))
  edge_ids=np.full(len(edges),-1,dtype=np.int64);edge_ids[chosen]=np.arange(chosen.sum())+len(V)
  p=mid[chosen];z,_=outside(p[:,0],p[:,1]);extra=np.column_stack([p,z])
  triangle_mids=edge_ids[inverse].reshape(3,-1).T
  changed=np.where((triangle_mids>=0).any(axis=1))[0]
  kept=F[(triangle_mids<0).all(axis=1)]
  # Preserve original face ordering (including the paired cavity) for validation.
  parts=[];centers=V[F[changed]].mean(axis=1);centers[:,2]=outside(centers[:,0],centers[:,1])[0]
  centroid_base=len(V)+len(extra)
  changed_map={int(k):j for j,k in enumerate(changed)}
  for i,face in enumerate(F):
   j=changed_map.get(i)
   if j is None:parts.append(tuple(face));continue
   boundary=[]
   for k in range(3):
    boundary.append(int(face[k]))
    if triangle_mids[i,k]>=0:boundary.append(int(triangle_mids[i,k]))
   c=centroid_base+j
   for k in range(len(boundary)):parts.append((boundary[k],boundary[(k+1)%len(boundary)],c))
  V=np.concatenate([V,extra,centers]);F=np.asarray(parts,dtype=np.int64)
  print({'refinement_pass':pass_index+1,'split_edges':int(chosen.sum()),'vertices':len(V),'triangles':len(F)},flush=True)
 return V,F
