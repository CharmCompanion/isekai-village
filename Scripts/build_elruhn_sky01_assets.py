"""Original El Ruhn levitation/tower art. Coordinates metres; deterministic source."""
from pathlib import Path
import math,json,numpy as np
from PIL import Image,ImageDraw,ImageFont
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/ElRuhnSky01';O.mkdir(parents=True,exist_ok=True)
TAU=math.tau
class Mesh:
 def __init__(self):self.v=[];self.f=[];self.m=[]
 def part(self,v,f,m):
  k=len(self.v);self.v.extend(v);self.f.extend([[k+i for i in q] for q in f]);self.m.extend([m]*len(f))
 def profile(self,rz,m='ivory',n=64,c=(0,0),phase=0,cap=True):
  v=[[c[0]+r*math.cos(TAU*i/n+phase),c[1]+r*math.sin(TAU*i/n+phase),z] for r,z in rz for i in range(n)];f=[]
  for j in range(len(rz)-1):
   for i in range(n):a=j*n+i;b=j*n+(i+1)%n;f.extend([[a,b,b+n],[a,b+n,a+n]])
  if cap:
   for i in range(1,n-1):f.extend([[0,i+1,i],[(len(rz)-1)*n,(len(rz)-1)*n+i,(len(rz)-1)*n+i+1]])
  self.part(v,f,m)
 def box(self,c,s,m='ivory',yaw=0):
  v=[]
  for z in [-1,1]:
   for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]:
    x*=s[0]/2;y*=s[1]/2;v.append([c[0]+x*math.cos(yaw)-y*math.sin(yaw),c[1]+x*math.sin(yaw)+y*math.cos(yaw),c[2]+z*s[2]/2])
  self.part(v,[[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]],m)
 def beam(self,a,b,w,m='gold',n=8):
  a=np.array(a,float);b=np.array(b,float);d=b-a;d/=np.linalg.norm(d);u=np.cross(d,[0,0,1] if abs(d[2])<.95 else [0,1,0]);u/=np.linalg.norm(u);v=np.cross(d,u)
  pts=[(p+(u*math.cos(t)+v*math.sin(t))*w/2).tolist() for p in [a,b] for t in np.arange(n)*TAU/n];f=[]
  for i in range(n):j=(i+1)%n;f.extend([[i,j,j+n],[i,j+n,i+n]])
  for i in range(1,n-1):f.extend([[0,i+1,i],[n,n+i,n+i+1]])
  self.part(pts,f,m)
 def curve(self,pts,w,m='gold',n=8):
  for a,b in zip(pts[:-1],pts[1:]):self.beam(a,b,w,m,n)
 def orbit(self,r,z,w=.15,m='magic',c=(0,0),n=192):
  pts=[(c[0]+r*math.cos(a),c[1]+r*math.sin(a),z) for a in np.linspace(0,TAU,n+1)];self.curve(pts,w,m,6)
 def arch(self,x,y,z,width,height,depth,m='ivory',yaw=0,fill=False):
  # Lancet arch with shoulders and a curved pointed apex, no jagged triangular portal.
  half=width/2;shoulder=height*.57
  line=[(-half,0),(-half,shoulder)]+[(-half*(1-t*t),shoulder+(height-shoulder)*t) for t in np.linspace(0,1,13)[1:]]+[(half*(1-t*t),shoulder+(height-shoulder)*t) for t in np.linspace(1,0,13)[1:]]+[(half,0)]
  def xyz(u,v):return [x+u*math.cos(yaw),y+u*math.sin(yaw),z+v]
  pts=[xyz(u,v) for u,v in line]
  if fill:self.part(pts,[[0,i+1,i] for i in range(1,len(pts)-1)],m)
  else:self.curve(pts,depth,m,8)
 def export(self,name):
  v=np.array(self.v,float);f=np.array(self.f,int);m=np.array(self.m);ns=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]);ar=np.linalg.norm(ns,axis=1);ok=ar>1e-9;f=f[ok];m=m[ok];ns=ns[ok]/ar[ok,None]
  assert np.isfinite(v).all()
  with (O/(name+'.obj')).open('w') as out:
   out.write('o '+name+'\n')
   for x,y,z in v:out.write('v %.6f %.6f %.6f\n'%(x*100,-y*100,z*100))
   for q,n in zip(f,ns):
    axes=[j for j in range(3) if j!=np.argmax(abs(n))]
    for u,w in v[q][:,axes]/3:out.write('vt %.6f %.6f\n'%(u,w))
   for x,y,z in ns:out.write('vn %.6f %.6f %.6f\n'%(x,-y,z))
   for mat in sorted(set(m)):
    out.write('usemtl '+mat+'\n')
    for i in np.flatnonzero(m==mat):out.write('f '+' '.join('%d/%d/%d'%(f[i,j]+1,i*3+j+1,i+1) for j in [2,1,0])+'\n')
  return {'name':name,'vertices':len(v),'triangles':len(f),'bounds_m':[v.min(axis=0).tolist(),v.max(axis=0).tolist()],'materials':sorted(set(m.tolist()))}

