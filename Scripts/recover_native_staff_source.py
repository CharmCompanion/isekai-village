import unreal as u,json
from pathlib import Path
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');out=r/'ArtSource/Golems/NativeWeapons';source=u.load_asset('/Game/MageSet01/Weapons/Staff_01/SKM_Staff_01');report={'class':source.get_class().get_name(),'bow_support':u.get_default_object(u.GolemEquipmentActor).get_editor_property('animate_bow_string')}
if isinstance(source,u.SkeletalMesh):
 report['original']=json.loads(u.GolemClothTools.inspect_clothing(source));mesh=u.AssetToolsHelpers.get_asset_tools().duplicate_asset('SK_StaffExportCopy','/Game/Elrhun/Golems/PlayerBody/ClothingSources',source);u.GolemClothTools.reset_cape_cloth(mesh);task=u.AssetExportTask();task.object=mesh;task.filename=str(out/'Staff_Source.fbx');task.automated=True;task.prompt=False;task.replace_identical=True;task.exporter=u.SkeletalMeshExporterFBX();task.options=u.FbxExportOption();assert u.Exporter.run_asset_export_task(task);report['file']=task.filename
(out/'staff_source.json').write_text(json.dumps(report,indent=2))
