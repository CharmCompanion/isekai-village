import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage')
render=json.loads((B/'Saved/living_world_render.json').read_text());close=json.loads((B/'Saved/living_world_close_render.json').read_text())
assert render['stage']=='complete' and close['stage']=='complete'
native=json.loads((B/'Saved/valley_native_validation.json').read_text());join=json.loads((B/'Saved/join_validation.json').read_text())
assert native['all_height_checks_pass'] and join['all_768_join_checks_pass'] and join['all_96_underside_checks_pass']
eye=unreal.Vector(85000,-128000,44000);target=unreal.Vector(0,3000,-19000)
unreal.EditorLevelLibrary.set_level_viewport_camera_info(eye,unreal.MathLibrary.find_look_at_rotation(eye,target));assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(B/'Saved/living_world_delivery.json').write_text(json.dumps({'saved':True,'trees':46000,'rock_clusters':2200,'outcrops':185,'houses':108,'water_surface':True,'island_checks_pass':True,'full_character_traversal_tested':False,'packaged_performance_tested':False},indent=2))
unreal.SystemLibrary.execute_console_command(unreal.EditorLevelLibrary.get_editor_world(),'QUIT_EDITOR')
