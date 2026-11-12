"""Sample the saved triangulated surface, rather than the analytic approximation."""
import numpy as np
from scipy.spatial import cKDTree
from pathlib import Path
class Surface:
 def __init__(self,path):
  d=np.load(path);self.v=d['vertices'];f=d['triangles'];centers=self.v[f].mean(axis=1);keep=(centers[:,0]>8000)&(centers[:,0]<31000)&(centers[:,1]>27000)&(centers[:,1]<47000)
  self.f=f[keep];self.tree=cKDTree(centers[keep,:2])
 def ground(self,p,k=32):
  p=np.asarray(p,float).reshape(-1,2);out=[]
  for start in range(0,len(p),3000):
   q=p[start:start+3000];_,ids=self.tree.query(q,k=k);t=self.v[self.f[ids]];a=t[:,:,0,:2];b=t[:,:,1,:2]-a;c=t[:,:,2,:2]-a;d=q[:,None,:]-a;den=b[:,:,0]*c[:,:,1]-b[:,:,1]*c[:,:,0];den=np.where(abs(den)<1e-14,np.nan,den)
   u=(d[:,:,0]*c[:,:,1]-d[:,:,1]*c[:,:,0])/den;w=(b[:,:,0]*d[:,:,1]-b[:,:,1]*d[:,:,0])/den;valid=(u>=-1e-7)&(w>=-1e-7)&(u+w<=1+1e-7)
   missing=~valid.any(axis=1)
   if missing.any():
    if k>=4096:
     # Dense local subdivision can put thousands of small-face centroids ahead
     # of a long triangle that actually contains the sample. Search bounds as
     # a final exact fallback instead of treating that as a hole.
     if not hasattr(self,'_bounds'):
      xy=self.v[self.f,:2];self._bounds=(xy.min(axis=1),xy.max(axis=1))
     lower,upper=self._bounds;fallback=[]
     for point in q[missing]:
      use=((point>=lower-1e-7)&(point<=upper+1e-7)).all(axis=1);tt=self.v[self.f[use]]
      aa=tt[:,0,:2];bb=tt[:,1,:2]-aa;cc=tt[:,2,:2]-aa;dd=point-aa;det=bb[:,0]*cc[:,1]-bb[:,1]*cc[:,0];det=np.where(abs(det)<1e-14,np.nan,det)
      uu=(dd[:,0]*cc[:,1]-dd[:,1]*cc[:,0])/det;ww=(bb[:,0]*dd[:,1]-bb[:,1]*dd[:,0])/det;ok=(uu>=-1e-7)&(ww>=-1e-7)&(uu+ww<=1+1e-7)
      if ok.any():
       j=np.flatnonzero(ok)[0];fallback.append(tt[j,0,2]+uu[j]*(tt[j,1,2]-tt[j,0,2])+ww[j]*(tt[j,2,2]-tt[j,0,2]))
      else:
       assert getattr(self,'allow_missing',False),point
       fallback.append(np.nan)
     fallback=np.asarray(fallback)
    else:fallback=self.ground(q[missing],k=min(k*8,4096))
   pick=valid.argmax(axis=1);ix=np.arange(len(q));z=t[:,:,0,2]+u*(t[:,:,1,2]-t[:,:,0,2])+w*(t[:,:,2,2]-t[:,:,0,2]);values=z[ix,pick]
   if missing.any():values[missing]=fallback
   out.extend(values)
  return np.array(out)
