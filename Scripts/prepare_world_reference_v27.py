from pathlib import Path
import numpy as np,json,heapq
from scipy.ndimage import gaussian_filter,map_coordinates,distance_transform_edt,binary_fill_holes,label,gaussian_filter1d
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
weights=np.stack([gaussian_filter(m.astype(float),11.0) for m in masks]);weights/=np.maximum(weights.sum(axis=0),1e-6)
desert,plains,forest,jungle,mountain,ice=weights
cache={}
def noise(k):
 if k not in cache:
  raw=np.random.default_rng(k+230).random((max(3,round(k*H/W)),k))
  cache[k]=map_coordinates(raw,[yy/(H-1)*(raw.shape[0]-1),xx/(W-1)*(raw.shape[1]-1)],order=3,mode='reflect')
 return cache[k]
coast=gaussian_filter(distance_transform_edt(filled)*M-distance_transform_edt(~filled)*M,1.35)
continental=smooth(-50,50,coast)
# A dry southern fringe extends into the reference's light-green western lowlands.
# Spring-fed pockets sit inside this semi-arid transition, rather than a uniform green desert.
south_fringe=plains*smooth(555,625,yy)*(1-smooth(720,800,yy))*(1-smooth(505,615,xx))
dry_fringe=south_fringe*(.72-.42*smooth(630,790,yy))
desert_distance=distance_transform_edt(~masks[0])*M
# Modest interior divide: easterly maritime air rises here; the western basin is sheltered.
divide=np.exp(-((desert_distance-1600)/1800)**2)*plains*smooth(475,560,xx)*(1-smooth(565,640,yy))*smooth(225,285,yy)
beach_width=160+260*noise(43)
rocky=np.clip(mountain*.8+ice*.7+divide*.5+.55*smooth(.53,.80,noise(43)),0,.92)
beach_belt=(1-smooth(beach_width,beach_width+180,coast))*smooth(-90,-30,coast)*(1-rocky)
# Flatten warm beaches into a low coastal bench, then rise through a coastal plain.
coastal_rise=smooth(300,3300,coast)
coastal_rise=coastal_rise*(1-rocky)+smooth(50,1000,coast)*rocky
# Connected mountain belt from the reference, with branching, uneven crests.
ridged=1-np.abs(2*noise(96)-1)
regional=520+190*noise(18)+120*noise(53)
regional+=plains*(90*noise(70))+forest*(190*noise(58))+jungle*(270*noise(43))
regional+=(desert+dry_fringe)*(65*np.sin((X+Y*.4)/700+noise(70)*4)**2)
regional+=mountain*(650+1800*ridged+500*(1-np.abs(2*noise(210)-1)))
regional+=ice*(190+550*(1-np.abs(2*noise(100)-1)))
regional+=divide*(500+750*ridged)
sea=-20600.;height=sea+continental*(np.minimum(np.maximum(coast,0),500)*.012+coastal_rise*regional)
# An eroded diagonal canyon cuts down through a broad sandstone plateau.
# The asymmetrical branching footprint replaces the former raised escarpment.
cliff_line=500-.40*(yy-340)+10*np.sin(yy/47)+6*np.sin(yy/19)
cliff_d=xx-cliff_line-(noise(150)-.5)*5
cliff_extent=smooth(315,355,yy)*(1-smooth(720,765,yy))*smooth(1000,3000,coast)*np.clip(desert+south_fringe,0,1)
width=18+5*np.sin(yy/67)+3*np.sin(yy/29)
relative=np.abs(cliff_d)/(width*(.75+.5*noise(180))*(1+.09*np.sin(yy/9)))
# Nested cuts leave broad, uneven benches between steep rock faces.
bench=relative*(.90+.20*noise(210))
main_cut=.23*(1-smooth(.83,1.15,relative))+.33*(1-smooth(.48,.70,bench))+.44*(1-smooth(.16,.34,relative*(.82+.35*noise(96))))
main_cut*=cliff_extent
branches=np.zeros_like(coast)
branch_paths=[([(454,425),(428,408),(416,379)],.68), ([(454,425),(475,449),(505,464)],.66), ([(422,505),(386,481),(375,452)],.78), ([(404,550),(430,568),(462,560)],.62), ([(384,630),(356,611),(332,584)],.70), ([(365,693),(388,714),(420,726)],.57)]
# Anchor each tributary's first point to the actual winding main channel.
for points,depth in branch_paths:
 ay=points[0][1];ax=500-.40*(ay-340)+10*np.sin(ay/47)+6*np.sin(ay/19);points=[(ax,ay)]+points[1:]
 control=np.array(points);ts=np.linspace(0,1,21);points=[tuple((1-t)**2*control[0]+2*(1-t)*t*control[1]+t*t*control[2]) for t in ts]
 lengths=[np.hypot(bx-ax,by-ay) for (ax,ay),(bx,by) in zip(points[:-1],points[1:])];total=sum(lengths);walked=0
 for (ax,ay),(bx,by),length in zip(points[:-1],points[1:],lengths):
  t=np.clip(((xx-ax)*(bx-ax)+(yy-ay)*(by-ay))/(length*length),0,1);along=(walked+t*length)/total
  dist=np.hypot(xx-ax-t*(bx-ax),yy-ay-t*(by-ay))
  span=(9-6*along)*(1+.10*np.sin(yy/7))
  cut=(1-smooth(.25,1.2,dist/(np.maximum(span,1)*(.80+.40*noise(180)))))*depth*(1-smooth(.6,1,along))
  branches=np.maximum(branches,cut);walked+=length
