"""A continuous asymmetric inverted horn with branched gullies and a dense rim seam."""
from pathlib import Path
import numpy as np, math, json
from scipy.ndimage import map_coordinates
S=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource')
H=np.load(S/'height_dish_peak_v11.npy')
def outline(a):return (1+.012*np.sin(7*a)+.008*np.sin(13*a))/(abs(np.cos(a))**4+abs(np.sin(a))**4)**.25
def height(x,y):return float(map_coordinates(H,[[(y+600)*.84],[(x+600)*.84]],order=1,mode='nearest')[0])
def delta(a,b):return math.atan2(math.sin(a-b),math.cos(a-b))
def smooth(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def noise(x,y,z):
 # Linear tetrahedral interpolation yields broken planar fracture faces,
 # unlike smooth value noise, which rounded the stone into soft lumps.
 p=np.array([.86*x-.5*y+.1*z,.46*x+.81*y-.36*z,.1*x+.35*y+.93*z]);i=np.floor(p);f=p-i;o=np.argsort(-f)
 c1=np.zeros(3);c1[o[0]]=1;c2=c1.copy();c2[o[1]]=1
 weights=[1-f[o[0]],f[o[0]]-f[o[1]],f[o[1]]-f[o[2]],f[o[2]]];v=0.
 for c,w in zip([np.zeros(3),c1,c2,np.ones(3)],weights):
  h=math.sin(float(np.dot(i+c,[127.1,311.7,74.7]))+31.2)*43758.5453;v+=(h-math.floor(h))*w
 return v*2-1
V=[];UV=[];F=[];rings=[]
levels=[(0.,2048),(.007,2048),(.018,1024),(.033,512)]+[(float(t),256) for t in np.linspace(.05,.985,76)]
gullies=[(.42,.095,62,.15),(1.10,.08,85,-.23),(2.09,.13,105,.21),(2.72,.065,64,-.17),(3.82,.115,97,-.26),(4.38,.075,58,.19),(5.26,.13,110,.20),(5.87,.07,67,-.16)]
for j,(t0,count) in enumerate(levels):
 ring=[]
 for i in range(count):
  angle=math.tau*i/count
  t=t0 if j<4 else t0+.0025*math.sin(i*17.3+j*4.2)*math.sin(math.pi*t0)
  radial=1-t;out=outline(angle);bx=580*math.cos(angle)*out;by=570*math.sin(angle)*out+20;h=height(bx,by)
  shifted=angle+.075*math.sin(t*4.1)
  distances=[abs(delta(shifted,c)) for c in [.16,1.69,3.46,4.98]]
  d=min(distances);cut=min(d/.70,1)**.80;env=math.sin(math.pi*t)**.9
  # Unequal shoulders along connected rock buttresses, not attached stones.
  spur=0.
  for centre,at,width,strength in [(.18,.28,.45,.24),(1.7,.39,.38,.14),(3.45,.24,.48,.20),(4.98,.48,.40,.18),(2.75,.30,.28,-.09),(5.8,.31,.25,-.12)]:
   spur+=strength*math.exp(-(delta(angle,centre)/width)**2)*math.exp(-((t-at)/.19)**2)
  scale=radial*(1+spur-.09*cut*env)
  bendx=-82*t+30*math.sin(math.pi*t)*math.sin(t*3);bendy=38*t-22*math.sin(math.pi*t)
  x=bx*scale+bendx;y=(by-20)*scale+20+bendy
  depth=880*t**1.04-125*cut*env
  gully=0
  for centre,width,amount,lean in gullies:
   dist=delta(angle,centre+lean*t)
   gully+=amount*.60*math.exp(-(dist/width)**2)*env*smooth(.035,.20,t)*(1-smooth(.77,.96,t))
   # One tributary joins the main gully part way down its face.
   fork=centre+lean*t+.16*(1-smooth(.12,.52,t))
   gully+=amount*.24*math.exp(-(delta(angle,fork)/(width*.55))**2)*env*(1-smooth(.45,.65,t))*smooth(.06,.18,t)
  depth-=gully
  relief=(noise(x/170,y/170,depth/130)*95+noise(x/63,y/63,depth/53)*31+noise(x/25,y/25,depth/23)*6)*env*smooth(.008,.06,t)
  z=h*(1-t)**5.5-depth+relief
  # Seam overlaps the native edge by centimetres, not a broad floating collar.
  if j==0:z-=.12
  ring.append(len(V));V.append((x,y,z));UV.append((min(1,cut*.65+gully/220),max(0,h-z)/100))
 rings.append(ring)
for outer,inner in zip(rings[:-1],rings[1:]):
 n=len(outer);m=len(inner);ratio=n//m
 for i in range(m):
  for k in range(ratio):F.append((outer[(i*ratio+k)%n],inner[i],outer[(i*ratio+k+1)%n]))
  F.append((outer[((i+1)*ratio)%n],inner[i],inner[(i+1)%m]))
V.append((-82,58,-884));UV.append((0,9.))
for i in range(len(rings[-1])):F.append((rings[-1][i],len(V)-1,rings[-1][(i+1)%len(rings[-1])]))
v=np.array(V);conv=v*np.array([1,-1,1]);faces=np.array(F)[:,::-1]
# Retain broad angular faces. No smooth normals that turn the rock into clay.
with (S/'SM_IV_OrbitMountain_v12.obj').open('w') as f:
 f.write('o SM_IV_OrbitMountain_v12\n')
 for x,y,z in conv:f.write(f'v {x*100:.5f} {y*100:.5f} {z*100:.5f}\n')
 for u,v in UV:f.write(f'vt {u:.6f} {v:.6f}\n')
 for face in faces:
  n=np.cross(conv[face[1]]-conv[face[0]],conv[face[2]]-conv[face[0]]);n/=np.linalg.norm(n);f.write('vn '+' '.join(f'{q:.7f}' for q in n)+'\n')
 for ni,face in enumerate(faces):f.write('f '+' '.join(f'{i+1}/{i+1}/{ni+1}' for i in face)+'\n')
edges={}
for face in F:
 for a,b in zip(face,(face[1],face[2],face[0])):
  k=tuple(sorted((a,b)));edges[k]=edges.get(k,0)+1
assert all(n in [1,2] for n in edges.values())
assert sum(n==1 for n in edges.values())==2048
report={'vertices':len(V),'triangles':len(F),'open_edges_at_landscape_seam':2048,'internal_open_edges':0,'nonmanifold_edges':0,'terrain_changed':False,'single_summit':[-82,58,-884]}
(S/'orbit_mountain_v12.json').write_text(json.dumps(report,indent=2));print(report)
