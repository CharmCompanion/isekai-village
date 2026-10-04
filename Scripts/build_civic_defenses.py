"""Generate future stone ramparts with road openings; keep them hidden in Village era."""
import json,math
from pathlib import Path
import numpy as np
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource';H=np.load(S/'height_layered_v05.npy')
plan=json.loads((B/'Content/IsekaiVillage/AdventureWorld/Design/SettlementGrid.json').read_text())
def h(x,y):return float(H[round((y+600)*.84),round((x+600)*.84)])
gates=[{'name':'Harbor Gate','xy':[30,-150],'yaw':90,'gap':12},{'name':'Trade Gate','xy':[-216,-13],'yaw':0,'gap':13},{'name':'Mine Gate','xy':[-200,141],'yaw':-9,'gap':12},{'name':'Expedition Gate','xy':[153,300],'yaw':90,'gap':12},{'name':'Royal Expansion Gate','xy':[230,300],'yaw':90,'gap':14},{'name':'Meadow Gate','xy':[297,70],'yaw':0,'gap':12}]
verts=[];faces=[];uv=[]
def box(cx,cy,z,l,w,height,yaw):
    a=math.radians(yaw);f=np.array([math.cos(a),math.sin(a)]);r=np.array([-f[1],f[0]])
    corners=[]
    for dz in (0,height):
        for dx,dy in [(-l/2,-w/2),(l/2,-w/2),(l/2,w/2),(-l/2,w/2)]:
            v=np.array([cx,cy])+f*dx+r*dy;corners.append((v[0],v[1],z+dz))
    for ids in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:
        base=len(verts);verts.extend([corners[i] for i in ids]);uv.extend([(0,0),(l/3,0),(l/3,height/3),(0,height/3)]);faces.extend([(base,base+1,base+2),(base,base+2,base+3)])
boundary=plan['rampart_centerline']
segments=0
for p,q in zip(boundary,boundary[1:]):
    dx=q[0]-p[0];dy=q[1]-p[1];d=math.hypot(dx,dy);n=math.ceil(d/3);yaw=math.degrees(math.atan2(dy,dx))
    for i in range(n):
        t=(i+.5)/n;x=p[0]+dx*t;y=p[1]+dy*t
        if any(math.hypot(x-g['xy'][0],y-g['xy'][1])<g['gap'] for g in gates):continue
        z=h(x,y)-1.0;box(x,y,z,d/n+.12,2.6,5.0,yaw)
        if i%2==0:box(x,y,z+5.0,1.3,2.6,1.15,yaw)
        segments+=1
# Gate flanking towers have a clear open carriageway between them.
for g in gates:
    a=math.radians(g['yaw']);r=np.array([-math.sin(a),math.cos(a)])
    for sign in [-1,1]:
        x,y=np.array(g['xy'])+r*sign*9;z=h(x,y)-.8
        box(x,y,z,5.5,5.5,7,g['yaw'])
        for dx,dy in [(-2,-2),(-2,2),(2,-2),(2,2)]:box(x+dx,y+dy,z+7,1.2,1.2,1.15,0)
lines=['# Future Large Town stone defenses, authored in world centimetres']
lines += [f'v {x*100:.3f} {-y*100:.3f} {z*100:.3f}' for x,y,z in verts]
lines += [f'vt {u:.4f} {v:.4f}' for u,v in uv]
lines += ['f '+' '.join(f'{i+1}/{i+1}' for i in tri) for tri in faces]
(S/'SM_LargeTown_Ramparts.obj').write_text('\n'.join(lines)+'\n')
(S/'civic_defenses.json').write_text(json.dumps({'gates':gates,'wall_sections':segments,'era':'LargeTown'},indent=2))
print('Prepared',segments,'wall sections and',len(gates),'open gates')
