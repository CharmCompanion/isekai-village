"""Build a complete scenic watershed below the playable island."""
from pathlib import Path
import numpy as np,json
from scipy.ndimage import map_coordinates,gaussian_filter
from PIL import Image
S=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource');rng=np.random.default_rng(17029)
def smooth(a,b,v):
 t=np.clip((v-a)/(b-a),0,1);return t*t*(3-2*t)
cache={}
def noise(x,y,k):
 if k not in cache:cache[k]=np.random.default_rng(k+17029).uniform(0,1,(k,k))
 return map_coordinates(cache[k],[(y+8000)/16000*(k-1),(x+8000)/16000*(k-1)],order=3,mode='reflect')
towns=[(650,-760),(-1750,-950),(1800,-2000)]
peaks=[(-410,320,220,270,150),(-140,530,220,230,190),(240,500,220,210,175),(420,150,190,300,115),(-510,0,170,300,100),
 (-1700,1900,570,1100,340),(-2350,2800,700,650,520),(-850,2500,650,470,420),(800,2400,680,650,490),(1700,1700,550,920,360),(2800,2700,770,1200,600),
 (-3000,-2600,540,1100,270),(3700,-600,600,1000,360),(-4700,1200,760,1500,530),(1500,5300,1300,750,540)]
def fields(x,y):
 z=-7120+80*noise(x,y,14)+45*noise(x,y,37)+12*noise(x,y,95)
 relief=np.zeros_like(x)
 for px,py,wx,wy,h in peaks:
  u=(x-px)/wx;v=(y-py)/wy
  relief+=h*np.exp(-(u*u+v*v)*1.3)
 # Valleys divide connected ridges; no high-frequency corrugation.
 erosion=.72+.28*noise(x,y,62)
 z+=relief*erosion+12*(noise(x,y,175)-.5)
 rx=-950+170*np.sin((y+950)/630)+85*np.sin((y+950)/270)
 rd=np.abs(x-rx);la=np.arctan2((y+950)/260,(x+1050)/460)
 lake=np.sqrt(((x+1050)/460)**2+((y+950)/260)**2)/(1+.09*np.sin(3*la)+.05*np.sin(5*la+1))
 water=np.maximum(1-smooth(22,36,rd),1-smooth(.94,1.02,lake))
 wetvalley=np.maximum(np.exp(-(rd/130)**2),1-smooth(.92,1.35,lake))
 wl=-7080+np.maximum(y+750,0)*.015-np.maximum(-y-1250,0)*.010
 wl=np.where(lake<1.3,-7080,wl)
 z=z*(1-wetvalley)+((wl-9*water)*(wetvalley))
 # A broken, irregular extraction basin with broad rock ledges and talus.
 a=np.arctan2(y-20,x);r=np.sqrt((x/225)**2+((y-20)/195)**2)/(1+.08*np.sin(3*a)+.04*np.cos(5*a))
 floor=-7240+13*noise(x,y,175)+8*np.sin(a)*np.minimum(r,1)
 bowl=smooth(.15,1.12,r)
 basin=floor+(z-floor)*bowl
 z=np.where(r<1.12,basin,z)
 z+=9*np.exp(-((r-1.2)/.18)**2)*( .6+.4*np.sin(3*a)**2 )
 # Settlements occupy level terraces; fields and connecting roads read from altitude.
 farm=np.zeros_like(x);road=np.zeros_like(x);town=np.zeros_like(x)
 for tx,ty in towns:
  d=np.hypot(x-tx,y-ty);town=np.maximum(town,1-smooth(95,190,d))
  terrace=-7045 if tx>0 else -7060
  flatten=1-smooth(150,270,d);z=z*(1-flatten)+terrace*flatten
  fx=(x-tx-200);fy=y-ty
  fm=(np.abs(fx)<145)&(np.abs(fy)<180)
  farm=np.where(fm,1,farm)
  z=np.where(fm,z*.15+terrace*.85,z)
  lanes=np.minimum(np.mod(fx+145,55),55-np.mod(fx+145,55))
  farm=np.where(fm&(lanes<3),.3,farm)
 # Country road curves past towns, avoiding the extraction basin and lake.
 roadx=700+500*np.sin((y+750)/1450)+220*np.sin((y+750)/670)
 road=np.maximum(1-smooth(6,10,np.abs(x-roadx)),road)
 for tx,ty in towns:road=np.maximum(road,(1-smooth(5,9,np.abs(y-ty)))*(1-smooth(200,600,np.abs(x-tx))))
 # Large connected woodland belts with small gaps, rather than camouflage spots.
 woodland=.54*noise(x,y,14)+.30*noise(x,y,38)+.16*noise(x,y,95)
 woodland+=.15*smooth(-900,1900,y)+.09*smooth(30,150,relief)
 forest=smooth(.37,.59,woodland)*(1-smooth(280,520,relief))
 forest*=1-np.maximum.reduce([water,town,farm,road,1-smooth(1.05,1.4,r)])
 return z,water,forest,farm,road,relief,r,wl,town

