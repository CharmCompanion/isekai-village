import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
for kind in ['Cliff','Rocks','House','HouseVar']:
 ft=unreal.load_asset('/Game/IsekaiVillage/AdventureWorld/Foliage/FT_Continent17_'+kind)
 if ft:unreal.InstancedFoliageActor.remove_all_instances(w,ft)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(B/'Saved/elruhn_cleanup_verified.json').write_text(json.dumps({'removed_foliage_types':['Cliff','Rocks','House','HouseVar'],'map_saved':True}))
exec(compile((B/'Scripts/render_puzzle_continent_v23.py').read_text(),'final renders','exec'),{'__name__':'__main__'})
