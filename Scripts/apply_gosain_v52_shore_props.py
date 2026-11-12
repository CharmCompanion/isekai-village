import unreal,json,math,shutil,time
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain52';D='/Game/IsekaiVillage/AdventureWorld/Gosain52';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();M=unreal.MaterialEditingLibrary;W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert (O/'applied.json').exists();assert not (O/'shore_applied.json').exists()
source='/Game/SoStylized/Environment/Rocks/Materials/Spire/MI_RockSpire_Rocks';path=D+'/Materials/MI_Gosain52_MossRock'
mat=unreal.load_asset(path) if A.does_asset_exist(path) else A.duplicate_asset(source,path)
M.set_material_instance_vector_parameter_value(mat,'Rock Tint',unreal.LinearColor(.38,.43,.34,1));M.set_material_instance_vector_parameter_value(mat,'Fake Reflection Tint',unreal.LinearColor(.22,.32,.27,1));M.set_material_instance_scalar_parameter_value(mat,'Metallic',0);M.set_material_instance_scalar_parameter_value(mat,'Faked Wet Reflection',.4);A.save_loaded_asset(mat)
sources=['/Game/SoStylized/Environment/Rocks/Spire/SM_RockSpire_RockClumpB0'+str(i) for i in [2,3,4]]+['/Game/AdvancedVillagePack/Meshes/'+n for n in ['SM_GrassPatch_Var01','SM_GrassPatch_Var02','SM_Flower_Var01','SM_Flower_Var05']]
fts=[];meshes=[]
for i,source in enumerate(sources):
 path=D+'/Meshes/SM_Shore'+str(i);mesh=unreal.load_asset(path) if A.does_asset_exist(path) else A.duplicate_asset(source,path);assert mesh
 if i<3:
  slots=list(mesh.static_materials)
  for s in slots:s.set_editor_property('material_interface',mat)
  mesh.set_editor_property('static_materials',slots)
 A.save_loaded_asset(mesh);meshes.append(mesh)
 path=D+'/Foliage/FT_Shore'+str(i);ft=unreal.load_asset(path) if A.does_asset_exist(path) else T.create_asset('FT_Shore'+str(i),D+'/Foliage',unreal.FoliageType_InstancedStaticMesh,unreal.FoliageType_InstancedStaticMeshFactory());ft.set_editor_property('mesh',mesh);A.save_loaded_asset(ft);fts.append(ft)
groups=[[] for _ in sources]
for q in json.loads((O/'shore_props.json').read_text()):
 idx=q['variant']+(0 if q['kind']=='rock' else 3);box=meshes[idx].get_bounding_box();lo=box.min;hi=box.max
 if q['kind']=='rock':scale=[q['size'][j]*100/[hi.x-lo.x,hi.y-lo.y,hi.z-lo.z][j] for j in range(3)]
 else:scale=[q['size']]*3
 ang=math.radians(q['yaw']);cx=(lo.x+hi.x)*.5*scale[0];cy=(lo.y+hi.y)*.5*scale[1]
 loc=unreal.Vector(q['xy'][0]*100-cx*math.cos(ang)+cy*math.sin(ang),q['xy'][1]*100-cx*math.sin(ang)-cy*math.cos(ang),q['z']*100-lo.z*scale[2])
 groups[idx].append(unreal.Transform(location=loc,rotation=unreal.Rotator(pitch=0,yaw=q['yaw'],roll=0),scale=unreal.Vector(*scale)))
backup=B/'Saved/WorldBackups'/('BeforeGosain52Shore_'+time.strftime('%Y%m%d_%H%M%S'));backup.mkdir(parents=True);shutil.copy2(B/'Content/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.umap',backup/'Map_AnimeAdventure.umap')
original=[]
try:
 for a in E.get_all_level_actors():
  if a.get_actor_label().startswith('Gosain | Lakeside grotto rock '):
   c=a.static_mesh_component;original.append((c,c.get_material(0)));c.set_material(0,mat)
 for ft,rows in zip(fts,groups):unreal.InstancedFoliageActor.add_instances(W,ft,rows)
 assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception:
 for c,m in original:c.set_material(0,m)
 for ft in fts:unreal.InstancedFoliageActor.remove_all_instances(W,ft)
 raise
(O/'shore_applied.json').write_text(json.dumps({'status':'saved','backup':str(backup),'counts':[len(g) for g in groups],'grotto_rock_overrides':len(original),'shared_source_assets_unchanged':True,'native_review':'pending'},indent=2))
