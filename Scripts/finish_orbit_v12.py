import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage')
r=json.loads((B/'Saved/orbit_after_review.json').read_text());v=json.loads((B/'Saved/orbit_validation.json').read_text())
assert r['stage']=='complete' and len(r['completed'])==14
assert v['all_48_radial_checks_pass'] and v['native_terrain_checks_pass'] and not v['visible_legacy_undersides']
eye=unreal.Vector(85000,-128000,44000);target=unreal.Vector(0,3000,-19000)
unreal.EditorLevelLibrary.set_level_viewport_camera_info(eye,unreal.MathLibrary.find_look_at_rotation(eye,target))
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(B/'Saved/orbit_delivery.json').write_text(json.dumps({'saved':True,'reviewed_views':r['completed'],'radial_checks':48,'native_height_checks':18,'terrain_heights_unchanged':True,'full_character_traversal_tested':False},indent=2))
unreal.SystemLibrary.quit_editor()
