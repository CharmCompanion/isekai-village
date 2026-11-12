"""Kingdom land-use and terrain proposal approved 20 October 2026; metres."""
import json,numpy as np,shapely
from shapely.geometry import Point,LineString
from shapely.affinity import scale
import gosain44_terraces as old
POLYS=old.POLYS;SEA=old.SEA
CENTERS=[old.CASTLE_CENTER-np.array([0,450]),np.array([14833.928091899152,39944.713312447166])]
def area_radius(poly,center,area):
    lo,hi=100.,6000.
    for _ in range(45):
        r=(lo+hi)/2;p=Point(center).buffer(r,quad_segs=64).intersection(poly.buffer(-80))
        if p.area<area:lo=r
        else:hi=r
    return p
TOWNS=[area_radius(p,c,6e6) for p,c in zip(POLYS,CENTERS)]
ROYAL_OPEN=area_radius(POLYS[0],CENTERS[0],POLYS[0].area*.35)
FOREST=POLYS[0].difference(ROYAL_OPEN)
LAKE_CENTER=np.array([24950.,37800.])
LAKE=scale(Point(LAKE_CENTER).buffer(1,quad_segs=64),780,470,origin=tuple(LAKE_CENTER)).intersection(FOREST.buffer(-180))
assert not LAKE.is_empty and LAKE.area>500000
LAKE_LEVEL=SEA+66
RIDGE=np.array([[12200.,43300.],[13000.,42400.],[13700.,41600.]])
MOUNTAIN=LineString(RIDGE)
MINE=np.array([13950.,41800.])
SCHOOL=CENTERS[1]+np.array([950.,-200.])
RESERVES=[Point(SCHOOL).buffer(230),Point(CENTERS[0]+[420,-120]).buffer(180)]
def heights(p,z):
    p=np.asarray(p,float);z=np.asarray(z,float);out=z.copy();pts=shapely.points(p)
    for i,poly in enumerate(POLYS):
        inside=shapely.contains(poly,pts);ix=np.flatnonzero(inside)
        if not len(ix):continue
        q=p[ix];ps=pts[ix];coast=shapely.distance(ps,poly.boundary)
        town=shapely.distance(ps,TOWNS[i]);blend=old.ease(town/350)*old.ease(coast/170)
        natural=SEA+68+18*np.sin(q[:,0]/1100)*np.cos(q[:,1]/1400)+11*np.sin((q[:,0]+q[:,1])/680)
        if i==1:
            dist=shapely.distance(ps,MOUNTAIN);ridge=480*np.exp(-(dist/850)**2)
            detail=1+.13*np.sin(q[:,0]/280)*np.sin(q[:,1]/330)+.08*np.cos(q[:,1]/160)
            natural+=ridge*detail
        out[ix]=z[ix]*(1-blend)+natural*blend
    # Irregular terrain bank surrounding the retained, level lake surface.
    d=shapely.distance(pts,LAKE);inside=shapely.contains(LAKE,pts);weight=np.where(inside,1.,1-old.ease(d/220))
    bed=LAKE_LEVEL-14+4*np.sin(p[:,0]/280)*np.sin(p[:,1]/300)
    out=out*(1-weight)+bed*weight
    # Keep the existing fortified bridge and its abutment terrain at their saved heights.
    for end in old.PLAN['bridge_endpoints_m']:
        distance=np.linalg.norm(p-np.array(end),axis=1)
        preserve=1-old.ease((distance-90)/170)
        out=out*(1-preserve)+z*preserve
    return out
