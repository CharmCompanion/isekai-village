"""Inspect native placement and local mine collision. No play-mode claim."""
import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain58';assert (O/'applied.json').exists()
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();actors=E.get_all_level_actors();rows=[]
plan=json.loads((B/'ArtSource/World/Gosain57/site_plan.json').read_text());C=plan['center'];F=plan['forward'];S=plan['side'];Z=plan['yard_floor_z']
def point(d,l,z):return unreal.Vector((C[0]+d*F[0]+l*S[0])*100,(C[1]+d*F[1]+l*S[1])*100,(Z+.012*d-.003*l+z)*100)
ignore=[]
def sphere(a,b):return unreal.SystemLibrary.sphere_trace_single(W,a,b,40.,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE) is not None
for a in actors:
 for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
  if c.static_mesh and any(t in c.static_mesh.get_path_name() for t in ['/Gosain56/Meshes/SM_RightForestTree','/Gosain50/Meshes/SM_Gosain50_Tree']):rows.append({'mesh':c.static_mesh.get_path_name(),'count':c.get_instance_count()})
tagged=[a for a in actors if 'Gosain57Mine' in [str(t) for t in a.tags]]
terrain=next(a for a in actors if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name()=='SM_IV_Continent_GosainRefined58')
support_names=['Gosain | Mine ground collision','Gosain | Mine hillside and adit']
ignore=[a for a in actors if a.get_actor_label() not in support_names]
floor_checks=[{'d':d,'hit':sphere(point(d,0,2),point(d,0,-3))} for d in [-30,-20,-10,0,10,20,30,40,50,60,70,80,88]]
ignore=[a for a in actors if a not in tagged]
passages=[{'d':d,'blocked':sphere(point(d,0,1.5),point(d+8,0,1.5))} for d in range(30,80,8)]
gate=sphere(point(88,0,1.5),point(94,0,1.5))
entrances=[{'lateral_m':l,'blocked':sphere(point(15,l,1.5),point(35,l,1.5))} for l in [-1.8,0,1.8]]
landform=next(a for a in tagged if a.get_actor_label()=='Gosain | Mine hillside and adit')
r={'world':W.get_path_name(),'terrain':terrain.static_mesh_component.static_mesh.get_path_name(),'landform':landform.static_mesh_component.static_mesh.get_path_name(),'left_trees':sum(q['count'] for q in rows if '/Gosain50/' in q['mesh']),'right_trees':sum(q['count'] for q in rows if '/Gosain56/' in q['mesh']),'mine_actor_count':len(tagged),'mine_lights':sum(isinstance(a,unreal.PointLight) for a in tagged),'floor_sphere_traces':floor_checks,'centerline_passages':passages,'entrance_passages':entrances,'deeper_gate_blocks':gate,'floor_test_isolation':support_names,'note':'0.4 m radius sweeps in editor. Floor support tests ignore everything except the mine ground collision and mine landform. Passage tests consider mine-tagged actors only. This does not certify runtime movement, navigation, performance or extraction gameplay.'}
(O/'native_verification.json').write_text(json.dumps(r,indent=2))
assert r['left_trees']==30177 and r['right_trees']==9706
assert all(q['hit'] for q in floor_checks)
assert not any(q['blocked'] for q in passages+entrances)
assert gate and len(tagged)==195
assert landform.static_mesh_component.static_mesh.get_name()=='SM_Gosain57_MineLandformFinal'
assert not terrain.get_actor_enable_collision()
r['terrain_actor_collision']=terrain.get_actor_enable_collision();r['terrain_component_collision']=str(terrain.static_mesh_component.get_collision_enabled())
r['terrain_material']=terrain.static_mesh_component.get_material(0).get_path_name()
route=next(a for a in actors if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name()=='SM_Gosain58_ContinuousRoutes')
r['routes']=route.static_mesh_component.static_mesh.get_path_name()
assert '/Gosain58/' in r['terrain_material']
applied=json.loads((O/'applied.json').read_text());assert applied['unrelated_static_actor_signature_before']==applied['unrelated_static_actor_signature_after']
r['unrelated_static_actor_signature_matches']=True
(O/'native_verification.json').write_text(json.dumps(r,indent=2))
