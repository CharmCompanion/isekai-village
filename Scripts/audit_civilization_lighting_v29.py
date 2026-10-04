import unreal,json
from pathlib import Path
r=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if any(s in a.get_class().get_name() for s in ['SkyAtmosphere','DirectionalLight','SkyLight','PostProcess','ExponentialHeightFog']):
  q={'class':a.get_class().get_name(),'label':a.get_actor_label(),'location':str(a.get_actor_location())}
  for c in a.get_components_by_class(unreal.ActorComponent):
   if isinstance(c,unreal.LightComponent):q['light']={'intensity':c.get_editor_property('intensity'),'color':str(c.get_editor_property('light_color'))}
  r.append(q)
Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/civilization_lighting_v29.json').write_text(json.dumps(r,indent=2))
