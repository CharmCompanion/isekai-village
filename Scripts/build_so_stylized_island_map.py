import unreal

def build_so_stylized_island():
    map_dir = "/Game/SpellCraft/Maps"
    map_name = "Map_IslandSanctum"
    full_map_path = f"{map_dir}/{map_name}"

    # 1. Create and Load Level
    if unreal.EditorAssetLibrary.does_asset_exist(full_map_path):
        unreal.EditorAssetLibrary.delete_asset(full_map_path)

    unreal.EditorLevelLibrary.new_level(full_map_path)
    unreal.EditorLevelLibrary.load_level(full_map_path)
    print(f"Created and loaded {full_map_path}")

    # Helper asset loader
    def load_obj(path):
        return unreal.EditorAssetLibrary.load_asset(path)

    # 2. Setup Lighting and Sky
    sun_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 8000), unreal.Rotator(-42, -45, 0))
    if sun_actor:
        sun_comp = sun_actor.get_component_by_class(unreal.DirectionalLightComponent)
        if sun_comp:
            sun_comp.set_editor_property("intensity", 7.5)
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
            fog_comp.set_editor_property("fog_density", 0.0015)
            fog_comp.set_editor_property("fog_inscattering_luminance", unreal.LinearColor(0.55, 0.78, 1.0, 1.0))

    # 3. Spawn Stylized Ocean Water (BP_Water)
    water_bp = unreal.load_class(None, "/Game/SoStylized/Environment/Water/BP_Water.BP_Water_C")
    if water_bp:
        water_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(water_bp, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
        if water_actor:
            water_actor.set_actor_scale3d(unreal.Vector(80, 80, 1))
            print("Spawned SoStylized BP_Water ocean expanse!")
    else:
        # Fallback ocean plane with MI_WaterWaves
        plane_mesh = load_obj("/Engine/BasicShapes/Plane.Plane")
        water_mat = load_obj("/Game/SoStylized/Environment/Water/Materials/MI_WaterWaves.MI_WaterWaves")
        ocean_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
        if ocean_actor and plane_mesh:
            ocean_comp = ocean_actor.get_component_by_class(unreal.StaticMeshComponent)
            ocean_comp.set_static_mesh(plane_mesh)
            if water_mat: ocean_comp.set_material(0, water_mat)
            ocean_actor.set_actor_scale3d(unreal.Vector(500, 500, 1))

    # Helper mesh spawner
    def spawn_mesh(mesh_path, loc, rot, scale, mat_path=None):
        mesh = load_obj(mesh_path)
        if not mesh: return None
        act = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, loc, rot)
        if act:
            comp = act.get_component_by_class(unreal.StaticMeshComponent)
            comp.set_static_mesh(mesh)
            if mat_path:
                mat = load_obj(mat_path)
                if mat: comp.set_material(0, mat)
            act.set_actor_scale3d(scale)
        return act

    # Paths to SoStylized Assets
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
    boulder_clump = "/Game/SoStylized/Environment/Rocks/Classic/SM_BoulderClumpClassic1.SM_BoulderClumpClassic1"

    # --- 4. ASSEMBLE ORGANIC ISLAND GEOMETRY ---

    # A. South Beach Starting Cove (Z = 10 to 60)
    spawn_mesh(plat1, unreal.Vector(-2400, -600, 10), unreal.Rotator(0, 35, 0), unreal.Vector(12, 14, 2.5))
    spawn_mesh(plat2, unreal.Vector(-2000, -300, 25), unreal.Rotator(2, -15, 0), unreal.Vector(10, 12, 2.8))
    spawn_mesh(boulder_clump, unreal.Vector(-2800, -900, 0), unreal.Rotator(0, 45, 0), unreal.Vector(4, 4, 3))
    spawn_mesh(boulder_clump, unreal.Vector(-1800, -1100, 0), unreal.Rotator(0, -60, 0), unreal.Vector(4, 4, 3))

    # B. Central Ascending Valley & Terraces (Z = 80 to 280)
    spawn_mesh(plat3, unreal.Vector(-1200, -200, 90), unreal.Rotator(0, 10, 0), unreal.Vector(14, 15, 3.5))
    spawn_mesh(plat4, unreal.Vector(-400, 100, 180), unreal.Rotator(0, -25, 0), unreal.Vector(16, 16, 4.0))
    spawn_mesh(plat1, unreal.Vector(400, 300, 270), unreal.Rotator(0, 40, 0), unreal.Vector(15, 14, 4.2))

    # Valley Flanking Sea Cliffs
    spawn_mesh(cliff1, unreal.Vector(-1600, 800, 40), unreal.Rotator(0, -75, 0), unreal.Vector(5, 5, 5))
    spawn_mesh(cliff2, unreal.Vector(-800, 1200, 80), unreal.Rotator(0, -90, 0), unreal.Vector(6, 6, 6))
    spawn_mesh(cliff3, unreal.Vector(200, 1400, 150), unreal.Rotator(0, -110, 0), unreal.Vector(7, 7, 7))

    spawn_mesh(cliff2, unreal.Vector(-1400, -1200, 40), unreal.Rotator(0, 80, 0), unreal.Vector(5, 5, 5))
    spawn_mesh(cliff4, unreal.Vector(-500, -1400, 100), unreal.Rotator(0, 95, 0), unreal.Vector(6, 6, 6))
    spawn_mesh(cliff1, unreal.Vector(400, -1300, 180), unreal.Rotator(0, 115, 0), unreal.Vector(7, 7, 7))

    # C. High Northern Tower Plateau (Z = 450 to 520) - Scenic building grounds overlooking ocean
    spawn_mesh(plat2, unreal.Vector(1500, 0, 440), unreal.Rotator(0, 0, 0), unreal.Vector(18, 18, 5.0))
    spawn_mesh(plat3, unreal.Vector(2100, 200, 460), unreal.Rotator(0, 30, 0), unreal.Vector(16, 15, 5.2))
    spawn_mesh(plat4, unreal.Vector(1900, -400, 450), unreal.Rotator(0, -20, 0), unreal.Vector(15, 16, 5.0))

    # Grand Sheer Northern Sea Cliffs (Massive backdrop into deep ocean)
    spawn_mesh(cliff1, unreal.Vector(2800, 600, 200), unreal.Rotator(0, -160, 0), unreal.Vector(9, 9, 9))
    spawn_mesh(cliff3, unreal.Vector(3000, -300, 200), unreal.Rotator(0, 175, 0), unreal.Vector(10, 10, 9))
    spawn_mesh(cliff2, unreal.Vector(2500, -1200, 200), unreal.Rotator(0, 150, 0), unreal.Vector(8, 8, 8))

    # Coastal Sea-Stack Pillars in Ocean
    spawn_mesh(cliff4, unreal.Vector(3800, 1200, -100), unreal.Rotator(0, 45, 0), unreal.Vector(7, 7, 10))
    spawn_mesh(cliff1, unreal.Vector(-3600, 1500, -100), unreal.Rotator(0, -45, 0), unreal.Vector(6, 6, 8))
    spawn_mesh(boulder1, unreal.Vector(-3200, -1600, -50), unreal.Rotator(0, 20, 0), unreal.Vector(5, 5, 6))

    # 5. Spawn PlayerStart on South Beach
    unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(-2400, -600, 120), unreal.Rotator(0, 30, 0))
    print("Spawned PlayerStart at South Beach Cove!")

    # 6. Save Level
    unreal.EditorLevelLibrary.save_current_level()
    print("Map_IslandSanctum successfully built and saved with SoStylized assets!")

if __name__ == "__main__":
    build_so_stylized_island()
