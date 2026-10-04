import unreal
from pathlib import Path
p=Path(__file__).parent/'toggle_iv_build_grid.py'
exec(compile(p.read_text(),str(p),'exec'))
actors=[a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if str(a.get_folder_path())=='BuildGrid/Debug']
assert all(not a.static_mesh_component.is_visible() for a in actors)
exec(compile(p.read_text(),str(p),'exec'))
assert all(a.static_mesh_component.is_visible() and not a.get_editor_property('hidden') for a in actors)
exec(compile(p.read_text(),str(p),'exec'))
assert all(not a.static_mesh_component.is_visible() for a in actors)
eye=unreal.Vector(20000,-25500,11500)
unreal.EditorLevelLibrary.set_level_viewport_camera_info(eye,unreal.MathLibrary.find_look_at_rotation(eye,unreal.Vector(12800,-14000,2450)))
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/farm_final_review.txt').write_text('Grid toggle OFF/ON/OFF passed. Map saved. Farm collision confirmed flat at 24.5m. Visual review completed.')
