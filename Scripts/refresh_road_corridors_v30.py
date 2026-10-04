from pathlib import Path
import numpy as np,json
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt
S=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource');D=dict(np.load(S/'world_reference_v30.npz'));meta=json.loads((S/'world_design_v30.json').read_text());H,W=D['height'].shape;cx=float(D['cx']);cy=float(D['cy']);m=float(D['mpp']);mask=Image.new('L',(W,H));draw=ImageDraw.Draw(mask)
for q in meta['routes']:draw.line([(round(cx-x/m),round(cy-y/m)) for x,y in q['points_m']],fill=255,width=1)
D['road_clearance']=(distance_transform_edt(np.asarray(mask)==0)*m).astype('float32');np.savez_compressed(S/'world_reference_v30.npz',**D)
