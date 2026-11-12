from pathlib import Path
import json,numpy as np
from scipy.spatial import Voronoi
from scipy.ndimage import map_coordinates
from shapely.geometry import Polygon,Point
from PIL import Image,ImageDraw
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain39';D=B/'Docs/WorldDesign/Gosain39';D.mkdir(exist_ok=True)
plan=json.loads((B/'ArtSource/World/Gosain38/whole_island_plan.json').read_text());ref=np.load(B/'Saved/AdventureWorldSource/world_reference_v30.npz');print(ref.files,flush=True)
rng=np.random.default_rng(3915);blocks=[];outlines=[]
for island in plan['islands']:
    poly=Polygon(island['wall_boundary_m']).buffer(-45);outlines.append(list(poly.exterior.coords));x0,y0,x1,y1=poly.bounds
    pts=np.array([[x+rng.uniform(-80,80),y+rng.uniform(-80,80)] for y in np.arange(y0-1000,y1+1000,350) for x in np.arange(x0-1000,x1+1000,350)])
    vor=Voronoi(pts)
    for i,ri in enumerate(vor.point_region):
        ids=vor.regions[ri]
        if not ids or -1 in ids:continue
        cell=Polygon(vor.vertices[ids]).intersection(poly)
        if cell.is_empty or cell.area<1800 or cell.geom_type!='Polygon':continue
        p=cell.representative_point();edge=cell.distance(poly.boundary)
        blocks.append({'id':len(blocks),'island':island['component'],'center_m':[p.x,p.y],'boundary_m':list(cell.exterior.coords),'area_m2':cell.area,'role':'waterfront' if edge<90 else 'urban','stage':'planned_not_applied'})
allp=np.array([b['center_m'] for b in blocks]);cx,cy,mpp=map(float,[ref['cx'],ref['cy'],ref['mpp']]);key=next(k for k in ('height','heights','z','h') if k in ref.files)
z=map_coordinates(ref[key],np.array([cy-allp[:,1]/mpp,cx-allp[:,0]/mpp]),order=1)
for b,h in zip(blocks,z):b['survey_height_m']=float(h)
(O/'whole_island_districts.json').write_text(json.dumps({'status':'planning_only','blocks':blocks,'note':'District parcels reserve the full enclosed land. Streets, engineered grades and housing layouts must be solved and validated before application.'},indent=2))
points=np.concatenate([np.array(p) for p in outlines]);lo=points.min(axis=0);hi=points.max(axis=0);scale=min(1400/(hi[0]-lo[0]),1050/(hi[1]-lo[1]))
def pix(p):return (int(80+(p[0]-lo[0])*scale),int(115+(hi[1]-p[1])*scale))
im=Image.new('RGB',(1560,1250),'#142c3c');dr=ImageDraw.Draw(im)
for b in blocks:
    dr.polygon([pix(p) for p in b['boundary_m']],fill='#b99568' if b['role']=='waterfront' else '#73846a',outline='#233943')
for p in outlines:dr.line([pix(q) for q in p],fill='#f1d59b',width=3)
dr.text((35,25),'GOSAIN | WHOLE-ISLAND DISTRICT RESERVATIONS',fill='white');dr.text((35,50),str(len(blocks))+' parcels | coast walls retained | all parcels PLANNED, not built',fill='white');dr.text((35,75),'Gold: waterfront districts. Green: urban districts. Fine street grids and terrain grading still to solve.',fill='white')
im.save(D/'Whole_Island_Districts.png');print('planned',len(blocks),'area km2',sum(b['area_m2'] for b in blocks)/1e6,flush=True)
