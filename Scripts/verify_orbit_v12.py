import unreal,json,math
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage')
exec(compile((B/'Scripts/verify_dish_peak_v11.py').read_text(),'native terrain verification','exec'),{'__name__':'__main__'})
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors=E.get_all_level_actors();w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
mountains=[a for a in actors if 'IVOrbit12' in [str(t) for t in a.tags]];assert len(mountains)==1
mountain=mountains[0];ignore=[a for a in actors if a!=mountain];checks=[]
for z in [-150,-400,-700]:
 for i in range(16):
  angle=math.tau*i/16;p=unreal.Vector((-82+1600*math.cos(angle))*100,(58+1600*math.sin(angle))*100,z*100);q=unreal.Vector(-8200,5800,z*100)
  hit=unreal.SystemLibrary.line_trace_single_for_objects(w,p,q,[unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1],True,ignore,unreal.DrawDebugTrace.NONE,True);result=hit.to_tuple() if hit else None
  checks.append({'angle_degrees':i*22.5,'height_m':z,'hit':bool(result and result[0])})
visible_legacy=[]
for a in actors:
 if set(str(t) for t in a.tags)&{'IVRockRim10','IVDishPeak11','IVOrganic09'}:
  if a.static_mesh_component.is_visible():visible_legacy.append(a.get_actor_label())
native=json.loads((B/'Saved/dish_peak_validation.json').read_text());geometry=json.loads((B/'Saved/AdventureWorldSource/orbit_mountain_v12.json').read_text())
report={'underside_radial_checks':checks,'all_48_radial_checks_pass':all(c['hit'] for c in checks),'native_terrain_checks_pass':native['all_height_checks_pass'],'visible_legacy_undersides':visible_legacy,'geometry':geometry,'foliage_instances':native['foliage_instances'],'character_traversal_tested':False}
(B/'Saved/orbit_validation.json').write_text(json.dumps(report,indent=2));assert report['all_48_radial_checks_pass'];assert not visible_legacy