t=Mesh()
# A deeply founded, layered octagonal podium with broad occupied floors.
t.profile([(44,-16),(44,0),(45,.5),(45,1.2),(43,2),(43,5.7),(42.6,6),(42.6,7.7),(42,8)],'foundation',64)
t.profile([(29,8),(29,12),(27.5,13),(27.5,34),(26,39),(21,43),(20,66),(18.2,92),(16.2,119),(14.4,139)],'ivory',16,phase=math.pi/16)
for z,r in [(8,30),(13,28.3),(34,28),(42,22),(65,20.8),(89,19.3),(115,17.3),(137,15.3)]:
 t.profile([(r-.5,z-1),(r+.35,z-.45),(r+.65,z),(r+.65,z+.55),(r,z+1.2),(r-.5,z+1.45)],'trim',64)
 t.profile([(r+.68,z+.12),(r+.7,z+.32)],'gold',64)
# Long flowing ribs and four flying buttresses connect the building rather than random spires.
for i in range(8):
 a=(i+.5)*TAU/8;u=np.array([math.cos(a),math.sin(a)])
 t.curve([[*(u*r),z] for r,z in [(28,10),(28.6,32),(23,44),(21,64),(19.5,88),(17.3,114),(15,139)]],.85,'trim')
 t.curve([[*(u*r),z] for r,z in [(29,13),(29,32),(23.5,44),(21.5,64),(20,88),(17.8,114),(15.5,139)]],.18,'gold')
 if i%2==0:
  c=tuple(u*34)
  t.profile([(3.7,8),(3.7,11),(3.1,12),(3.1,41),(2.5,44),(2.4,55),(.25,69)],'ivory',12,c)
  t.profile([(2.7,54),(2.4,55),(.12,72)],'roof',12,c)
  pts=[]
  for f in np.linspace(0,1,22):r=34-15*f;z=38+30*f+5*math.sin(math.pi*f);pts.append([*(u*r),z])
  t.curve(pts,1.3,'trim');t.curve([[p[0],p[1],p[2]+.7] for p in pts],.22,'gold')
# Recessed stained-glass windows and mullions in tiers. Eight narrow galleries.
for i in range(16):
 a=(i+1)*TAU/16;n=np.array([math.cos(a),math.sin(a)]);yaw=a+math.pi/2
 for z,r,h,w in [(17,27.05,12,3.4),(47,20.4,12,2.8),(70,18.8,13,2.6),(95,17,13,2.35),(121,15.1,10,2.0)]:
  first=len(t.v)
  c=n*r;t.arch(*c,z,w,h,0,'recess',yaw,True);c=n*(r+.08);t.arch(*c,z+.55,w*.72,h*.86,0,'glass',yaw,True);c=n*(r+.16);t.arch(*c,z,w+.2,h+.2,.25,'trim',yaw)
  t.beam([*c,z+.4],[*c,z+h-.8],.11,'gold',6)
  tangent=np.array([-n[1],n[0]])
  t.beam([*(c-tangent*w*.38),z+h*.48],[*(c+tangent*w*.38),z+h*.48],.13,'gold',6)
  # Follow the actual taper instead of letting a vertical window sink into the shaft.
  for vi in range(first,len(t.v)):
   p=t.v[vi];surface=float(np.interp(p[2],[13,34,39,43,66,92,119,139],[27.5,27.5,26,21,20,18.2,16.2,14.4]))*math.cos(math.pi/16)
   dr=surface-r+.10;p[0]+=n[0]*dr;p[1]+=n[1]*dr
# Observatory with a crown surrounding a suspended luminous heart.
t.profile([(15,139),(18,142),(18,144),(15.2,146)],'trim')
t.profile([(14,146),(14,150),(12.8,153),(10.4,158),(7,164),(2,171)],'roof',64)
for i in range(8):
 a=i*TAU/8;u=np.array([math.cos(a),math.sin(a)])
 t.curve([[*(u*r),z] for r,z in [(17,140),(20,154),(17,168),(8,181),(1.6,188)]],.75,'gold')
 t.profile([(1.8,150),(.08,173)],'trim',12,tuple(u*19))
