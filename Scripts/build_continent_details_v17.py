from pathlib import Path
import numpy as np,json
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource'
env={};src=(B/'Scripts/build_living_continent_v17.py').read_text();exec(src[:src.index('# Painted land-cover')],env);fields=env['fields'];rng=np.random.default_rng(17171)
verts=[];faces=[]
# A level lake surface follows the same irregular shoreline as the carved basin.
verts.append([-1050,-950,-7079.7]);n=160
for a in np.linspace(0,2*np.pi,n,endpoint=False):
 radius=.95*(1+.09*np.sin(3*a)+.05*np.sin(5*a+1));verts.append([-1050+460*radius*np.cos(a),-950+260*radius*np.sin(a),-7079.7])
for i in range(n):faces.append((0,i+1,(i+1)%n+1))
# River surface drops gradually through the valley, with tapering banks.
start=len(verts);ys=np.linspace(-7600,7600,1521)
for y in ys:
 x=-950+170*np.sin((y+950)/630)+85*np.sin((y+950)/270)
 h=-7080+max(y+750,0)*.015-max(-y-1250,0)*.010
 for side in [-1,1]:verts.append([x+side*22,y,h+.3])
for i in range(len(ys)-1):
 k=start+i*2;faces.extend([(k,k+1,k+2),(k+1,k+3,k+2)])
with (S/'SM_IV_ContinentWater_v17.obj').open('w') as f:
 f.write('o SM_IV_ContinentWater_v17\n')
 for x,y,z in verts:f.write(f'v {x*100:.3f} {-y*100:.3f} {z*100:.3f}\n')
 for x,y,z in verts:f.write(f'vt {x/80:.6f} {y/80:.6f}\n')
 f.write('vn 0 0 1\n')
 for face in faces:f.write('f '+' '.join(f'{i+1}/{i+1}/1' for i in reversed(face))+'\n')
rows=[]
for i in range(45):
 a=rng.uniform(0,2*np.pi);r=rng.uniform(.85,1.55)*(1+.08*np.sin(3*a)+.04*np.cos(5*a))
 x=225*r*np.cos(a);y=20+195*r*np.sin(a);z=fields(np.array([x]),np.array([y]))[0][0]
 rows.append([x,y,float(z),float(rng.uniform(4,12)),float(rng.uniform(0,360))])
for cx,cy,wx,wy,height in env['peaks']:
 if np.hypot(cx,cy)<900:continue
 for i in range(14):
  x=cx+rng.normal(0,wx*.29);y=cy+rng.normal(0,wy*.29);z=fields(np.array([x]),np.array([y]))[0][0]
  rows.append([x,y,float(z),float(rng.uniform(18,48)),float(rng.uniform(0,360))])
(S/'continent_cliffs_v17.json').write_text(json.dumps(rows));print(len(rows))
