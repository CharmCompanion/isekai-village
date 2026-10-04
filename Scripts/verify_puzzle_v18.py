import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
rows=[]
for a in actors:
 if isinstance(a,unreal.StaticMeshActor):
  m=a.static_mesh_component.static_mesh
  if m and m.get_name() in ['SM_IV_JoinedMountain_v13','SM_IV_PuzzleContinent_v18']:
   bb=m.get_bounding_box()
   rows.append(dict(mesh=m.get_name(),visible=a.static_mesh_component.is_visible(),location=str(a.get_actor_location()),rotation=str(a.get_actor_rotation()),scale=str(a.get_actor_scale3d()),bounds_min=str(bb.min),bounds_max=str(bb.max)))
houses=[]
for a in actors:
 if isinstance(a,unreal.InstancedFoliageActor):
  for c in a.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent):
   if c.static_mesh and c.static_mesh.get_name() in ['SM_House_Var01','SM_House_Var02']:
    houses.append(dict(mesh=c.static_mesh.get_name(),count=c.get_instance_count()))
(B/'Saved/puzzle_native_review.json').write_text(json.dumps(dict(meshes=rows,house_components=houses),indent=2))
