"""Preserve the inhabited landscape; sculpt its outer sky-island envelope."""
from pathlib import Path
import numpy as np, math, json
from PIL import Image
S=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource')
H=np.load(S/'height_coastal_v06.npy'); old=H.copy(); axis=np.linspace(-600,600,1009);X,Y=np.meshgrid(axis,axis)
def smooth(a,b,v):
 t=np.clip((v-a)/(b-a),0,1);return t*t*(3-2*t)
# Keep every town/grid/farm sample and the three mountain approaches unchanged.
front=1-smooth(-300,-240,Y)
H=H*(1-front)+np.maximum(H,21+2*np.sin(X/90)*np.cos(Y/71))*front
H+=front*(.23*np.sin(X/11+np.cos(Y/19))+.18*np.sin(Y/13)+.12*np.sin((X+Y)/7))
# A modest lake outside the ultimate town boundary, with a grassy shore.
lake=np.sqrt(((X+285)/73)**2+((Y+320)/59)**2)
H=H*(smooth(.82,1.15,lake))+13.5*(1-smooth(.82,1.15,lake))
riverx=-285+18*np.sin((Y+355)/55)
river=(1-smooth(6,11,np.abs(X-riverx)))*(1-smooth(-366,-355,Y))*smooth(-560,-550,Y)
H=H*(1-river)+16.3*river
dock=(1-smooth(10,23,np.abs(X-275)))*smooth(-545,-525,Y)*(1-smooth(-482,-457,Y))
H=H*(1-dock)+23.85*dock
# Right arm complements the existing north/west peaks without invading the grid.
arm=smooth(330,380,X)*(1-smooth(495,540,X))*smooth(-80,60,Y)*(1-smooth(330,400,Y))
ridge=60+95*np.exp(-((X-435)/55)**2)*(0.7+.3*np.sin(Y/49)**2)
H=H*(1-arm)+np.maximum(H,ridge)*arm
protected=(X>=-220)&(X<=300)&(Y>=-230)&(Y<=300)
assert np.array_equal(H[protected],old[protected])
theta=np.arctan2((Y-20)/570,X/580)
outline=(np.abs(X/580)**4+np.abs((Y-20)/570)**4)**.25
limit=1+.012*np.sin(theta*7)+.008*np.sin(theta*13)
outside=outline>limit
raw=np.rint(32768+H*64).astype('<u2');raw.tofile(S/'IV_Floating_v07.r16');np.save(S/'height_floating_v07.npy',H)
Image.fromarray(np.stack([raw>>8,raw&255,np.zeros_like(raw),np.full_like(raw,255)],-1).astype('uint8')).save(S/'T_IV_FloatingHeight_RG.png')
Image.fromarray(np.repeat((outside*255).astype('uint8')[...,None],4,axis=2)).save(S/'T_IV_FloatingVisibility.png')
M=np.asarray(Image.open(S/'T_IV_Biome_Coastal_v06.png')).copy();M[...,1]=0
M[...,0]=np.where(front>.8,0,M[...,0]);M[...,2]=np.maximum(M[...,2]*(1-front),arm*190).astype('uint8')
M[...,1]=(255*(1-smooth(.98,1.10,lake))).astype('uint8')
# Dock approach follows the open front-right meadow.
route=[(-15,-280),(-8,-305),(60,-340),(150,-365),(220,-410),(265,-460),(275,-493)]
distance=np.full_like(H,1e6)
for (ax,ay),(bx,by) in zip(route[:-1],route[1:]):
 t=np.clip(((X-ax)*(bx-ax)+(Y-ay)*(by-ay))/((bx-ax)**2+(by-ay)**2),0,1)
 distance=np.minimum(distance,np.hypot(X-(ax+t*(bx-ax)),Y-(ay+t*(by-ay))))
road=1-smooth(2.8,4.5,distance)
M[...,0]=np.maximum(M[...,0],road*255).astype('uint8')
Image.fromarray(M).save(S/'T_IV_Biome_Floating_v07.png')
def h(x,y):
 return float(H[round((y+600)*.84),round((x+600)*.84)])
def obj(name,verts,faces):
 with (S/(name+'.obj')).open('w') as f:
  f.write('o '+name+'\n')
  for x,y,z in verts:f.write(f'v {x*100:.4f} {-y*100:.4f} {z*100:.4f}\n')
  for x,y,z in verts:f.write(f'vt {x/15:.5f} {z/15:.5f}\n')
  for face in faces:f.write('f '+' '.join(f'{i+1}/{i+1}' for i in reversed(face))+'\n')
N=384;V=[];F=[]
for ring,(scale,depth) in enumerate([(1,0),(1.007,-15),(.94,-85),(.80,-195),(.61,-320),(.36,-455),(.12,-610),(.015,-730)]):
 for i in range(N):
  t=2*math.pi*i/N;den=(abs(math.cos(t))**4+abs(math.sin(t))**4)**.25
  rad=(1+.012*math.sin(7*t)+.008*math.sin(13*t))/den
  x=580*math.cos(t)*rad;y=20+570*math.sin(t)*rad
  # Fluted, asymmetric rock teeth form a sharp mountain underside.
  flutes=.7*math.sin(t*19+ring*.13)+.3*math.sin(t*9+.7)
  s=scale*(1+(0 if ring==0 else .025 if ring==1 else .11)*flutes)
  z=h(x,y)+.25 if ring==0 else min(h(x,y)-15,12)+depth+(12 if ring==1 else 55)*flutes
  V.append((x*s-45*(1-scale),(y-20)*s+20+25*(1-scale),z))
for r in range(7):
 for i in range(N):
  a=r*N+i;b=r*N+(i+1)%N;c=(r+1)*N+i;d=(r+1)*N+(i+1)%N
  F.extend([(a,c,b),(b,c,d)])
V.append((-45,45,-805))
for i in range(N):F.append((7*N+i,len(V)-1,7*N+(i+1)%N))
obj('SM_IV_FloatingUnderside',V,F)
# Water lake follows the terrain basin; ribbon connects to the falling edge.
V=[(-285,-320,18)];F=[]
for i in range(128):
 t=2*math.pi*i/128;V.append((-285+73*.985*math.cos(t),-320+59*.985*math.sin(t),18))
for i in range(128):F.append((0,1+i,1+(i+1)%128))
obj('SM_IV_SkyLake',V,F)
V=[];F=[]
for j,y in enumerate(np.linspace(-363,-544,100)):
 x=-285+18*math.sin((y+355)/55)
 V.extend([(x-6,y,18),(x+6,y,18)])
 if j:F.extend([(2*j-2,2*j,2*j-1),(2*j-1,2*j,2*j+1)])
obj('SM_IV_SkyRiver',V,F)
(S/'floating_island_v07.json').write_text(json.dumps({'lake':[-285,-320,18],'waterfall':[-280,-544,18],'dock':[275,-520,24],'protected_grid_unchanged':True,'native_landscape':True,'outline':'rounded superellipse, irregular rim','underside_depth_m':805},indent=2))
print('Floating island terrain, visibility mask, rock underside and water meshes generated; full town/farm grid unchanged.')
