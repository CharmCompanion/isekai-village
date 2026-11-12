import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain56';W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();p=json.loads((B/'ArtSource/World/Gosain55/mine_road_profile.json').read_text());rows=[]
for i in [0,175]:
 x,y=p['xy'][i];z=p['z'][i]
 for dx,dy in [(0,0),(.5,0),(-.5,0),(0,.5),(0,-.5)]:
  start=unreal.Vector((x+dx)*100,(y+dy)*100,(z+50)*100);end=unreal.Vector((x+dx)*100,(y+dy)*100,(z-50)*100)
  h=unreal.SystemLibrary.line_trace_single(W,start,end,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE)
  row={'sample':i,'offset_m':[dx,dy],'line_hit':h is not None}
  if h and hasattr(unreal.GameplayStatics,'break_hit_result'):row['hit_details']=str(unreal.GameplayStatics.break_hit_result(h))
  if dx==0 and dy==0:
   h=unreal.SystemLibrary.sphere_trace_single(W,start,end,40.,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE);row['sphere_hit']=h is not None
  rows.append(row)
(O/'collision_offsets.json').write_text(json.dumps(rows,indent=2))
