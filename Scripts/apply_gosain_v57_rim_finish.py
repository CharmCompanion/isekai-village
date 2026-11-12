import unreal,json,math,shutil,time
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain57';D='/Game/IsekaiVillage/AdventureWorld/Gosain57';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools()
assert (O/'contact_fix_applied.json').exists() and not (O/'rim_finish_applied.json').exists()
actors=E.get_all_level_actors();labels={a.get_actor_label():a for a in actors};rock=unreal.load_asset(D+'/Materials/M_Gosain57_WeatheredMine');name='SM_Gosain57_MineLandformFinal';path=D+'/Meshes/'+name
if not A.does_asset_exist(path):
 task=unreal.AssetImportTask();task.filename=str(O/(name+'.obj'));task.destination_path=D+'/Meshes';task.destination_name=name;task.automated=True;task.save=True
 op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;op.static_mesh_import_data.generate_lightmap_u_vs=False;op.static_mesh_import_data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;task.options=op;T.import_asset_tasks([task])
mesh=unreal.load_asset(path);assert mesh
slots=list(mesh.static_materials)
for slot in slots:slot.set_editor_property('material_interface',rock)
mesh.set_editor_property('static_materials',slots);mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);A.save_loaded_asset(mesh)
collision_name='SM_Gosain57_MineGroundCollision';collision_path=D+'/Meshes/'+collision_name
if not A.does_asset_exist(collision_path):
 task=unreal.AssetImportTask();task.filename=str(O/(collision_name+'.obj'));task.destination_path=D+'/Meshes';task.destination_name=collision_name;task.automated=True;task.save=True;task.options=op;T.import_asset_tasks([task])
collision=unreal.load_asset(collision_path);assert collision;collision.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);A.save_loaded_asset(collision)
backup=B/'Saved/WorldBackups'/('BeforeGosain57RimFinish_'+time.strftime('%Y%m%d_%H%M%S'));backup.mkdir(parents=True);shutil.copy2(B/'Content/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.umap',backup/'Map_AnimeAdventure.umap')
labels['Gosain | Mine hillside and adit'].static_mesh_component.set_static_mesh(mesh)
source=labels['Gosain | Mine hillside and adit'];ground=E.spawn_actor_from_class(unreal.StaticMeshActor,source.get_actor_location(),source.get_actor_rotation());ground.static_mesh_component.set_static_mesh(collision);ground.set_actor_label('Gosain | Mine ground collision');ground.tags=['Gosain57Mine'];ground.set_folder_path('World/Gosain/Mine57');ground.static_mesh_component.set_visibility(False,True);ground.set_actor_hidden_in_game(True);ground.set_actor_enable_collision(True);ground.static_mesh_component.set_collision_profile_name('BlockAll');ground.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
for label in ['Gosain | Mine loading yard','Gosain | Mine entrance track']:
 labels[label].set_actor_enable_collision(False);labels[label].static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
for q in json.loads((O/'props_refined.json').read_text()):
 if q['label'].startswith('Mine timber support'):q['size']=[1.7,10.7,8.2]
 elif not q['label'].startswith(('Mine bedrock shoulder','Mine roof strata','Mine weathered outcrop')):continue
 a=labels['Gosain | '+q['label']];sm=a.static_mesh_component.static_mesh;box=sm.get_bounding_box();lo=box.min;hi=box.max;sc=[q['size'][j]*100/v for j,v in enumerate([hi.x-lo.x,hi.y-lo.y,hi.z-lo.z])];ang=math.radians(q['yaw']);cx=(lo.x+hi.x)*.5*sc[0];cy=(lo.y+hi.y)*.5*sc[1];loc=unreal.Vector(q['xy'][0]*100-cx*math.cos(ang)+cy*math.sin(ang),q['xy'][1]*100-cx*math.sin(ang)-cy*math.cos(ang),q['z']*100-lo.z*sc[2]);a.set_actor_location(loc,False,False);a.set_actor_scale3d(unreal.Vector(*sc))
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(O/'rim_finish_applied.json').write_text(json.dumps({'status':'saved','backup':str(backup),'landform':mesh.get_path_name(),'rim_sampled_from_final_terrain':True,'supports_resized_to_fit_ceiling':True,'mine_ground_collision':collision.get_path_name(),'main_continent_collision_unchanged':True,'native_review':'pending'},indent=2))
