"""Grounded settlement layouts, scenery and regional infrastructure."""
from pathlib import Path
import json,numpy as np
from scipy.ndimage import map_coordinates,label,gaussian_filter1d
from PIL import Image
from world_reference_v29 import global_height
from civilization_ground_v29 import ground
from build_civilization_assets_v29 import Mesh
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource';O=S/'Civilizations29';meta=json.loads((S/'world_design_v29.json').read_text());sites=meta['settlements'];D=dict(np.load(S/'world_reference_v29.npz'));cx=float(D['cx']);cy=float(D['cy']);m=float(D['mpp']);rng=np.random.default_rng(29210)
REF=Path('D:/DEVELOPMENT/Games/GuildSim-Lineage/GuildFounder-DesktopCopy/BaseProject/assets/map/kingdoms');landmask=np.zeros(D['height'].shape,bool)
for name in ['BiomeDrt','BiomePln','BiomeFst','BiomeJgl','BiomeMtn','BiomeIce']:landmask|=np.asarray(Image.open(REF/(name+'.png')).convert('RGB').resize((landmask.shape[1],landmask.shape[0]))).max(2)>35
def onland(x,y):
 px=int(round(cx-x/m));py=int(round(cy-y/m));return 0<=py<landmask.shape[0] and 0<=px<landmask.shape[1] and bool(landmask[py,px])
P='/Game/IsekaiVillage/AdventureWorld/Meshes/Civilizations/'
assets={q['name']:P+q['name'] for q in json.loads((O/'assets.json').read_text())}
assets.update({'HouseA':'/Game/AdvancedVillagePack/Meshes/SM_House_Var01','HouseB':'/Game/AdvancedVillagePack/Meshes/SM_House_Var02','Tent':'/Game/StylizedIsland/Mesh/Props/SM_Tent/SM_Stylized_Tent_Mesh/SM_Stylized_Tent','Market':'/Game/Fantastic_Village_Pack/meshes/props/construction/SM_PROP_market_v01_01','Cart':'/Game/AdvancedVillagePack/Meshes/SM_Cart_Var01','Boat':'/Game/AdvancedVillagePack/Meshes/SM_Boat','Sails':'/Game/Fantastic_Village_Pack/meshes/buildings/SM_BLD_windmill_sail','Oak':'/Game/SoStylized/Environment/Trees/Oak/SM_OakTree2','Pine':'/Game/SoStylized/Environment/Trees/Pine/SM_Pine01','Palm':'/Game/SoStylized/Environment/Trees/Coastal/SM_PalmTree01','DesertPalm':'/Game/SoStylized/Environment/Trees/Desert/SM_DesertPalmTree01'})
bounds=json.loads((B/'Saved/civilization_assets_v29.json').read_text());rows={k:[] for k in assets};roads=Mesh();foundations=Mesh();landmarks=[]
def h(x,y):return ground(x,y)
def field(k,x,y):return float(map_coordinates(D[k],[[cy-y/m],[cx-x/m]],order=1,mode='nearest')[0])
def add(key,x,y,z=None,scale=1,yaw=0,height=None,site=None):
 if key in ['Oak','Pine','Palm','DesertPalm'] and not onland(x,y):return
 if z is None:z=h(x,y)
 if height is not None:
  bb=bounds[assets[key]];scale=height*100/(bb['max'][2]-bb['min'][2]);z-=bb['min'][2]*scale/100
 sc=[scale]*3 if np.isscalar(scale) else list(scale)
 rows[key].append([float(x),float(y),float(z),*map(float,sc),float(yaw),site])
def ribbon(points,width,mat='path'):
 p=np.array(points);out=[]
 for a,b in zip(p[:-1],p[1:]):
  dist=np.linalg.norm(b-a);n=max(2,int(dist/24)+1)
  out.extend(a+(b-a)*t for t in np.linspace(0,1,n,endpoint=False))
 out.append(p[-1]);p=np.array(out);tan=np.gradient(p,axis=0);tan/=np.maximum(np.linalg.norm(tan,axis=1,keepdims=True),1e-5);side=np.column_stack([-tan[:,1],tan[:,0]])*width*.5
 v=[]
 for a,b in zip(p-side,p+side):
  for q in [a,b]:v.append([*q,h(*q)+.12])
 f=[]
 for j in range(len(p)-1):a=2*j;f.extend([[a,a+3,a+1],[a,a+2,a+3]])
 roads.part(v,f,mat)
