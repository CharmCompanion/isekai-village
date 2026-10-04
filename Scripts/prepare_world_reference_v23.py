from pathlib import Path
import numpy as np,json,heapq
from scipy.ndimage import gaussian_filter,map_coordinates,distance_transform_edt,binary_fill_holes,label
from PIL import Image,ImageDraw
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource'
REF=Path('D:/DEVELOPMENT/Games/GuildSim-Lineage/GuildFounder-DesktopCopy/BaseProject/assets/map/kingdoms')
W,H=1758,1185;M=80.;rng=np.random.default_rng(230)
def smooth(a,b,v):
 t=np.clip((v-a)/(b-a),0,1);return t*t*(3-2*t)
def layer(name):
 im=Image.open(REF/(name+'.png')).convert('RGB').resize((W,H),Image.Resampling.BILINEAR)
 return np.max(np.array(im),axis=2)>35
names=['BiomeDrt','BiomePln','BiomeFst','BiomeJgl','BiomeMtn','BiomeIce']
masks=np.stack([layer(n) for n in names]);land=masks.any(axis=0);filled=binary_fill_holes(land);lakes=filled&~land
countries=['YozuanDesert','DivineEmpireofGosain','KelsinFederation','RabaricRepublic','VylfodDominion','KingdomofElRuhn']
cmasks=np.stack([layer(n) for n in countries]);er=cmasks[-1];ey,ex=np.where(er);cx=float(ex.mean());cy=float(ey.mean())
print('reference origin',cx,cy,flush=True)
yy,xx=np.mgrid[:H,:W];X=(xx-cx)*M;Y=(cy-yy)*M
weights=np.stack([gaussian_filter(m.astype(float),2.2) for m in masks]);weights/=np.maximum(weights.sum(axis=0),1e-6)
desert,plains,forest,jungle,mountain,ice=weights
cache={}
def noise(k):
 if k not in cache:
  raw=np.random.default_rng(k+230).random((max(3,round(k*H/W)),k))
  cache[k]=map_coordinates(raw,[yy/(H-1)*(raw.shape[0]-1),xx/(W-1)*(raw.shape[1]-1)],order=3,mode='reflect')
 return cache[k]
coast=distance_transform_edt(filled)*M-distance_transform_edt(~filled)*M
continental=smooth(-120,700,coast)
# Connected mountain belt from the reference, with branching, uneven crests.
ridged=1-np.abs(2*noise(96)-1)
regional=520+190*noise(18)+120*noise(53)
regional+=plains*(90*noise(70))+forest*(190*noise(58))+jungle*(270*noise(43))
regional+=desert*(65*np.sin((X+Y*.4)/700+noise(70)*4)**2)
regional+=mountain*(650+1800*ridged+500*(1-np.abs(2*noise(210)-1)))
regional+=ice*(190+550*(1-np.abs(2*noise(100)-1)))
sea=-20600.;height=sea+continental*regional
# Inland lake surfaces are level and their shore basins share this same field.
labels,nlake=label(lakes);lakeinfo=[]
for i in range(1,nlake+1):
 lm=labels==i
 if lm.sum()<4:continue
 ys,xs=np.where(lm);mx=float(xs.mean());my=float(ys.mean());near=distance_transform_edt(~lm)*M
 level=float(np.percentile(height[(near>0)&(near<700)],20))
 blend=1-smooth(0,750,near);height=height*(1-blend)+(level+np.minimum(near,450)*.03)*blend
 height[lm]=level
 lakeinfo.append({'id':i,'xy_m':[(cx-mx)*M,(cy-my)*M],'level_m':level})
slope=np.hypot(*np.gradient(height,M))
# Paint biomes as landscape, not country colors; preserve source geography.
fine=noise(850);macro=noise(180)
palette=np.array([[.50,.335,.135],[.25,.36,.105],[.052,.19,.073],[.027,.13,.070],[.23,.245,.245],[.68,.79,.84]])
color=np.einsum('khw,kc->hwc',weights,palette)*(.85+.25*macro[...,None]+.06*fine[...,None])
stone=smooth(.25,.7,slope)*.55+mountain*.3
stone=np.clip(stone,0,.85)
color=color*(1-stone[...,None])+np.array([.28,.285,.275])*stone[...,None]
snow=np.maximum(ice,smooth(1850,2900,height-sea)*mountain)
color=color*(1-snow[...,None])+np.array([.76,.84,.88])*(.90+.10*macro[...,None])*snow[...,None]
beach=(1-smooth(200,1100,coast))*smooth(-100,150,coast)
color=color*(1-beach[...,None])+np.array([.46,.42,.27])*beach[...,None]
ocean=np.stack([.018+smooth(-12000,0,coast)*.015,.065+smooth(-10000,0,coast)*.09,.115+smooth(-10000,0,coast)*.10],-1)
color=color*continental[...,None]+ocean*(1-continental[...,None]);color[lakes]=[.027,.15,.20]
# Locate settlements within each actual country mask on low usable ground.
settlements=[]
for ci,name in enumerate(countries[:-1]):
 suitable=cmasks[ci]&land&(coast>900)&(slope<.13)&(mountain<.35)&(ice<.5)
 candidates=np.column_stack(np.where(suitable))
 if len(candidates)<10:continue
 chosen=[]
 target=np.array([np.where(cmasks[ci])[0].mean(),np.where(cmasks[ci])[1].mean()])
 score=np.sum((candidates-target)**2,axis=1);chosen.append(candidates[np.argmin(score)])
 for k in range(7):
  cand=candidates[rng.choice(len(candidates),min(1500,len(candidates)),replace=False)]
  d=np.min(np.sum((cand[:,None,:]-np.array(chosen)[None,:,:])**2,axis=2),axis=1)
  chosen.append(cand[np.argmax(d)])
 for j,(py,px) in enumerate(chosen):
  kind='city' if j==0 else 'town' if j<3 else 'village';radius={'city':1050,'town':470,'village':180}[kind]
  settlements.append({'country':name,'kind':kind,'xy_m':[(cx-float(px))*M,(cy-float(py))*M],'pixel':[int(px),int(py)],'radius_m':radius,'name':name+' '+('capital study' if j==0 else kind+' study '+str(j))})
