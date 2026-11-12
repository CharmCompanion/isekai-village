"""Continuous terrain-grounded island curtains and supported inter-island bridge."""
import gosain37_geometry as g
from gosain37_geometry import np,json,ROOT,Mesh,ground_many
from shapely.geometry import Polygon,LineString,Point
O=ROOT/'ArtSource/World/Gosain38';g.OUT=O
plan=json.loads((O/'whole_island_plan.json').read_text())
walls=Mesh();bridge=Mesh();roads=Mesh();ends=np.array(plan['bridge_endpoints_m']);manifest=[]
def samples(line,step):return np.array([line.interpolate(t).coords[0] for t in np.linspace(0,line.length,max(3,int(line.length/step)+1))])
for i,island in enumerate(plan['islands']):
    boundary=LineString(island['wall_boundary_m']);p=samples(boundary,12)
    # Opening aligns with the bridge centerline; gate towers flank this opening.
    gate=Point(ends[i]).buffer(24)
    pieces=boundary.difference(gate)
    for piece in (pieces.geoms if hasattr(pieces,'geoms') else [pieces]):
        q=samples(piece,12);z=ground_many(q)
        walls.band(q,z-8,z+30,8,'stone')
        walls.band(q,z+30,z+31,9,'trim')
        for j in range(0,len(q),2):
            t=q[min(j+1,len(q)-1)]-q[max(0,j-1)];yaw=np.degrees(np.arctan2(t[1],t[0]))
            walls.box([*q[j],z[j]+31],[4,9,2.8],'trim',yaw)
        for j in range(5,len(q)-5,24):
            walls.box([*q[j],z[j]-9],[17,17,46],'stone')
            walls.box([*q[j],z[j]+37],[19,19,1.5],'trim')
    island['wall_samples']=len(p)
# Bridge deck uses gentle crown and exact sampled abutment elevations.
length=np.linalg.norm(ends[1]-ends[0]);t=np.linspace(0,1,int(length/8)+1);p=ends[0]+t[:,None]*(ends[1]-ends[0]);zz=ground_many(ends)+3
z=zz[0]*(1-t)+zz[1]*t+32*np.sin(np.pi*t)
bridge.band(p,z-6,z,32,'stone');bridge.band(p,z,z+.25,30,'paving')
axis=(ends[1]-ends[0])/length;side=np.array([-axis[1],axis[0]]);yaw=np.degrees(np.arctan2(axis[1],axis[0]))
for s in (-1,1):bridge.band(p+side*s*15,z,z+2,1.4,'trim')
for j in range(2,len(p)-2,12):
    q=p[j];bottom=-20620
    bridge.box([*q,bottom],[15,25,z[j]-6-bottom],'stone',yaw)
    bridge.box([*q,z[j]-12],[23,35,6],'trim',yaw)
for i in (0,1):
    for s in (-1,1):
        q=ends[i]+side*s*25
        bridge.box([*q,zz[i]-12],[18,18,57],'stone',yaw)
        bridge.box([*q,zz[i]+45],[20,20,2],'trim',yaw)
# Short abutment ramps reach inside each island; city arteries connect here next.
for i in (0,1):
    inner=ends[i]+axis*(1 if i==1 else -1)*100
    q=np.linspace(ends[i],inner,31);zground=ground_many(q);h=zground+.15;h[:10]=np.maximum(h[:10],np.linspace(zz[i]+.25,h[9],10))
    roads.band(q,h-.2,h,30,'paving')
origin=[18000,38000,-20000]
for mesh,name in [(walls,'SM_Gosain38_CoastalWalls'),(bridge,'SM_Gosain38_ImperialBridge'),(roads,'SM_Gosain38_BridgeApproaches')]:manifest.append(mesh.write(name,origin))
report={'status':'sources_generated_not_applied','meshes':manifest,'bridge_length_m':length,'bridge_end_heights_m':zz.tolist(),'enclosed_area_km2':sum(p['enclosed_area_km2'] for p in plan['islands']),'wall_circuits':2,'gate_openings':2}
(O/'defenses.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
