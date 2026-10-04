"""Continuous world-space slope shading for the distant scenic mainland."""
from pathlib import Path
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image
S=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource')
d=np.load(S/'world_reference_v30.npz')
h=gaussian_filter(d['height'].astype(float),1.0)
grow,gcol=np.gradient(h,float(d['mpp']))
# Reference columns/rows run opposite world X/Y.
n=np.stack([gcol,grow,np.ones_like(h)],axis=-1)
n/=np.linalg.norm(n,axis=-1,keepdims=True)
assert np.isfinite(n).all()
Image.fromarray(np.round((n*.5+.5)*255).clip(0,255).astype('uint8')).save(S/'T_IV_WorldSurface30.png')