# Painted land-cover atlas includes forest canopy, meadows, scree, fields and shorelines.
axis_tex=np.linspace(-8000,8000,2049);xx,yy=np.meshgrid(axis_tex,axis_tex)
z,water,forest,farm,road,relief,r,wl,town=fields(xx,yy)
gy,gx=np.gradient(z,16000/2048);slope=np.hypot(gx,gy)
fine=noise(xx,yy,601);macro=noise(xx,yy,85)
color=np.empty((*z.shape,3));color[:]=[.20,.38,.085]
color*= (.82+.30*macro+.12*fine)[...,None]
woods=np.stack([.045+.045*fine,.20+.065*fine,.065+.045*fine],-1)
color=color*(1-forest[...,None])+woods*forest[...,None]
Image.fromarray(np.uint8(np.clip(color,0,1)*255)).convert('RGBA').resize((2048,2048),Image.Resampling.LANCZOS).save(S/'T_IV_ContinentFar17.png')
rock=smooth(.40,.90,slope)*.85+smooth(190,420,relief)*.6
rock=np.clip(rock,0,1);stone=np.array([.31,.32,.29])*(.83+.30*fine[...,None])
color=color*(1-rock[...,None])+stone*rock[...,None]
scar=1-smooth(.88,1.28,r);scarstone=np.array([.24,.205,.155])*(.85+.3*fine[...,None])
color=color*(1-scar[...,None])+scarstone*scar[...,None]
fc=np.stack([.32+.12*np.sin(xx/53)**2,.32+.08*np.sin(yy/57)**2,.09+.04*macro],-1)
color=color*(1-farm[...,None])+fc*farm[...,None]
color=color*(1-road[...,None]*.8)+np.array([.46,.35,.18])*road[...,None]*.8
shore=np.clip(water*3,0,1)*(1-water)
color=color*(1-shore[...,None])+np.array([.42,.39,.23])*shore[...,None]
wc=np.stack([.022+fine*.01,.27+fine*.025,.31+fine*.025],-1)
color=color*(1-water[...,None])+wc*water[...,None]
im=Image.fromarray(np.uint8(np.clip(color,0,1)*255));im.save(S/'T_IV_LivingContinent_v17.png')
im.convert('RGBA').resize((2048,2048),Image.Resampling.LANCZOS).save(S/'T_IV_ContinentAtlas17.png')

axis=np.unique(np.r_[np.linspace(-100000,100000,101),np.linspace(-8000,8000,201),np.linspace(-3000,3000,401),np.linspace(-500,500,151)])
X,Y=np.meshgrid(axis,axis);H=fields(X,Y)[0]
far=smooth(6500,9000,np.hypot(X,Y));H=H*(1-far)+(-7170+260*noise(X,Y,14)+70*noise(X,Y,38))*far
H-=np.maximum(np.hypot(X,Y)-12000,0)**2/700000
gy,gx=np.gradient(H,axis,axis);norm=np.stack([-gx,-gy,np.ones_like(H)],-1);norm/=np.linalg.norm(norm,axis=-1,keepdims=True)
name='SM_IV_LivingContinent_v17';n=len(axis)
with (S/(name+'.obj')).open('w') as f:
 f.write('o '+name+'\n')
 for x,y,z in zip(X.flat,Y.flat,H.flat):f.write(f'v {x*100:.3f} {-y*100:.3f} {z*100:.3f}\n')
 for x,y in zip(X.flat,Y.flat):f.write(f'vt {x/16000+.5:.7f} {y/16000+.5:.7f}\n')
 for nx,ny,nz in norm.reshape(-1,3):f.write(f'vn {nx:.6f} {-ny:.6f} {nz:.6f}\n')
 for j in range(n-1):
  for i in range(n-1):
   k=j*n+i+1
   for face in [(k+n,k+1,k),(k+n,k+n+1,k+1)]:f.write('f '+' '.join(f'{v}/{v}/{v}' for v in face)+'\n')

# Native instances provide real canopy silhouettes and rocks in the main valley.
px=rng.uniform(-3200,3200,160000);py=rng.uniform(-2800,3400,160000)
pz,pw,pf,pa,pr,pm,pc,_,pt=fields(px,py)
keep=(rng.random(len(px))<pf*.64)&(pw<.01)&(pa<.01)&(pr<.01)&(pc>1.3)
rows={k:[] for k in ['Oak','OakVar','Pine','Rocks','House','HouseVar']}
for i in np.flatnonzero(keep)[:46000]:
 k='Pine' if pm[i]>90 else ('Oak' if i%2 else 'OakVar')
 rows[k].append([float(px[i]),float(py[i]),float(pz[i]),float(rng.uniform(23,38)),float(rng.uniform(0,360))])
for i in np.flatnonzero((pm>110)&(pw<.01)&(pc>1.1))[::13][:2200]:rows['Rocks'].append([float(px[i]),float(py[i]),float(pz[i]),float(rng.uniform(7,19)),float(rng.uniform(0,360))])
for tx,ty in towns:
 for j in range(-4,5):
  for i in [-2,-1,1,2]:
   x=tx+i*25+rng.uniform(-3,3);y=ty+j*22+rng.uniform(-3,3);h=fields(np.array([x]),np.array([y]))[0][0]
   rows['House' if (i+j)%2 else 'HouseVar'].append([x,y,float(h),float(rng.uniform(9,14)),90 if i<0 else 270])
(S/'living_continent_v17_instances.json').write_text(json.dumps(rows))
(S/'living_continent_v17_report.json').write_text(json.dumps({'vertices':n*n,'instances':{k:len(v) for k,v in rows.items()},'island_changed':False,'crater_width_m':450,'crater_depth_m':170},indent=2))
print({k:len(v) for k,v in rows.items()})
