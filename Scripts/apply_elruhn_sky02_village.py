"""Center the tower and author flexible building land in the copied sky map only."""
import unreal,json,math,array,shutil,datetime,hashlib
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/ElRuhnSky02';R='/Game/IsekaiVillage/AdventureWorld';D=R+'/ElRuhnSky02'
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);A=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
Q=json.loads((O/'village_plan.json').read_text());assert W.get_path_name().startswith(Q['map']+'.');assert not (O/'assembled.json').exists(),'Use a refinement script after completed assembly'
def status(s):(O/'progress.json').write_text(json.dumps({'stage':s}))
def v(p):return unreal.Vector(*[float(x)*100 for x in p])
def xyz(p):return [p.x,p.y,p.z]
cx,cy,cz=Q['center_m'];H=array.array('f');H.frombytes((O/'terrain_height_f32.bin').read_bytes())
def height(x,y):
 u=max(0,min(1007.999,(x+600)*.84));w=max(0,min(1007.999,(y+600)*.84));ix=int(u);iy=int(w);fx=u-ix;fy=w-iy
 return (H[iy*1009+ix]*(1-fx)+H[iy*1009+ix+1]*fx)*(1-fy)+(H[(iy+1)*1009+ix]*(1-fx)+H[(iy+1)*1009+ix+1]*fx)*fy
if not (O/'before.json').exists():
 backup=B/'Saved/WorldBackups'/('BeforeElRuhnSky02_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'));backup.mkdir(parents=True)
 shutil.copy2(B/'Content/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky.umap',backup/'Map_ElRuhnSky.umap')
 rows=[]
 for a in E.get_all_level_actors():
  r=a.get_actor_rotation();rows.append({'name':a.get_name(),'label':a.get_actor_label(),'folder':str(a.get_folder_path()),'p':xyz(a.get_actor_location()),'s':xyz(a.get_actor_scale3d()),'r':[r.pitch,r.yaw,r.roll]})
 (O/'before.json').write_text(json.dumps({'backup':str(backup),'actors':rows},indent=2))
before=json.loads((O/'before.json').read_text());old={r['name']:r for r in before['actors']};actors={a.get_name():a for a in E.get_all_level_actors()}
for a in list(actors.values()):
 if 'ElRuhnSky02' in [str(t) for t in a.tags]:E.destroy_actor(a)
def material(name,source):
 path=D+'/Materials/'+name;m=unreal.load_asset(path) if A.does_asset_exist(path) else A.duplicate_asset(source,path);assert m;return m
status('importing fitted streets and building land')
mats={'foundation':material('M_ES02_Foundation',R+'/ElRuhnSky01/Materials/M_ES01_Textured_foundation'),'trim':material('M_ES02_BoundaryStone',R+'/ElRuhnSky01/Materials/M_ES01_Textured_trim'),'paving':material('MI_ES02_Paving','/Game/StylizedIsland/Mesh/Modular_Pieces/MI_Stone_Floor')}
for row in Q['assets']:
 name=row['name'];task=unreal.AssetImportTask();task.filename=str(O/(name+'.obj'));task.destination_path=D+'/Meshes';task.destination_name=name;task.automated=True;task.replace_existing=True;task.save=True
 op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;op.static_mesh_import_data.generate_lightmap_u_vs=False;op.static_mesh_import_data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;task.options=op;T.import_asset_tasks([task]);mesh=unreal.load_asset(D+'/Meshes/'+name);assert mesh
 slots=list(mesh.static_materials)
 for s in slots:s.set_editor_property('material_interface',mats[str(s.material_slot_name)])
 mesh.set_editor_property('static_materials',slots);mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);A.save_loaded_asset(mesh)
 a=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());a.static_mesh_component.set_static_mesh(mesh);a.set_actor_label(name.replace('SM_ES02_','Village | '));a.set_folder_path('El Ruhn Sky/Village Layout');a.tags=['ElRuhnSky02'];a.set_actor_enable_collision('Boundaries' not in name)
