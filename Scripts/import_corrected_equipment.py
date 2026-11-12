import unreal as u,json,traceback
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');base='/Game/Elrhun/Golems'
sources=root/'ArtSource/Golems/CorrectedWardrobe'
mapping=json.loads((sources/'material_paths.json').read_text())
T=u.AssetToolsHelpers.get_asset_tools();A=u.EditorAssetLibrary
S=u.get_editor_subsystem(u.SkeletalMeshEditorSubsystem)
report=json.loads((root/'Saved/golem_corrected_import.json').read_text()) if (root/'Saved/golem_corrected_import.json').exists() else {'roles':{}}
report['success']=False
def resolve(name,role):
 if name in mapping:return u.load_asset(mapping[name]) if mapping[name] else None
 if 'Soul_gem' in name or 'Soul gem' in name:return u.load_asset(base+'/Materials/MI_SoulGem_'+role)
 if 'Dark_glossy' in name or 'Obsidian' in name:return u.load_asset(base+'/Materials/MI_DarkEyes')
 if 'joint' in name.lower() or 'burnished' in name.lower():return u.load_asset(base+'/Materials/MI_PolishedClay')
 if name=='ELR_StaffWood':return u.load_asset(base+'/Materials/MI_StaffWood')
 return u.load_asset(base+'/Materials/M_ClayBody')
try:
 skeleton=u.load_asset(base+'/Mesh/SK_ElrhunGolem_Skeleton')
 for role in globals().get('roles_to_import',['Tank','Mage','Ranger','Healer','Necromancer']):
  task=u.AssetImportTask();task.filename=str(sources/('SK_Golem_'+role+'.fbx'));task.destination_path=base+'/Mesh/Fitted';task.destination_name='SK_Golem_'+role
  task.automated=True;task.save=True;task.replace_existing=True
  opt=u.FbxImportUI();opt.automated_import_should_detect_type=False;opt.import_as_skeletal=True;opt.mesh_type_to_import=u.FBXImportType.FBXIT_SKELETAL_MESH
  opt.import_mesh=True;opt.import_animations=False;opt.import_materials=False;opt.import_textures=False;opt.create_physics_asset=False
  opt.set_editor_property('skeleton',skeleton);opt.skeletal_mesh_import_data.normal_import_method=u.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS
  task.options=opt;T.import_asset_tasks([task])
  mesh=next(u.load_asset(p) for p in task.imported_object_paths if isinstance(u.load_asset(p),u.SkeletalMesh))
  slots=list(mesh.get_editor_property('materials'));names=[];paths=[];gem=None
  for i,slot in enumerate(slots):
   name=str(slot.material_slot_name);names.append(name);material=resolve(name,role)
   if not material:raise RuntimeError('No material: '+role+' '+name)
   if 'Soul_gem' in name or 'Soul gem' in name:gem=i
   slot.set_editor_property('material_interface',material);slots[i]=slot;paths.append(material.get_path_name())
  assert gem is not None
  mesh.set_editor_property('materials',slots);settings=S.get_lod_build_settings(mesh,0);S.set_lod_build_settings(mesh,0,settings)
  A.save_loaded_asset(mesh,only_if_is_dirty=False)
  weapons=[]
  for i,item in enumerate(json.loads((sources/(role+'_attachments.json')).read_text())):
   task=u.AssetImportTask();task.filename=item['file'];task.destination_path=base+'/Equipment';task.destination_name='SM_'+item['name'];task.automated=True;task.save=True;task.replace_existing=True
   opt=u.FbxImportUI();opt.automated_import_should_detect_type=False;opt.import_as_skeletal=False;opt.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH
   opt.import_materials=False;opt.import_textures=False;opt.static_mesh_import_data.combine_meshes=True;opt.static_mesh_import_data.auto_generate_collision=True
   opt.static_mesh_import_data.normal_import_method=u.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;task.options=opt
   T.import_asset_tasks([task]);weapon=next(u.load_asset(p) for p in task.imported_object_paths if isinstance(u.load_asset(p),u.StaticMesh))
   for index,slot in enumerate(weapon.get_editor_property('static_materials')):
    mat=resolve(str(slot.material_slot_name),role);assert mat,(role,slot.material_slot_name)
    weapon.set_material(index,mat)
   A.save_loaded_asset(weapon,only_if_is_dirty=False)
   weapons.append({'mesh':weapon.get_path_name(),'bone':item['bone'],'name':item['name']})
  report['roles'][role]={'mesh':mesh.get_path_name(),'animation':base+'/Animations/A_Golem_EquippedIdle.A_Golem_EquippedIdle','gem_slot':gem,'slots':names,'materials':paths,'weapons':weapons,'vertices':S.get_num_verts(mesh,0)}
  (root/'Saved/golem_corrected_import.json').write_text(json.dumps(report,indent=2))
 report['success']=True
except Exception:report['error']=traceback.format_exc()
(root/'Saved/golem_corrected_import.json').write_text(json.dumps(report,indent=2))
