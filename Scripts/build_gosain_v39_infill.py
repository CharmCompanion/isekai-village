from pathlib import Path
import json
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage')
source=(B/'Scripts/build_gosain_v37.py').read_text()
# Reconstruct the deterministic street reservations without writing any old source assets.
exec(compile(source.split('# A market with actual')[0],str(B/'Scripts/build_gosain_v37.py'),'exec'))
import gosain37_geometry as geom
geom.OUT=B/'ArtSource/World/Gosain39'
pads=Mesh();rows={};before=len(placed)
old=json.loads((B/'ArtSource/World/Gosain37/Gosain37.json').read_text())
for key in ('Oak','Pine','Well','Market','Market2','Cart'):
    for p in old['instances'].get(key,[]):
        pos=np.array(p[:2]);cell=tuple(np.floor(pos/16).astype(int));occupied.setdefault(cell,[]).append((pos,8 if key in ('Oak','Pine') else 5))
for j,y in enumerate(np.arange(-650,480,14)):
    for x in np.arange(-665,625,14):
        p=CAP+[x+(j%2)*7,y]
        if not town_boundary.contains(Point(p)):continue
        # Orient infill along the nearest established street rather than random rotations.
        distances=[LineString(line).distance(Point(p)) for line,w in roadlines];idx=int(np.argmin(distances));line=LineString(roadlines[idx][0]);d=line.project(Point(p));a=np.array(line.interpolate(max(0,d-1)).coords[0]);b=np.array(line.interpolate(min(line.length,d+1)).coords[0]);yaw=np.degrees(np.arctan2(*(b-a)[::-1]))+90
        house(p,yaw)
mesh=pads.write('SM_Gosain39_InfillFootings',ORIGIN)
(geom.OUT/'capital_infill.json').write_text(json.dumps({'instances':rows,'mesh':mesh,'count':len(placed)-before,'status':'source_only'},indent=2))
print('additional houses',len(placed)-before,flush=True)
