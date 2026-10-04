import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage')
native=json.loads((B/'Saved/valley_native_validation.json').read_text())
join=json.loads((B/'Saved/join_validation.json').read_text())
renders=json.loads((B/'Saved/valley_origin_render.json').read_text())
assert native['all_height_checks_pass']
assert join['all_768_join_checks_pass'] and join['all_96_underside_checks_pass']
assert renders['stage']=='complete' and len(renders['completed'])==6
eye=unreal.Vector(85000,-128000,44000);target=unreal.Vector(0,3000,-19000)
unreal.EditorLevelLibrary.set_level_viewport_camera_info(eye,unreal.MathLibrary.find_look_at_rotation(eye,target))
saved=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
assert saved
(B/'Saved/valley_origin_delivery.json').write_text(json.dumps({'saved':saved,'map':'/Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure','native_height_checks':18,'perimeter_checks':768,'underside_checks':96,'reviewed_views':6,'full_character_traversal_tested':False,'notes':'Docs/WorldDesign/Valley_And_Origin_v14.md'},indent=2))
unreal.SystemLibrary.execute_console_command(unreal.EditorLevelLibrary.get_editor_world(),'QUIT_EDITOR')
