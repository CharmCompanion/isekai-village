import unreal

def build_natural_island():
    map_dir = "/Game/SpellCraft/Maps"
    map_name = "Map_IslandSanctum"
    full_map_path = f"{map_dir}/{map_name}"

    if unreal.EditorAssetLibrary.does_asset_exist(full_map_path):
        unreal.EditorAssetLibrary.delete_asset(full_map_path)

    unreal.EditorLevelLibrary.new_level(full_map_path)
    unreal.EditorLevelLibrary.load_level(full_map_path)
    print(f"Created clean level at: {full_map_path}")

    def load_obj(path):
        return unreal.EditorAssetLibrary.load_asset(path)

    # 1. Single Sun Directional Light (Clean, forward shading priority 0)
    sun_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 10000), unreal.Rotator(-40, -50, 0))
    if sun_actor:
        sun_comp = sun_actor.get_component_by_class(unreal.DirectionalLightComponent)
        if sun_comp:
            sun_comp.set_editor_property("intensity", 6.5)
            sun_comp.set_editor_property("light_color", unreal.Color(255, 248, 235, 255))
            sun_comp.set_editor_property("atmosphere_sun_light", True)

    # 2. Sky Atmosphere & Skylight
    unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))

    skylight_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 2000), unreal.Rotator(0, 0, 0))
    if skylight_actor:
        skylight_comp = skylight_actor.get_component_by_class(unreal.SkyLightComponent)
        if skylight_comp:
            skylight_comp.set_editor_property("real_time_capture", True)

    # 3. Soft Coastal Sea Mist Fog
    fog_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
    if fog_actor:
        fog_comp = fog_actor.get_component_by_class(unreal.ExponentialHeightFogComponent)
        if fog_comp:
            fog_comp.set_editor_property("fog_density", 0.001)
            fog_comp.set_editor_property("fog_inscattering_luminance", unreal.LinearColor(0.6, 0.8, 1.0, 1.0))

    # 4. Massive Horizon Ocean Water
    plane_mesh = load_obj("/Engine/BasicShapes/Plane.Plane")
    water_mat = load_obj("/Game/SoStylized/Environment/Water/Materials/MI_WaterWaves.MI_WaterWaves")
    if not water_mat:
        water_mat = load_obj("/Game/SoStylized/Environment/Water/Materials/MI_Water.MI_Water")

    ocean_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
    if ocean_actor and plane_mesh:
        ocean_comp = ocean_actor.get_component_by_class(unreal.StaticMeshComponent)
        ocean_comp.set_static_mesh(plane_mesh)
        if water_mat: ocean_comp.set_material(0, water_mat)
        ocean_actor.set_actor_scale3d(unreal.Vector(1200, 1200, 1)) # Vast ocean plane

    # Asset paths
    plat1 = "/Game/SoStylized/Environment/Rocks/Classic/SM_PlatformClassic1.SM_PlatformClassic1"
    plat2 = "/Game/SoStylized/Environment/Rocks/Classic/SM_PlatformClassic2.SM_PlatformClassic2"
    plat3 = "/Game/SoStylized/Environment/Rocks/Classic/SM_PlatformClassic3.SM_PlatformClassic3"
    plat4 = "/Game/SoStylized/Environment/Rocks/Classic/SM_PlatformClassic4.SM_PlatformClassic4"

    cliff1 = "/Game/SoStylized/Environment/Rocks/Classic/SM_CliffClassic1.SM_CliffClassic1"
    cliff2 = "/Game/SoStylized/Environment/Rocks/Classic/SM_CliffClassic2.SM_CliffClassic2"
    cliff3 = "/Game/SoStylized/Environment/Rocks/Classic/SM_CliffClassic3.SM_CliffClassic3"
    cliff4 = "/Game/SoStylized/Environment/Rocks/Classic/SM_CliffClassic4.SM_CliffClassic4"

    boulder1 = "/Game/SoStylized/Environment/Rocks/Classic/SM_BoulderClassic1.SM_BoulderClassic1"
    boulder2 = "/Game/SoStylized/Environment/Rocks/Classic/SM_BoulderClassic2.SM_BoulderClassic2"
    boulder3 = "/Game/SoStylized/Environment/Rocks/Classic/SM_BoulderClassic3.SM_BoulderClassic3"
    boulder_clump1 = "/Game/SoStylized/Environment/Rocks/Classic/SM_BoulderClumpClassic1.SM_BoulderClumpClassic1"
    boulder_clump2 = "/Game/SoStylized/Environment/Rocks/Classic/SM_BoulderClumpClassic2.SM_BoulderClumpClassic2"

    def spawn_mesh(mesh_path, loc, rot, scale):
        mesh = load_obj(mesh_path)
        if not mesh: return None
        act = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, loc, rot)
        if act:
            comp = act.get_component_by_class(unreal.StaticMeshComponent)
            comp.set_static_mesh(mesh)
            act.set_actor_scale3d(scale)
        return act

    # --- 5. NATURAL ORGANIC ISLAND SHORELINE & ELEVATIONS (Realistic human scale) ---

    # A. SOUTH BEACH COVE (Flat, gentle sand & rock shoreline at Z = 5 to 30)
    # Spanning 40 meters wide along the southern bay
    spawn_mesh(plat1, unreal.Vector(-3500, -800, 5), unreal.Rotator(0, 20, 0), unreal.Vector(3.5, 4.0, 1.2))
    spawn_mesh(plat2, unreal.Vector(-3000, -600, 12), unreal.Rotator(1, -10, 0), unreal.Vector(3.2, 3.8, 1.2))
    spawn_mesh(plat3, unreal.Vector(-2600, -900, 8), unreal.Rotator(-1, 35, 0), unreal.Vector(3.0, 3.5, 1.0))
    spawn_mesh(plat4, unreal.Vector(-2200, -700, 15), unreal.Rotator(0, -25, 0), unreal.Vector(3.5, 3.5, 1.2))

    # Shoreline boulder clusters breaking the waves naturally
    spawn_mesh(boulder_clump1, unreal.Vector(-3800, -1100, -10), unreal.Rotator(0, 45, 0), unreal.Vector(1.8, 1.8, 1.5))
    spawn_mesh(boulder1, unreal.Vector(-3200, -1200, -5), unreal.Rotator(15, -20, 0), unreal.Vector(1.5, 1.5, 1.5))
    spawn_mesh(boulder2, unreal.Vector(-2400, -1100, -8), unreal.Rotator(0, 60, 0), unreal.Vector(1.6, 1.6, 1.4))
    spawn_mesh(boulder_clump2, unreal.Vector(-1800, -950, -10), unreal.Rotator(0, -30, 0), unreal.Vector(1.7, 1.7, 1.5))

    # B. GENTLE ASCENDING VALLEY TRAIL (Z = 30 -> 120 -> 220)
    # Wide, walkable grassy path curving naturally up through the island
    spawn_mesh(plat1, unreal.Vector(-2000, -300, 35), unreal.Rotator(2, 15, 0), unreal.Vector(3.8, 4.0, 1.4))
    spawn_mesh(plat2, unreal.Vector(-1500, -100, 65), unreal.Rotator(3, -12, 0), unreal.Vector(3.6, 3.8, 1.5))
    spawn_mesh(plat3, unreal.Vector(-1000, 150, 105), unreal.Rotator(2, 30, 0), unreal.Vector(3.8, 3.6, 1.6))
    spawn_mesh(plat4, unreal.Vector(-500, 350, 150), unreal.Rotator(1, -20, 0), unreal.Vector(3.5, 3.8, 1.6))
    spawn_mesh(plat1, unreal.Vector(0, 200, 190), unreal.Rotator(2, 10, 0), unreal.Vector(4.0, 4.0, 1.8))
    spawn_mesh(plat2, unreal.Vector(500, 0, 230), unreal.Rotator(0, -15, 0), unreal.Vector(3.8, 3.8, 1.8))

    # Natural flanking hillside rock outcrops along the valley (Organic human scale 2.0 - 3.0)
    spawn_mesh(cliff1, unreal.Vector(-2200, 600, 20), unreal.Rotator(0, -60, 0), unreal.Vector(2.5, 2.5, 2.5))
    spawn_mesh(cliff2, unreal.Vector(-1400, 900, 60), unreal.Rotator(0, -85, 0), unreal.Vector(2.8, 2.8, 2.8))
    spawn_mesh(cliff3, unreal.Vector(-600, 1100, 110), unreal.Rotator(0, -105, 0), unreal.Vector(3.0, 3.0, 3.0))
    spawn_mesh(cliff4, unreal.Vector(200, 1000, 170), unreal.Rotator(0, -125, 0), unreal.Vector(3.0, 3.0, 3.0))

    spawn_mesh(cliff2, unreal.Vector(-1800, -1200, 20), unreal.Rotator(0, 65, 0), unreal.Vector(2.5, 2.5, 2.5))
    spawn_mesh(cliff4, unreal.Vector(-1000, -1000, 70), unreal.Rotator(0, 80, 0), unreal.Vector(2.8, 2.8, 2.8))
    spawn_mesh(cliff1, unreal.Vector(-200, -800, 130), unreal.Rotator(0, 95, 0), unreal.Vector(3.0, 3.0, 3.0))
    spawn_mesh(cliff3, unreal.Vector(600, -700, 190), unreal.Rotator(0, 110, 0), unreal.Vector(3.0, 3.0, 3.0))

    # C. EXPANSIVE NORTHERN TOWER PLATEAU (Flat, scenic elevated grounds at Z = 280 to 310)
    # A wide, open 50-meter building expanse overlooking the ocean
    spawn_mesh(plat1, unreal.Vector(1200, -300, 285), unreal.Rotator(0, 10, 0), unreal.Vector(4.5, 4.5, 2.0))
    spawn_mesh(plat2, unreal.Vector(1600, 200, 290), unreal.Rotator(0, -15, 0), unreal.Vector(4.5, 4.5, 2.0))
    spawn_mesh(plat3, unreal.Vector(1300, 600, 288), unreal.Rotator(0, 35, 0), unreal.Vector(4.0, 4.2, 2.0))
    spawn_mesh(plat4, unreal.Vector(1800, -200, 292), unreal.Rotator(0, -30, 0), unreal.Vector(4.2, 4.2, 2.0))
    spawn_mesh(plat1, unreal.Vector(2100, 300, 295), unreal.Rotator(0, 20, 0), unreal.Vector(4.5, 4.5, 2.0))

    # Scenic northern backdrop sea-cliffs guarding the edge overlooking deep ocean
    spawn_mesh(cliff1, unreal.Vector(2600, -400, 120), unreal.Rotator(0, 160, 0), unreal.Vector(3.5, 3.5, 3.8))
    spawn_mesh(cliff3, unreal.Vector(2700, 200, 130), unreal.Rotator(0, 180, 0), unreal.Vector(3.8, 3.8, 4.0))
    spawn_mesh(cliff2, unreal.Vector(2500, 800, 120), unreal.Rotator(0, -165, 0), unreal.Vector(3.5, 3.5, 3.8))

    # Coastal sea-stacks in the bay
    spawn_mesh(cliff4, unreal.Vector(3500, -1200, -50), unreal.Rotator(0, 45, 0), unreal.Vector(2.8, 2.8, 3.5))
    spawn_mesh(cliff1, unreal.Vector(3600, 1400, -50), unreal.Rotator(0, -45, 0), unreal.Vector(2.8, 2.8, 3.5))

    # 6. Player Start on the Sandy Beach
    unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(-3000, -600, 70), unreal.Rotator(0, 30, 0))
    print("Spawned PlayerStart at South Beach Cove!")

    unreal.EditorLevelLibrary.save_current_level()
    print("Natural organic island map built and saved!")

if __name__ == "__main__":
    build_natural_island()
