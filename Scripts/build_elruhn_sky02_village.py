"""Terrain-aware tower-centered village, purchase plots and private landscape weights."""
from pathlib import Path
import ast,json,math,numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates
from shapely.geometry import Polygon,Point,LineString,box
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/ElRuhnSky02';O.mkdir(parents=True,exist_ok=True);S=B/'Saved/AdventureWorldSource';TAU=math.tau
tree=ast.parse((B/'Scripts/build_elruhn_sky01_assets.py').read_text());node=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Mesh');exec(compile(ast.Module(body=[node],type_ignores=[]),'shared mesh writer','exec'))
source_height=S/'height_valley_v14.npy'
H=np.load(source_height) if source_height.is_file() else np.fromfile(O/'terrain_height_f32.bin',dtype='<f4').reshape(1009,1009)
cx,cy=json.loads((B/'ArtSource/World/ElRuhnSky01/centering_applied.json').read_text())['island_center_m'];C=np.array([cx,cy])
def height(x,y):return float(map_coordinates(H,[[((y+600)*.84)],[((x+600)*.84)]],order=1,mode='nearest')[0])
base=height(cx,cy);farm=box(82,-215,180,-70);fountain=C+[0,-150]
roads=[]
def avoid_farm(points):
 block=box(70,-230,192,-58);inside=[i for i,p in enumerate(points) if block.contains(Point(p))]
 if not inside:return points
 first,last=min(inside),max(inside);boundary=block.exterior;start=boundary.project(Point(points[first-1]));end=boundary.project(Point(points[last+1]));length=boundary.length;delta=(end-start)%length
 if delta>length/2:delta-=length
 detour=[list(boundary.interpolate((start+t*delta)%length).coords)[0] for t in np.linspace(0,1,math.ceil(abs(delta)/2)+1)]
 return points[:first]+[list(p) for p in detour]+points[last+1:]
for radius,width in [(74,8),(148,7),(222,6)]:
 pts=[(C+radius*np.array([math.cos(a),math.sin(a)])).tolist() for a in np.linspace(0,TAU,361)];roads.append({'name':'Tower promenade' if radius==74 else 'Village circuit '+str(radius),'width':width,'points':avoid_farm(pts)})
# Radial streets link the circuits, avoiding the southern courtyard, farm and fountain.
for deg in [0,60,120,180,225]:
 a=math.radians(deg);points=[(C+np.array([math.cos(a),math.sin(a)])*r).tolist() for r in np.linspace(45,255,120)];roads.append({'name':'District lane '+str(deg),'width':5.5,'points':points})
roads.append({'name':'Ceremonial approach','width':11,'points':[(C+[0,y]).tolist() for y in np.linspace(-89,-129,40)]})
for sign in [-1,1]:
 pts=[(fountain+np.array([sign*18*math.sin(a),18*math.cos(a)])).tolist() for a in np.linspace(0,math.pi,70)];roads.append({'name':'Fountain square bypass','width':6,'points':pts})
roads.append({'name':'Sky dock road connection','width':7,'points':[(fountain+np.array([5*math.sin(t*math.pi),-18-t*82])).tolist() for t in np.linspace(0,1,60)]})
roadlines=[LineString(r['points']).buffer(r['width']/2) for r in roads]
old=[('Guild Hall','Guild',6),('Inherited House','House',2),('Seabreeze Inn','Inn',8),('Bakery','Bakery',1),('General Store','Shop',4),('Smithy','Smith',3),('Cottage A','House',5),('Cottage B','House',7),('Cottage C','House',9),('Cottage D','House',10)]
plots=[];occupied=[];skipped=[]
def candidate(radius,deg,size,kind,name,era,bp,existing=None):
 a=math.radians(deg);center=C+radius*np.array([math.cos(a),math.sin(a)]);yaw=a-math.pi/2;t=np.array([math.cos(yaw),math.sin(yaw)]);n=np.array([-t[1],t[0]])
 corners=[center+t*x+n*y for x,y in [(-size/2,-size/2),(size/2,-size/2),(size/2,size/2),(-size/2,size/2)]];poly=Polygon(corners)
 if poly.buffer(6).intersects(farm) or poly.buffer(6).intersects(Point(fountain).buffer(23)) or any(poly.buffer(3).intersects(p) for p in occupied):return False
 # Native roads must pass between plots; connection spurs will be added after acceptance.
 if any(poly.buffer(1).intersects(r) for r in roadlines):return False
 heights=[height(*p) for p in corners]+[height(*center)];relief=max(heights)-min(heights)
 if relief>5.5:skipped.append({'center':center.tolist(),'reason':'steep foundation','relief_m':relief});return False
 z=max(heights)+.12;front=center-n*(size/2+2);frontz=height(*front)+.08
 costs={'House':(8,0,0),'Guild':(12,2,0),'Inn':(10,0,0),'Shop':(8,0,0),'Smith':(10,2,0),'Chapel':(12,0,0),'Bank':(10,4,0),'Bath':(8,3,0),'Academy':(12,6,0),'Manor':(14,6,0),'Warehouse':(10,0,0),'Training':(8,0,0),'Bell':(6,2,0),'Castle':(16,8,4),'Bakery':(8,0,0)}
 p={'id':'ES02_%02d'%(len(plots)+1),'name':name,'kind':kind,'era':era,'center_m':[*center,z],'yaw_deg':math.degrees(yaw),'size_m':size,'relief_m':relief,'corners_xy':[p.tolist() for p in corners],'stake_m':[*front,frontz],'cost':costs[kind],'beds':2 if kind=='House' else 4 if kind=='Inn' else 3 if kind=='Manor' else 0,'blueprint':'/Game/Fantastic_Village_Pack/blueprints/buildings/BP_BLD_house_'+str(bp),'existing_actor_label':existing}
 plots.append(p);occupied.append(poly);return True
