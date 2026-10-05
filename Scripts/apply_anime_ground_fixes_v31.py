"""v31 step 4 - ground-level fixes: black grass, floating props, rock tone.

* Every SoStylized grass/foliage instance had 'UseRVTColor?' on, sampling RVT_Landscape for its colour, but the level
  has no RuntimeVirtualTextureVolume, so all grass rendered as black shards. Switch the RVT colour path off and give the
  grass a flat anime green that sits with the landscape.
* Props (boulders, crates, barrels, stones...) hovering above the landscape are dropped onto it; things that are meant
  to be elevated (lanterns, quay planks over the void, bridges, tunnels, water) are left alone and listed.
* The strata rock from step 3 was too pale; darken/warm it so it reads as rock rather than chalk.
"""
import unreal, json, os
from pathlib import Path

B = Path('D:/DEVELOPMENT/Games/IsekaiVillage')
R = '/Game/IsekaiVillage/AdventureWorld'
MAP = R + '/Maps/Map_AnimeAdventure'
WS = [unreal.ObjectTypeQuery.ECC_WORLD_STATIC]
A = unreal.EditorAssetLibrary
M = unreal.MaterialEditingLibrary
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert w.get_path_name().startswith(MAP + '.'), w.get_path_name()
report = {}

# ---- rock tone
mat = unreal.load_asset(R + '/Materials/M_IV_SculptedGeology28')
for n in M.get_material_expressions(mat):
    if isinstance(n, unreal.MaterialExpressionCustom) and '/*AnimeStrata31*/' in n.get_editor_property('code'):
        code = n.get_editor_property('code')
        code = code.replace('lerp(float3(.56,.54,.52),float3(.74,.70,.63),strata)*lerp(.86,1.08,n)', 'lerp(float3(.33,.31,.29),float3(.50,.46,.40),strata)*lerp(.84,1.10,n)')
        code = code.replace('rock*=lerp(.92,1.08,saturate(lum*1.6));', 'rock*=lerp(.90,1.10,saturate(lum*1.6));\n float fine=.95+.05*sin(P.z/260.+n*3.);rock*=fine;')
        n.set_editor_property('code', code); report['rock'] = 'AnimeStrata31 darkened'
M.recompile_material(mat); A.save_loaded_asset(mat)

# ---- grass colour path
grass_fixed = []
for path in A.list_assets('/Game/SoStylized/Environment/Foliage/Materials', recursive=True, include_folder=False):
    mi = unreal.load_asset(path)
    if not isinstance(mi, unreal.MaterialInstanceConstant):
        continue
    names = [str(x) for x in M.get_static_switch_parameter_names(mi)]
    if 'UseRVTColor?' in names and M.get_material_instance_static_switch_parameter_value(mi, 'UseRVTColor?'):
        M.set_material_instance_static_switch_parameter_value(mi, 'UseRVTColor?', False)
        if mi.get_name().startswith('MI_Grass'):
            M.set_material_instance_vector_parameter_value(mi, 'Base Color', unreal.LinearColor(0.235, 0.43, 0.085, 1.0))
            M.set_material_instance_scalar_parameter_value(mi, 'Tip Brightness', 0.25)
        M.update_material_instance(mi); A.save_loaded_asset(mi); grass_fixed.append(mi.get_name())
report['rvt_colour_switched_off'] = grass_fixed

# ---- floating props
def trace_down(x, y, ztop, ignore):
    hit = unreal.SystemLibrary.line_trace_single_for_objects(w, unreal.Vector(x, y, ztop), unreal.Vector(x, y, ztop - 6000.0), WS, True, ignore, unreal.DrawDebugTrace.NONE, True)
    if hit and hit.to_tuple()[0]:
        t = hit.to_tuple(); return t[5].z, t[9]
    return None, None

SKIP = ('lantern', 'plane', 'cube', 'quay', 'dock', 'bridge', 'rail', 'portal', 'tunnel', 'civ30', 'cloud', 'falls', 'water', 'lake', 'roads', 'foundations', 'collar', 'foundation', 'sign', 'banner', 'flag', 'beam', 'smoke', 'roof', 'chimney', 'window', 'door')
floating, dropped = [], []
for a in E.get_all_level_actors():
    if not isinstance(a, unreal.StaticMeshActor):
        continue
    c = a.static_mesh_component
    if not c.static_mesh:
        continue
    loc = a.get_actor_location()
    if abs(loc.x) > 70000 or abs(loc.y) > 70000:
        continue
    o, ext, _ = unreal.SystemLibrary.get_component_bounds(c)
    bottom = o.z - ext.z
    hz, hit = trace_down(o.x, o.y, bottom + 20.0, [a])
    if hit is None:
        continue
    gap = (bottom - hz) / 100.0
    if gap < 0.25:
        continue
    label = a.get_actor_label(); mesh = c.static_mesh.get_name()
    entry = {'actor': label, 'mesh': mesh, 'xy_m': [round(o.x / 100, 1), round(o.y / 100, 1)], 'gap_m': round(gap, 2), 'on': hit.get_actor_label()}
    text = (label + ' ' + mesh).lower()
    if any(k in text for k in SKIP) or not isinstance(hit, unreal.LandscapeProxy) or gap > 4.0 or ext.x > 1500 or ext.y > 1500:
        floating.append(entry); continue
    a.set_actor_location(unreal.Vector(loc.x, loc.y, loc.z - gap * 100.0 + 8.0), False, False)  # 8 cm sink so the base is buried
    dropped.append(entry)
report['props_dropped'] = dropped
report['left_elevated'] = floating
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
report['saved'] = True
(B / 'Saved/anime_ground_v31.json').write_text(json.dumps(report, indent=1, default=str))
unreal.log('GROUND_V31 ' + json.dumps({'rock': report.get('rock'), 'grass': grass_fixed, 'dropped': len(dropped), 'left_elevated': len(floating)}))

if os.environ.get('IV_RENDER_AFTER') == '1':
    import importlib.util
    spec = importlib.util.spec_from_file_location('render_anime_polish_v31', str(B / 'Scripts/render_anime_polish_v31.py'))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    views = [v for v in mod.VIEWS if v[0] in ('Village', 'Meadow', 'Inn', 'Forest', 'RimFront', 'Island', 'DungeonPath')] + [
        ('Harbor', (-40, -340), None, (-64, -366, None)),
        ('EdgeSouth', (-100, -500), None, (120, -560, None)),
    ]
    mod.start_render(prefix='AnimePolish31_step4_', out_dir=Path(os.environ.get('IV_RENDER_DIR', str(B / 'Saved/AnimePolish31'))), views=views, warmup=90.0, quit_when_done=True)
