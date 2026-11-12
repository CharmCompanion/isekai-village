"""Apply the previewed shared sky correction only after specific user approval."""
import unreal,json,shutil,time
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain58';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert json.loads((O/'atmosphere_approval.json').read_text())['approved'] is True
assert not (O/'atmosphere_applied.json').exists()
assert json.loads((B/'Docs/WorldDesign/Gosain58_AtmosphereStudy/comparison_complete.json').read_text())['restored']
W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert W.get_path_name().startswith('/Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.')
sky=next(a for a in E.get_all_level_actors() if isinstance(a,unreal.SkyAtmosphere));old=sky.get_actor_location();assert abs(old.z+25000.)<1
backup=B/'Saved/WorldBackups'/('BeforeGosain58Atmosphere_'+time.strftime('%Y%m%d_%H%M%S'));backup.mkdir(parents=True);shutil.copy2(B/'Content/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.umap',backup/'Map_AnimeAdventure.umap')
try:
 sky.set_actor_location(unreal.Vector(old.x,old.y,-2060000.),False,False)
 assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception:sky.set_actor_location(old,False,False);raise
(O/'atmosphere_applied.json').write_text(json.dumps({'status':'saved','backup':str(backup),'old_location_cm':[old.x,old.y,old.z],'new_location_cm':[old.x,old.y,-2060000.],'effect':'shared atmospheric scattering; El Ruhn appearance changes as shown in approved comparison','geometry_materials_fog_unchanged':True},indent=2))
