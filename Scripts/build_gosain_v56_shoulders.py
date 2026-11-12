"""Feather the mine road into broad hillside shoulders; retain all unrelated geometry."""
import sys,json,numpy as np,shapely
from pathlib import Path
import gosain51_kingdom as k
import gosain55_roadbed as road
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain56';O.mkdir(exist_ok=True)
b=np.load(B/'ArtSource/World/Gosain55/graded_surface.npz');v=b['vertices'].copy();old=v.copy();f=b['triangles'];uv=b['uv'];normal=b['normals'].copy()
lo=road.XY.min(axis=0)-620;hi=road.XY.max(axis=0)+620;ix=np.flatnonzero(((v[:,:2]>=lo)&(v[:,:2]<=hi)).all(axis=1));p=v[ix,:2];inside=shapely.contains(k.POLYS[1],shapely.points(p));ix=ix[inside];p=v[ix,:2]
d,z=road.sample(p);delta=abs(v[ix,2]-z);td=shapely.distance(shapely.points(p),k.TOWNS[1]);townfade=np.clip(td/120,0,1);townfade=townfade*townfade*(3-2*townfade)
width=25+(np.clip(delta*4+80,120,550)-25)*townfade
w=np.clip((width-d)/(width-12),0,1);w=w*w*(3-2*w);v[ix,2]=v[ix,2]*(1-w)+z*w
# Preserve the already graded inner carriageway exactly.
v[ix[d<=12],2]=old[ix[d<=12],2]
changed=abs(v[:,2]-old[:,2])>1e-8;v[~changed]=old[~changed]
ff=f[changed[f].any(axis=1)];cross=np.cross(v[ff[:,1]]-v[ff[:,0]],v[ff[:,2]]-v[ff[:,0]]);acc=np.zeros_like(v)
for j in range(3):np.add.at(acc,ff[:,j],cross)
l=np.linalg.norm(acc,axis=1);use=changed&(l>1e-12);normal[use]=acc[use]/l[use,None]
assert np.array_equal(v[~changed],old[~changed]);assert np.array_equal(v[:,:2],old[:,:2]);assert np.isfinite(v).all()
np.savez_compressed(O/'graded_surface.npz',vertices=v,triangles=f,uv=uv,normals=normal,region=changed)
name='SM_IV_Continent_GosainShoulders56'
with (O/(name+'.obj')).open('w') as out:
 out.write('o '+name+'\n')
 for q in v:out.write('v %.5f %.5f %.5f\n'%(q[0]*100,-q[1]*100,q[2]*100))
 for q in uv:out.write('vt %.6f %.6f\n'%tuple(q))
 for q in normal:out.write('vn %.6f %.6f %.6f\n'%(q[0],-q[1],q[2]))
 for face in f:out.write('f '+' '.join('%d/%d/%d'%(i+1,i+1,i+1) for i in face[::-1])+'\n')
(O/'validation.json').write_text(json.dumps({'changed_vertices':int(changed.sum()),'topology_and_xy_unchanged':True,'outside_right_island_unchanged':True,'max_shoulder_width_m':550,'inner_carriageway_retained':True},indent=2));print('road shoulder source ready',int(changed.sum()),flush=True)

