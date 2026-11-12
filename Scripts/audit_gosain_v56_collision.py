import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain56';W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();p=json.loads((B/'ArtSource/World/Gosain55/mine_road_profile.json').read_text());rows=[]
for i in [0,175]:
 x,y=p['xy'][i];z=p['z'][i]
 for span in [20,100,500]:
  h=unreal.SystemLibrary.line_trace_single(W,unreal.Vector(x*100,y*100,(z+span)*100),unreal.Vector(x*100,y*100,(z-span)*100),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE)
  rows.append({'sample':i,'span_m':span,'hit':h is not None,'result':str(h)})
(O/'collision_diagnostic.json').write_text(json.dumps(rows,indent=2))
