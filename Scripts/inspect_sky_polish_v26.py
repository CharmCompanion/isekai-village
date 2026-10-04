import unreal,json
from pathlib import Path
out=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh:
  m=a.static_mesh_component.static_mesh;name=m.get_name()
  if 'cloud' in name.lower() or 'sky' in name.lower():
   out.append({'label':a.get_actor_label(),'mesh':name,'path':a.get_path_name(),'location':str(a.get_actor_location()),'scale':str(a.get_actor_scale3d()),'visible':a.static_mesh_component.is_visible(),'tags':[str(t) for t in a.tags]})
Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/sky_polish_inspect.json').write_text(json.dumps(out,indent=2))