t.profile([(.15,166),(5.5,175),(4.4,185),(.1,197)],'crystal',8)
t.orbit(28,164,.12);t.orbit(29.2,164,.08,'gold')
for i in range(24):
 a=i*TAU/24;t.beam([27*math.cos(a),27*math.sin(a),164],[30*math.cos(a),30*math.sin(a),164],.12,'magic',6)
# Entrance pavilion, sheltered portal, splayed jambs and rose seal.
t.box((0,-29,15),(17,12,14),'ivory');t.box((0,-35.1,15.5),(11,.4,15),'recess')
for j in range(4):t.arch(0,-35.4-j*.38,8,10+j*.9,19+j*.85,.65 if j<3 else .9,'trim' if j%2==0 else 'gold')
t.arch(0,-37,8.1,8.9,17.5,0,'door',0,True)
t.beam((0,-37.08,8.2),(0,-37.08,24.8),.16,'gold')
for x in [-3,-1.5,1.5,3]:t.beam((x,-37.1,9),(x,-37.1,22.5-abs(x)),.08,'gold')
for x in [-7.8,7.8]:
 t.profile([(1.3,8),(1.3,9),(1,10),(1,27),(1.4,28),(1.4,29)],'trim',24,(x,-35.3))
 t.profile([(1.5,29),(.12,36)],'roof',12,(x,-35.3))
 t.profile([(.1,34),(.8,36),(.1,38)],'crystal',8,(x,-35.3))
for i in range(40):
 h=(i+1)*.2;y=-62+(i+.5)*.58;t.box((0,y,h/2),(21.5,.61,h),'trim')
# Stair balustrades with a smooth ramp rail and finial lanterns.
for side in [-1,1]:
 x=side*11.4;t.beam((x,-62,1.25),(x,-38.8,9.25),.48,'trim')
 for i in range(13):
  y=-61+i*1.78;z=max(0,(y+62)/.58*.2);t.profile([(.3,z),(.3,z+1.2)],'trim',12,(x,y))
 for y,z in [(-62,0),(-39,8)]:
  t.profile([(.75,z),(.75,z+1.4),(.5,z+2.5)],'trim',16,(x,y));t.profile([(.1,z+2.1),(.65,z+3.2),(.1,z+4.3)],'crystal',8,(x,y))
# Marble courtyard compass and paired lantern colonnades.
t.box((0,-76,-.3),(31,28,.6),'foundation')
t.box((0,-76,-13),(31,28,25.4),'foundation')
# An additional lower processional stair descends to the existing village slope.
for i in range(80):
 z=-16+(i+1)*.2;y=-126+(i+.5)*.45;t.box((0,y,(z-23)/2),(13,.47,z+23),'trim')
for side in [-1,1]:
 t.beam((side*7,-126,-14.8),(side*7,-90,1.2),.4,'trim')
 for i in range(21):
  y=-126+i*1.8;z=-16+i*.8;t.profile([(.25,z),(.25,z+1.2)],'trim',12,(side*7,y))
for x in [-13,13]:
 for y in [-66,-77,-88]:
  t.profile([(.8,0),(.8,.8),(.5,1),(.5,4.8),(.9,5.1)],'trim',16,(x,y));t.profile([(.1,5.1),(.7,6.1),(.1,7.3)],'crystal',8,(x,y))
assets=[t.export('SM_ElRuhnSky_GrandTower')]
# Five individually shaped standing levitation megaliths; broad chipped facets, no needle pinch.
for k in range(5):
 rng=np.random.default_rng(901+k);m=Mesh();n=10;rad=rng.uniform(.84,1.13,n);ph=rng.uniform(-.08,.08,n);v=[]
 for j,(r,z) in enumerate([(7,-95),(16,-80),(23,-46),(22,8),(18,55),(11,78),(4,88)]):
  for i in range(n):a=TAU*i/n+ph[i];v.append([r*rad[i]*math.cos(a)+2*math.sin(j*.7+k),r*rad[i]*math.sin(a),z+(rng.uniform(-5,5) if j not in [0,6] else 0)])
 f=[]
 for j in range(6):
  for i in range(n):a=j*n+i;b=j*n+(i+1)%n;f.extend([[a,b,b+n],[a,b+n,a+n]])
 for i in range(1,n-1):f.extend([[0,i+1,i],[60,60+i,60+i+1]])
 m.part(v,f,'rock')
 for j in range(5):
  a=j*TAU/5+k*.4;r=23;pts=[[r*math.cos(a+off),r*math.sin(a+off),z] for off,z in [(0,-65),(.03,-32),(-.04,-10),(.05,16),(.03,48),(.1,66)]];m.curve(pts,.38,'magic',6)
 m.profile([(25,-6),(25.6,-5),(25.6,-3),(25,-2)],'gold',10,phase=.1)
 m.profile([(23,24),(24,25),(24,26),(23,27)],'gold',10,phase=.1)
 assets.append(m.export('SM_ElRuhnSky_AnchorStone_%02d'%(k+1)))
