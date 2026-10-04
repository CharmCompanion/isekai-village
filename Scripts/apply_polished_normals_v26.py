import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource';R='/Game/IsekaiVillage/AdventureWorld'
A=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);T=unreal.AssetToolsHelpers.get_asset_tools();w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
def progress(stage,**kw):(B/'Saved/puzzle_continent_result.json').write_text(json.dumps(dict(stage=stage,**kw),indent=2))
progress('importing')
name='SM_IV_PuzzleContinent_v26';t=unreal.AssetImportTask();t.filename=str(S/(name+'.obj'));t.destination_path=R+'/Meshes/Refinement';t.destination_name=name;t.automated=True;t.replace_existing=True;t.save=True
op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;op.static_mesh_import_data.set_editor_property('normal_import_method',unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS);t.options=op;T.import_asset_tasks([t]);mesh=unreal.load_asset(t.destination_path+'/'+name)
ss=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);bs=ss.get_lod_build_settings(mesh,0);bs.recompute_normals=False;ss.set_lod_build_settings(mesh,0,bs);A.save_loaded_asset(mesh)

for a in E.get_all_level_actors():
 if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name()==name:
  a.static_mesh_component.set_material(0,unreal.load_asset(R+'/Materials/M_IV_LivingContinent_Final26'))
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
progress('saved with refined scenic normals')
exec(compile((B/'Scripts/render_puzzle_continent_v26.py').read_text(),'final shaded views','exec'),{'__name__':'__main__'})
