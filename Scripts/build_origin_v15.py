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
r=radius(X/.35,(Y-20)/.35+20);region=r<2.2;query=np.c_[X[region]/.35,(Y[region]-20)/.35+20];core=interp(query);missing=~np.isfinite(core);core[missing]=near(query[missing]);scar=np.zeros_like(land);scar[region]=-7000+core*.45
disturb=(1-smooth(.98,1.85,r));land=land*(1-disturb)+scar*disturb
# Let the distant land roll below the horizon instead of ending as a flat board.
distance=np.hypot(X,Y);land-=np.maximum(distance-25000,0)**2/700000
gy,gx=np.gradient(land,axis,axis);norm=np.stack([-gx,-gy,np.ones_like(land)],-1);norm/=np.linalg.norm(norm,axis=-1,keepdims=True)
np.savez_compressed(S/'continent_origin_v15.npz',axis=axis,height=land)
with (S/'SM_IV_OriginContinent_v15.obj').open('w') as f:
 f.write('o SM_IV_OriginContinent_v15\n')
 for x,y,z in zip(X.flat,Y.flat,land.flat):f.write(f'v {x*100:.3f} {-y*100:.3f} {z*100:.3f}\n')
 for x,y in zip(X.flat,Y.flat):f.write(f'vt {x/70000+.5:.7f} {y/70000+.5:.7f}\n')
 for nx,ny,nz in norm.reshape(-1,3):f.write(f'vn {nx:.7f} {-ny:.7f} {nz:.7f}\n')
 for j in range(n-1):
  for i in range(n-1):
   k=j*n+i+1
   for face in [(k+n,k+1,k),(k+n,k+n+1,k+1)]:f.write('f '+' '.join(f'{q}/{q}/{q}' for q in face)+'\n')

print('Reduced hollow: 35 percent width; 12.25 percent footprint area')
