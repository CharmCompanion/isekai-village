"""Original exterior landmark source. No editor mutations; geographic site checks included."""
from pathlib import Path
import json, math, numpy as np
from shapely.geometry import Point
import gosain44_terraces as terrain
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain45';O.mkdir(exist_ok=True)
center=np.array(terrain.PLAN['islands'][1]['civic_center_m'])+np.array([500.,800.])
assert terrain.POLYS[1].contains(Point(center).buffer(130))
base=float(terrain.planned([center],[-20600])[0])
samples=np.array([center+[x,y] for x in [-105,0,105] for y in [-105,0,105]])
assert np.ptp(terrain.planned(samples,np.full(9,-20600)))<.1,'Site must be a level terrace'
V=[];F=[];MAT=[]
def part(v,f,m):
    n=len(V);V.extend(v);F.extend([[j+n for j in q] for q in f]);MAT.extend([m]*len(f))
def profile(rz,m='stone',n=16,c=(0,0),phase=0):
    v=[[c[0]+r*math.cos(a*2*math.pi/n+phase),c[1]+r*math.sin(a*2*math.pi/n+phase),z] for r,z in rz for a in range(n)]
    f=[]
    for j in range(len(rz)-1):
        for i in range(n):
            a=j*n+i;b=j*n+(i+1)%n;f.extend([[a,b,b+n],[a,b+n,a+n]])
    for i in range(1,n-1):f.extend([[0,i+1,i],[(len(rz)-1)*n,(len(rz)-1)*n+i,(len(rz)-1)*n+i+1]])
    part(v,f,m)
