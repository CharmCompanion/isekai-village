"""v31 step 3 - stylised rock for the foundation shell, rim collar and tunnels.

M_IV_SculptedGeology28 drove its colour almost entirely from a 45 m tiled rock photo texture, which read as blue-grey
noise across a 1.2 km shell. This rewrites the base colour as flat anime strata (two warm greys in horizontal bands warped
by large value noise), a cool darkening gradient toward the underside, soil and moss on up-facing ledges just below the
landscape, and only a faint texture breakup. Roughness goes matte and the detail normal tiles broader. M_IV_CaveStone
(tunnels, portals, quay buttresses) gets the same banding treatment. Also probes the grass material and the modular
house footprints for the next step.
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

STRATA = '''/*AnimeStrata31*/
 float3 q=P/13000.;float3 i=floor(q);float3 f=frac(q);f=f*f*(3-2*f);float n=0;
 for(int x=0;x<2;x++)for(int y=0;y<2;y++)for(int z=0;z<2;z++){
 float3 c=float3(x,y,z);float h=frac(sin(dot(i+c,float3(127.1,311.7,74.7)))*43758.5453);
 float3 w=lerp(1-f,f,c);n+=h*w.x*w.y*w.z;}
 float height=(H.r*65280.+H.g*255.-32768.)/64.*100.;
 float below=max(0,height-P.z);
 float band=sin(P.z/1100.+n*6.+P.x/9000.);
 float strata=smoothstep(-.25,.25,band);
 float3 rock=lerp(float3(.56,.54,.52),float3(.74,.70,.63),strata)*lerp(.86,1.08,n);
 float lum=dot(C,float3(.3,.59,.11));
 rock*=lerp(.92,1.08,saturate(lum*1.6));
 float deep=saturate(below/25000.);
 rock=lerp(rock,rock*float3(.60,.65,.76),deep);
 float up=smoothstep(.35,.75,N.z);
 float nearTop=1-smoothstep(300.,2500.,below);
 rock=lerp(rock,float3(.46,.36,.24),up*nearTop*.7);
 rock=lerp(rock,float3(.32,.52,.22),up*nearTop*smoothstep(.45,.9,n+.3)*.85);
 return rock*(1-.15*saturate(U.x));
 '''

mat = unreal.load_asset(R + '/Materials/M_IV_SculptedGeology28')
changed = []
for n in M.get_material_expressions(mat):
    if isinstance(n, unreal.MaterialExpressionCustom):
        code = n.get_editor_property('code')
        if '/*Mountain12*/' in code or '/*AnimeStrata31*/' in code:
            n.set_editor_property('code', STRATA); changed.append('base colour -> AnimeStrata31')
        elif code.strip() in ('return P.xy/1800.;', 'return P.xz/1800.;', 'return P.yz/1800.;'):
            n.set_editor_property('code', code.replace('1800.', '4200.')); changed.append('normal tiling 18 m -> 42 m')
    elif isinstance(n, unreal.MaterialExpressionConstant) and abs(n.get_editor_property('r') - 0.74) < 1e-4:
        n.set_editor_property('r', 0.92); changed.append('roughness .74 -> .92')
M.recompile_material(mat); A.save_loaded_asset(mat)
report['M_IV_SculptedGeology28'] = changed

cave = unreal.load_asset(R + '/Materials/M_IV_CaveStone')
nodes = M.get_material_expressions(cave)
pos = next(n for n in nodes if isinstance(n, unreal.MaterialExpressionWorldPosition))
cave_changes = []
for n in nodes:
    if isinstance(n, unreal.MaterialExpressionCustom) and n.get_editor_property('code').startswith('float3 w=pow(abs(N),4)'):
        inputs = list(n.get_editor_property('inputs'))
        if not any(str(p.get_editor_property('input_name')) == 'P' for p in inputs):
            p = unreal.CustomInput(); p.set_editor_property('input_name', 'P'); inputs.append(p); n.set_editor_property('inputs', inputs)
            M.connect_material_expressions(pos, '', n, 'P')
        n.set_editor_property('code', '/*CaveStrata31*/ float3 w=pow(abs(N),4);w/=max(dot(w,1),.001);float3 t=(A*w.z+B*w.y+C*w.x);'
                                      'float lum=dot(t,float3(.3,.59,.11));float band=.92+.08*sin(P.z/420.+sin(P.x/1300.)+sin(P.y/1700.));'
                                      'float3 rock=lerp(float3(.50,.47,.44),float3(.66,.62,.56),smoothstep(.2,.7,lum))*band;'
                                      'return rock;')
        cave_changes.append('triplanar colour -> CaveStrata31 bands')
M.recompile_material(cave); A.save_loaded_asset(cave)
report['M_IV_CaveStone'] = cave_changes

# ---- probes for step 4
def trace(x, y, ztop, zbot, ignore):
    hit = unreal.SystemLibrary.line_trace_single_for_objects(w, unreal.Vector(x, y, ztop), unreal.Vector(x, y, zbot), WS, True, ignore, unreal.DrawDebugTrace.NONE, True)
    if hit and hit.to_tuple()[0]:
        t = hit.to_tuple(); return t[5].z, t[9]
    return None, None

def landscape_z(x, y, ignore):
    z = 60000.0
    for _ in range(8):
        hz, actor = trace(x, y, z, -60000.0, ignore)
        if actor is None:
            return None
        if isinstance(actor, unreal.LandscapeProxy):
            return hz
        z = hz - 5.0
    return None

houses = []
def probe_houses():
  for a in E.get_all_level_actors():
    cls = a.get_class().get_name()
    if not cls.startswith('BP_BLD_house'):
        continue
    o, ext = a.get_actor_bounds(False)
    base_z = o.z - ext.z
    corners = [(o.x - ext.x * .9, o.y - ext.y * .9), (o.x + ext.x * .9, o.y - ext.y * .9), (o.x + ext.x * .9, o.y + ext.y * .9), (o.x - ext.x * .9, o.y + ext.y * .9), (o.x, o.y)]
    gz = [landscape_z(x, y, [a]) for x, y in corners]
    comps = []
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        if c.static_mesh:
            co, ce, _ = unreal.SystemLibrary.get_component_bounds(c)
            comps.append({'mesh': c.static_mesh.get_name(), 'z_min_m': round((co.z - ce.z) / 100, 2), 'materials': [m.get_name() for m in c.get_materials() if m]})
    comps.sort(key=lambda d: d['z_min_m'])
    houses.append({'label': a.get_actor_label(), 'cls': cls, 'origin_m': [round(o.x / 100, 1), round(o.y / 100, 1)], 'extent_m': [round(ext.x / 100, 1), round(ext.y / 100, 1), round(ext.z / 100, 1)],
                   'base_z_m': round(base_z / 100, 2), 'ground_z_m': [round(z / 100, 2) if z is not None else None for z in gz],
                   'gap_m': [round((base_z - z) / 100, 2) if z is not None else None for z in gz], 'lowest_components': comps[:6]})

grass = {}
def probe_grass():
  for p in ('/Game/SoStylized/Environment/Foliage/Materials/MI_Grass', '/Game/SoStylized/Environment/Foliage/Materials/MI_Grass_LOD1'):
    mi = unreal.load_asset(p)
    if not mi:
        grass[p] = None; continue
    parent = mi.get_editor_property('parent')
    g = {'parent': parent.get_path_name() if parent else None, 'scalar': {}, 'vector': {}, 'texture': {}, 'static_switch': {}, 'parent_nodes': []}
    base = parent
    while isinstance(base, unreal.MaterialInstance):
        base = base.get_editor_property('parent')
    if base:
        for n in M.get_material_expressions(base):
            e = {'cls': n.get_class().get_name()}
            for k in ('parameter_name', 'default_value', 'texture', 'virtual_texture', 'material_type'):
                try:
                    v = n.get_editor_property(k); e[k] = v.get_path_name() if hasattr(v, 'get_path_name') else str(v)
                except Exception:
                    pass
            if isinstance(n, unreal.MaterialExpressionCustom):
                e['code'] = n.get_editor_property('code')[:400]
            g['parent_nodes'].append(e)
        g['base'] = base.get_path_name(); g['shading_model'] = str(base.get_editor_property('shading_model')); g['two_sided'] = base.get_editor_property('two_sided'); g['blend_mode'] = str(base.get_editor_property('blend_mode'))
    for name in M.get_scalar_parameter_names(mi):
        g['scalar'][str(name)] = M.get_material_instance_scalar_parameter_value(mi, name)
    for name in M.get_vector_parameter_names(mi):
        g['vector'][str(name)] = str(M.get_material_instance_vector_parameter_value(mi, name))
    for name in M.get_texture_parameter_names(mi):
        t = M.get_material_instance_texture_parameter_value(mi, name); g['texture'][str(name)] = t.get_path_name() if t else None
    for name in M.get_static_switch_parameter_names(mi):
        g['static_switch'][str(name)] = M.get_material_instance_static_switch_parameter_value(mi, name)
    grass[p] = g

for probe in (probe_houses, probe_grass):  # probes are informational; never let them block the render/quit
    try:
        probe()
    except Exception:
        import traceback; report.setdefault('probe_errors', []).append(traceback.format_exc()); unreal.log_warning('ROCK_V31 probe failed: ' + traceback.format_exc())
report['houses'] = houses; report['grass'] = grass
report['rvt_volumes'] = [a.get_actor_label() for a in E.get_all_level_actors() if isinstance(a, unreal.RuntimeVirtualTextureVolume)]

(B / 'Saved/anime_rock_v31.json').write_text(json.dumps(report, indent=1, default=str))
unreal.log('ROCK_V31 ' + json.dumps({'rock': changed, 'cave': cave_changes, 'houses': len(houses), 'rvt_volumes': report['rvt_volumes']}))

if os.environ.get('IV_RENDER_AFTER') == '1':
    import importlib.util
    spec = importlib.util.spec_from_file_location('render_anime_polish_v31', str(B / 'Scripts/render_anime_polish_v31.py'))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    views = [v for v in mod.VIEWS if v[0] in ('RimFront', 'RimEast', 'RimWest', 'RimNorth', 'Island', 'DungeonPath')] + [
        ('EdgeEast', (400, -100), None, (560, -40, None)),
        ('TradePassMouth', (-310, -100), None, (-355, -85, None)),
    ]
    mod.start_render(prefix='AnimePolish31_step3_', out_dir=Path(os.environ.get('IV_RENDER_DIR', str(B / 'Saved/AnimePolish31'))), views=views, warmup=90.0, quit_when_done=True)
