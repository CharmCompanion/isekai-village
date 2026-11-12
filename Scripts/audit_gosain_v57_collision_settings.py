import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain57';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors=E.get_all_level_actors();rows=[]
for a in actors:
 if not isinstance(a,unreal.StaticMeshActor):continue
 c=a.static_mesh_component;m=c.static_mesh
 if not m:continue
 if m.get_name() not in ['SM_IV_Continent_GosainMine57','SM_Gosain57_MineLandformFinal','SM_Gosain57_KingdomRoutesRefined']:continue
 b=m.get_editor_property('body_setup');rows.append({'actor':a.get_name(),'mesh':m.get_name(),'actor_collision':a.get_actor_enable_collision(),'component_collision':str(c.get_collision_enabled()),'profile':str(c.get_collision_profile_name()),'trace_flag':str(b.get_editor_property('collision_trace_flag')),'response_visibility':str(c.get_collision_response_to_channel(unreal.CollisionChannel.ECC_VISIBILITY))})
(O/'collision_settings.json').write_text(json.dumps(rows,indent=2))
