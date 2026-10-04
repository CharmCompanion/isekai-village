from pathlib import Path
import numpy as np, math,random,json
S=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource');H=np.load(S/'height_dish_peak_v11.npy');rng=random.Random(291209);rows=[]
def h(x,y):return float(H[round((y+600)*.84),round((x+600)*.84)])
def radius(x,y):
 a=math.atan2((y-20)/570,x/580);return ((abs(x/580)**4+abs((y-20)/570)**4)**.25)/(1+.012*math.sin(7*a)+.008*math.sin(13*a))
centres=[(-525,-170),(-535,120),(-488,-395),(-155,-509),(75,-510),(423,-420),(535,-230),(532,15),(500,205)]
for kind,count,lo,hi in [('Grass',3400,1.3,2.5),('Flowers',650,.8,1.4),('Bush',125,.6,1.4),('Rocks',75,.65,1.4),('Talus',18,.35,.65)]:
 made=0
 for attempt in range(count*150):
  if made>=count:break
  if kind=='Grass':x=rng.uniform(-580,580);y=rng.uniform(-535,270)
  else:
   cx,cy=rng.choice(centres);x=rng.gauss(cx,24);y=rng.gauss(cy,24)
  if abs(x)>580 or y>285 or y< -545:continue
  r=radius(x,y)
  if not .862<r<.984:continue
  # Keep all water, the dock approach and cliff lip itself clear.
  if ((x+285)/225)**2+((y+373)/132)**2<1.1:continue
  if y< -415 and abs(x-275)<42:continue
  if y< -465 and abs(x+280)<42:continue
  z=h(x,y);sx=(h(x+2,y)-h(x-2,y))/4;sy=(h(x,y+2)-h(x,y-2))/4
  if z<20 or math.hypot(sx,sy)>.65:continue
  rows.append({'kind':kind,'pos':[x,y,z],'scale':rng.uniform(lo,hi),'yaw':rng.uniform(0,360),'slope':[sx,sy]});made+=1
 print(kind,made)
(S/'rim_ecology_v12.json').write_text(json.dumps(rows))
