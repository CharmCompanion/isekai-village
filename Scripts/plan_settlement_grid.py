"""Farm revision plus a metre-based, versioned town construction plan."""
import json, math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont

BASE=Path('D:/DEVELOPMENT/Games/IsekaiVillage')
S=BASE/'Saved/AdventureWorldSource'
OUT=BASE/'Content/IsekaiVillage/AdventureWorld/Design'
OUT.mkdir(parents=True,exist_ok=True)
data=json.loads((S/'world.json').read_text())
H=np.load(S/'height.npy');old=H.copy();N=1009
axis=np.linspace(-600,600,N);X,Y=np.meshgrid(axis,axis)
mask=np.array(Image.open(S/'T_IV_Biome.png')).astype(float)/255
def smooth(a,b,v):
    t=np.clip((v-a)/(b-a),0,1);return t*t*(3-2*t)
def sample(x,y):
    u=np.clip((x+600)/1200*1008,0,1007.999);v=np.clip((y+600)/1200*1008,0,1007.999)
    i=int(u);j=int(v);a=u-i;b=v-j
    return float((H[j,i]*(1-a)+H[j,i+1]*a)*(1-b)+(H[j+1,i]*(1-a)+H[j+1,i+1]*a)*b)
def dist(x,y,points):
    best=np.full(np.broadcast(x,y).shape,1e6)
    for (a,b),(c,d) in zip(points,points[1:]):
        t=np.clip(((x-a)*(c-a)+(y-b)*(d-b))/max((c-a)**2+(d-b)**2,.0001),0,1)
        best=np.minimum(best,np.hypot(x-a-t*(c-a),y-b-t*(d-b)))
    return best
# Erase only the former farm's dirt overlay. The wider world stays byte-identical.
farm_region=(X>30)&(X<212)&(Y>-312)&(Y<-193)
mask[:,:,0]=np.where(farm_region,0,mask[:,:,0])
# One level terrace directly beside the existing village; skirts blend into the meadow.
farm_plateau=1-smooth(0,10,np.maximum.reduce([92-X,X-164,-203-Y,Y+85,np.zeros_like(X)]))
H=H*(1-farm_plateau)+24.5*farm_plateau
fields=[{'id':f'FIELD_{i+1:02}','center':[x,y],'size':[24,26],'crop':crop} for i,(x,y,crop) in enumerate([(110,-145,'Wheat'),(146,-145,'Vegetables'),(110,-181,'Wheat'),(146,-181,'Pumpkins')])]
for f in fields:
    x,y=f['center'];z=24.5;d=np.maximum(abs(X-x)/12,abs(Y-y)/13)
    weight=1-smooth(1,1.22,d);H=H*(1-weight)+z*weight
    # Subtle ridged soil is painted; no giant raised platforms.
    soil=(1-smooth(.96,1.02,d))*(.88+.10*np.cos((X-x)*math.pi))
    mask[:,:,0]=np.maximum(mask[:,:,0],soil)
farm_main={'name':'Farmhouse Road','width':3,'points':[(123,-66),(128,-77),(130,-87)]}
farm_service={'name':'Farm Service Lane','width':2,'points':[(130,-108),(128,-118),(128,-163),(128,-201)]}
farm_cross={'name':'Field Access','width':1.8,'points':[(94,-163),(162,-163)]}
data['routes']=[r for r in data['routes'] if r['name']!='Farm Lane']+[farm_main,farm_service,farm_cross]
data['buildings']=[([name,130,-98,r,variant,yaw] if name=='Farmhouse' else [name,x,y,r,variant,yaw]) for name,x,y,r,variant,yaw in data['buildings']]
for r in [farm_main,farm_service,farm_cross]:
    d=dist(X,Y,r['points']);road=1-smooth(r['width']*.7,r['width']+1,d)
    mask[:,:,0]=np.maximum(mask[:,:,0],road)
# Preserve all height samples outside the four field terraces.
raw=np.rint(32768+H*64).astype('<u2');raw.tofile(S/'IV_Adventure_Farm_v02.r16')
Image.fromarray(raw).save(S/'IV_Adventure_Farm_v02.png')
Image.fromarray(np.stack([raw>>8,raw&255,np.zeros_like(raw),np.full_like(raw,255)],-1).astype('uint8')).save(S/'T_IV_FarmHeight_RG.png')
Image.fromarray(np.rint(mask*255).astype('uint8')).save(S/'T_IV_Biome_Farm_v02.png')
np.save(S/'height_farm_v02.npy',H)
data['fields']=fields
(S/'world_farm_v02.json').write_text(json.dumps(data,indent=2))

boundary=[[-200,-150],[70,-150],[70,-225],[225,-225],[225,-145],[290,-80],[300,140],[230,300],[-80,300],[-190,200],[-220,20]]
def inside(x,y):
    c=False
    for (a,b),(d,e) in zip(boundary,boundary[1:]+boundary[:1]):
        if ((b>y)!=(e>y)) and x<(d-a)*(y-b)/(e-b)+a:c=not c
    return c
