import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');counts={}
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
  mesh=c.static_mesh
  if not mesh:continue
  n=mesh.get_name()
  if n.startswith('SM_Civ29_'):counts[n]=counts.get(n,0)+c.get_instance_count()
assert counts.get('SM_Civ29_Cathedral',0)==7
assert counts.get('SM_Civ29_ArcaneTower',0)==6
assert counts.get('SM_Civ29_Sanctuary',0)==2
assert counts.get('SM_Civ29_Gatehouse',0)==10
r={'native_counts':counts,'level_saved':unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()}
(B/'Saved/civilization_native_validation_v29.json').write_text(json.dumps(r,indent=2))
