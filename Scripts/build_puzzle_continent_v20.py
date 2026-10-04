"""Build a complete scenic watershed below the playable island."""
from pathlib import Path
import numpy as np,json
from scipy.ndimage import map_coordinates,gaussian_filter,gaussian_filter1d
from PIL import Image
from scipy.interpolate import PchipInterpolator
S=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource');rng=np.random.default_rng(17029)
def smooth(a,b,v):
 t=np.clip((v-a)/(b-a),0,1);return t*t*(3-2*t)
cache={}
def noise(x,y,k):
 if k not in cache:cache[k]=np.random.default_rng(k+17029).uniform(0,1,(k,k))
 return map_coordinates(cache[k],[(y+8000)/16000*(k-1),(x+8000)/16000*(k-1)],order=3,mode='reflect')
towns=[(2200,-1800),(-2800,-1500),(3300,900)]
peaks=[
 (-1700,1900,570,1100,340),(-2350,2800,700,650,520),(-850,2500,650,470,420),(800,2400,680,650,490),(1700,1700,550,920,360),(2800,2700,770,1200,600),
 (-3000,-2600,540,1100,270),(3700,-600,600,1000,360),(-4700,1200,760,1500,530),(1500,5300,1300,750,540)]
river_curve=PchipInterpolator([-8000,-3000,-1600,-1350,-1100,0,1000,2300,4000,6000,8000],[-3100,-2450,-1970,-1850,-1850,-2250,-3050,-3450,-3400,-3100,-3200])
def hydro(x,y):
 rx=river_curve(y);rd=np.abs(x-rx)
 la=np.arctan2((y+1350)/230,(x+1850)/390)
 lake=np.sqrt(((x+1850)/390)**2+((y+1350)/230)**2)/(1+.07*np.sin(3*la)+.035*np.sin(5*la+1))
 width=28+5*np.sin(y/570)+3*np.sin(y/210)
 wl=-7080+np.maximum(y+1080,0)*.008-np.maximum(-y-1620,0)*.006
 wl=np.where(lake<1.4,-7080,wl)
 water=np.maximum(1-smooth(width-2,width+5,rd),1-smooth(.97,1.025,lake))
 return rd,lake,width,wl,water

def carve(z,x,y):
 rd,lake,width,wl,water=hydro(x,y)
 # A continuous floodplain, raised banks, then a submerged channel.
 valley=1-smooth(100,330,rd)
 shelf=wl+4+np.maximum(rd-width,0)*.055
 z=z*(1-valley)+np.minimum(z,shelf)*valley
 bed=wl-5+9*smooth(width-4,width+20,rd)
 channel=1-smooth(width+15,width+45,rd)
 z=z*(1-channel)+bed*channel
 shore=1-smooth(.94,1.28,lake)
 lakebed=-7089+13*smooth(.83,1.08,lake)
 z=z*(1-shore)+np.minimum(z,lakebed)*shore
 return z