def beam(a,b,w,m):
    a=np.array(a);b=np.array(b);d=b-a;d/=np.linalg.norm(d);ref=np.array([0,0,1]) if abs(d[2])<.95 else np.array([0,1,0]);u=np.cross(d,ref);u/=np.linalg.norm(u);v=np.cross(d,u)
    pts=[(p+u*x*w/2+v*y*w/2).tolist() for p in [a,b] for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    part(pts,[[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]],m)
def lancet(angle,r,z,w,h,mat='glass'):
    n=np.array([math.cos(angle),math.sin(angle),0]);t=np.array([-n[1],n[0],0]);c=n*r+np.array([0,0,z])
    shape=[(-w/2,0),(w/2,0),(w/2,h*.73),(w*.31,h*.88),(0,h),(-w*.31,h*.88),(-w/2,h*.73)]
    p=[c+t*x+np.array([0,0,y]) for x,y in shape]
    part([q.tolist() for q in p],[[0,i,i+1] for i in range(1,len(p)-1)],mat)
    for a,b in zip(p,p[1:]+p[:1]):beam(a+n*.24,b+n*.24,.65,'trim')
    beam(c+n*.3,c+n*.3+np.array([0,0,h*.9]),.32,'gold')
    beam(c-t*w/2+np.array([0,0,h*.48])+n*.3,c+t*w/2+np.array([0,0,h*.48])+n*.3,.32,'trim')
# Broad inhabited podium with a continuous tapered central shaft and articulated cornices.
profile([(103,-3),(103,0),(100,2),(100,5),(96,5),(96,8),(91,8),(91,11),(86,11),(86,17)],'foundation',32)
profile([(77,17),(77,48),(72,58),(55,66),(46,77),(44,100),(42,180),(38,246),(32,292),(27,323),(22,346)],'stone')
for z,r in [(18,78),(47,78),(58,73),(76,47),(100,45),(145,44),(190,42),(235,40),(276,35),(306,31),(328,27),(346,23)]:
    profile([(r,z-1.3),(r+2,z-1),(r+2,z+.5),(r+.7,z+1.7),(r,z+2)],'trim')
    profile([(r+2.05,z-.65),(r+2.05,z-.25)],'gold')
# Eight tall buttress towers grow out of podium; taper and attach to the central body.
for i in range(8):
    a=i*math.pi/4;xy=(62*math.cos(a),62*math.sin(a));top=165 if i%2 else 188
    profile([(12,17),(12,55),(10,62),(10,top-38),(8,top-28),(8,top-20),(0.35,top)],'stone',8,xy,math.pi/8)
    for z in [50,90,130,top-28]:profile([(11,z),(11.7,z+.4),(11.7,z+2),(10.5,z+3)],'trim',8,xy,math.pi/8)
    for z in [68,108]:
        beam([xy[0],xy[1],z],[math.cos(a)*41,math.sin(a)*41,z+43],4,'stone')
    profile([(8,top-20),(0.2,top+5)],'gold',8,xy,math.pi/8)
    for j in range(8):
        aa=j*math.pi/4+math.pi/8;n=np.array([math.cos(aa),math.sin(aa)])
        # Satellite windows on outer-facing facets only.
        if np.dot(n,np.array(xy))>0:
            p=np.array(xy)+n*10
            for z in [68,107]:beam([*p,z],[*p,z+19],1.3,'glass')
# Facade lancets face flat planes; grouped fenestration gives believable occupied floors.
for i in range(16):
    a=(i+.5)*math.pi/8
    for z,r,h,w in [(23,75.6,21,9),(83,44.5,13,5),(108,42.7,25,5),(154,41,25,5),(199,38.4,24,4.7),(245,35.1,22,4.2),(284,30.3,17,3.6),(313,26,14,3)]:
        lancet(a,r,z,w,h,'recess')
        if i%2==0 and z>=154:lancet(a,r+.12,z+1,w*.40,h*.82,'glass')
# Crown of stone/gold lancets around a long faceted cyan crystal.
profile([(21,342),(21,352),(17,359)],'trim')
profile([(0.1,348),(11,365),(9,389),(.2,414)],'glass',8)
for i in range(8):
    a=i*math.pi/4;xy=np.array([math.cos(a),math.sin(a)])
    beam([*(xy*20),333],[*(xy*24),365],2.8,'stone')
    beam([*(xy*24),365],[*(xy*6),408],1.5,'gold')
    profile([(3.4,355),(.1,382)],'gold',8,tuple(xy*24))
profile([(1.5,410),(.12,427)],'gold',8)
# Narrow arcane orbit, restrained relative to masonry; not a bulky donut.
for r,z in [(68,367),(71,367)]:
    pts=[[r*math.cos(a),r*math.sin(a),z] for a in np.linspace(0,2*math.pi,129)]
    for a,b in zip(pts[:-1],pts[1:]):beam(a,b,.22,'magic')
for i in range(24):
    a=i*math.pi/12;beam([67*math.cos(a),67*math.sin(a),367],[72*math.cos(a),72*math.sin(a),367],.22,'magic')
# Entrance steps and portal treatment on the south face, attached to podium.
for i in range(17):
    y=-118+i*1.8;beam([-14,y,i],[14,y,i],1.8,'trim')
lancet(-math.pi/2,75.7,18,15,28,'recess')

v=np.array(V);f=np.array(F);m=np.array(MAT);norm=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]);area=np.linalg.norm(norm,axis=1);ok=area>1e-8;f=f[ok];norm=norm[ok]/area[ok,None];m=m[ok]
assert np.isfinite(v).all() and len(f)>0
name='SM_Gosain45_ArcaneTower'
with (O/(name+'.obj')).open('w') as out:
    out.write('o '+name+'\n')
    for x,y,z in v:out.write('v %.5f %.5f %.5f\n'%(x*100,-y*100,z*100))
    for face,n in zip(f,norm):
        axes=[j for j in range(3) if j!=np.argmax(np.abs(n))]
        for u,w in v[face][:,axes]/4:out.write('vt %.5f %.5f\n'%(u,w))
    for x,y,z in norm:out.write('vn %.6f %.6f %.6f\n'%(x,-y,z))
    for material in sorted(set(m)):
        out.write('usemtl '+material+'\n')
        for i in np.flatnonzero(m==material):out.write('f '+' '.join('%d/%d/%d'%(f[i,j]+1,i*3+j+1,i+1) for j in [2,1,0])+'\n')
report={'status':'source_only','name':name,'origin_m':[*center.tolist(),base],'height_m':427,'triangles':len(f),'vertices':len(v),'materials':sorted(set(m.tolist())),'site_relief_m':float(np.ptp(terrain.planned(samples,np.full(9,-20600)))),'limitations':['Exterior landmark first pass; no navigable interiors.','Native review required; surrounding city remains a later stage.']}
(O/'tower.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
