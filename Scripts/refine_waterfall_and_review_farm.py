import unreal
from pathlib import Path
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
fall=next(a for a in E.get_all_level_actors() if a.get_actor_label()=='Veil Falls - Hidden Dungeon Approach')
fall.set_actor_location(unreal.Vector(-34900,27220,7880),False,False)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
unreal.AutomationLibrary.take_high_res_screenshot(1600,900,'D:/DEVELOPMENT/Games/IsekaiVillage/Docs/WorldDesign/Waterfall_Review.png',delay=1.)
