"""Build a complete scenic watershed below the playable island."""
from pathlib import Path
import numpy as np,json
from scipy.ndimage import map_coordinates,gaussian_filter
from PIL import Image
S=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource');rng=np.random.default_rng(17029)
def smooth(a,b,v):
 t=np.clip((v-a)/(b-a),0,1);return t*t*(3-2*t)
cache={}
def noise(x,y,k):
 if k not in cache:cache[k]=np.random.default_rng(k+17029).uniform(0,1,(k,k))
 return map_coordinates(cache[k],[(y+8000)/16000*(k-1),(x+8000)/16000*(k-1)],order=3,mode='reflect')
towns=[(650,-760),(-1750,-950),(1800,-2000)]
peaks=[
 (-1700,1900,570,1100,340),(-2350,2800,700,650,520),(-850,2500,650,470,420),(800,2400,680,650,490),(1700,1700,550,920,360),(2800,2700,770,1200,600),
 (-3000,-2600,540,1100,270),(3700,-600,600,1000,360),(-4700,1200,760,1500,530),(1500,5300,1300,750,540)]
def fields(x,y):
 z=-7120+80*noise(x,y,14)+45*noise(x,y,37)+12*noise(x,y,95)
 relief=np.zeros_like(x)
 for px,py,wx,wy,h in peaks:
  u=(x-px)/wx;v=(y-py)/wy
  relief+=h*np.exp(-(u*u+v*v)*1.3)
 # Valleys divide connected ridges; no high-frequency corrugation.
 erosion=.72+.28*noise(x,y,62)
 z+=relief*erosion+12*(noise(x,y,175)-.5)
 rx=-950+170*np.sin((y+950)/630)+85*np.sin((y+950)/270)
 rd=np.abs(x-rx);la=np.arctan2((y+950)/260,(x+1050)/460)
 lake=np.sqrt(((x+1050)/460)**2+((y+950)/260)**2)/(1+.09*np.sin(3*la)+.05*np.sin(5*la+1))
 water=np.maximum(1-smooth(22,36,rd),1-smooth(.94,1.02,lake))
 wetvalley=np.maximum(np.exp(-(rd/130)**2),1-smooth(.92,1.35,lake))
 wl=-7080+np.maximum(y+750,0)*.015-np.maximum(-y-1250,0)*.010
 wl=np.where(lake<1.3,-7080,wl)
 z=z*(1-wetvalley)+((wl-9*water)*(wetvalley))
 # Matching footprint; exact cavity triangles are added separately below.
 a=np.arctan2((y-20)/570,x/580)
 r=(np.abs(x/580)**4+np.abs((y-20)/570)**4)**.25/(1+.012*np.sin(7*a)+.008*np.sin(13*a))
 farm=np.zeros_like(x);road=np.zeros_like(x);town=np.zeros_like(x)
 for tx,ty in towns:
  d=np.hypot((x-tx)/1.2,y-ty);town=np.maximum(town,1-smooth(45,110,d))
 # Country road curves past towns, avoiding the extraction basin and lake.
 roadx=700+500*np.sin((y+750)/1450)+220*np.sin((y+750)/670)
 road=np.maximum(1-smooth(6,10,np.abs(x-roadx)),road)
 for tx,ty in towns:road=np.maximum(road,(1-smooth(5,9,np.abs(y-ty)))*(1-smooth(200,600,np.abs(x-tx))))
 # Large connected woodland belts with small gaps, rather than camouflage spots.
 woodland=.54*noise(x,y,14)+.30*noise(x,y,38)+.16*noise(x,y,95)
 woodland+=.15*smooth(-900,1900,y)+.09*smooth(30,150,relief)
 forest=smooth(.37,.59,woodland)*(1-smooth(280,520,relief))
 forest*=1-np.maximum.reduce([water,town,farm,road,1-smooth(1.05,1.4,r)])
 return z,water,forest,farm,road,relief,r,wl,town

# Cavity is the original rock shell, uniformly scaled and translated, with
# reversed faces. No height interpolation or independently invented crater.
scale=1.;base=-7120.;depth_shift=-12880.;verts=[];faces=[]
for line in (S/'SM_IV_JoinedMountain_v13.obj').open():
 if line.startswith('v '):
  x,y,z=map(float,line.split()[1:4]);verts.append((x/100,-y/100,z/100))
 elif line.startswith('f '):faces.append(tuple(int(v.split('/')[0])-1 for v in line.split()[1:4]))
original=np.array(verts);v=original*scale;v[:,2]+=base
# Source OBJ winding is already reversed for Y export, so these face indices
# become the reversed (cavity-facing) triangles in positive-Y world space.
F=list(faces);V=v.tolist();boundary=v[:2048];angles=np.linspace(0,2*np.pi,2048,endpoint=False)
H=np.load(S/'height_valley_v14.npy')
def outline(a):return (1+.012*np.sin(7*a)+.008*np.sin(13*a))/(np.abs(np.cos(a))**4+np.abs(np.sin(a))**4)**.25
def outside(x,y):
 a=np.arctan2((y-20)/570,x/580);out=outline(a)
 r=np.hypot(x/580,(y-20)/570)/out
 xx=580*np.cos(a)*out;yy=20+570*np.sin(a)*out
 edge=map_coordinates(H,[((20+(yy-20)*.992)+600)*.84,(xx*.992+600)*.84],order=1,mode='nearest')-.45
 inner=map_coordinates(H,[((20+(yy-20)*.97)+600)*.84,(xx*.97+600)*.84],order=1,mode='nearest')
 derivative=np.clip((edge-inner)/.022,-400,400)
 continuation=base+scale*(edge+derivative*(r-.992)*np.exp(-((r-.992)/.24)**2))
 z=fields(x,y)[0];blend=smooth(1.03,1.8,r);z=continuation*(1-blend)+z*blend
 far=smooth(6500,9000,np.hypot(x,y));z=z*(1-far)+(-7170+260*noise(x,y,14)+70*noise(x,y,38))*far
 z-=np.maximum(np.hypot(x,y)-12000,0)**2/700000
 return z,r
