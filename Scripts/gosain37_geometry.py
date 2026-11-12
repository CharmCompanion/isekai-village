"""Local, deterministic geometry helpers. Never executes an earlier world builder."""
from pathlib import Path
import json, numpy as np
from scipy.ndimage import label, map_coordinates
from scipy.spatial import cKDTree
ROOT=Path('D:/DEVELOPMENT/Games/IsekaiVillage')
SRC=ROOT/'Saved/AdventureWorldSource'
OUT=ROOT/'ArtSource/World/Gosain37'; OUT.mkdir(parents=True,exist_ok=True)
D=np.load(SRC/'world_reference_v30.npz')
CX,CY,MPP=float(D['cx']),float(D['cy']),float(D['mpp'])
COMP,_=label(~D['water'])
CAP=np.array([22173.92809189915,41624.713312447166])
MON=np.array([14333.928091899152,39144.713312447166])
TRI=np.load(SRC/'civilization_terrain30_full.npz')['tri'].astype(float)
TREE=cKDTree(TRI[:,:,:2].mean(axis=1))
def component(p):
    p=np.asarray(p);x=np.rint(CX-p[...,0]/MPP).astype(int);y=np.rint(CY-p[...,1]/MPP).astype(int)
    return COMP[np.clip(y,0,COMP.shape[0]-1),np.clip(x,0,COMP.shape[1]-1)]
