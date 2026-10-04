import unreal,json
from pathlib import Path
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);d=[]
for a in E.get_all_level_actors():
 if isinstance(a,unreal.StaticMeshActor):
  c=a.static_mesh_component;o,e=a.get_actor_bounds(False);m=c.static_mesh
  if m and (max(e.x,e.y)>70000 or 'cloud' in m.get_name().lower()):d.append({'label':a.get_actor_label(),'mesh':m.get_path_name(),'folder':str(a.get_folder_path()),'visible':c.is_visible(),'hidden':a.get_editor_property('hidden'),'loc':[o.x,o.y,o.z],'extent':[e.x,e.y,e.z]})
Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/large_actor_audit.json').write_text(json.dumps(d,indent=2))
