import unreal as u,json,traceback
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');base='/Game/Elrhun/Golems';src=root/'ArtSource/Golems/HandheldEquipment'
manifest=json.loads((src/'manifest.json').read_text());mapping=json.loads((src.parent/'CorrectedWardrobe/material_paths.json').read_text())
T=u.AssetToolsHelpers.get_asset_tools();A=u.EditorAssetLibrary;M=u.MaterialEditingLibrary
report={'success':False,'items':{}}
try:
 data=json.loads((root/'Saved/golem_corrected_import.json').read_text())
 leather=u.load_asset(base+'/Materials/MI_GripLeather')
 if not leather:
  leather=T.create_asset('MI_GripLeather',base+'/Materials',u.MaterialInstanceConstant,u.MaterialInstanceConstantFactoryNew());M.set_material_instance_parent(leather,u.load_asset(base+'/Materials/M_ClayBody'));M.set_material_instance_vector_parameter_value(leather,'BodyColor',u.LinearColor(.055,.024,.012,1));A.save_loaded_asset(leather)
 linen=u.load_asset(base+'/Materials/MI_HealerLinen') or T.create_asset('MI_HealerLinen',base+'/Materials',u.MaterialInstanceConstant,u.MaterialInstanceConstantFactoryNew())
 M.set_material_instance_parent(linen,u.load_asset(base+'/Materials/M_ClayBody'));M.set_material_instance_vector_parameter_value(linen,'BodyColor',u.LinearColor(.88,.80,.60,1));A.save_loaded_asset(linen)
 def import_item(item):
  task=u.AssetImportTask();task.filename=item['file'];task.destination_path=base+'/Equipment/Handheld';task.destination_name='SM_'+item['name'];task.automated=True;task.save=True;task.replace_existing=True
  opt=u.FbxImportUI();opt.automated_import_should_detect_type=False;opt.import_as_skeletal=False;opt.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH;opt.import_materials=False;opt.import_textures=False;opt.static_mesh_import_data.combine_meshes=True;opt.static_mesh_import_data.auto_generate_collision=False;opt.static_mesh_import_data.normal_import_method=u.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;task.options=opt
  T.import_asset_tasks([task]);mesh=next(u.load_asset(p) for p in task.imported_object_paths if isinstance(u.load_asset(p),u.StaticMesh))
  for i,slot in enumerate(mesh.get_editor_property('static_materials')):
   name=str(slot.material_slot_name)
   mat=leather if name=='ELR_GripLeather' else linen if name=='ELR_HealerLinen' else u.load_asset(base+'/Materials/MI_DarkEyes') if name=='ELR_EvilBrows' else u.load_asset(mapping[name])
   assert mat,(item,name);mesh.set_material(i,mat)
  if item['name']!='Golem_EvilBrows' and not item['name'].startswith('Healer_Linen_'):assert u.GolemClothTools.ensure_weapon_collision(mesh)>0,item
  A.save_loaded_asset(mesh,only_if_is_dirty=False)
  return {'mesh':mesh.get_path_name(),'bone':item['bone'],'name':item['name']}
 for role,items in manifest.items():
  if role=='HealerUnderlay':
   data.setdefault('accessories',{})['HealerUnderlay']=[import_item(item) for item in items];continue
  if role=='EvilBrows':
   data.setdefault('accessories',{})['EvilBrows']=import_item(items);continue
  data['roles'][role]['weapons']=[import_item(item) for item in items];report['items'][role]=data['roles'][role]['weapons']
 (root/'Saved/golem_corrected_import.json').write_text(json.dumps(data,indent=2));report['success']=True
except Exception:report['error']=traceback.format_exc()
(root/'Saved/golem_handheld_import.json').write_text(json.dumps(report,indent=2))
