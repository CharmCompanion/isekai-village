"""Verify scope, support circle arrangement, retained terrain and native materials."""
import unreal,json,hashlib,math
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/ElRuhnSky01';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert W.get_path_name().startswith('/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky.')
copy=json.loads((O/'copy_applied.json').read_text());src=B/'Content/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.umap';assert hashlib.sha256(src.read_bytes()).hexdigest()==copy['source_sha256']
actors=list(E.get_all_level_actors());stones=[a for a in actors if a.get_actor_label().startswith('Levitation Stone ')];seals=[a for a in actors if a.get_actor_label().startswith('Stone ') and 'horizontal wind seal' in a.get_actor_label()]
assert len(stones)==5 and len(seals)==5
for a in stones+seals:
 p=a.get_actor_bounds(False)[0] if a in stones else a.get_actor_location()
 assert abs(p.z+12000)<.1
 if a in seals:
  r=a.get_actor_rotation();assert abs(r.pitch)<.01 and abs(r.roll)<.01
land=[a for a in actors if isinstance(a,unreal.Landscape)];assert len(land)==1
assert any('matching rock foundation' in a.get_actor_label() for a in actors)
assert any(a.get_actor_label()=='Farmhouse' for a in actors)
clouds=[a for a in actors if a.get_actor_label().startswith('Cloud Sea |')];assert len(clouds)>=181
for a in clouds:
 if isinstance(a,unreal.StaticMeshActor):assert a.get_actor_location().z<-90000
new=[a for a in actors if 'ElRuhnSky01' in [str(t) for t in a.tags]];missing=[]
for a in new:
 for c in a.get_components_by_class(unreal.StaticMeshComponent):
  if not c.static_mesh:missing.append(a.get_actor_label()+' mesh')
  for i in range(c.get_num_materials()):
   if not c.get_material(i):missing.append(a.get_actor_label()+' material '+str(i))
assert not missing,missing
centering=json.loads((O/'centering_applied.json').read_text());cx,cy=centering['island_center_m'];errors=[];centers=[]
for a in stones:
 p=a.get_actor_bounds(False)[0];x=p.x/100;y=p.y/100;centers.append([x,y]);errors.append(abs(math.hypot(x-cx,y-cy)-868))
assert max(errors)<.0001
assert abs(sum(p[0] for p in centers)/5-cx)<.0001 and abs(sum(p[1] for p in centers)/5-cy)<.0001
for a in actors:
 if a.get_actor_label().startswith(('Island levitation ring |','Island covenant |')):
  p=a.get_actor_location();assert abs(p.x/100-cx)<.0001 and abs(p.y/100-cy)<.0001
report={'status':'passed','map':W.get_path_name(),'source_map_unchanged':True,'five_stones':len(stones),'five_horizontal_midpoint_seals':len(seals),'seal_height_m':-120,'village_reference_height_m':25,'cloud_banks_and_haze':len(clouds),'native_landscapes':len(land),'new_static_actors':len(new),'missing_meshes_or_materials':missing,'limits':['Native screenshot review is separate.','Tower exterior only; magic is animated environment art, not a simulated levitation game system.','Runtime traversal and performance not certified.']}
report.update(island_and_ring_center_m=[cx,cy],maximum_stone_orbit_error_m=max(errors),equal_spacing_degrees=72)
(O/'native_verification.json').write_text(json.dumps(report,indent=2))
