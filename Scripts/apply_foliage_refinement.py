import unreal,json,struct,math
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource';R='/Game/IsekaiVillage/AdventureWorld';A=unreal.EditorAssetLibrary;E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);T=unreal.AssetToolsHelpers.get_asset_tools();w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();raw=struct.unpack('<'+'H'*1009**2,(S/'IV_Refined_v08.r16').read_bytes())
def h(x,y):
 i=max(0,min(1008,round((x+600)*.84)));j=max(0,min(1008,round((y+600)*.84)));return (raw[j*1009+i]-32768)/64
# Cache original instances once by mesh before adding variants that share source meshes.
cache={}
for a in E.get_all_level_actors():
 if isinstance(a,unreal.InstancedFoliageActor):
  for c in a.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent):
   if c.static_mesh:cache.setdefault(c.static_mesh.get_path_name(),[]).extend(c.get_instance_transform(i,world_space=True) for i in range(c.get_instance_count()))
regrounded=0
for path in A.list_assets(R+'/Foliage',recursive=False,include_folder=False):
 ft=unreal.load_asset(path)
 if not isinstance(ft,unreal.FoliageType_InstancedStaticMesh) or ft.get_name().startswith('FT_R08_'):continue
 kept=[]
 for tf in cache.get(ft.get_editor_property('mesh').get_path_name(),[]):
  p=tf.translation;x=p.x/100;y=p.y/100;z=h(x,y)
  if y<-235 and z<19.8:continue
  if y<-235 or x<-220 or x>300 or y>300:tf.translation=unreal.Vector(p.x,p.y,z*100-12)
  kept.append(tf)
 unreal.InstancedFoliageActor.remove_all_instances(w,ft)
 if kept:unreal.InstancedFoliageActor.add_instances(w,ft,kept)
 regrounded+=len(kept)
P='/Game/SoStylized/Environment/'
assets={'Oak2':'Trees/Oak/SM_OakTree2','Oak4':'Trees/Oak/SM_OakTree4','LargeOak':'Trees/Oak/SM_OakTreeLarge1','Pine':'Trees/Pine/SM_Pine01','Sapling':'Trees/Oak/SM_OakSapling1','Grass':'Foliage/SM_Grass2','Foxtails':'Foliage/SM_Flower_Foxtails1','Flowers':'Foliage/SM_Flower_Daisies1','Fern':'Foliage/SM_Fern2','Bush':'Foliage/SM_BushLeafy01','Rocks':'Rocks/Spire/SM_RockSpire_RockClump02','Log':'Trees/Oak/SM_OakFallen1','Branch':'Trees/Oak/SM_OakBranch1','Stump':'Trees/Oak/SM_OakStump1','Talus':'Rocks/Spire/SM_RockSpire_RockClumpB03'}
counts={}
for kind,positions in json.loads((S/'foliage_refinement_v08.json').read_text()).items():
 name='FT_R08_'+kind;path=R+'/Foliage/'+name;ft=unreal.load_asset(path) if A.does_asset_exist(path) else T.create_asset(name,R+'/Foliage',unreal.FoliageType_InstancedStaticMesh,unreal.FoliageType_InstancedStaticMeshFactory());m=unreal.load_asset(P+assets[kind]);assert m,kind;ft.set_editor_property('mesh',m)
 cull=0 if kind in ['Oak2','Oak4','LargeOak','Pine','Sapling','Talus'] else 17000 if kind in ['Grass','Flowers','Foxtails','Fern'] else 50000
 if cull:ft.set_editor_property('cull_distance',unreal.Int32Interval(min=cull-4000,max=cull))
 A.save_loaded_asset(ft);unreal.InstancedFoliageActor.remove_all_instances(w,ft)
 b=m.get_bounding_box();transforms=[]
 for x,y,z,s,yaw in positions:
  base=z*100-b.min.z*s-(18 if kind not in ['Rocks','Talus'] else (b.max.z-b.min.z)*s*.22)
  transforms.append(unreal.Transform(location=unreal.Vector(x*100,y*100,base),rotation=unreal.Rotator(yaw=yaw),scale=unreal.Vector(s,s,s)))
 unreal.InstancedFoliageActor.add_instances(w,ft,transforms);counts[kind]=len(transforms)
 (B/'Saved/refinement_foliage_result.json').write_text(json.dumps({'stage':kind,'counts':counts,'existing_kept':regrounded},indent=2))
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(B/'Saved/refinement_foliage_result.json').write_text(json.dumps({'stage':'saved','counts':counts,'existing_kept':regrounded},indent=2))

