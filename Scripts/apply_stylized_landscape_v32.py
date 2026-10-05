"""v32: put El Ruhn on the SoStylized landscape pipeline so grass / dirt / sand / rock / water match the
Demonstration map (/Game/SoStylized/Maps/CompleteVol1/Demonstration).

Run with Map_AnimeAdventure open (the runner waits for the world, then executes):
  UnrealEditor.exe <uproject> /Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure -ExecCmds="py Scripts/apply_stylized_landscape_v32.py"

What it does
1. Duplicates SoStylized M_Landscape -> M_IV_StylizedLandscape32 and
   a. converts it to a masked material whose opacity mask is the LandscapeVisibilityMask (the island outline
      is cut with the __LANDSCAPE_VISIBILITY__ layer; the shipped material is opaque and would draw the whole
      1.2 km square);
   b. replaces its LandscapeLayerBlend / LandscapeLayerSample nodes with the same blends driven by a packed
      weight texture (R=Grass G=Dirt B=Sand A=Rock, Scripts/build_biome_layers_v32.py) sampled by world
      position. UE 5.8's Python API has no way to add paint target layers to an existing landscape
      (`target_layers` is read-only, no AddTargetLayer glue), and the result is pixel-identical to painted
      weightmaps at the landscape's own 1.19 m resolution. AutoCliff, sand sparkle, wet shoreline, RVT output
      and the LandscapeGrassOutput -> LG_Grass ground cover all keep working.
2. Duplicates MI_Landscape -> MI_IV_StylizedLandscape32 (keeps every demo tint / scale / switch), reparents it
   and assigns it to the landscape (also as hole material).
3. Spawns RVTV_Landscape / RVTV_LandscapeHeight volumes covering the island and binds RVT_Landscape +
   RVT_LandscapeHeight to the landscape, like the demo, then re-enables UseRVTColor? on the ground grass
   instances so blades take the ground colour again.
4. Lays a cobble disc over the village plaza (the old custom shader painted it; the layered material cannot).
5. Tunes MI_IV_SkyLake to the demo MI_Water look (strong caustics over the sandy bed, lighter murk, shore foam).
Idempotent: re-running updates in place (actor tag IVStylized32, material marker = BreakMaterialAttributes node).
"""
import unreal, json
from pathlib import Path

B = Path('D:/DEVELOPMENT/Games/IsekaiVillage'); S = B / 'Saved/AdventureWorldSource'
R = '/Game/IsekaiVillage/AdventureWorld'; SO = '/Game/SoStylized/Environment/Landscape'
MAP = '/Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure'
A = unreal.EditorAssetLibrary; M = unreal.MaterialEditingLibrary; T = unreal.AssetToolsHelpers.get_asset_tools()
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert w.get_path_name().startswith(MAP + '.'), 'open Map_AnimeAdventure first'
TAG = unreal.Name('IVStylized32'); report = {}
land = next(a for a in E.get_all_level_actors() if isinstance(a, unreal.Landscape))
LAYERS = ('Grass', 'Dirt', 'Sand', 'Rock'); CHANNEL = {'Grass': 'R', 'Dirt': 'G', 'Sand': 'B', 'Rock': 'A'}


def texture(name, filt=unreal.TextureFilter.TF_NEAREST):
    t = unreal.AssetImportTask(); t.filename = str(S / (name + '.png')); t.destination_path = R + '/Textures'; t.destination_name = name; t.automated = True; t.save = True; t.replace_existing = True
    T.import_asset_tasks([t]); a = unreal.load_asset(R + '/Textures/' + name); assert a, name
    for k, v in [('srgb', False), ('compression_settings', unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP), ('mip_gen_settings', unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS), ('filter', filt)]:
        a.set_editor_property(k, v)
    A.save_loaded_asset(a); return a


# ---------------------------------------------------------------- 1. masked, texture-weighted copy of M_Landscape
MARK = 'IV island weight UV v2'
mat_path = R + '/Materials/M_IV_StylizedLandscape32'; mi_path = R + '/Materials/MI_IV_StylizedLandscape32'
mat = unreal.load_asset(mat_path)


def has_mark(m):
    return any(isinstance(n, unreal.MaterialExpressionCustom) and n.get_editor_property('desc') == MARK for n in M.get_material_expressions(m))