def ground_many(p):
    p=np.asarray(p,float).reshape(-1,2);out=np.full(len(p),np.nan)
    for count in (16,96,384):
        ids=np.where(np.isnan(out))[0]
        if not len(ids):break
        for sub in np.array_split(ids,max(1,len(ids)//3000+1)):
            _,ix=TREE.query(p[sub],k=count);q=TRI[ix];a=q[:,:,0,:2];b=q[:,:,1,:2]-a;c=q[:,:,2,:2]-a;v=p[sub,None,:]-a
            den=b[:,:,0]*c[:,:,1]-b[:,:,1]*c[:,:,0];safe=np.abs(den)>1e-8
            u=np.divide(v[:,:,0]*c[:,:,1]-v[:,:,1]*c[:,:,0],den,out=np.zeros_like(den),where=safe)
            w=np.divide(b[:,:,0]*v[:,:,1]-b[:,:,1]*v[:,:,0],den,out=np.zeros_like(den),where=safe)
            legal=safe&(u>=-1e-6)&(w>=-1e-6)&(u+w<=1.000001);hit=legal.any(axis=1);j=legal.argmax(axis=1);i=np.arange(len(sub))
            zz=q[i,j,0,2]+u[i,j]*(q[i,j,1,2]-q[i,j,0,2])+w[i,j]*(q[i,j,2,2]-q[i,j,0,2]);out[sub[hit]]=zz[hit]
    if np.isnan(out).any():raise ValueError(('No ground',p[np.isnan(out)][:3].tolist()))
    return out
original_ground_many=ground_many
def planned_height(p,base):
    """Three broad occupied levels, with graded approaches, confined to the capital."""
    p=np.asarray(p,float).reshape(-1,2);base=np.asarray(base,float);q=p-CAP
    def ease(t):t=np.clip(t,0,1);return t*t*(3-2*t)
    outer=np.sqrt((q[:,0]/950)**2+(q[:,1]/970)**2)
    blend=1-ease((outer-.77)/.23)
    oldtown=np.sqrt(((q[:,0]+30)/465)**2+((q[:,1]+35)/465)**2)
    middle=1-ease((oldtown-.92)/.16)
    # The sacred plateau follows the irregular precinct, not a circular hill.
    import shapely
    poly=shapely.Polygon(np.array([[-146,-177],[-146,35],[-118,177],[48,195],[151,143],[172,-70],[144,-177]]))
    inside=shapely.contains_xy(poly,q[:,0],q[:,1]);dist=shapely.distance(shapely.points(q),poly)
    upper=np.where(inside,1.,1-ease(dist/65.))
    target=-19638.09765625+1.5+middle*6.0+upper*7.0
    # Keep the nearby natural valleys: no large fill just to force a square pad.
    target=base+np.clip(target-base,-30.,30.)
    return base*(1-blend)+target*blend
def ground_many(p):
    p=np.asarray(p,float).reshape(-1,2)
    return planned_height(p,original_ground_many(p))
def ground(x,y):return float(ground_many([[x,y]])[0])
def field(key,p):
    p=np.asarray(p,float).reshape(-1,2)
    return map_coordinates(D[key],np.array([CY-p[:,1]/MPP,CX-p[:,0]/MPP]),order=1,mode='nearest')

class Mesh:
    def __init__(self):self.v=[];self.f=[];self.mat=[]
    def part(self,v,f,mat):
        n=len(self.v);self.v.extend(np.asarray(v).tolist());self.f.extend((np.asarray(f,int)+n).tolist());self.mat.extend([mat]*len(f))
    def box(self,center,size,mat,yaw=0):
        x,y,z=center;w,d,h=size
        v=np.array([[-w/2,-d/2,0],[w/2,-d/2,0],[w/2,d/2,0],[-w/2,d/2,0],[-w/2,-d/2,h],[w/2,-d/2,h],[w/2,d/2,h],[-w/2,d/2,h]])
        a=np.radians(yaw);u=v[:,0].copy();t=v[:,1].copy();v[:,0]=x+u*np.cos(a)-t*np.sin(a);v[:,1]=y+u*np.sin(a)+t*np.cos(a);v[:,2]+=z
        self.part(v,[[0,2,1],[0,3,2],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7],[4,5,6],[4,6,7]],mat)
    def band(self,points,bottom,top,width,mat,closed=False):
        p=np.asarray(points,float);tan=np.roll(p,-1,axis=0)-np.roll(p,1,axis=0) if closed else np.gradient(p,axis=0)
        tan/=np.maximum(np.linalg.norm(tan,axis=1,keepdims=True),1e-9);s=np.column_stack([-tan[:,1],tan[:,0]])*width/2
        bottom=np.broadcast_to(bottom,(len(p),));top=np.broadcast_to(top,(len(p),))
        v=np.empty((len(p),4,3));v[:,0,:2]=p-s;v[:,1,:2]=p+s;v[:,2,:2]=p+s;v[:,3,:2]=p-s;v[:,0:2,2]=bottom[:,None];v[:,2:4,2]=top[:,None]
        f=[]
        for i in range(len(p) if closed else len(p)-1):
            a=i*4;b=((i+1)%len(p))*4
            for k in range(4):j=(k+1)%4;f.extend([[a+k,b+j,b+k],[a+k,a+j,b+j]])
        if not closed:f.extend([[0,2,1],[0,3,2],[len(v)*4-4,len(v)*4-3,len(v)*4-2],[len(v)*4-4,len(v)*4-2,len(v)*4-1]])
        self.part(v.reshape(-1,3),f,mat)
    def write(self,name,origin=(0,0,0)):
        v=np.asarray(self.v,float)-origin;f=np.asarray(self.f,int)
        assert np.isfinite(v).all()
        # Face normals preserve crisp masonry edges; tiled world materials do not depend on these UVs.
        norms=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]);areas=np.linalg.norm(norms,axis=1);valid=areas>1e-8
        f=f[valid];norms=norms[valid]/areas[valid,None];mats=np.asarray(self.mat)[valid]
        with (OUT/(name+'.obj')).open('w') as o:
            o.write('o '+name+'\n')
            for x,y,z in v:o.write(f'v {x*100:.5f} {-y*100:.5f} {z*100:.5f}\n')
            for x,y,z in v:o.write(f'vt {x/4:.6f} {y/4:.6f}\n')
            for x,y,z in norms:o.write(f'vn {x:.6f} {-y:.6f} {z:.6f}\n')
            last=None
            for k,(face,mat) in enumerate(zip(f,mats)):
                if mat!=last:o.write('usemtl '+mat+'\n');last=mat
                o.write('f '+' '.join(f'{i+1}/{i+1}/{k+1}' for i in face[::-1])+'\n')
        return {'name':name,'vertices':len(v),'triangles':len(f),'materials':sorted(set(mats.tolist())),'origin_m':list(origin)}
