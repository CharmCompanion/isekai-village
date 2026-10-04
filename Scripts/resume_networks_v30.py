"""Resume routing from the saved terrain/population stage."""
from pathlib import Path
import numpy as np,json,heapq
from PIL import Image,ImageDraw
from scipy.ndimage import label,distance_transform_edt,map_coordinates,gaussian_filter1d
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource';P=B/'Scripts'
globals().update(dict(np.load(S/'networks30_checkpoint.npz')));globals().update(json.loads((S/'networks30_checkpoint.json').read_text()));D=dict(np.load(S/'world_reference_v28.npz'));H,W=h.shape;M=float(D['mpp']);cx=float(D['cx']);cy=float(D['cy']);countries=['YozuanDesert','DivineEmpireofGosain','KelsinFederation','RabaricRepublic','VylfodDominion']
def sample(a,x,y,order=1):return map_coordinates(a,[cy-np.asarray(y)/M,cx-np.asarray(x)/M],order=order,mode='constant',cval=0)
exec(compile('# A* on a conservative'+(P/'prepare_civilized_world_v30.py').read_text().split('# A* on a conservative',1)[1],'route stage','exec'))
