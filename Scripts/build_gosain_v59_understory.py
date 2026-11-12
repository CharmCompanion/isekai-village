"""Layered native foliage for the final 1.8 km of the existing mine approach."""
import json,numpy as np,shapely
from pathlib import Path
from scipy.spatial import cKDTree
from shapely.geometry import LineString,Point
from gosain_surface_sampler import Surface
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain59';O.mkdir(exist_ok=True)
assert not (O/'applied.json').exists();p=json.loads((B/'ArtSource/World/Gosain55/mine_road_profile.json').read_text());line=LineString(p['xy']);length=line.length;start=max(0,length-1800)
path=LineString([line.interpolate(t).coords[0] for t in np.linspace(start,length,500)])
terrain=Surface(B/'ArtSource/World/Gosain58/graded_surface.npz');trees=np.array(json.loads((B/'ArtSource/World/Gosain58/right_forest_instances.json').read_text()));tree=cKDTree(trees[:,:2]);rng=np.random.default_rng(59026);mine=np.array([15950.,41900.]);rows=[]
fol='/Game/SoStylized/Environment/Foliage/'
assets=[('grass1',fol+'SM_Grass1',.22,.46),('grass2',fol+'SM_Grass2',.35,.70),('fern',fol+'SM_Fern2',.55,1.05),('bush',fol+'SM_BushLeafy01',.85,1.65),('flowers',fol+'SM_FlowerCrocus01',.22,.43),('stone','/Game/SoStylized/Environment/Rocks/Classic/SM_BoulderClassic3',.45,1.6),('outcrop','/Game/SoStylized/Environment/Rocks/Classic/SM_BoulderClumpClassic1',1.5,4.3)]
a,b,c,d=path.buffer(95).bounds
def candidates(step,radius):
 xx,yy=np.meshgrid(np.arange(a,c,step),np.arange(b,d,step));q=np.c_[xx.ravel(),yy.ravel()]+rng.uniform(-step*.42,step*.42,(xx.size,2));ps=shapely.points(q);dist=shapely.distance(ps,path);dt,_=tree.query(q,workers=2)
 mask=(dist>6.2)&(dist<radius)&(np.linalg.norm(q-mine,axis=1)>115)&(dt>2.6)
 q=q[mask];dist=dist[mask];dt=dt[mask];z=terrain.ground(q);dx=terrain.ground(q+[.5,0])-terrain.ground(q-[.5,0]);dy=terrain.ground(q+[0,.5])-terrain.ground(q-[0,.5]);slope=np.sqrt(dx*dx+dy*dy);ok=slope<.55
 return q[ok],z[ok],dist[ok],dt[ok]
q,z,dist,dt=candidates(1.65,82)
# Unequal drifts, lighter bare margins, fern hollows and occasional flowering patches.
patch=.5+.25*np.sin(q[:,0]/23+np.sin(q[:,1]/37))+.25*np.cos(q[:,1]/31);chance=np.clip((.26+.7*patch)*np.clip((dist-6.2)/8,0,1)*np.clip((82-dist)/22,0,1),0,1)
keep=rng.random(len(q))<chance
for xy,zz,ds,tt,pa in zip(q[keep],z[keep],dist[keep],dt[keep],patch[keep]):
 key=0 if rng.random()<.7 else 1
 if pa>.72 and 8<ds<34 and rng.random()<.12:key=4
 elif tt<11 and rng.random()<.10:key=2
 height=rng.uniform(*assets[key][2:]);rows.append([key,*xy,float(zz)-.025,float(rng.uniform(0,360)),float(height)])
q,z,dist,dt=candidates(7.5,88)
for xy,zz,ds,tt in zip(q,z,dist,dt):
 pattern=np.sin(xy[0]/41)+np.cos(xy[1]/53)
 if pattern<.35 or rng.random()>.55:continue
 key=3 if rng.random()<.64 else 2;height=rng.uniform(*assets[key][2:]);rows.append([key,*xy,float(zz)-.04,float(rng.uniform(0,360)),float(height)])
q,z,dist,dt=candidates(17,92)
for xy,zz,ds,tt in zip(q,z,dist,dt):
 if rng.random()>.20 or ds<9:continue
 key=6 if ds>20 and rng.random()<.25 else 5;height=rng.uniform(*assets[key][2:]);rows.append([key,*xy,float(zz)-height*.24,float(rng.uniform(0,360)),float(height)])
data={'assets':[{'key':key,'path':path,'height_min':lo,'height_max':hi} for key,path,lo,hi in assets],'instances':rows,'extent':'last 1.8 km of mine road, 6.2–92 m from centerline, outside 115 m mine work area','terrain_source':'Gosain58/graded_surface.npz'}
assert np.isfinite(np.array(rows)).all();counts={a[0]:sum(int(r[0])==i for r in rows) for i,a in enumerate(assets)}
(O/'understory.json').write_text(json.dumps(data));(O/'source_verification.json').write_text(json.dumps({'instances':len(rows),'counts':counts,'native_pack_reuse':True,'minimum_road_center_clearance_m':float(shapely.distance(shapely.points(np.array(rows)[:,1:3]),path).min()),'mine_footprint_clear':bool((np.linalg.norm(np.array(rows)[:,1:3]-mine,axis=1)>115).all()),'finite':True},indent=2));print(counts,flush=True)
