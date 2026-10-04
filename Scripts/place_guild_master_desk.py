"""Place AGuildMasterDesk on the island map, offset from spawn and the warp portal."""
import unreal

MAP = "/Game/IsekaiVillage/Maps/Map_Village"
LABEL = "GuildMasterDesk"
CLS = "/Script/IsekaiVillage.GuildMasterDesk"

levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
world_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels.load_level(MAP)

desk_cls = unreal.load_class(None, CLS)
if not desk_cls:
    raise RuntimeError("GuildMasterDesk class missing")

desk = None
for actor in world_sub.get_all_level_actors():
    if actor.get_actor_label() == LABEL:
        desk = actor
        break

loc = unreal.Vector(0.0, 350.0, 40.0)
if desk is None:
    desk = world_sub.spawn_actor_from_class(desk_cls, loc, unreal.Rotator())
else:
    desk.set_actor_location(loc, False, False)

desk.set_actor_label(LABEL)
desk.set_folder_path("Gameplay")
if not levels.save_current_level():
    raise RuntimeError("save failed")
unreal.log(f"[guild] placed {LABEL} at {desk.get_actor_location()}")
