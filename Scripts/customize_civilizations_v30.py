from pathlib import Path
P=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Scripts')
p=P/'build_civilizations_v30.py';s=p.read_text()
a=s.index('REF=Path');b=s.index("P='/Game",a)
s=s[:a]+'''landmask=~D['water'];clearance=D['water_clearance']
def onland(x,y,margin=80):
 px=int(round(cx-x/m));py=int(round(cy-y/m));return 0<=py<landmask.shape[0] and 0<=px<landmask.shape[1] and bool(clearance[py,px]>margin)
'''+s[b:]
s=s.replace("if key in ['Oak','Pine','Palm','DesertPalm'] and not onland(x,y):return", """# Docks may extend over tidal water; all buildings, vegetation and walls stay dry.
 if key not in ['Boat','SM_Civ30_Boardwalk'] and not onland(x,y,120 if key not in ['Oak','Pine','Palm','DesertPalm','SM_Civ30_Reeds'] else 70):return""")
s=s.replace("n=max(2,int(dist/24)+1)","n=max(2,int(dist/38)+1)")
s=s.replace("for j in range(len(p)-1):a=2*j;f.extend([[a,a+3,a+1],[a,a+2,a+3]])", """for j in range(len(p)-1):
  if not all(onland(*q,55) for q in [p[j],p[j+1],(p[j]+p[j+1])*.5]):continue
  a=2*j;f.extend([[a,a+3,a+1],[a,a+2,a+3]])""")
s=s.replace("if culture=='farming' and np.sin(xx/230)+np.cos(yy/330)<.85:continue", "if culture=='farming':continue")
s=s.replace("9000 if kind=='city' else 2400 if kind=='town' else 850", "7000 if kind=='city' else 1800 if kind=='town' else 500")
a=s.index('# Orchards and hedgerows');b=s.index('# Tidal reed banks',a)
s=s[:a]+'''# National routes meet the local north/south streets and city gates.
for q in meta['routes']+meta['farm_lanes']:ribbon(q['points_m'],q['width_m'])
# One survey grid across the farming country, rather than detached decorative fields.
for k,q in enumerate(meta['agricultural_parcels']):
 pts=np.array(q['corners']);ax,ay=pts[0];bx,by=pts[2];nx=4;ny=8;v=[]
 for j in range(ny+1):
  for i in range(nx+1):
   xx=ax+(bx-ax)*i/nx;yy=ay+(by-ay)*j/ny;v.append([xx,yy,h(xx,yy)+.18])
 f=[]
 for j in range(ny):
  for i in range(nx):
   a=j*(nx+1)+i;f.extend([[a,a+1,a+nx+2],[a,a+nx+2,a+nx+1]])
 roads.part(v,f,'crop'+str(q['crop']))
 # Sparse hedges retain the clean survey lines; leave junctions open.
 if k%4==0:
  for yy in np.arange(ay+50,by-35,105):add('Oak',ax-11,yy,height=rng.uniform(6,9),yaw=rng.uniform(0,360))
 if k%25==0:
  add('SM_Civ30_Granary',ax+30,ay+32,scale=.65)
  add('Cart',ax+55,ay+30,height=3,yaw=90)
'''+s[b:]
p.write_text(s)
p=P/'apply_civilizations_v30.py';s=p.read_text();a=s.index('materials={}')
s=s[:a]+"""# Clear every previous regional foliage type, including the palette variants.
for ap in A.list_assets(R+'/Foliage/Civilizations',recursive=True):
 ft=unreal.load_asset(ap)
 if isinstance(ft,unreal.FoliageType_InstancedStaticMesh):unreal.InstancedFoliageActor.remove_all_instances(W,ft)
for actor in E.get_all_level_actors():
 if any(str(t).startswith('Civ29_') for t in actor.tags):E.destroy_actor(actor)
colors.update({'crop0':(.34,.39,.12),'crop1':(.46,.39,.17),'crop2':(.25,.36,.13),'crop3':(.43,.46,.19),'crop4':(.31,.32,.13),'crop5':(.48,.43,.20)})
"""+s[a:]
s=s.replace("if name in ['cropgold','cropgreen']:code+=", "if name.startswith('crop'):code+=").replace('sin(p.x*.75+p.y*.35)','sin(p.x*1.1)')
p.write_text(s)
