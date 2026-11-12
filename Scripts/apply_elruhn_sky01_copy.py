"""Duplicate the world before isolating El Ruhn. Never prune source map."""
import unreal,json,hashlib,time
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/ElRuhnSky01';SRC='/Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure';DST='/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky'
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);A=unreal.EditorAssetLibrary;L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert W.get_path_name().startswith(SRC+'.')
assert not (O/'copy_applied.json').exists()
srcfile=B/'Content/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.umap';source_hash=hashlib.sha256(srcfile.read_bytes()).hexdigest()
if not A.does_asset_exist(DST):assert unreal.EditorLoadingAndSavingUtils.save_map(W,DST)
assert L.load_level(DST)
W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert W.get_path_name().startswith(DST+'.'),W.get_path_name()
(O/'copy_created.json').write_text(json.dumps({'map':DST,'source_sha256':source_hash,'source':SRC},indent=2))
audit=json.loads((O/'scene_audit.json').read_text());near={r['name']:r for r in audit['actors']};removed=[];kept=[]
for a in list(E.get_all_level_actors()):
 p=a.get_actor_location();label=a.get_actor_label();folder=str(a.get_folder_path());cls=a.get_class().get_name()
 # Keep native terrain, island-level actors, lighting and foliage; discard mainland/archived stages in COPY only.
 keep=True
 if isinstance(a,unreal.InstancedFoliageActor):pass
 elif isinstance(a,unreal.StaticMeshActor):
  c=a.static_mesh_component;m=c.static_mesh;name=m.get_name() if m else ''
  keep=abs(p.x)<180000 and abs(p.y)<180000 and p.z>-180000
  if any(s in (label+' '+name+' '+folder).lower() for s in ['continent','gosain','civilization','regional civilizations','painted drifting cloudbank','archived','cloud sea']):keep=False
  if not c.is_visible() or a.get_editor_property('hidden'):keep=False
 elif cls in ['CameraActor','CineCameraActor','TextRenderActor']:keep=False
 elif not isinstance(a,(unreal.SkyAtmosphere,unreal.DirectionalLight,unreal.SkyLight,unreal.ExponentialHeightFog,unreal.PostProcessVolume)):
  if abs(p.x)>180000 or abs(p.y)>180000 or p.z<-180000:keep=False
 if 'Archived' in folder:keep=False
 if keep:kept.append([a.get_name(),label,cls])
 else:removed.append([a.get_name(),label]);E.destroy_actor(a)
# Foliage component instance removal is confined to the duplicate world's component data.
fol=[]
for a in E.get_all_level_actors():
 for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
  idx=[];n=c.get_instance_count()
  for i in range(n):
   p=c.get_instance_transform(i,True).translation
   if abs(p.x)>180000 or abs(p.y)>180000 or p.z<-180000:idx.append(i)
  if idx:assert c.remove_instances(idx)
  fol.append({'mesh':c.static_mesh.get_path_name() if c.static_mesh else '', 'before':n,'removed':len(idx),'retained':c.get_instance_count()})
assert L.save_current_level();assert hashlib.sha256(srcfile.read_bytes()).hexdigest()==source_hash
(O/'copy_applied.json').write_text(json.dumps({'status':'saved','map':DST,'source_sha256':source_hash,'source_unchanged':True,'kept':kept,'removed':removed,'foliage':fol},indent=2))
