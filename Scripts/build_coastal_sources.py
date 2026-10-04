from pathlib import Path
import numpy as np
from PIL import Image
S=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource');H=np.load(S/'height_layered_v05.npy');M=np.asarray(Image.open(S/'T_IV_Biome_Layered_v05.png')).copy();axis=np.linspace(-600,600,1009);X,Y=np.meshgrid(axis,axis)
def smooth(a,b,v):
    t=np.clip((v-a)/(b-a),0,1);return t*t*(3-2*t)
weight=smooth(340,415,X)*smooth(-460,-340,Y)*(1-smooth(370,490,Y))
offset=24*np.sin(Y/95)+9*np.sin(Y/31+1.7)
out=H.copy();biome=M.copy()
for j in range(1009):
    warped=np.interp(axis+offset[j],axis,H[j]);out[j]=H[j]*(1-weight[j])+warped*weight[j]
    for c in range(4):biome[j,:,c]=np.rint(M[j,:,c]*(1-weight[j])+np.interp(axis+offset[j],axis,M[j,:,c])*weight[j])
raw=np.rint(32768+out*64).astype('<u2');raw.tofile(S/'IV_Adventure_Coastal_v06.r16');np.save(S/'height_coastal_v06.npy',out)
Image.fromarray(np.stack([raw>>8,raw&255,np.zeros_like(raw),np.full_like(raw,255)],-1).astype('uint8')).save(S/'T_IV_CoastalHeight_RG.png');Image.fromarray(biome).save(S/'T_IV_Biome_Coastal_v06.png')
assert np.array_equal(raw[:,axis<=340],np.rint(32768+H[:,axis<=340]*64).astype('<u2'))
print('Eastern coast sculpted into irregular headlands; town, farms and tunnels unchanged.')
