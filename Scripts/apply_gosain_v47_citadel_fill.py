"""Add the summit district beside the saved basilica. Does not move existing actors."""
import unreal, json
from pathlib import Path
B = Path('D:/DEVELOPMENT/Games/IsekaiVillage')
O = B / 'ArtSource/World/Gosain47'
R = '/Game/IsekaiVillage/AdventureWorld'
assert (O / 'applied.json').exists()
assert not (O / 'citadel_fill_applied.json').exists()
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
T = unreal.AssetToolsHelpers.get_asset_tools()
A = unreal.EditorAssetLibrary
SS = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
name = 'SM_Gosain47_CitadelDistrict'
task = unreal.AssetImportTask()
task.filename = str(O / (name + '.obj'))
task.destination_path = R + '/Gosain47/Meshes'
task.destination_name = name
task.automated = True
task.replace_existing = True
task.save = True
op = unreal.FbxImportUI()
op.import_materials = False
op.import_textures = False
op.static_mesh_import_data.combine_meshes = True
op.static_mesh_import_data.auto_generate_collision = False
op.static_mesh_import_data.generate_lightmap_u_vs = False
op.static_mesh_import_data.normal_import_method = unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS
task.options = op
T.import_asset_tasks([task])
mesh = unreal.load_asset(R + '/Gosain47/Meshes/' + name)
assert mesh
mats = {
    'limestone': unreal.load_asset(R + '/Gosain42/Materials/M_Gosain42_limestone'),
    'ivory': unreal.load_asset(R + '/Gosain42/Materials/M_Gosain42_ivory'),
    'aged': unreal.load_asset(R + '/Gosain42/Materials/M_Gosain42_aged'),
    'warmstone': unreal.load_asset(R + '/Gosain42/Materials/M_Gosain42_warmstone'),
    'foundation': unreal.load_asset(R + '/Gosain42/Materials/M_Gosain42_foundation'),
    'trim': unreal.load_asset(R + '/Gosain42/Materials/M_Gosain42_trim'),
    'recess': unreal.load_asset(R + '/Gosain42/Materials/M_Gosain42_recess'),
    'roofstone': unreal.load_asset(R + '/Gosain42/Materials/M_Gosain42_roofstone'),
    'terracotta': unreal.load_asset(R + '/Gosain39/Materials/M_Gosain39_Terracotta'),
    'paving': unreal.load_asset(R + '/Gosain37/Materials/M_Gosain37_paving'),
}
slots = list(mesh.static_materials)
for slot in slots:
    slot.set_editor_property('material_interface', mats[str(slot.material_slot_name)])
mesh.set_editor_property('static_materials', slots)
nanite = mesh.get_editor_property('nanite_settings')
nanite.enabled = True
SS.set_nanite_settings(mesh, nanite, True)
A.save_loaded_asset(mesh)
actor = E.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, 0))
actor.static_mesh_component.set_static_mesh(mesh)
actor.set_actor_label('Gosain | Citadel District')
actor.set_folder_path('Regional Civilizations/Gosain/Packed City')
actor.tags = ['Gosain47', 'CitadelDistrict']
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(O / 'citadel_fill_applied.json').write_text(json.dumps({'status': 'saved', 'actor': actor.get_name()}))
unreal.log('GOSAIN47 citadel district saved')
