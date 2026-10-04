"""Reusable sculpted landmark architecture, real mesh detail and material slots."""
from pathlib import Path
import numpy as np,json,math
S=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource');O=S/'Civilizations29';O.mkdir(exist_ok=True)
class Mesh:
 def __init__(self):self.v=[];self.f=[];self.mat=[]
 def part(self,v,f,mat):
  n=len(self.v);self.v.extend(v);self.f.extend([[n+i for i in q] for q in f]);self.mat.extend([mat]*len(f))
 def rings(self,rings,n,mat,xy=(0,0),yaw=0):
  v=[]
  for z,rx,ry in rings:
   for i in range(n):
    a=2*np.pi*i/n+yaw;v.append([xy[0]+rx*np.cos(a),xy[1]+ry*np.sin(a),z])
  f=[]
  for j in range(len(rings)-1):
   for i in range(n):
    a=j*n+i;b=j*n+(i+1)%n;c=b+n;dd=a+n;f.extend([[a,b,c],[a,c,dd]])
  for i in range(1,n-1):f.extend([[0,i+1,i],[(len(rings)-1)*n,(len(rings)-1)*n+i,(len(rings)-1)*n+i+1]])
  self.part(v,f,mat)
 def cyl(self,x,y,z,r,h,mat,n=32):self.rings([(z,r*.96,r*.96),(z+.4,r,r),(z+h-.4,r,r),(z+h,r*.96,r*.96)],n,mat,(x,y))
 def box(self,x,y,z,w,d,h,mat,b=.3,yaw=0):
  b=min(b,w*.2,d*.2,h*.2);v=[]
  for zz,inset in [(z,b),(z+b,0),(z+h-b,0),(z+h,b)]:
   a=w/2-inset;c=d/2-inset;be=min(b,a*.5,c*.5)
   pts=[(a-be,c),( -a+be,c),(-a,c-be),(-a,-c+be),(-a+be,-c),(a-be,-c),(a,-c+be),(a,c-be)]
   for u,t in pts:v.append([x+u*np.cos(yaw)-t*np.sin(yaw),y+u*np.sin(yaw)+t*np.cos(yaw),zz])
  f=[]
  for j in range(3):
   for i in range(8):a=j*8+i;bb=j*8+(i+1)%8;f.extend([[a,bb,bb+8],[a,bb+8,a+8]])
  for i in range(1,7):f.extend([[0,i+1,i],[24,24+i,24+i+1]])
  self.part(v,f,mat)
 def roof(self,x,y,z,w,d,h,mat):
  # Tiled roof with a softened ridge, eaves and several raised courses.
  self.part([[x-w/2,y-d/2,z],[x+w/2,y-d/2,z],[x+w/2,y+d/2,z],[x-w/2,y+d/2,z],[x,y-d/2,z+h],[x,y+d/2,z+h]],[[0,4,1],[3,2,5],[0,3,5],[0,5,4],[1,4,5],[1,5,2],[0,1,2],[0,2,3]],mat)
  self.box(x,y,z+h-.3,.8,d+1,.7,'trim')
  for j in range(1,7):
   u=j/8;self.box(x-w/2*(1-u),y,z+h*u,.55,d+.6,.4,mat,b=.1);self.box(x+w/2*(1-u),y,z+h*u,.55,d+.6,.4,mat,b=.1)
 def torus(self,x,y,z,r,t,mat,vertical=False):
  v=[];n=48;m=8
  for i in range(n):
   a=i*np.pi*2/n
   for j in range(m):
    b=j*np.pi*2/m;u=(r+t*np.cos(b))*np.cos(a);v1=(r+t*np.cos(b))*np.sin(a);zz=t*np.sin(b);v.append([x+u,y+(zz if vertical else v1),z+(v1 if vertical else zz)])
  f=[]
  for i in range(n):
   for j in range(m):a=i*m+j;b=((i+1)%n)*m+j;c=((i+1)%n)*m+(j+1)%m;d=i*m+(j+1)%m;f.extend([[a,b,c],[a,c,d]])
  self.part(v,f,mat)
 def write(self,name):
  v=np.array(self.v);f=np.array(self.f);norm=np.zeros_like(v);c=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]])
  for k in range(3):np.add.at(norm,f[:,k],c)
  norm/=np.maximum(np.linalg.norm(norm,axis=1,keepdims=True),1e-9)
  with (O/(name+'.obj')).open('w') as out:
   out.write('o '+name+'\n')
   for x,y,z in v:out.write(f'v {x*100:.5f} {-y*100:.5f} {z*100:.5f}\n')
   for x,y,z in v:out.write(f'vt {x/12:.6f} {z/12:.6f}\n')
   for x,y,z in norm:out.write(f'vn {x:.6f} {-y:.6f} {z:.6f}\n')
   last=None
   for face,mat in zip(f,self.mat):
    if last!=mat:out.write('usemtl '+mat+'\n');last=mat
    out.write('f '+' '.join(f'{i+1}/{i+1}/{i+1}' for i in face[::-1])+'\n')
  return {'name':name,'vertices':len(v),'triangles':len(f),'materials':sorted(set(self.mat))}
