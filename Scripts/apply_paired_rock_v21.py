import unreal
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');R='/Game/IsekaiVillage/AdventureWorld';A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools()
name='SM_IV_JoinedMountain_v21';t=unreal.AssetImportTask();t.filename=str(B/'Saved/AdventureWorldSource'/(name+'.obj'));t.destination_path=R+'/Meshes/Refinement';t.destination_name=name;t.automated=True;t.replace_existing=True;t.save=True
op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;op.static_mesh_import_data.set_editor_property('normal_import_method',unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS);t.options=op;T.import_asset_tasks([t]);m=unreal.load_asset(t.destination_path+'/'+name)
ss=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);bs=ss.get_lod_build_settings(m,0);bs.recompute_normals=False;ss.set_lod_build_settings(m,0,bs);m.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);A.save_loaded_asset(m)
count=0
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if isinstance(a,unreal.StaticMeshActor):
  c=a.static_mesh_component
  if c.static_mesh and c.is_visible() and c.static_mesh.get_name() in ['SM_IV_JoinedMountain_v13',name]:
   c.set_static_mesh(m);c.set_material(0,unreal.load_asset(R+'/Materials/M_IV_JoinedGeology_v13'));count+=1
assert count==1
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
