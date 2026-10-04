"""Continuous fractured geology, with the exact terrain rim retained."""
import numpy as np,math,json,random
from pathlib import Path
S=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource');H=np.load(S/'height_refined_v08.npy');rng=random.Random(92028);N=256;K=64
# Smooth periodic coherent fields; faults extend across many triangles.
fields=[(rng.uniform(0,math.tau),rng.uniform(-3,3)) for _ in range(12)]
def h(x,y):return float(H[max(0,min(1008,round((y+600)*.84))),max(0,min(1008,round((x+600)*.84)))])
def hash3(i,j,k):
 v=math.sin(i*127.1+j*311.7+k*74.7+918.3)*43758.5453;return (v-math.floor(v))*2-1
def noise3(x,y,z):
 i=math.floor(x);j=math.floor(y);k=math.floor(z);u=x-i;v=y-j;w=z-k
 return sum(hash3(i+dx,j+dy,k+dz)*(u if dx else 1-u)*(v if dy else 1-v)*(w if dz else 1-w) for dx in [0,1] for dy in [0,1] for dz in [0,1])
def shell(a,t):
 den=(abs(math.cos(a))**4+abs(math.sin(a))**4)**.25;outline=(1+.012*math.sin(7*a)+.008*math.sin(13*a))/den
 x=580*math.cos(a)*outline;y=570*math.sin(a)*outline;top=h(x,y+20)
 # The upper seam stays exactly at the existing native Landscape edge.
 envelope=math.sin(math.pi*t)**.7
 macro=.095*math.sin(3*a+2.1*t)+.07*math.sin(5*a-3*t+1.7)+.035*math.sin(9*a+4*t)
 smaller=.018*math.sin(23*a+19*t)+.014*math.sin(37*a-27*t+1)
 faults=0
 for center,lean,width,depth in [(0.5,1.1,.11,.16),(1.9,-.7,.15,.13),(3.1,.8,.10,.20),(4.4,-1.2,.14,.18),(5.55,.5,.09,.12)]:
  d=math.atan2(math.sin(a-center-lean*t),math.cos(a-center-lean*t));faults+=depth*math.exp(-(d/width)**2)*math.sin(math.pi*t)**.6
 fracture=noise3(x/95,y/95,t*870/95)*.18+noise3(x/37,y/37,t*870/37)*.055
 fracture*=min(1,t/.035)*min(1,(1-t)/.08)
 scale=(1-t)**.70*(1+envelope*macro*.5+fracture-faults*.6)
 skewx=-115*t+48*math.sin(t*4.5)*envelope;skewy=65*t+32*math.sin(t*5.4)*envelope
 # Non-parallel bedding avoids the visible horizontal courses of separate blocks.
 z=top*(1-t)**2-870*t+envelope*(44*math.sin(a*3+t*6)+28*math.sin(a*7-t*10)+13*math.sin(a*17+t*15))
 return (x*scale+skewx,y*scale+20+skewy,z)
V=[];F=[]
for j in range(K):
 for i in range(N):
  a=math.tau*i/N;t=j/K
  if j>0:t+=rng.uniform(-.0028,.0028)
  V.append(shell(a,t))
for j in range(K-1):
 for i in range(N):
  a=j*N+i;b=j*N+(i+1)%N;c=a+N;d=b+N
  if (i+j)%2:F.extend([(a,c,d),(a,d,b)])
  else:F.extend([(a,c,b),(b,c,d)])
V.append((-115,85,-905))
for i in range(N):F.append(((K-1)*N+i,len(V)-1,(K-1)*N+(i+1)%N))
with (S/'SM_IV_OrganicUnderside_v09.obj').open('w') as f:
 f.write('o SM_IV_OrganicUnderside_v09\ns off\n')
 for x,y,z in V:f.write(f'v {x*100:.3f} {-y*100:.3f} {z*100:.3f}\n')
 for x,y,z in V:f.write(f'vt {x/20:.5f} {z/20:.5f}\n')
 for face in F:f.write('f '+' '.join(f'{v+1}/{v+1}' for v in reversed(face))+'\n')
# Sparse clustered fracture accents, no concentric placements.
placements=[]
for i in range(104):
 a=rng.uniform(0,math.tau);t=rng.uniform(.04,.36) if i<55 else rng.uniform(.30,.88);x,y,z=shell(a,t)
 placements.append({'loc':[x,y,z],'angle':a,'depth':t,'dims':[rng.uniform(45,110),rng.uniform(45,115),rng.uniform(70,180)],'seed':rng.randrange(100000)})
(S/'organic_underside_v09.json').write_text(json.dumps({'placements':placements,'vertices':len(V),'triangles':len(F),'landscape_unchanged':True},indent=2));print(len(V),'vertices;',len(F),'triangles')
