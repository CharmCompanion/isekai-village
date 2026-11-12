"""Import the packed Gosain city, place the arcane tower, and clear temporary town clutter inside the walls."""
import unreal, json, shutil, time, traceback
from pathlib import Path
B = Path('D:/DEVELOPMENT/Games/IsekaiVillage')
O = B / 'ArtSource/World/Gosain47'
O.mkdir(exist_ok=True)
(O / 'apply_progress.json').write_text(json.dumps({'stage': 'script_entered'}))
unreal.load_object(None, '/Script/UnrealEd.Default__EditorPerformanceSettings').set_editor_property('bThrottleCPUWhenNotForeground', False)
unreal.SystemLibrary.execute_console_command(None, 't.IdleWhenNotForeground 0')
R = '/Game/IsekaiVillage/AdventureWorld'
D = R + '/Gosain47'
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
W = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
T = unreal.AssetToolsHelpers.get_asset_tools()
A = unreal.EditorAssetLibrary
SS = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
assert W.get_path_name().startswith(R + '/Maps/Map_AnimeAdventure.')
assert (B / 'ArtSource/World/Gosain44/applied.json').exists()
assert not (O / 'applied.json').exists(), 'Already applied'
assert not (B / 'ArtSource/World/Gosain45/applied.json').exists(), 'Tower already placed'
report = {'stage': 'preflight'}

def status(s):
    report['stage'] = s
    (O / 'apply_progress.json').write_text(json.dumps(report, indent=2))
    unreal.log('GOSAIN47 ' + s)

MATS = {
    'limestone': R + '/Gosain42/Materials/M_Gosain42_limestone',
    'ivory': R + '/Gosain42/Materials/M_Gosain42_ivory',
    'aged': R + '/Gosain42/Materials/M_Gosain42_aged',
    'warmstone': R + '/Gosain42/Materials/M_Gosain42_warmstone',
    'foundation': R + '/Gosain42/Materials/M_Gosain42_foundation',
    'trim': R + '/Gosain42/Materials/M_Gosain42_trim',
    'recess': R + '/Gosain42/Materials/M_Gosain42_recess',
    'roofstone': R + '/Gosain42/Materials/M_Gosain42_roofstone',
    'terracotta': R + '/Gosain39/Materials/M_Gosain39_Terracotta',
    'paving': R + '/Gosain37/Materials/M_Gosain37_paving',
}
materials = {k: unreal.load_asset(v) for k, v in MATS.items()}
assert all(materials.values()), [k for k, v in materials.items() if not v]
for mat in materials.values():
    try:
        mat.set_editor_property('used_with_nanite', True)
    except Exception:
        pass

def pip(x, y, ring):
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi):
            inside = not inside
        j = i
    return inside

plan = json.loads((B / 'ArtSource/World/Gosain38/whole_island_plan.json').read_text())
rings = []
for island in plan['islands']:
    ring = island['wall_boundary_m']
    xs = [p[0] for p in ring]
    ys = [p[1] for p in ring]
    rings.append((ring, min(xs), max(xs), min(ys), max(ys)))

def inside_walls(x, y):
    for ring, x0, x1, y0, y1 in rings:
        if x0 <= x <= x1 and y0 <= y <= y1 and pip(x, y, ring):
            return True
    return False

def import_obj(filename, name, folder):
    status('importing ' + name)
    task = unreal.AssetImportTask()
    task.filename = str(filename)
    task.destination_path = folder
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
    mesh = unreal.load_asset(folder + '/' + name)
    assert mesh, name
    return mesh

def assign_named(mesh):
    slots = list(mesh.static_materials)
    for slot in slots:
        mat = materials[str(slot.material_slot_name)]
        slot.set_editor_property('material_interface', mat)
    mesh.set_editor_property('static_materials', slots)
    nanite = mesh.get_editor_property('nanite_settings')
    nanite.enabled = True
    SS.set_nanite_settings(mesh, nanite, True)
    A.save_loaded_asset(mesh)