if mat and not has_mark(mat):
    # stale / partially converted copy from an earlier run: detach the instance, drop it and start from the shipped graph
    old_mi = unreal.load_asset(mi_path)
    if old_mi:
        M.set_material_instance_parent(old_mi, unreal.load_asset(SO + '/Materials/M_Landscape')); A.save_loaded_asset(old_mi)
    assert A.delete_asset(mat_path), 'could not delete stale ' + mat_path
    mat = None
if not mat:
    mat = A.duplicate_asset(SO + '/Materials/M_Landscape', mat_path); assert mat
if not has_mark(mat):
    ATTR_SINKS = (unreal.MaterialExpressionBlendMaterialAttributes, unreal.MaterialExpressionSetMaterialAttributes, unreal.MaterialExpressionGetMaterialAttributes, unreal.MaterialExpressionBreakMaterialAttributes)
    weights = texture('T_IV_Layer32_Weights', unreal.TextureFilter.TF_BILINEAR)
    nodes = list(M.get_material_expressions(mat))

    # (a) visibility-mask opacity via BreakMaterialAttributes
    root = M.get_material_property_input_node(mat, unreal.MaterialProperty.MP_MATERIAL_ATTRIBUTES); assert root, 'no attribute root'
    brk = M.create_material_expression(mat, unreal.MaterialExpressionBreakMaterialAttributes, -300, 800)
    assert M.connect_material_expressions(root, '', brk, '')
    mat.set_editor_property('use_material_attributes', False)
    mat.set_editor_property('blend_mode', unreal.BlendMode.BLEND_MASKED)
    for out, prop in [('BaseColor', 'MP_BASE_COLOR'), ('Metallic', 'MP_METALLIC'), ('Specular', 'MP_SPECULAR'), ('Roughness', 'MP_ROUGHNESS'),
                      ('EmissiveColor', 'MP_EMISSIVE_COLOR'), ('Normal', 'MP_NORMAL'), ('AmbientOcclusion', 'MP_AMBIENT_OCCLUSION'),
                      ('WorldPositionOffset', 'MP_WORLD_POSITION_OFFSET'), ('PixelDepthOffset', 'MP_PIXEL_DEPTH_OFFSET')]:
        if hasattr(unreal.MaterialProperty, prop):
            assert M.connect_material_property(brk, out, getattr(unreal.MaterialProperty, prop)), out
    vis = M.create_material_expression(mat, unreal.MaterialExpressionLandscapeVisibilityMask, -300, 1300)
    assert M.connect_material_property(vis, '', unreal.MaterialProperty.MP_OPACITY_MASK)

    # (b) weight texture sampled by world position (same texel mapping as the heightmap import)
    pos = M.create_material_expression(mat, unreal.MaterialExpressionWorldPosition, -1500, 1600)
    uv = M.create_material_expression(mat, unreal.MaterialExpressionCustom, -1300, 1600)
    pin = unreal.CustomInput(); pin.set_editor_property('input_name', 'P'); uv.set_editor_property('inputs', [pin])
    uv.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT2)
    uv.set_editor_property('code', 'return (P.xy+60000.0+59.52381)/120119.04762;'); uv.set_editor_property('desc', MARK)
    assert M.connect_material_expressions(pos, '', uv, 'P')
    wtex = M.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -1100, 1600)
    wtex.set_editor_property('texture', weights); wtex.set_editor_property('sampler_type', unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR); wtex.set_editor_property('desc', 'IV layer weights R=Grass G=Dirt B=Sand A=Rock')
    assert M.connect_material_expressions(uv, '', wtex, 'UVs')

    def consumers_of(target):
        """[(node, input_name)] for every input in the graph currently fed by `target`."""
        found = []
        for n in M.get_material_expressions(mat):
            if n == target:
                continue
            try:
                names = [str(x) for x in M.get_material_expression_input_names(n)]
                srcs = list(M.get_inputs_for_material_expression(mat, n))
            except Exception:
                continue
            for i, src in enumerate(srcs):
                if src is not None and src == target and i < len(names):
                    found.append((n, names[i]))
        return found

    def src_output_name(node, input_name):
        for args in ((mat, node, input_name), (node, input_name)):
            try:
                return str(M.get_input_node_output_name_for_material_expression(*args))
            except Exception:
                pass
        return ''

    def node(cls, x, y):
        return M.create_material_expression(mat, cls, x, y)

    def scalar_add(a, b, x, y):
        s = node(unreal.MaterialExpressionAdd, x, y); assert M.connect_material_expressions(a, '', s, 'A') and M.connect_material_expressions(b, '', s, 'B'); return s

    rewired = []
    for n in nodes:
        if isinstance(n, unreal.MaterialExpressionLandscapeLayerBlend):
            names = [str(x) for x in M.get_material_expression_input_names(n)]; srcs = list(M.get_inputs_for_material_expression(mat, n))
            p0 = M.get_material_expression_node_position(n); x0, y0 = (int(p0[0]), int(p0[1])) if isinstance(p0, tuple) else (int(p0.x), int(p0.y))
            cons = consumers_of(n); assert cons, n.get_name()
            attr_mode = any(isinstance(c, ATTR_SINKS) for c, _ in cons)
            layer_src = {}
            for k, layer in enumerate(LAYERS):
                src = srcs[names.index('Layer ' + layer)]; out = src_output_name(n, 'Layer ' + layer) if src else ''
                if src is None:
                    src = node(unreal.MaterialExpressionMakeMaterialAttributes if attr_mode else unreal.MaterialExpressionConstant3Vector, x0 - 400, y0 + 120 * k); out = ''
                layer_src[layer] = (src, out)
            if attr_mode:
                # Sequential BlendMaterialAttributes with normalised alphas: Dirt/(G+D), Sand/(G+D+S), Rock/(G+D+S+R)=Rock.
                eps = node(unreal.MaterialExpressionConstant, x0 - 700, y0 + 500); eps.set_editor_property('r', 0.0001)
                running = node(unreal.MaterialExpressionAdd, x0 - 560, y0 + 500)  # G + eps
                assert M.connect_material_expressions(wtex, 'R', running, 'A') and M.connect_material_expressions(eps, '', running, 'B')
                total = None; prev = layer_src['Grass']
                for k, layer in enumerate(LAYERS[1:], 1):
                    nxt = node(unreal.MaterialExpressionAdd, x0 - 560 + 140 * k, y0 + 500)  # running + this layer's weight
                    assert M.connect_material_expressions(running, '', nxt, 'A') and M.connect_material_expressions(wtex, CHANNEL[layer], nxt, 'B'); running = nxt
                    alpha = node(unreal.MaterialExpressionDivide, x0 - 400 + 140 * k, y0 + 620)
                    assert M.connect_material_expressions(wtex, CHANNEL[layer], alpha, 'A') and M.connect_material_expressions(running, '', alpha, 'B')
                    bl = node(unreal.MaterialExpressionBlendMaterialAttributes, x0 - 200 + 160 * k, y0 + 120 * k)
                    assert M.connect_material_expressions(prev[0], prev[1], bl, 'A'), layer
                    assert M.connect_material_expressions(layer_src[layer][0], layer_src[layer][1], bl, 'B'), layer
                    assert M.connect_material_expressions(alpha, '', bl, 'Alpha'), layer
                    prev = (bl, ''); total = bl
            else:
                total = None
                for k, layer in enumerate(LAYERS):
                    src, out = layer_src[layer]
                    mul = node(unreal.MaterialExpressionMultiply, x0 - 200, y0 + 120 * k)
                    assert M.connect_material_expressions(src, out, mul, 'A'), layer
                    assert M.connect_material_expressions(wtex, CHANNEL[layer], mul, 'B'), layer
                    total = mul if total is None else scalar_add(total, mul, x0 - 60, y0 + 120 * k)
            for c, iname in cons:
                assert M.connect_material_expressions(total, '', c, iname), (c.get_name(), iname)
            rewired.append((n.get_name(), 'attributes' if attr_mode else 'scalar', [(c.get_name(), i) for c, i in cons])); M.delete_material_expression(mat, n)
        elif isinstance(n, unreal.MaterialExpressionLandscapeLayerSample):
            layer = str(n.get_editor_property('parameter_name')); assert layer in CHANNEL, layer
            cons = consumers_of(n)
            for c, iname in cons:
                assert M.connect_material_expressions(wtex, CHANNEL[layer], c, iname), (c.get_name(), iname)
            rewired.append((n.get_name(), [(c.get_name(), i) for c, i in cons])); M.delete_material_expression(mat, n)
        elif isinstance(n, (unreal.MaterialExpressionLandscapeLayerWeight, unreal.MaterialExpressionLandscapeLayerSwitch)):
            raise RuntimeError('unexpected landscape layer node ' + n.get_name())
    M.recompile_material(mat); A.save_loaded_asset(mat)
    report['rewired'] = rewired
