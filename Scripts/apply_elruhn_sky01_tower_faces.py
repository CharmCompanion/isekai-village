"""Correct exterior window normals in the new private tower mesh."""
import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/ElRuhnSky01';D='/Game/IsekaiVillage/AdventureWorld/ElRuhnSky01';name='SM_ElRuhnSky_GrandTower';A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools()
mesh=unreal.load_asset(D+'/Meshes/'+name);assert mesh
slots=list(mesh.static_materials)
task=unreal.AssetImportTask();task.filename=str(O/(name+'.obj'));task.destination_path=D+'/Meshes';task.destination_name=name;task.automated=True;task.save=True;task.replace_existing=True
op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;op.static_mesh_import_data.generate_lightmap_u_vs=False;op.static_mesh_import_data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;task.options=op;T.import_asset_tasks([task])
mesh=unreal.load_asset(D+'/Meshes/'+name);mesh.set_editor_property('static_materials',slots);mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);A.save_loaded_asset(mesh)
(O/'tower_normals_fixed.json').write_text(json.dumps({'outward_lancet_normals':True,'private_mesh_only':True}))
