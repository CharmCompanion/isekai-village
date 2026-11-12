import json,sys,numpy as np,shapely,math
from pathlib import Path
from shapely.geometry import Point
from shapely.ops import nearest_points
sys.path.insert(0,'Scripts');import gosain51_kingdom as k;import gosain50_kingdom as old
B=Path('.');O=B/'ArtSource/World/Gosain51'
rows=json.loads((O/'baseline_foliage.json').read_text());known={}
for ver in [43,44]:
 for r in json.loads((B/f'ArtSource/World/Gosain{ver}/foliage_moves.json').read_text()):known[r['mesh']]=r['foliage_type']
changes=[];trees=np.load(O/'forest_instances.npy')
for r in rows:
 tr=np.array(r['transforms'],float)
 if not len(tr):continue
 if '/Gosain50/' in r['mesh']:
  idx=int(r['mesh'].split('Tree')[-1]);new=[]
  for x,y,z,yaw,scale,i in trees:
   if int(i)==idx:new.append([x*100,y*100,z*100,0,0,math.sin(math.radians(yaw)/2),math.cos(math.radians(yaw)/2),scale,scale,scale])
  changes.append({'foliage_type':f'/Game/IsekaiVillage/AdventureWorld/Gosain50/Foliage/FT_Gosain50_Tree{idx}','old_count':len(tr),'new':new});continue
 p=tr[:,:2]/100;ps=shapely.points(p)
 use=shapely.contains(k.POLYS[0],ps)&((shapely.distance(ps,k.LAKE)<500)|(shapely.distance(ps,old.LAKE)<500))&(tr[:,2]<-1800000)
 if not use.any():continue
 assert r['mesh'] in known,('Need foliage type mapping',r['mesh'])
 ix=np.flatnonzero(use);before=p[ix].copy();after=before.copy()
 for j,pt in enumerate(before):
  if k.LAKE.buffer(100).contains(Point(pt)):
   edge=nearest_points(k.LAKE.buffer(145),Point(pt))[0] if not k.LAKE.buffer(145).contains(Point(pt)) else nearest_points(k.LAKE.buffer(145).boundary,Point(pt))[0]
   after[j]=edge.coords[0]
 base0=old.old.planned(before,np.full(len(ix),k.SEA));base1=k.old.planned(after,np.full(len(ix),k.SEA))
 tr[ix,:2]=after*100;tr[ix,2]+=(k.heights(after,base1)-old.heights(before,base0))*100
 changes.append({'foliage_type':known[r['mesh']],'old_count':len(tr),'new':tr.tolist(),'local_instances_adjusted':len(ix)})
(O/'foliage_changes.json').write_text(json.dumps(changes));print('Prepared',len(changes),'foliage types')
