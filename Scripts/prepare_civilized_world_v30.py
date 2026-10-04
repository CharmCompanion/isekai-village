"""Water-safe population, gridded agricultural landscape, and overland routes."""
from pathlib import Path
import numpy as np,json,heapq
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt,map_coordinates,label,gaussian_filter1d
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource';P=B/'Scripts'
# Re-evaluate the authoritative lake/oasis shapes and clean biome colors before the
# old settlement and route paint. This preserves every authored irregular spring.
env={};exec(compile((P/'prepare_world_reference_v28.py').read_text().split('# Locate settlements')[0],'base ecology','exec'),env)
h=env['height'].copy();color=env['color'].copy();land=env['filled']&~env['lakes'];H,W=h.shape;M=env['M'];cx=env['cx'];cy=env['cy'];sea=env['sea'];coast=env['coast'];yy,xx=np.mgrid[:H,:W];X=(cx-xx)*M;Y=(cy-yy)*M
D=dict(np.load(S/'world_reference_v28.npz'));meta=json.loads((S/'world_design_v29.json').read_text());countries=env['countries'][:-1];cm=dict(zip(countries,env['cmasks'][:-1]));rng=np.random.default_rng(30041)
def smooth(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def sample(a,x,y,order=1):return map_coordinates(a,[cy-np.asarray(y)/M,cx-np.asarray(x)/M],order=order,mode='constant',cval=0)
# The existing sea-connected tidal creeks remain water, including their shoulders.
wetregion=cm['VylfodDominion']&(coast>0)&(coast<4400)&(Y<-12000);wetblend=(1-smooth(2200,4400,coast))*wetregion
bank=sea+3+np.maximum(coast,0)*.005+5*(.5+.5*np.sin(X/570)*np.cos(Y/730));h=h*(1-wetblend)+bank*wetblend
channel=np.zeros_like(h)
for offset in [-34000,-42000,-50000]:
 axis=offset+800*np.sin(Y/1800)+360*np.sin(Y/650);c=(1-smooth(75,190,np.abs(X-axis)))*wetregion*(1-smooth(2600,3900,coast));channel=np.maximum(channel,c)
h=h*(1-channel)+(sea-4)*channel
color=color*(1-wetblend[...,None]*.8)+np.array([.11,.24,.13])*wetblend[...,None]*.8
color=color*(1-channel[...,None])+np.array([.025,.15,.18])*channel[...,None]
water=~land|(channel>.025)|(h<sea+1);dry=~water;clear=distance_transform_edt(dry)*M
slope=np.hypot(*np.gradient(h,M));countryclear={n:distance_transform_edt(v)*M for n,v in cm.items()}
components,_=label(dry);usable=dry&(np.hypot(X,Y)>19000)&(D['cliff']<.055)&(D['mountain']<.42)&(slope<.11)
labels={'YozuanDesert':'Yozuan','DivineEmpireofGosain':'Gosain','KelsinFederation':'Kelsin','RabaricRepublic':'Rabaric','VylfodDominion':'Vylfod'}
roles={'YozuanDesert':'nomad','DivineEmpireofGosain':'religious','KelsinFederation':'arcane','RabaricRepublic':'farming','VylfodDominion':'wetland'}
relocated=[];sites=[]
def candidates(country,r,culture,component=None):
 valid=usable&cm[country]&(clear>r*1.65+180)&(countryclear[country]>r+100)
 if culture=='harbor':valid&=(coast<4200)&(Y<-19000)
 if component:valid&=components==component
 return np.column_stack(np.where(valid))
def place(q,wanted,component=None):
 r=q['radius_m'];cand=candidates(q['country'],r,q['culture'],component)
 if not len(cand):raise ValueError(('no dry foundation',q))
 xy=np.column_stack([(cx-cand[:,1])*M,(cy-cand[:,0])*M]);score=np.sum((xy-wanted)**2,axis=1)
 for old in sites:
  delta=np.linalg.norm(xy-np.array(old['xy_m']),axis=1);score[delta<r+old['radius_m']+650]=np.inf
 j=np.argmin(score)
 if not np.isfinite(score[j]):raise ValueError(('no separated foundation',q))
 q['xy_m']=xy[j].tolist();py,px=cand[j];q['pixel']=[int(px),int(py)];q['land_component']=int(components[py,px]);q['water_clearance_m']=float(clear[py,px]);q['id']='site_'+str(len(sites)).zfill(3)
 if np.linalg.norm(xy[j]-wanted)>100:relocated.append({'name':q['name'],'from':list(wanted),'to':q['xy_m'],'distance_m':float(np.linalg.norm(xy[j]-wanted))})
 sites.append(q)
# Keep identities and move the entire site, not individual buildings, off water.
for old in meta['settlements']:
 q={k:old[k] for k in ['name','country','kind','culture','radius_m']};wanted=np.array(old['xy_m']);px,py=old['pixel'];comp=int(components[py,px]) if old['culture']=='citadel' or 'Northern island' in old['name'] else None
 if q['culture']=='citadel':q['radius_m']=850
 place(q,wanted,comp)
print({'existing_sites_placed':len(sites)},flush=True)
# A hierarchy of regional towns and satellite villages fills the intervening land.
# Farming sites prefer intersections of the national survey grid.
targets={'YozuanDesert':23,'DivineEmpireofGosain':22,'KelsinFederation':25,'RabaricRepublic':44,'VylfodDominion':25}
for country,target in targets.items():
 while sum(q['country']==country for q in sites)<target:
  n=sum(q['country']==country for q in sites);kind='town' if n%4==0 else 'village';r=400 if kind=='town' else 190;culture=roles[country]
  if country=='YozuanDesert' and n%7==0:culture='cult'
  cand=candidates(country,r,culture)
  if len(cand)>9000:cand=cand[rng.choice(len(cand),9000,replace=False)]
  xy=np.column_stack([(cx-cand[:,1])*M,(cy-cand[:,0])*M]);existing=np.array([q['xy_m'] for q in sites]);dist=np.min(np.linalg.norm(xy[:,None]-existing[None,:],axis=2),axis=1)
  # Best-spaced candidate, with a gentle preference for dry lowlands and grid nodes.
  score=dist/(1+slope[cand[:,0],cand[:,1]]*2)
  if country=='RabaricRepublic':score-=np.linalg.norm((xy+400)%800-400,axis=1)*3
  j=int(np.argmax(score));wanted=xy[j]
  role='caravan camp' if culture=='nomad' else 'hidden sanctuary' if culture=='cult' else 'market town' if kind=='town' and culture=='farming' else 'workshop town' if kind=='town' and culture=='arcane' else kind
  place({'country':country,'culture':culture,'kind':kind,'radius_m':r,'name':f'{labels[country]} {role} {n+1}'},wanted)
print({'expanded_sites':len(sites)},flush=True)
# Smooth inland foundation terraces stop well short of every water margin.
urban=np.zeros_like(h,dtype=bool)
for q in sites:
 x,y=q['xy_m'];r=q['radius_m'];dist=np.hypot(X-x,Y-y);inside=dist<r*.95;level=float(np.median(h[inside]));q['ground_m']=level
 blend=(1-smooth(r*.92,r*1.6,dist))*dry;h=h*(1-blend)+level*blend;urban|=dist<r*1.18
# Country-wide rectangular fields: preserve water, slopes, shore belts and towns.
slope=np.hypot(*np.gradient(h,M));farmvalid=cm['RabaricRepublic']&(clear>180)&(coast>300)&(slope<.18)&(h>sea+15)&(np.hypot(X,Y)>12000)&~urban
farmclear=distance_transform_edt(farmvalid)*M
farms=[];farmcover=np.zeros_like(dry);palette=np.array([[.34,.39,.12],[.46,.39,.17],[.25,.36,.13],[.43,.46,.19],[.31,.32,.13],[.48,.43,.20]])
# 800m blocks, two cropped parcels per block; lanes stay on one shared survey grid.
for gx in np.arange(np.floor(X[farmvalid].min()/800)*800,np.ceil(X[farmvalid].max()/800)*800+1,800):
 for gy in np.arange(np.floor(Y[farmvalid].min()/800)*800,np.ceil(Y[farmvalid].max()/800)*800+1,800):
  for half in [0,1]:
   ax=gx+28+half*400;bx=gx+372+half*400;ay=gy+28;by=gy+772
   tx,ty=np.meshgrid(np.linspace(ax,bx,5),np.linspace(ay,by,9))
   if not sample(farmvalid.astype(float),tx.ravel(),ty.ravel(),0).all():continue
   center=[(ax+bx)/2,(ay+by)/2];corners=[[ax,ay],[bx,ay],[bx,by],[ax,by]];k=len(farms);col=palette[int(rng.integers(len(palette)))];sel=(X>=ax)&(X<=bx)&(Y>=ay)&(Y<=by);farmcover|=sel
   color[sel]=col*(.96+.04*np.sin(X[sel,None]/9));farms.append({'center':center,'corners':corners,'angle':0,'color':(col*255).astype(int).tolist(),'crop':k%6})
print({'gridded_farms':len(farms)},flush=True)
# Connected farm-lane grid, clipped to dry usable land; town connectors below join it.
gridroutes=[]
def runs(points,valid):
 start=None
 for j,yes in enumerate(np.r_[valid,False]):
  if yes and start is None:start=j
  if not yes and start is not None:
   if j-start>=4:yield points[start:j]
   start=None
laneok=cm['RabaricRepublic']&(clear>140)&(coast>250)&(slope<.22)&(np.hypot(X,Y)>12000)&~urban
for axis in [0,1]:
 vals=X[farmvalid] if axis==0 else Y[farmvalid];other=Y[farmvalid] if axis==0 else X[farmvalid]
 for fixed in np.arange(np.floor(vals.min()/800)*800,np.ceil(vals.max()/800)*800+1,800):
  t=np.arange(np.floor(other.min()/80)*80,np.ceil(other.max()/80)*80,80);p=np.column_stack([np.full_like(t,fixed),t]) if axis==0 else np.column_stack([t,np.full_like(t,fixed)])
  ok=sample(laneok.astype(float),p[:,0],p[:,1],0)>.5
  for path in runs(p,ok):gridroutes.append({'country':'RabaricRepublic','kind':'farm_lane','width_m':10 if round(fixed/800)%3 else 15,'points_m':path.tolist()})
# Persist the terrain/population stage separately so routing can be refined independently.
np.savez_compressed(S/'networks30_checkpoint.npz',h=h,color=color,clear=clear,slope=slope,X=X,Y=Y,channel=channel,wetblend=wetblend,urban=urban,farmcover=farmcover,dry=dry,water=water)
(S/'networks30_checkpoint.json').write_text(json.dumps({'sites':sites,'meta':meta,'farms':farms,'gridroutes':gridroutes,'relocated':relocated}))
# A* on a conservative 320m grid. Clearance prohibits diagonal corner cutting
# across lakes and narrow creeks; no fictitious bridges or roads over the sea.
# Water keeps absolute priority. Land passes use a terrain cost rather than
# disconnecting whole provinces behind an arbitrary slope threshold.
localenv={};exec(compile((P/'build_puzzle_continent_v30.py').read_text().split('# Remaining branches')[0].replace('from world_reference_v30 import global_height',''),'local water','exec'),localenv)
rd,lk,ww,wl,wa=localenv['hydro'](X,Y)
localwater=(np.hypot(X,Y)<15000)&(np.abs(Y)<12000)&((rd<ww+60)|(lk<1.12))
water=water|localwater;dry=~water;clear=distance_transform_edt(dry)*M
stride=4;step=M*stride;walk=(clear>step*.8)&(slope<1.20)&(np.hypot(X,Y)>9500)
walk=walk[::stride,::stride];gh,gw=walk.shape;cost=(1+np.minimum(slope,2)*50+D['mountain']*6+D['cliff']*110)[::stride,::stride]
roadlabels,_=label(walk);wy,wx=np.where(walk);walkxy=np.column_stack([wx,wy]);used=np.zeros_like(cost)
def nearest(q,component=None):
 px,py=q['pixel'];d=(wx-px/stride)**2+(wy-py/stride)**2
 if component is not None:d=np.where(roadlabels[wy,wx]==component,d,np.inf)
 j=np.argmin(d);return (int(wy[j]),int(wx[j]))
def route(start,goal):
 sy,sx=start;gy,gx=goal;heap=[(0,0,sy,sx)];dist={start:0.};prev={}
 while heap:
  _,current,y,x=heapq.heappop(heap)
  if current!=dist.get((y,x)):continue
  if (y,x)==goal:break
  for dy,dx in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
   ny,nx=y+dy,x+dx
   if not(0<=ny<gh and 0<=nx<gw) or not walk[ny,nx] or not walk[y,nx] or not walk[ny,x]:continue
   c=float(cost[ny,nx])*(.7 if used[ny,nx] else 1);nd=current+c*(1.41421356 if dx*dy else 1)
   if nd<dist.get((ny,nx),1e30):dist[(ny,nx)]=nd;prev[(ny,nx)]=(y,x);heapq.heappush(heap,(nd+.7*np.hypot(ny-gy,nx-gx),nd,ny,nx))
 else:return []
 p=[goal]
 while p[-1]!=start:p.append(prev[p[-1]])
 for y,x in p:used[y,x]=1
 return np.array([[(cx-x*stride)*M,(cy-y*stride)*M] for y,x in p[::-1]])
# MST plus nearby secondary links; countries sharing land are connected together.
nodes=[nearest(q) for q in sites];parent=list(range(len(sites)))
def root(a):
 while parent[a]!=a:a=parent[a]
 return a
edges=[]
for i in range(len(sites)):
 for j in range(i):
  if roadlabels[nodes[i]]==roadlabels[nodes[j]]:edges.append((np.linalg.norm(np.array(sites[i]['xy_m'])-sites[j]['xy_m']),i,j))
edges.sort();links=[];degree=np.zeros(len(sites),int)
for dist,i,j in edges:
 if root(i)!=root(j):parent[root(i)]=root(j);links.append((i,j));degree[i]+=1;degree[j]+=1
for dist,i,j in edges:
 if dist<8500 and (degree[i]<2 or degree[j]<2) and (i,j) not in links:links.append((i,j));degree[i]+=1;degree[j]+=1
routes=[]
for k,(i,j) in enumerate(links):
 approach=[]
 for a,b in [(i,j),(j,i)]:
  q=sites[a];x,y=q['xy_m'];sgn=1 if sites[b]['xy_m'][1]>y else -1
  temp={'pixel':[cx-x/M,cy-(y+sgn*q['radius_m']*1.35)/M]};approach.append(nearest(temp,int(roadlabels[nodes[a]])))
 p=route(*approach)
 if len(p)==0:raise ValueError(('unroutable sites',i,j))
 if len(p)==1:p=np.vstack([p,p])
 # Roads enter through the existing north/south street or fortress gate axes.
 ends=[]
 for site,near in [(sites[i],p[1]),(sites[j],p[-2])]:
  x,y=site['xy_m'];r=site['radius_m'];sign=1 if near[1]>y else -1
  ends.append([[x,y+sign*r*.55],[x,y+sign*r*.97],[x,y+sign*r*1.35]])
 p=np.vstack([ends[0],p,ends[1][::-1]])
 # Smooth only when every resampled point and shoulder remains dry.
 curve=gaussian_filter1d(p,1,axis=0,mode='nearest');curve[0]=p[0];curve[-1]=p[-1]
 def safe(poly):
  pts=np.vstack([a+(b-a)*t for a,b in zip(poly[:-1],poly[1:]) for t in np.linspace(0,1,max(2,int(np.linalg.norm(b-a)/35)))])
  return bool((sample(clear,pts[:,0],pts[:,1])>90).all())
 if safe(curve):p=curve
 assert safe(p),(i,j,'road crosses water')
 routes.append({'from':sites[i]['id'],'to':sites[j]['id'],'country':sites[i]['country'],'kind':'caravan_trail' if sites[i]['culture'] in ['nomad','cult'] else 'regional_road','width_m':12 if sites[i]['kind']=='village' and sites[j]['kind']=='village' else 19,'points_m':p.tolist()})
 if k%25==0:print({'routed':k+1,'of':len(links)},flush=True)
# A restrained map-scale road tint makes connections readable in the wide view.
roadmask=Image.new('L',(W,H));draw=ImageDraw.Draw(roadmask)
for q in routes+gridroutes:draw.line([(round(cx-x/M),round(cy-y/M)) for x,y in q['points_m']],fill=125 if q['kind']=='farm_lane' else 160,width=1)
roadpaint=np.asarray(roadmask)/255*.5;roadpaint*=dry;color=color*(1-roadpaint[...,None])+np.array([.43,.36,.22])*roadpaint[...,None]
mainmask=Image.new('L',(W,H));md=ImageDraw.Draw(mainmask)
for q in routes:md.line([(round(cx-x/M),round(cy-y/M)) for x,y in q['points_m']],fill=255,width=1)
D['road_clearance']=(distance_transform_edt(np.asarray(mainmask)==0)*M).astype('float32')
D.update(height=h.astype('float32'),wetland=wetblend.astype('float32'),channel=channel.astype('float32'),water=water,water_clearance=clear.astype('float32'),farm=farmcover,urban=urban)
np.savez_compressed(S/'world_reference_v30.npz',**D)
Image.fromarray(np.uint8(np.clip(color,0,1)*255)).resize((4096,4096),Image.Resampling.BICUBIC).convert('RGBA').save(S/'T_IV_WorldBiomes30.png')
meta.update(content_version=30,settlements=sites,agricultural_parcels=farms,routes=routes,farm_lanes=gridroutes,relocated_settlements=relocated,scope='Regional scenery with water-safe settlement footprints and connected roads; mainland gameplay is not implemented.')
meta['civilizations']['RabaricRepublic']['visuals']='country-wide surveyed rectangular crop grid, market towns, farm villages, mills, granaries and connecting farm lanes'
meta['network_summary']={'sites':len(sites),'by_country':{n:sum(q['country']==n for q in sites) for n in countries},'regional_links':len(routes),'regional_road_km':sum(np.linalg.norm(np.diff(q['points_m'],axis=0),axis=1).sum() for q in routes)/1000,'farm_lane_sections':len(gridroutes),'farm_lane_km':sum(np.linalg.norm(np.diff(q['points_m'],axis=0),axis=1).sum() for q in gridroutes)/1000,'farm_parcels':len(farms),'cultivated_km2':float(farmcover.sum()*M*M/1e6),'relocated_sites':len(relocated)}
(S/'world_design_v30.json').write_text(json.dumps(meta,indent=2));print(meta['network_summary'],flush=True)
exec(compile((P/'build_world_surface_v30.py').read_text(),'surface','exec'),{'__name__':'__main__'})
