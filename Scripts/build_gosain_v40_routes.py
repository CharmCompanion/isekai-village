"""Terrain-aware main routes between bridge gates, towns and island ends."""
import gosain37_geometry as g
from pathlib import Path
import numpy as np,json,heapq
from scipy.ndimage import distance_transform_edt
from shapely.geometry import LineString,Polygon
import shapely
B=g.ROOT;O=B/'ArtSource/World/Gosain40';g.OUT=O;D=g.D;COMP=g.COMP;sea=-20600
plan=json.loads((B/'ArtSource/World/Gosain38/whole_island_plan.json').read_text());ends=np.array(plan['bridge_endpoints_m']);axis=(ends[1]-ends[0])/np.linalg.norm(ends[1]-ends[0]);roads=g.Mesh();routes=[]
def ground(p):
    z=g.ground_many(p);return np.where(z>sea,sea+(z-sea)*.30,z)
for ii,component in enumerate([2,1]):
    poly=Polygon(plan['islands'][ii]['wall_boundary_m']).buffer(-65)
    x0,y0,x1,y1=poly.bounds;GX,GY=np.meshgrid(np.arange(x0,x1,40),np.arange(y0,y1,40));valid=shapely.contains_xy(poly,GX,GY)
    dist=distance_transform_edt(valid)*40;yy,xx=np.where(valid);pts=np.c_[GX[yy,xx],GY[yy,xx]];h=ground(pts)-sea
    print('surveyed actual terrain',component,len(pts),flush=True)
    start=ends[ii]+axis*(1 if ii==1 else -1)*100;si=int(np.argmin(np.linalg.norm(pts-start,axis=1)));lookup={(int(y),int(x)):i for i,(y,x) in enumerate(zip(yy,xx))}
    cost=np.full(len(pts),np.inf);prev=np.full(len(pts),-1,int);cost[si]=0;heap=[(0.,si)]
    while heap:
        c,i=heapq.heappop(heap)
        if c!=cost[i]:continue
        for dy,dx in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            j=lookup.get((int(yy[i]+dy),int(xx[i]+dx)))
            if j is None:continue
            length=40*np.hypot(dy,dx);slope=abs(h[j]-h[i])/length;nc=c+length*(1+20*slope*slope+max(0,slope-.12)*500)
            if nc<cost[j]:cost[j]=nc;prev[j]=i;heapq.heappush(heap,(nc,j))
    hub=g.CAP+[100,-910] if ii==0 else g.MON+[0,-700];hi=int(np.argmin(np.linalg.norm(pts-hub,axis=1)));eligible=np.isfinite(cost)&(dist[yy,xx]>250);far=int(np.argmax(np.where(eligible,np.linalg.norm(pts-start,axis=1),-1)))
    for role,ti in [('town',hi),('outer_districts',far)]:
        path=[];i=ti
        while i!=-1:path.append(pts[i]);i=prev[i]
        path=np.array(path[::-1]);assert np.allclose(path[0],pts[si]);path=np.vstack([start,path])
        line=LineString(path).simplify(2);p=np.array([line.interpolate(t).coords[0] for t in np.linspace(0,line.length,int(line.length/8)+1)])
        tangent=np.gradient(p,axis=0);tangent/=np.maximum(np.linalg.norm(tangent,axis=1,keepdims=True),1e-8);side=np.c_[-tangent[:,1],tangent[:,0]];width=18
        vertices=[]
        for offset in [-.5,-.25,0,.25,.5]:
            q=p+side*(width*offset);vertices.append(np.c_[q,ground(q)+.10])
        v=np.stack(vertices,axis=1).reshape(-1,3);faces=[]
        for j in range(len(p)-1):
            for k in range(4):a=j*5+k;b=(j+1)*5+k;faces.extend([[a,b,b+1],[a,b+1,a+1]])
        roads.part(v,faces,'paving');z=ground(p);grade=np.abs(np.diff(z))/np.maximum(np.linalg.norm(np.diff(p,axis=0),axis=1),1e-6)
        routes.append({'island':component,'role':role,'points_m':p.tolist(),'length_m':line.length,'max_grade':float(grade.max()),'p95_grade':float(np.percentile(grade,95))})
mesh=roads.write('SM_Gosain40_MainRoutes',[18000,38000,-20000]);(O/'main_routes.json').write_text(json.dumps({'status':'candidate_requires_grade_and_junction_validation','mesh':mesh,'routes':routes},indent=2));print([(r['island'],r['role'],round(r['length_m']),round(r['max_grade'],3)) for r in routes],flush=True)
