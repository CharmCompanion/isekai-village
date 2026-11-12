import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain56';assert (O/'applied.json').exists()
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();actors=E.get_all_level_actors();rows=[]
for a in actors:
 for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
  if c.static_mesh and any(t in c.static_mesh.get_path_name() for t in ['/Gosain56/Meshes/SM_RightForestTree','/Gosain50/Meshes/SM_Gosain50_Tree']):rows.append({'mesh':c.static_mesh.get_path_name(),'count':c.get_instance_count()})
right=sum(x['count'] for x in rows if '/Gosain56/' in x['mesh']);left=sum(x['count'] for x in rows if '/Gosain50/' in x['mesh']);assert right==9706 and left==30177,(right,left)
p=json.loads((B/'ArtSource/World/Gosain55/mine_road_profile.json').read_text());hits=[]
for i in range(0,len(p['xy']),max(1,len(p['xy'])//16)):
 x,y=p['xy'][i];z=p['z'][i];h=unreal.SystemLibrary.line_trace_single(W,unreal.Vector(x*100,y*100,(z+2)*100),unreal.Vector(x*100,y*100,(z-5)*100),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE)
 hits.append({'sample':i,'hit':h is not None,'result':str(h)})
terrain=next(a for a in actors if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name()=='SM_IV_Continent_GosainShoulders56')
r={'saved_mesh':terrain.static_mesh_component.static_mesh.get_path_name(),'material':terrain.static_mesh_component.get_material(0).get_path_name(),'left_trees':left,'right_trees':right,'road_downward_trace_hits':sum(q['hit'] for q in hits),'road_downward_trace_samples':len(hits),'road_traces':hits,'note':'Downward collision checks only; does not certify navigation, movement, road clearance or performance.'}
(O/'native_verification.json').write_text(json.dumps(r,indent=2))
