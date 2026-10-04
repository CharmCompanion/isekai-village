from pathlib import Path
P=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Scripts');p=P/'connect_wetlands_v30.py';s=p.read_text().replace('stride=2;walk=(shore>240)','stride=1;walk=(shore>110)').replace('links=[];bridges=[];candidates=[]',"links=[];bridges=meta.get('bridges',[]);candidates=[]")
s=s.replace("if not w.any() or not (values('channel',segment)[w]>.01).all():break","if not w.any():continue\n  if not (values('channel',segment)[w]>.01).all():break")
p.write_text(s)
p=P/'build_civilizations_v30.py';s=p.read_text();marker='# One survey grid across'
s=s.replace(marker,"""# Timber decks physically span the tidal channels; ordinary road ribbons stop at water.
for bridge in meta.get('bridges',[]):
 p=np.array(bridge['points_m']);distance=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))];z0=h(*p[0])+.35;z1=h(*p[-1])+.35
 zz=np.maximum(z0+(z1-z0)*distance/max(distance[-1],1),-20595.)
 tangent=np.gradient(p,axis=0);tangent/=np.maximum(np.linalg.norm(tangent,axis=1,keepdims=True),1e-6);side=np.column_stack([-tangent[:,1],tangent[:,0]])*6
 v=[]
 for q,l,z in zip(p,side,zz):v.extend([[*(q-l),z],[*(q+l),z]])
 f=[]
 for k in range(len(p)-1):
  a=k*2;f.extend([[a,a+3,a+1],[a,a+2,a+3]])
  mid=(p[k]+p[k+1])*.5;length=np.linalg.norm(p[k+1]-p[k]);yaw=np.arctan2(*(p[k+1]-p[k])[::-1])
  if length<1:continue
  for sign in [-1,1]:
   rail=mid+side[k]*sign;roads.box(*rail,(zz[k]+zz[k+1])*.5+1.45,length,.35,.45,'wood',.08,yaw)
  if k%2==0:
   for sign in [-1,1]:
    xy=p[k]+side[k]*sign*.85;bottom=h(*xy)-2;roads.cyl(*xy,bottom,.55,max(.3,zz[k]+1.6-bottom),'wood',12)
 roads.part(v,f,'wood')
"""+marker);p.write_text(s)
p=P/'apply_world_terrain_v30.py';s=(P/'apply_puzzle_continent_v30.py').read_text();s=s[:s.index("exec(compile((B/'Scripts/apply_civilizations_v30.py')")];p.write_text(s)
(P/'finish_world_networks_v30.py').write_text("from pathlib import Path\nB=Path('D:/DEVELOPMENT/Games/IsekaiVillage')\nfor script in ['apply_civilizations_v30.py','polish_civilization_palette_v30.py','final_continent_material_v30.py']:\n exec(compile((B/'Scripts'/script).read_text(),script,'exec'),{'__name__':'__main__'})\n")
