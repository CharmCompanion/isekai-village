import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');R='/Game/IsekaiVillage/AdventureWorld'
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
a=next(a for a in E.get_all_level_actors() if a.get_name()=='StaticMeshActor_560')
old=a.static_mesh_component.static_mesh
assert old.get_name()=='SM_Civ36_Roads_OutsideGosain37',old.get_path_name()
backup=B/'Saved/WorldBackups/BeforeGosain38BridgeCleanup_20261015'
backup.mkdir(exist_ok=True)
import shutil
shutil.copy2(B/'Content/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.umap',backup/'Map_AnimeAdventure.umap')
name='SM_Civ36_Roads_OutsideOldGosainBridge38'
t=unreal.AssetImportTask();t.filename=str(B/'ArtSource/World/Gosain38'/(name+'.obj'));t.destination_path=R+'/Gosain38/Meshes';t.destination_name=name;t.automated=True;t.save=True
op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;op.static_mesh_import_data.generate_lightmap_u_vs=False;t.options=op
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
m=unreal.load_asset(t.destination_path+'/'+name);assert m
slots={str(s.material_slot_name):s.material_interface for s in old.static_materials}
for i,s in enumerate(m.static_materials):
    assert str(s.material_slot_name) in slots
    m.set_material(i,slots[str(s.material_slot_name)])
unreal.EditorAssetLibrary.save_loaded_asset(m)
a.static_mesh_component.set_static_mesh(m)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(B/'Saved/Gosain38/bridge_cleanup_result.json').write_text(json.dumps({'status':'saved','actor':a.get_name(),'old':old.get_path_name(),'new':m.get_path_name(),'removed_faces':77}))
