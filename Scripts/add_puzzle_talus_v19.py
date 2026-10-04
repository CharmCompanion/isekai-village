import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');R='/Game/IsekaiVillage/AdventureWorld';A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
path=R+'/Foliage/FT_PuzzleTalus19'
ft=unreal.load_asset(path) if A.does_asset_exist(path) else T.create_asset('FT_PuzzleTalus19',R+'/Foliage',unreal.FoliageType_InstancedStaticMesh,unreal.FoliageType_InstancedStaticMeshFactory())
m=unreal.load_asset('/Game/SoStylized/Environment/Rocks/Spire/SM_RockSpire_RockClump02');ft.set_editor_property('mesh',m);ft.set_editor_property('cast_shadow',False);ft.set_editor_property('cull_distance',unreal.Int32Interval(min=0,max=0));A.save_loaded_asset(ft)
unreal.InstancedFoliageActor.remove_all_instances(w,ft);bb=m.get_bounding_box();transforms=[]
for x,y,z,h,yaw in json.loads((B/'Saved/AdventureWorldSource/puzzle_talus_v19.json').read_text()):
 s=h*100/max(1,bb.max.z-bb.min.z)
 transforms.append(unreal.Transform(location=unreal.Vector(x*100,y*100,z*100-bb.min.z*s-h*20),rotation=unreal.Rotator(yaw=yaw),scale=unreal.Vector(s*1.3,s,s*.7)))
unreal.InstancedFoliageActor.add_instances(w,ft,transforms)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
exec(compile((B/'Scripts/render_puzzle_continent_v19.py').read_text(),'review','exec'),{'__name__':'__main__'})
