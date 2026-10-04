"""
Reset Height map: remove scattered props, fix lighting, set up Demonstration-style
environment (sky, RVT, water, grass streaming). Optional modest island props.

Run with editor CLOSED:
  T:\\Program Files\\UE_5.8\\Engine\\Binaries\\Win64\\UnrealEditor-Cmd.exe ^
    F:\\DEVELOPMENT\\Games\\SpellCraft\\SpellCraft.uproject ^
    -run=pythonscript ^
    -script="F:\\DEVELOPMENT\\Games\\SpellCraft\\Scripts\\reset_and_setup_height_map.py"
"""
import math
import unreal

MAP_PATH = "/Game/SpellCraft/Maps/Height"
GRASS_STREAMING = "/Game/SoStylized/Maps/CompleteVol1/StreamingLevel_Demo_Grass"

ASSETS = {
    "landscape_mat": "/Game/SoStylized/Environment/Landscape/Materials/MI_Landscape.MI_Landscape",
    "rvt_landscape": "/Game/SoStylized/Environment/Landscape/Textures/RVT_Landscape.RVT_Landscape",
    "rvt_height": "/Game/SoStylized/Environment/Landscape/Textures/RVT_LandscapeHeight.RVT_LandscapeHeight",
    "sky_bp": "/Game/SoStylized/Environment/Sky/BP_StylizedSky_Lite.BP_StylizedSky_Lite_C",
    "water_bp": "/Game/SoStylized/Environment/Water/BP_Water.BP_Water_C",
}

RVT_SPECS = [
    {
        "loc": unreal.Vector(-50400.0, -50400.0, -4320.3125),
        "scale": unreal.Vector(100800.0, 100908.0, 25468.75),
        "rvt": "rvt_landscape",
    },
    {
        "loc": unreal.Vector(-50400.0, -50400.0, -4320.3125),
        "scale": unreal.Vector(100800.0, 100800.0, 25468.75),
        "rvt": "rvt_height",
    },
]

# Coast cliffs + beach rocks + interior trees (modest counts, island-scale placement)
CLIFF_MESHES = [
    "/Game/SoStylized/Environment/Rocks/Classic/SM_CliffClassic1.SM_CliffClassic1",
    "/Game/SoStylized/Environment/Rocks/Classic/SM_CliffClassic2.SM_CliffClassic2",
    "/Game/SoStylized/Environment/Rocks/Classic/SM_CliffClassic3.SM_CliffClassic3",
    "/Game/SoStylized/Environment/Rocks/Classic/SM_CliffClassic4.SM_CliffClassic4",
]

ROCK_MESHES = [
    "/Game/SoStylized/Environment/Rocks/Classic/SM_BoulderClumpClassic1.SM_BoulderClumpClassic1",
    "/Game/SoStylized/Environment/Rocks/Classic/SM_RockClumpClassic2.SM_RockClumpClassic2",
    "/Game/SoStylized/Environment/Rocks/Classic/SM_BoulderClassic2.SM_BoulderClassic2",
]

TREE_MESHES = [
    "/Game/SoStylized/Environment/Trees/Oak/SM_OakTree1.SM_OakTree1",
    "/Game/SoStylized/Environment/Trees/Oak/SM_OakTree2.SM_OakTree2",
    "/Game/SoStylized/Environment/Trees/Pine/SM_Pine01.SM_Pine01",
]

BUSH_MESHES = [
    "/Game/SoStylized/Environment/Foliage/SM_Bush1.SM_Bush1",
    "/Game/SoStylized/Environment/Foliage/SM_Fern1.SM_Fern1",
]

# Island center in world space (landscape origin + half extent)
ISLAND_CENTER = unreal.Vector(0.0, 0.0, 0.0)
ISLAND_COAST_RADIUS = 14000.0


def log(msg):
    unreal.log(msg)
    print(msg)


def load_asset(path):
    return unreal.EditorAssetLibrary.load_asset(path)


def actor_sub():
    return unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


def load_map():
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP_PATH)


def all_actors():
    return actor_sub().get_all_level_actors()


