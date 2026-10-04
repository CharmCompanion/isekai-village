import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');R='/Game/IsekaiVillage/AdventureWorld';A=unreal.EditorAssetLibrary;w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
for kind in ['House','HouseVar']:
 ft=unreal.load_asset(R+'/Foliage/FT_Continent17_'+kind)
 if ft:unreal.InstancedFoliageActor.remove_all_instances(w,ft)
ft=unreal.load_asset(R+'/Foliage/FT_Continent17_Cliff')
if ft:
 unreal.InstancedFoliageActor.remove_all_instances(w,ft);mesh=ft.get_editor_property('mesh');bb=mesh.get_bounding_box();transforms=[]
 for x,y,z,h,yaw in json.loads((B/'Saved/AdventureWorldSource/continent_cliffs_v17.json').read_text()):
  if x*x+y*y<1200**2:continue
  scale=h*100/(bb.max.z-bb.min.z);transforms.append(unreal.Transform(location=unreal.Vector(x*100,y*100,(z-12880)*100-bb.min.z*scale-h*18),rotation=unreal.Rotator(yaw=yaw),scale=unreal.Vector(scale,scale,scale)))
 if transforms:unreal.InstancedFoliageActor.add_instances(w,ft,transforms)
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if 'IVContinentWater17' in [str(t) for t in a.tags]:a.set_actor_location(unreal.Vector(0,0,-1288000),False,False)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