city = json.loads((O / 'city.json').read_text())
actors = E.get_all_level_actors()
before = {}
for actor in actors:
    loc = actor.get_actor_location()
    mesh = None
    comps = actor.get_components_by_class(unreal.StaticMeshComponent)
    if len(comps) == 1 and not isinstance(comps[0], unreal.InstancedStaticMeshComponent) and comps[0].static_mesh:
        mesh = comps[0].static_mesh.get_path_name()
    before[actor.get_name()] = (loc.x, loc.y, loc.z, actor.is_hidden_ed(), mesh, actor.get_actor_label())

backup = B / 'Saved/WorldBackups' / ('BeforeGosain47_' + time.strftime('%Y%m%d_%H%M%S'))
backup.mkdir(parents=True)
shutil.copy2(B / 'Content/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.umap', backup / 'Map_AnimeAdventure.umap')
spawned = []
hidden = []
swapped = []
try:
    imported = []
    for info in city['meshes']:
        mesh = import_obj(O / (info['name'] + '.obj'), info['name'], D + '/Meshes')
        assign_named(mesh)
        imported.append((info['name'], mesh))
    roads = import_obj(O / 'SM_Gosain47_RoadsOutsideCity.obj', 'SM_Gosain47_RoadsOutsideCity', D + '/Meshes')
    pads = import_obj(O / 'SM_Gosain47_FoundationsOutsideCity.obj', 'SM_Gosain47_FoundationsOutsideCity', D + '/Meshes')
    tower_q = json.loads((B / 'ArtSource/World/Gosain45/tower.json').read_text())
    tower = import_obj(B / 'ArtSource/World/Gosain45' / (tower_q['name'] + '.obj'), tower_q['name'], R + '/Gosain45/Meshes')
    status('placing tower')
    def make_material(name):
        path = R + '/Gosain45/Materials/' + name
        if A.does_asset_exist(path):
            return unreal.load_asset(path)
        return unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, R + '/Gosain45/Materials', unreal.Material, unreal.MaterialFactoryNew())
    gold = make_material('M_Gosain45_Gold')
    M = unreal.MaterialEditingLibrary
    def const_color(mat, color, prop):
        node = M.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector)
        node.constant = unreal.LinearColor(*color, 1)
        M.connect_material_property(node, '', prop)
    const_color(gold, (0.58, 0.36, 0.09), unreal.MaterialProperty.MP_BASE_COLOR)
    rough = M.create_material_expression(gold, unreal.MaterialExpressionConstant)
    rough.r = 0.3
    M.connect_material_property(rough, '', unreal.MaterialProperty.MP_ROUGHNESS)
    metal = M.create_material_expression(gold, unreal.MaterialExpressionConstant)
    metal.r = 0.65
    M.connect_material_property(metal, '', unreal.MaterialProperty.MP_METALLIC)
    M.recompile_material(gold)
    A.save_loaded_asset(gold)
    glass = unreal.AssetToolsHelpers.get_asset_tools().create_asset('M_Gosain45_CyanCrystal', R + '/Gosain45/Materials', unreal.Material, unreal.MaterialFactoryNew())
    const_color(glass, (0.015, 0.44, 0.65), unreal.MaterialProperty.MP_BASE_COLOR)
    emit = M.create_material_expression(glass, unreal.MaterialExpressionConstant3Vector)
    emit.constant = unreal.LinearColor(0.03, 0.75, 1.1, 1)
    M.connect_material_property(emit, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    M.recompile_material(glass)
    A.save_loaded_asset(glass)
    magic = unreal.AssetToolsHelpers.get_asset_tools().create_asset('M_Gosain45_ArcaneOrbit', R + '/Gosain45/Materials', unreal.Material, unreal.MaterialFactoryNew())
    const_color(magic, (0.03, 0.56, 0.85), unreal.MaterialProperty.MP_BASE_COLOR)
    emit = M.create_material_expression(magic, unreal.MaterialExpressionConstant3Vector)
    emit.constant = unreal.LinearColor(0.1, 1.6, 2.4, 1)
    M.connect_material_property(emit, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    M.recompile_material(magic)
    A.save_loaded_asset(magic)
    tower_mats = {
        'stone': materials['ivory'], 'trim': materials['trim'], 'foundation': materials['foundation'], 'recess': materials['recess'],
        'gold': gold, 'glass': glass, 'magic': magic,
    }
    slots = list(tower.static_materials)
    for slot in slots:
        slot.set_editor_property('material_interface', tower_mats[str(slot.material_slot_name)])
    tower.set_editor_property('static_materials', slots)
    nanite = tower.get_editor_property('nanite_settings')
    nanite.enabled = True
    SS.set_nanite_settings(tower, nanite, True)
    A.save_loaded_asset(tower)
    origin = tower_q['origin_m']
    tower_actor = E.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(origin[0] * 100, origin[1] * 100, origin[2] * 100))
    tower_actor.static_mesh_component.set_static_mesh(tower)
    tower_actor.set_actor_label('Gosain | Great Arcane Tower 45')
    tower_actor.set_folder_path('Regional Civilizations/Gosain/Arcane Landmark')
    tower_actor.tags = ['Gosain45', 'Gosain47', 'ApprovedConceptLandmark']
    spawned.append(tower_actor)
    status('placing city')
    for name, mesh in imported:
        actor = E.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, 0))
        actor.static_mesh_component.set_static_mesh(mesh)
        actor.set_actor_label('Gosain | ' + name)
        actor.set_folder_path('Regional Civilizations/Gosain/Packed City')
        actor.tags = ['Gosain47', 'PackedCity']
        spawned.append(actor)
    def find_label(text):
        found = [a for a in E.get_all_level_actors() if text in str(a.get_actor_label())]
        assert len(found) == 1, (text, len(found))
        return found[0]
    for actor, mesh in ((find_label('Town streets, plazas and bridges'), roads), (find_label('House pads'), pads)):
        old = actor.static_mesh_component.static_mesh
        slots = list(mesh.static_materials)
        source_slots = list(old.static_materials)
        for i, slot in enumerate(slots):
            slot.set_editor_property('material_interface', source_slots[min(i, len(source_slots) - 1)].material_interface)
        mesh.set_editor_property('static_materials', slots)
        A.save_loaded_asset(mesh)
        actor.static_mesh_component.set_static_mesh(mesh)
        swapped.append(actor.get_name())
    for label in ('Gosain | CityStreets', 'Gosain | PrecinctWalls', 'Gosain | HouseFootings', 'Gosain | Capital infill foundations'):
        actor = find_label(label)
        hidden.append({'name': actor.get_name(), 'was_hidden': actor.is_hidden_ed()})
        actor.set_actor_hidden_in_game(True)
        actor.set_is_temporarily_hidden_in_editor(True)
        actor.static_mesh_component.set_visibility(False, True)
    status('clearing temporary buildings inside the walls')
    removed = 0
    kept = 0
    for actor in E.get_all_level_actors():
        for comp in actor.get_components_by_class(unreal.InstancedStaticMeshComponent):
            count = comp.get_instance_count()
            if count == 0:
                continue
            drop = []
            for i in range(count):
                p = comp.get_instance_transform(i, True).translation
                if inside_walls(p.x / 100.0, p.y / 100.0):
                    drop.append(i)
            if not drop:
                kept += count
                continue
            for i in reversed(drop):
                comp.remove_instance(i)
            removed += len(drop)
            kept += count - len(drop)
    report['foliage_removed_inside_walls'] = removed
    report['foliage_kept'] = kept
    status('checking unrelated actors')
    after = {a.get_name(): a for a in E.get_all_level_actors()}
    for name, (x, y, z, was_hidden, mesh, label) in before.items():
        actor = after[name]
        loc = actor.get_actor_location()
        assert abs(loc.x - x) < 0.1 and abs(loc.y - y) < 0.1 and abs(loc.z - z) < 0.1, name
        if name in swapped or any(h['name'] == name for h in hidden):
            continue
        assert actor.is_hidden_ed() == was_hidden, name
        comps = actor.get_components_by_class(unreal.StaticMeshComponent)
        if mesh and len(comps) == 1 and not isinstance(comps[0], unreal.InstancedStaticMeshComponent):
            assert comps[0].static_mesh.get_path_name() == mesh, name
    assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception:
    (O / 'apply_error.txt').write_text(traceback.format_exc())
    for actor in spawned:
        E.destroy_actor(actor)
    raise
