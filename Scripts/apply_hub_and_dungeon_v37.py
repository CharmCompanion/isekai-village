"""Stamp El Ruhn adventurer plaza, five capital-tower hubs, and the starter dungeon map."""
import json
from pathlib import Path

import unreal

B = Path('D:/DEVELOPMENT/Games/IsekaiVillage')
S = B / 'Saved/AdventureWorldSource'
R = '/Game/IsekaiVillage/AdventureWorld'
ADV = R + '/Maps/Map_AnimeAdventure'
DUN = R + '/Maps/Map_ElRuhnDungeon'
TAG = 'Hub37'
OUT = B / 'Saved/hub_dungeon_applied_v37.json'


def status(**kw):
    OUT.write_text(json.dumps(kw, indent=2))


def uclass(name):
    cls = getattr(unreal, name, None)
    if cls:
        return cls
    loaded = unreal.load_class(None, '/Script/IsekaiVillage.' + name)
    assert loaded, name
    return loaded


def has_tag(actor, name):
    return name in [str(t) for t in actor.tags]


E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
W = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert W.get_path_name().startswith(ADV + '.'), W.get_path_name()

HubCls = uclass('AdventurerHub')
RuntimeCls = uclass('DungeonRuntime')
design = json.loads((S / 'world_design_v36.json').read_text(encoding='utf-8'))
capitals = [
    next(s for s in design['settlements'] if s['name'] == 'Yozuan regional capital'),
    next(s for s in design['settlements'] if s['name'] == 'Kelsin regional capital'),
    next(s for s in design['settlements'] if s['name'] == 'Rabaric regional capital'),
    next(s for s in design['settlements'] if s['name'] == 'Vylfod regional capital'),
    next(s for s in design['settlements'] if s['name'] == 'Northern island cathedral fortress'),
]

for actor in list(E.get_all_level_actors()):
    if has_tag(actor, TAG):
        E.destroy_actor(actor)

placed = []


def spawn_hub(label, xyz_m, interiors):
    loc = unreal.Vector(xyz_m[0] * 100.0, xyz_m[1] * 100.0, xyz_m[2] * 100.0)
    actor = E.spawn_actor_from_class(HubCls, loc, unreal.Rotator())
    actor.set_actor_label(label)
    actor.set_folder_path('Adventure/Hubs')
    actor.tags = [TAG]
    actor.set_editor_property('dungeon_level', DUN)
    actor.set_editor_property('dungeon_start_tag', 'DungeonStart')
    try:
        actor.set_editor_property('playable_interiors', interiors)
    except Exception:
        actor.set_editor_property('b_playable_interiors', interiors)
    placed.append({'label': label, 'xyz_m': xyz_m, 'interiors': interiors})
    return actor


# Plaza sits just south of the sealed mouth so the arch faces the tunnel.
spawn_hub('El Ruhn adventurer plaza', [230.0, 432.0, 115.0], True)
ret = E.spawn_actor_from_class(unreal.TargetPoint, unreal.Vector(23000.0, 42000.0, 11600.0))
ret.set_actor_label('Dungeon return')
ret.set_folder_path('Adventure/Hubs')
ret.tags = [TAG, 'DungeonReturn']
ps_ret = E.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(23000.0, 42000.0, 11680.0))
ps_ret.set_actor_label('Dungeon return start')
ps_ret.set_folder_path('Adventure/Hubs')
ps_ret.tags = [TAG, 'DungeonReturn']
ps_ret.set_editor_property('player_start_tag', 'DungeonReturn')

for site in capitals:
    x, y = site['xy_m']
    z = site['ground_m']
    spawn_hub(site['name'] + ' dungeon gate', [x, y - 80.0, z + 1.2], False)

assert LES.save_current_level()

if unreal.EditorAssetLibrary.does_asset_exist(DUN):
    LES.load_level(DUN)
else:
    LES.new_level(DUN)

E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for actor in list(E.get_all_level_actors()):
    if has_tag(actor, TAG) or actor.get_class().get_name() in ('DungeonRuntime', 'PlayerStart', 'DirectionalLight', 'SkyLight', 'ExponentialHeightFog', 'SkyAtmosphere'):
        if actor.get_class().get_name() != 'WorldSettings':
            if has_tag(actor, TAG) or actor.get_class().get_name() == 'DungeonRuntime':
                E.destroy_actor(actor)

runtime = E.spawn_actor_from_class(RuntimeCls, unreal.Vector(0, 0, 0))
runtime.set_actor_label('El Ruhn sealed cave runtime')
runtime.set_folder_path('Dungeon')
runtime.tags = [TAG]
runtime.set_editor_property('return_level', ADV)
runtime.set_editor_property('return_start_tag', 'DungeonReturn')

start = E.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(0, -300, 120))
start.set_actor_label('Dungeon start')
start.set_folder_path('Dungeon')
start.tags = [TAG, 'DungeonStart']
start.set_editor_property('player_start_tag', 'DungeonStart')

sun = E.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 2000), unreal.Rotator(pitch=-35, yaw=40))
sun.set_actor_label('Dungeon sun')
sun.tags = [TAG]
sky = E.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 1800))
sky.set_actor_label('Dungeon sky light')
sky.tags = [TAG]
fog = E.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(0, 0, 400))
fog.set_actor_label('Dungeon fog')
fog.tags = [TAG]

assert LES.save_current_level()
status(saved=True, adventure=ADV, dungeon=DUN, hubs=placed, graph=str(S / 'elruhn_dungeon_v37.json'))
unreal.log('V37_HUB_DUNGEON_APPLIED ' + str(len(placed)))
