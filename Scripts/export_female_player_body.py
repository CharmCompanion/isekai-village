import unreal as u,json
from pathlib import Path
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');out=r/'ArtSource/Golems/PlayerBody';out.mkdir(parents=True,exist_ok=True)
mesh=u.load_asset('/Game/StylizedCharacters/BodyB/Body/SKM_BodyB');assert mesh
t=u.AssetExportTask();t.object=mesh;t.filename=str(out/'SKM_BodyB.fbx');t.automated=True;t.prompt=False;t.replace_identical=True;t.exporter=u.SkeletalMeshExporterFBX();t.options=u.FbxExportOption();t.options.level_of_detail=False;ok=u.Exporter.run_asset_export_task(t);assert ok
(r/'Saved/golem_female_body_source.json').write_text(json.dumps({'success':True,'source':mesh.get_path_name(),'skeleton':mesh.get_editor_property('skeleton').get_path_name(),'physics':mesh.get_editor_property('physics_asset').get_path_name() if mesh.get_editor_property('physics_asset') else None,'file':t.filename},indent=2))