# Offset streets from lot centers; existing buildings become the settled inner neighborhood.
angles=[15,45,75,105,135,165,195,225,255,285,315,345]
oi=0
for deg in angles:
 if oi<len(old):name,kind,bp=old[oi]
 else:name,kind,bp='Village Chapel','Chapel',12
 if candidate(109,deg,32,kind,name,'Village',bp,name if oi<len(old) else None):oi+=1
assert oi>=len(old),'All existing homes/services need valid lots'
special=[('Chapel','Village Chapel','Village',12),('Bank','Royal Bank','LargeTown',13),('Bath','Public Bathhouse','LargeTown',14),('Academy','Magic Academy','LargeTown',6),('Manor','Lord\'s Residence','LargeTown',12),('Warehouse','Warehouse','Village',11),('Training','Knight School','Village',6),('Bell','Civic Bell House','LargeTown',13)]
si=0;homes=0
for radius,degrees in [(195,range(10,360,20)),(245,[20,40,80,100,140,160,200,220,260,280,340])]:
 for deg in degrees:
  if si<len(special):kind,name,era,bp=special[si];size=34
  else:
   kind='House';name=('Noble Residence ' if homes%5==4 else 'Commoner Home ')+str(homes+1);era='LargeTown' if homes%5==4 else 'Village';bp=[2,5,7,9,12][homes%5];size=28 if era=='Village' else 34
  if candidate(radius,deg,size,kind,name,era,bp):
   if si<len(special):si+=1
   else:homes+=1
assert si==len(special),si
for radius,degrees in [(195,range(10,360,20)),(253,range(10,360,20))]:
 for deg in degrees:
  name=('Noble Residence ' if homes%5==4 else 'Commoner Home ')+str(homes+1);era='LargeTown' if homes%5==4 else 'Village';bp=[2,5,7,9,12][homes%5]
  if candidate(radius,deg,24,'House',name,era,bp):homes+=1
assert homes>=8,'Reserve a useful housing expansion capacity'
# Shared physical foundations, subtle lot borders and corner stones, all above exact source terrain.
pads=Mesh();marks=Mesh();roadmesh=Mesh()
for p in plots:
 x,y,z=p['center_m'];size=p['size_m'];yaw=math.radians(p['yaw_deg']);low=min(height(*q) for q in p['corners_xy'])-.3
 pads.box((x,y,(low+z)/2),(size,size,z-low),'foundation',yaw)
 for k,(a,b) in enumerate(zip(p['corners_xy'],p['corners_xy'][1:]+p['corners_xy'][:1])):
  # Open the front edge for entry and an eventual storefront.
  if k==0:continue
  marks.beam([*a,z+.18],[*b,z+.18],.24,'trim',6)
 for q in p['corners_xy']:marks.profile([(.35,z),(.35,z+.9),(.45,z+1.05)],'trim',8,tuple(q))
 # Short terraced entry leading to the purchase marker and road.
 a=np.array(p['stake_m'][:2]);b=np.array(p['center_m'][:2]);b=a+(b-a)*.45;steps=max(1,math.ceil((z-p['stake_m'][2])/.2))
 for j in range(steps):
  f=(j+.5)/steps;pt=a+(b-a)*f;top=p['stake_m'][2]+(z-p['stake_m'][2])*(j+1)/steps;roadmesh.box((pt[0],pt[1],(top+low)/2),(4,np.linalg.norm(b-a)/steps+.04,top-low),'paving',yaw)
 # Link each front gate to its nearest road circuit.
 c=np.array(p['center_m'][:2])-C;radius=74 if np.linalg.norm(c)<140 else 148 if np.linalg.norm(c)<225 else 222;target=C+c/np.linalg.norm(c)*radius
 points=[(a*(1-f)+target*f).tolist() for f in np.linspace(0,1,24)]
 if not LineString(points).buffer(2).intersects(farm):roads.append({'name':p['id']+' access','width':3.6,'points':points})