# Routed links use a land-only lowland cost field, avoiding lakes and steep mountains.
stride=5;gh=(H+stride-1)//stride;gw=(W+stride-1)//stride
walk=filled[::stride,::stride]&~lakes[::stride,::stride]
cost=1+mountain[::stride,::stride]*15+ice[::stride,::stride]*5+np.minimum(slope[::stride,::stride],2)*18
roadmask=Image.new('L',(W,H));draw=ImageDraw.Draw(roadmask);routes=[]
def route(start,goal):
 sy,sx=start;gy,gx=goal;heap=[(0,sy,sx)];dist={(sy,sx):0};prev={};found=False
 while heap:
  _,y,x=heapq.heappop(heap)
  if (y,x)==(gy,gx):found=True;break
  d=dist[(y,x)]
  for dy,dx in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
   ny,nx=y+dy,x+dx
   if not(0<=ny<gh and 0<=nx<gw) or not walk[ny,nx]:continue
   nd=d+float(cost[ny,nx])*(1.414 if dx*dy else 1)
   if nd<dist.get((ny,nx),1e30):dist[(ny,nx)]=nd;prev[(ny,nx)]=(y,x);heapq.heappush(heap,(nd+np.hypot(ny-gy,nx-gx),ny,nx))
 if not found:return []
 p=[(gy,gx)]
 while p[-1]!=(sy,sx):p.append(prev[p[-1]])
 return [(x*stride,y*stride) for y,x in p[::-1]]
for name in countries[:-1]:
 nodes=[q for q in settlements if q['country']==name]
 for j in range(1,len(nodes)):
  target=min(nodes[:j],key=lambda t:np.linalg.norm(np.array(t['xy_m'])-nodes[j]['xy_m']))
  ax,ay=nodes[j]['pixel'];bx,by=target['pixel'];path=route((ay//stride,ax//stride),(by//stride,bx//stride))
  if len(path)>1:draw.line(path,fill=100,width=1);routes.append({'country':name,'points_m':[[(cx-x)*M,(cy-y)*M] for x,y in path]})
road=np.asarray(roadmask,dtype=float)/255;road=gaussian_filter(road,.55)
color=color*(1-road[...,None]*.5)+np.array([.38,.32,.22])*road[...,None]*.5
for q in settlements:
 px,py=q['pixel'];rr=q['radius_m']/M;rad=int(rr*1.6)+2
 x0=max(0,px-rad);x1=min(W,px+rad+1);y0=max(0,py-rad);y1=min(H,py+rad+1)
 u=(xx[y0:y1,x0:x1]-px)/rr;v=(yy[y0:y1,x0:x1]-py)/(rr*.7)
 d=np.hypot(u,v)+.17*np.sin(u*5+v*3)+.12*np.cos(v*7-u*2)
 patch=1-smooth(.6,1.25,d)
 detail=.8+.2*noise(850)[y0:y1,x0:x1]
 tint=np.array([.38,.33,.245])*detail[...,None]
 sub=color[y0:y1,x0:x1];color[y0:y1,x0:x1]=sub*(1-patch[...,None]*.7)+tint*patch[...,None]*.7
Image.fromarray(np.uint8(np.clip(color,0,1)*255)).resize((4096,4096),Image.Resampling.BICUBIC).convert('RGBA').save(S/'T_IV_WorldBiomes23.png')
np.savez_compressed(S/'world_reference_v23.npz',height=height.astype('float32'),cx=cx,cy=cy,mpp=M,width=W,height_px=H)
metadata={'source_folder':str(REF),'metres_per_original_pixel':M/2,'origin_reference_pixel':[cx*2,cy*2],'world_extent_m':[W*M,H*M],'biomes':dict(zip(names,['desert','plains','forest','jungle','mountains','ice'])),'ElRuhn':{'name':'Kingdom of El Ruhn','status':'small neutral sovereign floating country','sovereign_territory':'existing playable floating island','scale_note':'Reference geography guides neighboring regions; current playable island size is preserved. The map is not a literal survey of island dimensions.'},'settlements':settlements,'lakes':lakeinfo,'routes':routes}
(S/'world_design_v23.json').write_text(json.dumps(metadata,indent=2));print({'settlements':len(settlements),'routes':len(routes),'lakes':len(lakeinfo),'map':metadata['world_extent_m']},flush=True)