status('moving the tower and settled village')
tower=next(a for a in E.get_all_level_actors() if a.get_actor_label()=='El Ruhn | Tower of the Five Winds');tower.set_actor_location(v(Q['tower_origin_m']),False,False)
building_old=[r for r in before['actors'] if r['folder']=='Village/Buildings'];moved={};fountain=Q['fountain_m']
released={p['released_starter_actor'] for p in Q['plots'] if p.get('released_starter_actor')}
for p in Q['plots']:
 if not p['existing_actor_label']:continue
 a=next(a for a in E.get_all_level_actors() if a.get_actor_label()==p['existing_actor_label']);src=old[a.get_name()];a.set_actor_rotation(unreal.Rotator(yaw=p['yaw_deg']),False);a.set_actor_scale3d(unreal.Vector(*src['s']));a.set_actor_location(v(p['center_m']),False,False)
 center,ext=a.get_actor_bounds(False);loc=a.get_actor_location();fit=min(1.,p['size_m']*100*.78/max(ext.x*2,ext.y*2));a.set_actor_scale3d(a.get_actor_scale3d()*fit);center,ext=a.get_actor_bounds(False)
 delta=v(p['center_m'])-unreal.Vector(center.x,center.y,center.z-ext.z);a.set_actor_location(a.get_actor_location()+delta,False,False)
 moved[a.get_name()]={'old':src,'plot':p,'position':xyz(a.get_actor_location()),'rotation':p['yaw_deg']};a.set_folder_path('El Ruhn Sky/Village Buildings')
for name,src in old.items():
 a=actors.get(name)
 if not a or name in moved:continue
 x,y,z=[u/100 for u in src['p']];folder=src['folder'];label=src['label']
 if label in released:
  E.destroy_actor(a);continue
 if folder in ['Village/Civic','Village/Civic Gardens'] or label=='Village plaza cobbles' or (folder=='Village/Lanterns' and math.hypot(x,y)<25):
  nx=x+fountain[0];ny=y+fountain[1];nz=z+height(nx,ny)-height(x,y);a.set_actor_location(v([nx,ny,nz]),False,False)
 elif folder in ['Village/Props','Village/Lanterns']:
  nearest=min(building_old,key=lambda b:math.hypot(b['p'][0]/100-x,b['p'][1]/100-y));move=moved.get(nearest['name'])
  if nearest['label'] in released and math.hypot(nearest['p'][0]/100-x,nearest['p'][1]/100-y)<26:
   E.destroy_actor(a);continue
  if move and math.hypot(nearest['p'][0]/100-x,nearest['p'][1]/100-y)<26:
   angle=math.radians(move['rotation']-nearest['r'][1]);dx=x-nearest['p'][0]/100;dy=y-nearest['p'][1]/100;nx=move['plot']['center_m'][0]+dx*math.cos(angle)-dy*math.sin(angle);ny=move['plot']['center_m'][1]+dx*math.sin(angle)+dy*math.cos(angle)
   nz=move['plot']['center_m'][2] if math.hypot(nx-move['plot']['center_m'][0],ny-move['plot']['center_m'][1])<move['plot']['size_m']*.5 else height(nx,ny)
   a.set_actor_location(v([nx,ny,nz+(z-height(x,y))]),False,False);a.set_actor_rotation(unreal.Rotator(pitch=src['r'][0],yaw=src['r'][1]+math.degrees(angle),roll=src['r'][2]),False)
 if folder.startswith('BuildGrid/'):
  E.destroy_actor(a);continue
 if isinstance(a,unreal.PlayerStart):a.set_actor_location(v([cx+8,cy-173,height(cx+8,cy-173)+1.1]),False,False);a.set_actor_rotation(unreal.Rotator(yaw=90),False);a.set_actor_label('Start | Tower village square')
status('private landscape painting')
task=unreal.AssetImportTask();task.filename=str(O/'T_ES02_VillageWeights.png');task.destination_path=D+'/Textures';task.automated=True;task.replace_existing=True;task.save=True;T.import_asset_tasks([task]);tex=unreal.load_asset(D+'/Textures/T_ES02_VillageWeights');assert tex
tex.set_editor_property('srgb',False);tex.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP);tex.set_editor_property('mip_gen_settings',unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS);tex.set_editor_property('filter',unreal.TextureFilter.TF_BILINEAR);tex.set_editor_property('address_x',unreal.TextureAddress.TA_CLAMP);tex.set_editor_property('address_y',unreal.TextureAddress.TA_CLAMP);A.save_loaded_asset(tex)
land=next(a for a in E.get_all_level_actors() if isinstance(a,unreal.Landscape));parent=material('M_ES02_Landscape',R+'/Materials/M_IV_StylizedLandscape32');mi=material('MI_ES02_Landscape',R+'/Materials/MI_IV_StylizedLandscape32');replaced=0
for n in M.get_material_expressions(parent):
 if isinstance(n,unreal.MaterialExpressionTextureSample) and n.texture and 'Layer32_Weights' in n.texture.get_name():n.set_editor_property('texture',tex);replaced+=1
