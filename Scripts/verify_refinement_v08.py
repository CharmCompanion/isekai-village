import unreal,json,struct,math
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();actors=E.get_all_level_actors();ignore=[a for a in actors if not isinstance(a,unreal.LandscapeProxy)];raw=struct.unpack('<'+'H'*1009**2,(S/'IV_Refined_v08.r16').read_bytes());out=[]
def h(x,y):return (raw[round((y+600)*.84)*1009+round((x+600)*.84)]-32768)/64
samples=[(130,-98,24.5),(110,-145,24.5),(146,-145,24.5),(110,-181,24.5),(146,-181,24.5),(0,0,25),(590,-590,None),(-590,590,None),(595,0,None)]
for x,y in [(-285,-373),(-400,-380),(-130,-360),(-280,-510),(-219,151),(-245,0),(275,-493)]:samples.append((x,y,h(x,y)))
for x,y,expect in samples:
 r=unreal.SystemLibrary.line_trace_single_for_objects(w,unreal.Vector(x*100,y*100,60000),unreal.Vector(x*100,y*100,-70000),[unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1],False,ignore,unreal.DrawDebugTrace.NONE,True);hit=r.to_tuple() if r else None;z=hit[4].z/100 if hit and hit[0] else None
 out.append({'xy':[x,y],'expected':expect,'measured':z,'pass':z is None if expect is None else z is not None and abs(z-expect)<.65})
clouds=[a for a in actors if str(a.get_folder_path())=='Archived/Blob Clouds'];main=[a for a in actors if str(a.get_folder_path())=='Refinement/Distant World'];rocks=[a for a in actors if str(a.get_folder_path())=='Refinement/Underside'];report={'collision':out,'all_collision_pass':all(c['pass'] for c in out),'old_clouds_hidden':all(not a.static_mesh_component.is_visible() for a in clouds),'underside_pieces':len(rocks),'mainland_exists':len(main)==1,'native_landscape_count':sum(isinstance(a,unreal.Landscape) for a in actors)}
(B/'Saved/refinement_validation.json').write_text(json.dumps(report,indent=2));assert report['all_collision_pass'],out