report['material'] = mat_path
assert str(mat.get_editor_property('blend_mode')).endswith('BLEND_MASKED: 1>'), 'material not masked'
stats = M.get_statistics(mat); report['material_stats'] = str(stats)
assert stats.num_pixel_shader_instructions > 0, 'material failed to compile - see log'

mi = unreal.load_asset(mi_path)
if not mi:
    mi = A.duplicate_asset(SO + '/Materials/MI_Landscape', mi_path); assert mi
M.set_material_instance_parent(mi, mat)
# Island-specific tuning on top of the demo values: slightly greener grass than the cool demo meadow so it sits
# with the oak canopy, a warmer sand; everything else is the shipped look.
M.set_material_instance_vector_parameter_value(mi, 'Grass Tint', unreal.LinearColor(0.56, 0.78, 0.50, 1))
M.set_material_instance_vector_parameter_value(mi, 'Sand Tint', unreal.LinearColor(0.90, 0.84, 0.58, 1))
M.set_material_instance_vector_parameter_value(mi, 'Dirt Tint', unreal.LinearColor(0.86, 0.80, 0.56, 1))
M.set_material_instance_scalar_parameter_value(mi, 'Auto Cliff Start', 0.80)
M.set_material_instance_scalar_parameter_value(mi, 'Auto Cliff Fade', 0.75)
M.set_material_instance_scalar_parameter_value(mi, 'Waterline Height', 1800.0 + 20.0)  # lake surface 18 m
M.set_material_instance_scalar_parameter_value(mi, 'Waterline Distance', 120.0)
M.update_material_instance(mi); A.save_loaded_asset(mi)
land.set_editor_property('landscape_material', mi); land.set_editor_property('landscape_hole_material', mi)
land.force_layers_full_update()

