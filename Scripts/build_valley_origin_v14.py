"""Retain the joined island boundary; sculpt interior hills and its continental birthplace."""
from pathlib import Path
import numpy as np,math,json
from scipy.ndimage import map_coordinates,gaussian_filter
from scipy.interpolate import LinearNDInterpolator,NearestNDInterpolator
from PIL import Image
S=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource')
def smooth(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def radius(x,y):
 a=np.arctan2((y-20)/570,x/580)
 return ((abs(x/580)**4+abs((y-20)/570)**4)**.25)/(1+.012*np.sin(7*a)+.008*np.sin(13*a))
H=np.load(S/'height_dish_peak_v11.npy');old=H.copy();X,Y=np.meshgrid(np.linspace(-600,600,1009),np.linspace(-600,600,1009));r=radius(X,Y)
# Unequal low hills, with broad inward slopes; retain the outer repaired seam.
raise_by=np.zeros_like(H)
for x,y,sx,sy,z in [(-515,-80,75,120,13),(-520,175,65,95,11),(-490,-315,65,80,10),(-125,-505,115,55,12),(70,-505,90,60,15),(415,-425,95,60,16),(530,-245,65,110,17),(535,-40,65,100,14),(530,165,60,95,10)]:
 raise_by+=z*np.exp(-((X-x)/sx)**2-((Y-y)/sy)**2)
raise_by*=smooth(.77,.86,r)*(1-smooth(.952,.988,r))
protected=(X>=-220)&(X<=300)&(Y>=-230)&(Y<=300)
lake=((X+285)/225)**2+((Y+373)/133)**2
raise_by*=smooth(1.02,1.25,lake)
routes=json.loads((S/'mountain_routes_v04.json').read_text())
points=[p[:2] for route in routes['routes'] for p in route['points']]
points += [[-395,-205],[-450,-275],[-500,-325],[-550,-350]]
points += [[275,y] for y in np.linspace(-440,-580,24)]
points += [[-285+18*np.sin((y+355)/55),y] for y in np.linspace(-465,-560,24)]
for x,y in points:raise_by*=smooth(13,26,np.hypot(X-x,Y-y))
raise_by[protected]=0;raise_by[r>=.988]=0;H+=raise_by
assert np.array_equal(H[protected],old[protected]);assert np.array_equal(H[r>=.988],old[r>=.988])
raw=np.rint(32768+H*64).astype('<u2');raw.tofile(S/'IV_Valley_v14.r16');np.save(S/'height_valley_v14.npy',H)
Image.fromarray(np.stack([raw>>8,raw&255,np.zeros_like(raw),np.full_like(raw,255)],-1).astype('uint8')).save(S/'T_IV_ValleyHeight_RG.png')
biome=np.asarray(Image.open(S/'T_IV_Biome_Dish_v11.png')).copy();gy,gx=np.gradient(H,1200/1008);slope=np.hypot(gx,gy)
biome[...,2]=np.where(raise_by>1,np.maximum(biome[...,2],smooth(.65,1.3,slope)*210),biome[...,2]);Image.fromarray(biome).save(S/'T_IV_Biome_Valley_v14.png')

# Adaptive sampling: detail at the extraction scar, gentle broad relief far away.
axis=np.unique(np.r_[np.linspace(-100000,100000,201),np.linspace(-35000,35000,281),np.linspace(-4000,4000,161),np.linspace(-1100,1100,177)])
X,Y=np.meshgrid(axis,axis);n=len(axis);rng=np.random.default_rng(291414)
def noise(k):
 f=rng.uniform(0,1,(k,k));return map_coordinates(f,[(Y+35000)/70000*(k-1),(X+35000)/70000*(k-1)],order=3,mode='nearest')
land=-7350+420*noise(10)+180*noise(20)+55*noise(42)
# A connected crescent mountain system, north and west with an eastern arm.
ridge=np.zeros_like(land)
chain=[(-14000,-5000),(-10000,1500),(-5800,5100),(-1000,6400),(4600,5300),(9800,1800),(12500,-3200)]
for (ax,ay),(bx,by) in zip(chain[:-1],chain[1:]):
 t=np.clip(((X-ax)*(bx-ax)+(Y-ay)*(by-ay))/((bx-ax)**2+(by-ay)**2),0,1)
 dist=np.hypot(X-ax-t*(bx-ax),Y-ay-t*(by-ay));ridge=np.maximum(ridge,np.exp(-(dist/2100)**2))
land+=1800*ridge*(.40+.60*noise(30))
# Broad eroded spurs break up the long crest without corrugated micro-noise.
for x,y,sx,sy,z in [(-12000,-1500,2200,3800,650),(-7600,4200,2600,1700,850),(-2500,6400,2000,2400,1150),(3000,5700,2500,1800,900),(8200,3300,1700,3100,1100),(11700,-2100,2200,2500,750),(-19000,14500,6500,3500,1600),(16000,19000,5000,8000,2100),(-23000,-19000,7500,4500,1200)]:
 land+=z*np.exp(-((X-x)/sx)**2-((Y-y)/sy)**2)
land+=160*(noise(65)-.5)*np.clip(ridge*1.4,0,1)
land+=380*np.exp(-((X+2000)/3200)**2-((Y-1700)/2700)**2)
land+=460*np.exp(-((X-1700)/2100)**2-((Y-2200)/2900)**2)
riverx=5200+2900*np.sin(Y/10500)+900*np.sin(Y/4500)
valley=np.exp(-((X-riverx)/1500)**2);land=land*(1-.60*valley)+(-7150)*.60*valley

# The actual underside supplies the missing core's negative shape, at 1:1 scale.
verts=[]
for line in (S/'SM_IV_JoinedMountain_v13.obj').open():
 if line.startswith('v '):
  x,y,z=map(float,line.split()[1:4]);verts.append([x/100,-y/100,z/100])
v=np.array(verts);interp=LinearNDInterpolator(v[:,:2],v[:,2]);near=NearestNDInterpolator(v[:,:2],v[:,2])
r=radius(X,Y);region=r<2.2;query=np.c_[X[region],Y[region]];core=interp(query);missing=~np.isfinite(core);core[missing]=near(query[missing]);scar=np.zeros_like(land);scar[region]=-7000+core
disturb=(1-smooth(.98,1.85,r));land=land*(1-disturb)+scar*disturb
# Let the distant land roll below the horizon instead of ending as a flat board.
distance=np.hypot(X,Y);land-=np.maximum(distance-25000,0)**2/700000
gy,gx=np.gradient(land,axis,axis);norm=np.stack([-gx,-gy,np.ones_like(land)],-1);norm/=np.linalg.norm(norm,axis=-1,keepdims=True)
np.savez_compressed(S/'continent_origin_v14.npz',axis=axis,height=land)
with (S/'SM_IV_OriginContinent_v14.obj').open('w') as f:
 f.write('o SM_IV_OriginContinent_v14\n')
 for x,y,z in zip(X.flat,Y.flat,land.flat):f.write(f'v {x*100:.3f} {-y*100:.3f} {z*100:.3f}\n')
 for x,y in zip(X.flat,Y.flat):f.write(f'vt {x/70000+.5:.7f} {y/70000+.5:.7f}\n')
 for nx,ny,nz in norm.reshape(-1,3):f.write(f'vn {nx:.7f} {-ny:.7f} {nz:.7f}\n')
 for j in range(n-1):
  for i in range(n-1):
   k=j*n+i+1
   for face in [(k+n,k+1,k),(k+n,k+n+1,k+1)]:f.write('f '+' '.join(f'{q}/{q}/{q}' for q in face)+'\n')
report={'protected_town_samples':int(protected.sum()),'outer_join_heights_unchanged':True,'hill_raise_max_m':float(raise_by.max()),'continent_width_m':200000,'continent_vertices':n*n,'scar_core_width_m':1160,'scar_disturbance_width_m':2146,'scar_floor_m':float(land[r<1].min()),'scar_uses_actual_underside':True}
(S/'valley_origin_v14.json').write_text(json.dumps(report,indent=2));print(report)
