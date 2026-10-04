from pathlib import Path
import numpy as np,json
from scipy.spatial import cKDTree
b=Path('D:/DEVELOPMENT/Games/IsekaiVillage');s=b/'Saved/AdventureWorldSource';env={};src=(b/'Scripts/build_puzzle_continent_v24.py').read_text();exec(src[:src.index('rings=[list(range(2048))]')],env)
v=[];faces=[]
for l in (s/'SM_IV_PuzzleContinent_v24.obj').open():
 if l.startswith('v '):
  x,y,z=map(float,l.split()[1:]);v.append([x/100,-y/100,z/100])
 elif l.startswith('f '):faces.append([int(w.split('/')[0])-1 for w in l.split()[1:]])
v=np.array(v);f=np.array(faces)[56448:];tri=v[f];tree=cKDTree(tri[:,:,:2].mean(axis=1))
ys=np.linspace(-7500,7500,1201);xs=env['river_curve'](ys);rd,lk,width,wl,water=env['hydro'](xs,ys)
points=np.column_stack([xs,ys]);_,ids=tree.query(points,k=24);ts=tri[ids];ab=ts[:,:,1,:2]-ts[:,:,0,:2];ac=ts[:,:,2,:2]-ts[:,:,0,:2];ap=points[:,None,:]-ts[:,:,0,:2]
det=ab[:,:,0]*ac[:,:,1]-ab[:,:,1]*ac[:,:,0]
u=(ap[:,:,0]*ac[:,:,1]-ap[:,:,1]*ac[:,:,0])/det;w=(ab[:,:,0]*ap[:,:,1]-ab[:,:,1]*ap[:,:,0])/det
inside=(u>=-1e-7)&(w>=-1e-7)&(u+w<=1+1e-7)
assert np.all(inside.any(axis=1))
zs=ts[:,:,0,2]+u*(ts[:,:,1,2]-ts[:,:,0,2])+w*(ts[:,:,2,2]-ts[:,:,0,2]);ground=np.max(np.where(inside,zs,-np.inf),axis=1);clearance=wl-12880+.12-ground
report={'mesh_centerline_samples':len(ys),'minimum_water_clearance_m':float(clearance.min()),'obstructed_samples':int((clearance<.1).sum()),'worst_y':float(ys[np.argmin(clearance)])}
(s/'watershed_mesh_validation_v24.json').write_text(json.dumps(report,indent=2));print(report)
assert report['obstructed_samples']==0
