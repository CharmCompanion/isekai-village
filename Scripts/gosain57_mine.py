import json,numpy as np
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain57';O.mkdir(exist_ok=True)
C=np.array([15950.,41900.]);F=np.array([350.,-300.]);F/=np.linalg.norm(F);S=np.array([-F[1],F[0]]);Z=-20295.54547438858

def xy(d,l):return C+np.asarray(d)[...,None]*F+np.asarray(l)[...,None]*S

def local(p):
 q=np.asarray(p)-C;return q@F,q@S

def ease(x):
 t=np.clip(x,0,1);return t*t*(3-2*t)

def floor(d,l=0):return Z+.012*np.asarray(d)-.003*np.asarray(l)

def shape(p,z):
 d,l=local(p);out=np.asarray(z).copy();radius=np.sqrt(((d+5)/40)**2+(l/31)**2);w=1-ease((radius-.75)/.7);out=out*(1-w)+floor(d,l)*w
 # Cut a continuous walkable adit floor into the hillside, covered by a closed rock shell.
 w=(1-ease((abs(l)-5.5)/9))*ease((d-18)/10)*(1-ease((d-96)/16));target=floor(d,0)-.12
 out=out*(1-w)+np.minimum(out,target)*w
 return out
(O/'site_plan.json').write_text(json.dumps({'center':C.tolist(),'forward':F.tolist(),'side':S.tolist(),'yard_floor_z':Z,'portal_d':28,'tunnel_end_d':94,'opening_width_m':10,'opening_height_m':8.5,'yard_extent_m':[80,62]},indent=2))