result = {
    'status': 'saved',
    'actors': [a.get_name() for a in spawned],
    'swapped': swapped,
    'hidden': hidden,
    'backup': str(backup),
    'buildings': city['buildings'],
    'foliage_removed_inside_walls': report['foliage_removed_inside_walls'],
    'limitations': city['limitations'] + ['Temporary foliage inside the walls was removed. Outside-wall instances were kept.'],
}
(O / 'applied.json').write_text(json.dumps(result, indent=2))
(B / 'ArtSource/World/Gosain45/applied.json').write_text(json.dumps({'status': 'saved', 'via': 'Gosain47', 'actor': spawned[0].get_name(), 'origin_m': origin}, indent=2))
status('saved')

views = [
    ('Both_Islands', (28000, 30000, -17600), (18000, 40000, -20450)),
    ('Capital_City', (25500, 39500, -19200), (22200, 41800, -20440)),
    ('Citadel', (23200, 41200, -20040), (22474, 42290, -20370)),
    ('Tower', (15800, 39200, -19850), (14834, 39945, -20280)),
    ('Bridge', (20800, 41600, -20140), (19640, 42590, -20520)),
    ('Street', (22174, 41625, -20428), (22440, 41625, -20448)),
]
output = B / 'Docs/WorldDesign/Gosain47'
output.mkdir(exist_ok=True)
state = {'i': 0, 'phase': 0, 'next': time.monotonic() + 20, 'done': []}
handle = {}

