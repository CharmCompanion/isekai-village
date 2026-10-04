import unreal
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');R='/Game/IsekaiVillage/AdventureWorld';T=unreal.AssetToolsHelpers.get_asset_tools();A=unreal.EditorAssetLibrary;E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for name in ['SM_IV_FloatingUnderside','SM_IV_SkyLake','SM_IV_SkyRiver']:
 t=unreal.AssetImportTask();t.filename=str(B/'Saved/AdventureWorldSource'/(name+'.obj'));t.destination_path=R+'/Meshes/FloatingIsland';t.destination_name=name;t.automated=True;t.replace_existing=True;t.save=True
 op=unreal.FbxImportUI();op.set_editor_property('import_materials',False);op.set_editor_property('import_textures',False);op.static_mesh_import_data.set_editor_property('combine_meshes',True);op.static_mesh_import_data.set_editor_property('auto_generate_collision',False);t.options=op;T.import_asset_tasks([t])
 m=unreal.load_asset(R+'/Meshes/FloatingIsland/'+name)
 if 'Underside' in name:m.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 A.save_loaded_asset(m)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
