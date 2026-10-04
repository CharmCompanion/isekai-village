"""Bake precise field membership for terrain shading and remove floating crop overlays."""
from pathlib import Path
from PIL import Image,ImageDraw
import json
S=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource');meta=json.loads((S/'world_design_v30.json').read_text());cx=814.1741011487394;cy=638.3089164055896;W=1758;H=1185;M=80;res=4096
im=Image.new('RGB',(res,res));draw=ImageDraw.Draw(im)
for q in meta['agricultural_parcels']:
 a=q['corners'][0];b=q['corners'][2];kind=85 if b[0]-a[0]>200 else 170
 draw.polygon([((cx-x/M)/W*res,(cy-y/M)/H*res) for x,y in q['corners']],fill=(kind,int(q['crop']/5*255),255))
im.save(S/'T_IV_Agriculture30.png')
path=S/'Civilizations30/SM_Civ30_Roads.obj';out=[];mat='';removed=0
for l in path.read_text().splitlines():
 if l.startswith('usemtl '):mat=l.split()[1]
 if mat.startswith('crop') and (l.startswith('f ') or l.startswith('usemtl ')):
  if l.startswith('f '):removed+=1
  continue
 out.append(l)
path.write_text('\n'.join(out)+'\n');man=json.loads((S/'Civilizations30/assets.json').read_text())
for q in man:
 if q['name']=='SM_Civ30_Roads':q['triangles']-=removed;q['materials']=[m for m in q['materials'] if not m.startswith('crop')]
(S/'Civilizations30/assets.json').write_text(json.dumps(man,indent=2));print({'crop_overlay_faces_removed':removed},flush=True)