def fields(x,y):
 z=-7120+80*noise(x,y,14)+45*noise(x,y,37)+12*noise(x,y,95)
 relief=np.zeros_like(x)
 for px,py,wx,wy,h in peaks:
  u=(x-px)/wx;v=(y-py)/wy
  relief+=h*np.exp(-(u*u+v*v)*1.3)
 # Valleys divide connected ridges; no high-frequency corrugation.
 erosion=.72+.28*noise(x,y,62)
 z+=relief*erosion+12*(noise(x,y,175)-.5)
 rd,lake,width,wl,water=hydro(x,y)
 z=carve(z,x,y)
 # Matching footprint; exact cavity triangles are added separately below.
 a=np.arctan2((y-20)/570,x/580)
 r=(np.abs(x/580)**4+np.abs((y-20)/570)**4)**.25/(1+.012*np.sin(7*a)+.008*np.sin(13*a))
 farm=np.zeros_like(x);road=np.zeros_like(x);town=np.zeros_like(x)
 for tx,ty in towns:
  u=(x-tx)/230;v=(y-ty)/140
  d=np.sqrt(u*u+v*v)+.25*(noise(x,y,95)-.5)
  town=np.maximum(town,1-smooth(.4,1.2,d))
 # Only a faint sinuous route in the inhabited eastern valley, far from the scar.
 route=2650+370*np.sin(y/1700)+90*np.sin(y/480)
 road=(1-smooth(5,13,np.abs(x-route)))*smooth(1400,2100,x)
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
# A low-frequency continuation outside the precise island contact line.
edge_angles=np.linspace(0,2*np.pi,2048,endpoint=False)
edge_outline=outline(edge_angles)
edge_x=580*np.cos(edge_angles)*edge_outline*.992
edge_y=20+570*np.sin(edge_angles)*edge_outline*.992
edge_samples=map_coordinates(H,[(edge_y+600)*.84,(edge_x+600)*.84],order=1,mode='nearest')-.45
smooth_edge=gaussian_filter1d(edge_samples,24,mode='wrap')
def outside(x,y):
 a=np.arctan2((y-20)/570,x/580);out=outline(a)
 r=np.hypot(x/580,(y-20)/570)/out
 xx=580*np.cos(a)*out;yy=20+570*np.sin(a)*out
 edge=map_coordinates(H,[((20+(yy-20)*.992)+600)*.84,(xx*.992+600)*.84],order=1,mode='nearest')-.45
 inner=map_coordinates(H,[((20+(yy-20)*.97)+600)*.84,(xx*.97+600)*.84],order=1,mode='nearest')
 # Carry the rim elevation into broad shoulders without invented periodic spurs.
 soft=np.interp(np.mod(a,2*np.pi),np.r_[edge_angles,2*np.pi],np.r_[smooth_edge,smooth_edge[0]])
 edgeblend=smooth(.992,1.22,r)
 continuation=base+edge*(1-edgeblend)+soft*edgeblend
 z=fields(x,y)[0];blend=smooth(.992,2.05,r);z=continuation*(1-blend)+z*blend
 z=carve(z,x,y)
 far=smooth(6500,9000,np.hypot(x,y));z=z*(1-far)+(-7170+260*noise(x,y,14)+70*noise(x,y,38))*far
 z=carve(z,x,y)
 return z,r
rings=[list(range(2048))]
radials=[(1.005,2048),(1.03,2048),(1.07,1024)]+[(float(r),1024 if r<15 else 512) for r in np.r_[np.linspace(1.10,4,135),np.linspace(4.05,15,180),np.linspace(15.3,40,60),np.geomspace(41,700,65)]]
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
from scipy.sparse import coo_matrix
ij=np.concatenate([F[:,[0,1]],F[:,[1,2]],F[:,[2,0]]]);ij=np.concatenate([ij,ij[:,::-1]])
adj=coo_matrix((np.ones(len(ij)),(ij[:,0],ij[:,1])),shape=(len(V),len(V))).tocsr()
deg=np.maximum(np.asarray(adj.sum(axis=1)),1)
for _ in range(3):
 avg=adj@norm/deg
 norm[:len(original)]=.45*norm[:len(original)]+.55*avg[:len(original)]
 norm/=np.maximum(np.linalg.norm(norm,axis=1,keepdims=True),1e-10)
name='SM_IV_PuzzleContinent_v20'
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
a=np.arctan2(Y-20,X)
# Unequal bare-earth wedges and exposed shoulders connect the fracture to local geology.
reach=1.07+.045*noise(X,Y,95)+.07*noise(X,Y,37)
scar=1-smooth(.98,reach,r)
fracture=np.array([.235,.24,.215])*(.92+.12*macro[...,None])
color=color*(1-scar[...,None])+fracture*scar[...,None]
# Soft settlement-toned clearings imply occupation without houses or farm grids.
color=color*(1-town[...,None]*.42)+np.array([.30,.29,.20])*town[...,None]*.42
color=color*(1-road[...,None]*.55)+np.array([.38,.32,.19])*road[...,None]*.55
rd,lk,ww,wl,wa=hydro(X,Y)
shore=np.maximum((1-smooth(ww+5,ww+20,rd))*smooth(ww-3,ww+3,rd),(1-smooth(1.03,1.085,lk))*smooth(.99,1.025,lk))
color=color*(1-shore[...,None]*.5)+np.array([.25,.285,.17])*shore[...,None]*.5
wc=np.stack([.018+fine*.004,.115+fine*.008,.145+fine*.008],-1);color=color*(1-water[...,None])+wc*water[...,None]
Image.fromarray(np.uint8(np.clip(color,0,1)*255)).convert('RGBA').save(S/'T_IV_ContinentAtlas20.png')

