"""v31 step 2 - rock collar around the El Ruhn landscape edge.

Seen from outside, the playable landscape ended on a dead-straight 'cake cut' line against the rock foundation, with
the pale landscape boundary plate showing wherever the two did not meet. This marches 720 rays out from the island
centre, finds the outermost landscape sample on each ray (looking through anything standing on top of it), and builds
a faceted rock collar that rises out of the grass a few metres inside the edge, bulges over the rim and tucks back into
the foundation shell 40 m below. Where something man-made or water sits on the edge (quay, waterfall) the collar is
buried so it never cuts through a feature. Also dumps the foundation material/collision so step 3 can retune it.
"""
import unreal, json, math, os
from pathlib import Path

B = Path('D:/DEVELOPMENT/Games/IsekaiVillage')
S = B / 'Saved/AdventureWorldSource'
R = '/Game/IsekaiVillage/AdventureWorld'
MAP = R + '/Maps/Map_AnimeAdventure'
WS = [unreal.ObjectTypeQuery.ECC_WORLD_STATIC]
TAG = 'IVRimCollar31'
NAME = 'SM_IV_RimCollar_v31'
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
A = unreal.EditorAssetLibrary
T = unreal.AssetToolsHelpers.get_asset_tools()
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert w.get_path_name().startswith(MAP + '.'), w.get_path_name()
assert (B / 'Saved/WorldBackups/BeforeAnimePolish_v31/Map_AnimeAdventure.umap').exists(), 'run apply_anime_lighting_v31 first'

report = {}
actors = E.get_all_level_actors()
for a in actors:  # previous collar must go before tracing, or its geometry would register as an edge feature
    if TAG in [str(t) for t in a.tags]:
        E.destroy_actor(a)
