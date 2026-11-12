"""Repair protected-area normals and join existing road ribbons; do not relocate routes."""
import json,time,numpy as np,shapely
from pathlib import Path
from collections import defaultdict
import gosain51_kingdom as k
from gosain_surface_sampler import Surface
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain58'
assert not (O/'applied.json').exists()
assert json.loads((O/'source_complete.json').read_text())['stage']=='smoothed_and_coast_refined'
(O/'source_complete.json').write_text(json.dumps({'status':'finishing_surface'}))
b=np.load(O/'graded_surface.npz');v=b['vertices'];f=b['triangles'];uv=b['uv'];norm=b['normals'].copy()
use=shapely.dwithin(shapely.points(v[:,:2]),shapely.union_all(k.POLYS),180)
cross=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]);acc=np.zeros_like(v)
for j in range(3):np.add.at(acc,f[:,j],cross)
length=np.linalg.norm(acc,axis=1);use&=length>1e-12;new=acc[use]/length[use,None]
angle=np.degrees(np.arccos(np.clip(np.einsum('ij,ij->i',norm[use],new),-1,1)))
norm[use]=new
np.savez_compressed(O/'graded_surface.npz',vertices=v,triangles=f,uv=uv,normals=norm,region=b['region'])
name='SM_IV_Continent_GosainRefined58'
with (O/(name+'.obj')).open('w') as out:
 out.write('o '+name+'\n')
 for p in v:out.write('v %.5f %.5f %.5f\n'%(p[0]*100,-p[1]*100,p[2]*100))
 for p in uv:out.write('vt %.6f %.6f\n'%tuple(p))
 for p in norm:out.write('vn %.6f %.6f %.6f\n'%(p[0],-p[1],p[2]))
 for face in f:out.write('f '+' '.join('%d/%d/%d'%(i+1,i+1,i+1) for i in face[::-1])+'\n')
print('All Gosain surface normals repaired',flush=True)
report={'recomputed_normals':int(use.sum()),'normals_changed_over_one_degree':int((angle>1).sum()),'max_normal_correction_degrees':float(angle.max())}
del acc,cross,b,v,f,norm,uv
# Each original quad is one road segment. Shared center sections preserve path layout.
verts=[];face_mats={};mat='';face_ids=[]
for line in (B/'ArtSource/World/Gosain57/SM_Gosain57_KingdomRoutesRefined.obj').read_text().splitlines():
 if line.startswith('v '):verts.append(np.array(list(map(float,line.split()[1:])))*[.01,-.01,.01])
 elif line.startswith('usemtl '):mat=line.split()[1]
 elif line.startswith('f '):
  ids=[int(q.split('/')[0])-1 for q in line.split()[1:]];quad=ids[0]//4;assert all(i//4==quad for i in ids);face_mats[quad]=mat;face_ids.append(ids)
v=np.array(verts);quadids=sorted(face_mats);quads={i:v[i*4:i*4+4,:2].copy() for i in quadids};ends=defaultdict(list)
for i,q in quads.items():
 for indices in [(0,1),(3,2)]:
  ends[tuple(np.round(q[list(indices)].mean(axis=0),3))].append((i,indices))
joined=0;max_shift=0.
for refs in ends.values():
 if len(refs)<2:continue
 assert len(refs)==2,refs
 a,ia=refs[0];c,ic=refs[1];pa=quads[a][list(ia)];pc=quads[c][list(ic)]
 if np.linalg.norm(pa[0]-pc[1])<np.linalg.norm(pa[0]-pc[0]):ic=ic[::-1];pc=pc[::-1]
 mid=(pa+pc)*.5;max_shift=max(max_shift,float(np.linalg.norm(mid-pa,axis=1).max()));quads[a][list(ia)]=mid;quads[c][list(ic)]=mid;joined+=1
rv=[];rf=[];rm=[]
for i,q in quads.items():
 start=(q[0]+q[1])*.5;end=(q[3]+q[2])*.5;n=max(2,int(np.ceil(np.linalg.norm(end-start)/2))+1);width=4;offset=len(rv)
 for t in np.linspace(0,1,n):
  left=q[0]*(1-t)+q[3]*t;right=q[1]*(1-t)+q[2]*t
  for u in np.linspace(0,1,width+1):rv.append(left*(1-u)+right*u)
 for j in range(n-1):
  for h in range(width):
   a=offset+j*(width+1)+h;c=a+width+1;rf.extend([[a,a+1,c+1],[a,c+1,c]]);rm.extend([face_mats[i]]*2)
rv=np.array(rv);unique,inv=np.unique(np.round(rv,5),axis=0,return_inverse=True);rf=inv[np.array(rf)];surface=Surface(O/'graded_surface.npz');z=surface.ground(unique)+.15;rv=np.c_[unique,z]
cross=np.cross(rv[rf[:,1]]-rv[rf[:,0]],rv[rf[:,2]]-rv[rf[:,0]]);reverse=cross[:,2]<0;rf[reverse]=rf[reverse,::-1]
cross=np.cross(rv[rf[:,1]]-rv[rf[:,0]],rv[rf[:,2]]-rv[rf[:,0]]);rn=np.zeros_like(rv)
for j in range(3):np.add.at(rn,rf[:,j],cross)
rn/=np.maximum(np.linalg.norm(rn,axis=1)[:,None],1e-12)
name='SM_Gosain58_ContinuousRoutes'
with (O/(name+'.obj')).open('w') as out:
 out.write('o '+name+'\n')
 for p in rv:out.write('v %.5f %.5f %.5f\n'%(p[0]*100,-p[1]*100,p[2]*100))
 for p in rn:out.write('vn %.6f %.6f %.6f\n'%(p[0],-p[1],p[2]))
 current=None
 for face,mat in zip(rf,rm):
  if mat!=current:out.write('usemtl '+mat+'\n');current=mat
  out.write('f '+' '.join('%d//%d'%(j+1,j+1) for j in face[::-1])+'\n')
assert np.isfinite(rv).all();report.update({'road_vertices':len(rv),'road_triangles':len(rf),'joined_cross_sections':joined,'max_lateral_join_adjustment_m':max_shift,'road_clearance_m':.15,'road_segment_count':len(quads),'retained_original_segment_count':len(face_mats),'road_materials':sorted(set(rm))})
(O/'surface_finish_validation.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
(O/'source_complete.json').write_text(json.dumps({'status':'ready_for_native_import','stage':'coast_normals_and_roads_finished','time':time.strftime('%Y-%m-%d %H:%M:%S')}))
