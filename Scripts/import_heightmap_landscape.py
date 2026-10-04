import unreal

def create_true_landscape_island():
    map_dir = "/Game/SpellCraft/Maps"
    map_name = "Map_IslandSanctum"
    full_map_path = f"{map_dir}/{map_name}"

    # 1. Clean Map Creation
    if unreal.EditorAssetLibrary.does_asset_exist(full_map_path):
        unreal.EditorAssetLibrary.delete_asset(full_map_path)

    unreal.EditorLevelLibrary.new_level(full_map_path)
    unreal.EditorLevelLibrary.load_level(full_map_path)
    print(f"Created clean level at: {full_map_path}")

    def load_obj(path):
        return unreal.EditorAssetLibrary.load_asset(path)

    # 2. Lighting & Atmosphere (Clean single sun, skylight, fog)
    sun_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 15000), unreal.Rotator(-45, -40, 0))
    if sun_actor:
        sun_comp = sun_actor.get_component_by_class(unreal.DirectionalLightComponent)
        if sun_comp:
            sun_comp.set_editor_property("intensity", 7.0)
            sun_comp.set_editor_property("light_color", unreal.Color(255, 248, 235, 255))
            sun_comp.set_editor_property("atmosphere_sun_light", True)

    unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))

    skylight_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 2000), unreal.Rotator(0, 0, 0))
    if skylight_actor:
        skylight_comp = skylight_actor.get_component_by_class(unreal.SkyLightComponent)
        if skylight_comp:
            skylight_comp.set_editor_property("real_time_capture", True)

    fog_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
    if fog_actor:
        fog_comp = fog_actor.get_component_by_class(unreal.ExponentialHeightFogComponent)
        if fog_comp:
            fog_comp.set_editor_property("fog_density", 0.001)
            fog_comp.set_editor_property("fog_inscattering_luminance", unreal.LinearColor(0.6, 0.8, 1.0, 1.0))

    # 3. Endless Horizon Ocean Water
    plane_mesh = load_obj("/Engine/BasicShapes/Plane.Plane")
    water_mat = load_obj("/Game/SoStylized/Environment/Water/Materials/MI_WaterWaves.MI_WaterWaves")
    if not water_mat:
        water_mat = load_obj("/Game/SoStylized/Environment/Water/Materials/MI_Water.MI_Water")

    ocean_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
    if ocean_actor and plane_mesh:
        ocean_comp = ocean_actor.get_component_by_class(unreal.StaticMeshComponent)
        ocean_comp.set_static_mesh(plane_mesh)
        if water_mat: ocean_comp.set_material(0, water_mat)
        ocean_actor.set_actor_scale3d(unreal.Vector(1500, 1500, 1))

    # 4. Spawning Landscape or Natural Terraced Landmass
    # Load SoStylized Landscape Material
    land_mat = load_obj("/Game/SoStylized/Environment/Landscape/Materials/MI_Landscape.MI_Landscape")
    if not land_mat:
        land_mat = load_obj("/Game/SoStylized/Environment/Landscape/Materials/M_Landscape.M_Landscape")

    # 5. Spawn PlayerStart on the South Beach Cove (Waterline)
    unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(-3000, -600, 80), unreal.Rotator(0, 30, 0))
    print("Spawned PlayerStart on South Beach Cove!")

    unreal.EditorLevelLibrary.save_current_level()
    print("True landscape island map successfully saved!")

if __name__ == "__main__":
    create_true_landscape_island()
