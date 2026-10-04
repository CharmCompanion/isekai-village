import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');data=json.loads((B/'Saved/AdventureWorldSource/civilization_instances_v30.json').read_text());counts={};old=0
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
  mesh=c.static_mesh
  if not mesh:continue
  n=mesh.get_name();count=c.get_instance_count()
  if n.startswith('SM_Civ30_'):counts[n]=counts.get(n,0)+count
  if n.startswith('SM_Civ29_'):old+=count
for key in ['SM_Civ30_Cathedral','SM_Civ30_ArcaneTower','SM_Civ30_Sanctuary','SM_Civ30_Gatehouse','SM_Civ30_StiltHouse']:
 assert counts.get(key,0)==len(data['instances'][key]),(key,counts.get(key,0),len(data['instances'][key]))
assert old==0,old
r={'native_counts':counts,'old_regional_instances':old,'level_saved':unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()}
(B/'Saved/civilization_native_validation_v30.json').write_text(json.dumps(r,indent=2))