def save():
    unreal.EditorLevelLibrary.save_current_level()


def clear_mess():
    """Remove all placed static meshes and duplicate environment actors."""
    removed = {"meshes": 0, "lights": 0, "sky": 0, "water": 0, "rvt": 0, "fog": 0}

    for act in list(all_actors()):
        if isinstance(act, unreal.StaticMeshActor):
            actor_sub().destroy_actor(act)
            removed["meshes"] += 1

    # Keep only the first of each environment type; destroy duplicates
    seen = {
        "DirectionalLight": False,
        "SkyLight": False,
        "SkyAtmosphere": False,
        "ExponentialHeightFog": False,
        "RuntimeVirtualTextureVolume": 0,
        "BP_StylizedSky_Lite_C": False,
        "BP_Water_C": False,
    }

    for act in list(all_actors()):
        cls = act.get_class().get_name()
        if isinstance(act, unreal.DirectionalLight):
            if seen["DirectionalLight"]:
                actor_sub().destroy_actor(act)
                removed["lights"] += 1
            else:
                seen["DirectionalLight"] = True
        elif isinstance(act, unreal.SkyLight):
            if seen["SkyLight"]:
                actor_sub().destroy_actor(act)
                removed["lights"] += 1
            else:
                seen["SkyLight"] = True
        elif isinstance(act, unreal.SkyAtmosphere):
            if seen["SkyAtmosphere"]:
                actor_sub().destroy_actor(act)
                removed["fog"] += 1
            else:
                seen["SkyAtmosphere"] = True
        elif isinstance(act, unreal.ExponentialHeightFog):
            if seen["ExponentialHeightFog"]:
                actor_sub().destroy_actor(act)
                removed["fog"] += 1
            else:
                seen["ExponentialHeightFog"] = True
        elif isinstance(act, unreal.RuntimeVirtualTextureVolume):
            seen["RuntimeVirtualTextureVolume"] += 1
            if seen["RuntimeVirtualTextureVolume"] > 2:
                actor_sub().destroy_actor(act)
                removed["rvt"] += 1
        elif cls == "BP_StylizedSky_Lite_C":
            if seen["BP_StylizedSky_Lite_C"]:
                actor_sub().destroy_actor(act)
                removed["sky"] += 1
            else:
                seen["BP_StylizedSky_Lite_C"] = True
        elif cls == "BP_Water_C":
            if seen["BP_Water_C"]:
                actor_sub().destroy_actor(act)
                removed["water"] += 1
            else:
                seen["BP_Water_C"] = True

    log(f"Cleared mess: {removed}")
    return removed


def find_landscape():
    for act in all_actors():
        if isinstance(act, unreal.Landscape):
            return act
    return None


def ensure_sky():
    if not any(a.get_class().get_name() == "BP_StylizedSky_Lite_C" for a in all_actors()):
        cls = unreal.load_class(None, ASSETS["sky_bp"])
        if cls:
            actor_sub().spawn_actor_from_class(cls, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
            log("Spawned BP_StylizedSky_Lite")


def ensure_atmosphere():
    sub = actor_sub()
    if not any(isinstance(a, unreal.SkyAtmosphere) for a in all_actors()):
        sub.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
    if not any(isinstance(a, unreal.ExponentialHeightFog) for a in all_actors()):
        fog = sub.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
        comp = fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
        if comp:
            comp.set_editor_property("fog_density", 0.0012)
            comp.set_editor_property("fog_inscattering_luminance", unreal.LinearColor(0.55, 0.78, 1.0, 1.0))


def ensure_single_sun():
    sun = None
    for act in all_actors():
        if isinstance(act, unreal.DirectionalLight):
            sun = act
            break
    if not sun:
        sun = actor_sub().spawn_actor_from_class(
            unreal.DirectionalLight,
            unreal.Vector(0, 0, 15000),
            unreal.Rotator(-42, -45, 0),
        )
    comp = sun.get_component_by_class(unreal.DirectionalLightComponent)
    if comp:
        comp.set_editor_property("intensity", 7.5)
        comp.set_editor_property("atmosphere_sun_light", True)
        comp.set_editor_property("light_color", unreal.Color(255, 248, 235, 255))
        try:
            comp.set_editor_property("forward_shading_priority", 0)
        except Exception:
            pass


def ensure_skylight():
    sl = None
    for act in all_actors():
        if isinstance(act, unreal.SkyLight):
            sl = act
            break
    if not sl:
        sl = actor_sub().spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 2000), unreal.Rotator(0, 0, 0))
    comp = sl.get_component_by_class(unreal.SkyLightComponent)
    if comp:
        comp.set_editor_property("real_time_capture", True)


