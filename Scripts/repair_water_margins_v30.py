"""Trim the two agricultural intrusions at the local watershed transition."""
from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates
S=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource');meta=json.loads((S/'world_design_v30.json').read_text());D=dict(np.load(S/'world_reference_v30.npz'));cx=float(D['cx']);cy=float(D['cy']);m=float(D['mpp']);H,W=D['height'].shape
im=np.array(Image.open(S/'T_IV_WorldBiomes30.png').convert('RGBA'));base=np.array(Image.open(S/'T_IV_WorldBiomes28.png').convert('RGBA').resize((im.shape[1],im.shape[0])))
def clear(p):return map_coordinates(D['water_clearance'],[cy-p[:,1]/m,cx-p[:,0]/m],order=1,mode='constant')
keep=[];bad=[]
for q in meta['agricultural_parcels']:
 a=np.array(q['corners'][0]);b=np.array(q['corners'][2]);x,y=np.meshgrid(np.linspace(a[0],b[0],9),np.linspace(a[1],b[1],17));p=np.column_stack([x.ravel(),y.ravel()])
 if clear(p).min()>=80:keep.append(q);continue
 bad.append(q);px0=int((cx-b[0]/m)/W*im.shape[1])-2;px1=int((cx-a[0]/m)/W*im.shape[1])+3;py0=int((cy-b[1]/m)/H*im.shape[0])-2;py1=int((cy-a[1]/m)/H*im.shape[0])+3;im[py0:py1,px0:px1]=base[py0:py1,px0:px1]
 D['farm'][int(cy-b[1]/m):int(cy-a[1]/m)+1,int(cx-b[0]/m):int(cx-a[0]/m)+1]=False
meta['agricultural_parcels']=keep
lanes=[]
for q in meta['farm_lanes']:
 points=np.array(q['points_m']);okay=clear(points)>140;starts=np.where(np.diff(np.r_[False,okay,False].astype(int))==1)[0];ends=np.where(np.diff(np.r_[False,okay,False].astype(int))==-1)[0]
 for a,b in zip(starts,ends):
  if b-a>1:r=dict(q);r['points_m']=points[a:b].tolist();lanes.append(r)
meta['farm_lanes']=lanes;meta['network_summary'].update(farm_parcels=len(keep),cultivated_km2=float(D['farm'].sum()*m*m/1e6),farm_lane_sections=len(lanes),farm_lane_km=float(sum(np.linalg.norm(np.diff(q['points_m'],axis=0),axis=1).sum() for q in lanes)/1000))
# Remove already-exported crop faces belonging to rejected parcels.
path=S/'Civilizations30/SM_Civ30_Roads.obj';lines=path.read_text().splitlines();v=[];out=[];mat='';removed=0
for line in lines:
 if line.startswith('v '):x,y,z=map(float,line.split()[1:]);v.append([x/100,-y/100])
 if line.startswith('usemtl '):mat=line.split()[1]
 if line.startswith('f ') and mat.startswith('crop'):
  ids=[int(q.split('/')[0])-1 for q in line.split()[1:]];p=np.mean([v[i] for i in ids],axis=0)
  if any(q['corners'][0][0]<=p[0]<=q['corners'][2][0] and q['corners'][0][1]<=p[1]<=q['corners'][2][1] for q in bad):removed+=1;continue
 out.append(line)
if removed:
 path.write_text('\n'.join(out)+'\n');manifest=json.loads((S/'Civilizations30/assets.json').read_text())
 for q in manifest:
  if q['name']=='SM_Civ30_Roads':q['triangles']-=removed
 (S/'Civilizations30/assets.json').write_text(json.dumps(manifest,indent=2))
Image.fromarray(im).save(S/'T_IV_WorldBiomes30.png');np.savez_compressed(S/'world_reference_v30.npz',**D);(S/'world_design_v30.json').write_text(json.dumps(meta,indent=2));print({'removed_fields':len(bad),'removed_crop_faces':removed,'farm_parcels':len(keep),'lanes':len(lanes)},flush=True)
