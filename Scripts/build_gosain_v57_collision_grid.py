"""Regular local collision surface; retain full visual terrain separately."""
import numpy as np,json
from pathlib import Path
from gosain_surface_sampler import Surface
import gosain57_mine as m
s=Surface(m.O/'graded_surface.npz');ds=np.arange(-90,152,2.);ls=np.arange(-54,56,2.);dd,ll=np.meshgrid(ds,ls,indexing='ij');p=np.c_[dd.ravel(),ll.ravel()];z=s.ground(m.xy(p[:,0],p[:,1]))-m.Z;v=np.c_[p,z];f=[]
for i in range(len(ds)-1):
 for j in range(len(ls)-1):
  a=i*len(ls)+j;b=a+len(ls);f.extend([[a,b,b+1],[a,b+1,a+1]])
f=np.array(f);sample=f[::max(1,len(f)//1200)];mid=v[sample].mean(axis=1);real=s.ground(m.xy(mid[:,0],mid[:,1]))-m.Z;error=abs(real-mid[:,2]);yard=(mid[:,0]<30)&(mid[:,0]>-45)&(abs(mid[:,1])<30)
report={'vertices':len(v),'triangles':len(f),'grid_spacing_m':2,'validation_samples':len(mid),'max_vertical_error_m':float(error.max()),'yard_max_vertical_error_m':float(error[yard].max()),'p95_vertical_error_m':float(np.quantile(error,.95))}
assert report['yard_max_vertical_error_m']<.20,report
with (m.O/'SM_Gosain57_MineGroundCollisionGrid.obj').open('w') as o:
 o.write('o SM_Gosain57_MineGroundCollisionGrid\nusemtl mine_ground\n')
 for q in v:o.write('v %.6f %.6f %.6f\n'%(q[0]*100,-q[1]*100,q[2]*100))
 for face in f:o.write('f '+' '.join(str(i+1) for i in face[::-1])+'\n')
(m.O/'ground_collision_grid.json').write_text(json.dumps(report,indent=2));print(report)