def tower(m,x,y,z,r,h,mat='stone',spire=False):
 m.rings([(z,r*1.18,r*1.18),(z+3,r*1.18,r*1.18),(z+5,r,r),(z+h-4,r,r),(z+h-2,r*1.13,r*1.13),(z+h,r*1.13,r*1.13)],40,mat,(x,y))
 for zz in [z+6,z+h*.48,z+h-5]:m.cyl(x,y,zz,r*1.04,1.2,'trim',40)
 for zz in [z+h*.3,z+h*.65]:
  for a in np.arange(8)*np.pi/4:m.box(x+r*np.cos(a),y+r*np.sin(a),zz,2,.65,5,'window',b=.25,yaw=a+np.pi/2)
 if spire:
  m.rings([(z+h,r*1.22,r*1.22),(z+h+2,r*1.22,r*1.22),(z+h+20,r*.35,r*.35),(z+h+31,.3,.3)],40,'roof',(x,y));m.cyl(x,y,z+h+30,.45,7,'gold',16);m.torus(x,y,z+h+39,2.3,.5,'gold',True)
 else:
  for a in np.arange(12)*np.pi/6:m.box(x+r*np.cos(a),y+r*np.sin(a),z+h,3.3,3.3,4,mat)
manifest=[]
m=Mesh();tower(m,0,0,-8,12,57,spire=True);manifest.append(m.write('SM_Civ29_SacredTower'))
m=Mesh();tower(m,0,0,-8,10,39);manifest.append(m.write('SM_Civ29_Bastion'))
m=Mesh();tower(m,-24,0,-8,10,49,spire=True);tower(m,24,0,-8,10,49,spire=True)
for x in [-15,15]:m.box(x,0,-10,6,14,28,'stone')
# A true open semicircular gateway, including its inner soffit.
v=[]
for y in [-7,7]:
 for r in [12,18]:
  for a in np.linspace(0,np.pi,25):v.append([r*np.cos(a),y,18+r*np.sin(a)])
f=[]
for i in range(24):
 for a,b,c,d in [(i,i+1,i+26,i+25),(i+50,i+75,i+76,i+51),(i,i+50,i+51,i+1),(i+25,i+26,i+76,i+75)]:f.extend([[a,b,c],[a,c,d]])
m.part(v,f,'stone');m.box(0,0,36,46,16,3,'trim');manifest.append(m.write('SM_Civ29_Gatehouse'))
m=Mesh();m.cyl(0,0,-2,.22,22,'gold',12)
v=[]
for j in range(9):
 for i in range(5):v.append([i*1.4,.4*np.sin(i*.6+j*.3),18-j*.85])
f=[]
for j in range(8):
 for i in range(4):a=j*5+i;f.extend([[a,a+1,a+6],[a,a+6,a+5]])
m.part(v,f,'crimson');m.torus(2.8,-.15,14.5,1.3,.24,'gold',True);manifest.append(m.write('SM_Civ29_Banner'))
m=Mesh();m.box(0,0,-12,42,7,38,'stone',.7);m.box(0,0,24,42,9,2,'trim')
for x in range(-18,20,6):m.box(x,0,26,3.5,8,4,'stone')
for x in [-17,-6,6,17]:m.box(x,3.6,8,1.4,.8,5,'window',.2)
manifest.append(m.write('SM_Civ29_CurtainWall'))
m=Mesh();m.box(0,0,-9,92,146,12,'stone',1.2);m.box(0,0,0,54,126,39,'stone',1);m.roof(0,0,39,62,135,24,'roof');m.box(0,5,8,104,38,30,'stone');m.roof(0,5,38,112,44,21,'roof')
for x in [-34,34]:
 tower(m,x,-60,0,12,67,spire=True)
 for y in [-37,-12,14,40]:
  m.box(x,y,0,8,10,27,'stone',.6);m.box(x*.82,y,20,4,8,15,'trim')
  m.box(x*.805,y,15,1,5,15,'window')
