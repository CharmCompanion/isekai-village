import numpy as np,json,math,random
from pathlib import Path
from PIL import Image
S=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource');H=np.load(S/'height_refined_v08.npy');M=np.asarray(Image.open(S/'T_IV_Biome_Refined_v08.png'));outside=np.fromfile(S/'IV_FloatingVisibility.raw',dtype='uint8').reshape(1009,1009)>0;r=random.Random(80928);D=json.loads((S/'world_farm_v02.json').read_text());out={}
road=M[...,0]>35
expanded=road.copy()
for dx in range(-10,11,2):
 for dy in range(-10,11,2):
  if dx*dx+dy*dy<=100:expanded|=np.roll(np.roll(road,dx,1),dy,0)
gy,gx=np.gradient(H,1200/1008);slope=np.hypot(gx,gy)
def data(x,y):
 i=round((x+600)*.84);j=round((y+600)*.84);return i,j,float(H[j,i])
def clear(x,y,margin):
 if x*x+y*y<(27+margin)**2:return False
 if 85-margin<x<170+margin and -210-margin<y<-72+margin:return False
 for _,bx,by,rad,*_ in D['buildings']:
  if math.hypot(x-bx,y-by)<rad+margin:return False
 return True
def add(kind,x,y,z,s):out.setdefault(kind,[]).append([round(x,3),round(y,3),round(z,3),round(s,3),round(r.uniform(0,360),2)])
for yy in np.arange(-520,560,9):
 for xx in np.arange(-550,560,9):
  x=xx+r.uniform(-3.7,3.7);y=yy+r.uniform(-3.7,3.7);i,j,z=data(x,y)
  if outside[j,i] or expanded[j,i] or z<20 or z>195 or slope[j,i]>.95:continue
  if -237<x<317 and -247<y<317:continue
  if not clear(x,y,8):continue
  # Dense continuous woodland, openings arise from roads, rock and variable terrain.
  density=.89 if y>-220 else .44
  if r.random()>density:continue
  kind=r.choices(['Oak2','Oak4','LargeOak','Pine','Sapling'],[29,28,8,27 if z>85 else 10,8])[0]
  add(kind,x,y,z,r.uniform(1.1,1.75) if kind!='LargeOak' else r.uniform(.75,1.05))
# Natural clustered undergrowth; avoid construction foundations, routes and crop beds.
for _ in range(100000):
 x=r.uniform(-557,557);y=r.uniform(-535,562);i,j,z=data(x,y)
 if outside[j,i] or road[j,i] or z<20 or z>220 or slope[j,i]>1.1 or not clear(x,y,2):continue
 grid=(-228<x<308 and -238<y<308);woods=not grid and y>-240
 patch=.5+.5*math.sin(x/27+math.sin(y/43))*math.cos(y/32)
 if r.random()>(.46 if woods else .24)*(.35+.65*patch):continue
 if grid:kind=r.choices(['Grass','Flowers','Foxtails'],[85,10,5])[0]
 else:kind=r.choices(['Grass','Fern','Bush','Flowers','Foxtails','Rocks','Branch','Log','Stump'],[43,18,11,7,6,9,3,1.5,1.5])[0]
 if expanded[j,i] and kind in ['Bush','Rocks','Branch','Log','Stump']:continue
 scale=r.uniform(.75,1.55)
 if kind=='Grass':scale=r.uniform(1.0,1.8)
 if kind=='Rocks':scale=r.uniform(.75,2.3)
 add(kind,x,y,z,scale)
# Broken foothill shelves create a transition from canopy into large mountains.
for _ in range(1200):
 x=r.uniform(-530,530);y=r.uniform(-130,555);i,j,z=data(x,y)
 if outside[j,i] or expanded[j,i] or z<65 or z>250 or slope[j,i]<.25 or slope[j,i]>1.5:continue
 if -242<x<322 and -250<y<322:continue
 if not clear(x,y,12):continue
 add('Talus',x,y,z,r.uniform(2,5))
(S/'foliage_refinement_v08.json').write_text(json.dumps(out,separators=(',',':')))
print({k:len(v) for k,v in out.items()})
