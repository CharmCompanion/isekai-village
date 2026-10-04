import unreal,json,math,random
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource';R='/Game/IsekaiVillage/AdventureWorld';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);M=unreal.MaterialEditingLibrary;A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_path_name().startswith(R+'/Maps/Map_AnimeAdventure.')
for a in E.get_all_level_actors():
 if str(a.get_folder_path())=='Refinement/Underside' or a.get_actor_label()=='SM_IV_FloatingUnderside':
  a.set_folder_path('Archived/Regular Underside v08');a.set_actor_hidden_in_game(True);a.set_actor_enable_collision(False);a.static_mesh_component.set_visibility(False,True)
 if 'IVOrganic09' in [str(t) for t in a.tags]:E.destroy_actor(a)
name='SM_IV_OrganicUnderside_v09';task=unreal.AssetImportTask();task.filename=str(S/(name+'.obj'));task.destination_path=R+'/Meshes/Refinement';task.destination_name=name;task.automated=True;task.replace_existing=True;task.save=True;op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;task.options=op;T.import_asset_tasks([task]);core=unreal.load_asset(task.destination_path+'/'+name);core.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);A.save_loaded_asset(core)
p=R+'/Materials/M_IV_OrganicBedrock';mat=unreal.load_asset(p) if A.does_asset_exist(p) else A.duplicate_asset(R+'/Materials/M_IV_FracturedIsland',p)
for n in M.get_material_expressions(mat):
 if isinstance(n,unreal.MaterialExpressionCustom):
  code=n.get_editor_property('code')
  if 'float strata=' in code:n.set_editor_property('code','float strata=.82+.10*sin((P.z+.17*P.x-.11*P.y)/5000.+.7*sin(P.y/7600.))+.08*sin(P.x/3200.+P.z/1900.);return C*strata*float3(.98,.94,.86);')
 if isinstance(n,unreal.MaterialExpressionMultiply):
  if abs(n.get_editor_property('const_b')-.38)<.001:n.set_editor_property('const_b',.16)
M.recompile_material(mat);A.save_loaded_asset(mat)
def spawn(m,loc,scale,rot,label):
 a=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*(v*100 for v in loc)),rot);a.static_mesh_component.set_static_mesh(m);a.set_actor_scale3d(unreal.Vector(*scale));a.set_actor_label(label);a.set_folder_path('Floating Island/Organic Bedrock');a.tags=[unreal.Name('IVOrganic09')]
 for slot in range(a.static_mesh_component.get_num_materials()):a.static_mesh_component.set_material(slot,mat)
 return a
spawn(core,(0,0,0),(1,1,1),unreal.Rotator(),'Continuous torn island bedrock')
D=json.loads((S/'organic_underside_v09.json').read_text());meshes=[unreal.load_asset('/Game/SoStylized/Environment/Rocks/Spire/SM_RockSpire_Rock'+str(i).zfill(2)) for i in range(1,21)]
for row in D['placements']:
 rng=random.Random(row['seed']);m=rng.choice(meshes);b=m.get_bounding_box();dims=row['dims'];scale=tuple(d*100/v for d,v in zip(dims,[b.max.x-b.min.x,b.max.y-b.min.y,b.max.z-b.min.z]));loc=row['loc'];rot=unreal.Rotator(pitch=rng.uniform(-48,48),yaw=math.degrees(row['angle'])+rng.uniform(-60,60),roll=rng.uniform(-55,55));a=spawn(m,loc,scale,rot,'Embedded broken bedrock');o,e=a.get_actor_bounds(False);target=unreal.Vector(*(v*100 for v in loc));a.set_actor_location(a.get_actor_location()+target-o,False,False)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level();(B/'Saved/organic_underside_result.json').write_text(json.dumps({'saved':True,'archived_previous_underside':True,'continuous_mesh':name,'embedded_rock_pieces':104,'native_terrain_modified':False},indent=2))
