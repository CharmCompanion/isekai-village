import unreal,json,shutil,time
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain57';D='/Game/IsekaiVillage/AdventureWorld/Gosain57';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools()
assert (O/'rim_finish_applied.json').exists() and not (O/'collision_grid_applied.json').exists();v=json.loads((O/'ground_collision_grid.json').read_text());assert v['yard_max_vertical_error_m']<.2
name='SM_Gosain57_MineGroundCollisionGrid';path=D+'/Meshes/'+name
if not A.does_asset_exist(path):
 task=unreal.AssetImportTask();task.filename=str(O/(name+'.obj'));task.destination_path=D+'/Meshes';task.destination_name=name;task.automated=True;task.save=True
 op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;op.static_mesh_import_data.generate_lightmap_u_vs=False;task.options=op;T.import_asset_tasks([task])
mesh=unreal.load_asset(path);assert mesh;mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);A.save_loaded_asset(mesh)
a=next(a for a in E.get_all_level_actors() if a.get_actor_label()=='Gosain | Mine ground collision');backup=B/'Saved/WorldBackups'/('BeforeGosain57CollisionGrid_'+time.strftime('%Y%m%d_%H%M%S'));backup.mkdir(parents=True);shutil.copy2(B/'Content/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.umap',backup/'Map_AnimeAdventure.umap');a.static_mesh_component.set_static_mesh(mesh);assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level();(O/'collision_grid_applied.json').write_text(json.dumps({'status':'saved','backup':str(backup),'mesh':mesh.get_path_name(),'triangle_count':v['triangles'],'native_review':'pending'},indent=2))
