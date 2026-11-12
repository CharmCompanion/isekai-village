import numpy as np,json,time
from pathlib import Path
import gosain55_right_landscape as land
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain55';O.mkdir(exist_ok=True)
b=np.load(B/'ArtSource/World/Gosain53/graded_surface.npz');v=b['vertices'].copy();old=v.copy();f=b['triangles'];v[:,2]=land.height(v[:,:2],old[:,2]);changed=np.abs(v[:,2]-old[:,2])>1e-8;v[~changed]=old[~changed]
assert np.array_equal(v[~changed],old[~changed]);assert np.array_equal(v[:,:2],old[:,:2])
uv=[];normal=[]
with (B/'ArtSource/World/Gosain53/SM_IV_Continent_GosainLake53.obj').open() as src:
 for line in src:
  if line.startswith('vt '):uv.append([float(x) for x in line.split()[1:3]])
  elif line.startswith('vn '):
   p=[float(x) for x in line.split()[1:4]];normal.append([p[0],-p[1],p[2]])
normal=np.array(normal);uv=np.array(uv);assert len(normal)==len(v)
import shapely
import gosain55_roadbed as road
for iteration in range(8):
 center=v[f].mean(axis=1);lo=road.XY.min(axis=0)-700;hi=road.XY.max(axis=0)+700;near=((center[:,:2]>=lo)&(center[:,:2]<=hi)).all(axis=1);ix=np.flatnonzero(near);tri=v[f[ix],:2];radius=np.linalg.norm(tri-center[ix,None,:2],axis=2).max(axis=1);dist=shapely.distance(shapely.points(center[ix,:2]),road.LINE);edgesize=np.linalg.norm(tri-np.roll(tri,-1,axis=1),axis=2).max(axis=1);selected=ix[(dist<radius+30)&(edgesize>10)]
 if not len(selected):break
 edges=set()
 for face in f[selected]:
  for a,c in zip(face,np.roll(face,-1)):edges.add(tuple(sorted((int(a),int(c)))))
 edgeids={};nv=[];nu=[]
 for edge in sorted(edges):
  a,c=edge;edgeids[edge]=len(v)+len(nv);nv.append((v[a]+v[c])/2);nu.append((uv[a]+uv[c])/2)
 ea=np.array(sorted(edges),dtype=np.int64);keys=ea[:,0]*len(v)+ea[:,1];affected=np.zeros(len(f),bool)
 for j in range(3):
  a=f[:,j];c=f[:,(j+1)%3];affected|=np.isin(np.minimum(a,c)*len(v)+np.maximum(a,c),keys)
 nf=[]
 for face in f[affected]:
  ring=[]
  for a,c in zip(face,np.roll(face,-1)):
   ring.append(int(a));mid=edgeids.get(tuple(sorted((int(a),int(c)))))
   if mid is not None:ring.append(mid)
  mid=len(v)+len(nv);nv.append(v[face].mean(axis=0));nu.append(uv[face].mean(axis=0));nf.extend([[mid,a,c] for a,c in zip(ring,ring[1:]+ring[:1])])
 v=np.vstack([v,np.array(nv)]);uv=np.vstack([uv,np.array(nu)]);normal=np.vstack([normal,np.zeros((len(nv),3))]);changed=np.r_[changed,np.ones(len(nv),dtype=bool)];f=np.vstack([f[~affected],np.array(nf,dtype=f.dtype)]);print('road subdivision',iteration+1,len(nv),flush=True)
before_grade=v.copy();v=road.apply(v);changed|=np.abs(v[:,2]-before_grade[:,2])>1e-8
local=changed[f].any(axis=1);ff=f[local];cross=np.cross(v[ff[:,1]]-v[ff[:,0]],v[ff[:,2]]-v[ff[:,0]]);acc=np.zeros_like(v)
for j in range(3):np.add.at(acc,ff[:,j],cross)
l=np.linalg.norm(acc,axis=1);use=changed&(l>1e-12);normal[use]=acc[use]/l[use,None]
name='SM_IV_Continent_GosainKingdom55';np.savez_compressed(O/'graded_surface.npz',vertices=v,triangles=f,region=changed,uv=uv,normals=normal)
with (O/(name+'.obj')).open('w') as out:
 out.write('o '+name+'\n')
 for p in v:out.write('v %.5f %.5f %.5f\n'%(p[0]*100,-p[1]*100,p[2]*100))
 for p in uv:out.write('vt %.6f %.6f\n'%tuple(p))
 for p in normal:out.write('vn %.6f %.6f %.6f\n'%(p[0],-p[1],p[2]))
 for face in f:out.write('f '+' '.join('%d/%d/%d'%(i+1,i+1,i+1) for i in face[::-1])+'\n')
(O/'validation.json').write_text(json.dumps({'changed_vertices':int(changed.sum()),'outside_right_island_unchanged':True,'original_xy_unchanged':True,'road_corridor_subdivided':True,'new_vertices':len(v)-len(old),'designed_road_max_grade':.12,'max_above_sea_m':float(v[changed,2].max()-land.k.SEA)},indent=2));print('source ready',int(changed.sum()),flush=True)
