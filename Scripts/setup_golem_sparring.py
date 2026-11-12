from pathlib import Path
import json,shutil,unreal as u
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');backup=r/'Saved/VillageLoopBackup/Map_ElRuhnSky_BeforeSparring.umap'
if not backup.exists():shutil.copy2(r/'Content/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky.umap',backup)
w=u.EditorLoadingAndSavingUtils.load_map('/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky')
e=u.get_editor_subsystem(u.EditorActorSubsystem);v=next(a for a in e.get_all_level_actors() if isinstance(a,u.VillageRuntime))
cls=u.load_class(None,'/Game/IsekaiVillage/Magic/Slimes/BP_WaterSlimeMage.BP_WaterSlimeMage_C');assert cls
v.modify();v.set_editor_property('sparring_slime_class',cls)
assert u.EditorLoadingAndSavingUtils.save_map(w,'/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky')
(r/'Saved/golem_sparring_setup.json').write_text(json.dumps({'success':True,'map':w.get_path_name(),'slime':cls.get_path_name(),'normal_slot':str(v.construction_save_slot)}))
