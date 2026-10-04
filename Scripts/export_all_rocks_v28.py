import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');root='/Game/SoStylized/Environment/Rocks';paths=[root+'/Classic/SM_CliffClassic1',root+'/Spire/SM_RockSpire_RockClump02',root+'/Spire/SM_RockSpire_RockClumpB03'];out={}
for path in paths:
 m=unreal.load_asset(path);box=m.get_bounding_box();out[m.get_name()]={'path':path,'min':[box.min.x,box.min.y,box.min.z],'max':[box.max.x,box.max.y,box.max.z],'materials':[str(q.material_interface.get_path_name()) if q.material_interface else None for q in m.static_materials]}
 t=unreal.AssetExportTask();t.object=m;t.filename=str(B/'Saved/AdventureWorldSource'/(m.get_name()+'_source_v28.obj'));t.automated=True;t.prompt=False;t.exporter=unreal.StaticMeshExporterOBJ();assert unreal.Exporter.run_asset_export_task(t)
(B/'Saved/rock_sources_v28.json').write_text(json.dumps(out,indent=2))