assert replaced or any(isinstance(n,unreal.MaterialExpressionTextureSample) and n.texture==tex for n in M.get_material_expressions(parent));M.recompile_material(parent);M.set_material_instance_parent(mi,parent);M.update_material_instance(mi);A.save_loaded_asset(parent);A.save_loaded_asset(mi)
land.set_editor_property('landscape_material',mi);land.set_editor_property('landscape_hole_material',mi);land.force_layers_full_update()
status('clearing foliage only beneath new structures and paths')
def nearsegment(x,y,a,b,width):
 dx=b[0]-a[0];dy=b[1]-a[1];t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/max(dx*dx+dy*dy,.001)));return (x-a[0]-t*dx)**2+(y-a[1]-t*dy)**2<width*width
segments=[]
for r in Q['roads']:
 pts=r['points'];segments.extend((a,b,r['width']/2+.5) for a,b in zip(pts,pts[1:]))
# Spatial bins keep the foliage check linear rather than comparing 100k instances with every road segment.
bins={}
for seg in segments:
 a,b,width=seg
 for ix in range(math.floor((min(a[0],b[0])-width)/20),math.floor((max(a[0],b[0])+width)/20)+1):
  for iy in range(math.floor((min(a[1],b[1])-width)/20),math.floor((max(a[1],b[1])+width)/20)+1):bins.setdefault((ix,iy),[]).append(seg)
cleared=0
for a in E.get_all_level_actors():
 for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
  remove=[]
  for i in range(c.get_instance_count()):
   pos=c.get_instance_transform(i,True).translation;x=pos.x/100;y=pos.y/100
   if math.hypot(x-cx,y-cy)>290:continue
   hit=math.hypot(x-cx,y-cy)<48 or (abs(x-cx)<19 and cy-92<y<cy) or math.hypot(x-fountain[0],y-fountain[1])<23
   if not hit:
    for p in Q['plots']:
     angle=math.radians(p['yaw_deg']);dx=x-p['center_m'][0];dy=y-p['center_m'][1]
     if abs(dx*math.cos(angle)+dy*math.sin(angle))<p['size_m']/2+1 and abs(-dx*math.sin(angle)+dy*math.cos(angle))<p['size_m']/2+1:hit=True;break
   if not hit:hit=any(nearsegment(x,y,*seg) for seg in bins.get((math.floor(x/20),math.floor(y/20)),[]))
   if hit:remove.append(i)
  if remove:c.remove_instances(remove);cleared+=len(remove)
status('authoring player-choice building catalogue')
runtime=E.spawn_actor_from_class(unreal.VillageRuntime,v([cx,cy-154,height(cx,cy-154)]));runtime.set_actor_label('Village | player construction');runtime.set_folder_path('El Ruhn Sky/Gameplay');runtime.tags=['ElRuhnSky02'];runtime.set_editor_property('use_authored_plots',True);runtime.set_editor_property('construction_save_slot','ElRuhnSky_Village02')
catalog=[];templates={};catalog_report=[]
entries=[('Cottage','House','Commoner cottage','Village',2,8,0,0,2),('Townhouse','House','Commoner townhouse','Village',5,10,0,0,3),('CountryHome','House','Timber family home','Village',7,8,0,0,2),('Inn','Inn','Adventurers inn','Village',8,10,0,0,4),('Shop','Shop','General shop','Village',4,8,0,0,0),('Smith','Smith','Blacksmith','Village',3,10,2,0,0),('Guild','Guild','Adventurers guild','Village',6,12,2,0,0),('Chapel','Chapel','Church','Village',12,12,0,0,0),('Training','Training','Knight school','Village',6,8,0,0,0),('Warehouse','Warehouse','Warehouse','Village',11,10,0,0,0),('Bakery','Bakery','Bakery','Village',1,8,0,0,0),('Bank','Bank','Bank','LargeTown',13,10,4,0,0),('Bath','Bath','Bathhouse','LargeTown',14,8,3,0,0),('Bell','Bell','Bell house','LargeTown',13,6,2,0,0),('Academy','Academy','Magic academy','LargeTown',6,12,6,0,0),('Manor','Manor','Noble residence','LargeTown',12,14,6,0,3),('Castle','Castle','Lords residence','Kingdom',14,16,8,4,6)]
entries.insert(0,('InheritedHouse','House','Inherited home','Village',2,0,0,0,2))
for ident,kind,title,era,bp,wood,iron,crystal,beds in entries:
 path='/Game/Fantastic_Village_Pack/blueprints/buildings/BP_BLD_house_'+str(bp);blueprint=unreal.load_asset(path);assert blueprint,path;cls=blueprint.generated_class()
 if bp not in templates:
  sample=E.spawn_actor_from_class(cls,unreal.Vector(0,0,100000));o,e=sample.get_actor_bounds(False);scale=1800/max(2*e.x,2*e.y);sample.set_actor_scale3d(unreal.Vector(scale,scale,scale));o,e=sample.get_actor_bounds(False);offset=unreal.Vector(-o.x,-o.y,100000-(o.z-e.z));templates[bp]=(scale,offset);E.destroy_actor(sample)
 scale,offset=templates[bp];entry=unreal.TownPlot();entry.set_editor_property('id',ident);entry.set_editor_property('kind',getattr(unreal.TownBuilding,kind.upper()));entry.set_editor_property('era',getattr(unreal.TownEra,{'Village':'VILLAGE','LargeTown':'LARGE_TOWN','Kingdom':'KINGDOM'}[era]));entry.set_editor_property('display_name',title);entry.set_editor_property('building_class',cls);entry.set_editor_property('building_scale',unreal.Vector(scale,scale,scale));entry.set_editor_property('building_offset',offset);entry.set_editor_property('buildable_size',2000.)
 for key,value in [('wood_cost',wood),('iron_cost',iron),('crystal_cost',crystal),('bed_bonus',beds)]:entry.set_editor_property(key,value)
 entry.set_editor_property('unique_building',ident in ('InheritedHouse','Guild'))
 catalog.append(entry);catalog_report.append({'id':ident,'use':kind,'name':title,'era':era,'model':path,'model_scale':scale,'offset_cm':xyz(offset),'cost':[wood,iron,crystal],'beds':beds,'unique':ident in ('InheritedHouse','Guild')})
