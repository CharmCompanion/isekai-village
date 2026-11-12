import unreal as u,json,traceback
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
r={}
try:
 task=u.AssetImportTask();task.filename=str(root/'ArtSource/Golems/FittedWardrobe/SK_Golem_Tank_Equipped.fbx')
 task.destination_path='/Game/Elrhun/Golems/Animations';task.destination_name='A_Golem_EquippedIdle';task.automated=True;task.save=True;task.replace_existing=True
 opt=u.FbxImportUI();opt.automated_import_should_detect_type=False;opt.import_mesh=False;opt.import_animations=True;opt.import_materials=False;opt.import_textures=False
 opt.mesh_type_to_import=u.FBXImportType.FBXIT_ANIMATION
 opt.set_editor_property('skeleton',u.load_asset('/Game/Elrhun/Golems/Mesh/SK_ElrhunGolem_Skeleton'));task.options=opt
 u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
 paths=list(task.imported_object_paths)
 anims=[u.load_asset(p) for p in paths if isinstance(u.load_asset(p),u.AnimSequence)]
 assert anims,paths
 info=json.loads((root/'Saved/golem_equipped_import.json').read_text())
 for role in info['roles'].values():role['animation']=anims[0].get_path_name()
 (root/'Saved/golem_equipped_import.json').write_text(json.dumps(info,indent=2))
 r={'success':True,'animation':anims[0].get_path_name()}
except Exception:r={'success':False,'error':traceback.format_exc()}
(root/'Saved/golem_equipped_idle.json').write_text(json.dumps(r,indent=2))
if r.get('success'):
 exec(compile((root/'Scripts/setup_golem_equipment.py').read_text(),str(root/'Scripts/setup_golem_equipment.py'),'exec'),{'__name__':'__main__'})
