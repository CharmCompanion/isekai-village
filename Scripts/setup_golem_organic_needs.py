from pathlib import Path
import json,unreal as u
w=u.EditorLoadingAndSavingUtils.load_map('/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky')
e=u.get_editor_subsystem(u.EditorActorSubsystem);v=next(a for a in e.get_all_level_actors() if isinstance(a,u.VillageRuntime))
v.modify();v.set_editor_property('use_organic_golem_needs',True)
assert u.EditorLoadingAndSavingUtils.save_map(w,'/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky')
Path('D:/DEVELOPMENT/Games/Tower of Elrhun/Saved/golem_organic_setup.json').write_text(json.dumps({'success':True,'map':w.get_path_name(),'organic_needs':True}))
