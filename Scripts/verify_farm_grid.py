import unreal,json,struct,math
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource'
raw=struct.unpack('<'+'H'*(1009*1009),(S/'IV_Adventure_Farm_v02.r16').read_bytes())
e=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();actors=e.get_all_level_actors()
ignore=[a for a in actors if not isinstance(a,unreal.LandscapeProxy)]
out={'samples':[],'debug':[]}
for x,y in [(0,0),(130,-98),(110,-145),(146,-145),(110,-181),(146,-181),(128,-163),(-350,274),(300,0),(0,200)]:
    hit=unreal.SystemLibrary.line_trace_single(w,unreal.Vector(x*100,y*100,60000),unreal.Vector(x*100,y*100,-6000),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,ignore,unreal.DrawDebugTrace.NONE,True)
    measured=hit.to_tuple()[4].z/100 if hit else None
    expected=(raw[round((y+600)/1200*1008)*1009+round((x+600)/1200*1008)]-32768)/64
    out['samples'].append({'xy':[x,y],'measured':measured,'expected':expected,'delta':measured-expected if measured is not None else None})
for a in actors:
    if str(a.get_folder_path())=='BuildGrid/Debug':out['debug'].append({'name':a.get_actor_label(),'bounds':str(a.get_actor_bounds(False)),'mesh_bounds':str(a.static_mesh_component.static_mesh.get_bounding_box())})
unreal.EditorLevelLibrary.set_level_viewport_camera_info(unreal.Vector(20000,-25500,11500),unreal.MathLibrary.find_look_at_rotation(unreal.Vector(20000,-25500,11500),unreal.Vector(12800,-15000,2450)))
out['camera']=str(unreal.EditorLevelLibrary.get_level_viewport_camera_info())
(B/'Saved/farm_grid_verification.json').write_text(json.dumps(out,indent=2))