runtime.set_editor_property('building_catalog',catalog);plots=[]
for p in Q['plots']:
 slot=unreal.TownPlot();slot.set_editor_property('id',p['id']);slot.set_editor_property('location',v(p['center_m']));slot.set_editor_property('stake_offset',v([b-a for a,b in zip(p['center_m'],p['stake_m'])]));slot.set_editor_property('building_rotation',unreal.Rotator(yaw=p['yaw_deg']));slot.set_editor_property('buildable_size',p['size_m']*100);slot.set_editor_property('flexible_use',not bool(p['existing_actor_label']));slot.set_editor_property('display_name',p['name']);slot.set_editor_property('built',bool(p['existing_actor_label']));slot.set_editor_property('scenery',bool(p['existing_actor_label']))
 if p['existing_actor_label']:slot.set_editor_property('kind',getattr(unreal.TownBuilding,p['kind'].upper()));slot.set_editor_property('bed_bonus',p['beds'])
 else:slot.set_editor_property('kind',unreal.TownBuilding.UNASSIGNED)
 plots.append(slot)
farm=unreal.TownPlot();farm.set_editor_property('id','ExistingFarm');farm.set_editor_property('kind',unreal.TownBuilding.FARM);farm.set_editor_property('built',True);farm.set_editor_property('scenery',True);farm.set_editor_property('location',v([130,-98,height(130,-98)]));plots.append(farm)
runtime.set_editor_property('authored_plots',plots)
ghostpath=D+'/Materials/M_ES02_PlacementPreview';ghost=unreal.load_asset(ghostpath) if A.does_asset_exist(ghostpath) else T.create_asset('M_ES02_PlacementPreview',D+'/Materials',unreal.Material,unreal.MaterialFactoryNew());M.delete_all_material_expressions(ghost);ghost.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT);ghost.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT);ghost.set_editor_property('two_sided',True)
color=M.create_material_expression(ghost,unreal.MaterialExpressionVectorParameter);color.set_editor_property('parameter_name','PreviewColor');color.set_editor_property('default_value',unreal.LinearColor(.08,.8,.55,1));M.connect_material_property(color,'RGB',unreal.MaterialProperty.MP_EMISSIVE_COLOR);alpha=M.create_material_expression(ghost,unreal.MaterialExpressionConstant);alpha.r=.38;M.connect_material_property(alpha,'',unreal.MaterialProperty.MP_OPACITY);M.recompile_material(ghost);A.save_loaded_asset(ghost);runtime.set_editor_property('placement_preview_material',ghost)
W.get_world_settings().set_editor_property('default_game_mode',unreal.load_class(None,'/Script/IsekaiVillage.IsekaiVillageGameMode'))
status('saving centered village')
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level();A.save_directory(D,only_if_is_dirty=True,recursive=True)
source=json.loads((B/'ArtSource/World/ElRuhnSky01/copy_applied.json').read_text());assert hashlib.sha256((B/'Content/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.umap').read_bytes()).hexdigest()==source['source_sha256']
(O/'assembled.json').write_text(json.dumps({'status':'saved','map':Q['map'],'tower_center_m':Q['center_m'],'existing_buildings_relocated':len(moved),'unassigned_purchase_plots':Q['purchase_slots'],'catalog':catalog_report,'cleared_instances':cleared,'source_map_unchanged':True,'farm_unchanged':True,'runtime_save_slot':'ElRuhnSky_Village02'},indent=2));status('saved')
