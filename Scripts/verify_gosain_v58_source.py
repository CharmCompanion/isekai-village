"""Check the delivered source, not an intermediate smoothing stage."""
import json,numpy as np,shapely
from pathlib import Path
import gosain51_kingdom as k
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain58'
old=np.load(B/'ArtSource/World/Gosain57/graded_surface.npz')['vertices'];new=np.load(O/'graded_surface.npz');v=new['vertices'];f=new['triangles'];n=len(old)
outside=~shapely.dwithin(shapely.points(old[:,:2]),shapely.union_all(k.POLYS),180)
town=shapely.contains(shapely.union_all(k.TOWNS),shapely.points(old[:,:2]));mine=np.linalg.norm(old[:,:2]-[15950.,41900.],axis=1)<185
out={'vertices':len(v),'faces':len(f),'outside_gosain_original_vertices_identical':bool(np.array_equal(old[outside],v[:n][outside])),'town_original_vertices_identical':bool(np.array_equal(old[town],v[:n][town])),'mine_original_vertices_identical':bool(np.array_equal(old[mine],v[:n][mine])),'finite_terrain':bool(np.isfinite(v).all() and np.isfinite(new['normals']).all())}
assert all(out[x] for x in ['outside_gosain_original_vertices_identical','town_original_vertices_identical','mine_original_vertices_identical','finite_terrain'])
del old,new,v,f
def mesh(path):
 v=[];f=[]
 for line in path.read_text().splitlines():
  if line.startswith('v '):v.append(list(map(float,line.split()[1:])))
  elif line.startswith('f '):f.append([int(x.split('/')[0])-1 for x in line.split()[1:]])
 return np.array(v),np.array(f)
v,f=mesh(O/'SM_Gosain58_ContinuousRoutes.obj');cross=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]])
out['road_degenerate_faces']=int((np.linalg.norm(cross,axis=1)<1e-6).sum());assert out['road_degenerate_faces']==0
edges=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),axis=1);_,counts=np.unique(edges,axis=0,return_counts=True);out['road_nonmanifold_edges']=int((counts>2).sum());assert out['road_nonmanifold_edges']==0
v,f=mesh(B/'ArtSource/World/Gosain57/SM_Gosain57_MineLandformFinal.obj');edges=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),axis=1);_,counts=np.unique(edges,axis=0,return_counts=True)
out['final_mine_vertices']=len(v);out['final_mine_faces']=len(f);out['final_mine_edges_not_two']=int((counts!=2).sum());assert out['final_mine_edges_not_two']==0
(O/'source_verification.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
