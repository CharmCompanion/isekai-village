"""Fill the smaller arable gaps at country boundaries and town edges."""
from pathlib import Path
import numpy as np,json
from PIL import Image,ImageDraw
from scipy.ndimage import map_coordinates
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource';D=dict(np.load(S/'world_reference_v30.npz'));meta=json.loads((S/'world_design_v30.json').read_text());h=D['height'];H,W=h.shape;M=float(D['mpp']);cx=float(D['cx']);cy=float(D['cy']);yy,xx=np.mgrid[:H,:W];X=(cx-xx)*M;Y=(cy-yy)*M
mask=np.asarray(Image.open(Path(meta['source_folder'])/'RabaricRepublic.png').convert('RGB').resize((W,H))).max(2)>35
valid=mask&(D['water_clearance']>180)&(D['coast']>300)&(np.hypot(*np.gradient(h,M))<.18)&(h>-20585)&(np.hypot(X,Y)>12000)&~D['urban']&~D['farm']
validbytes=valid.astype('uint8')
color=np.array(Image.open(S/'T_IV_WorldBiomes30.png').convert('RGB').resize((W,H),Image.Resampling.BICUBIC))/255.;palette=np.array([[.34,.39,.12],[.46,.39,.17],[.25,.36,.13],[.43,.46,.19],[.31,.32,.13],[.48,.43,.20]])
farms=meta['agricultural_parcels'];before=len(farms)
for gx in np.arange(np.floor(X[valid].min()/200)*200,np.ceil(X[valid].max()/200)*200+1,200):
 for gy in np.arange(np.floor(Y[valid].min()/400)*400,np.ceil(Y[valid].max()/400)*400+1,400):
  ax=gx+28;bx=gx+172;ay=gy+28;by=gy+372;tx,ty=np.meshgrid(np.linspace(ax,bx,3),np.linspace(ay,by,5))
  if not (map_coordinates(validbytes,[cy-ty.ravel()/M,cx-tx.ravel()/M],order=0,mode='constant')>0).all():continue
  crop=(int(gx/200)*17+int(gy/400)*31)%6;col=palette[crop];x0=max(0,int(np.ceil(cx-bx/M)));x1=min(W,int(np.floor(cx-ax/M))+1);y0=max(0,int(np.ceil(cy-by/M)));y1=min(H,int(np.floor(cy-ay/M))+1)
  color[y0:y1,x0:x1]=col;D['farm'][y0:y1,x0:x1]=True
  farms.append({'center':[(ax+bx)/2,(ay+by)/2],'corners':[[ax,ay],[bx,ay],[bx,by],[ax,by]],'angle':0,'color':(col*255).astype(int).tolist(),'crop':crop})
roadmask=Image.new('L',(W,H));draw=ImageDraw.Draw(roadmask)
for q in meta['routes']+meta['farm_lanes']:draw.line([(round(cx-x/M),round(cy-y/M)) for x,y in q['points_m']],fill=125 if q['kind']=='farm_lane' else 160,width=1)
road=np.asarray(roadmask)/255*.30;road*=~D['water'];color=color*(1-road[...,None])+np.array([.43,.36,.22])*road[...,None]
Image.fromarray(np.uint8(np.clip(color,0,1)*255)).resize((4096,4096),Image.Resampling.BICUBIC).convert('RGBA').save(S/'T_IV_WorldBiomes30.png');np.savez_compressed(S/'world_reference_v30.npz',**D)
meta['network_summary'].update(farm_parcels=len(farms),cultivated_km2=float(D['farm'].sum()*M*M/1e6),rabaric_area_km2=float(mask.sum()*M*M/1e6));(S/'world_design_v30.json').write_text(json.dumps(meta,indent=2));print({'infill_parcels':len(farms)-before,**meta['network_summary']},flush=True)


