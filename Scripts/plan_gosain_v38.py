"""Whole-island city boundary and circulation plan from existing terrain data."""
from pathlib import Path
import json,numpy as np
from scipy.ndimage import label
from scipy.spatial import cKDTree
from skimage.measure import find_contours
from shapely.geometry import Polygon,LineString,Point
from shapely.ops import nearest_points
from PIL import Image,ImageDraw,ImageFont
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain38';O.mkdir(exist_ok=True,parents=True)
d=np.load(B/'Saved/AdventureWorldSource/world_reference_v30.npz');c,_=label(~d['water']);cx,cy,mpp=map(float,(d['cx'],d['cy'],d['mpp']))
polys=[]
for cid in (2,1):
    # Water mask includes a submerged coastal apron; keep the city on dry land.
    mask=(c==cid)&(d['height']>-20588)
    contours=find_contours(mask.astype(float),.5)
    rings=[Polygon(np.column_stack([(cx-p[:,1])*mpp,(cy-p[:,0])*mpp])).buffer(0) for p in contours]
    poly=max(rings,key=lambda p:p.area).simplify(35,preserve_topology=True).buffer(-35)
    if poly.geom_type=='MultiPolygon':poly=max(poly.geoms,key=lambda p:p.area)
    polys.append(poly)
a,b=nearest_points(polys[0].boundary,polys[1].boundary)
bridge=np.array([a.coords[0],b.coords[0]])
sites=[np.array([22173.92809189915,41624.713312447166]),np.array([14333.928091899152,39144.713312447166])]
out={'status':'planning_only_not_applied','sea_level_m':-20600,'islands':[],'bridge_endpoints_m':bridge.tolist(),'bridge_length_m':float(np.linalg.norm(bridge[1]-bridge[0])),'protected':'El Ruhn and other regions'}
for i,p in enumerate(polys):
    out['islands'].append({'component':[2,1][i],'wall_boundary_m':list(map(list,p.exterior.coords)),'enclosed_area_km2':p.area/1e6,'civic_center_m':sites[i].tolist(),'wall_length_m':p.length})
(O/'whole_island_plan.json').write_text(json.dumps(out,indent=2))
im=Image.new('RGB',(1500,1200),'#163544');dr=ImageDraw.Draw(im)
bounds=np.array([p.bounds for p in polys]);lo=bounds[:,:2].min(0)-350;hi=bounds[:,2:].max(0)+350
sc=min(1380/(hi[0]-lo[0]),960/(hi[1]-lo[1]))
def xy(p):return (70+(p[0]-lo[0])*sc,110+(hi[1]-p[1])*sc)
colors=['#557e63','#688767']
for i,p in enumerate(polys):
    dr.polygon([xy(v) for v in p.exterior.coords],fill=colors[i],outline='#efd8a0',width=5)
    # Urban infill is represented at district scale; this image is a plan only.
    for x in np.arange(p.bounds[0],p.bounds[2],180):
        line=LineString([(x,p.bounds[1]),(x,p.bounds[3])]).intersection(p.buffer(-20))
        for g in (line.geoms if hasattr(line,'geoms') else [line]):
            if g.geom_type=='LineString':dr.line([xy(v) for v in g.coords],fill='#a1aa83',width=1)
    for y in np.arange(p.bounds[1],p.bounds[3],180):
        line=LineString([(p.bounds[0],y),(p.bounds[2],y)]).intersection(p.buffer(-20))
        for g in (line.geoms if hasattr(line,'geoms') else [line]):
            if g.geom_type=='LineString':dr.line([xy(v) for v in g.coords],fill='#a1aa83',width=1)
    x,y=xy(sites[i]);dr.ellipse((x-9,y-9,x+9,y+9),fill='#f4d18a');dr.text((x+15,y),['Cathedral quarter','Monastery quarter'][i],fill='white')
dr.line([xy(v) for v in bridge],fill='#f6c873',width=8)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',27)
dr.text((40,28),'GOSAIN | Both islands enclosed and urbanized',font=font,fill='white')
dr.text((40,1085),'Coastal wall circuits | Dense blocks throughout | Bridge-linked streets',font=font,fill='#f4d18a')
dr.text((40,1130),'Planning diagram from existing terrain. Building placement and native validation pending.',fill='white',font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20))
dest=B/'Docs/WorldDesign/Gosain38';dest.mkdir(exist_ok=True,parents=True);im.save(dest/'Whole_Island_Plan.png')
print(json.dumps({k:v for k,v in out.items() if k!='islands'}));print([(i['enclosed_area_km2'],i['wall_length_m']) for i in out['islands']])