walls=boundary+[boundary[0]]
gates=[{'name':'South / Harbor Gate','center':[0,-150],'width':22}, {'name':'West / Horde Gate','center':[-215,-10],'width':26},{'name':'North / Expedition Gate','center':[230,300],'width':24},{'name':'East / Meadow Gate','center':[295,70],'width':20}]
# Broad reserved streets fit future districts while early meadows remain unpaved.
future_roads=[{'name':'North Civic Avenue','width':5,'points':[[-60,55],[-48,108],[-30,160],[40,205],[120,245],[200,265],[230,300]]},
 {'name':'Noble Crescent','width':5,'points':[[65,-50],[145,-18],[205,55],[235,135],[200,215],[120,245]]},
 {'name':'West Residential Lane','width':4,'points':[[-72,-37],[-125,-85],[-175,-40],[-165,55],[-125,130],[-90,180],[-30,160]]}]
catalogue={
 'CommonerHouse':{'cells':[2,2],'era':'Village','variants':['Timber cottage','Stone townhouse','Kingdom artisan home']},
 'GeneralShop':{'cells':[2,2],'era':'Village','variants':['Timber provisioner','Stone merchant shop','Royal emporium']},
 'Blacksmith':{'cells':[3,3],'era':'Village','variants':['Village forge','Stone smithy','Royal foundry']},
 'AdventurersGuild':{'cells':[4,4],'era':'Village','variants':['Timber guildhall','Stone adventurers hall','Royal expedition guild']},
 'Inn':{'cells':[3,3],'era':'Village','variants':['Country inn','Town coaching inn','Grand inn']},
 'Chapel':{'cells':[3,3],'era':'Village','variants':['Timber chapel','Stone church','Grand sanctuary']},
 'BankTreasury':{'cells':[3,3],'era':'LargeTown','variants':['Vault office','Town bank','Royal treasury']},
 'LordsManor':{'cells':[4,4],'era':'LargeTown','variants':['Steward residence','Baron manor','Ducal residence']},
 'NobleHouse':{'cells':[3,3],'era':'LargeTown','variants':['Country estate','Stone villa','Kingdom noble mansion']},
 'Bathhouse':{'cells':[3,3],'era':'LargeTown','variants':['Village bath','Stone bathhouse','Royal baths']},
 'Bakery':{'cells':[2,2],'era':'Village','variants':['Timber bakery','Town bakery','Artisan patisserie']},
 'Warehouse':{'cells':[3,3],'era':'Village','variants':['Timber barn','Stone warehouse','Royal storehouse']},
 'Academy':{'cells':[4,4],'era':'LargeTown','variants':['Apprentice lodge','Magic academy','Royal academy']},
 'TrainingGround':{'cells':[4,4],'era':'Village','variants':['Practice yard','Training court','Royal barracks']},
 'BellTower':{'cells':[2,2],'era':'LargeTown','variants':['Village bell','Stone belfry','Civic bell tower']},
 'Castle':{'cells':[6,6],'era':'Kingdom','variants':['Reserved estate','Reserved citadel','Architect DLC castle']}}
# Grid-aligned candidate reservations: chosen only if all cells remain valid.
requests=[('Chapel','Civic',(-55,125)),('BankTreasury','Civic',(75,115)),('LordsManor','Noble',(155,155)),('Bathhouse','Civic',(120,65)),('Academy','Civic',(5,185)),('TrainingGround','Defense',(-140,65)),('BellTower','Civic',(-15,90)),('Castle','Kingdom',(135,245)),('Warehouse','Commerce',(110,-105)),('AdventurersGuild','Civic',(10,125)),('Inn','Commerce',(165,-80)),('Blacksmith','Commerce',(-155,-90)),('GeneralShop','Commerce',(80,-100))]
cells=[];lookup={}
all_roads=data['routes']+future_roads
for iy,y in enumerate(range(-230,300,10)):
    for ix,x in enumerate(range(-220,300,10)):
        cx=x+5;cy=y+5;corners=[(x,y),(x+10,y),(x,y+10),(x+10,y+10),(cx,cy)]
        reason='available'
        if not all(inside(a,b) for a,b in corners):reason='outside'
        elif float(dist(cx,cy,walls))<14:reason='rampart'
        elif any(float(dist(cx,cy,r['points']))<r['width']+8 for r in all_roads):reason='road'
        elif 82<cx<182 and -220<cy<-80:reason='farm'
        elif math.hypot(cx,cy)<30:reason='grand_square'
        elif any(math.hypot(cx-a,cy-b)<r+8 for _,a,b,r,_,_ in data['buildings']):reason='occupied'
        elif max(sample(a,b) for a,b in corners)-min(sample(a,b) for a,b in corners)>2.7:reason='slope'
        if any(math.hypot(cx-g['center'][0],cy-g['center'][1])<g['width'] for g in gates):reason='gate_approach'
        district='Noble' if cx>140 and cy>40 else 'Civic' if cy>85 else 'Commoner' if cx<0 else 'Commerce'
        cell={'id':f'{ix}:{iy}','i':ix,'j':iy,'center':[cx,cy,round(sample(cx,cy),3)],'status':reason,'district':district}
        lookup[ix,iy]=cell;cells.append(cell)
