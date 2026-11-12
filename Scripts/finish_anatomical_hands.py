import unreal as u,json
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
system=u.get_editor_subsystem(u.EditorActorSubsystem)
a=next(a for a in system.get_all_level_actors() if a.get_actor_label()=='Golem Mage')
system.set_selected_level_actors([])
p=a.get_actor_location();eye=p+u.Vector(-18,-105,112)
u.EditorLevelLibrary.set_level_viewport_camera_info(eye,u.MathLibrary.find_look_at_rotation(eye,p+u.Vector(0,0,96)))
u.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
u.EditorLoadingAndSavingUtils.save_map(world,'/Game/Elrhun/Golems/Maps/Map_GolemSoulGems')
(root/'Saved/golem_anatomical_hands_complete.json').write_text(json.dumps({'saved':True,'palms':'anatomical connected clay hands','fingers':'webbed bases, knuckles and relaxed curl','holding_hands':'closed surfaces with handle clearance','variants':8,'bare_model':True}))
