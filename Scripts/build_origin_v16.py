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
# Regional features are brought down to the scale of the island footprint.
land=-7040+65*noise(20)+25*noise(42)
# Extend the actual island rim profile outward from the small extraction core.
# This preserves the north crescent, east/west arms, and low southern opening.
H=gaussian_filter(np.load(S/'height_valley_v14.npy'),18)
sx=X/.35;sy=(Y-20)/.35+20
rr=radius(sx,sy)
bx=sx/np.maximum(rr,1.e-5)*.91
by=(sy-20)/np.maximum(rr,1.e-5)*.91+20
edge=map_coordinates(H,[(by+600)/1200*1008,(bx+600)/1200*1008],order=1,mode='nearest')
mountain=np.maximum(edge-45,0)
# Continuation follows each rim sector rather than an unrelated giant C ridge.
land+=mountain*.85*np.exp(-((rr-1.65)/.72)**2)
land+=mountain*.45*np.exp(-((rr-2.75)/1.10)**2)
land+=30*np.sin(X/180+np.sin(Y/210))*np.sin(Y/170)*np.exp(-((rr-2.2)/1.5)**2)
# Small river outside the extraction area, matched to the regional scale.
riverx=900+260*np.sin(Y/1800)+90*np.sin(Y/650)
valley=np.exp(-((X-riverx)/150)**2)
land=land*(1-.5*valley)+(-7030)*.5*valley

# The actual underside supplies the missing core's negative shape, at 1:1 scale.
verts=[]
for line in (S/'SM_IV_JoinedMountain_v13.obj').open():
 if line.startswith('v '):
  x,y,z=map(float,line.split()[1:4]);verts.append([x/100,-y/100,z/100])
v=np.array(verts);interp=LinearNDInterpolator(v[:,:2],v[:,2]);near=NearestNDInterpolator(v[:,:2],v[:,2])
r=radius(X/.35,(Y-20)/.35+20);region=r<2.2;query=np.c_[X[region]/.35,(Y[region]-20)/.35+20];core=interp(query);missing=~np.isfinite(core);core[missing]=near(query[missing]);scar=np.zeros_like(land);scar[region]=-7000+core*.45
disturb=(1-smooth(.98,1.30,r));land=land*(1-disturb)+scar*disturb
# Let the distant land roll below the horizon instead of ending as a flat board.
distance=np.hypot(X,Y);land-=np.maximum(distance-25000,0)**2/700000
gy,gx=np.gradient(land,axis,axis);norm=np.stack([-gx,-gy,np.ones_like(land)],-1);norm/=np.linalg.norm(norm,axis=-1,keepdims=True)
np.savez_compressed(S/'continent_origin_v16.npz',axis=axis,height=land)
with (S/'SM_IV_OriginContinent_v16.obj').open('w') as f:
 f.write('o SM_IV_OriginContinent_v16\n')
 for x,y,z in zip(X.flat,Y.flat,land.flat):f.write(f'v {x*100:.3f} {-y*100:.3f} {z*100:.3f}\n')
 for x,y in zip(X.flat,Y.flat):f.write(f'vt {x/70000+.5:.7f} {y/70000+.5:.7f}\n')
 for nx,ny,nz in norm.reshape(-1,3):f.write(f'vn {nx:.7f} {-ny:.7f} {nz:.7f}\n')
 for j in range(n-1):
  for i in range(n-1):
   k=j*n+i+1
   for face in [(k+n,k+1,k),(k+n,k+n+1,k+1)]:f.write('f '+' '.join(f'{q}/{q}/{q}' for q in face)+'\n')

print('Mountain profile sampled from the actual island; compact continuation around the hollow')
