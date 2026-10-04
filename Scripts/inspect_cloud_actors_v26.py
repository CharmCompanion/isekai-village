import unreal,json
from pathlib import Path
out=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if any(q in (a.get_actor_label()+' '+a.get_class().get_name()).lower() for q in ['cloud','sky','fog']):
  out.append({'label':a.get_actor_label(),'class':a.get_class().get_name(),'path':a.get_path_name(),'location':str(a.get_actor_location()),'tags':[str(t) for t in a.tags]})
Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/sky_actor_inspect.json').write_text(json.dumps(out,indent=2))
