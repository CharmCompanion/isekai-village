import sys,json,numpy as np,shapely
from pathlib import Path
from shapely.geometry import Point
sys.path.insert(0,'Scripts');import gosain51_kingdom as k
O=Path('ArtSource/World/Gosain52');rng=np.random.default_rng(521023)
def ground(p):
 p=np.asarray(p).reshape(-1,2);return k.heights(p,k.old.planned(p,np.full(len(p),k.SEA)))
ring=k.LAKE.exterior
rows=[]
for i in range(520):
 t=rng.uniform(0,ring.length);p=np.array(ring.interpolate(t).coords[0]);a=np.array(ring.interpolate((t-3)%ring.length).coords[0]);b=np.array(ring.interpolate((t+3)%ring.length).coords[0]);v=b-a;v=np.array([v[1],-v[0]]);v/=np.linalg.norm(v)
 if k.LAKE.contains(Point(p+v*5)):v=-v
 # Find the bank's actual crossing of lake level, then move inland.
 lo=0;hi=260
 for _ in range(12):
  mid=(lo+hi)/2
  if ground([p+v*mid])[0]<k.LAKE_LEVEL+2:lo=mid
  else:hi=mid
 shore=p+v*hi
 cluster=.5+.5*np.sin(t/370)*np.sin(t/190+.8)
 if cluster<.32:continue
 xy=shore+v*rng.uniform(4,38)
 if not k.POLYS[0].buffer(-100).contains(Point(xy)):continue
 z=float(ground([xy])[0]);size=float(rng.uniform(2.5,7.5));rows.append({'kind':'rock','variant':int(rng.integers(0,3)),'xy':xy.tolist(),'z':z-.4,'size':[size*1.4,size,size*.7],'yaw':float(rng.uniform(0,360))})
 for j in range(int(rng.integers(3,8))):
  pos=xy+rng.normal(0,9,2)
  if ground([pos])[0]<k.LAKE_LEVEL+1.5:continue
  rows.append({'kind':'plant','variant':int(rng.integers(0,4)),'xy':pos.tolist(),'z':float(ground([pos])[0])-.1,'size':float(rng.uniform(1.4,2.8)),'yaw':float(rng.uniform(0,360))})
g=json.loads(Path('ArtSource/World/Gosain51/grotto.json').read_text());c=np.array(g['entrance']);v=np.array(g['direction']);side=np.array([-v[1],v[0]])
# Geological shoulders connect the recess to a larger, uneven outcrop.
for depth,lateral,size in [(9,-21,16),(22,-24,22),(39,-19,29),(48,-2,34),(42,22,25),(24,24,20),(4,19,12),(-8,-16,8),(-12,17,6),(58,18,17),(60,-20,15)]:
 p=c+depth*v+lateral*side;rows.append({'kind':'rock','variant':int(rng.integers(0,3)),'xy':p.tolist(),'z':float(ground([p])[0])-size*.2,'size':[size*1.2,size,size*.8],'yaw':float(rng.uniform(0,360))})
for i in range(160):
 p=c+rng.uniform(-65,65,2)
 # Keep the entrance and approach corridor clear.
 rel=p-c
 if abs(rel@side)<9 and rel@v<30:continue
 rows.append({'kind':'plant','variant':int(rng.integers(0,4)),'xy':p.tolist(),'z':float(ground([p])[0])-.1,'size':float(rng.uniform(1.4,2.3)),'yaw':float(rng.uniform(0,360))})
(O/'shore_props.json').write_text(json.dumps(rows));print('props',len(rows),'rocks',sum(r['kind']=='rock' for r in rows))
