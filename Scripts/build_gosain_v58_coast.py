"""Conforming shoreline subdivision with heightfield resampling, not just smooth normals."""
import json,numpy as np,shapely,time
from pathlib import Path
from scipy.spatial import cKDTree
from scipy.ndimage import map_coordinates
import gosain51_kingdom as k
from gosain_surface_sampler import Surface
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain58';assert (O/'source_complete.json').exists();(O/'source_complete.json').write_text(json.dumps({'status':'refining_coast'}))
b=np.load(O/'graded_surface.npz');v=b['vertices'].copy();f=b['triangles'].copy();uv=b['uv'].copy();normal=b['normals'].copy();original=len(v);mine=np.array([15950.,41900.]);routes=[]
for line in (B/'ArtSource/World/Gosain57/SM_Gosain57_KingdomRoutesRefined.obj').read_text().splitlines():
 if line.startswith('v '):routes.append(np.array([float(x) for x in line.split()[1:4]])*[.01,-.01,.01])
rt=cKDTree(np.array(routes)[:,:2]);fields=[np.load(O/('island_field_'+str(i)+'.npz')) for i in range(2)]
def resample(p,z):
 out=z.copy();ps=shapely.points(p)
 for i,poly in enumerate(k.POLYS):
  dist=shapely.distance(ps,poly);w=1-k.old.ease((dist-30)/150);w*=k.old.ease((shapely.distance(ps,k.TOWNS[i])-35)/110);w*=k.old.ease((shapely.distance(ps,k.LAKE)-160)/160);w*=k.old.ease((np.linalg.norm(p-mine,axis=1)-185)/110)
  for end in k.old.PLAN['bridge_endpoints_m']:w*=k.old.ease((np.linalg.norm(p-np.array(end),axis=1)-180)/140)
  d,_=rt.query(p,workers=2);w*=k.old.ease((d-12)/65);field=fields[i];target=map_coordinates(field['height'],[(p[:,1]-field['ys'][0])/8,(p[:,0]-field['xs'][0])/8],order=1,mode='nearest');out+=w*(target-out)
 return out
for iteration in range(6):
 centers=v[f].mean(axis=1);near=np.zeros(len(f),bool)
 for poly in k.POLYS:
  a,b0,c,d=poly.bounds;near|=(centers[:,0]>a-700)&(centers[:,0]<c+700)&(centers[:,1]>b0-700)&(centers[:,1]<d+700)
 ids=np.flatnonzero(near);p=v[f[ids],:2];radius=np.linalg.norm(p-centers[ids,None,:2],axis=2).max(axis=1);edge=np.linalg.norm(p-np.roll(p,-1,axis=1),axis=2).max(axis=1);dist=shapely.distance(shapely.points(centers[ids,:2]),shapely.union_all([p.boundary for p in k.POLYS]));selected=ids[(dist<radius+190)&(edge>40)]
 if not len(selected):break
 es=np.sort(np.concatenate([f[selected][:,[0,1]],f[selected][:,[1,2]],f[selected][:,[2,0]]]),axis=1);es=np.unique(es,axis=0);es=es[np.linalg.norm(v[es[:,0],:2]-v[es[:,1],:2],axis=1)>40];n=len(v);edgeids={tuple(pair):n+i for i,pair in enumerate(es)};nv=list(v[es].mean(axis=1));nu=list(uv[es].mean(axis=1));keys=es[:,0]*n+es[:,1];affected=np.zeros(len(f),bool)
 for j in range(3):
  a=f[:,j];c=f[:,(j+1)%3];affected|=np.isin(np.minimum(a,c)*n+np.maximum(a,c),keys)
 nf=[]
 for face in f[affected]:
  mids=[edgeids.get(tuple(sorted((int(a),int(c))))) for a,c in zip(face,np.roll(face,-1))];split=[j for j,x in enumerate(mids) if x is not None]
  if len(split)==1:
   j=split[0];a,b0,c=[int(face[(j+k)%3]) for k in range(3)];mid=mids[j];nf.extend([[a,mid,c],[mid,b0,c]])
  elif len(split)==2:
   j=next(j for j in range(3) if mids[j] is not None and mids[(j+1)%3] is not None);a,b0,c=[int(face[(j+k)%3]) for k in range(3)];m1=mids[j];m2=mids[(j+1)%3];nf.extend([[m1,b0,m2],[a,m1,c],[m1,m2,c]])
  else:
   a,b0,c=map(int,face);m1,m2,m3=mids;nf.extend([[a,m1,m3],[m1,b0,m2],[m3,m2,c],[m1,m2,m3]])
 nv=np.array(nv);nv[:,2]=resample(nv[:,:2],nv[:,2]);v=np.vstack([v,nv]);uv=np.vstack([uv,nu]);normal=np.vstack([normal,np.zeros_like(nv)]);f=np.vstack([f[~affected],np.array(nf,dtype=f.dtype)]);print('coast refinement',iteration+1,'added',len(nv),flush=True)
region=np.r_[b['region'],np.ones(len(v)-original,bool)];ff=f[np.any(f>=original,axis=1)];edges=np.sort(np.concatenate([ff[:,[0,1]],ff[:,[1,2]],ff[:,[2,0]]]),axis=1);edges=edges[np.any(edges>=original,axis=1)];_,counts=np.unique(edges,axis=0,return_counts=True);assert np.all(counts==2)
cross=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]);acc=np.zeros_like(v)
for j in range(3):np.add.at(acc,f[:,j],cross)
use=np.zeros(len(v),bool);use[np.unique(f[region[f].any(axis=1)])]=True;length=np.linalg.norm(acc,axis=1);use&=length>1e-12;normal[use]=acc[use]/length[use,None]
assert np.array_equal(v[:original],b['vertices']);assert np.isfinite(v).all();np.savez_compressed(O/'graded_surface.npz',vertices=v,triangles=f,uv=uv,normals=normal,region=region)
name='SM_IV_Continent_GosainRefined58'
with (O/(name+'.obj')).open('w') as out:
 out.write('o '+name+'\n')
 for p in v:out.write('v %.5f %.5f %.5f\n'%(p[0]*100,-p[1]*100,p[2]*100))
 for p in uv:out.write('vt %.6f %.6f\n'%tuple(p))
 for p in normal:out.write('vn %.6f %.6f %.6f\n'%(p[0],-p[1],p[2]))
 for face in f:out.write('f '+' '.join('%d/%d/%d'%(i+1,i+1,i+1) for i in face[::-1])+'\n')
report={'added_vertices':len(v)-original,'final_faces':len(f),'new_edge_incidence_not_two':int((counts!=2).sum()),'existing_vertices_preserved_from_smoothed_stage':True};(O/'coast_validation.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
surface=Surface(O/'graded_surface.npz')
for side in ['left','right']:
 p=O/(side+'_forest_instances.json');rows=np.array(json.loads(p.read_text()));rows[:,2]=surface.ground(rows[:,:2]);assert np.isfinite(rows).all();p.write_text(json.dumps(rows.tolist()));print(side,'forest realigned',flush=True)
(O/'source_complete.json').write_text(json.dumps({'status':'ready_for_native_import','stage':'smoothed_and_coast_refined','time':time.strftime('%Y-%m-%d %H:%M:%S')}))
