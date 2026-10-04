import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource';R='/Game/IsekaiVillage/AdventureWorld';T=unreal.AssetToolsHelpers.get_asset_tools();A=unreal.EditorAssetLibrary;W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
name='SM_Civ29_Roads';path=R+'/Meshes/Civilizations/'+name;mesh=unreal.load_asset(path);materials=list(mesh.static_materials);t=unreal.AssetImportTask();t.filename=str(S/'Civilizations29'/(name+'.obj'));t.destination_path=R+'/Meshes/Civilizations';t.destination_name=name;t.automated=True;t.replace_existing=True;t.save=True;op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;op.static_mesh_import_data.set_editor_property('normal_import_method',unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS);t.options=op;T.import_asset_tasks([t]);mesh=unreal.load_asset(path);mesh.set_editor_property('static_materials',materials);A.save_loaded_asset(mesh)
data=json.loads((S/'civilization_instances_v29.json').read_text())
for key in ['Oak','Pine','Palm','DesertPalm']:
 ft=unreal.load_asset(R+'/Foliage/Civilizations/FT_Civ29_'+key);unreal.InstancedFoliageActor.remove_all_instances(W,ft);rows=data['instances'][key];unreal.InstancedFoliageActor.add_instances(W,ft,[unreal.Transform(location=unreal.Vector(p[0]*100,p[1]*100,p[2]*100),rotation=unreal.Rotator(yaw=p[6]),scale=unreal.Vector(*p[3:6])) for p in rows])
exec(compile((B/'Scripts/polish_civilization_palette_v29.py').read_text(),'regional material finish','exec'),{'__name__':'__main__'})
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
exec(compile((B/'Scripts/render_puzzle_continent_v29.py').read_text(),'final regions','exec'),{'__name__':'__main__'})