tower(m,0,16,38,13,38,spire=True);m.box(0,-64,1,16,3,21,'window');m.torus(0,-65,30,6,1,'gold',True)
for j in range(9):m.box(0,-80-j*3,-j*.6,36+j*2,3,1,'stone')
manifest.append(m.write('SM_Civ29_Cathedral'))
m=Mesh();m.cyl(0,0,-8,27,12,'stone');m.cyl(0,0,3,20,43,'plaster');m.cyl(0,0,44,24,4,'gold');m.rings([(48,24,24),(52,23,23),(59,19,19),(65,12,12),(68,1,1)],48,'arcane');m.torus(0,0,57,31,1.3,'gold');m.torus(0,0,80,14,1.1,'gold',True)
for a in np.arange(8)*np.pi/4:
 x=20*np.cos(a);y=20*np.sin(a);m.box(x,y,13,3,1.3,20,'arcane',yaw=a+np.pi/2);m.cyl(x*1.35,y*1.35,0,2,47,'trim',16)
m.rings([(68,4,4),(77,6,6),(91,.1,.1)],12,'crystal');manifest.append(m.write('SM_Civ29_ArcaneTower'))
m=Mesh();m.box(0,0,-7,59,76,10,'stone');m.box(0,0,2,46,62,21,'plaster');m.roof(0,0,23,54,71,12,'roof')
for x in [-25,25]:
 for y in [-22,0,22]:m.cyl(x,y,0,2,24,'gold',16);m.box(x*.94,y,7,1,7,10,'arcane',yaw=np.pi/2)
m.torus(0,0,40,17,.8,'gold');m.rings([(32,5,5),(40,7,7),(53,.1,.1)],12,'crystal');manifest.append(m.write('SM_Civ29_Manufactory'))
m=Mesh()
for i in range(5):m.box(0,0,-6+i*3,88-i*9,100-i*9,3.5,'darkstone',.8)
for x in [-27,27]:
 for y in [-28,0,28]:m.cyl(x,y,9,3,27,'darkstone',24);m.cyl(x,y,34,4,3,'gold',24)
m.box(0,0,36,68,77,5,'darkstone');m.roof(0,0,41,70,80,15,'darkstone');m.rings([(56,3,3),(69,4,4),(87,.1,.1)],8,'amber');m.box(0,0,9,26,36,18,'darkstone');m.box(0,-19,10,10,2,13,'window');manifest.append(m.write('SM_Civ29_Sanctuary'))
m=Mesh();m.cyl(0,0,-6,8,8,'stone');m.rings([(2,8,8),(24,5,5)],32,'plaster');m.rings([(24,7,7),(34,.1,.1)],32,'roof')
manifest.append(m.write('SM_Civ29_Mill'))
m=Mesh();m.box(0,0,0,22,35,15,'plaster');m.roof(0,0,15,26,40,11,'roof')
for x in [-10,10]:
 for y in [-15,0,15]:m.box(x,y,-7,1.3,1.3,25,'wood')
m.box(0,-17.6,1,7,.5,10,'wood');manifest.append(m.write('SM_Civ29_Granary'))
m=Mesh();m.box(0,0,0,27,28,2,'wood');m.box(0,0,2,21,22,11,'plaster');m.roof(0,0,13,29,30,9,'tealroof')
for x in [-11,11]:
 for y in [-11,11]:m.cyl(x,y,-16,.65,18,'wood',12)
for x in [-6,6]:m.box(x,-11.2,5,3,.5,4,'window');m.box(x,-11.5,4.7,3.6,.7,.7,'wood')
m.box(0,-11.5,2,3,.6,7,'wood');manifest.append(m.write('SM_Civ29_StiltHouse'))
m=Mesh();m.box(0,0,0,7,24,1,'wood')
for x in [-3,3]:
 for y in [-10,0,10]:m.cyl(x,y,-16,.4,20,'wood',10)
for x in [-3,3]:m.box(x,0,3, .35,24,.5,'wood',.1)
manifest.append(m.write('SM_Civ29_Boardwalk'))
m=Mesh();m.cyl(0,0,-.2,1.4,.4,'mud',16)
rg=np.random.default_rng(6)
for i in range(22):
 x,y=rg.uniform(-1.2,1.2,2);z=rg.uniform(1.4,3.3);m.cyl(x,y,0,.045,z,'reed',6);m.cyl(x,y,z-.3,.13,.5,'seed',8)
manifest.append(m.write('SM_Civ29_Reeds'))
(O/'assets.json').write_text(json.dumps(manifest,indent=2));print([(x['name'],x['triangles']) for x in manifest],flush=True)
