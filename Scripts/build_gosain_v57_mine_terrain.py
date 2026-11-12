import numpy as np,json
from pathlib import Path
import gosain57_mine as m
B=m.B;O=m.O;b=np.load(B/'ArtSource/World/Gosain56/graded_surface.npz');v=b['vertices'].copy();old=v.copy();f=b['triangles'];uv=b['uv'];normal=b['normals'].copy();original_count=len(v)
# Shared-edge refinement in the excavation only; original distant terrain is retained.
for it in range(6):
 c=v[f].mean(axis=1);near=np.linalg.norm(c[:,:2]-m.C,axis=1)<250;ids=np.flatnonzero(near);t=v[f[ids],:2];rad=np.linalg.norm(t-c[ids,None,:2],axis=2).max(axis=1);d,l=m.local(c[ids,:2]);edgesize=np.linalg.norm(t-np.roll(t,-1,axis=1),axis=2).max(axis=1);sel=ids[(d+rad>14)&(d-rad<116)&(abs(l)<rad+23)&(edgesize>3)]
 if not len(sel):break
 edges=set()
 for face in f[sel]:
  for a,b0 in zip(face,np.roll(face,-1)):edges.add(tuple(sorted((int(a),int(b0)))))
 edgeids={};nv=[];nu=[]
 for a,b0 in sorted(edges):edgeids[(a,b0)]=len(v)+len(nv);nv.append((v[a]+v[b0])/2);nu.append((uv[a]+uv[b0])/2)
 e=np.array(sorted(edges));keys=e[:,0]*len(v)+e[:,1];aff=np.zeros(len(f),bool)
 for j in range(3):
  a=f[:,j];b0=f[:,(j+1)%3];aff|=np.isin(np.minimum(a,b0)*len(v)+np.maximum(a,b0),keys)
 nf=[]
 for face in f[aff]:
  ring=[]
  for a,b0 in zip(face,np.roll(face,-1)):
   ring.append(int(a));mid=edgeids.get(tuple(sorted((int(a),int(b0)))))
   if mid is not None:ring.append(mid)
  mid=len(v)+len(nv);nv.append(v[face].mean(axis=0));nu.append(uv[face].mean(axis=0));nf.extend([[mid,a,b0] for a,b0 in zip(ring,ring[1:]+ring[:1])])
 v=np.vstack([v,nv]);uv=np.vstack([uv,nu]);normal=np.vstack([normal,np.zeros((len(nv),3))]);f=np.vstack([f[~aff],nf]);print('mine refinement',it+1,len(nv),flush=True)
local=np.linalg.norm(v[:,:2]-m.C,axis=1)<170;ix=np.flatnonzero(local);v[ix,2]=m.shape(v[ix,:2],v[ix,2]);changed=np.r_[np.abs(v[:original_count,2]-old[:,2])>1e-8,np.ones(len(v)-original_count,bool)];v[:original_count][~changed[:original_count]]=old[~changed[:original_count]]
ff=f[changed[f].any(axis=1)];cross=np.cross(v[ff[:,1]]-v[ff[:,0]],v[ff[:,2]]-v[ff[:,0]]);acc=np.zeros_like(v)
for j in range(3):np.add.at(acc,ff[:,j],cross)
l=np.linalg.norm(acc,axis=1);use=changed&(l>1e-12);normal[use]=acc[use]/l[use,None]
assert np.array_equal(v[:original_count][~changed[:original_count]],old[~changed[:original_count]]);assert np.isfinite(v).all();np.savez_compressed(O/'graded_surface.npz',vertices=v,triangles=f,uv=uv,normals=normal,region=changed)
name='SM_IV_Continent_GosainMine57'
with (O/(name+'.obj')).open('w') as out:
 out.write('o '+name+'\n')
 for p in v:out.write('v %.5f %.5f %.5f\n'%(p[0]*100,-p[1]*100,p[2]*100))
 for p in uv:out.write('vt %.6f %.6f\n'%tuple(p))
 for p in normal:out.write('vn %.6f %.6f %.6f\n'%(p[0],-p[1],p[2]))
 for face in f:out.write('f '+' '.join('%d/%d/%d'%(i+1,i+1,i+1) for i in face[::-1])+'\n')
(O/'terrain_validation.json').write_text(json.dumps({'changed_original_vertices':int(changed[:original_count].sum()),'added_local_vertices':len(v)-original_count,'unchanged_original_vertices':int((~changed[:original_count]).sum()),'edit_radius_m':170,'finite_geometry':True,'mine_excavation':True},indent=2));print('terrain source ready',flush=True)
