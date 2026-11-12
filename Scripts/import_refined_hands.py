import unreal as u,json,traceback
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');base='/Game/Elrhun/Golems';source=root/'ArtSource/Golems/RefinedHands'
T=u.AssetToolsHelpers.get_asset_tools();A=u.EditorAssetLibrary;S=u.get_editor_subsystem(u.SkeletalMeshEditorSubsystem)
mapping=json.loads((source.parent/'CorrectedWardrobe/material_paths.json').read_text());report={'success':False,'meshes':{}}
def material_for(name,role):
 if name in mapping:return u.load_asset(mapping[name])
 if 'Soul_gem' in name or 'Soul gem' in name:return u.load_asset(base+'/Materials/MI_SoulGem_'+role)
 if 'Dark_glossy' in name or 'Obsidian' in name:return u.load_asset(base+'/Materials/MI_DarkEyes')
 if 'joint' in name.lower() or 'burnished' in name.lower():return u.load_asset(base+'/Materials/MI_PolishedClay')
 return u.load_asset(base+'/Materials/M_ClayBody')
try:
 data=json.loads((root/'Saved/golem_corrected_import.json').read_text());skeleton=u.load_asset(base+'/Mesh/SK_ElrhunGolem_Skeleton');physics=u.load_asset(base+'/Physics/PHYS_GolemBody_Cloth')
 u.SystemLibrary.execute_console_command(u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world(),'Interchange.FeatureFlags.Import.FBX 0')
 for role in globals().get('roles_to_import',['Bare','Tank','Mage','Ranger','Healer','Necromancer']):
  path=base+'/Mesh/SK_ElrhunGolem' if role=='Bare' else data['roles'][role]['mesh'];old=u.load_asset(path);u.GolemClothTools.reset_cape_cloth(old)
  package=old.get_path_name().split('.')[0];folder,name=package.rsplit('/',1)
  task=u.AssetImportTask();task.filename=str(source/('SK_ElrhunGolem.fbx' if role=='Bare' else 'SK_Golem_'+role+'.fbx'));task.destination_path=folder;task.destination_name=name;task.automated=True;task.save=True;task.replace_existing=True;task.factory=u.FbxFactory()
  opt=u.FbxImportUI();opt.automated_import_should_detect_type=False;opt.import_as_skeletal=True;opt.mesh_type_to_import=u.FBXImportType.FBXIT_SKELETAL_MESH;opt.import_mesh=True;opt.import_animations=False;opt.import_materials=False;opt.import_textures=False;opt.create_physics_asset=False;opt.set_editor_property('skeleton',skeleton)
  opt.skeletal_mesh_import_data.normal_import_method=u.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;opt.skeletal_mesh_import_data.set_editor_property('bImportMorphTargets',True);task.options=opt
  T.import_asset_tasks([task]);mesh=next(u.load_asset(p) for p in task.imported_object_paths if isinstance(u.load_asset(p),u.SkeletalMesh))
  slots=list(mesh.get_editor_property('materials'));names=[];materials=[];gem=None
  for i,slot in enumerate(slots):
   n=str(slot.material_slot_name);names.append(n);material=material_for(n,'Tank' if role=='Bare' else role);assert material,(role,n)
   if 'Soul_gem' in n or 'Soul gem' in n:gem=i
   slot.set_editor_property('material_interface',material);slots[i]=slot;materials.append(material.get_path_name())
  mesh.set_editor_property('materials',slots);mesh.set_editor_property('physics_asset',physics);settings=S.get_lod_build_settings(mesh,0);S.set_lod_build_settings(mesh,0,settings);A.save_loaded_asset(mesh,only_if_is_dirty=False)
  assert gem is not None,(role,names)
  if role!='Bare':data['roles'][role].update({'mesh':mesh.get_path_name(),'slots':names,'materials':materials,'gem_slot':gem,'vertices':S.get_num_verts(mesh,0)})
  report['meshes'][role]={'path':mesh.get_path_name(),'vertices':S.get_num_verts(mesh,0),'gem_slot':gem}
 (root/'Saved/golem_corrected_import.json').write_text(json.dumps(data,indent=2));report['success']=True
except Exception:report['error']=traceback.format_exc()
finally:u.SystemLibrary.execute_console_command(u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world(),'Interchange.FeatureFlags.Import.FBX 1')
(root/'Saved/golem_refined_hands_import.json').write_text(json.dumps(report,indent=2))
