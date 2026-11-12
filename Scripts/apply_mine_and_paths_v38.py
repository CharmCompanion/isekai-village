"""Hide left/right mountain routes, keep the mine approach, stamp a mining portal, author the mine map."""
import json
from pathlib import Path

import unreal

B = Path('D:/DEVELOPMENT/Games/IsekaiVillage')
R = '/Game/IsekaiVillage/AdventureWorld'
ADV = R + '/Maps/Map_AnimeAdventure'
MINE = R + '/Maps/Map_ElRuhnMine'
TAG = 'Mine38'
OUT = B / 'Saved/mine_paths_applied_v38.json'


def status(**kw):
    OUT.write_text(json.dumps(kw, indent=2))


def uclass(name):
    cls = getattr(unreal, name, None)
    return cls or unreal.load_class(None, '/Script/IsekaiVillage.' + name)


E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
W = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert W.get_path_name().startswith(ADV + '.'), W.get_path_name()

hidden = []
restored = []
for actor in list(E.get_all_level_actors()):
    folder = str(actor.get_folder_path())
    label = actor.get_actor_label()
    tags = [str(t) for t in actor.tags]
    is_mine = ('Adventure/Routes/Mine' in folder) or label.startswith('Mine') or ('Mine' in label and 'IVMountainRoutesV04' in tags)
    if is_mine:
        actor.set_actor_hidden_in_game(False)
        actor.set_actor_enable_collision(True)
        restored.append(label)
        continue
    drop = (
        'Adventure/Routes/TradePass' in folder
        or 'Adventure/Routes/Dungeon' in folder
        or label in ('Western Trade Pass', 'Sealed Dungeon Expedition Trail', 'Crown Pass')
        or ('TradePass' in label and 'IVMountainRoutesV04' in tags)
        or ('Dungeon' in label and 'IVMountainRoutesV04' in tags)
    )
    if drop:
        actor.set_actor_hidden_in_game(True)
        actor.set_actor_enable_collision(False)
        hidden.append(label)

for actor in list(E.get_all_level_actors()):
    if TAG in [str(t) for t in actor.tags]:
        E.destroy_actor(actor)

PortalCls = uclass('IslandWarpPortal')
loc = unreal.Vector(-32800.0, 29400.0, 6900.0)
portal = E.spawn_actor_from_class(PortalCls, loc, unreal.Rotator())
portal.set_actor_label('El Ruhn mine portal')
portal.set_folder_path('Adventure/Hubs')
portal.tags = [TAG]
portal.set_editor_property('destination_level', MINE)
portal.set_editor_property('arrival_player_start_tag', 'MineStart')
portal.set_editor_property('required_level', 1)

ret = E.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(-32800.0, 28600.0, 7000.0))
ret.set_actor_label('Mine return start')
ret.set_folder_path('Adventure/Hubs')
ret.tags = [TAG, 'MineReturn']
ret.set_editor_property('player_start_tag', 'MineReturn')
tp = E.spawn_actor_from_class(unreal.TargetPoint, unreal.Vector(-32800.0, 28600.0, 6980.0))
tp.set_actor_label('Mine return')
tp.set_folder_path('Adventure/Hubs')
tp.tags = [TAG, 'MineReturn']

assert LES.save_current_level()

if unreal.EditorAssetLibrary.does_asset_exist(MINE):
    LES.load_level(MINE)
else:
    LES.new_level(MINE)

E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
RuntimeCls = uclass('MineRuntime')
for actor in list(E.get_all_level_actors()):
    if TAG in [str(t) for t in actor.tags] or actor.get_class().get_name() == 'MineRuntime':
        E.destroy_actor(actor)

runtime = E.spawn_actor_from_class(RuntimeCls, unreal.Vector(0, 0, 0))
runtime.set_actor_label('El Ruhn mine runtime')
runtime.set_folder_path('Mine')
runtime.tags = [TAG]
runtime.set_editor_property('return_level', ADV)
runtime.set_editor_property('return_start_tag', 'MineReturn')

start = E.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(0, -400, 120))
start.set_actor_label('Mine start')
start.set_folder_path('Mine')
start.tags = [TAG, 'MineStart']
start.set_editor_property('player_start_tag', 'MineStart')

sun = E.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 2000), unreal.Rotator(pitch=-25, yaw=20))
sun.set_actor_label('Mine sun')
sun.tags = [TAG]
sky = E.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 1600))
sky.set_actor_label('Mine sky')
sky.tags = [TAG]
fog = E.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(0, 0, 200))
fog.set_actor_label('Mine fog')
fog.tags = [TAG]

assert LES.save_current_level()
status(saved=True, hidden=hidden, restored=restored, mine=MINE, portal=[-328, 294, 69])
unreal.log('V38_MINE_PATHS_APPLIED hidden=%d restored=%d' % (len(hidden), len(restored)))
