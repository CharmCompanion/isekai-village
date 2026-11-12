"""Gosain milestone 1: complete-house cathedral district and coherent masonry.
Only generates new source assets; applying is a separate editor operation.
"""
from gosain37_geometry import *
from scipy.ndimage import gaussian_filter1d, distance_transform_edt
from scipy.interpolate import CubicSpline
from skimage.measure import find_contours
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union, nearest_points
from scipy.spatial import Voronoi
from PIL import Image, ImageDraw, ImageFont
import hashlib

R='/Game/IsekaiVillage/AdventureWorld'
old=json.loads((SRC/'civilization_instances_v36.json').read_text())
assets=old['assets'].copy();rows={};manifest=[];rng=np.random.default_rng(37013)
ORIGIN=[float(CAP[0]),float(CAP[1]),ground(*CAP)]
roads=Mesh();stone=Mesh();pads=Mesh();report={}
def put(k,p,scale=1.,yaw=0.,z=None):
    p=np.array(p,float);sc=[scale]*3 if np.isscalar(scale) else list(scale)
    z=ground(*p) if z is None else float(z)
    rows.setdefault(k,[]).append([float(p[0]),float(p[1]),z,*map(float,sc),float(yaw)])
def smooth(coords,closed=False,step=4):
    p=np.array(coords,float)
    if closed:p=np.vstack([p,p[0]])
    t=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))]
    sp=CubicSpline(t,p,bc_type='periodic' if closed else 'natural')
    return sp(np.linspace(0,t[-1],int(t[-1]/step)+1,endpoint=not closed))
roadlines=[]
def road(local,width=7,closed=False):
    p=smooth(np.array(local)+CAP,closed);roadlines.append((p,width))
    tan=np.roll(p,-1,axis=0)-np.roll(p,1,axis=0) if closed else np.gradient(p,axis=0)
    tan/=np.linalg.norm(tan,axis=1,keepdims=True);side=np.column_stack([-tan[:,1],tan[:,0]])
    vv=[]
    for s in (-.5,-.25,0,.25,.5):
        q=p+side*width*s;vv.append(np.column_stack([q,ground_many(q)+.065]))
    v=np.stack(vv,axis=1).reshape(-1,3);f=[]
    for i in range(len(p) if closed else len(p)-1):
        a=i*5;b=((i+1)%len(p))*5
        for j in range(4):f.extend([[a+j,b+j,b+j+1],[a+j,b+j+1,a+j+1]])
    roads.part(v,f,'paving')
    return p

# Older irregular precinct and three generations of connecting streets.
road([(0,-166),(0,-215),(15,-315),(40,-480),(100,-710),(100,-910)],13)
road([(-925,368),(-660,280),(-435,160),(-285,-50),(-160,-220),(15,-315)],9)
road([(15,-315),(225,-230),(440,-80),(660,80),(820,200)],10)
road([(-165,30),(-245,190),(-80,340),(165,290),(240,60),(175,-100)],7)
road([(-490,365),(-665,80),(-515,-350),(-135,-655),(245,-600),(625,-230),(610,165),(270,465),(-125,480)],7,True)
# Irregular blocks grew between the older radial roads. Offset survey rows create
# varied quadrangles, rather than repeating concentric ribbons of houses.
town_boundary=Polygon(np.array([[-490,365],[-665,80],[-515,-350],[-135,-655],[245,-600],[625,-230],[610,165],[270,465],[-125,480]])+CAP).buffer(-18)
holy=Polygon(np.array([[-210,-205],[-210,150],[-100,270],[205,225],[225,-195]])+CAP)
cells=[]
for j,y in enumerate(np.arange(-1000,1001,95)):
    for x in np.arange(-1000,1001,105):cells.append([x+(j%2)*23+rng.uniform(-20,20),y+rng.uniform(-20,20)])
vor=Voronoi(np.array(cells)+CAP)
for edge in vor.ridge_vertices:
    if -1 in edge:continue
    line=LineString(vor.vertices[edge]).intersection(town_boundary).difference(holy)
    parts=list(line.geoms) if hasattr(line,'geoms') else [line]
    for part in parts:
        if part.geom_type=='LineString' and part.length>22:
            road(np.array(part.coords)-CAP,4.8)

