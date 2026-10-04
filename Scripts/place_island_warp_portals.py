"""
Place IslandWarpPortal + tagged PlayerStarts on the island and overworld maps.

UnrealEditor-Cmd.exe IsekaiVillage.uproject -unattended -nopause -nosplash
  -ExecutePythonScript=Scripts/place_island_warp_portals.py
"""
import unreal

ISLAND_MAPS = (
    "/Game/Maps/Map_Village",
    "/Game/IsekaiVillage/Maps/Map_Village",
)
OVERWORLD_MAP = "/Game/IsekaiVillage/Maps/Map_Overworld"
PORTAL_CLASS_PATH = "/Script/IsekaiVillage.IslandWarpPortal"
PORTAL_LABEL = "IslandWarpPortal"
START_LABEL = "WarpPlayerStart"


def actors_of(world_sub, cls):
    return [a for a in world_sub.get_all_level_actors() if isinstance(a, cls)]


def find_label(world_sub, label):
    for actor in world_sub.get_all_level_actors():
        if actor.get_actor_label() == label:
            return actor
    return None


def place_map(level_path, start_tag, dest_level, arrival_tag):
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    world_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    levels.load_level(level_path)

    portal_cls = unreal.load_class(None, PORTAL_CLASS_PATH)
    if not portal_cls:
        raise RuntimeError("IslandWarpPortal class missing — compile the game module first")

    existing_starts = actors_of(world_sub, unreal.PlayerStart)
    start = find_label(world_sub, START_LABEL)
    if start is None and existing_starts:
        start = existing_starts[0]
    if start is None:
        start = world_sub.spawn_actor_from_class(
            unreal.PlayerStart, unreal.Vector(0.0, 0.0, 100.0), unreal.Rotator()
        )
    start.set_actor_label(START_LABEL)
    start.set_editor_property("player_start_tag", unreal.Name(start_tag))
    start_loc = start.get_actor_location()

    portal_loc = unreal.Vector(start_loc.x + 500.0, start_loc.y, start_loc.z - 80.0)
    portal = find_label(world_sub, PORTAL_LABEL)
    if portal is None:
        portal = world_sub.spawn_actor_from_class(portal_cls, portal_loc, unreal.Rotator())
    else:
        portal.set_actor_location(portal_loc, False, False)
    portal.set_actor_label(PORTAL_LABEL)
    portal.set_folder_path("Gameplay")
    portal.set_editor_property("destination_level", unreal.Name(dest_level))
    portal.set_editor_property("arrival_player_start_tag", unreal.Name(arrival_tag))

    if not levels.save_current_level():
        raise RuntimeError(f"Failed to save {level_path}")

    unreal.log(
        f"[warp] {level_path} start={start_tag} at {start.get_actor_location()} "
        f"portal->{dest_level} arrive={arrival_tag} at {portal.get_actor_location()}"
    )


place_map(
    OVERWORLD_MAP,
    "Overworld",
    "/Game/IsekaiVillage/Maps/Map_Village",
    "Island",
)
for island_map in ISLAND_MAPS:
    if island_map == "/Game/Maps/Map_Village":
        continue
    place_map(
        island_map,
        "Island",
        "/Game/IsekaiVillage/Maps/Map_Overworld",
        "Overworld",
    )

unreal.log("[warp] placement complete")