rows=json.loads((S/'living_continent_v17_instances.json').read_text());rows['House']=[];rows['HouseVar']=[]
for kind,points in rows.items():
 if not points:continue
 p=np.array(points);zz,rr=outside(p[:,0],p[:,1]);p[:,2]=zz+depth_shift;rd,lk,ww,wl,wa=hydro(p[:,0],p[:,1]);keep=(rr>1.12)&(rd>ww+28)&(lk>1.15);p=p[keep];rows[kind]=p.tolist()
(S/'puzzle_continent_v20_instances.json').write_text(json.dumps(rows))
edges=np.sort(np.concatenate([F[:,[0,1]],F[:,[1,2]],F[:,[2,0]]]),axis=1);_,counts=np.unique(edges,axis=0,return_counts=True)
seat=np.max(np.abs((V[:len(original)]-[0,0,base+depth_shift])/scale-original))
assert seat<1e-9 and int((counts==1).sum())==512 and int((counts>2).sum())==0
report={'uniform_scale':scale,'translation_m':[0,0,base+depth_shift],'inverse_fit_max_error_m':float(seat),'cavity_vertices_copied':len(original),'cavity_triangles_reversed':len(faces),'seam_vertices_shared':2048,'internal_open_edges':0,'outer_horizon_open_edges':512,'nonmanifold_edges':0,'houses':0,'farm_masks':0,'island_changed':False,'vertices':len(V),'triangles':len(F)}
(S/'puzzle_continent_v20_report.json').write_text(json.dumps(report,indent=2));print(report)


waterV=[[-1850,-1350,-7080+depth_shift+.12]];waterF=[];n=192
for a in np.linspace(0,2*np.pi,n,endpoint=False):
 radius=.995*(1+.07*np.sin(3*a)+.035*np.sin(5*a+1))
 waterV.append([-1850+390*radius*np.cos(a),-1350+230*radius*np.sin(a),-7080+depth_shift+.12])
for i in range(n):waterF.append((0,i+1,(i+1)%n+1))
ys=np.linspace(-7900,7900,3161);start=len(waterV)
for y in ys:
 x=float(river_curve(y));rd,lk,width,wl,wa=hydro(np.array([x]),np.array([y]))
 for side in [-1,1]:waterV.append([x+side*float(width[0]),float(y),float(wl[0])+depth_shift+.12])
for i in range(len(ys)-1):
 k=start+i*2;waterF.extend([(k,k+1,k+2),(k+1,k+3,k+2)])
with (S/'SM_IV_ContinentWater_v20.obj').open('w') as f:
 f.write('o SM_IV_ContinentWater_v20\n')
 for x,y,z in waterV:f.write(f'v {x*100:.5f} {-y*100:.5f} {z*100:.5f}\n')
 for face in waterF:f.write('f '+' '.join(str(i+1) for i in reversed(face))+'\n')
# Reground distant outcrops and exclude the watershed.
cliffs=json.loads((S/'continent_cliffs_v17.json').read_text());out=[]
for x,y,z,h,yaw in cliffs:
 zz,rr=outside(np.array([x]),np.array([y]));rd,lk,ww,wl,wa=hydro(np.array([x]),np.array([y]))
 if rr[0]>1.5 and rd[0]>250 and lk[0]>1.5:out.append([x,y,float(zz[0]+depth_shift),h,yaw])
(S/'continent_cliffs_v20.json').write_text(json.dumps(out))
ys=np.linspace(-7500,7500,3001);xs=river_curve(ys);rd,lk,ww,wl,wa=hydro(xs,ys);ground,_=outside(xs,ys)
assert np.all(np.diff(wl)>=-1e-8)
assert np.max(ground-wl)<-3
(S/'watershed_v20_validation.json').write_text(json.dumps({'samples':len(ys),'downstream_monotonic':True,'minimum_centerline_clearance_m':float(np.min(wl-ground))},indent=2))