def paved_rect(center,w,d):
    xs=np.linspace(-w/2,w/2,max(3,int(w/3)+1));ys=np.linspace(-d/2,d/2,max(3,int(d/3)+1))
    p=np.array([[center[0]+x,center[1]+y] for y in ys for x in xs])+CAP
    v=np.column_stack([p,ground_many(p)+.08]);f=[];n=len(xs)
    for j in range(len(ys)-1):
        for i in range(n-1):a=j*n+i;f.extend([[a,a+1,a+n+1],[a,a+n+1,a+n]])
    roads.part(v,f,'paving')
paved_rect((0,-123),125,100)
paved_rect((20,-303),100,80)
paved_rect((-415,165),72,64)

# Separate the old cathedral and later imperial spire: no tower through the nave.
put('SM_Civ30_Cathedral',CAP+[0,5],1.0)
put('SM_Civ33_MagicTower',CAP+[107,76],1.0)
put('SM_Civ30_Gatehouse',CAP+[0,-177],.58)
precinct=np.array([[-146,-177],[-146,35],[-118,177],[48,195],[151,143],[172,-70],[144,-177]])+CAP

def wall_path(points,height=14,width=3.5,closed=False,gate=None,wall=stone):
    p=smooth(points,closed,step=6) if len(points)>4 else np.array(points,float)
    if len(p)<3:
        p=np.linspace(p[0],p[-1],max(3,int(np.linalg.norm(p[-1]-p[0])/6)))
    g=ground_many(p);wall.band(p,g-3,g+height,width,'stone',closed)
    wall.band(p,g+height-.35,g+height+.35,width+.45,'trim',closed)
    # Two low parapets leave a continuous walkable wall crown.
    tan=np.gradient(p,axis=0);tan/=np.maximum(np.linalg.norm(tan,axis=1,keepdims=True),1e-6);side=np.column_stack([-tan[:,1],tan[:,0]])
    for sg in (-1,1):
        pp=p+side*sg*(width*.5-.32);wall.band(pp,g+height,g+height+1.15,.62,'stone',closed)
    for i in range(0,len(p),2):
        yaw=np.degrees(np.arctan2(tan[i,1],tan[i,0]))
        for sg in (-1,1):wall.box([*(p[i]+side[i]*sg*(width*.5-.32)),g[i]+height+1.05],[2.2,.82,1.0],'trim',yaw)
    return p,g
wall_path(precinct,14,3.5)
wall_path([CAP+[-146,-177],CAP+[-18,-177]],14,3.5)
wall_path([CAP+[18,-177],CAP+[144,-177]],14,3.5)
for p in (precinct[0],precinct[2],precinct[4],precinct[-1]):put('SM_Civ30_Bastion',p,.48)

# Complete houses only. Street reservations and a spatial grid reject intersections.
road_reserve=unary_union([LineString(p).buffer(w/2+1.0) for p,w in roadlines])
plazas=unary_union([Polygon((np.array([[-w/2,-d/2],[w/2,-d/2],[w/2,d/2],[-w/2,d/2]])+center+CAP)) for center,w,d in [((0,-123),137,112),((20,-303),106,86),((-415,165),78,70)]])
precinct_poly=Polygon(precinct).buffer(12)
blocked=unary_union([road_reserve,plazas,precinct_poly]);occupied={};placed=[]
def clear(p,r):
    cell=np.floor(p/16).astype(int)
    for x in range(cell[0]-2,cell[0]+3):
        for y in range(cell[1]-2,cell[1]+3):
            for q,qr in occupied.get((x,y),[]):
                if np.linalg.norm(p-q)<r+qr+.8:return False
    return not blocked.intersects(Point(p).buffer(r))
