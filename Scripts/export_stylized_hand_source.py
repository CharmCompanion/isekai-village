import unreal as u,json
from pathlib import Path
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
asset=u.load_asset('/Game/StylizedCharacters/BodyA/Body/SKM_BodyA_hands')
task=u.AssetExportTask();task.object=asset;task.filename=str(r/'ArtSource/Golems/WardrobeSources/SKM_BodyA_hands.fbx');task.automated=True;task.prompt=False;task.replace_identical=True;task.exporter=u.SkeletalMeshExporterFBX();task.options=u.FbxExportOption();task.options.ascii=False;task.options.level_of_detail=False
ok=u.Exporter.run_asset_export_task(task)
(r/'Saved/golem_hand_donor_export.json').write_text(json.dumps({'success':ok,'file':task.filename}))
