import unreal as u,json,traceback
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');base='/Game/Elrhun/Golems';report={'success':False}
try:
 task=u.AssetImportTask();task.filename=str(root/'ArtSource/Golems/CorrectedWardrobe/Golem_HandheldIdle.fbx');task.destination_path=base+'/Animations';task.destination_name='A_Golem_EquippedIdle';task.automated=True;task.save=True;task.replace_existing=True
 opt=u.FbxImportUI();opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=u.FBXImportType.FBXIT_ANIMATION;opt.import_as_skeletal=True;opt.import_mesh=False;opt.import_animations=True;opt.import_materials=False;opt.import_textures=False;opt.set_editor_property('skeleton',u.load_asset(base+'/Mesh/SK_ElrhunGolem_Skeleton'));task.options=opt
 u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task]);report['assets']=list(task.imported_object_paths);report['success']=bool(task.imported_object_paths)
except Exception:report['error']=traceback.format_exc()
(root/'Saved/golem_handheld_idle_import.json').write_text(json.dumps(report,indent=2))
