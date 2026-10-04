import unreal,json
from pathlib import Path
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();actors=E.get_all_level_actors();ignore=[a for a in actors if not isinstance(a,unreal.LandscapeProxy)];out=[]
for x,y,expect in [(130,-98,24.5),(110,-145,24.5),(146,-145,24.5),(110,-181,24.5),(146,-181,24.5),(0,0,25),(590,-590,None),(-590,590,None),(595,0,None),(-285,-320,13.5)]:
 # The editor adds a hole-free Visibility-only heightfield for sculpting.
 # Query WorldStatic to test the actual game collision, excluding that editor aid.
 result=unreal.SystemLibrary.line_trace_single_for_objects(w,unreal.Vector(x*100,y*100,60000),unreal.Vector(x*100,y*100,-70000),[unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1],False,ignore,unreal.DrawDebugTrace.NONE,True)
 hit=result.to_tuple() if result else None;z=hit[4].z/100 if hit and hit[0] else None
 out.append({'xy':[x,y],'expected':expect,'measured':z,'pass':z is None if expect is None else z is not None and abs(z-expect)<.1})
Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/floating_collision_review.json').write_text(json.dumps(out,indent=2))
assert all(p['pass'] for p in out),out
assert all(not a.static_mesh_component.is_visible() for a in actors if a.get_actor_label()=='Southern Sea - Coastal Ocean')
