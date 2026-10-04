"""
Flat graybox arena for magic testing. No landscape / island.

Close Unreal first, then:
  UnrealEditor-Cmd SpellCraft.uproject -run=pythonscript -script=Scripts/create_graybox_arena.py
"""
import unreal

MAP_PATH = "/Game/SpellCraft/Maps/Map_GrayboxArena"
CUBE_MESH = "/Engine/BasicShapes/Cube.Cube"


def spawn_static_mesh(mesh, loc, scale, name):
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
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


def create_graybox_arena():
    if not unreal.EditorAssetLibrary.does_directory_exist("/Game/SpellCraft/Maps"):
        unreal.EditorAssetLibrary.make_directory("/Game/SpellCraft/Maps")

    if unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH):
        unreal.EditorAssetLibrary.delete_asset(MAP_PATH)

    unreal.EditorLevelLibrary.new_level(MAP_PATH)
    unreal.EditorLevelLibrary.load_level(MAP_PATH)
    print(f"Created {MAP_PATH}")

    cube = unreal.EditorAssetLibrary.load_asset(CUBE_MESH)
    if not cube:
        unreal.log_error(f"Missing mesh: {CUBE_MESH}")
        return

    # Floor: 100m x 100m (cube is 100uu, scale 100,100,0.2 → 10000x10000x20)
    spawn_static_mesh(cube, unreal.Vector(0, 0, -10), unreal.Vector(100, 100, 0.2), "GB_Floor")

    # Perimeter low walls
    wall_h = unreal.Vector(100, 2, 4)
    spawn_static_mesh(cube, unreal.Vector(0, 5000, 200), wall_h, "GB_Wall_N")
    spawn_static_mesh(cube, unreal.Vector(0, -5000, 200), wall_h, "GB_Wall_S")
    spawn_static_mesh(cube, unreal.Vector(5000, 0, 200), unreal.Vector(2, 100, 4), "GB_Wall_E")
    spawn_static_mesh(cube, unreal.Vector(-5000, 0, 200), unreal.Vector(2, 100, 4), "GB_Wall_W")

    # Cover blocks for spell testing
    covers = [
        (unreal.Vector(800, 400, 150), unreal.Vector(3, 3, 3), "GB_Cover_A"),
        (unreal.Vector(-600, 900, 100), unreal.Vector(4, 2, 2), "GB_Cover_B"),
        (unreal.Vector(1200, -700, 200), unreal.Vector(2, 6, 4), "GB_Cover_C"),
        (unreal.Vector(-1400, -200, 250), unreal.Vector(5, 2, 5), "GB_Cover_D"),
        (unreal.Vector(0, 1800, 100), unreal.Vector(8, 2, 2), "GB_Cover_E"),
    ]
    for loc, scale, name in covers:
        spawn_static_mesh(cube, loc, scale, name)

    # Lighting
    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.DirectionalLight, unreal.Vector(0, 0, 4000), unreal.Rotator(-50, -30, 0)
    )
    if sun:
        c = sun.get_component_by_class(unreal.DirectionalLightComponent)
        if c:
            c.set_editor_property("intensity", 5.0)
            c.set_editor_property("atmosphere_sun_light", True)

    unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.SkyAtmosphere, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0)
    )

    sky = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.SkyLight, unreal.Vector(0, 0, 1000), unreal.Rotator(0, 0, 0)
    )
    if sky:
        c = sky.get_component_by_class(unreal.SkyLightComponent)
        if c:
            c.set_editor_property("real_time_capture", True)

    unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.PlayerStart, unreal.Vector(0, 0, 100), unreal.Rotator(0, 0, 0)
    )

    world = unreal.EditorLevelLibrary.get_editor_world()
    if world:
        ws = world.get_world_settings()
        if ws:
            gm = unreal.load_class(None, "/Script/SpellCraft.SpellCraftGameMode")
            if gm:
                ws.set_editor_property("default_game_mode", gm)
                print("WorldSettings GameMode -> SpellCraftGameMode")

    unreal.EditorLevelLibrary.save_current_level()
    print("GRAYBOX_OK saved Map_GrayboxArena")


if __name__ == "__main__":
    create_graybox_arena()
