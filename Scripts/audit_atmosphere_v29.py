import unreal,json
from pathlib import Path
r={}
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if isinstance(a,unreal.SkyAtmosphere):
  c=a.get_component_by_class(unreal.SkyAtmosphereComponent)
  for key in ['transform_mode','bottom_radius','atmosphere_height','aerial_perspective_view_distance_scale','aerial_perspective_start_depth']:
   try:r[key]=str(c.get_editor_property(key))
   except Exception as e:r[key]=str(e)
Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/atmosphere_audit_v29.json').write_text(json.dumps(r,indent=2))
