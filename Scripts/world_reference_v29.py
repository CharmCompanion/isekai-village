from pathlib import Path
import numpy as np
from scipy.ndimage import map_coordinates,spline_filter
D=np.load(Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource/world_reference_v29.npz'))
HEIGHT=spline_filter(D['height'],order=3);CX=float(D['cx']);CY=float(D['cy']);MPP=float(D['mpp'])
def global_height(x,y):
 return map_coordinates(HEIGHT,[(CY-y/MPP),(-x/MPP+CX)],order=3,prefilter=False,mode='constant',cval=-20600.)
