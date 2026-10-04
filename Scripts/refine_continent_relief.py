from pathlib import Path
import numpy as np
from PIL import Image
S=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource');rng=np.random.default_rng(2874);n=385;a=np.linspace(-35000,35000,n);X,Y=np.meshgrid(a,a)
def noise(k):
 im=Image.fromarray(rng.uniform(0,1,(k,k)).astype('float32'));return np.asarray(im.resize((n,n),Image.Resampling.BICUBIC))
f=noise(11)*.48+noise(25)*.28+noise(55)*.15+noise(119)*.065+noise(231)*.025
ridged=1-np.abs(2*f-1)
spine=1-np.abs(np.sin(X/7300+np.sin(Y/8400)*1.3+noise(37)*.7))
mount=1550*spine**2*(.4+.6*noise(13))+1250*(ridged-.55).clip(0)**1.2+270*noise(91)+80*noise(231)
rx=3500+4200*np.sin(Y/8000)+1600*np.sin(Y/3100);valley=np.exp(-((X-rx)/1450)**2);H=-7400+mount*(1-valley*.95)
with (S/'SM_IV_DistantContinent.obj').open('w') as f:
 f.write('o SM_IV_DistantContinent\n')
 for x,y,z in zip(X.flat,Y.flat,H.flat):f.write(f'v {x*100:.2f} {-y*100:.2f} {z*100:.2f}\n')
 for x,y in zip(X.flat,Y.flat):f.write(f'vt {x/70000+.5:.5f} {y/70000+.5:.5f}\n')
 for j in range(n-1):
  for i in range(n-1):
   k=j*n+i+1
   for face in [(k+n,k+1,k),(k+n,k+n+1,k+1)]:f.write('f '+' '.join(f'{q}/{q}' for q in face)+'\n')
print('Mainland: continuous eroded ridges and forested river valley,',round(float(H.max()+7400)),'m relief')
