from pathlib import Path
import numpy as np
from PIL import Image
S=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource')
old=np.fromfile(S/'IV_Adventure_Farm_v02.r16',dtype='<u2').reshape(1009,1009)
H=(old.astype(float)-32768)/64
X,Y=np.meshgrid(np.linspace(-600,600,1009),np.linspace(-600,600,1009))
r=np.sqrt(((X+349)/8)**2+((Y-263)/11)**2)
def smooth(a,b,v):
    t=np.clip((v-a)/(b-a),0,1);return t*t*(3-2*t)
bed=77.5+1.9*smooth(.55,1.05,r)
weight=1-smooth(1.05,1.65,r)
H=H*(1-weight)+bed*weight
raw=np.rint(32768+H*64).astype('<u2')
assert np.array_equal(raw[r>=1.65],old[r>=1.65])
raw.tofile(S/'IV_Adventure_Waterfall_v03.r16')
np.save(S/'height_waterfall_v03.npy',H)
Image.fromarray(np.stack([raw>>8,raw&255,np.zeros_like(raw),np.full_like(raw,255)],-1).astype('uint8')).save(S/'T_IV_WaterfallHeight_RG.png')
print('Changed terrain samples:',int(np.count_nonzero(raw!=old)),'; all changes confined to northwest basin')
