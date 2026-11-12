"""Massive battered curtains with clear wall walks; both Gosain island circuits."""
import gosain37_geometry as g
from gosain43_terraces import planned,PLAN
from shapely.geometry import LineString,Point
import numpy as np,json
O=g.ROOT/'ArtSource/World/Gosain43';g.OUT=O;walls=g.Mesh();bridge=g.Mesh();roads=g.Mesh()
def ground(p):return planned(p,-20600+(g.ground_many(p)+20600)*.3)
def samples(line,step):return np.array([line.interpolate(t).coords[0] for t in np.linspace(0,line.length,max(3,int(line.length/step)+1))])
ends=np.array(PLAN['bridge_endpoints_m']);tower_count=0
def tower(q,z,yaw=0):
    global tower_count
    tower_count+=1;walls.box([*q,z-10],[32,32,80],'stone',yaw);walls.box([*q,z+70],[35,35,1.8],'trim',yaw)
    a=np.radians(yaw);u=np.array([np.cos(a),np.sin(a)]);v=np.array([-u[1],u[0]])
    for side in [-1,1]:
        for axis,perp in [(u,v),(v,u)]:
            c=q+side*axis*16;walls.box([*c,z+71.8],[32,1.6,2.3],'stone',float(np.degrees(np.arctan2(perp[1],perp[0]))))
            for d in [-12,-4,4,12]:walls.box([*(c+perp*d),z+74.1],[4,2.0,2.3],'trim',float(np.degrees(np.arctan2(perp[1],perp[0]))))
for i,island in enumerate(PLAN['islands']):
    boundary=LineString(island['wall_boundary_m']);pieces=boundary.difference(Point(ends[i]).buffer(29))
    for piece in (pieces.geoms if hasattr(pieces,'geoms') else [pieces]):
        p=samples(piece,12);z=ground(p);start=len(walls.v);walls.band(p,z-10,z+54,28,'stone')
        # Battered base 28m across narrows to an 18m-wide crown.
        for j,q in enumerate(p):
            for k in [2,3]:
                ix=start+j*4+k;old=np.array(walls.v[ix][:2]);walls.v[ix][:2]=(q+(old-q)*(18/28)).tolist()
        walls.band(p,z+54,z+55,18.8,'trim')
        tan=np.gradient(p,axis=0);tan/=np.linalg.norm(tan,axis=1,keepdims=True);side=np.c_[-tan[:,1],tan[:,0]]
        for sign in [-1,1]:
            pp=p+side*sign*8.1;walls.band(pp,z+55,z+57.3,1.5,'stone')
            for j in range(0,len(p),2):
                yaw=float(np.degrees(np.arctan2(tan[j,1],tan[j,0])));walls.box([*pp[j],z[j]+57.3],[5,1.9,2.6],'trim',yaw)
        for j in range(8,len(p)-8,20):tower(p[j],float(z[j]),float(np.degrees(np.arctan2(tan[j,1],tan[j,0]))))
length=np.linalg.norm(ends[1]-ends[0]);axis=(ends[1]-ends[0])/length;side=np.array([-axis[1],axis[0]]);yaw=float(np.degrees(np.arctan2(axis[1],axis[0])))
t=np.linspace(0,1,int(length/8)+1);p=ends[0]+t[:,None]*(ends[1]-ends[0]);zz=ground(ends)+3;z=zz[0]*(1-t)+zz[1]*t+6*np.sin(np.pi*t)
bridge.band(p,z-7,z,36,'stone');bridge.band(p,z,z+.25,34,'paving')
for sign in [-1,1]:bridge.band(p+side*sign*17,z,z+2.4,1.6,'trim')
for j in range(2,len(p)-2,12):bridge.box([*p[j],-20620],[20,30,z[j]+20620-7],'stone',yaw);bridge.box([*p[j],z[j]-13],[26,38,6],'trim',yaw)
for i in [0,1]:
    for sign in [-1,1]:tower(ends[i]+side*sign*35,float(zz[i]-3),yaw)
    inner=ends[i]+axis*(1 if i else -1)*140;q=np.linspace(ends[i],inner,40);h=ground(q)+.15;h[:15]=np.linspace(zz[i]+.25,h[14],15);roads.band(q,h-.2,h,34,'paving')
origin=[18000,38000,-20000];meshes=[]
for m,name in [(walls,'SM_Gosain43_CoastalWalls'),(bridge,'SM_Gosain43_ImperialBridge'),(roads,'SM_Gosain43_BridgeApproaches')]:meshes.append(m.write(name,origin))
(O/'defenses.json').write_text(json.dumps({'status':'source_only','meshes':meshes,'wall_base_width_m':28,'wall_crown_width_m':18,'wall_height_to_walk_m':55,'wall_height_to_merlons_m':59.9,'tower_height_m':76.4,'towers':tower_count,'bridge_length_m':length,'bridge_end_heights_m':zz.tolist()},indent=2));print('defenses ready',tower_count,'towers',flush=True)
