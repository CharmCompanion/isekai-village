"""Forest, lake, town defenses and civic grounds for the reduced kingdom layout."""
import json,math,numpy as np,shapely
from shapely.geometry import Point,LineString
from shapely.ops import nearest_points
import gosain51_kingdom as k
import build_gosain_v50_towns as g
from pathlib import Path
O=Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/World/Gosain55');O.mkdir(exist_ok=True);g.OUT=O
from gosain_surface_sampler import Surface
from scipy.interpolate import PchipInterpolator
import gosain55_right_landscape as land
surface=Surface('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/World/Gosain55/graded_surface.npz')
surface.allow_missing=True
def ground(p):
 p=np.asarray(p,float).reshape(-1,2);out=surface.ground(p);missing=~np.isfinite(out)
 if missing.any():out[missing]=k.heights(p[missing],k.old.planned(p[missing],np.full(int(missing.sum()),k.SEA)))
 return out
g.MATS.append('foresttrail')

def ribbon(chunk,pts,w,mat=9):
    z=ground(pts)
    for a,b,za,zb in zip(pts,pts[1:],z,z[1:]):chunk.ribbon(a,b,w,za,zb,mat,.22)
def route(points):
    l=LineString(points);return np.array([l.interpolate(t).coords[0] for t in np.linspace(0,l.length,max(2,int(l.length/18)))])
routes=[]
for i,poly in enumerate(k.POLYS):
    end=next(e for e in k.old.PLAN['bridge_endpoints_m'] if poly.buffer(30).covers(Point(e)))
    routes.append(route([end,(np.array(end)+k.CENTERS[i])/2,k.CENTERS[i]]))
mineguide=np.array([k.CENTERS[1],k.CENTERS[1]+[-500,800],[14000,41400],[14600,41600],[15200,41650],[15600,42200],land.MINE])
mt=np.r_[0,np.cumsum(np.linalg.norm(np.diff(mineguide,axis=0),axis=1))]
routes.append(PchipInterpolator(mt,mineguide,axis=0)(np.linspace(0,mt[-1],int(mt[-1]/10))))
approach=k.CENTERS[0]+[1200,-1800]
landing=np.array(nearest_points(k.LAKE.buffer(240).boundary,Point(approach))[0].coords[0])
guide=np.array([approach,[24100,39750],[24550,39300],[24750,38700],[25450,38400],[25850,37650],landing])
t=np.r_[0,np.cumsum(np.linalg.norm(np.diff(guide,axis=0),axis=1))];curve=PchipInterpolator(t,guide,axis=0)(np.arange(0,t[-1],8));curve=np.vstack([curve,landing])
routes.append(np.vstack([route([k.CENTERS[0],approach]),curve[1:]]))
roadzone=shapely.union_all([LineString(p).buffer(5 if i==3 else 16) for i,p in enumerate(routes)])
chunk=g.Chunk()
for i,pts in enumerate(routes):
 width=5 if i==3 else 9;mat=10 if i==3 else 9
 for a,b in zip(pts,pts[1:]):
  v=b-a;n=np.array([-v[1],v[0]])/np.linalg.norm(v)*width*.5;xy=np.array([a+n,a-n,b-n,b+n]);z=ground(xy)+.12
  chunk.quad([[*p,h] for p,h in zip(xy,z)],mat)
g.write_obj(chunk,'SM_Gosain55_KingdomRoutes')
# New right-island woodland: foothills and irregular country copses, not a ring.
rng=np.random.default_rng(55023);a,b,c,d=k.POLYS[1].bounds
xx,yy=np.meshgrid(np.arange(a,c,28),np.arange(b,d,28));p=np.c_[xx.ravel(),yy.ravel()]+rng.uniform(-11,11,(xx.size,2));ps=shapely.points(p)
foothills=(p[:,1]>40700)&(p[:,1]<44600)
copses=(np.sin(p[:,0]/570)+np.cos(p[:,1]/730)+np.sin((p[:,0]+p[:,1])/990))>1.85
keep=shapely.contains(k.POLYS[1].buffer(-400),ps)&(shapely.distance(ps,k.TOWNS[1])>280)&(foothills|copses)&(shapely.distance(ps,roadzone)>24)&(np.linalg.norm(p-land.MINE,axis=1)>130)
p=p[keep];surface.allow_missing=True;z=surface.ground(p)
dx=surface.ground(p+[8,0])-surface.ground(p-[8,0]);dy=surface.ground(p+[0,8])-surface.ground(p-[0,8]);slope=np.sqrt(dx*dx+dy*dy)/16
valid=np.isfinite(z)&np.isfinite(slope)&(slope<.5)&(z<k.SEA+380);skipped=int((~valid).sum());p=p[valid];z=z[valid]
# Dappled gaps break the canopy into unequal stands.
glade=(np.sin(p[:,0]/170)+np.cos(p[:,1]/260)+np.sin((p[:,0]-p[:,1])/410))>2.1;p=p[~glade];z=z[~glade]
trees=np.c_[p,z,rng.uniform(0,360,len(p)),rng.uniform(2.0,3.1,len(p)),rng.integers(0,5,len(p))]
np.save(O/'forest_instances.npy',trees);(O/'forest_instances.json').write_text(json.dumps(trees.tolist()))
routez=ground(routes[2]);grades=np.abs(np.diff(routez))/np.linalg.norm(np.diff(routes[2],axis=0),axis=1)
(O/'countryside_report.json').write_text(json.dumps({'right_forest_trees':len(trees),'excluded_steep_high_or_missing_samples':skipped,'mine_xy_m':land.MINE.tolist(),'mine_route_max_grade':float(grades.max()),'right_forest_extent':'foothills and scattered lower-country copses'},indent=2));print('right forest',len(trees),'mine max grade',grades.max())
