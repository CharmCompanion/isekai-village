import unreal as u,json
from pathlib import Path
data=[]
for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
 if isinstance(a,u.SkeletalMeshActor):
  c=a.get_editor_property('skeletal_mesh_component')
  a.set_actor_hidden_in_game(False);c.set_hidden_in_game(False)
  lo,ex=a.get_actor_bounds(False)
  data.append({'actor':a.get_actor_label(),'mesh':str(c.get_editor_property('skeletal_mesh_asset')),'hidden_ed':a.is_hidden_ed(),'visible':c.is_visible(),'bounds':str(ex),'scale':str(a.get_actor_scale3d()),'loc':str(a.get_actor_location()),'material':str(c.get_material(1))})
Path('D:/DEVELOPMENT/Games/Tower of Elrhun/Saved/golem_component_debug.json').write_text(json.dumps(data,indent=2))
