import numpy as np,json
from scipy.interpolate import PchipInterpolator
from scipy.ndimage import gaussian_filter1d
from pathlib import Path
import gosain51_kingdom as k
import gosain55_right_landscape as land
from gosain_surface_sampler import Surface
O=Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/World/Gosain55')
g=np.array([k.CENTERS[1],k.CENTERS[1]+[-500,800],[14000,41400],[14600,41600],[15200,41650],[15600,42200],land.MINE]);t=np.r_[0,np.cumsum(np.linalg.norm(np.diff(g,axis=0),axis=1))];p=PchipInterpolator(t,g,axis=0)(np.linspace(0,t[-1],int(t[-1]/10)));s=Surface(O/'graded_surface.npz');raw=s.ground(p);ds=np.linalg.norm(np.diff(p,axis=0),axis=1);z=gaussian_filter1d(raw,12);z[0]=raw[0];z[-1]=raw[-1]
for _ in range(12):
 z[0]=raw[0]
 for i in range(1,len(z)):z[i]=np.clip(z[i],z[i-1]-.12*ds[i-1],z[i-1]+.12*ds[i-1])
 z[-1]=raw[-1]
 for i in range(len(z)-2,-1,-1):z[i]=np.clip(z[i],z[i+1]-.12*ds[i],z[i+1]+.12*ds[i])
assert np.max(abs(np.diff(z))/ds)<.120001
(O/'mine_road_profile.json').write_text(json.dumps({'xy':p.tolist(),'z':z.tolist(),'raw_z':raw.tolist(),'max_grade':float(np.max(abs(np.diff(z))/ds))}));print('profile ready',len(p))
