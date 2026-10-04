import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');counts={};meshes={}
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
  m=c.static_mesh
  if m and any(q in m.get_name().lower() for q in ['rock','cliff','spire']):
   count=c.get_instance_count()
   if count:counts[m.get_path_name()]=counts.get(m.get_path_name(),0)+count;meshes[m.get_path_name()]=m
(B/'Saved/rock_foliage_audit_v28.json').write_text(json.dumps(counts,indent=2))
m=unreal.load_asset('/Game/SoStylized/Environment/Rocks/Classic/SM_CliffClassic1');t=unreal.AssetExportTask();t.object=m;t.filename=str(B/'Saved/AdventureWorldSource/SM_CliffClassic1_source_v28.obj');t.automated=True;t.prompt=False;t.exporter=unreal.StaticMeshExporterOBJ();result=unreal.Exporter.run_asset_export_task(t);unreal.log('cliff_export_v28 '+str(result))
