from pathlib import Path
import numpy as np
from scipy.ndimage import map_coordinates
D=np.load(Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource/world_reference_v23.npz'))
HEIGHT=D['height'];CX=float(D['cx']);CY=float(D['cy']);MPP=float(D['mpp'])
def global_height(x,y):
 return map_coordinates(HEIGHT,[(CY-y/MPP),(-x/MPP+CX)],order=1,mode='constant',cval=-20600.)
