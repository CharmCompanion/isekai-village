import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in E.get_all_level_actors():
 if 'IVRemnant22' in [str(t) for t in a.tags]:E.destroy_actor(a)
meshes={i:unreal.load_asset('/Game/SoStylized/Environment/Rocks/Spire/SM_RockSpire_Spire'+str(i).zfill(2)) for i in range(1,5)}
for x,y,z,h,yaw,kind in json.loads((B/'Saved/AdventureWorldSource/terrain_remnants_v22.json').read_text()):
 m=meshes[kind];assert m
 bb=m.get_bounding_box();s=h*100/(bb.max.z-bb.min.z)
 a=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(x*100,y*100,z*100-bb.min.z*s-h*38),unreal.Rotator(yaw=yaw))
 a.static_mesh_component.set_static_mesh(m);a.set_actor_scale3d(unreal.Vector(s*1.8,s*1.45,s));a.set_actor_enable_collision(False)
 a.tags=[unreal.Name('IVRemnant22')];a.set_folder_path('ContinentalWorld/Remaining mountain branches');a.set_actor_label('Bedrock remaining along the island mountain ridge')
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
