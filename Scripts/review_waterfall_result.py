import unreal,json
from pathlib import Path
e=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
ignore=[a for a in e.get_all_level_actors() if not isinstance(a,unreal.LandscapeProxy)]
out=[]
for x,y in [(-349,263),(-349,276),(130,-98),(110,-145),(146,-181)]:
    hit=unreal.SystemLibrary.line_trace_single(w,unreal.Vector(x*100,y*100,60000),unreal.Vector(x*100,y*100,-6000),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,ignore,unreal.DrawDebugTrace.NONE,True)
    out.append({'xy':[x,y],'height_m':hit.to_tuple()[4].z/100})
eye=unreal.Vector(-32000,23500,12500)
unreal.EditorLevelLibrary.set_level_viewport_camera_info(eye,unreal.MathLibrary.find_look_at_rotation(eye,unreal.Vector(-34900,27200,8800)))
Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/waterfall_collision_review.json').write_text(json.dumps(out,indent=2))
