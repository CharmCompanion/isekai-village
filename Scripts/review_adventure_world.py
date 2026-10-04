import unreal,json,traceback
from pathlib import Path
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert w.get_path_name().startswith('/Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.')
e=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors=e.get_all_level_actors();out={'actors':[],'terrain_samples':[]}
for a in actors:
    if isinstance(a,unreal.InstancedFoliageActor):continue
    loc=a.get_actor_location();o,b=a.get_actor_bounds(False)
    out['actors'].append({'name':a.get_actor_label(),'class':a.get_class().get_name(),'location':[loc.x,loc.y,loc.z],'rotation':str(a.get_actor_rotation()),'bounds':[o.x,o.y,o.z,b.x,b.y,b.z]})
ignore=[a for a in actors if not isinstance(a,unreal.LandscapeProxy)]
for x,y in [(0,-20),(100,-230),(133,-244),(162,-222),(115,-181),(-350,274),(300,0),(0,200)]:
    try:
        hit=unreal.SystemLibrary.line_trace_single(w,unreal.Vector(x*100,y*100,60000),unreal.Vector(x*100,y*100,-6000),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,ignore,unreal.DrawDebugTrace.NONE,True)
        out['hit_api']=dir(hit)
        out['terrain_samples'].append({'xy':[x,y],'hit':str(hit.to_tuple()) if hit else None})
    except:out['terrain_samples'].append({'error':traceback.format_exc()})
Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/adventure_review.json').write_text(json.dumps(out,indent=2))
unreal.EditorLevelLibrary.set_level_viewport_camera_info(unreal.Vector(14000,-18500,13500),unreal.Rotator(pitch=-30,yaw=125))
