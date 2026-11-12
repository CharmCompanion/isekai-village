import numpy as np,json
from pathlib import Path
from scipy.spatial import cKDTree
from shapely.geometry import LineString
P=json.loads(Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/World/Gosain55/mine_road_profile.json').read_text());XY=np.array(P['xy']);Z=np.array(P['z']);LINE=LineString(XY);A=XY[:-1];V=np.diff(XY,axis=0);L2=(V*V).sum(axis=1);TREE=cKDTree(A+V*.5)
def sample(p):
 p=np.asarray(p).reshape(-1,2);_,ix=TREE.query(p,k=4);v=V[ix];a=A[ix];t=np.clip(((p[:,None]-a)*v).sum(axis=2)/L2[ix],0,1);d=np.linalg.norm(p[:,None]-(a+v*t[:,:,None]),axis=2);j=d.argmin(axis=1);i=np.arange(len(p));edge=ix[i,j];return d[i,j],Z[edge]+t[i,j]*(Z[edge+1]-Z[edge])
def apply(v):
 out=v.copy();lo=XY.min(axis=0)-30;hi=XY.max(axis=0)+30;use=np.flatnonzero(((v[:,:2]>=lo)&(v[:,:2]<=hi)).all(axis=1));d,z=sample(v[use,:2]);w=np.clip((25-d)/13,0,1);w=w*w*(3-2*w);out[use,2]=v[use,2]*(1-w)+z*w;return out