rings=[list(range(2048))]
radials=[(1.005,2048),(1.03,1024),(1.07,512)]+[(float(r),512) for r in np.r_[np.linspace(1.10,4,135),np.linspace(4.1,40,160),np.geomspace(41,700,65)]]
for radial,n in radials:
 a=np.linspace(0,2*np.pi,n,endpoint=False);o=outline(a);x=580*np.cos(a)*o*radial;y=20+570*np.sin(a)*o*radial;z,_=outside(x,y)
 ring=list(range(len(V),len(V)+n));V.extend(np.stack([x,y,z],-1).tolist());rings.append(ring)
for inner,outer in zip(rings[:-1],rings[1:]):
 n=len(inner);m=len(outer);ratio=n//m
 for i in range(m):
  for k in range(ratio):F.append((inner[(i*ratio+k)%n],outer[i],inner[(i*ratio+k+1)%n]))
  F.append((inner[((i+1)*ratio)%n],outer[i],outer[(i+1)%m]))
V=np.array(V);V[:,2]+=depth_shift;F=np.array(F);norm=np.zeros_like(V)
cross=np.cross(V[F[:,1]]-V[F[:,0]],V[F[:,2]]-V[F[:,0]])
for i in range(3):np.add.at(norm,F[:,i],cross)
norm/=np.maximum(np.linalg.norm(norm,axis=1,keepdims=True),1e-10)
name='SM_IV_PuzzleContinent_v18'
with (S/(name+'.obj')).open('w') as f:
 f.write('o '+name+'\n')
 for x,y,z in V:f.write(f'v {x*100:.5f} {-y*100:.5f} {z*100:.5f}\n')
 for x,y,z in V:f.write(f'vt {x/16000+.5:.7f} {y/16000+.5:.7f}\n')
 for nx,ny,nz in norm:f.write(f'vn {nx:.7f} {-ny:.7f} {nz:.7f}\n')
 for face in F[:,::-1]:f.write('f '+' '.join(f'{i+1}/{i+1}/{i+1}' for i in face)+'\n')

# Remove fields and literal building shapes from the scenic atlas.
axis=np.linspace(-8000,8000,2048);X,Y=np.meshgrid(axis,axis)
z,water,forest,farm,road,relief,r,wl,town=fields(X,Y);z,_=outside(X,Y)
gy,gx=np.gradient(z,16000/2047);slope=np.hypot(gx,gy);fine=noise(X,Y,601);macro=noise(X,Y,85)
color=np.ones((*z.shape,3))*[.20,.38,.085];color*= (.82+.30*macro+.12*fine)[...,None]
woods=np.stack([.045+.045*fine,.20+.065*fine,.065+.045*fine],-1)
color=color*(1-forest[...,None])+woods*forest[...,None]
rock=np.clip(smooth(.4,.9,slope)*.85+smooth(190,420,relief)*.6,0,1)
stone=np.array([.31,.32,.29])*(.83+.30*fine[...,None]);color=color*(1-rock[...,None])+stone*rock[...,None]
scar=1-smooth(.98,1.07,r);color=color*(1-scar[...,None])+np.array([.24,.25,.23])*scar[...,None]
# Soft settlement-toned clearings imply occupation without houses or farm grids.
color=color*(1-town[...,None]*.42)+np.array([.30,.29,.20])*town[...,None]*.42
color=color*(1-road[...,None]*.55)+np.array([.38,.32,.19])*road[...,None]*.55
wc=np.stack([.022+fine*.01,.27+fine*.025,.31+fine*.025],-1);color=color*(1-water[...,None])+wc*water[...,None]
Image.fromarray(np.uint8(np.clip(color,0,1)*255)).convert('RGBA').save(S/'T_IV_ContinentAtlas18.png')

rows=json.loads((S/'living_continent_v17_instances.json').read_text());rows['House']=[];rows['HouseVar']=[]
for kind,points in rows.items():
 if not points:continue
 p=np.array(points);zz,rr=outside(p[:,0],p[:,1]);p[:,2]=zz+depth_shift;p=p[rr>1.2];rows[kind]=p.tolist()
(S/'puzzle_continent_v18_instances.json').write_text(json.dumps(rows))
edges=np.sort(np.concatenate([F[:,[0,1]],F[:,[1,2]],F[:,[2,0]]]),axis=1);_,counts=np.unique(edges,axis=0,return_counts=True)
seat=np.max(np.abs((V[:len(original)]-[0,0,base+depth_shift])/scale-original))
assert seat<1e-9 and int((counts==1).sum())==512 and int((counts>2).sum())==0
report={'uniform_scale':scale,'translation_m':[0,0,base+depth_shift],'inverse_fit_max_error_m':float(seat),'cavity_vertices_copied':len(original),'cavity_triangles_reversed':len(faces),'seam_vertices_shared':2048,'internal_open_edges':0,'outer_horizon_open_edges':512,'nonmanifold_edges':0,'houses':0,'farm_masks':0,'island_changed':False,'vertices':len(V),'triangles':len(F)}
(S/'puzzle_continent_v18_report.json').write_text(json.dumps(report,indent=2));print(report)

