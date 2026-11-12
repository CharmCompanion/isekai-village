"""El Ruhn only: real rock albedo on the underside, rim/foundation stop walling the meadow."""
import unreal, json
from pathlib import Path

B = Path('D:/DEVELOPMENT/Games/IsekaiVillage')
R = '/Game/IsekaiVillage/AdventureWorld'
MAP = R + '/Maps/Map_AnimeAdventure'
A = unreal.EditorAssetLibrary
M = unreal.MaterialEditingLibrary
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert w.get_path_name().startswith(MAP + '.'), w.get_path_name()


def enum_val(cls, *names):
    for n in names:
        if hasattr(cls, n):
            return getattr(cls, n)
    return None


NO_COL = enum_val(unreal.CollisionEnabled, 'NO_COLLISION', 'QueryOnly')
PAWN = enum_val(unreal.CollisionChannel, 'PAWN', 'ECC_PAWN')
IGNORE = enum_val(unreal.CollisionResponse, 'IGNORE', 'ECR_IGNORE')
DEFAULT_TRACE = enum_val(unreal.CollisionTraceFlag, 'CTF_USE_DEFAULT', 'UseDefault')

ROCK = '''/*RockTex35*/
 float3 rock=C;
 float lum=dot(max(C,.001),float3(.3,.59,.11));
 rock*=lerp(.88,1.10,saturate(lum*1.45));
 float height=(H.r*65280.+H.g*255.-32768.)/64.*100.;
 float below=max(0,height-P.z);
 rock=lerp(rock,rock*float3(.78,.80,.84),saturate(below/28000.)*.35);
 return rock;
'''

report = {'material': [], 'custom_before': [], 'collar': [], 'foundation': []}

mat = unreal.load_asset(R + '/Materials/M_IV_SculptedGeology28')
assert mat
for n in M.get_material_expressions(mat):
    if not isinstance(n, unreal.MaterialExpressionCustom):
        continue
    code = n.get_editor_property('code')
    report['custom_before'].append(code[:180].replace('\n', ' | '))
    compact = code.replace(' ', '')
    if '/*AnimeStrata31*/' in code or '/*Mountain12*/' in code or '/*RockTex35*/' in code or 'band=sin(P.z' in compact:
        n.set_editor_property('code', ROCK)
        report['material'].append('base colour -> T_RockSpire triplanar, no bands')
    elif 'return (A*w.z+B*w.y+C*w.x)*float3' in compact:
        n.set_editor_property('code', 'float3 w=pow(abs(N),4);w/=max(dot(w,1),.001); return (A*w.z+B*w.y+C*w.x);')
        report['material'].append('removed grey/blue tint on triplanar rock')
    elif compact in ('return P.xy/4500.;', 'return P.xz/4500.;', 'return P.yz/4500.;',
                     'return P.xy/4200.;', 'return P.xz/4200.;', 'return P.yz/4200.;',
                     'return P.xy/1800.;', 'return P.xz/1800.;', 'return P.yz/1800.;',
                     'return P.xy/2400.;', 'return P.xz/2400.;', 'return P.yz/2400.;'):
        plane = 'xy' if '.xy' in compact else 'xz' if '.xz' in compact else 'yz'
        n.set_editor_property('code', 'return P.%s/2400.;' % plane)
        report['material'].append('%s tile 24 m' % plane)
M.recompile_material(mat)
A.save_loaded_asset(mat)


def disable_blocking(actor, bucket, also_mesh=False):
    actor.set_actor_enable_collision(False)
    c = actor.static_mesh_component
    if NO_COL is not None:
        c.set_collision_enabled(NO_COL)
    if PAWN is not None and IGNORE is not None:
        c.set_collision_response_to_channel(PAWN, IGNORE)
    mesh = c.static_mesh
    if also_mesh and mesh and DEFAULT_TRACE is not None:
        bs = mesh.get_editor_property('body_setup')
        if bs:
            bs.set_editor_property('collision_trace_flag', DEFAULT_TRACE)
            A.save_loaded_asset(mesh)
    report[bucket].append(actor.get_actor_label())


for a in E.get_all_level_actors():
    if not isinstance(a, unreal.StaticMeshActor):
        continue
    label = a.get_actor_label()
    tags = [str(t) for t in a.tags]
    mesh = a.static_mesh_component.static_mesh
    mesh_name = mesh.get_name() if mesh else ''
    if label == 'El Ruhn - rim rock collar v31' or 'IVRimCollar31' in tags or mesh_name == 'SM_IV_RimCollar_v31':
        disable_blocking(a, 'collar', also_mesh=True)
    elif label == 'El Ruhn - matching rock foundation' or mesh_name == 'SM_IV_JoinedMountain_v28':
        if PAWN is not None and IGNORE is not None:
            a.static_mesh_component.set_collision_response_to_channel(PAWN, IGNORE)
        report['foundation'].append(label)

assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(B / 'Saved/island_rock_fix_v35.json').write_text(json.dumps(report, indent=2))
unreal.log('V35_ISLAND_ROCK ' + json.dumps({k: report[k] for k in ('material', 'collar', 'foundation')}))
