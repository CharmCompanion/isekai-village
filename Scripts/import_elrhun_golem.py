import unreal as u,json,traceback
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
target='/Game/Elrhun/Golems'
tools=u.AssetToolsHelpers.get_asset_tools()
report={}
try:
 task=u.AssetImportTask()
 task.filename=str(root/'ArtSource/Golems/Elrhun_SoulSocket_Golem.fbx')
 task.destination_path=target+'/Mesh'
 task.destination_name='SK_ElrhunGolem'
 task.automated=True;task.save=True;task.replace_existing=False
 options=u.FbxImportUI()
 options.automated_import_should_detect_type=False
 options.import_as_skeletal=True
 options.mesh_type_to_import=u.FBXImportType.FBXIT_SKELETAL_MESH
 options.import_mesh=True;options.import_animations=True
 options.import_materials=False;options.import_textures=False

 options.skeletal_mesh_import_data.normal_import_method=u.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS
 task.options=options
 tools.import_asset_tasks([task])
 report['imported']=list(task.imported_object_paths)
 meshes=[u.load_asset(p) for p in task.imported_object_paths if isinstance(u.load_asset(p),u.SkeletalMesh)]
 assert meshes,'No skeletal mesh imported'
 mesh=meshes[0]
 report['mesh']=mesh.get_path_name()
 report['material_slots']=[str(m.material_slot_name) for m in mesh.get_editor_property('materials')]
 report['animations']=[p for p in task.imported_object_paths if isinstance(u.load_asset(p),u.AnimSequence)]
 report['success']=True
except Exception:
 report['success']=False;report['error']=traceback.format_exc()
finally:
 (root/'Saved').mkdir(exist_ok=True)
 (root/'Saved/golem_import_report.json').write_text(json.dumps(report,indent=2))
 u.log('GOLEM_IMPORT_REPORT '+json.dumps(report))

if report.get('success'):
 exec(compile((root/'Scripts/setup_elrhun_soul_golems.py').read_text(),str(root/'Scripts/setup_elrhun_soul_golems.py'),'exec'),{'__name__':'__main__'})

