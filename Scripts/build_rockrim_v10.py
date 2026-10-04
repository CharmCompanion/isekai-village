import numpy as np,math,json
from pathlib import Path
from PIL import Image
S=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource');H=np.load(S/'height_refined_v08.npy');old=H.copy();X,Y=np.meshgrid(np.linspace(-600,600,1009),np.linspace(-600,600,1009));a=np.arctan2((Y-20)/570,X/580);limit=1+.012*np.sin(a*7)+.008*np.sin(a*13);r=(np.abs(X/580)**4+np.abs((Y-20)/570)**4)**.25/limit

def smooth(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
# Broad footslope with a narrow, steep inner scarp. No level shelf around the edge.
base=np.exp(-((r-.948)/.061)**2)*(10+6*np.sin(a*4+.7)**2)
scarp=smooth(.918,.932,r)*(1-smooth(.962,1.012,r))*(31+14*np.sin(a*3+.8)**2+8*np.sin(a*11)**2)
# Retain the authored airship gangway and waterfall channel.
dock=(1-smooth(15,29,np.abs(X-275)))*(1-smooth(-465,-440,Y))
riverx=-285+18*np.sin((Y+355)/55);water=(1-smooth(10,20,np.abs(X-riverx)))*(1-smooth(-490,-470,Y))
front=(1-smooth(-330,-260,Y))*(1-smooth(370,480,np.abs(X)))
change=(base*(1-.65*front)+scarp*(1-.73*front))*(1-dock)*(1-water)
protected=(X>=-220)&(X<=300)&(Y>=-230)&(Y<=300);change=np.where(protected,0,change);change=np.where(r<.84,0,change);H+=change
# Join the eastern mountain shoulder into the outer crest instead of leaving a flat trench.
east=smooth(420,470,X)*smooth(-265,-145,Y)*(1-smooth(440,535,Y))
shoulder=57+49*np.exp(-((Y-95)/230)**2)+16*np.sin(Y/77+.4)**2-.4*(X-440)
H=H*(1-east)+np.maximum(H,shoulder+base+scarp)*east
change=H-old
raw=np.rint(32768+H*64).astype('<u2');raw.tofile(S/'IV_RockRim_v10.r16');np.save(S/'height_rockrim_v10.npy',H);Image.fromarray(np.stack([raw>>8,raw&255,np.zeros_like(raw),np.full_like(raw,255)],-1).astype('uint8')).save(S/'T_IV_RockRimHeight_RG.png')
M=np.asarray(Image.open(S/'T_IV_Biome_Refined_v08.png')).copy();gy,gx=np.gradient(H,1200/1008);slope=np.hypot(gx,gy);rimpaint=smooth(3,12,change)*smooth(.4,1.3,slope);M[...,2]=np.maximum(M[...,2],rimpaint*255).astype('uint8');M[...,0]=np.where(change>8,0,M[...,0]);Image.fromarray(M).save(S/'T_IV_Biome_RockRim_v10.png')
assert np.array_equal(H[protected],old[protected]);(S/'rockrim_v10.json').write_text(json.dumps({'protected_samples':int(protected.sum()),'max_rim_raise_m':float(change.max()),'dock_and_waterfall_retained':True},indent=2));print('Raised continuous irregular natural rim; protected village untouched.')