# ---------------------------------------------------------------- 2. runtime virtual textures
o, ext = land.get_actor_bounds(False)
z0 = o.z - ext.z - 1500.0; z1 = o.z + ext.z + 1500.0
for label, rvt in [('RVTV_Landscape', 'RVT_Landscape'), ('RVTV_LandscapeHeight', 'RVT_LandscapeHeight')]:
    vol = next((a for a in E.get_all_level_actors() if isinstance(a, unreal.RuntimeVirtualTextureVolume) and a.get_actor_label() == label), None)
    if not vol:
        vol = E.spawn_actor_from_class(unreal.RuntimeVirtualTextureVolume, unreal.Vector(0, 0, 0)); vol.set_actor_label(label); vol.set_folder_path('Floating Island/RVT')
        vol.set_editor_property('tags', [TAG])
    comp = vol.get_editor_property('virtual_texture_component')
    comp.set_editor_property('virtual_texture', unreal.load_asset(SO + '/Textures/' + rvt))
    try:
        comp.set_editor_property('bounds_align_actor', land)
    except Exception as ex:
        unreal.log_warning('bounds_align_actor: %s' % ex)
    vol.set_actor_location(unreal.Vector(o.x - ext.x, o.y - ext.y, z0), False, False)
    vol.set_actor_scale3d(unreal.Vector(ext.x * 2, ext.y * 2, z1 - z0))
land.set_editor_property('runtime_virtual_textures', [unreal.load_asset(SO + '/Textures/RVT_Landscape'), unreal.load_asset(SO + '/Textures/RVT_LandscapeHeight')])
try:
    land.set_editor_property('virtual_texture_render_pass_type', unreal.RuntimeVirtualTextureMainPassType.ALWAYS)
except Exception as ex:
    unreal.log_warning('render pass type not set: %s' % ex)
report['rvt_bounds_m'] = [round((o.x - ext.x) / 100), round((o.y - ext.y) / 100), round(z0 / 100), round((o.x + ext.x) / 100), round((o.y + ext.y) / 100), round(z1 / 100)]