def house(p,yaw):
    sc=float(rng.uniform(1.15,1.65));r=4.25*sc
    if not clear(p,r) or component(p)!=2:return
    corners=np.array([p+[-r,-r],p+[r,-r],p+[r,r],p+[-r,r]]);zz=ground_many(corners)
    if np.ptp(zz)>2.8:return
    z=float(max(ground(*p),zz.max()-.1))
    key='HouseA' if rng.random()<.55 else 'HouseB'
    put(key,p,sc,yaw,z+.025)
    pads.box([*p,float(zz.min()-1)],[6.1*sc,5.9*sc,z-float(zz.min())+1.02],'foundation',yaw)
    cell=tuple(np.floor(p/16).astype(int));occupied.setdefault(cell,[]).append((p,r));placed.append((p,r,yaw))

for ri,(p,w) in enumerate(roadlines):
    line=LineString(p)
    for dist in np.arange(7,line.length-6,13.5):
        q=np.array(line.interpolate(dist).coords[0]);t=np.array(line.interpolate(min(dist+1,line.length)).coords[0])-q;t/=max(np.linalg.norm(t),1e-8);side=np.array([-t[1],t[0]])
        for sg in (-1,1):
            off=w/2+rng.uniform(8.2,9.5);pt=q+side*sg*off
            house(pt,np.degrees(np.arctan2(t[1],t[0]))+90*sg)
            # Service yards and rear rows form blocks, rather than a single ribbon of buildings.
            if ri>=4:house(q+side*sg*(off+18),np.degrees(np.arctan2(t[1],t[0]))+90*sg)

# A market with actual open circulation and clustered stock, plus sacred gardens.
for i,x in enumerate([-38,-21,-4,13,30,47]):
    for sy in (-1,1):
        p=CAP+[x+20,-303+sy*28]
        put('Market' if i%2 else 'Market2',p,1.6,180 if sy>0 else 0)
        put('Crate',p+[3,sy*4],1.2,float(rng.integers(0,360)))
        put('Barrel',p+[-2,sy*4],1.1,float(rng.integers(0,360)))
for p in [CAP+[20,-303],CAP+[-415,165]]:put('Well',p,1.7)
for px in (-100,100):
    for py in (-106,-61,-16):
        put('Oak',CAP+[px,py],1.0,float(rng.uniform(0,360)))
        put('Bench',CAP+[px+(6 if px<0 else -6),py],1.3,90 if px<0 else -90)
for ri,(p,w) in enumerate(roadlines):
    line=LineString(p)
    for dist in np.arange(30,line.length-20,55):
        q=np.array(line.interpolate(dist).coords[0]);t=np.array(line.interpolate(dist+1).coords[0])-q;t/=np.linalg.norm(t);side=np.array([-t[1],t[0]])
        for sg in (-1,1):
            pt=q+side*sg*(w/2+.55)
            if not precinct_poly.contains(Point(pt)):
                put('Lamp',pt,1.35,np.degrees(np.arctan2(t[1],t[0])))
for i,(p,r,yaw) in enumerate(placed):
    if i%5==0:
        a=np.radians(yaw);pt=p+np.array([np.cos(a),np.sin(a)])*(r+1.4)
        if not road_reserve.contains(Point(pt)):put('Cart' if i%20==0 else 'Barrel',pt,1.0,yaw)

# Intentional small groves and gardens in unbuilt blocks; preserve streets and buildings.
for _ in range(2600):
    p=CAP+rng.uniform([-830,-820],[830,780]);r=4.7
    if component(p)!=2 or not clear(p,r):continue
    local=p-CAP
    if np.linalg.norm(local)<250:continue
    if rng.random()>.40+.24*np.sin(local[0]/88)*np.cos(local[1]/77):continue
    if np.ptp(ground_many([p,p+[10,0],p+[0,10]]))>8:continue
    put('Oak' if rng.random()<.8 else 'Pine',p,float(rng.uniform(.8,1.35)),float(rng.uniform(0,360)))
    cell=tuple(np.floor(p/16).astype(int));occupied.setdefault(cell,[]).append((p,r))

# Source masks confine the material improvement to Gosain's two offshore islands.
islands=np.isin(COMP,[1,2]);fade=np.clip(distance_transform_edt(islands)/2,0,1)
Image.fromarray(np.uint8(fade*255)).save(OUT/'T_Gosain37_Region.png')

