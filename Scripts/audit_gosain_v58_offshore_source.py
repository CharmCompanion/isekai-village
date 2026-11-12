import json,numpy as np,shapely
from pathlib import Path
import gosain51_kingdom as k
O=Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/World/Gosain58');v=np.load(O/'graded_surface.npz')['vertices'];rows=[]
for i,poly in enumerate(k.POLYS):
 lo=np.array(poly.bounds[:2])-600;hi=np.array(poly.bounds[2:])+600;ix=np.flatnonzero(((v[:,:2]>=lo)&(v[:,:2]<=hi)).all(axis=1));p=shapely.points(v[ix,:2]);d=shapely.distance(p,poly);mask=(d>30)&(d<550);q=v[ix][mask];dd=d[mask]
 bad=q[:,2]>k.SEA+2
 rows.append({'island':i,'offshore_vertices':len(q),'above_sea_vertices':int(bad.sum()),'max_offshore_height_above_sea_m':float(q[:,2].max()-k.SEA),'examples':np.c_[q[bad],dd[bad]][:25].tolist()})
(O/'offshore_audit.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
