"""Weather the saved Gosain city: stone, broken plaster, ivy, terracotta tiles, cobbles.

Assigns new materials onto the Gosain48 meshes. Does not rebuild or move the city.
"""
import unreal, json, time, traceback
from pathlib import Path
B = Path('D:/DEVELOPMENT/Games/IsekaiVillage')
O = B / 'ArtSource/World/Gosain49'
R = '/Game/IsekaiVillage/AdventureWorld'
D = R + '/Gosain49'
A = unreal.EditorAssetLibrary
T = unreal.AssetToolsHelpers.get_asset_tools()
M = unreal.MaterialEditingLibrary
(O / 'apply_progress.json').write_text(json.dumps({'stage': 'script_entered'}))
unreal.load_object(None, '/Script/UnrealEd.Default__EditorPerformanceSettings').set_editor_property('bThrottleCPUWhenNotForeground', False)
report = {'stage': 'preflight'}

def status(s):
    report['stage'] = s
    (O / 'apply_progress.json').write_text(json.dumps(report, indent=2))
    unreal.log('GOSAIN49 ' + s)

def node(mat, cls):
    return M.create_material_expression(mat, cls)

def custom(mat, code, inputs, typ):
    expr = node(mat, unreal.MaterialExpressionCustom)
    pins = []
    for name in inputs:
        pin = unreal.CustomInput()
        pin.set_editor_property('input_name', name)
        pins.append(pin)
    expr.set_editor_property('inputs', pins)
    expr.set_editor_property('output_type', typ)
    expr.set_editor_property('code', code)
    for name, src in inputs.items():
        assert M.connect_material_expressions(src, '', expr, name)
    return expr

def import_png(filename, name, srgb):
    status('importing ' + name)
    task = unreal.AssetImportTask()
    task.filename = str(O / filename)
    task.destination_path = D + '/Textures'
    task.destination_name = name
    task.automated = True
    task.replace_existing = True
    task.save = True
    T.import_asset_tasks([task])
    tex = unreal.load_asset(D + '/Textures/' + name)
    assert tex, name
    tex.set_editor_property('srgb', srgb)
    if not srgb:
        tex.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_GRAYSCALE)
    A.save_loaded_asset(tex)
    return tex

def triplanar(mat, position, texture, scale, sampler=None):
    samples = []
    for axis in ('yz', 'xz', 'xy'):
        uv = custom(mat, 'return P.%s/%s;' % (axis, float(scale)), {'P': position}, unreal.CustomMaterialOutputType.CMOT_FLOAT2)
        sample = node(mat, unreal.MaterialExpressionTextureSample)
        sample.texture = texture
        if sampler is not None:
            sample.sampler_type = sampler
        assert M.connect_material_expressions(uv, '', sample, 'UVs')
        samples.append(sample)
    return samples

def finish(mat, color, roughness):
    mat.set_editor_property('used_with_nanite', True)
    assert M.connect_material_property(color, '', unreal.MaterialProperty.MP_BASE_COLOR)
    rough = node(mat, unreal.MaterialExpressionConstant)
    rough.r = roughness
    assert M.connect_material_property(rough, '', unreal.MaterialProperty.MP_ROUGHNESS)
    M.recompile_material(mat)
    A.save_loaded_asset(mat)
    return mat

def make(name):
    path = D + '/Materials/M_Gosain49_' + name
    mat = unreal.load_asset(path) if A.does_asset_exist(path) else T.create_asset('M_Gosain49_' + name, D + '/Materials', unreal.Material, unreal.MaterialFactoryNew())
    M.delete_all_material_expressions(mat)
    return mat

