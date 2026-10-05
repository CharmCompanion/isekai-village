"""v32b: swap the lake surface for the grid mesh, trim the spillway ribbon to the
lake outline, floor the bottomless western bay with sand, and clear the water so
the sandy bed and caustics read near the shore (SoStylized Demonstration lake).
Run inside the editor on Map_AnimeAdventure after build_sky_lake_grid_v32.py.
"""
import unreal, json
from pathlib import Path

B = Path('D:/DEVELOPMENT/Games/IsekaiVillage'); S = B / 'Saved/AdventureWorldSource'
R = '/Game/IsekaiVillage/AdventureWorld'
A = unreal.EditorAssetLibrary; M = unreal.MaterialEditingLibrary
T = unreal.AssetToolsHelpers.get_asset_tools()
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert w.get_path_name().startswith(R + '/Maps/Map_AnimeAdventure.'), w.get_path_name()
report = {}

water = unreal.load_asset(R + '/Materials/MI_IV_SkyLake'); assert water


def reimport(name, folder):
    """Reimport over the existing asset so every actor reference stays valid."""
    t = unreal.AssetImportTask()
    t.filename = str(S / (name + '.obj')); t.destination_path = R + folder
    t.destination_name = name; t.automated = True; t.replace_existing = True; t.save = True
    op = unreal.FbxImportUI(); op.import_materials = False; op.import_textures = False
    op.static_mesh_import_data.combine_meshes = True; op.static_mesh_import_data.auto_generate_collision = False
    t.options = op
    T.import_asset_tasks([t])
    m = unreal.load_asset(R + folder + '/' + name); assert m, name
    m.set_material(0, water); A.save_loaded_asset(m)
    report[name] = {'triangles': m.get_num_triangles(0), 'vertices': m.get_num_vertices(0)}
    return m


lake = reimport('SM_IV_GrandSkyLake', '/Meshes/Refinement')
assert report['SM_IV_GrandSkyLake']['triangles'] > 1000, report
river = reimport('SM_IV_SkyRiver', '/Meshes/FloatingIsland')
for label, mesh in [('SM_IV_SkyLake', lake), ('SM_IV_SkyRiver', river)]:
    actors = [a for a in E.get_all_level_actors() if a.get_actor_label() == label]
    assert actors, label + ' actor missing'
    for a in actors:
        a.static_mesh_component.set_static_mesh(mesh); a.static_mesh_component.set_material(0, water)
        a.static_mesh_component.set_cast_shadow(False)
    report[label + '_actors'] = len(actors)

# Sand floor for the bottomless western bay (see build_sky_lake_grid_v32.py).
bedmat_path = R + '/Materials/M_IV_LakeBed32'
bedmat = unreal.load_asset(bedmat_path) if A.does_asset_exist(bedmat_path) else T.create_asset('M_IV_LakeBed32', R + '/Materials', unreal.Material, unreal.MaterialFactoryNew())
M.delete_all_material_expressions(bedmat)
pos = M.create_material_expression(bedmat, unreal.MaterialExpressionWorldPosition)
n = M.create_material_expression(bedmat, unreal.MaterialExpressionCustom)
pin = unreal.CustomInput(); pin.set_editor_property('input_name', 'P'); n.set_editor_property('inputs', [pin])
n.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT3)
# Rippled sand matching the landscape Sand Tint (0.90, 0.84, 0.58), slightly darker for a wet bed.
n.set_editor_property('code', 'float3 p=P/100.;float r=.9+.08*sin(p.x*1.7+sin(p.y*1.1))*cos(p.y*1.3)+.04*sin((p.x+p.y)*4.1);return float3(0.72,0.66,0.44)*r;')
M.connect_material_expressions(pos, '', n, 'P'); M.connect_material_property(n, '', unreal.MaterialProperty.MP_BASE_COLOR)
rough = M.create_material_expression(bedmat, unreal.MaterialExpressionConstant); rough.r = .92
M.connect_material_property(rough, '', unreal.MaterialProperty.MP_ROUGHNESS)
M.recompile_material(bedmat); A.save_loaded_asset(bedmat)

tb = unreal.AssetImportTask()
tb.filename = str(S / 'SM_IV_LakeBed.obj'); tb.destination_path = R + '/Meshes/Refinement'
tb.destination_name = 'SM_IV_LakeBed'; tb.automated = True; tb.replace_existing = True; tb.save = True
opb = unreal.FbxImportUI(); opb.import_materials = False; opb.import_textures = False
opb.static_mesh_import_data.combine_meshes = True; opb.static_mesh_import_data.auto_generate_collision = False
tb.options = opb
T.import_asset_tasks([tb])
bed = unreal.load_asset(R + '/Meshes/Refinement/SM_IV_LakeBed'); assert bed
bed.set_material(0, bedmat); A.save_loaded_asset(bed)
BED_LABEL = 'Lake bed - sand floor under the western bay'
for a in E.get_all_level_actors():
    if a.get_actor_label() == BED_LABEL:
        E.destroy_actor(a)
a = E.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, 0), unreal.Rotator())
a.static_mesh_component.set_static_mesh(bed); a.static_mesh_component.set_material(0, bedmat)
a.set_actor_label(BED_LABEL); a.set_folder_path('Floating Island'); a.tags = [unreal.Name('IVStylized32')]
a.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
report['lake_bed'] = {'triangles': bed.get_num_triangles(0), 'z_m': 9.3}

# Clearer water: the Demonstration lake shows the bed and caustics for several
# metres before the colour saturates; keep the turquoise tint but lower the murk.
names = [str(n) for n in M.get_scalar_parameter_names(water)]
for k, v in [('Water Murkiness', .22), ('Water Scattering', .14), ('Caustic Strength', 48.), ('Foam Multiply', 1.25), ('Distance', 80.)]:
    assert k in names, (k, names)
    M.set_material_instance_scalar_parameter_value(water, k, v); report['water_' + k] = v
A.save_loaded_asset(water)

# The inverted-mountain foundation is a closed 1.2 km volume under the landscape.
# Lumen treats that as a cave, so the western lake and dungeon path shade as if
# they are underground (the hard wedge on the water). Keep the mesh for the
# underside view; stop it — and leftover archived shells — contributing to GI/SDF.
FOUND = ('El Ruhn - matching rock foundation', 'El Ruhn - rim rock collar v31')
n_gi = 0
for a in E.get_all_level_actors():
    if not isinstance(a, unreal.StaticMeshActor):
        continue
    folder = str(a.get_folder_path())
    if a.get_actor_label() not in FOUND and not folder.startswith('Archived/'):
        continue
    c = a.static_mesh_component
    c.set_editor_property('affect_distance_field_lighting', False)
    c.set_editor_property('affect_dynamic_indirect_lighting', False)
    if folder.startswith('Archived/'):
        a.set_actor_hidden_in_game(True); a.set_actor_enable_collision(False)
        c.set_visibility(False, True); c.set_cast_shadow(False)
    n_gi += 1
report['foundation_gi_actors'] = n_gi

unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(B / 'Saved/sky_lake_v32_result.json').write_text(json.dumps(report, indent=2))
unreal.log('V32B_APPLIED ' + json.dumps(report))
