"""Forest, lake, town defenses and civic grounds for the reduced kingdom layout."""
import json,math,numpy as np,shapely
from shapely.geometry import Point,LineString
from shapely.ops import nearest_points
import gosain50_kingdom as k
import build_gosain_v50_towns as g
O=g.OUT
def ground(p):
    p=np.asarray(p,float).reshape(-1,2);return k.heights(p,k.old.planned(p,np.full(len(p),k.SEA)))
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
routes.append(route([k.CENTERS[0],k.CENTERS[0]+[1200,-1800],k.LAKE_CENTER+[-850,100],k.LAKE_CENTER+[0,-1000]]))
roadzone=shapely.union_all([LineString(p).buffer(16) for p in routes])
chunk=g.Chunk()
for pts in routes:ribbon(chunk,pts,9)
g.write_obj(chunk,'SM_Gosain50_KingdomRoutes')
# City walls are retained as local town circuits rather than coastline-wide defenses.
wall=g.Chunk()
for i,town in enumerate(k.TOWNS):
    ring=town.buffer(12).exterior;l=ring.length;pts=np.array([ring.interpolate(t).coords[0] for t in np.linspace(0,l,int(l/24)+1)])
    z=ground(pts)
    for j,(a,b,za,zb) in enumerate(zip(pts,pts[1:],z,z[1:])):
        mid=(a+b)/2
        if roadzone.buffer(12).covers(Point(mid)):continue
        d=b-a;n=np.array([-d[1],d[0]])/np.linalg.norm(d)*9
        wall.quad([[*(a+n),za-2],[*(b+n),zb-2],[*(b+n),zb+40],[*(a+n),za+40]],0)
        wall.quad([[*(b-n),zb-2],[*(a-n),za-2],[*(a-n),za+40],[*(b-n),zb+40]],0)
        wall.ribbon(a,b,18,za+40,zb+40,5,0)
        for sign in [-1,1]:wall.ribbon(a+sign*n,b+sign*n,1.2,za+42,zb+42,5,0)
        if j%6==0:g.lathe(wall,a,[(13,za-2),(13,za+47),(15,za+48),(15,za+50)],0,0,8)
g.write_obj(wall,'SM_Gosain50_TownWalls')
# Visible civic compounds; interiors and gameplay remain separate.
civic=g.Chunk();school=k.SCHOOL;z=float(ground([school])[0])
for off,size,floors in [((-130,0),(35,220),4),((130,0),(35,220),4),((0,100),(225,35),5),((0,-130),(140,24),2)]:g.building(civic,school+off,size,0,z,floors,0,15)
civic.quad([[*(school+[x,y]),z+.25] for x,y in [(-100,-95),(100,-95),(100,80),(-100,80)]],9)
royal=k.CENTERS[0]+[420,-120]
for off in [(-80,-60),(80,-60),(-80,65),(80,65)]:
    c=royal+off;g.building(civic,c,(45,60),0,float(ground([c])[0]),5,1,15)
g.write_obj(civic,'SM_Gosain50_RoyalAndKnightGrounds')
# Water clips to the real height function, forming banks rather than a disk over grass.
water=g.Chunk();xmin,ymin,xmax,ymax=k.LAKE.buffer(260).bounds;step=24
for x in np.arange(xmin,xmax,step):
    ys=np.arange(ymin,ymax,step);corners=np.array([[x,y] for y in ys]+[[x+step,y] for y in ys]);zs=ground(corners)
    for j in range(len(ys)-1):
        for ids in [(j,len(ys)+j,len(ys)+j+1),(j,len(ys)+j+1,j+1)]:
            pts=[(corners[t],zs[t]) for t in ids];clipped=[]
            for (a,za),(b,zb) in zip(pts,pts[1:]+pts[:1]):
                ina=za<k.LAKE_LEVEL;inb=zb<k.LAKE_LEVEL
                if ina:clipped.append(a)
                if ina!=inb:clipped.append(a+(b-a)*(k.LAKE_LEVEL-za)/(zb-za))
            if len(clipped)>=3:water.add([[*p,k.LAKE_LEVEL] for p in clipped],[[0,t,t+1] for t in range(1,len(clipped)-1)],0)
g.write_obj(water,'SM_Gosain50_RoyalLake')
# Mixed mature canopy, with irregular glades, open shoreline and traversable route clearances.
rng=np.random.default_rng(5020);a,b,c,d=k.FOREST.bounds
xx,yy=np.meshgrid(np.arange(a,c,24),np.arange(b,d,24));p=np.c_[xx.ravel(),yy.ravel()]+rng.uniform(-9,9,(xx.size,2));ps=shapely.points(p)
keep=shapely.contains(k.FOREST.buffer(-22),ps)&(shapely.distance(ps,k.LAKE)>90)&(shapely.distance(ps,roadzone)>18)
glade=(np.sin(p[:,0]/230)+np.sin(p[:,1]/310)+np.sin((p[:,0]+p[:,1])/540))>2.1
p=p[keep&~glade];z=ground(p)
trees=np.c_[p,z,rng.uniform(0,360,len(p)),rng.uniform(2.2,3.25,len(p)),rng.integers(0,5,len(p))]
np.save(O/'forest_instances.npy',trees)
port=nearest_points(k.POLYS[0].boundary,Point(k.CENTERS[0]+[-1700,-500]))[0]
report={'status':'source_only','town_area_km2':[p.area/1e6 for p in k.TOWNS],'forest_zone_percent':k.FOREST.area/k.POLYS[0].area*100,'lake_basin_km2':k.LAKE.area/1e6,'tree_instances':len(trees),'forest_zone_includes_lake':True,'school_xy_m':school.tolist(),'royal_houses_xy_m':royal.tolist(),'mine_xy_m':k.MINE.tolist(),'port_reservation_xy_m':list(port.coords[0]),'town_polygons':[list(p.exterior.coords) for p in k.TOWNS],'forest_polygon':shapely.to_geojson(k.FOREST),'limitations':['Port is a reserved shoreline site; docks and graded harbor approach remain unbuilt.','Mine is a reserved ridge access point; cave interior and entrance remain unbuilt.','Knight and royal compounds are exterior first-pass buildings; interiors, activities and detail remain.','65 percent is forest-and-lake land allocation, not measured tree-canopy cover.']}
(O/'kingdom.json').write_text(json.dumps(report,indent=2));print({k:report[k] for k in ['town_area_km2','forest_zone_percent','tree_instances']})
