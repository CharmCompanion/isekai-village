import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/ElRuhnSky02';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert 'Map_ElRuhnSky.' in W.get_path_name()
rows=[]
for a in E.get_all_level_actors():
 if str(a.get_folder_path())=='Village/Buildings':
  p=a.get_actor_location();o,e=a.get_actor_bounds(False);s=a.get_actor_scale3d();r=a.get_actor_rotation();rows.append({'label':a.get_actor_label(),'class':a.get_class().get_path_name(),'position':[p.x,p.y,p.z],'origin':[o.x,o.y,o.z],'extent':[e.x,e.y,e.z],'scale':[s.x,s.y,s.z],'rotation':[r.pitch,r.yaw,r.roll]})
(O/'building_native_audit.json').write_text(json.dumps(rows,indent=2))
unreal.SystemLibrary.execute_console_command(W,'Automation RunTests IsekaiVillage.Construction.AuthoredPlots')
