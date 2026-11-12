import unreal as u,json,traceback
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');base='/Game/Elrhun/Golems';source=root/'ArtSource/Golems/HandheldEquipment/Golem_ClosedGrip_Library.fbx'
report={'success':False,'assets':[],'roles':{}}
try:
 world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
 u.SystemLibrary.execute_console_command(world,'Interchange.FeatureFlags.Import.FBX 0')
 data=json.loads((root/'Saved/golem_corrected_import.json').read_text())
 for role in ['Tank','Mage','Ranger','Healer','Necromancer']:
  clips={}
  for kind in ['GripIdle','GripCheck']:
   task=u.AssetImportTask();task.filename=str(source.parent/('Golem_'+kind+'_'+role+'.fbx'));task.destination_path=base+'/Animations/ClosedGrip';task.destination_name='A_Golem_'+kind+'_'+role;task.automated=True;task.save=True;task.replace_existing=True;task.factory=u.FbxFactory()
   opt=u.FbxImportUI();opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=u.FBXImportType.FBXIT_ANIMATION;opt.import_as_skeletal=True;opt.import_mesh=False;opt.import_animations=True;opt.import_materials=False;opt.import_textures=False;opt.set_editor_property('skeleton',u.load_asset(base+'/Mesh/SK_ElrhunGolem_Skeleton'));task.options=opt
   u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task]);report['assets'].extend(task.imported_object_paths)
   clips[kind]=next((u.load_asset(p) for p in task.imported_object_paths if isinstance(u.load_asset(p),u.AnimSequence)),None)
  idle=clips['GripIdle'];check=clips['GripCheck'];assert idle and check,(role,report['assets'])
  data['roles'][role]['animation']=idle.get_path_name();data['roles'][role]['grip_check_animation']=check.get_path_name();report['roles'][role]={'idle':idle.get_path_name(),'check':check.get_path_name()}
 (root/'Saved/golem_corrected_import.json').write_text(json.dumps(data,indent=2));report['success']=True
except Exception:report['error']=traceback.format_exc()
finally:u.SystemLibrary.execute_console_command(u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world(),'Interchange.FeatureFlags.Import.FBX 1')
(root/'Saved/golem_closed_grip_import.json').write_text(json.dumps(report,indent=2))