# Island circle stays annular: glyphs and five support nodes, no luminous filled disk.
ring=Mesh()
for r,w in [(795,.45),(801,.17),(858,.22),(868,.45)]:ring.orbit(r,0,w,n=512)
for i in range(90):
 a=i*TAU/90;r0=802 if i%3 else 795;r1=812 if i%3 else 818;ring.beam((r0*math.cos(a),r0*math.sin(a),0),(r1*math.cos(a),r1*math.sin(a),0),.22,'magic',6)
for i in range(5):
 a=-math.pi/2+i*TAU/5;c=(868*math.cos(a),868*math.sin(a));ring.orbit(66,0,.35,c=c);ring.orbit(61,0,.14,c=c)
assets.append(ring.export('SM_ElRuhnSky_IslandHalo'))

fontpath=B/'ReferenceAssets/Magic Spell/SpellRunes-Regular.otf';font=ImageFont.truetype(str(fontpath),180)
def glyph_ring(name,sentence,annular=False):
 N=4096;im=Image.new('RGBA',(N,N));d=ImageDraw.Draw(im);c=N/2
 def pt(r,a):return (c+r*math.cos(a),c+r*math.sin(a))
 if annular:radii=[(1935,5),(1920,2),(1792,2),(1775,5)];textR=1850
 else:radii=[(1920,7),(1880,3),(1560,5),(1500,2),(1090,4)];textR=1700
 for r,w in radii:d.ellipse((c-r,c-r,c+r,c+r),outline='white',width=w)
 txt=(sentence+' - ').upper()*(3 if annular else 2)
 for i,ch in enumerate(txt):
  if ch==' ':continue
  a=-math.pi/2+(i+.5)*TAU/len(txt);g=Image.new('RGBA',(260,260));ImageDraw.Draw(g).text((130,130),ch,font=font,anchor='mm',fill='white')
  if not g.getbbox():continue
  g=g.crop(g.getbbox());g.thumbnail((56 if annular else 84,86 if annular else 130),Image.Resampling.LANCZOS);tile=Image.new('RGBA',(220,220));tile.alpha_composite(g,((220-g.width)//2,(220-g.height)//2));tile=tile.rotate(-math.degrees(a)-90,Image.Resampling.BICUBIC);x,y=pt(textR,a);im.alpha_composite(tile,(round(x-110),round(y-110)))
 if not annular:
  for i in range(30):a=i*TAU/30;d.line([pt(1500,a),pt(1090,a)],fill='white',width=4)
  pts=[pt(1020,-math.pi/2+i*TAU/5) for i in range(5)];d.line(pts+[pts[0]],fill='white',width=6)
  for i in range(5):
   x,y=pts[i];d.ellipse((x-95,y-95,x+95,y+95),outline='white',width=5)
  # A rising wind seal instead of a cross, consistent with current four-element grammar.
  for off in [-180,0,180]:d.line([(c-140,c+off+80),(c,c+off-100),(c+140,c+off+80)],fill='white',width=9)
 im.save(O/(name+'.png'))
glyph_ring('T_ElRuhnSky_Levitation','Sustain - Island - Heavenly Ascent')
glyph_ring('T_ElRuhnSky_IslandScript','Sustain - Island - Fivefold Covenant',True)
H=np.load(B/'Saved/AdventureWorldSource/height_valley_v14.npy');cx,cy=125,220;base=float(H[round((cy+600)*.84),round((cx+600)*.84)])
report={'assets':assets,'tower_origin_m':[cx,cy,base],'tower_height_m':197,'anchor_centers_m':[[868*math.cos(-math.pi/2+i*TAU/5),868*math.sin(-math.pi/2+i*TAU/5),-120] for i in range(5)],'island_circle_z_m':-120,'cloud_deck_z_m':-950,'source_design':'Original architecture; Wind pentagon and Effect - Target - Spell grammar from current project documents. Five support nodes do not create a fifth element.','limitations':['Exterior tower and visual levitation system, no tower interiors or gameplay simulation.']}
(O/'source.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
