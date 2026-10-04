import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');rows=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if isinstance(a,unreal.StaticMeshActor):
  c=a.static_mesh_component;m=c.static_mesh
  if m and c.is_visible() and m.get_name() in ['SM_IV_PuzzleContinent_v19','SM_IV_PuzzleContinent_v20','SM_IV_ContinentWater_v17','SM_IV_ContinentWater_v20','SM_IV_JoinedMountain_v13']:
   rows.append(dict(mesh=m.get_name(),location=str(a.get_actor_location()),scale=str(a.get_actor_scale3d()),rotation=str(a.get_actor_rotation()),material=c.get_material(0).get_path_name()))
assert {r['mesh'] for r in rows}=={'SM_IV_PuzzleContinent_v20','SM_IV_ContinentWater_v20','SM_IV_JoinedMountain_v13'},rows
(B/'Saved/watershed_native_review_v20.json').write_text(json.dumps(rows,indent=2))
