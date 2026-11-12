"""Remove only the obsolete ribbon crossing beneath the new bridge."""
from pathlib import Path
import numpy as np,json
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain38'
src=B/'ArtSource/World/Gosain37/SM_Civ36_Roads_OutsideGosain37.obj'
d=np.load(B/'Saved/AdventureWorldSource/world_reference_v30.npz');v=[];removed=0
for line in src.open():
    if line.startswith('v '):
        x,y,z=map(float,line.split()[1:]);v.append([x/100,-y/100,z/100])
v=np.array(v);name='SM_Civ36_Roads_OutsideOldGosainBridge38'
with (O/(name+'.obj')).open('w') as out:
    for line in src.open():
        if line.startswith('f '):
            ix=[int(t.split('/')[0])-1 for t in line.split()[1:]];q=v[ix].mean(0)
            if 19000<q[0]<20500 and 42000<q[1]<43500:
                px=int(round(float(d['cx'])-q[0]/80));py=int(round(float(d['cy'])-q[1]/80))
                if d['height'][py,px]<-20588:removed+=1;continue
        out.write(line)
assert removed>0
(O/'old_bridge_filter.json').write_text(json.dumps({'mesh':name,'removed_faces':removed,'source':str(src)}));print('Removed bridge ribbon faces',removed)
