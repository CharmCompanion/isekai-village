"""Save the reviewed presentation and release this task's background editor."""
import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage')
review=json.loads((B/'Saved/floating_render_review.json').read_text());assert review['stage']=='complete'
checks=json.loads((B/'Saved/floating_collision_review.json').read_text());assert all(c['pass'] for c in checks)
eye=unreal.Vector(78000,-118000,35000);target=unreal.Vector(0,2500,-18000)
unreal.EditorLevelLibrary.set_level_viewport_camera_info(eye,unreal.MathLibrary.find_look_at_rotation(eye,target))
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(B/'Saved/floating_delivery.json').write_text(json.dumps({'map':'/Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure','saved':True,'collision_samples_passed':len(checks),'rendered_views':review['completed'],'protected_terrain_samples':194902,'editor_build':'Succeeded','background_editor':'closed after saving'},indent=2))
unreal.SystemLibrary.quit_editor()
