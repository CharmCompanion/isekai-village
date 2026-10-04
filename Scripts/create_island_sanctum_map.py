import unreal

def create_island_sanctum_map():
    map_dir = "/Game/SpellCraft/Maps"
    map_name = "Map_IslandSanctum"
    full_map_path = f"{map_dir}/{map_name}"

    # 1. Create New World
    world_factory = unreal.WorldFactory()
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

    if unreal.EditorAssetLibrary.does_asset_exist(full_map_path):
        unreal.EditorAssetLibrary.delete_asset(full_map_path)

    # Create new level package
    unreal.EditorLevelLibrary.new_level(full_map_path)
    print(f"Created new level at: {full_map_path}")

    # Load and make it the active editing world
    unreal.EditorLevelLibrary.load_level(full_map_path)

    # 2. Spawn Directional Light (Sun)
    sun_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 5000), unreal.Rotator(-45, -35, 0))
    if sun_actor:
        sun_comp = sun_actor.get_component_by_class(unreal.DirectionalLightComponent)
        if sun_comp:
            sun_comp.set_editor_property("intensity", 6.0)
            sun_comp.set_editor_property("light_color", unreal.Color(255, 245, 230, 255))
            sun_comp.set_editor_property("atmosphere_sun_light", True)

    # 3. Spawn Sky Atmosphere
    unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))

    # 4. Spawn Sky Light
    skylight_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 1000), unreal.Rotator(0, 0, 0))
    if skylight_actor:
        skylight_comp = skylight_actor.get_component_by_class(unreal.SkyLightComponent)
        if skylight_comp:
            skylight_comp.set_editor_property("real_time_capture", True)

    # 5. Spawn Exponential Height Fog (Mystical Ocean Sea Mist)
    fog_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
    if fog_actor:
        fog_comp = fog_actor.get_component_by_class(unreal.ExponentialHeightFogComponent)
        if fog_comp:
            fog_comp.set_editor_property("fog_density", 0.003)
            fog_comp.set_editor_property("fog_inscattering_luminance", unreal.LinearColor(0.6, 0.8, 1.0, 1.0))

    # 6. Spawn Island Terrain Actor
    island_class = unreal.load_class(None, "/Script/SpellCraft.IslandTerrainActor")
    if island_class:
        island_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(island_class, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
        print("Spawned IslandTerrainActor successfully!")

    # 7. Spawn PlayerStart on South Beach Cove
    player_start = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(-2200, -400, 60), unreal.Rotator(0, 25, 0))
    print("Spawned PlayerStart at South Beach Cove!")

    # Save Current Level
    unreal.EditorLevelLibrary.save_current_level()
    print(f"Level {full_map_path} saved successfully!")

if __name__ == "__main__":
    create_island_sanctum_map()
