"""Low earthen basin lip and one inverted, ridge-carved mountain. Metres."""
import numpy as np, math, json
from pathlib import Path
from PIL import Image
from scipy.ndimage import map_coordinates, gaussian_filter1d
S=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource')
H=np.load(S/'height_refined_v08.npy'); original=H.copy()
X,Y=np.meshgrid(np.linspace(-600,600,1009),np.linspace(-600,600,1009))
def smooth(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def outline(a):
 return (1+.012*np.sin(7*a)+.008*np.sin(13*a))/(abs(np.cos(a))**4+abs(np.sin(a))**4)**.25
a=np.arctan2((Y-20)/570,X/580); r=(abs(X/580)**4+abs((Y-20)/570)**4)**.25/(1+.012*np.sin(7*a)+.008*np.sin(13*a))
angles=np.linspace(-np.pi,np.pi,2048,endpoint=False);o=outline(angles)
anchor=map_coordinates(H,[(20+570*np.sin(angles)*o*.80+600)*.84,(580*np.cos(angles)*o*.80+600)*.84],order=1,mode='nearest')
anchor=gaussian_filter1d(np.maximum(anchor,26),25,mode='wrap')
floor=np.interp(a,angles,anchor,period=math.tau)
# A broad 90m earthen rise, 10-16m high; rounded crest gently rolls outward.
lip=(11+3*np.sin(3*a+.5)+2*np.sin(5*a))*smooth(.80,.965,r)-3*smooth(.975,1.02,r)
target=floor+lip
blend=smooth(.80,.945,r)
blend=np.maximum(blend,smooth(400,470,X)*smooth(-330,-240,Y))
# Retain the existing northern mountain crescent above the low lip.
target=np.maximum(target,original*smooth(230,320,Y))
protected=(X>=-220)&(X<=300)&(Y>=-230)&(Y<=300)
dock=(1-smooth(15,30,abs(X-275)))*(1-smooth(-460,-435,Y))
riverx=-285+18*np.sin((Y+355)/55)
fall=(1-smooth(10,22,abs(X-riverx)))*(1-smooth(-485,-465,Y))
blend*= (1-dock)*(1-fall)*(~protected)
H=H*(1-blend)+target*blend
raw=np.rint(32768+H*64).astype('<u2');raw.tofile(S/'IV_DishPeak_v11.r16');np.save(S/'height_dish_peak_v11.npy',H)
Image.fromarray(np.stack([raw>>8,raw&255,np.zeros_like(raw),np.full_like(raw,255)],-1).astype('uint8')).save(S/'T_IV_DishHeight_RG.png')
biome=np.asarray(Image.open(S/'T_IV_Biome_Refined_v08.png')).copy()
gy,gx=np.gradient(H,1200/1008);slope=np.hypot(gx,gy)
biome[...,0]=np.where(blend>.1,biome[...,0]*(1-blend),biome[...,0])
biome[...,2]=np.where(blend>.1,np.maximum(0,smooth(.55,1.4,slope)*255),biome[...,2])
Image.fromarray(biome).save(S/'T_IV_Biome_Dish_v11.png')
assert np.array_equal(H[protected],original[protected])
def height(x,y):return float(map_coordinates(H,[[(y+600)*.84],[(x+600)*.84]],order=1,mode='nearest')[0])
# Four unequal arêtes running to one offset summit. Broad concave faces
# between them are the form, with subsidiary gullies cut into those faces.
N=160; K=62; V=[];F=[]
for j in range(K):
 t=j/K; radial=1-t
 for i in range(N):
  ang=math.tau*i/N;out=float(outline(ang));bx=580*math.cos(ang)*out;by=570*math.sin(ang)*out+20
  cx=-80*t;cy=38*t
  x=bx*radial+cx;y=by*radial+cy
  shifted=ang+.055*math.sin(radial*4)
  distances=[abs(math.atan2(math.sin(shifted-c),math.cos(shifted-c))) for c in [.20,1.78,3.43,4.91]]
  d=min(distances)
  # Planar crests, strongly hollowed faces, no horizontal ring courses.
  facecut=min(d/.67,1)**.72
  envelope=math.sin(math.pi*radial)**.85
  depth=880*t**1.03-195*facecut*envelope
  branch=abs(math.sin(ang*9+radial*2.8))**1.2
  small=abs(math.sin(ang*23-radial*9))**5
  depth-=envelope*(65*branch+14*small)*smooth(.08,.35,radial)
  # Very small broken bedding steps: relief follows the mountain faces.
  depth+=envelope*7.0*math.sin(x/23+y/41+depth/19)
  z=height(bx,by)*(1-t)**7-depth
  V.append((x,y,z))
for j in range(K-1):
 for i in range(N):
  q=j*N+i;b=j*N+(i+1)%N;c=q+N;d=b+N
  F.extend([(q,c,b),(b,c,d)])
V.append((-80,38,-884))
for i in range(N):F.append(((K-1)*N+i,len(V)-1,(K-1)*N+(i+1)%N))
v=np.array(V); conv=v*np.array([1,-1,1]); faces=np.array(F)[:,::-1]
normals=np.zeros_like(conv)
for f in faces:
 n=np.cross(conv[f[1]]-conv[f[0]],conv[f[2]]-conv[f[0]])
 for idx in f:normals[idx]+=n
normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-9)
with (S/'SM_IV_InvertedMountain_v11.obj').open('w') as f:
 f.write('o SM_IV_InvertedMountain_v11\n')
 for x,y,z in conv:f.write(f'v {x*100:.4f} {y*100:.4f} {z*100:.4f}\n')
 for x,y,z in v:f.write(f'vt {x/75:.6f} {z/75:.6f}\n')
 for face in faces:
  n=np.cross(conv[face[1]]-conv[face[0]],conv[face[2]]-conv[face[0]]);n/=np.linalg.norm(n)
  f.write('vn '+' '.join(f'{a:.7f}' for a in n)+'\n')
 for idx,face in enumerate(faces):f.write('f '+' '.join(f'{i+1}/{i+1}/{idx+1}' for i in face)+'\n')
report={'protected_samples':int(protected.sum()),'protected_exact':True,'mesh_vertices':len(V),'mesh_triangles':len(F),'summit_m':[-80,38,-884],'separate_rock_accents':0,'lip_rise_m':[6,16]}
(S/'dish_peak_v11.json').write_text(json.dumps(report,indent=2));print(report)