def pad(x,y,z,w,d):foundations.box(x,y,z-12,w,d,12.8,'stone',.4)
def ringwall(x,y,r,n,scale=1,site=None):
 pts=[]
 for a in np.linspace(0,2*np.pi,n+1):pts.append([x+r*np.cos(a),y+r*np.sin(a)])
 for k,(a,b) in enumerate(zip(pts[:-1],pts[1:])):
  mid=(np.array(a)+b)/2;length=np.linalg.norm(np.array(b)-a);yaw=np.degrees(np.arctan2(b[1]-a[1],b[0]-a[0]));
  if k in [n//4,3*n//4]:
   add('SM_Civ29_Gatehouse',*mid,scale=[length/48,scale,scale],yaw=yaw,site=site)
   inward=(mid-np.array([x,y]));inward/=np.linalg.norm(inward)
   ribbon([mid-inward*90,mid+inward*140],18)
  else:add('SM_Civ29_CurtainWall',*mid,scale=[length/42,scale,scale],yaw=yaw,site=site)
  if k%12==0:add('SM_Civ29_Banner',*mid,z=h(*mid)+31*scale,scale=scale,site=site)
  if k%4==0:add('SM_Civ29_Bastion',*a,scale=scale,site=site)
for si,q in enumerate(sites):
 x,y=q['xy_m'];r=q['radius_m'];culture=q['culture'];kind=q['kind'];level=q['ground_m'];q['instance_start']={k:len(v) for k,v in rows.items()}
 # Two crooked main streets leave space for district squares and natural outskirts.
 if culture not in ['nomad','cult','harbor']:
  for off in [-r*.27,r*.27]:ribbon([[x+t,y+off+35*np.sin(t/(r*.38))] for t in np.linspace(-r*.85,r*.85,35)],15 if kind=='city' else 9)
  ribbon([[x+25*np.sin(t/(r*.5)),y+t] for t in np.linspace(-r*.9,r*.9,35)],19 if kind=='city' else 10)
 n={'city':700,'town':140,'village':32}[kind]
 if culture in ['nomad','cult']:n={'city':105,'town':45,'village':20}[kind]
 for k in range(n*4):
  if n<=0:break
  u,v=rng.uniform(-r*.82,r*.82,2)
  if culture=='nomad':
   hub=[(-.42,-.3),(.36,-.4),(-.28,.35),(.42,.32)][k%4]
   u=hub[0]*r+rng.normal(0,r*.17);v=hub[1]*r+rng.normal(0,r*.17)
  if (u/r)**2+(v/r)**2>.78:continue
  if culture in ['citadel','religious','arcane','cult'] and np.hypot(u,v)<r*.26:continue
  if abs(u)<29 or min(abs(v-r*.27-35*np.sin(u/(r*.38))),abs(v+r*.27-35*np.sin(u/(r*.38))))<24:continue
  # Discrete parcels prevent overlapping houses while leaving varied orientations.
  spacing=43 if kind=='city' else 32;u=round(u/spacing)*spacing+rng.uniform(-5,5);v=round(v/spacing)*spacing+rng.uniform(-5,5)
  if abs(u)<30 or min(abs(v-r*.27-35*np.sin(u/(r*.38))),abs(v+r*.27-35*np.sin(u/(r*.38))))<30:continue
  if culture=='citadel' and abs(np.hypot(u,v-r*.1)-r*.4)<42:continue
  if culture=='arcane' and any(np.hypot(u-r*.42*np.cos(a),v-r*.42*np.sin(a))<70 for a in np.linspace(0,2*np.pi,7,endpoint=False)):continue
  if culture=='farming' and min(np.hypot(u+r*.5,v-r*.1),np.hypot(u-r*.5,v+r*.1))<75:continue
  if 'taken' not in q:q['taken']=[]
  if any(np.hypot(u-a,v-b)<spacing*.8 for a,b in q['taken']):continue
  q['taken'].append([u,v]);xx=x+u;yy=y+v;zz=h(xx,yy);yaw=float(rng.choice([0,90,180,270])+rng.uniform(-9,9))
  if culture in ['nomad','cult']:
   add('Tent',xx,yy,height=rng.uniform(6,10),yaw=rng.uniform(0,360),site=si)
   if k%5==0:add('Cart',xx+12,yy+7,height=3,site=si)
  elif culture in ['wetland','harbor']:
   add('SM_Civ29_StiltHouse',xx,yy,z=zz+7,scale=rng.uniform(.7,1.05),yaw=0,site=si)
   tx=x+(-r*.35 if u<0 else r*.35);length=abs(tx-xx)
   for j in range(max(1,int(np.ceil(length/24)))):
    t=(j+.5)/max(1,int(np.ceil(length/24)));bx=xx+(tx-xx)*t
    add('SM_Civ29_Boardwalk',bx,yy-15,z=h(bx,yy-15)+6,yaw=90,site=si)
  else:
   ht=rng.uniform(31,43) if kind=='city' else rng.uniform(20,29)
   add('HouseA' if k%3 else 'HouseB',xx,yy,z=zz+1,height=ht,yaw=yaw,site=si)
   pad(xx,yy,zz,ht*.85,ht*.85)
  n-=1
 # Civil and religious landmarks, distinct from generic housing.
 if culture in ['citadel','religious']:
  sc=2.5 if culture=='citadel' else 1.1 if kind=='city' else .7
  add('SM_Civ29_Cathedral',x,y+r*.1,scale=sc,site=si);landmarks.append({'name':q['name'],'xy_m':[x,y],'z':level,'culture':culture,'radius':r})
  if kind!='village':
   ringwall(x,y,r*.93,max(24,int(r*2*np.pi/42)),1.5 if culture=='citadel' else 1,si)
   if culture=='citadel':
    ringwall(x,y+r*.1,r*.4,60,1.6,si)
    for u in [-r*.63,r*.63]:add('SM_Civ29_SacredTower',x+u,y-r*.54,scale=2,site=si)
 elif culture=='arcane':
  add('SM_Civ29_ArcaneTower',x,y,scale=2 if kind=='city' else .9,site=si)
  for a in np.linspace(0,2*np.pi,7,endpoint=False):
   u=x+r*.42*np.cos(a);v=y+r*.42*np.sin(a);add('SM_Civ29_Manufactory',u,v,scale=1 if kind=='city' else .6,yaw=np.degrees(a),site=si)
   ribbon([[x,y],[u,v]],3,'conduit')
  if kind=='city':landmarks.append({'name':'Kelsin arcane manufacturing city','xy_m':[x,y],'z':level,'culture':culture,'radius':r})
 elif culture=='cult':
  add('SM_Civ29_Sanctuary',x,y,scale=1.7 if kind!='village' else .8,site=si)
  for a in np.linspace(0,2*np.pi,6,endpoint=False):add('SM_Civ29_Bastion',x+np.cos(a)*r*.62,y+np.sin(a)*r*.62,scale=.6,site=si)
  landmarks.append({'name':q['name'],'xy_m':[x,y],'z':level,'culture':culture,'radius':r})
 elif culture=='nomad':
  for u,v in [(-25,-20),(22,35),(47,-7),(-50,25)]:add('Market',x+u,y+v,height=8,site=si)
  if kind=='city':landmarks.append({'name':'Yozuan caravan gathering','xy_m':[x,y],'z':level,'culture':culture,'radius':r})
 elif culture=='farming':
  for u,v in [(-r*.5,r*.1),(r*.5,-r*.1)]:
   xx=x+u;yy=y+v;zz=h(xx,yy);add('SM_Civ29_Mill',xx,yy,scale=1.3,site=si);add('Sails',xx,yy-10,zz+26,scale=2,site=si)
   add('SM_Civ29_Granary',xx+50,yy,scale=1.2,site=si)
  if kind=='city':landmarks.append({'name':'Rabaric farming capital','xy_m':[x,y],'z':level,'culture':culture,'radius':r})
 if culture in ['wetland','harbor']:
  for xx in [x-r*.35,x+r*.35]:
   for yy in np.arange(y-r*.8,y+r*.8,24):add('SM_Civ29_Boardwalk',xx,yy,z=h(xx,yy)+6,site=si)
  if culture=='harbor':landmarks.append({'name':q['name'],'xy_m':[x,y],'z':level,'culture':culture,'radius':r})
 # Planted courtyards and orchard strips within inhabited districts.
 if culture not in ['nomad','cult','harbor','wetland']:
  for k in range(110 if kind=='city' else 30):
   a=rng.uniform(0,2*np.pi);rr=rng.uniform(r*.3,r*.78);xx=x+rr*np.cos(a);yy=y+rr*np.sin(a)
   if any(np.hypot(xx-x-u,yy-y-v)<29 for u,v in q.get('taken',[])):continue
   add('Oak' if culture in ['farming','arcane'] else 'Pine',xx,yy,height=rng.uniform(13,22),site=si)
 # Market squares and civic trees join residences to their landmarks.
 if culture not in ['cult','nomad']:
  for k in range(5 if kind=='city' else 2):add('Market',x-r*.15+k*15,y-r*.24,height=6,site=si)
 for k in range(9000 if kind=='city' else 2400 if kind=='town' else 850):
  a=rng.uniform(0,2*np.pi);rad=rng.uniform(r*1.03,r*2.5);xx=x+rad*np.cos(a);yy=y+rad*np.sin(a)
  if culture=='farming' and np.sin(xx/230)+np.cos(yy/330)<.85:continue
  if np.sin(xx/320)+np.cos(yy/460)+np.sin((xx+yy)/720)<-.7:continue
  if field('coast',xx,yy)<200 or field('cliff',xx,yy)>.08:continue
  zz=h(xx,yy)
  if zz<-20585:continue
  tree='DesertPalm' if culture in ['nomad','cult'] else 'Palm' if culture in ['wetland','harbor'] else 'Pine' if culture in ['citadel','religious'] else 'Oak'
  if culture in ['nomad','cult']:continue
  add(tree,xx,yy,z=zz,height=rng.uniform(17,35),yaw=rng.uniform(0,360),site=si)
 q.pop('taken',None);q['instances']=sum(len(rows[k])-q['instance_start'][k] for k in rows);q.pop('instance_start')
# The smaller northern island is fortified beyond the central city: a coastal wall
# circuit and regular watch bastions follow its own coastline, avoiding sea bridges.
q=next(s for s in sites if s['culture']=='citadel');x,y=q['xy_m'];angles=np.linspace(0,2*np.pi,241,endpoint=False);outline=[]
for a in angles:
 rs=np.arange(1100,12500,35);xx=x+rs*np.cos(a);yy=y+rs*np.sin(a);co=map_coordinates(D['coast'],[cy-yy/m,cx-xx/m],order=1,mode='constant',cval=-1000);valid=np.where(co<300)[0];dist=rs[valid[0]]-70 if len(valid) else rs[-1];outline.append([x+dist*np.cos(a),y+dist*np.sin(a)])
outline=gaussian_filter1d(np.array(outline),1.4,axis=0,mode='wrap')
for k,(a,b) in enumerate(zip(outline,np.roll(outline,-1,axis=0))):
 mid=(a+b)*.5;length=np.linalg.norm(b-a)
 if field('coast',*mid)<120:continue
 n=max(1,int(np.ceil(length/55)))
 for t in (np.arange(n)+.5)/n:
  xx,yy=a+(b-a)*t;add('SM_Civ29_CurtainWall',xx,yy,scale=[length/n/42,1.2,2],yaw=np.degrees(np.arctan2(*(b-a)[::-1])))
 if k%10==0:add('SM_Civ29_SacredTower',*a,scale=1.6)
# Orchards and hedgerows make agricultural parcels read as lived-in land.
meta['agricultural_parcels']=[q for q in meta['agricultural_parcels'] if np.linalg.norm(q['center'])>19500]
for i,q in enumerate(meta['agricultural_parcels']):
 pts=np.array(q['corners'])
 for a,b in zip(pts,np.roll(pts,-1,axis=0)):
  for t in np.linspace(0,1,max(2,int(np.linalg.norm(b-a)/40))):
   xy=a+(b-a)*t
   if rng.random()<.76:add('Oak',*xy,height=rng.uniform(7,12),yaw=rng.uniform(0,360))
 if i%12==0:
  x,y=q['center'];add('SM_Civ29_Granary',x,y,scale=.7)
# The farming capital has a readable belt of crop parcels close to its villages.
for q in [q for q in sites if q['culture']=='farming' and q['kind'] in ['city','town']]:
 x,y=q['xy_m'];r=q['radius_m']
 for k in range(22 if q['kind']=='city' else 9):
  a=k*2.39996;rad=r*(1.25+.65*(k%3));fx=x+rad*np.cos(a);fy=y+rad*np.sin(a);w=160 if q['kind']=='city' else 95;length=w*1.55
  if field('coast',fx,fy)<600:continue
  v=[];nx=12;ny=16
  for j in range(ny+1):
   for i in range(nx+1):
    u=(i/nx-.5)*w;t=(j/ny-.5)*length;xx=fx+u*np.cos(a)-t*np.sin(a);yy=fy+u*np.sin(a)+t*np.cos(a);v.append([xx,yy,h(xx,yy)+.12])
  f=[]
  for j in range(ny):
   for i in range(nx):
    aa=j*(nx+1)+i;f.extend([[aa,aa+1,aa+nx+2],[aa,aa+nx+2,aa+nx+1]])
  f=[face for face in f if onland(*np.asarray(v)[face,:2].mean(0))]
  roads.part(v,f,'cropgold' if k%3==0 else 'cropgreen')
  for t in np.linspace(-length*.5,length*.5,15):
   xx=fx+w*.53*np.cos(a)-t*np.sin(a);yy=fy+w*.53*np.sin(a)+t*np.cos(a);add('Oak',xx,yy,height=rng.uniform(7,10))
# Tidal reed banks and palm clumps, only on terrain above water.
wet=D['wetland'];valid=(wet>.25)&(D['channel']<.2)&(D['height']>-20599)&(D['height']<-20565)
py,px=np.where(valid)
for k in range(3600):
 j=int(rng.integers(len(px)));x=(cx-px[j])*m+rng.uniform(-35,35);y=(cy-py[j])*m+rng.uniform(-35,35);z=h(x,y)
 if z<-20599:continue
 add('SM_Civ29_Reeds',x,y,z=z,scale=rng.uniform(3,6),yaw=rng.uniform(0,360))
 if k%7==0:add('Palm',x+12,y+15,height=rng.uniform(20,34),yaw=rng.uniform(0,360))
# A raised harbor pier explicitly reaches the nearest tidal water cell.
q=next(q for q in sites if q['culture']=='harbor');x,y=q['xy_m']
py,px=np.where((D['channel']>.90)&(D['height']<-20599));wx=(cx-px)*m;wy=(cy-py)*m;j=int(np.argmin((wx-x)**2+(wy-y)**2));target=np.array([wx[j],wy[j]]);start=np.array([x,y]);length=np.linalg.norm(target-start);direction=(target-start)/length;yaw=np.degrees(np.arctan2(direction[1],direction[0]))-90
for t in np.linspace(0,1,max(2,int(length/23)+1)):
 xy=start+(target-start)*t;z=max(-20595.,h(*xy)+5);add('SM_Civ29_Boardwalk',*xy,z=z,yaw=yaw)
for side in [-1,1]:add('Boat',target[0]+direction[1]*22*side,target[1]-direction[0]*22*side,z=-20599.3,height=4,yaw=yaw+90)
# Oasis vegetation follows real spring margins rather than arbitrary desert dots.
for spring in meta['oasis_sites']:
 x,y=spring['xy_m'];rx,ry=spring['radius_m']
 for j in range(45):
  a=rng.uniform(0,2*np.pi);rr=rng.uniform(1.10,1.8);xx=x+rx*rr*np.cos(a);yy=y+ry*rr*np.sin(a)
  add('DesertPalm',xx,yy,height=rng.uniform(15,25),yaw=rng.uniform(0,360))
# Boats sit in the connected tidal channels, at the ocean surface.
py,px=np.where((D['channel']>.97)&(D['coast']>300))
for k in range(min(32,len(px))):
 j=int(rng.integers(len(px)));add('Boat',(cx-px[j])*m,(cy-py[j])*m,z=-20599.3,height=3.5,yaw=rng.uniform(0,360))
# Adapt retaining-wall foundations to the height difference along each segment.
for p in rows['SM_Civ29_CurtainWall']:
 a=np.radians(p[6]);dx=20*p[3]*np.cos(a);dy=20*p[3]*np.sin(a)
 variation=max(abs(h(p[0]+dx,p[1]+dy)-p[2]),abs(h(p[0]-dx,p[1]-dy)-p[2]))
 p[5]=max(p[5],(variation+3)/11)
roads.write('SM_Civ29_Roads');foundations.write('SM_Civ29_Foundations')
manifest=json.loads((O/'assets.json').read_text())
for mesh,name in [(roads,'SM_Civ29_Roads'),(foundations,'SM_Civ29_Foundations')]:manifest.append({'name':name,'vertices':len(mesh.v),'triangles':len(mesh.f),'materials':sorted(set(mesh.mat))})
(O/'assets.json').write_text(json.dumps(manifest,indent=2));assets.update({q['name']:P+q['name'] for q in manifest})
(S/'civilization_instances_v29.json').write_text(json.dumps({'assets':assets,'instances':rows,'landmarks':landmarks},indent=2));meta['settlements']=sites;meta['placed_instances']=sum(map(len,rows.values()));meta['regional_landmarks']=landmarks;(S/'world_design_v29.json').write_text(json.dumps(meta,indent=2));print({'instances':meta['placed_instances'],'counts':{k:len(v) for k,v in rows.items()},'landmarks':landmarks},flush=True)
