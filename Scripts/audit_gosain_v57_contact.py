import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain57';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors=E.get_all_level_actors();p=json.loads((O/'site_plan.json').read_text());C=p['center'];F=p['forward'];S=p['side'];Z=p['yard_floor_z'];W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
terrain=next(a for a in actors if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name()=='SM_IV_Continent_GosainMine57');ignore=[a for a in actors if a!=terrain];rows=[]
for d,l in [(19,-23),(19,23),(27,-23),(27,23),(95,-31),(95,31),(130,0),(145,0),(145,10)]:
 x=(C[0]+F[0]*d+S[0]*l)*100;y=(C[1]+F[1]*d+S[1]*l)*100
 lo=Z-30;hi=Z+50
 for i in range(17):
  mid=(lo+hi)/2;h=unreal.SystemLibrary.line_trace_single(W,unreal.Vector(x,y,hi*100),unreal.Vector(x,y,mid*100),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE)
  if h is not None:lo=mid
  else:hi=mid
 rows.append({'d':d,'l':l,'terrain_relative_z':(lo+hi)/2-Z})
(O/'contact_audit.json').write_text(json.dumps({'terrain_transform':str(terrain.get_actor_transform()),'samples':rows},indent=2))