branches*=np.clip(desert+south_fringe,0,1)*smooth(1800,3500,coast)
canyon_cut=np.maximum(main_cut,branches)
plateau=(1-smooth(45,110,np.abs(cliff_d)))*cliff_extent*620
height+=plateau
floor=sea+510-330*smooth(340,745,yy)+25*noise(96)
height-=np.maximum(height-floor,0)*canyon_cut
canyon_mask=smooth(.015,.14,canyon_cut)
cliff_relief=canyon_mask*1000
# Keep a useful refinement footprint around both walls and tributary ravines.
cliff_detail=gaussian_filter(canyon_mask,4)
# Fixed-seed spatial sampling gives irregular, reproducible oasis placement,
# with varying basin sizes; no authored arc or evenly spaced row.
spring_masks=[];spring_sites=[];oasis=np.zeros_like(coast)
spring_rng=np.random.default_rng(250921)
existing_water_distance=distance_transform_edt(~lakes)*M
for j in range(10):
 zone=(south_fringe>.20) if j<5 else ((desert>.65)&(yy>315)&(yy<665))
 eligible=zone&land&(coast>2200)&(existing_water_distance>2200)&(cliff_relief<30)
 for q in spring_sites:eligible&=np.hypot(xx-q['pixel'][0],yy-q['pixel'][1])>spring_rng.uniform(40,65)
 ys,xs=np.where(eligible)
 if len(xs)==0:continue
 previous=json.loads((S/'world_design_v26.json').read_text())['oasis_sites'][j]
 wanted=previous['pixel'];k=np.argmin((xs-wanted[0])**2+(ys-wanted[1])**2);px=int(xs[k]);py=int(ys[k])
 rx=spring_rng.uniform(2,5.5);ry=spring_rng.uniform(1.8,4.3);angle=spring_rng.uniform(-3.14,3.14)
 dx=xx-px;dy=yy-py;u=(dx*np.cos(angle)+dy*np.sin(angle))/rx;v=(-dx*np.sin(angle)+dy*np.cos(angle))/ry
 theta=np.arctan2(v,u);rr=np.hypot(u,v)/(1+.14*np.sin(theta*3+angle)+.1*np.cos(theta*5))
 lm=(rr<1)&land;spring_masks.append(lm);lakes|=lm
 reach=spring_rng.uniform(850,1750)
 near=distance_transform_edt(~lm)*M
 # Irregular vegetation follows the spring basin rather than a circular dot.
 green=(1-smooth(100,reach,near*(.70+.65*noise(180))))*(.75+.25*noise(300))
 oasis=np.maximum(oasis,green)
 spring_sites.append({'pixel':[px,py],'xy_m':[(cx-px)*M,(cy-py)*M],'radius_m':[rx*M,ry*M],'vegetation_reach_m':reach})