def tick(dt):
    if time.monotonic() < state['next']:
        return
    if state['i'] >= len(views):
        unreal.unregister_slate_post_tick_callback(handle['h'])
        (output / 'native_views_complete.json').write_text(json.dumps({'status': 'captured', 'files': state['done']}))
        return
    name, eye, target = views[state['i']]
    if state['phase'] == 0:
        p = unreal.Vector(eye[0] * 100, eye[1] * 100, eye[2] * 100)
        q = unreal.Vector(target[0] * 100, target[1] * 100, target[2] * 100)
        unreal.EditorLevelLibrary.set_level_viewport_camera_info(p, unreal.MathLibrary.find_look_at_rotation(p, q))
        state.update(phase=1, next=time.monotonic() + 8)
    elif state['phase'] == 1:
        path = output / (name + '.png')
        state.update(phase=2, next=time.monotonic() + 2, started=time.monotonic(), old=path.stat().st_mtime if path.exists() else 0)
        unreal.AutomationLibrary.take_high_res_screenshot(1600, 1000, str(path), delay=0.5)
    else:
        path = output / (name + '.png')
        if path.exists() and path.stat().st_mtime > state['old']:
            state['done'].append(str(path))
            state.update(i=state['i'] + 1, phase=0, next=time.monotonic() + 2)
        elif time.monotonic() - state['started'] > 90:
            state['done'].append('FAILED ' + name)
            state.update(i=state['i'] + 1, phase=0, next=time.monotonic() + 2)

handle['h'] = unreal.register_slate_post_tick_callback(tick)
