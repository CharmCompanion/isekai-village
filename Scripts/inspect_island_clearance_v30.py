from pathlib import Path
import numpy as np,json
from PIL import Image
from scipy.ndimage import distance_transform_edt,label
S=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource');D=np.load(S/'world_reference_v29.npz');meta=json.loads((S/'world_design_v29.json').read_text());F=Path(meta['source_folder']);shape=D['height'].shape
land=np.logical_or.reduce([np.array(Image.open(F/(n+'.png')).convert('RGB').resize(shape[::-1])).max(2)>35 for n in ['BiomeDrt','BiomePln','BiomeFst','BiomeJgl','BiomeMtn','BiomeIce']]);c,n=label(land);clear=distance_transform_edt(land)*80
for q in meta['settlements'][-3:]:
 x,y=q['pixel'];mask=c==c[y,x];print(q['name'],q['pixel'],'maxclear',clear[mask].max(),'current',clear[y,x], 'mountain',D['mountain'][y,x])