# Ground-cover grass reads the landscape colour from the RVT again (v31 turned it off because no volume existed).
# The pack's *_NoRVT* variants are meant to stay texture/colour driven - keep (or restore) them off.
flipped = []; seen = set()
for path in A.list_assets('/Game/SoStylized/Environment/Foliage/Materials', recursive=True, include_folder=False):
    m2 = unreal.load_asset(path)
    if not isinstance(m2, unreal.MaterialInstanceConstant) or not m2.get_name().startswith('MI_Grass') or m2.get_name() in seen:
        continue
    seen.add(m2.get_name())
    names = [str(n) for n in M.get_static_switch_parameter_names(m2)]
    if 'UseRVTColor?' not in names:
        continue
    want = 'NoRVT' not in m2.get_name()
    if M.get_material_instance_static_switch_parameter_value(m2, 'UseRVTColor?') != want:
        M.set_material_instance_static_switch_parameter_value(m2, 'UseRVTColor?', want); M.update_material_instance(m2); A.save_loaded_asset(m2); flipped.append((m2.get_name(), want))
report['grass_rvt_colour'] = flipped

# ---------------------------------------------------------------- 3. plaza cobbles
plaza = next((a for a in E.get_all_level_actors() if TAG in a.tags and a.get_actor_label() == 'Village plaza cobbles'), None)
if not plaza:
    plaza = E.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, 0)); plaza.set_actor_label('Village plaza cobbles'); plaza.set_folder_path('Floating Island/Village')
    plaza.set_editor_property('tags', [TAG])
WS = [unreal.ObjectTypeQuery.ECC_WORLD_STATIC]
# Ground height = landscape hits only (props / portal on the square would otherwise float the disc), sampled on two rings.
import math
zs = []
for r_m, count in ((9.0, 8), (16.5, 12)):
    for i in range(count):
        ang = 2 * math.pi * i / count; x = math.cos(ang) * r_m * 100; y = math.sin(ang) * r_m * 100
        for hit in unreal.SystemLibrary.line_trace_multi_for_objects(w, unreal.Vector(x, y, 20000), unreal.Vector(x, y, -20000), WS, True, [plaza], unreal.DrawDebugTrace.NONE, True) or []:
            t = hit.to_tuple()
            if t[0] and any(isinstance(e, unreal.Landscape) for e in t):
                zs.append(t[5].z); break
assert zs, 'no landscape hits under the plaza'
zs.sort(); pz = zs[len(zs) // 2]; report['plaza_ground_span_cm'] = [round(zs[0]), round(zs[-1])]
plaza.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cylinder'))
plaza.static_mesh_component.set_material(0, unreal.load_asset('/Game/StylizedIsland/Mesh/Modular_Pieces/MI_Stone_Floor'))
plaza.set_actor_location(unreal.Vector(0, 0, pz + 3.0 - 30.0), False, False); plaza.set_actor_scale3d(unreal.Vector(36.0, 36.0, 0.6))  # 36 m disc, 60 cm thick, top 3 cm proud
plaza.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
report['plaza_top_z_m'] = round((pz + 3.0) / 100, 2)

# ---------------------------------------------------------------- 4. lake water to the demo look
lake = unreal.load_asset(R + '/Materials/MI_IV_SkyLake')
for k, v in [('Caustic Strength', 48.0), ('Water Murkiness', 0.22), ('Water Scattering', 0.14), ('Foam Multiply', 1.25), ('Distance', 80.0),
             ('Normal1 Flatness', 0.95), ('Normal2 Flatness', 0.93), ('Roughness', 0.20), ('Specular', 0.25)]:
    M.set_material_instance_scalar_parameter_value(lake, k, v)
M.set_material_instance_vector_parameter_value(lake, 'Scattering Color', unreal.LinearColor(0.12, 0.38, 0.46, 1))
M.update_material_instance(lake); A.save_loaded_asset(lake)

# Foundation is a closed volume under the playable surface; keep it visible from
# below but out of Lumen GI / distance fields (see apply_sky_lake_v32.py).
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
A.save_directory(R + '/Materials', only_if_is_dirty=True, recursive=False); A.save_directory(R + '/Textures', only_if_is_dirty=True, recursive=False)
(B / 'Saved/stylized_landscape_v32_result.json').write_text(json.dumps(report, indent=2))
unreal.log('V32_APPLIED ' + json.dumps(report))
