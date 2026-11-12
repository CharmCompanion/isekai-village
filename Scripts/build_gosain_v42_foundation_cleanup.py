"""Remove only retired stock-house pad boxes in the replacement district."""
import json,numpy as np
from pathlib import Path
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain42';d=json.loads((O/'district.json').read_text())
area=unary_union([Polygon(p) for p in d['blocks']]).buffer(8)
(O/'removal_boundary.json').write_text(json.dumps([list(p.exterior.coords) for p in (list(area.geoms) if hasattr(area,'geoms') else [area])]))
result=[]
for old in ['SM_Gosain37_HouseFootings_Relief40','SM_Gosain39_InfillFootings_Relief40']:
    lines=(B/'ArtSource/World/Gosain40'/(old+'.obj')).read_text().splitlines(True)
    v=np.array([[float(c) for c in l.split()[1:4]] for l in lines if l.startswith('v ')])/100
    assert len(v)%8==0
    centers=v.reshape(-1,8,3).mean(axis=1);centers[:,1]*=-1
    remove={i for i,p in enumerate(centers) if area.covers(Point(p[:2]))}
    name=old+'_OutsideDistrict42';count=0
    with (O/(name+'.obj')).open('w') as out:
        for line in lines:
            if line.startswith('f '):
                ids=[(int(t.split('/')[0])-1)//8 for t in line.split()[1:]]
                assert len(set(ids))==1
                if ids[0] in remove:count+=1;continue
            out.write(line)
    result.append({'old_name':old,'name':name,'removed_boxes':len(remove),'removed_faces':count})
(O/'foundation_cleanup.json').write_text(json.dumps(result,indent=2));print(result)
