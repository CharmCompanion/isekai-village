import unreal as u,json,traceback,time
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');base='/Game/Elrhun/Golems'
sources=root/'ArtSource/Golems/FittedWardrobe'
mapping=json.loads((sources/'material_paths.json').read_text())
T=u.AssetToolsHelpers.get_asset_tools();A=u.EditorAssetLibrary;M=u.MaterialEditingLibrary
report={'roles':{},'success':False}
try:
 skeleton=u.load_asset(base+'/Mesh/SK_ElrhunGolem_Skeleton')
 for role in ['Tank','Mage','Ranger','Healer','Necromancer']:
  task=u.AssetImportTask();task.filename=str(sources/('SK_Golem_'+role+'.fbx'));task.destination_path=base+'/Mesh/Clothed';task.destination_name='SK_Golem_'+role
  task.automated=True;task.save=True;task.replace_existing=True
  opt=u.FbxImportUI();opt.automated_import_should_detect_type=False;opt.import_as_skeletal=True;opt.mesh_type_to_import=u.FBXImportType.FBXIT_SKELETAL_MESH
  opt.import_mesh=True;opt.import_animations=True;opt.import_materials=False;opt.import_textures=False
  opt.set_editor_property('skeleton',skeleton);opt.skeletal_mesh_import_data.normal_import_method=u.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS
  task.options=opt;T.import_asset_tasks([task])
  imported=[u.load_asset(p) for p in task.imported_object_paths]
  mesh=next(o for o in imported if isinstance(o,u.SkeletalMesh))
  anim=next((o for o in imported if isinstance(o,u.AnimSequence)),None)
  slots=list(mesh.get_editor_property('materials'));slot_names=[];gem_slot=None
  resolved=[]
  for i,slot in enumerate(slots):
   name=str(slot.material_slot_name);slot_names.append(name)
   if name in mapping:material=u.load_asset(mapping[name]) if mapping[name] else None
   elif 'Soul_gem' in name or 'Soul gem' in name:material=u.load_asset(base+'/Materials/MI_SoulGem_'+role);gem_slot=i
   elif 'Dark_glossy' in name or 'Obsidian' in name:material=u.load_asset(base+'/Materials/MI_DarkEyes')
   elif 'joint' in name.lower() or 'burnished' in name.lower():material=u.load_asset(base+'/Materials/MI_PolishedClay')
   elif name=='ELR_StaffWood':
    material=u.load_asset(base+'/Materials/MI_StaffWood')
    if not material:
     material=T.create_asset('MI_StaffWood',base+'/Materials',u.MaterialInstanceConstant,u.MaterialInstanceConstantFactoryNew())
     M.set_material_instance_parent(material,u.load_asset(base+'/Materials/M_ClayBody'))
     M.set_material_instance_vector_parameter_value(material,'BodyColor',u.LinearColor(.10,.045,.018,1));A.save_loaded_asset(material)
   else:material=u.load_asset(base+'/Materials/M_ClayBody')
   if not material:raise RuntimeError('Unresolved material '+role+' '+name)
   slot.set_editor_property('material_interface',material);slots[i]=slot;resolved.append(material.get_path_name())
  assert gem_slot is not None,(role,slot_names)
  mesh.set_editor_property('materials',slots)
  sub=u.get_editor_subsystem(u.SkeletalMeshEditorSubsystem)
  settings=sub.get_lod_build_settings(mesh,0);sub.set_lod_build_settings(mesh,0,settings)
  A.save_loaded_asset(mesh,only_if_is_dirty=False)
  report['roles'][role]={'mesh':mesh.get_path_name(),'animation':anim.get_path_name() if anim else None,'gem_slot':gem_slot,'slots':slot_names,'materials':resolved,'vertices':sub.get_num_verts(mesh,0)}
  (root/'Saved/golem_clothed_import.json').write_text(json.dumps(report,indent=2))
 report['success']=True
except Exception:report['error']=traceback.format_exc()
(root/'Saved/golem_clothed_import.json').write_text(json.dumps(report,indent=2))