reservations=[]
def reserve(kind,district,near,label=None):
    w,d=catalogue[kind]['cells'];options=[]
    for (i,j),c in lookup.items():
        group=[lookup.get((i+a,j+b)) for a in range(w) for b in range(d)]
        if any(g is None or g['status']!='available' for g in group):continue
        x=-220+(i+w/2)*10;y=-230+(j+d/2)*10
        relief=max(g['center'][2] for g in group)-min(g['center'][2] for g in group)
        if relief>max(4,w*1.3):continue
        options.append(((x-near[0])**2+(y-near[1])**2,i,j,x,y,group))
    if not options:return False
    _,i,j,x,y,group=min(options,key=lambda r:r[0])
    rid=f'{kind}_{sum(p["type"]==kind for p in reservations)+1:02}'
    for c in group:c['status']='reserved';c['reservation']=rid;c['district']=district
    reservations.append({'id':rid,'type':kind,'district':district,'era':catalogue[kind]['era'],'anchor':[i,j],'size_cells':[w,d],'center':[x,y,round(sample(x,y),3)],'cells':[g['id'] for g in group]})
    return True
# Largest plots first so landmark space cannot be consumed by cottages.
for k,d,p in sorted(requests,key=lambda q:catalogue[q[0]]['cells'][0],reverse=True):reserve(k,d,p)
for k,d,spots in [('NobleHouse','Noble',[(205,80),(195,145),(175,200),(240,170)]),('CommonerHouse','Commoner',[(-130,-60),(-95,-100),(-165,0),(-140,105),(-90,140),(35,-110),(90,0),(130,15),(195,-30),(-110,50),(-65,100),(75,160)])]:
    for p in spots:reserve(k,d,p)
plan={'version':2,'units':'metres','map':'/Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure','cell_size':10,'origin':[-220,-230],'dimensions':[52,53],'boundary':boundary,'eras':['Village','LargeTown','Kingdom'],'source_priority':['IsekaiVillage_GDD.md','User added civic/defense requirements','FFCC reference'], 'catalogue':catalogue,'cells':cells,'reservations':reservations,'future_roads':future_roads,'rampart_centerline':walls,'gates':gates,'farm':{'fields':fields,'roads':[farm_main,farm_service,farm_cross],'farmhouse':[130,-98],'terrace_bounds':[92,-203,164,-85],'terrace_height':24.5,'expansion_bounds':[170,-205,205,-120]}}
(OUT/'SettlementGrid.json').write_text(json.dumps(plan,indent=2))
# Render thin debug borders as an importable mesh, no collision or game geometry.
for category,selected in [('Available',[c for c in cells if c['status']=='available']),('Reserved',[c for c in cells if c['status']=='reserved']),('Protected',[c for c in cells if c['status'] not in ['available','reserved','outside']])]:
    verts=[];faces=[]
    for c in selected:
        cx,cy,_=c['center'];x=cx-5;y=cy-5
        for a,b,d,e in [(x,y,x+10,y),(x+10,y,x+10,y+10),(x+10,y+10,x,y+10),(x,y+10,x,y)]:
            vx=e-b;vy=a-d;length=max(math.hypot(vx,vy),.001);vx*=.055/length;vy*=.055/length
            points=[(a+vx,b+vy),(d+vx,e+vy),(d-vx,e-vy),(a-vx,b-vy)]
            n=len(verts)
            verts.extend([(px*100,py*100,(sample(px,py)+.35)*100) for px,py in points]);faces.extend([(n+1,n+2,n+3),(n+1,n+3,n+4)])
    # UE's OBJ translator preserves Z-up and reverses Y for handedness.
    lines=['o Grid'+category]+[f'v {x:.3f} {-y:.3f} {z:.3f}' for x,y,z in verts]+['vt 0 0','vn 0 0 1']+['f %d/1/1 %d/1/1 %d/1/1'%f for f in faces]
    (S/('SM_Grid_'+category+'.obj')).write_text('\n'.join(lines))
summary={'total_cells':len(cells),'available_cells':sum(c['status']=='available' for c in cells),'reserved_plots':len(reservations),'missing_types':[k for k,_,_ in requests if not any(r['type']==k for r in reservations)],'changed_height_samples':int(np.count_nonzero(H!=old))}
(OUT/'PlanValidation.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary))
