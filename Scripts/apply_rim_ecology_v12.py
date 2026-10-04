import unreal,json,math
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');R='/Game/IsekaiVillage/AdventureWorld';A=unreal.EditorAssetLibrary;E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();rows=json.loads((B/'Saved/AdventureWorldSource/rim_ecology_v12.json').read_text());report={}
for kind in ['Grass','Flowers','Bush','Rocks','Talus']:
 path=R+'/Foliage/FT_R12_Rim'+kind;ft=unreal.load_asset(path) if A.does_asset_exist(path) else A.duplicate_asset(R+'/Foliage/FT_R08_'+kind,path)
 unreal.InstancedFoliageActor.remove_all_instances(w,ft)
 if kind in ['Rocks','Talus']:ft.set_editor_property('cull_distance',unreal.Int32Interval(min=0,max=0))
 A.save_loaded_asset(ft);mesh=ft.get_editor_property('mesh');b=mesh.get_bounding_box();transforms=[]
 for r in rows:
  if r['kind']!=kind:continue
  x,y,z=r['pos'];s=r['scale'];sx,sy=r['slope']
  normal=unreal.Vector(-sx,-sy,1).normal();rot=unreal.MathLibrary.make_rot_from_z(normal);q=rot.quaternion()*unreal.Rotator(yaw=r['yaw']).quaternion()
  bury=.55 if kind in ['Rocks','Talus'] else 1
  offset=-b.min.z*s*bury
  transforms.append(unreal.Transform(location=unreal.Vector(x*100,y*100,z*100+offset-3),rotation=q.rotator(),scale=unreal.Vector(s,s,s)))
 if transforms:unreal.InstancedFoliageActor.add_instances(w,ft,transforms)
 report[kind]=len(transforms)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(B/'Saved/rim_ecology_result.json').write_text(json.dumps(report,indent=2))

