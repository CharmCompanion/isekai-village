import numpy as np,json
from pathlib import Path
import gosain57_mine as m
b=np.load(m.O/'graded_surface.npz');v=b['vertices'];f=b['triangles'];radius=np.linalg.norm(v[:,:2]-m.C,axis=1);use=np.all(radius[f]<160,axis=1);faces=f[use];ids,ix=np.unique(faces,return_inverse=True);p=v[ids].copy();d,l=m.local(p[:,:2]);p=np.c_[d,l,p[:,2]-m.Z];faces=ix.reshape(-1,3)
with (m.O/'SM_Gosain57_MineGroundCollision.obj').open('w') as o:
 o.write('o SM_Gosain57_MineGroundCollision\nusemtl mine_ground\n')
 for q in p:o.write('v %.6f %.6f %.6f\n'%(q[0]*100,-q[1]*100,q[2]*100))
 for face in faces:o.write('f '+' '.join(str(i+1) for i in face[::-1])+'\n')
(m.O/'ground_collision_source.json').write_text(json.dumps({'vertices':len(p),'triangles':len(faces),'radius_m':160,'purpose':'Hidden query/physics surface for the mine only. Main continent collision stays unchanged.'},indent=2));print(len(p),len(faces))
