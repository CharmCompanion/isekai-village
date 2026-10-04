import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource';R='/Game/IsekaiVillage/AdventureWorld';A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
def progress(*args,**kwargs):pass
rows=json.loads((S/'puzzle_continent_v22_instances.json').read_text());P='/Game/SoStylized/Environment/'
assets={'Oak':P+'Trees/Oak/SM_OakTree2','OakVar':P+'Trees/Oak/SM_OakTree4','Pine':P+'Trees/Pine/SM_Pine01','Rocks':P+'Rocks/Spire/SM_RockSpire_RockClump02','House':'/Game/AdvancedVillagePack/Meshes/SM_House_Var01','HouseVar':'/Game/AdvancedVillagePack/Meshes/SM_House_Var02'}
counts={}
for kind,positions in rows.items():
 path=R+'/Foliage/FT_Continent17_'+kind
 ft=unreal.load_asset(path) if A.does_asset_exist(path) else T.create_asset('FT_Continent17_'+kind,R+'/Foliage',unreal.FoliageType_InstancedStaticMesh,unreal.FoliageType_InstancedStaticMeshFactory())
 m=unreal.load_asset(assets[kind]);assert m,kind
 ft.set_editor_property('mesh',m);ft.set_editor_property('cull_distance',unreal.Int32Interval(min=0,max=0));ft.set_editor_property('cast_shadow',False);A.save_loaded_asset(ft)
 unreal.InstancedFoliageActor.remove_all_instances(w,ft)
 bounds=m.get_bounding_box();height=max(bounds.max.z-bounds.min.z,1);transforms=[]
 for x,y,z,h,yaw in positions:
  s=h*100/height
  transforms.append(unreal.Transform(location=unreal.Vector(x*100,y*100,z*100-bounds.min.z*s),rotation=unreal.Rotator(yaw=yaw),scale=unreal.Vector(s,s,s)))
 if transforms:unreal.InstancedFoliageActor.add_instances(w,ft,transforms)
 counts[kind]=len(transforms);progress('dressing '+kind,counts=counts)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level();progress('saved',counts=counts)