spring_water=np.logical_or.reduce(spring_masks) if spring_masks else np.zeros_like(land)
wet_distance=distance_transform_edt(~lakes)*M
oasis=np.maximum(oasis,south_fringe*(1-smooth(180,1400,wet_distance)))

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
palette=np.array([[.50,.335,.135],[.25,.36,.105],[.052,.19,.073],[.027,.13,.070],[.23,.245,.245],[.22,.30,.19]])
color=np.einsum('khw,kc->hwc',weights,palette)*(.85+.25*macro[...,None]+.06*fine[...,None])
# Sand and dry grass interlock around visibly wet green oases.
sand=np.array([.50,.335,.135])*(.88+.18*macro[...,None])
color=color*(1-dry_fringe[...,None])+sand*dry_fringe[...,None]
oasis_color=np.array([.075,.29,.10])*(.88+.22*macro[...,None])
color=color*(1-oasis[...,None]*.9)+oasis_color*oasis[...,None]*.9
stone=smooth(.25,.7,slope)*.55+(mountain+divide)*.3
stone=np.clip(stone,0,.85)
color=color*(1-stone[...,None])+np.array([.28,.285,.275])*stone[...,None]
# Broken woodland edges and fine canopy texture remain readable at aerial scale.
canopy=np.clip(forest+jungle,0,1)*(1-stone)
canopy_detail=.86+.20*fine+.10*noise(300)
color*=1-canopy[...,None]*(1-canopy_detail[...,None])
# Broad landforms get subtle valley shading without baking a directional light.
valley=np.clip((gaussian_filter(height,9)-height)/500,0,.22)
color*=1-valley[...,None]
# Warm rock bands distinguish the desert escarpment from snow and beaches.
cliff_exposure=canyon_mask
strata=.78+.13*np.sin((height-sea)/65+noise(96)*.7)+.10*noise(180)
layer=smooth(-.55,.60,np.sin((height-sea)/110+noise(96)*1.7))
cliff_color=(np.array([.29,.12,.052])[None,None,:]*(1-layer[...,None])+np.array([.40,.215,.11])[None,None,:]*layer[...,None])*strata[...,None]
cliff_color*=1-canyon_cut[...,None]*.37
color=color*(1-cliff_exposure[...,None])+cliff_color*cliff_exposure[...,None]
snow=smooth(1850,2850,height-sea)*np.clip(mountain+ice+divide,0,1)
color=color*(1-snow[...,None])+np.array([.76,.84,.88])*(.90+.10*macro[...,None])*snow[...,None]
beach=beach_belt
sand_tint=np.array([.44,.31,.15])*(.92+.12*macro[...,None])
color=color*(1-beach[...,None])+sand_tint*beach[...,None]
# Wet sand along the lower beach; cool rocky shores remain locally exposed.
wet_sand=(1-smooth(60,150,coast))*beach
color=color*(1-wet_sand[...,None]*.35)+np.array([.31,.29,.20])*wet_sand[...,None]*.35
ocean=np.stack([.018+smooth(-12000,0,coast)*.015,.065+smooth(-10000,0,coast)*.09,.115+smooth(-10000,0,coast)*.10],-1)
color=color*continental[...,None]+ocean*(1-continental[...,None]);lake_dist=distance_transform_edt(lakes)*M-distance_transform_edt(~lakes)*M
lake_alpha=smooth(-65,65,lake_dist)
lake_deep=smooth(100,650,np.maximum(lake_dist,0))
lake_color=np.array([.026,.12,.15])[None,None,:]*(1-lake_deep[...,None])+np.array([.016,.072,.105])[None,None,:]*lake_deep[...,None]
color=color*(1-lake_alpha[...,None])+lake_color*lake_alpha[...,None]
color[spring_water]*=np.array([.8,1.12,1.02])
# Locate settlements within each actual country mask on low usable ground.
settlements=[]
for ci,name in enumerate(countries[:-1]):
 suitable=cmasks[ci]&land&(coast>900)&(slope<.13)&(mountain<.35)&(ice<.5)&~lakes&(canyon_mask<.08)
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
cost=1+canyon_mask[::stride,::stride]*50+mountain[::stride,::stride]*15+ice[::stride,::stride]*5+np.minimum(slope[::stride,::stride],2)*18
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
  if len(path)>1:
   original=np.array(path,dtype=float);curve=gaussian_filter1d(original,2.0,axis=0,mode='nearest');curve[0]=original[0];curve[-1]=original[-1]
   dense=np.linspace(0,len(curve)-1,max(2,len(curve)*4));curve=np.column_stack([np.interp(dense,np.arange(len(curve)),curve[:,k]) for k in range(2)])
   legal=map_coordinates((land&~lakes).astype(float),[curve[:,1],curve[:,0]],order=0,mode='constant')>.5
   if not legal.all():curve=original
   path=[tuple(q) for q in curve];draw.line(path,fill=80,width=1);routes.append({'country':name,'points_m':[[(cx-x)*M,(cy-y)*M] for x,y in path]})
road=np.asarray(roadmask,dtype=float)/255;road=gaussian_filter(road,.7);road*=land&~lakes
color=color*(1-road[...,None]*.5)+np.array([.38,.32,.22])*road[...,None]*.5
for q in settlements:
 px,py=q['pixel'];rr=q['radius_m']/M;rad=int(rr*1.6)+2
 x0=max(0,px-rad);x1=min(W,px+rad+1);y0=max(0,py-rad);y1=min(H,py+rad+1)
 u=(xx[y0:y1,x0:x1]-px)/rr;v=(yy[y0:y1,x0:x1]-py)/(rr*.7)
 d=np.hypot(u,v)+.17*np.sin(u*5+v*3)+.12*np.cos(v*7-u*2)
 patch=1-smooth(.6,1.25,d)
 detail=.72+.22*noise(850)[y0:y1,x0:x1]+.08*np.sin(u*21+v*7)*np.cos(v*19-u*3)
 # Dense interior districts and loose outskirts, without literal house symbols.
 patch*=np.clip(.65+.35*noise(300)[y0:y1,x0:x1]+.10*np.sin(u*9+v*4),.3,1)
 tint=np.array([.23,.19,.13])*detail[...,None]
 sub=color[y0:y1,x0:x1];color[y0:y1,x0:x1]=sub*(1-patch[...,None]*.7)+tint*patch[...,None]*.7
