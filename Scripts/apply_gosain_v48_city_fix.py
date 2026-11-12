"""Swap the packed Gosain city meshes for the townhouse rebuild. Does not move the tower or touch foliage."""
import unreal, json, shutil, time, traceback
from pathlib import Path
B = Path('D:/DEVELOPMENT/Games/IsekaiVillage')
O = B / 'ArtSource/World/Gosain48'
(O / 'apply_progress.json').write_text(json.dumps({'stage': 'script_entered'}))
unreal.load_object(None, '/Script/UnrealEd.Default__EditorPerformanceSettings').set_editor_property('bThrottleCPUWhenNotForeground', False)
unreal.SystemLibrary.execute_console_command(None, 't.IdleWhenNotForeground 0')
R = '/Game/IsekaiVillage/AdventureWorld'
D = R + '/Gosain48'
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
W = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
T = unreal.AssetToolsHelpers.get_asset_tools()
A = unreal.EditorAssetLibrary
SS = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
assert W.get_path_name().startswith(R + '/Maps/Map_AnimeAdventure.')
assert (B / 'ArtSource/World/Gosain47/applied.json').exists()
assert not (O / 'applied.json').exists(), 'Already applied'
report = {'stage': 'preflight'}

def status(s):
    report['stage'] = s
    (O / 'apply_progress.json').write_text(json.dumps(report, indent=2))
    unreal.log('GOSAIN48 ' + s)

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
backup = B / 'Saved/WorldBackups' / ('BeforeGosain48_' + time.strftime('%Y%m%d_%H%M%S'))
backup.mkdir(parents=True)
shutil.copy2(B / 'Content/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.umap', backup / 'Map_AnimeAdventure.umap')
swapped = []
try:
    imported = {}
    for info in city['meshes']:
        mesh = import_obj(O / (info['name'] + '.obj'), info['name'], D + '/Meshes')
        assign_named(mesh)
        imported[info['name']] = mesh
    pairs = (
        ('Gosain | SM_Gosain47_Capital', 'SM_Gosain48_Capital'),
        ('Gosain | SM_Gosain47_FarSouth', 'SM_Gosain48_FarSouth'),
        ('Gosain | SM_Gosain47_FarNorth', 'SM_Gosain48_FarNorth'),
        ('Gosain | SM_Gosain47_Citadel', 'SM_Gosain48_Citadel'),
    )
    status('swapping city meshes')
    for label, name in pairs:
        found = [a for a in E.get_all_level_actors() if str(a.get_actor_label()) == label]
        assert len(found) == 1, (label, len(found))
        actor = found[0]
        actor.static_mesh_component.set_static_mesh(imported[name])
        actor.set_actor_label('Gosain | ' + name)
        swapped.append({'actor': actor.get_name(), 'label': 'Gosain | ' + name, 'mesh': name})
    assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception:
    (O / 'apply_error.txt').write_text(traceback.format_exc())
    raise
result = {
    'status': 'saved',
    'swapped': swapped,
    'backup': str(backup),
    'buildings': city['buildings'],
    'limitations': city['limitations'],
}
(O / 'applied.json').write_text(json.dumps(result, indent=2))
status('saved')

views = [
    ('Both_Islands', (28000, 30000, -17600), (18000, 40000, -20450)),
    ('Capital_City', (25500, 39500, -19200), (22200, 41800, -20440)),
    ('Citadel', (23200, 41200, -20040), (22474, 42290, -20370)),
    ('Tower', (15800, 39200, -19850), (14834, 39945, -20280)),
    ('Bridge', (20800, 41600, -20140), (19640, 42590, -20520)),
    ('Street', (22174, 41625, -20453), (22340, 41625, -20454)),
]
output = B / 'Docs/WorldDesign/Gosain48'
output.mkdir(exist_ok=True)
state = {'i': 0, 'phase': 0, 'next': time.monotonic() + 12, 'done': []}
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