try:
    W = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    assert W.get_path_name().startswith(R + '/Maps/Map_AnimeAdventure.')
    break_tex = import_png('T_Gosain49_Break.png', 'T_Gosain49_Break', False)
    ivy_tex = import_png('T_Gosain49_Ivy.png', 'T_Gosain49_Ivy', True)
    stone_tex = unreal.load_asset('/Game/Fantastic_Village_Pack/textures/T_stonebrick_01_BC')
    dress_tex = unreal.load_asset('/Game/Fantastic_Village_Pack/textures/T_ENV_stone_BC')
    roof_tex = unreal.load_asset('/Game/Fantastic_Village_Pack/textures/T_rooftiles_01_BC')
    cobble_tex = unreal.load_asset('/Game/Fantastic_Village_Pack/textures/T_ENV_pavingstone_01_BC')
    assert all([stone_tex, dress_tex, roof_tex, cobble_tex])
    recess = unreal.load_asset(R + '/Gosain42/Materials/M_Gosain42_recess')
    assert recess

    def wall(name, texture, plaster, peel, ivy_amount, scale):
        status('material ' + name)
        mat = make(name)
        position = node(mat, unreal.MaterialExpressionWorldPosition)
        normal = node(mat, unreal.MaterialExpressionVertexNormalWS)
        stone = triplanar(mat, position, texture, scale)
        broken = triplanar(mat, position, break_tex, 860, unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_GRAYSCALE)
        vines = triplanar(mat, position, ivy_tex, 700)
        code = '''
float3 w = pow(abs(N), 4);
w /= max(w.x + w.y + w.z, 0.0001);
float3 stone = SA * w.x + SB * w.y + SC * w.z;
float br = dot(BA * w.x + BB * w.y + BC * w.z, float3(0.33, 0.5, 0.17));
float blot = smoothstep(0.78, 0.93, frac(sin(dot(floor(P.xyz / 420.0), float3(12.989, 78.233, 37.719))) * 43758.5453));
float peelAmt = saturate(smoothstep(0.62, 0.84, br + %s) + blot);
float3 plaster = float3(%s, %s, %s);
float3 wall = lerp(plaster, stone * float3(1.15, 0.82, 0.55), peelAmt);
float3 ivy = IA * w.x + IB * w.y + IC * w.z;
float a = AA * w.x + AB * w.y + AC * w.z;
float2 uv = float2(P.x + P.y, P.z) / 340.0;
float stem = smoothstep(0.05, 0.0, abs(frac(uv.x * 0.42 + 0.1 * sin(uv.y * 2.4)) - 0.5) - 0.455);
float leaf = smoothstep(0.2, 0.02, length(frac(uv * float2(0.85, 0.4)) - float2(0.18, 0.5)));
float vine = saturate(stem + leaf * stem * 1.6);
float cell = frac(sin(floor(P.x / 1400.0) * 12.9898 + floor(P.y / 1400.0) * 78.233) * 43758.5453);
float grow = smoothstep(0.22, 0.55, cell) * %s;
float3 ivyCol = lerp(float3(0.04, 0.28, 0.07), ivy, saturate(a));
wall = lerp(wall, ivyCol, saturate(max(a, vine) * grow));
float macro = 0.88 + 0.12 * sin(P.x / 4800.0) * cos(P.y / 4100.0);
return wall * macro;
''' % (peel, plaster[0], plaster[1], plaster[2], ivy_amount)
        color = node(mat, unreal.MaterialExpressionCustom)
        pins = []
        for pin_name in ('P', 'N', 'SA', 'SB', 'SC', 'BA', 'BB', 'BC', 'IA', 'IB', 'IC', 'AA', 'AB', 'AC'):
            pin = unreal.CustomInput()
            pin.set_editor_property('input_name', pin_name)
            pins.append(pin)
        color.set_editor_property('inputs', pins)
        color.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT3)
        color.set_editor_property('code', code)
        links = {
            'P': (position, ''), 'N': (normal, ''),
            'SA': (stone[0], ''), 'SB': (stone[1], ''), 'SC': (stone[2], ''),
            'BA': (broken[0], ''), 'BB': (broken[1], ''), 'BC': (broken[2], ''),
            'IA': (vines[0], ''), 'IB': (vines[1], ''), 'IC': (vines[2], ''),
            'AA': (vines[0], 'A'), 'AB': (vines[1], 'A'), 'AC': (vines[2], 'A'),
        }
        for pin_name, (src, output) in links.items():
            assert M.connect_material_expressions(src, output, color, pin_name), pin_name
        return finish(mat, color, 0.9)

    def flat_triplanar(name, texture, scale, tint, roughness):
        status('material ' + name)
        mat = make(name)
        position = node(mat, unreal.MaterialExpressionWorldPosition)
        normal = node(mat, unreal.MaterialExpressionVertexNormalWS)
        samples = triplanar(mat, position, texture, scale)
        code = '''
float3 w = pow(abs(N), 4);
w /= max(w.x + w.y + w.z, 0.0001);
float3 c = A * w.x + B * w.y + C * w.z;
float l = dot(c, float3(0.3, 0.5, 0.2));
float v = 0.9 + 0.1 * sin(P.x / 1600.0 + P.y / 1300.0);
return float3(l, l, l) * float3(%s, %s, %s) * v;
''' % tint
        color = custom(mat, code, {'P': position, 'N': normal, 'A': samples[0], 'B': samples[1], 'C': samples[2]}, unreal.CustomMaterialOutputType.CMOT_FLOAT3)
        return finish(mat, color, roughness)

    mats = {
        'limestone': wall('PlasterPale', stone_tex, (1.45, 1.12, 0.78), -0.08, 0.85, 210),
        'aged': wall('PlasterAged', stone_tex, (1.05, 0.72, 0.42), 0.08, 1.4, 210),
        'warmstone': wall('PlasterOchre', stone_tex, (1.55, 0.92, 0.42), 0.0, 1.05, 210),
        'ivory': wall('Travertine', dress_tex, (1.25, 1.08, 0.82), -0.14, 0.4, 260),
        'foundation': wall('StoneBase', stone_tex, (0.72, 0.58, 0.4), 0.28, 0.55, 180),
        'trim': wall('DressedStone', dress_tex, (1.2, 1.05, 0.82), -0.22, 0.2, 240),
        'terracotta': flat_triplanar('TerracottaTiles', roof_tex, 150, (1.25, 0.4, 0.16), 0.82),
        'roofstone': flat_triplanar('RoofStone', roof_tex, 170, (0.72, 0.4, 0.28), 0.86),
        'paving': flat_triplanar('Cobble', cobble_tex, 125, (0.78, 0.68, 0.52), 0.92),
        'recess': recess,
    }
    status('assigning city meshes')
    changed = []
    for mesh_name in ('SM_Gosain48_Capital', 'SM_Gosain48_FarSouth', 'SM_Gosain48_FarNorth', 'SM_Gosain48_Citadel'):
        mesh = unreal.load_asset(R + '/Gosain48/Meshes/' + mesh_name)
        assert mesh, mesh_name
        for index, slot in enumerate(mesh.static_materials):
            key = str(slot.material_slot_name)
            if key not in mats:
                continue
            mesh.set_material(index, mats[key])
            changed.append([mesh_name, key])
        A.save_loaded_asset(mesh)
    report['assigned'] = changed
    status('saved')
    (O / 'applied.json').write_text(json.dumps({'status': 'saved', 'assigned': changed}, indent=2))
except Exception:
    (O / 'apply_error.txt').write_text(traceback.format_exc())
    raise

views = [
    ('Close', (22230, 41648, -20451), (22248, 41672, -20450)),
    ('Street', (22174, 41625, -20453), (22340, 41625, -20454)),
    ('Capital_City', (25500, 39500, -19200), (22200, 41800, -20440)),
    ('Citadel', (23200, 41200, -20040), (22474, 42290, -20370)),
]
output = B / 'Docs/WorldDesign/Gosain49'
output.mkdir(exist_ok=True)
state = {'i': 0, 'phase': 0, 'next': time.monotonic() + 8, 'done': []}
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