def ensure_rvt():
    count = sum(1 for a in all_actors() if isinstance(a, unreal.RuntimeVirtualTextureVolume))
    if count >= 2:
        return
    for spec in RVT_SPECS[count:]:
        rvt_asset = load_asset(ASSETS[spec["rvt"]])
        vol = actor_sub().spawn_actor_from_class(
            unreal.RuntimeVirtualTextureVolume,
            spec["loc"],
            unreal.Rotator(0, 0, 0),
        )
        vol.set_actor_scale3d(spec["scale"])
        comp = vol.get_component_by_class(unreal.RuntimeVirtualTextureComponent)
        if comp and rvt_asset:
            try:
                comp.set_editor_property("virtual_texture", rvt_asset)
            except Exception:
                pass
        log(f"Spawned RVT ({spec['rvt']})")


def ensure_ocean():
    water_cls = unreal.load_class(None, ASSETS["water_bp"])
    if not water_cls:
        return
    ocean = None
    for act in all_actors():
        if act.get_class().get_name() == "BP_Water_C":
            ocean = act
            break
    if not ocean:
        ocean = actor_sub().spawn_actor_from_class(water_cls, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
    ocean.set_actor_location(unreal.Vector(0, 0, -200.0), False, False)
    ocean.set_actor_scale3d(unreal.Vector(200, 200, 1))


def configure_landscape(landscape):
    mat = load_asset(ASSETS["landscape_mat"])
    if mat:
        landscape.set_editor_property("landscape_material", mat)
    loc = landscape.get_actor_location()
    if loc.z < 50:
        landscape.set_actor_location(unreal.Vector(loc.x, loc.y, 100.0), False, False)
    try:
        landscape.set_grass_enabled(True)
    except Exception:
        pass
    try:
        log(f"Landscape layers: {landscape.get_target_layer_names()}")
    except Exception:
        pass


def add_grass_streaming():
    if unreal.EditorAssetLibrary.does_asset_exist(GRASS_STREAMING):
        try:
            unreal.EditorLevelLibrary.add_level_streaming(GRASS_STREAMING)
            log("Added StreamingLevel_Demo_Grass")
        except Exception as exc:
            log(f"Grass streaming note: {exc}")


def estimate_z(x, y, base_z=100.0):
    """Rough height from island heightmap layout (south low, north plateau)."""
    dy = y - ISLAND_CENTER.y
    dx = x - ISLAND_CENTER.x
    dist = math.sqrt(dx * dx + dy * dy)
    if dist > ISLAND_COAST_RADIUS * 1.1:
        return base_z + 80.0
    if dy < -4000:
        return base_z + 400.0
    if dy > 5000 and abs(dx) < 6000:
        return base_z + 4200.0
    t = max(0.0, min(1.0, (dy + 4000.0) / 12000.0))
    return base_z + 500.0 + t * 2500.0


def spawn_mesh(mesh_path, loc, rot, scale):
    mesh = load_asset(mesh_path)
    if not mesh:
        return
    act = actor_sub().spawn_actor_from_class(unreal.StaticMeshActor, loc, rot)
    comp = act.get_component_by_class(unreal.StaticMeshComponent)
    comp.set_static_mesh(mesh)
    act.set_actor_scale3d(scale)


def place_island_props():
    """Coastal cliffs, beach rocks, valley trees — NOT a tight center ring."""
    cx, cy = ISLAND_CENTER.x, ISLAND_CENTER.y
    base_z = 100.0

    # Sea cliffs evenly around the island coast
    for i in range(14):
        angle = (i / 14.0) * math.pi * 2.0
        r = ISLAND_COAST_RADIUS + 800.0
        x = cx + math.cos(angle) * r
        y = cy + math.sin(angle) * r
        z = estimate_z(x, y, base_z)
        mesh = CLIFF_MESHES[i % len(CLIFF_MESHES)]
        yaw = math.degrees(angle) + 90.0
        scale = 4.5 + (i % 3) * 0.8
        spawn_mesh(
            mesh,
            unreal.Vector(x, y, z - 350.0),
            unreal.Rotator(0, yaw, 0),
            unreal.Vector(scale, scale, scale * 1.6),
        )

    # South beach boulders
    beach_spots = [
        (-6000, -11000), (-2000, -12000), (3000, -10500), (7000, -9000),
    ]
    for i, (bx, by) in enumerate(beach_spots):
        z = estimate_z(bx, by, base_z)
        spawn_mesh(
            ROCK_MESHES[i % len(ROCK_MESHES)],
            unreal.Vector(bx, by, z - 60.0),
            unreal.Rotator(0, i * 40.0, 0),
            unreal.Vector(2.0, 2.0, 2.0),
        )

    # North plateau tree grove
    tree_spots = [
        (-1500, 8000), (1200, 8500), (0, 9500), (-2500, 7200), (2800, 7600), (800, 7000),
    ]
    for i, (tx, ty) in enumerate(tree_spots):
        z = estimate_z(tx, ty, base_z)
        spawn_mesh(
            TREE_MESHES[i % len(TREE_MESHES)],
            unreal.Vector(tx, ty, z - 30.0),
            unreal.Rotator(0, i * 55.0, 0),
            unreal.Vector(1.2, 1.2, 1.2),
        )

    # Valley trail bushes
    bush_spots = [
        (-4000, -2000), (-1000, 500), (2000, 1500), (-3000, 3000), (4500, 2000),
    ]
    for i, (ux, uy) in enumerate(bush_spots):
        z = estimate_z(ux, uy, base_z)
        spawn_mesh(
            BUSH_MESHES[i % len(BUSH_MESHES)],
            unreal.Vector(ux, uy, z - 10.0),
            unreal.Rotator(0, i * 70.0, 0),
            unreal.Vector(1.0, 1.0, 1.0),
        )

    log("Placed island props: 14 coast cliffs, 4 beach rocks, 6 trees, 5 bushes")


def ensure_player_start():
    # South beach entry
    px, py = -3000.0, -9000.0
    pz = estimate_z(px, py, 100.0) + 200.0
    for act in all_actors():
        if isinstance(act, unreal.PlayerStart):
            act.set_actor_location(unreal.Vector(px, py, pz), False, False)
            act.set_actor_rotation(unreal.Rotator(0, 35, 0), False)
            log(f"PlayerStart -> south beach ({px:.0f}, {py:.0f}, {pz:.0f})")
            return
    actor_sub().spawn_actor_from_class(
        unreal.PlayerStart,
        unreal.Vector(px, py, pz),
        unreal.Rotator(0, 35, 0),
    )
    log(f"Spawned PlayerStart at south beach ({px:.0f}, {py:.0f}, {pz:.0f})")


def reset_and_setup():
    if not unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH):
        log(f"ERROR: {MAP_PATH} not found")
        return

    log("=== Resetting Height map ===")
    load_map()
    clear_mess()

    landscape = find_landscape()
    if not landscape:
        log("ERROR: No Landscape. Import Island_Heightmap_1009.r16 first.")
        return

    ensure_sky()
    ensure_atmosphere()
    ensure_single_sun()
    ensure_skylight()
    ensure_rvt()
    ensure_ocean()
    configure_landscape(landscape)
    add_grass_streaming()
    place_island_props()
    ensure_player_start()

    save()
    log("SUCCESS: Height map reset and configured.")


if __name__ == "__main__":
    reset_and_setup()
