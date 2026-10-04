import unreal,json,struct,math
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();actors=E.get_all_level_actors();ignore=[a for a in actors if not isinstance(a,unreal.LandscapeProxy)];raw=struct.unpack('<'+'H'*1009**2,(B/'Saved/AdventureWorldSource/IV_Valley_v14.r16').read_bytes())
def h(x,y):return (raw[max(0,min(1008,round((y+600)*.84)))*1009+max(0,min(1008,round((x+600)*.84)))]-32768)/64
def trace(p,q):
 r=unreal.SystemLibrary.line_trace_single_for_objects(w,unreal.Vector(*(v*100 for v in p)),unreal.Vector(*(v*100 for v in q)),[unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1],False,ignore,unreal.DrawDebugTrace.NONE,True);return r.to_tuple() if r else None
checks=[]
for x,y,expected in [(130,-98,24.5),(110,-145,24.5),(146,-145,24.5),(110,-181,24.5),(146,-181,24.5),(0,0,25),(590,-590,None),(-590,590,None),(595,0,None)]+[(x,y,h(x,y)) for x,y in [(-285,-373),(-400,-380),(-130,-360),(-219,151),(-245,0),(275,-493),(520,-40),(540,-40),(555,120)]]:
 hit=trace((x,y,600),(x,y,-700));z=hit[4].z/100 if hit and hit[0] else None;checks.append({'xy':[x,y],'expected':expected,'measured':z,'pass':z is None if expected is None else z is not None and abs(z-expected)<1.0})
foliage=sum(c.get_instance_count() for a in actors if isinstance(a,unreal.InstancedFoliageActor) for c in a.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent))
visible_old=[]
for a in actors:
 if 'IVRockRim10' in [str(t) for t in a.tags] and a.static_mesh_component.is_visible():visible_old.append(a.get_actor_label())
report={'height_checks':checks,'all_height_checks_pass':all(c['pass'] for c in checks),'visible_old_rocks':visible_old,'foliage_instances':foliage,'full_character_traversal_tested':False}
(B/'Saved/valley_native_validation.json').write_text(json.dumps(report,indent=2));assert report['all_height_checks_pass'];assert not visible_old

exec(compile((B/'Scripts/verify_join_v13.py').read_text(),'preserved edge verification','exec'),{'__name__':'__main__'})
