"""Add native instanced understory without changing terrain, architecture or shared assets."""
import unreal,json,math,time,shutil,hashlib
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain59';D='/Game/IsekaiVillage/AdventureWorld/Gosain59';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert W.get_path_name().startswith('/Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.')
assert not (O/'applied.json').exists()
assert json.loads((B/'Docs/WorldDesign/Gosain58_AtmosphereStudy/comparison_complete.json').read_text())['restored']
data=json.loads((O/'understory.json').read_text());validation=json.loads((O/'source_verification.json').read_text());assert validation['mine_footprint_clear'] and validation['minimum_road_center_clearance_m']>6.1
meshes=[unreal.load_asset(a['path']) for a in data['assets']];assert all(meshes)
def counts():
 out={m.get_path_name():0 for m in meshes}
 for a in E.get_all_level_actors():
  for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
   if c.static_mesh and c.static_mesh.get_path_name() in out:out[c.static_mesh.get_path_name()]+=c.get_instance_count()
 return out
def static_signature():
 out=[]
 for a in E.get_all_level_actors():
  if not isinstance(a,unreal.StaticMeshActor):continue
  c=a.static_mesh_component;p=a.get_actor_location();r=a.get_actor_rotation();s=a.get_actor_scale3d();out.append([a.get_name(),c.static_mesh.get_path_name() if c.static_mesh else '',[p.x,p.y,p.z,r.pitch,r.yaw,r.roll,s.x,s.y,s.z],[c.get_material(i).get_path_name() if c.get_material(i) else '' for i in range(c.get_num_materials())]])
 return hashlib.sha256(json.dumps(sorted(out),sort_keys=True).encode()).hexdigest()
before=counts();signature=static_signature();fts=[];groups=[[] for m in meshes];bounds=[]
for i,(asset,mesh) in enumerate(zip(data['assets'],meshes)):
 name='FT_Gosain59_'+asset['key'];assert not A.does_asset_exist(D+'/Foliage/'+name)
 ft=T.create_asset(name,D+'/Foliage',unreal.FoliageType_InstancedStaticMesh,unreal.FoliageType_InstancedStaticMeshFactory());ft.set_editor_property('mesh',mesh);maximum=45000 if i in [0,1,2,4] else 100000 if i==3 else 350000;ft.set_editor_property('cull_distance',unreal.Int32Interval(min=int(maximum*.75),max=maximum));ft.set_editor_property('cast_shadow',i in [3,5,6]);A.save_loaded_asset(ft);fts.append(ft)
 box=mesh.get_bounding_box();bounds.append((box.min,box.max));assert box.max.z-box.min.z>1
for i,x,y,z,yaw,height in data['instances']:
 i=int(i);lo,hi=bounds[i];scale=height*100/(hi.z-lo.z);angle=math.radians(yaw);cx=(lo.x+hi.x)*.5*scale;cy=(lo.y+hi.y)*.5*scale;loc=unreal.Vector(x*100-cx*math.cos(angle)+cy*math.sin(angle),y*100-cx*math.sin(angle)-cy*math.cos(angle),z*100-lo.z*scale);groups[i].append(unreal.Transform(location=loc,rotation=unreal.Rotator(pitch=0,yaw=yaw,roll=0),scale=unreal.Vector(scale,scale,scale)))
backup=B/'Saved/WorldBackups'/('BeforeGosain59_'+time.strftime('%Y%m%d_%H%M%S'));backup.mkdir(parents=True);shutil.copy2(B/'Content/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.umap',backup/'Map_AnimeAdventure.umap')
try:
 for ft,rows in zip(fts,groups):unreal.InstancedFoliageActor.add_instances(W,ft,rows)
 after=counts();assert signature==static_signature()
 for mesh,rows in zip(meshes,groups):assert after[mesh.get_path_name()]-before[mesh.get_path_name()]==len(rows)
 assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception:
 for ft in fts:unreal.InstancedFoliageActor.remove_all_instances(W,ft)
 raise
(O/'applied.json').write_text(json.dumps({'status':'saved','backup':str(backup),'instances':len(data['instances']),'assets':[m.get_path_name() for m in meshes],'instance_counts_before':before,'instance_counts_after':after,'all_static_actors_unchanged':True,'native_visual_review':'pending','global_sky_not_changed_by_this_script':True},indent=2))
