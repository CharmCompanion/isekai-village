"""Conforming local terrain refinement around Gosain's lake; outside geometry retained."""
import sys,json,time,numpy as np,shapely
from pathlib import Path
import gosain51_kingdom as k
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain53';O.mkdir(exist_ok=True)
b=np.load(B/'ArtSource/World/Gosain51/graded_surface.npz');base=np.load(B/'ArtSource/World/Gosain37/terrace_base.npz');v=b['vertices'].copy();f=b['triangles'].copy();uv=base['uv'].copy();original_count=len(v)
# Edges are split once globally, then both adjacent faces use the same midpoint.
# Faces with one or two split edges are fan triangulated as well: no T junctions.
for iteration in range(2):
 centers=v[f].mean(axis=1);selected=shapely.dwithin(shapely.points(centers[:,:2]),k.LAKE,460)
 edges=set()
 for face in f[selected]:
  for a,c in zip(face,np.roll(face,-1)):edges.add(tuple(sorted((int(a),int(c)))))
 edgeids={};nv=[];nu=[]
 for edge in sorted(edges):
  a,c=edge;edgeids[edge]=len(v)+len(nv);nv.append((v[a]+v[c])/2);nu.append((uv[a]+uv[c])/2)
 # Vectorized edge membership avoids a Python loop over all continent faces.
 edgearray=np.array(sorted(edges),dtype=np.int64);keys=edgearray[:,0]*len(v)+edgearray[:,1];affected=np.zeros(len(f),bool)
 for j in range(3):
  a=f[:,j];c=f[:,(j+1)%3];key=np.minimum(a,c)*len(v)+np.maximum(a,c);affected|=np.isin(key,keys)
 newfaces=[]
 for face in f[affected]:
  ring=[]
  for a,c in zip(face,np.roll(face,-1)):
   ring.append(int(a));mid=edgeids.get(tuple(sorted((int(a),int(c)))))
   if mid is not None:ring.append(mid)
  center=len(v)+len(nv);nv.append(v[face].mean(axis=0));nu.append(uv[face].mean(axis=0))
  newfaces.extend([[center,a,c] for a,c in zip(ring,ring[1:]+ring[:1])])
 nv=np.array(nv);raw=k.old.planned(nv[:,:2],np.full(len(nv),k.SEA));distance=shapely.distance(shapely.points(nv[:,:2]),k.LAKE)
 weight=(1-k.old.ease((distance-280)/140))*shapely.contains(k.POLYS[0],shapely.points(nv[:,:2]))
 nv[:,2]=nv[:,2]*(1-weight)+k.heights(nv[:,:2],raw)*weight
 v=np.vstack([v,nv]);uv=np.vstack([uv,np.array(nu)]);f=np.vstack([f[~affected],np.array(newfaces,dtype=f.dtype)])
 print('refinement',iteration+1,'added',len(nv),'vertices',flush=True)
assert np.array_equal(v[:original_count],b['vertices']);assert np.isfinite(v).all()
region=np.r_[b['region']|np.load(B/'ArtSource/World/Gosain44/graded_surface.npz')['region']|np.load(B/'ArtSource/World/Gosain43/graded_surface.npz')['region'],np.ones(len(v)-original_count,dtype=bool)]
normal=np.vstack([base['normals'],np.zeros((len(v)-original_count,3))]);ff=f[region[f].any(axis=1)];cross=np.cross(v[ff[:,1]]-v[ff[:,0]],v[ff[:,2]]-v[ff[:,0]]);acc=np.zeros_like(v)
for j in range(3):np.add.at(acc,ff[:,j],cross)
l=np.linalg.norm(acc,axis=1);use=region&(l>1e-12);normal[use]=acc[use]/l[use,None]
name='SM_IV_Continent_GosainLake53';np.savez_compressed(O/'graded_surface.npz',vertices=v,triangles=f,region=region)
with (O/(name+'.obj')).open('w') as out:
 out.write('o '+name+'\n')
 for p in v:out.write('v %.5f %.5f %.5f\n'%(p[0]*100,-p[1]*100,p[2]*100))
 for p in uv:out.write('vt %.6f %.6f\n'%tuple(p))
 for p in normal:out.write('vn %.6f %.6f %.6f\n'%(p[0],-p[1],p[2]))
 for face in f:out.write('f '+' '.join('%d/%d/%d'%(i+1,i+1,i+1) for i in face[::-1])+'\n')
(O/'validation.json').write_text(json.dumps({'original_vertices_unchanged':True,'added_local_vertices':len(v)-original_count,'faces':len(f),'purpose':'Remove coarse lake-bank facets with shared-edge subdivision; native review required'},indent=2));print('source ready',flush=True)
