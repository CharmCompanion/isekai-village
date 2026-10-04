"""v08: larger lake and enclosing hills, protected settlement, distant mainland."""
import numpy as np, math,json
from pathlib import Path
from PIL import Image
S=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource');H=np.load(S/'height_floating_v07.npy');old=H.copy();X,Y=np.meshgrid(np.linspace(-600,600,1009),np.linspace(-600,600,1009))
def smooth(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
theta=np.arctan2((Y+373)/118,(X+285)/207);edge=1+.055*np.sin(theta*3)+.025*np.sin(theta*7+.4)
lake=np.hypot((X+285)/207,(Y+373)/118)/edge
# Rolling containment ridge on the outer western and southern banks.
rim=np.exp(-((lake-1.34)/.20)**2)*(1-smooth(-100,-50,X))*(1-smooth(-260,-235,Y))
H+=rim*(21+11*np.sin(X/53+Y/71)**2)
blend=1-smooth(.84,1.12,lake);bed=10.8+1.2*np.sin(X/65)*np.cos(Y/42)
H=H*(1-blend)+bed*blend
# Retain a controlled spillway connecting the larger basin to the existing fall.
rx=-285+18*np.sin((Y+355)/55);river=(1-smooth(6,12,np.abs(X-rx)))*smooth(-560,-550,Y)*(1-smooth(-470,-460,Y))
H=H*(1-river)+16.3*river
M=np.asarray(Image.open(S/'T_IV_Biome_Floating_v07.png')).copy()
# Gentle foothill breakup outside future town, keep authored routes and portals unchanged.
protected=(X>=-220)&(X<=300)&(Y>=-230)&(Y<=300)
routeprotect=smooth(0,55,M[...,0].astype(float))
outer=np.clip(np.maximum(np.maximum((-X-220)/60,(X-300)/60),(Y-300)/60),0,1)
foothill=outer*(1-routeprotect)*(1-smooth(200,260,H))*smooth(30,55,H)*smooth(-210,-80,Y)
H+=foothill*(2.7*np.sin(X/26+np.sin(Y/52))*np.sin(Y/31)+1.5*np.sin((X+Y)/12))
# Never alter the planning rectangle or authored road surface.
H=np.where(protected,old,H);H=np.where((M[...,0]>80)&(Y>-235),old,H)
assert np.array_equal(H[protected],old[protected])
raw=np.rint(32768+H*64).astype('<u2');raw.tofile(S/'IV_Refined_v08.r16');np.save(S/'height_refined_v08.npy',H)
Image.fromarray(np.stack([raw>>8,raw&255,np.zeros_like(raw),np.full_like(raw,255)],-1).astype('uint8')).save(S/'T_IV_RefinedHeight_RG.png')
M[...,1]=np.where(Y<-235,255*(1-smooth(.97,1.13,lake)),M[...,1]).astype('uint8')
# More graduated grassy foothills; cliff exposure follows slope as well as elevation.
dy,dx=np.gradient(H,1200/1008);slope=np.hypot(dx,dy)
rock=np.maximum(smooth(.45,1.1,slope),smooth(95,210,H)*.65)
M[...,2]=np.where(~protected,np.maximum(M[...,2]*.7,rock*255),M[...,2]).astype('uint8')
M[...,3]=(M[...,3]*.55).astype('uint8')
Image.fromarray(M).save(S/'T_IV_Biome_Refined_v08.png')
def obj(name,V,F):
 with (S/(name+'.obj')).open('w') as f:
  f.write('o '+name+'\n')
  for x,y,z in V:f.write(f'v {x*100:.3f} {-y*100:.3f} {z*100:.3f}\n')
  for x,y,z in V:f.write(f'vt {x/15000+.5:.6f} {y/15000+.5:.6f}\n')
  for face in F:f.write('f '+' '.join(f'{i+1}/{i+1}' for i in reversed(face))+'\n')
V=[(-285,-373,18)];F=[]
for i in range(256):
 t=2*math.pi*i/256;e=1+.055*math.sin(t*3)+.025*math.sin(t*7+.4);V.append((-285+207*e*1.03*math.cos(t),-373+118*e*1.03*math.sin(t),18))
for i in range(256):F.append((0,i+1,(i+1)%256+1))
obj('SM_IV_GrandSkyLake',V,F)
# Large distant continental relief: varied ridges, plains and a winding river valley.
a=np.linspace(-35000,35000,321);CX,CY=np.meshgrid(a,a)
riverx=3500+4200*np.sin(CY/8000)+1600*np.sin(CY/3100)
valley=np.exp(-((CX-riverx)/1000)**2)
ridge=(np.sin(CX/4900+np.sin(CY/7000))*np.cos(CY/5400))**2
mount=2300*ridge**2+500*np.sin(CX/2100)*np.cos(CY/2800)+240*np.sin((CX+CY)/950)
CH=-7400+np.maximum(0,mount)*(1-valley*.97)
V=list(zip(CX.flat,CY.flat,CH.flat));F=[]
for j in range(320):
 for i in range(320):
  k=j*321+i;F.extend([(k,k+1,k+321),(k+1,k+322,k+321)])
obj('SM_IV_DistantContinent',V,F)
(S/'refinement_v08.json').write_text(json.dumps({'lake_center':[-285,-373,18],'lake_dimensions_m':[414,236],'protected_height_samples':int(protected.sum()),'mainland_base_m':-7400,'mainland_span_m':70000},indent=2))
print('v08 height, masks, 414m lake and 70km distant continent written; settlement protected.')
