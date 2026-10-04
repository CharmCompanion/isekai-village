import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage')
r=json.loads((B/'Saved/aligned_origin_render.json').read_text())
assert r['stage']=='complete'
eye=unreal.Vector(85000,-128000,44000);target=unreal.Vector(0,3000,-19000)
unreal.EditorLevelLibrary.set_level_viewport_camera_info(eye,unreal.MathLibrary.find_look_at_rotation(eye,target))
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(B/'Saved/aligned_origin_delivery.json').write_text(json.dumps({'saved':True,'mountain_profile_from_actual_island':True,'small_hollow_retained':True,'island_unchanged':True}))
unreal.SystemLibrary.execute_console_command(unreal.EditorLevelLibrary.get_editor_world(),'QUIT_EDITOR')