def ribbon(points,width):
 p=np.array(points);d=np.gradient(p,axis=0);d/=np.maximum(np.linalg.norm(d,axis=1,keepdims=True),1e-8);normal=np.stack([-d[:,1],d[:,0]],axis=1);v=[]
 for c,n in zip(p,normal):
  for side in [-1,1]:x,y=c+n*width*.5*side;v.append([x,y,height(x,y)+.10])
 f=[]
 for i in range(len(p)-1):k=i*2;f.extend([[k,k+1,k+3],[k,k+3,k+2]])
 # Correct +Z winding for front-face ground ribbons.
 roadmesh.part(v,[q[::-1] for q in f],'paving')
for r in roads:ribbon(r['points'],r['width'])
for r in [22]:
 v=[[fountain[0],fountain[1],height(*fountain)+.12]]
 for a in np.linspace(0,TAU,129):x,y=fountain+r*np.array([math.cos(a),math.sin(a)]);v.append([x,y,height(x,y)+.12])
 roadmesh.part(v,[[0,i,i+1] for i in range(1,129)],'paving')
assets=[pads.export('SM_ES02_BuildingFoundations'),marks.export('SM_ES02_PlotBoundaries'),roadmesh.export('SM_ES02_VillageStreets')]
# Remove superseded center dirt routes only on a private copy of the island material's weight map.
baseline_weights=O/'Original_Island_Weights.png'
if not baseline_weights.exists():baseline_weights.write_bytes((S/'T_IV_Layer32_Weights.png').read_bytes())
weights=np.asarray(Image.open(baseline_weights)).copy();X,Y=np.meshgrid(np.linspace(-600,600,1009),np.linspace(-600,600,1009));rr=np.hypot(X-cx,Y-cy);farmmask=(X>75)&(X<188)&(Y>-225)&(Y<-65);reset=(rr<252)&~farmmask
weights[reset,0]=np.minimum(255,weights[reset,0].astype(int)+weights[reset,1]);weights[reset,1]=0
for r in roads:
 d=np.full(H.shape,1e6)
 for x,y in r['points'][::3]:d=np.minimum(d,np.hypot(X-x,Y-y))
 amount=np.clip((r['width']/2+2-d)/3,0,1)*.95;use=(amount>0)&~farmmask
 weights[use,1]=np.maximum(weights[use,1],(amount[use]*255).astype('uint8'));weights[use,0]=(255-weights[use,1].astype(int)-weights[use,2].astype(int)-weights[use,3].astype(int)).clip(0,255).astype('uint8')
for p in plots:
 dx=X-p['center_m'][0];dy=Y-p['center_m'][1];yaw=math.radians(p['yaw_deg']);px=dx*math.cos(yaw)+dy*math.sin(yaw);py=-dx*math.sin(yaw)+dy*math.cos(yaw);mask=(abs(px)<p['size_m']/2+1)&(abs(py)<p['size_m']/2+1)
 weights[mask]=[0,255,0,0]
mask=(rr<47)|((abs(X-cx)<18)&(Y>cy-90)&(Y<cy));weights[mask]=[0,255,0,0]
Image.fromarray(weights).save(O/'T_ES02_VillageWeights.png')
H.astype('<f4').tofile(O/'terrain_height_f32.bin')
for p in plots:
 if p['existing_actor_label'] in ['Guild Hall','Inherited House']:
  p['released_starter_actor']=p['existing_actor_label'];p['existing_actor_label']=None
 if not p['existing_actor_label']:
  p['name']='Unassigned land '+p['id'];p['kind']=None;p['era']=None;p['blueprint']=None;p['cost']=[0,0,0];p['beds']=0;p['flexible_use']=True
report={'map':'/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky','center_m':[cx,cy,base],'tower_origin_m':[cx,cy,base],'fountain_m':[*fountain,height(*fountain)],'plots':plots,'roads':roads,'assets':assets,'prebuilt':sum(p['existing_actor_label'] is not None for p in plots),'purchase_slots':sum(p['existing_actor_label'] is None for p in plots),'skipped_steep_sites':skipped,'terrain_height_unchanged':True,'farm_reserved_bounds':[82,-215,180,-70]}
(O/'village_plan.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:report[k] for k in ['center_m','prebuilt','purchase_slots','skipped_steep_sites']},indent=2))
