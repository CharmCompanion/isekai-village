"""Country-specific terrain and settlement foundations; source map stays read-only."""
from pathlib import Path
import numpy as np,json
from PIL import Image,ImageDraw
from scipy.ndimage import gaussian_filter,map_coordinates,label,distance_transform_edt
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource';REF=Path('D:/DEVELOPMENT/Games/GuildSim-Lineage/GuildFounder-DesktopCopy/BaseProject/assets/map/kingdoms')
d=dict(np.load(S/'world_reference_v28.npz'));h=d['height'].astype(float);H,W=h.shape;M=float(d['mpp']);cx=float(d['cx']);cy=float(d['cy']);yy,xx=np.mgrid[:H,:W];X=(cx-xx)*M;Y=(cy-yy)*M;coast=d['coast'];sea=-20600.;rng=np.random.default_rng(29041)
meta=json.loads((S/'world_design_v28.json').read_text());color=np.asarray(Image.open(S/'T_IV_WorldBiomes28.png').convert('RGB').resize((W,H),Image.Resampling.BICUBIC),dtype=float)/255

def layer(name):return np.asarray(Image.open(REF/(name+'.png')).convert('RGB').resize((W,H))).max(2)>35
def smooth(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def value(arr,x,y):return map_coordinates(arr,[[cy-y/M],[cx-x/M]],order=1,mode='nearest')[0]
countries=['YozuanDesert','DivineEmpireofGosain','KelsinFederation','RabaricRepublic','VylfodDominion'];cm={n:layer(n) for n in countries}
# The southeast is a low tidal region, with branching sea-connected channels.
wetregion=cm['VylfodDominion']&(coast>0)&(coast<4400)&(Y<-12000)
wetblend=(1-smooth(2200,4400,coast))*wetregion
bank=sea+3+np.maximum(coast,0)*.005+5*(.5+.5*np.sin(X/570)*np.cos(Y/730))
h=h*(1-wetblend)+bank*wetblend
channel=np.zeros_like(h)
for offset in [-34000,-42000,-50000]:
 axis=offset+800*np.sin(Y/1800)+360*np.sin(Y/650)
 c=1-smooth(75,190,np.abs(X-axis));c*=wetregion*(1-smooth(2600,3900,coast));channel=np.maximum(channel,c)
h=h*(1-channel)+(sea-4)*channel
color=color*(1-wetblend[...,None]*.8)+np.array([.11,.24,.13])*wetblend[...,None]*.8
color=color*(1-channel[...,None])+np.array([.025,.15,.18])*channel[...,None]
# Keep established town coordinates wherever they are outside the exact-seat landscape.
sites=[]
labels={'DivineEmpireofGosain':'Gosain','YozuanDesert':'Yozuan','KelsinFederation':'Kelsin','RabaricRepublic':'Rabaric','VylfodDominion':'Vylfod'}
for q in meta['settlements']:
 x,y=q['xy_m']
 if np.hypot(x,y)<20000:continue
 q=dict(q);q['culture']={'DivineEmpireofGosain':'religious','YozuanDesert':'nomad','KelsinFederation':'arcane','RabaricRepublic':'farming','VylfodDominion':'wetland'}[q['country']]
 q['radius_m']={'city':850,'town':430,'village':190}[q['kind']]
 q['name']=labels[q['country']]+' '+('regional capital' if q['kind']=='city' else q['kind']+' '+str(len(sites)+1))
 if q['country']=='YozuanDesert' and len([v for v in sites if v['country']==q['country']]) in [2,5]:q['culture']='cult';q['name']='Yozuan secluded cult sanctuary'
 sites.append(q)
# Two northern offshore islands share the fortified religious identity; the smaller
# western island receives the sovereign cathedral citadel requested by the user.
islands,n=label(cm['DivineEmpireofGosain']);sizes=[(int((islands==i).sum()),i) for i in range(1,n+1)];sizes=sorted([q for q in sizes if q[0]>100])[:2]
for k,(_,i) in enumerate(sizes):
 mask=islands==i;interior=distance_transform_edt(mask);py,px=np.unravel_index(np.argmax(interior),interior.shape)
 sites.append({'country':'DivineEmpireofGosain','culture':'citadel' if k==0 else 'religious','kind':'city' if k==0 else 'town','radius_m':1050 if k==0 else 530,'xy_m':[(cx-px)*M,(cy-py)*M],'pixel':[int(px),int(py)],'name':'Northern island cathedral fortress' if k==0 else 'Northern island monastery fortress'})
# A shoreline stilt town is positioned on the tidal shelf, rather than inland jungle.
valid=wetregion&(coast>600)&(coast<1500)&(channel>.02)&(channel<.20)&(Y<-19000)
py,px=np.where(valid);j=np.argmin((X[py,px]+39500)**2+(Y[py,px]+27000)**2)
sites.append({'country':'VylfodDominion','culture':'harbor','kind':'town','radius_m':450,'xy_m':[float(X[py[j],px[j]]),float(Y[py[j],px[j]])],'pixel':[int(px[j]),int(py[j])],'name':'Vylfod tidal harbor'})
# Found settlements on gentle, continuous terraces. Their surroundings fade back
# into the original land; no floating flat platforms or changes near El Ruhn.
for q in sites:
 x,y=q['xy_m'];r=q['radius_m'];dist=np.hypot(X-x,Y-y);inside=dist<r*.95
 level=float(np.median(h[inside]));q['ground_m']=level
 if q['culture']=='harbor':level=sea+11;q['ground_m']=level
 blend=1-smooth(r*.92,r*1.6,dist);blend*=coast>400
 h=h*(1-blend)+level*blend
 q['pixel']=[round(cx-x/M),round(cy-y/M)]
# Agricultural parcels are landscape-scale shapes, fitted only to gentle southern plains.
farms=[];farmmask=Image.new('RGB',(W,H));fd=ImageDraw.Draw(farmmask)
grad=np.hypot(*np.gradient(h,M))
valid=cm['RabaricRepublic']&(coast>1100)&(grad<.17)&(h>sea+50)
py,px=np.where(valid)
for k in range(180):
 j=int(rng.integers(len(px)));fx=float(X[py[j],px[j]]);fy=float(Y[py[j],px[j]])
 if np.hypot(fx,fy)<19500:continue
 if any(np.hypot(fx-t['xy_m'][0],fy-t['xy_m'][1])<t['radius_m']*1.2 for t in sites):continue
 a=rng.uniform(-.6,.6);w=rng.uniform(120,350);l=rng.uniform(180,460)
 pts=[]
 for u,v in [(-w,-l),(w*.9,-l*.92),(w,l),(-w*.92,l*.95)]:
  tx=fx+u*np.cos(a)-v*np.sin(a);ty=fy+u*np.sin(a)+v*np.cos(a);pts.append((tx,ty))
 if not all(value(valid.astype(float),u,v)>.8 for u,v in pts):continue
 palette=[(80,102,35),(124,113,48),(62,99,43),(111,90,46),(105,127,49)];col=palette[k%len(palette)]
 fd.polygon([(int(cx-u/M),int(cy-v/M)) for u,v in pts],fill=col)
 farms.append({'center':[fx,fy],'corners':pts,'angle':a,'color':np.array(col).tolist()})
f=np.asarray(farmmask)/255;fm=f.max(2)>0;color[fm]=color[fm]*.25+f[fm]*.75
# Coastal dune edges retain sandy contact with water outside the marsh channels.
color=np.clip(color,0,1);Image.fromarray(np.uint8(color*255)).resize((4096,4096),Image.Resampling.BICUBIC).convert('RGBA').save(S/'T_IV_WorldBiomes29.png')
d['height']=h.astype('float32');d['wetland']=wetblend.astype('float32');d['channel']=channel.astype('float32');np.savez_compressed(S/'world_reference_v29.npz',**d)
meta['settlements']=sites;meta['agricultural_parcels']=farms
meta['civilizations']={'DivineEmpireofGosain':{'identity':'fortified religious island nation with mainland provinces','visuals':'cathedral citadel, defensive curtain walls, gate towers, monasteries, banner standards'},'YozuanDesert':{'identity':'two distinct groups: nomads and cultists','visuals':'nomad caravan camps and oasis markets; separate remote dark sandstone sanctuaries'},'KelsinFederation':{'identity':'resource-poor society specializing in magic technology','visuals':'arcane manufactories, civic workshops, crystal-powered towers, conduit networks; no mines or resource export depots'},'RabaricRepublic':{'identity':'lush plains and farming','visuals':'irregular fields, hedgerows, orchards, granaries, mills, market villages'},'VylfodDominion':{'identity':'beaches and wetlands','visuals':'tidal creeks, reed beds, palms, stilt homes, raised boardwalks and fishing harbors'}}
meta['content_version']=29;meta['scope']='Finished regional environmental art pass; scenic civilizations, not simulated populations or playable interiors.'
(S/'world_design_v29.json').write_text(json.dumps(meta,indent=2));(S/'civilization_sites_v29.json').write_text(json.dumps(sites,indent=2));print({'sites':len(sites),'farms':len(farms),'fortress':[q for q in sites if q['culture']=='citadel']},flush=True)
exec(compile((B/'Scripts/build_world_surface_v29.py').read_text(),'surface','exec'))
