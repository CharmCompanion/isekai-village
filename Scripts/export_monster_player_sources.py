"""Export local references from a rendering editor; never modifies pack assets."""
import unreal,json
from pathlib import Path
out=Path('D:/DEVELOPMENT/Games/IsekaiVillage/ArtSource/Monsters/PlayerReference')
out.mkdir(parents=True,exist_ok=True)
rows=[]
paths=['/Game/StylizedCharacters/BodyA/Body/SKM_BodyA','/Game/StylizedCharacters/BodyA/Heads/Head_01/SKM_HeadA_01']
for path in paths:
    mesh=unreal.load_asset(path)
    assert mesh,path
    task=unreal.AssetExportTask()
    task.object=mesh
    task.filename=str(out/(mesh.get_name()+'.fbx'))
    task.automated=True
    task.prompt=False
    task.replace_identical=True
    task.exporter=unreal.SkeletalMeshExporterFBX()
    task.options=unreal.FbxExportOption()
    task.options.set_editor_property('level_of_detail',False)
    ok=unreal.Exporter.run_asset_export_task(task)
    rows.append({'asset':path,'exported':bool(ok),'file':task.filename,'skeleton':mesh.get_editor_property('skeleton').get_path_name()})
(out/'export_report.json').write_text(json.dumps(rows,indent=2))
tex=unreal.load_asset('/Game/StylizedCharacters/BodyA/Eyes/Eyes_01/Textures/T_Eye_01_Grayscale')
if tex:
    task=unreal.AssetExportTask();task.object=tex;task.filename=str(out/'T_Eye_01_Grayscale.png');task.automated=True;task.prompt=False;task.replace_identical=True;task.exporter=unreal.TextureExporterPNG()
    unreal.Exporter.run_asset_export_task(task)
