"""
Create small non-World-Partition battle arenas at unused paths.
Does not load Map_Village / Map_Overworld / Map_Battle_* redirectors.

Close Unreal first, then:
  UnrealEditor-Cmd IsekaiVillage.uproject -ExecutePythonScript=Scripts/create_battle_stub_maps.py
"""
import unreal

MAPS = [
    "/Game/IsekaiVillage/Maps/BattleStub_Plains",
    "/Game/IsekaiVillage/Maps/BattleStub_Forest",
    "/Game/IsekaiVillage/Maps/BattleStub_Desert",
    "/Game/IsekaiVillage/Maps/BattleStub_Arena",
]
CUBE_MESH = "/Engine/BasicShapes/Cube.Cube"
GM_PATH = "/Script/IsekaiVillage.IsekaiVillageGameMode"


def spawn_static_mesh(mesh, loc, scale, name):
    actor_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actor = actor_sub.spawn_actor_from_class(
        unreal.StaticMeshActor, loc, unreal.Rotator(0, 0, 0)
    )
    if not actor:
        return None
    actor.set_actor_label(name)
    smc = actor.static_mesh_component
    smc.set_static_mesh(mesh)
    smc.set_world_scale3d(scale)
    smc.set_mobility(unreal.ComponentMobility.STATIC)
    return actor


def fill_arena(cube):
    actor_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    spawn_static_mesh(cube, unreal.Vector(0, 0, -10), unreal.Vector(40, 40, 0.2), "Battle_Floor")
    spawn_static_mesh(cube, unreal.Vector(0, 2000, 100), unreal.Vector(40, 1, 2), "Battle_Wall_N")
    spawn_static_mesh(cube, unreal.Vector(0, -2000, 100), unreal.Vector(40, 1, 2), "Battle_Wall_S")
    spawn_static_mesh(cube, unreal.Vector(2000, 0, 100), unreal.Vector(1, 40, 2), "Battle_Wall_E")
    spawn_static_mesh(cube, unreal.Vector(-2000, 0, 100), unreal.Vector(1, 40, 2), "Battle_Wall_W")

    sun = actor_sub.spawn_actor_from_class(
        unreal.DirectionalLight, unreal.Vector(0, 0, 4000), unreal.Rotator(-50, -30, 0)
    )
    if sun:
        c = sun.get_component_by_class(unreal.DirectionalLightComponent)
        if c:
            c.set_editor_property("intensity", 5.0)
            c.set_editor_property("atmosphere_sun_light", True)

    actor_sub.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
    sky = actor_sub.spawn_actor_from_class(
        unreal.SkyLight, unreal.Vector(0, 0, 1000), unreal.Rotator(0, 0, 0)
    )
    if sky:
        c = sky.get_component_by_class(unreal.SkyLightComponent)
        if c:
            c.set_editor_property("real_time_capture", True)

    ps = actor_sub.spawn_actor_from_class(
        unreal.PlayerStart, unreal.Vector(0, 0, 120), unreal.Rotator(0, 0, 0)
    )
    if ps:
        ps.set_actor_label("PlayerStart")

    world = unreal.UnrealEditorSubsystem().get_editor_world()
    if world:
        ws = world.get_world_settings()
        gm = unreal.load_class(None, GM_PATH)
        if ws and gm:
            ws.set_editor_property("default_game_mode", gm)


def create_battle_stub_maps():
    cube = unreal.EditorAssetLibrary.load_asset(CUBE_MESH)
    if not cube:
        unreal.log_error(f"Missing mesh: {CUBE_MESH}")
        return

    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    for path in MAPS:
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            print(f"BATTLE_STUB_SKIP exists {path}")
            continue
        les.new_level(path)
        fill_arena(cube)
        les.save_current_level()
        print(f"BATTLE_STUB_OK {path}")


if __name__ == "__main__":
    create_battle_stub_maps()
