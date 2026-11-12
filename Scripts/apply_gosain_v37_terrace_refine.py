"""Replace the first terrace transition with the restrained valley-preserving version."""
import unreal,json,hashlib
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain37';R='/Game/IsekaiVillage/AdventureWorld/Gosain37'
data=json.loads((O/'Gosain37.json').read_text());terrain_report=json.loads((O/'terrain_report.json').read_text())
assert terrain_report['max_displacement_m']<=30.01
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();SS=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
assert W.get_path_name().startswith('/Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.')
def status(stage):
    (B/'Saved/Gosain37/terrace_refine_result.json').write_text(json.dumps({'stage':stage,'terrain':terrain_report,'house_count':data['report']['complete_houses']}));unreal.log('GOSAIN37_REFINE '+stage)
names=[q['name'] for q in data['meshes']]+['SM_IV_Continent_GosainTerraces37']
for name in names:
    mesh=unreal.load_asset(R+'/Meshes/'+name);assert mesh
    materials=[s.material_interface for s in mesh.static_materials]
    task=unreal.AssetImportTask();task.filename=str(O/(name+'.obj'));task.destination_path=R+'/Meshes';task.destination_name=name;task.automated=True;task.replace_existing=True;task.save=True
    op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;op.static_mesh_import_data.set_editor_property('normal_import_method',unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS);op.static_mesh_import_data.set_editor_property('generate_lightmap_u_vs',False);task.options=op
    status('importing '+name);T.import_asset_tasks([task]);mesh=unreal.load_asset(R+'/Meshes/'+name)
    for i,m in enumerate(materials):mesh.set_material(i,m)
    bs=SS.get_lod_build_settings(mesh,0);bs.recompute_normals=False;bs.generate_lightmap_u_vs=False;SS.set_lod_build_settings(mesh,0,bs);A.save_loaded_asset(mesh)
for key,instances in data['instances'].items():
    ft=unreal.load_asset(R+'/Foliage/FT_Gosain37_'+key);assert ft,key
    unreal.InstancedFoliageActor.remove_all_instances(W,ft)
    ts=[unreal.Transform(location=unreal.Vector(p[0]*100,p[1]*100,p[2]*100),rotation=unreal.Rotator(yaw=p[6]),scale=unreal.Vector(*p[3:6])) for p in instances]
    unreal.InstancedFoliageActor.add_instances(W,ft,ts)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
status('saved')
