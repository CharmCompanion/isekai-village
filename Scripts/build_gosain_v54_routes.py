"""Forest, lake, town defenses and civic grounds for the reduced kingdom layout."""
import json,math,numpy as np,shapely
from shapely.geometry import Point,LineString
from shapely.ops import nearest_points
import gosain51_kingdom as k
import build_gosain_v50_towns as g
from pathlib import Path
O=Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/World/Gosain54');O.mkdir(exist_ok=True);g.OUT=O
from gosain_surface_sampler import Surface
from scipy.interpolate import PchipInterpolator
surface=Surface('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/World/Gosain53/graded_surface.npz')
def ground(p):
 p=np.asarray(p,float).reshape(-1,2);pts=shapely.points(p);town=shapely.contains(shapely.union_all([q.buffer(180) for q in k.TOWNS]),pts)
 out=k.heights(p,k.old.planned(p,np.full(len(p),k.SEA)))
 if (~town).any():out[~town]=surface.ground(p[~town])
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
routes.append(route([k.CENTERS[1],k.CENTERS[1]+[-500,800],k.MINE]))
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
g.write_obj(chunk,'SM_Gosain54_KingdomRoutes')
# Mixed mature canopy, with irregular glades, open shoreline and traversable route clearances.
rng=np.random.default_rng(5020);a,b,c,d=k.FOREST.bounds
xx,yy=np.meshgrid(np.arange(a,c,24),np.arange(b,d,24));p=np.c_[xx.ravel(),yy.ravel()]+rng.uniform(-9,9,(xx.size,2));ps=shapely.points(p)
keep=shapely.contains(k.FOREST.buffer(-22),ps)&(shapely.distance(ps,k.LAKE)>240)&(shapely.distance(ps,roadzone)>18)
glade=(np.sin(p[:,0]/230)+np.sin(p[:,1]/310)+np.sin((p[:,0]+p[:,1])/540))>2.1
grotto=np.array(json.loads((Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/World/Gosain51/grotto.json')).read_text())['entrance'])
keep &= np.linalg.norm(p-grotto,axis=1)>80
p=p[keep&~glade];z=ground(p)
trees=np.c_[p,z,rng.uniform(0,360,len(p)),rng.uniform(2.2,3.25,len(p)),rng.integers(0,5,len(p))]
np.save(O/'forest_instances.npy',trees)
(O/'forest_instances.json').write_text(json.dumps(trees.tolist()))
(O/'route_report.json').write_text(json.dumps({'forest_trees':len(trees),'trail_points':len(routes[3]),'trail_ground':'sampled from saved53 triangles'},indent=2))
print('ready',len(trees))