Image.fromarray(np.uint8(np.clip(color,0,1)*255)).resize((4096,4096),Image.Resampling.BICUBIC).convert('RGBA').save(S/'T_IV_WorldBiomes27.png')
np.savez_compressed(S/'world_reference_v27.npz',height=height.astype('float32'),cx=cx,cy=cy,mpp=M,width=W,height_px=H,coast=coast.astype('float32'),cliff=cliff_detail.astype('float32'),mountain=mountain.astype('float32'))
metadata={'source_folder':str(REF),'metres_per_original_pixel':M/2,'origin_reference_pixel':[cx*2,cy*2],'world_extent_m':[W*M,H*M],'biomes':dict(zip(names,['desert','plains','forest','jungle','mountains','ice'])),'ElRuhn':{'name':'Kingdom of El Ruhn','status':'small neutral sovereign floating country','sovereign_territory':'existing playable floating island','scale_note':'Reference geography guides neighboring regions; current playable island size is preserved. The map is not a literal survey of island dimensions.'},'settlements':settlements,'lakes':lakeinfo,'routes':routes}
metadata['map_orientation']={'north':'+Y','east':'-X'}
metadata['ecology']={'version':27,'climate_assumption':'Easterly maritime moisture; a sheltered western dry basin, spring-fed southern desert fringe and wetter eastern and southern woodland. Stylized compressed regional geography, not a climate simulation.','northern_lowlands':'cool scrub and woodland; snow restricted to high elevation','desert_transition':'desert to semi-arid sand and grass mosaic with spring-fed oases, then plains','coast':'variable sandy beaches on low coasts, exposed rocky coasts near highlands','spring_lakes':len(spring_masks),'beach_width_m':[160,420],'preserved_original_inland_lakes':9}
metadata['polish']={'routes':'smoothed bends with land/water validation','cliff':'deep winding canyon, layered walls, side ravines and remnant ledges','water':'blended lake margins, shallow-to-deep color','settlements':'dense interior and broken outskirts','terrain':'adaptive shoreline, cliff and mountain mesh refinement'}
metadata['polish']['clouds']='24 visible banks in three uneven groups; opacity .59; central view open'
metadata['oasis_sites']=spring_sites
metadata['desert_canyon']={'type':'deep diagonal sandstone canyon with stepped walls and six side ravines','approximate_length_km':33,'approximate_width_km':[2.2,4.2],'depth_below_plateau_m':[700,1100],'floor':'dry seasonal wash; no arbitrary lake or river crossing','future_use':'broad remnant ledges for a possible nomad cliff settlement','replaces':'raised v26 escarpment'}
metadata['ecology']['coast']='Golden sand reaches the same shoreline coordinate as the ocean; wet sand blends directly into water. Low coastal benches; rockier highland coasts.'
metadata['biomes']['BiomeIce']='cool northern lowlands and alpine snow'
metadata['biomes']['BiomeJgl']='humid dense woodland'
assert np.isfinite(height).all() and np.isfinite(color).all()
assert np.any(beach>.7) and len(spring_masks)>=4
assert np.min(height[canyon_cut>.98]-sea)>0
(S/'canyon_v27_validation.json').write_text(json.dumps({'canyon_cells':int((canyon_mask>.5).sum()),'side_ravines':len(branch_paths),'minimum_floor_above_sea_m':float(np.min(height[canyon_cut>.98]-sea)),'maximum_incision_m':float(np.max(np.maximum((sea+continental*(np.minimum(np.maximum(coast,0),500)*.012+coastal_rise*regional)+plateau)-height,0))),'finite_terrain':bool(np.isfinite(height).all())},indent=2))
(S/'ecology_v27_validation.json').write_text(json.dumps({'spring_lakes':len(spring_masks),'beach_cells':int((beach>.5).sum()),'oasis_cells':int((oasis>.25).sum()),'snow_below_1850m':int(((snow>.01)&(height-sea<1850)).sum()),'finite_terrain':True},indent=2))
(S/'world_design_v27.json').write_text(json.dumps(metadata,indent=2));print({'settlements':len(settlements),'routes':len(routes),'lakes':len(lakeinfo),'map':metadata['world_extent_m']},flush=True)
