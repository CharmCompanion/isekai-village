"""Authoritative Gosain terrace elevations in world metres; no scene mutation."""
import json,numpy as np,shapely
from pathlib import Path
from shapely.geometry import Polygon
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');SEA=-20600.
PLAN=json.loads((B/'ArtSource/World/Gosain38/whole_island_plan.json').read_text())
POLYS=[Polygon(q['wall_boundary_m']) for q in PLAN['islands']]
CAP=np.array(PLAN['islands'][0]['civic_center_m'])
# An upper castle platform behind the established cathedral district.
CASTLE_CENTER=CAP+np.array([300.,650.])
CASTLE=Polygon(np.array([[-440,-340],[230,-380],[440,-160],[400,260],[80,370],[-360,250]])+CASTLE_CENTER)
assert POLYS[0].contains(CASTLE.buffer(80))
def ease(t):t=np.clip(t,0,1);return t*t*(3-2*t)
def planned(p,old):
    p=np.asarray(p,float).reshape(-1,2);old=np.asarray(old,float);out=old.copy();pts=shapely.points(p)
    for i,poly in enumerate(POLYS):
        near=shapely.dwithin(pts,poly,140);ix=np.flatnonzero(near)
        if not len(ix):continue
        pp=p[ix];ps=pts[ix];inside=shapely.contains(poly,ps);dist=shapely.distance(ps,poly.boundary);signed=np.where(inside,dist,-dist)
        center=np.array(PLAN['islands'][i]['civic_center_m'])
        north=(pp[:,1]-center[1])-.45*(pp[:,0]-center[0])
        # Broad cross-island benches, not scaled versions of the old bumpy relief.
        if i==0:
            height=48+32*ease((north+5300)/320)+32*ease((north+3000)/320)+32*ease((north+1550)/320)
        else:
            height=48+24*ease((north+3400)/320)+24*ease((north+1100)/320)+24*ease((north-1300)/320)
        # A level perimeter footing and broad inner lowland meet the massive curtain.
        height=48+(height-48)*ease((signed-75)/180)
        if i==0:
            dc=shapely.distance(ps,CASTLE);insidecastle=shapely.contains(CASTLE,ps)
            weight=np.where(insidecastle,1.,1-ease(dc/200))
            height=height*(1-weight)+224*weight
        # Blend into the existing coastal apron outside the walls, preserving the sea.
        weight=ease((signed+140)/140)
        out[ix]=old[ix]*(1-weight)+(SEA+height)*weight
    return out