actors = [a for a in actors if TAG not in [str(t) for t in a.tags]]
shell = next(a for a in actors if isinstance(a, unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name() == 'SM_IV_JoinedMountain_v28')
landscapes = [a for a in actors if isinstance(a, unreal.LandscapeProxy)]

# ---- probe for step 3: what the foundation material and its collision actually are
def dump_material(mat):
    out = {'path': mat.get_path_name(), 'nodes': []}
    for n in unreal.MaterialEditingLibrary.get_material_expressions(mat):
        e = {'cls': n.get_class().get_name(), 'name': n.get_name()}
        if isinstance(n, unreal.MaterialExpressionCustom):
            e['code'] = n.get_editor_property('code'); e['inputs'] = [str(p.get_editor_property('input_name')) for p in n.get_editor_property('inputs')]
        elif isinstance(n, unreal.MaterialExpressionTextureSample):
            t = n.get_editor_property('texture'); e['texture'] = t.get_path_name() if t else None
        elif isinstance(n, (unreal.MaterialExpressionConstant, unreal.MaterialExpressionConstant3Vector, unreal.MaterialExpressionScalarParameter, unreal.MaterialExpressionVectorParameter)):
            for k in ('r', 'constant', 'default_value', 'parameter_name'):
                try:
                    e[k] = str(n.get_editor_property(k))
                except Exception:
                    pass
        out['nodes'].append(e)
    for prop in ('MP_BASE_COLOR', 'MP_NORMAL', 'MP_ROUGHNESS', 'MP_SPECULAR', 'MP_EMISSIVE_COLOR'):
        n = unreal.MaterialEditingLibrary.get_material_property_input_node(mat, getattr(unreal.MaterialProperty, prop))
        out[prop] = n.get_name() if n else None
    return out

shell_mesh = shell.static_mesh_component.static_mesh
bs = shell_mesh.get_editor_property('body_setup')
report['shell'] = {'label': shell.get_actor_label(), 'mesh': shell_mesh.get_path_name(), 'tris': shell_mesh.get_num_triangles(0), 'collision_trace_flag': str(bs.get_editor_property('collision_trace_flag')),
                   'materials': [m.get_path_name() if m else None for m in shell.static_mesh_component.get_materials()]}
report['materials'] = {p: dump_material(unreal.load_asset(R + '/Materials/' + p)) for p in ('M_IV_SculptedGeology28', 'M_IV_FoothillRock', 'M_IV_IslandRock', 'M_IV_CaveStone') if A.does_asset_exist(R + '/Materials/' + p)}
usage = {}
for a in actors:
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        for m in c.get_materials():
            if m and m.get_name() in ('M_IV_SculptedGeology28', 'M_IV_FoothillRock', 'M_IV_IslandRock', 'M_IV_CaveStone'):
                usage.setdefault(m.get_name(), []).append(a.get_actor_label())
report['material_usage'] = {k: {'count': len(v), 'sample': v[:8]} for k, v in usage.items()}

# ---- landscape boundary by polar march
def trace(x, y, ztop, zbot):
    hit = unreal.SystemLibrary.line_trace_single_for_objects(w, unreal.Vector(x, y, ztop), unreal.Vector(x, y, zbot), WS, True, [], unreal.DrawDebugTrace.NONE, True)
    if hit and hit.to_tuple()[0]:
        t = hit.to_tuple(); return t[5].z, t[9]
    return None, None

def column(x, y):
    """(landscape_z, feature_z): landscape surface under anything standing on it; feature_z = top of a non-landscape,
    non-shell actor above the landscape, else None."""
    z = 60000.0; feature = None
    for _ in range(8):
        hz, actor = trace(x, y, z, -60000.0)
        if actor is None:
            return None, feature
        if isinstance(actor, unreal.LandscapeProxy):
            return hz, feature
        if feature is None and actor is not shell:
            feature = hz
        z = hz - 5.0
    return None, feature

N = 720
STEP = 200.0  # cm
R0, R1 = 25000.0, 70000.0
rays = []
for k in range(N):
    th = 2 * math.pi * k / N; cx, cy = math.cos(th), math.sin(th)
    samples = []  # (r, landscape_z, feature_z)
    r = R0
    while r <= R1:
        lz, fz = column(cx * r, cy * r); samples.append((r, lz, fz)); r += STEP
    outer = max((i for i, s in enumerate(samples) if s[1] is not None), default=None)
    if outer is None:
        rays.append(None); continue
    rb, zb, fb = samples[outer]
    inner = next((samples[i] for i in range(outer - 4, -1, -1) if samples[i][1] is not None), samples[outer])
    # feature on or just beyond the edge => bury the collar here
    near = samples[max(0, outer - 3):min(len(samples), outer + 4)]
    feature = any(s[2] is not None and (s[1] is None or s[2] > s[1] + 20.0) for s in near)
    rays.append({'th': th, 'r': rb, 'z': zb, 'inner_z': inner[1], 'inner_r': inner[0], 'feature': feature})
missing = [k for k, v in enumerate(rays) if v is None]
assert len(missing) < N * 0.05, missing
for k in missing:  # fill from neighbours
    for d in range(1, N):
        if rays[(k + d) % N]:
            rays[k] = dict(rays[(k + d) % N]); rays[k]['th'] = 2 * math.pi * k / N; break
# spread feature exclusion so the collar fades out 3 samples either side of a feature
feat = [v['feature'] for v in rays]
fade = []
for k in range(N):
    d = min((abs(((k - j + N // 2) % N) - N // 2) for j in range(N) if feat[j]), default=99)
    fade.append(1.0 if d >= 4 else d / 4.0)  # 1 = full collar, 0 = buried
report['rim'] = {'rays': N, 'missing_filled': len(missing), 'feature_rays': sum(feat), 'z_range_m': [round(min(v['z'] for v in rays) / 100, 1), round(max(v['z'] for v in rays) / 100, 1)],
                 'r_range_m': [round(min(v['r'] for v in rays) / 100, 1), round(max(v['r'] for v in rays) / 100, 1)]}

# ---- collar mesh
def hashf(a, b):
    return (math.sin(a * 12.9898 + b * 78.233) * 43758.5453) % 1.0

def lip_m(th):  # crest height above the landscape edge, metres. Mostly low rocks with taller crags scattered around.
    v = 0.9 + 1.1 * math.sin(th * 23 + 1.3) + 0.8 * math.sin(th * 57 + 0.4) + 0.5 * math.sin(th * 131 + 2.1)
    return max(-0.2, min(3.2, v))

def bulge_m(th):
    return 1.5 + 1.2 * math.sin(th * 41 + 0.7) + 0.6 * math.sin(th * 97 + 1.9)

rings = []  # rings[k] = list of 7 (x, y, z) profile points for ray k
for k, v in enumerate(rays):
    th = v['th']; cx, cy = math.cos(th), math.sin(th); f = fade[k]
    rb, zb = v['r'], v['z']
    lip = lip_m(th) * 100 * f - 150 * (1 - f)
    bul = bulge_m(th) * 100 * f
    jit = lambda i, s: (hashf(k * 7 + i, s) - 0.5) * 120 * f
    prof = [  # (radial offset cm, z cm)
        (v['inner_r'] - rb - 100, v['inner_z'] - 150),
        (-300 + jit(1, 1), zb + lip + jit(1, 2)),
        (bul + jit(2, 3), zb + lip * 0.6 + jit(2, 4)),
        (bul + 200 + jit(3, 5), zb - 400 + jit(3, 6)),
        (bul + 100 + jit(4, 7), zb - 1200),
        (50, zb - 2500),
        (-600, zb - 4000),
    ]
    rings.append([(cx * (rb + dr), cy * (rb + dr), z) for dr, z in prof])

S.mkdir(parents=True, exist_ok=True)
tris = []  # ((p, q, s), (uv, uv, uv)) in UE world cm
for k in range(N):
    a, b = rings[k], rings[(k + 1) % N]
    ua, ub = k * 0.05, (k + 1) * 0.05
    for i in range(6):
        # outward-facing winding (ring k -> k+1 runs counter-clockwise seen from above; profile runs top->down)
        tris.append(((a[i], a[i + 1], b[i]), ((ua, i * .25), (ua, (i + 1) * .25), (ub, i * .25))))
        tris.append(((b[i], a[i + 1], b[i + 1]), ((ub, i * .25), (ua, (i + 1) * .25), (ub, (i + 1) * .25))))
allv = [p for tri, _ in tris for p in tri]
expect = [min(p[i] for p in allv) for i in range(3)] + [max(p[i] for p in allv) for i in range(3)]

def write_obj(mapping):
    """The OBJ goes through the FBX importer, which mirrors Y (right- to left-handed) and keeps Z up, so UE (x, y, z) is
    written as (x, -y, z). The mapping is verified against the expected bounds after import, with fallbacks."""
    def m(p):
        return tuple(p[abs(i) - 1] * (1 if i > 0 else -1) for i in mapping)
    lines = ['# El Ruhn rim rock collar v31 (cm)']; vi = 0
    for (p, q, s), u in tris:
        ax, ay, az = q[0] - p[0], q[1] - p[1], q[2] - p[2]; bx, by, bz = s[0] - p[0], s[1] - p[1], s[2] - p[2]
        n = (ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx); L = math.sqrt(sum(c * c for c in n)) or 1.0
        for pt, uv in zip((p, q, s), u):
            lines.append('v %.1f %.1f %.1f' % m(pt)); lines.append('vt %.4f %.4f' % uv)
        lines.append('vn %.4f %.4f %.4f' % m(tuple(c / L for c in n)))
        f = vi // 3 + 1
        lines.append('f %d/%d/%d %d/%d/%d %d/%d/%d' % (vi + 1, vi + 1, f, vi + 2, vi + 2, f, vi + 3, vi + 3, f)); vi += 3
    (S / (NAME + '.obj')).write_text('\n'.join(lines) + '\n')

# ---- import, material, placement
mesh = None
for mapping in ((1, -2, 3), (1, 2, 3), (1, 3, 2), (1, -3, 2)):
    write_obj(mapping)
    t = unreal.AssetImportTask(); t.filename = str(S / (NAME + '.obj')); t.destination_path = R + '/Meshes/Refinement'; t.destination_name = NAME
    t.automated = True; t.replace_existing = True; t.save = False
    op = unreal.FbxImportUI(); op.import_materials = False; op.import_textures = False
    op.static_mesh_import_data.combine_meshes = True; op.static_mesh_import_data.auto_generate_collision = False
    op.static_mesh_import_data.set_editor_property('normal_import_method', unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
    t.options = op; T.import_asset_tasks([t])
    mesh = unreal.load_asset(t.destination_path + '/' + NAME); assert mesh, 'collar import failed'
    bb = mesh.get_bounding_box(); got = [bb.min.x, bb.min.y, bb.min.z, bb.max.x, bb.max.y, bb.max.z]
    err = max(abs(g - e) for g, e in zip(got, expect))
    report['mesh'] = {'tris': len(tris), 'obj': str(S / (NAME + '.obj')), 'axis_mapping': mapping, 'bounds_error_cm': round(err, 1), 'bounds_m': [round(v / 100, 1) for v in got]}
    unreal.log('RIM_V31 import mapping %s bounds err %.1f cm' % (mapping, err))
    if err < 5.0:
        break
else:
    unreal.log_error('RIM_V31 no OBJ axis mapping reproduced the collar bounds: %s' % report['mesh'])
    if os.environ.get('IV_RENDER_AFTER') == '1':  # unattended run: do not leave the editor hanging
        unreal.SystemLibrary.execute_console_command(w, 'QUIT_EDITOR')
    raise RuntimeError('collar import bounds mismatch')
mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag', unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
A.save_loaded_asset(mesh)
# two-sided instance of the foundation material: the collar is seen from the meadow side as well as from outside
mat_path = R + '/Materials/MI_IV_RimCollar_v31'
if A.does_asset_exist(mat_path):
    mat = unreal.load_asset(mat_path)
else:
    mat = T.create_asset('MI_IV_RimCollar_v31', R + '/Materials', unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    mat.set_editor_property('parent', shell.static_mesh_component.get_material(0))
    ov = mat.get_editor_property('base_property_overrides'); ov.set_editor_property('override_two_sided', True); ov.set_editor_property('two_sided', True)
    mat.set_editor_property('base_property_overrides', ov)
    A.save_loaded_asset(mat)
collar = E.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector())
collar.static_mesh_component.set_static_mesh(mesh); collar.static_mesh_component.set_material(0, mat)
collar.set_actor_label('El Ruhn - rim rock collar v31'); collar.set_folder_path('Floating Island/Rim Collar v31'); collar.tags = [unreal.Name(TAG)]
report['collar'] = {'actor': collar.get_actor_label(), 'material': mat.get_path_name() if mat else None, 'mesh_tris': mesh.get_num_triangles(0)}

assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
report['saved'] = True
(B / 'Saved/anime_rim_v31.json').write_text(json.dumps(report, indent=1))
unreal.log('RIM_V31 ' + json.dumps({k: report[k] for k in ('rim', 'mesh', 'collar', 'saved')}))

if os.environ.get('IV_RENDER_AFTER') == '1':
    import importlib.util
    spec = importlib.util.spec_from_file_location('render_anime_polish_v31', str(B / 'Scripts/render_anime_polish_v31.py'))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    views = [v for v in mod.VIEWS if v[0] in ('RimFront', 'RimEast', 'RimWest', 'RimNorth', 'FrontEdge', 'Island')] + [
        ('EdgeEast', (400, -100), None, (560, -40, None)),
        ('EdgeSouth', (-100, -500), None, (120, -560, None)),
        ('EdgeNorthWest', (-380, 300), None, (-470, 420, None)),
    ]
    mod.start_render(prefix='AnimePolish31_step2_', out_dir=Path(os.environ.get('IV_RENDER_DIR', str(B / 'Saved/AnimePolish31'))), views=views, quit_when_done=True)