for mesh,name in [(roads,'SM_Gosain37_CityStreets'),(stone,'SM_Gosain37_PrecinctWalls'),(pads,'SM_Gosain37_HouseFootings')]:
    manifest.append(mesh.write(name,ORIGIN))

# Record exact removals, preserving every other transform byte-for-byte in the source audit.
base=json.loads((ROOT/'Saved/Gosain37/baseline_foliage.json').read_text());remove={};outside={};removed=0
for c in base:
    tr=np.array(c['transforms']);local=tr[:,:2]/100-CAP if len(tr) else np.empty((0,2))
    # This milestone only replaces the capital district, not the coastal defenses or monastery.
    take=(np.abs(local[:,0])<960)&(np.abs(local[:,1])<980)&(tr[:,2]<-1900000)&(tr[:,2]>-2100000)
    if take.any():remove[c['name']]=np.flatnonzero(take).tolist();removed+=int(take.sum())
    keep=[r for r,t in zip(c['transforms'],take) if not t]
    outside[c['name']]=hashlib.sha256(json.dumps(keep,separators=(',',':')).encode()).hexdigest()

# Filter old combined roads/foundations in the same district without regenerating other regions.
def filter_old(name):
    p=SRC/'Civilizations36'/(name+'.obj');dest=OUT/(name+'_OutsideGosain37.obj')
    verts=[];lines=[]
    for line in p.open():
        if line.startswith('v '):
            x,y,z=map(float,line.split()[1:]);verts.append([x/100,-y/100,z/100])
        lines.append(line)
    v=np.array(verts);n=0
    with dest.open('w') as f:
        for line in lines:
            if line.startswith('f '):
                ix=[int(q.split('/')[0])-1 for q in line.split()[1:]];q=v[ix].mean(axis=0)
                # Cut only wholly local geometry; boundary triangles remain as road connections.
                local=v[ix,:2]-CAP
                if (np.abs(local[:,0])<960).all() and (np.abs(local[:,1])<980).all() and q[2]<-19000:n+=1;continue
            f.write(line)
    return {'name':name+'_OutsideGosain37','replaces_tag':'Civ36_'+name,'origin_m':[0,0,0],'removed_faces':n}
filtered=[filter_old('SM_Civ36_Roads'),filter_old('SM_Civ36_Foundations')]
report.update(complete_houses=len(placed),counts={k:len(v) for k,v in rows.items()},removed_instances=removed,scope='capital district only; coastal walls/bridges and monastery remain queued',new_meshes=manifest)
data={'origin_m':ORIGIN,'assets':assets,'instances':rows,'meshes':manifest,'filtered':filtered,'remove':remove,'outside_sha256':outside,'report':report,'roads':[{'points_m':p.tolist(),'width':w} for p,w in roadlines]}
(OUT/'Gosain37.json').write_text(json.dumps(data,indent=1))
(OUT/'build_report.json').write_text(json.dumps(report,indent=2))

# A reviewable planning diagram, separate from actual Unreal renders.
im=Image.new('RGB',(1200,1100),'#192c31');draw=ImageDraw.Draw(im)
def screen(p):return (600+(p[0]-CAP[0])*.53,530-(p[1]-CAP[1])*.53)
for p,w in roadlines:draw.line([screen(q) for q in p],fill='#dfc598',width=max(2,int(w*.53)))
for p,r,yaw in placed:
    x,y=screen(p);draw.rectangle([x-r*.45,y-r*.45,x+r*.45,y+r*.45],fill='#bc805b')
draw.polygon([screen(p) for p in precinct],outline='#eee2bb',width=4)
draw.text((35,30),'GOSAIN | Cathedral district, first repair checkpoint',fill='white',font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',27))
draw.text((35,1030),'Warm masonry: older precinct  |  Curved streets: later town  |  Markets, yards and gardens',fill='#eee2bb',font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19))
im.save(ROOT/'Docs/WorldDesign/Gosain37/Capital_Layout_Plan.png')
print(json.dumps(report,indent=2))
