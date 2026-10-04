"""Structured terrain variation with protected construction land and road corridors."""
import numpy as np,json,math
from PIL import Image
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource'
H=np.load(S/'height_routes_v04.npy').copy();old=H.copy();N=1009
X,Y=np.meshgrid(np.linspace(-600,600,N),np.linspace(-600,600,N));rng=np.random.default_rng(92726)
def smooth(a,b,v):
    t=np.clip((v-a)/(b-a),0,1);return t*t*(3-2*t)
def noise(n):return np.array(Image.fromarray(rng.random((n,n)).astype('float32')).resize((N,N),Image.Resampling.BICUBIC))-.5
n1,n2,n3,n4=noise(12),noise(28),noise(65),noise(130)
road_data=json.loads((S/'world_farm_v02.json').read_text())
routes=json.loads((S/'mountain_routes_v04.json').read_text())
distance=np.full_like(H,1e6)
all_paths=[r['points'] for r in road_data['routes']]+[r['points'] for r in routes['routes']]+[routes['trade_exit'],routes['mine_apron']]
for path in all_paths:
    for a,b in zip(path,path[1:]):
        ax,ay=a[:2];bx,by=b[:2];t=np.clip(((X-ax)*(bx-ax)+(Y-ay)*(by-ay))/max((bx-ax)**2+(by-ay)**2,.001),0,1)
        distance=np.minimum(distance,np.hypot(X-ax-t*(bx-ax),Y-ay-t*(by-ay)))
town_dist=np.maximum.reduce([-245-X,X-325,-255-Y,Y-325,np.zeros_like(X)])
protect=smooth(0,35,town_dist)*smooth(12,28,distance)
# Existing waterfall and new dungeon pool retain their authored water levels.
for px,py,rad in [(-349,267,29),(219,442,24),(-35,-410,27)]:protect*=smooth(rad,rad+15,np.hypot(X-px,Y-py))
mount=smooth(65,160,H)
# Narrow ridges and erosion channels replace rounded, uniformly smooth peaks.
ridge=(1-np.abs(n2*2))*2-1
gullies=np.maximum(0,.24-np.abs(n3))/.24
delta=(n1*13+n2*8+n3*3+n4*.85)*(1-mount)+(ridge*18+n3*12+n4*4-gullies*4)*mount
# Rock shelves follow elevation bands, softened and broken by low-frequency noise.
terrace=(np.sin((H+n2*6)/4.3)*1.6)*mount
coastal=(1-smooth(9,20,np.abs(H)))*(n2*2.8+n3*.8)
H+=(delta+terrace+coastal)*protect
# Flat civic platform with a gentle grass transition; farming terraces remain exact.
plaza=1-smooth(18,21,np.hypot(X,Y));H=H*(1-plaza)+25*plaza
mask=np.asarray(Image.open(S/'T_IV_Biome_Routes_v04.png')).copy().astype(float)/255
dy,dx=np.gradient(H,1200/1008);slope=np.hypot(dx,dy)
mask[:,:,1]=1-smooth(6,17,H) # continuous beach/sand transition
mask[:,:,2]=np.maximum(smooth(.48,1.18,slope),smooth(70,145,H)*.72)*(1-smooth(-1,7,12-H))
mask[:,:,3]=smooth(205,258,H)*(1-smooth(.6,1.2,slope))
mask[:,:,2]*=1-plaza
raw=np.rint(32768+H*64).astype('<u2');raw.tofile(S/'IV_Adventure_Layered_v05.r16')
Image.fromarray(np.stack([raw>>8,raw&255,np.zeros_like(raw),np.full_like(raw,255)],-1).astype('uint8')).save(S/'T_IV_LayeredHeight_RG.png')
Image.fromarray(np.rint(np.clip(mask,0,1)*255).astype('uint8')).save(S/'T_IV_Biome_Layered_v05.png')
np.save(S/'height_layered_v05.npy',H)
farm=(X>=92)&(X<=164)&(Y>=-203)&(Y<=-85)
assert np.array_equal(raw[farm],np.rint(32768+old[farm]*64).astype('<u2'))
# Grid remains level/unchanged except its protected central plaza.
town=(X>=-220)&(X<=300)&(Y>=-230)&(Y<=300)&(np.hypot(X,Y)>21)
assert np.array_equal(raw[town],np.rint(32768+old[town]*64).astype('<u2'))
np.save(S/'terrain_variation_delta.npy',H-old)
(S/'layered_terrain_validation.json').write_text(json.dumps({'farm_unchanged':True,'buildable_grid_unchanged':True,'height_change_min_m':float((H-old).min()),'height_change_max_m':float((H-old).max()),'road_buffer_m':12,'modified_samples':int(np.count_nonzero(raw!=np.rint(32768+old*64).astype('<u2')))},indent=2))
print('Layered terrain sources prepared; farm and buildable grid unchanged.')
