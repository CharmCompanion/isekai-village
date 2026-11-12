import unreal as u,json
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
a=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Golem Evil_Crimson')
loc=a.get_actor_location();eye=loc+u.Vector(-40,-150,130);look=loc+u.Vector(0,0,96)
u.EditorLevelLibrary.set_level_viewport_camera_info(eye,u.MathLibrary.find_look_at_rotation(eye,look))
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
u.EditorLoadingAndSavingUtils.save_map(world,'/Game/Elrhun/Golems/Maps/Map_GolemSoulGems')
(root/'Saved/golem_handheld_complete.json').write_text(json.dumps({'saved':True,'review':'Golem Evil_Crimson','handheld_weapons':True,'evil_eyebrows':True,'cloth_scale_fixed':True}))
