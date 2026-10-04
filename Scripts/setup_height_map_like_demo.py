"""
Set up /Game/SpellCraft/Maps/Height to visually match SoStylized Demonstration.

Run with the editor CLOSED:
  T:\\Program Files\\UE_5.8\\Engine\\Binaries\\Win64\\UnrealEditor-Cmd.exe ^
    F:\\DEVELOPMENT\\Games\\SpellCraft\\SpellCraft.uproject ^
    -run=pythonscript ^
    -script="F:\\DEVELOPMENT\\Games\\SpellCraft\\Scripts\\setup_height_map_like_demo.py"

Or in-editor: Tools -> Execute Python Script
"""
import math
import random
import unreal

MAP_PATH = "/Game/SpellCraft/Maps/Height"
GRASS_STREAMING = "/Game/SoStylized/Maps/CompleteVol1/StreamingLevel_Demo_Grass"

# SoStylized asset paths (same pack as Demonstration)
ASSETS = {
    "landscape_mat": "/Game/SoStylized/Environment/Landscape/Materials/MI_Landscape.MI_Landscape",
    "rvt_landscape": "/Game/SoStylized/Environment/Landscape/Textures/RVT_Landscape.RVT_Landscape",
    "rvt_height": "/Game/SoStylized/Environment/Landscape/Textures/RVT_LandscapeHeight.RVT_LandscapeHeight",
    "sky_bp": "/Game/SoStylized/Environment/Sky/BP_StylizedSky_Lite.BP_StylizedSky_Lite_C",
    "water_bp": "/Game/SoStylized/Environment/Water/BP_Water.BP_Water_C",
    "layer_grass": "/Game/SoStylized/Environment/Landscape/LL_Grass.LL_Grass",
    "layer_rock": "/Game/SoStylized/Environment/Landscape/LL_Rock.LL_Rock",
    "layer_sand": "/Game/SoStylized/Environment/Landscape/LL_Sand.LL_Sand",
    "layer_dirt": "/Game/SoStylized/Environment/Landscape/LL_Dirt.LL_Dirt",
    "grass_type": "/Game/SoStylized/Environment/Landscape/LG_Grass.LG_Grass",
}

ROCK_MESHES = [
    "/Game/SoStylized/Environment/Rocks/Classic/SM_RockClassic1.SM_RockClassic1",
    "/Game/SoStylized/Environment/Rocks/Classic/SM_RockClassic3.SM_RockClassic3",
    "/Game/SoStylized/Environment/Rocks/Classic/SM_RockClassic5.SM_RockClassic5",
    "/Game/SoStylized/Environment/Rocks/Classic/SM_RockClassic8.SM_RockClassic8",
    "/Game/SoStylized/Environment/Rocks/Classic/SM_RockClumpClassic1.SM_RockClumpClassic1",
    "/Game/SoStylized/Environment/Rocks/Classic/SM_RockClumpClassic3.SM_RockClumpClassic3",
    "/Game/SoStylized/Environment/Rocks/Classic/SM_BoulderClassic1.SM_BoulderClassic1",
    "/Game/SoStylized/Environment/Rocks/Classic/SM_BoulderClassic2.SM_BoulderClassic2",
    "/Game/SoStylized/Environment/Rocks/Classic/SM_BoulderClumpClassic1.SM_BoulderClumpClassic1",
]

CLIFF_MESHES = [
    "/Game/SoStylized/Environment/Rocks/Classic/SM_CliffClassic1.SM_CliffClassic1",
    "/Game/SoStylized/Environment/Rocks/Classic/SM_CliffClassic2.SM_CliffClassic2",
    "/Game/SoStylized/Environment/Rocks/Classic/SM_CliffClassic3.SM_CliffClassic3",
    "/Game/SoStylized/Environment/Rocks/Classic/SM_CliffClassic4.SM_CliffClassic4",
]

TREE_MESHES = [
    "/Game/SoStylized/Environment/Trees/Oak/SM_OakTree1.SM_OakTree1",
    "/Game/SoStylized/Environment/Trees/Oak/SM_OakTree2.SM_OakTree2",
    "/Game/SoStylized/Environment/Trees/Oak/SM_OakTree3.SM_OakTree3",
    "/Game/SoStylized/Environment/Trees/Oak/SM_OakTreeLarge1.SM_OakTreeLarge1",
    "/Game/SoStylized/Environment/Trees/Pine/SM_Pine01.SM_Pine01",
    "/Game/SoStylized/Environment/Trees/Pine/SM_Pine02.SM_Pine02",
]

BUSH_MESHES = [
    "/Game/SoStylized/Environment/Foliage/SM_Bush1.SM_Bush1",
    "/Game/SoStylized/Environment/Foliage/SM_Bush2.SM_Bush2",
    "/Game/SoStylized/Environment/Foliage/SM_Bush3.SM_Bush3",
    "/Game/SoStylized/Environment/Foliage/SM_Fern1.SM_Fern1",
    "/Game/SoStylized/Environment/Foliage/SM_Fern2.SM_Fern2",
]

# Matches Demonstration RVT placement over the landscape
RVT_SPECS = [
    {
        "loc": unreal.Vector(-50400.0, -50400.0, -4320.3125),
        "scale": unreal.Vector(100800.0, 100908.0, 25468.75),
        "rvt_key": "rvt_landscape",
    },
    {
        "loc": unreal.Vector(-50400.0, -50400.0, -4320.3125),
        "scale": unreal.Vector(100800.0, 100800.0, 25468.75),
        "rvt_key": "rvt_height",
    },
]


def log(msg):
    unreal.log(msg)
    print(msg)


def load_asset(path):
    obj = unreal.EditorAssetLibrary.load_asset(path)
    if not obj:
        log(f"WARNING: Could not load {path}")
    return obj


def load_mesh(path):
    return load_asset(path)


def get_actor_subsystem():
    return unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


def load_map(map_path):
    level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    level_sub.load_level(map_path)


def get_all_actors():
    return get_actor_subsystem().get_all_level_actors()


def find_landscape(actors):
    for act in actors:
        if isinstance(act, unreal.Landscape):
            return act
    return None


def actor_exists(actors, cls):
    for act in actors:
        if isinstance(act, cls):
            return True
    return False


def actor_class_exists(actors, class_name):
    for act in actors:
        if act.get_class().get_name() == class_name:
            return True
    return False


def estimate_landscape_z(landscape, x, y, center_x, center_y, island_radius, fallback_z=500.0):
    """Height estimate from island heightmap layout (no line trace — null RHI has no collision)."""
    dx = x - center_x
    dy = y - center_y
    dist = math.sqrt(dx * dx + dy * dy)
    if dist > island_radius * 1.05:
        return landscape.get_actor_location().z + 50.0

    base = landscape.get_actor_location().z
    # South beach (low Y relative to center)
    if dy < -island_radius * 0.15:
        return base + 350.0 + (dist / island_radius) * 120.0
    # North plateau (high Y)
    if dy > island_radius * 0.2 and abs(dx) < island_radius * 0.35:
        return base + 4200.0 - abs(dx) * 3.0
    # Mid valley ascent
    t = max(0.0, min(1.0, (dy + island_radius * 0.15) / (island_radius * 0.55)))
    ridge = abs(math.cos(dx / island_radius * 4.0)) * 350.0
    return base + 600.0 + t * 2800.0 + ridge


def ensure_sky_and_lighting(actors, actor_sub):
    if not actor_class_exists(actors, "BP_StylizedSky_Lite_C"):
        sky_cls = unreal.load_class(None, ASSETS["sky_bp"])
        if sky_cls:
            actor_sub.spawn_actor_from_class(sky_cls, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
            log("Spawned BP_StylizedSky_Lite")

    if not actor_exists(actors, unreal.SkyAtmosphere):
        actor_sub.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
        log("Spawned SkyAtmosphere")

    sun = None
    for act in actors:
        if isinstance(act, unreal.DirectionalLight):
            sun = act
            break
    if not sun:
        sun = actor_sub.spawn_actor_from_class(
            unreal.DirectionalLight,
            unreal.Vector(0, 0, 15000),
            unreal.Rotator(-42, -45, 0),
        )
        log("Spawned DirectionalLight")
    sun_comp = sun.get_component_by_class(unreal.DirectionalLightComponent)
    if sun_comp:
        sun_comp.set_editor_property("intensity", 7.5)
        sun_comp.set_editor_property("atmosphere_sun_light", True)
        sun_comp.set_editor_property("light_color", unreal.Color(255, 248, 235, 255))

    skylight = None
    for act in actors:
        if isinstance(act, unreal.SkyLight):
            skylight = act
            break
    if not skylight:
        skylight = actor_sub.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 2000), unreal.Rotator(0, 0, 0))
        log("Spawned SkyLight")
    sl_comp = skylight.get_component_by_class(unreal.SkyLightComponent)
    if sl_comp:
        sl_comp.set_editor_property("real_time_capture", True)

    if not actor_exists(actors, unreal.ExponentialHeightFog):
        fog = actor_sub.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
        fog_comp = fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
        if fog_comp:
            fog_comp.set_editor_property("fog_density", 0.0015)
            fog_comp.set_editor_property(
                "fog_inscattering_luminance",
                unreal.LinearColor(0.55, 0.78, 1.0, 1.0),
            )
        log("Spawned ExponentialHeightFog")


def ensure_rvt_volumes(actors, actor_sub):
    existing = sum(1 for a in actors if isinstance(a, unreal.RuntimeVirtualTextureVolume))
    if existing >= 2:
        log(f"RVT volumes already present ({existing})")
        return

    for spec in RVT_SPECS:
        rvt_asset = load_asset(ASSETS[spec["rvt_key"]])
        vol = actor_sub.spawn_actor_from_class(
            unreal.RuntimeVirtualTextureVolume,
            spec["loc"],
            unreal.Rotator(0, 0, 0),
        )
        vol.set_actor_scale3d(spec["scale"])
        comp = None
        for cls_name in ("RuntimeVirtualTextureComponent", "RuntimeVirtualTextureVolumeComponent"):
            cls = getattr(unreal, cls_name, None)
            if cls:
                comp = vol.get_component_by_class(cls)
                if comp:
                    break
        if comp and rvt_asset:
            try:
                comp.set_editor_property("virtual_texture", rvt_asset)
            except Exception as exc:
                log(f"RVT assign note: {exc}")
        log(f"Spawned RVT volume ({spec['rvt_key']})")


def ensure_ocean(actors, actor_sub):
    water_cls = unreal.load_class(None, ASSETS["water_bp"])
    if not water_cls:
        return

    main_ocean = None
    for act in actors:
        if act.get_class().get_name() == "BP_Water_C":
            loc = act.get_actor_location()
            if abs(loc.x) < 5000 and abs(loc.y) < 5000:
                main_ocean = act
                break

    if not main_ocean:
        main_ocean = actor_sub.spawn_actor_from_class(water_cls, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
        log("Spawned main BP_Water ocean")

    main_ocean.set_actor_location(unreal.Vector(0, 0, 0), False, False)
    main_ocean.set_actor_scale3d(unreal.Vector(200, 200, 1))


def configure_landscape(landscape):
    land_mat = load_asset(ASSETS["landscape_mat"])
    if land_mat:
        landscape.set_editor_property("landscape_material", land_mat)

    loc = landscape.get_actor_location()
    if loc.z < 50:
        landscape.set_actor_location(unreal.Vector(loc.x, loc.y, 100.0), False, False)
        log("Raised landscape to Z=100 (Demonstration match)")

    try:
        landscape.set_grass_enabled(True)
    except Exception as exc:
        log(f"Could not enable grass: {exc}")

    for layer_key in ("layer_grass", "layer_rock", "layer_sand", "layer_dirt"):
        layer = load_asset(ASSETS[layer_key])
        if layer:
            log(f"Layer asset ready: {layer_key}")

    try:
        layers = landscape.get_target_layer_names()
        log(f"Landscape target layers: {layers}")
    except Exception as exc:
        log(f"Target layer query: {exc}")


def add_grass_streaming_level():
    if not unreal.EditorAssetLibrary.does_asset_exist(GRASS_STREAMING):
        log(f"WARNING: Grass streaming level missing: {GRASS_STREAMING}")
        return

    try:
        unreal.EditorLevelLibrary.add_level_streaming(GRASS_STREAMING)
        log(f"Added streaming level: {GRASS_STREAMING}")
    except Exception as exc:
        log(f"Streaming level add skipped ({exc}) - add manually if grass is sparse")


def spawn_mesh_actor(actor_sub, mesh_path, location, rotation, scale):
    mesh = load_mesh(mesh_path)
    if not mesh:
        return None
    act = actor_sub.spawn_actor_from_class(unreal.StaticMeshActor, location, rotation)
    comp = act.get_component_by_class(unreal.StaticMeshComponent)
    comp.set_static_mesh(mesh)
    act.set_actor_scale3d(scale)
    return act


def scatter_props(actor_sub, landscape, rng):
    existing_meshes = sum(
        1 for a in get_all_actors() if isinstance(a, unreal.StaticMeshActor)
    )
    if existing_meshes > 100:
        log(f"Skipping prop scatter — already {existing_meshes} StaticMeshActors in level")
        return {"rocks": 0, "cliffs": 0, "trees": 0, "bushes": 0, "skipped": True}

    origin = landscape.get_actor_location()
    # Landscape spans roughly origin -> origin + (100800, 100800) based on demo RVT
    min_x, min_y = origin.x, origin.y
    max_x, max_y = origin.x + 100800.0, origin.y + 100800.0
    center_x = (min_x + max_x) * 0.5
    center_y = (min_y + max_y) * 0.5
    island_radius = 28000.0

    spawned = {"rocks": 0, "cliffs": 0, "trees": 0, "bushes": 0}

    # Coastline cliffs - ring outside inner island
    for i in range(24):
        angle = (i / 24.0) * math.pi * 2.0
        radius = island_radius + rng.uniform(2000, 8000)
        x = center_x + math.cos(angle) * radius
        y = center_y + math.sin(angle) * radius
        z = estimate_landscape_z(landscape, x, y, center_x, center_y, island_radius, 300.0)
        mesh = CLIFF_MESHES[i % len(CLIFF_MESHES)]
        yaw = math.degrees(angle) + 90.0
        scale = rng.uniform(2.5, 5.5)
        spawn_mesh_actor(
            actor_sub,
            mesh,
            unreal.Vector(x, y, z - 200.0),
            unreal.Rotator(0, yaw + rng.uniform(-15, 15), 0),
            unreal.Vector(scale, scale, scale * rng.uniform(1.2, 2.0)),
        )
        spawned["cliffs"] += 1

    # Medium/small rocks on beaches and slopes
    for _ in range(80):
        angle = rng.uniform(0, math.pi * 2)
        radius = rng.uniform(island_radius * 0.55, island_radius * 1.05)
        x = center_x + math.cos(angle) * radius
        y = center_y + math.sin(angle) * radius
        z = estimate_landscape_z(landscape, x, y, center_x, center_y, island_radius, 200.0)
        mesh = ROCK_MESHES[rng.randint(0, len(ROCK_MESHES) - 1)]
        s = rng.uniform(0.8, 2.8)
        spawn_mesh_actor(
            actor_sub,
            mesh,
            unreal.Vector(x, y, z - 40.0),
            unreal.Rotator(rng.uniform(-8, 8), rng.uniform(0, 360), rng.uniform(-8, 8)),
            unreal.Vector(s, s, s),
        )
        spawned["rocks"] += 1

    # Trees on inner grassy areas
    for _ in range(55):
        angle = rng.uniform(0, math.pi * 2)
        radius = rng.uniform(island_radius * 0.1, island_radius * 0.75)
        x = center_x + math.cos(angle) * radius
        y = center_y + math.sin(angle) * radius
        z = estimate_landscape_z(landscape, x, y, center_x, center_y, island_radius, 400.0)
        mesh = TREE_MESHES[rng.randint(0, len(TREE_MESHES) - 1)]
        s = rng.uniform(0.9, 1.6)
        spawn_mesh_actor(
            actor_sub,
            mesh,
            unreal.Vector(x, y, z - 20.0),
            unreal.Rotator(0, rng.uniform(0, 360), 0),
            unreal.Vector(s, s, s),
        )
        spawned["trees"] += 1

    # Bushes/ferns scattered everywhere on land
    for _ in range(90):
        angle = rng.uniform(0, math.pi * 2)
        radius = rng.uniform(island_radius * 0.2, island_radius * 0.9)
        x = center_x + math.cos(angle) * radius
        y = center_y + math.sin(angle) * radius
        z = estimate_landscape_z(landscape, x, y, center_x, center_y, island_radius, 300.0)
        mesh = BUSH_MESHES[rng.randint(0, len(BUSH_MESHES) - 1)]
        s = rng.uniform(0.7, 1.4)
        spawn_mesh_actor(
            actor_sub,
            mesh,
            unreal.Vector(x, y, z - 10.0),
            unreal.Rotator(0, rng.uniform(0, 360), 0),
            unreal.Vector(s, s, s),
        )
        spawned["bushes"] += 1

    log(f"Scattered props: {spawned}")
    return spawned


def ensure_player_start(actor_sub, landscape, rng):
    origin = landscape.get_actor_location()
    center_x = origin.x + 50400.0
    center_y = origin.y + 50400.0
    # South beach of procedural island heightmap
    px = center_x + rng.uniform(-8000, 8000)
    py = center_y - 22000.0
    pz = estimate_landscape_z(landscape, px, py, center_x, center_y, 28000.0, 600.0)

    for act in get_all_actors():
        if isinstance(act, unreal.PlayerStart):
            act.set_actor_location(unreal.Vector(px, py, pz), False, False)
            act.set_actor_rotation(unreal.Rotator(0, 35, 0), False)
            log(f"Moved PlayerStart to south beach: ({px:.0f}, {py:.0f}, {pz:.0f})")
            return

    actor_sub.spawn_actor_from_class(
        unreal.PlayerStart,
        unreal.Vector(px, py, pz),
        unreal.Rotator(0, 35, 0),
    )
    log(f"Spawned PlayerStart at south beach: ({px:.0f}, {py:.0f}, {pz:.0f})")


def setup_height_map_like_demo():
    if not unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH):
        log(f"ERROR: Map not found: {MAP_PATH}")
        return

    log(f"Loading {MAP_PATH} ...")
    load_map(MAP_PATH)
    actor_sub = get_actor_subsystem()
    actors = get_all_actors()

    landscape = find_landscape(actors)
    if not landscape:
        log("ERROR: No Landscape in Height map. Import your heightmap first:")
        log("  Landscape mode -> Import from File -> Island_Heightmap_1009.r16")
        return

    ensure_sky_and_lighting(actors, actor_sub)
    ensure_rvt_volumes(get_all_actors(), actor_sub)
    ensure_ocean(get_all_actors(), actor_sub)
    configure_landscape(landscape)
    add_grass_streaming_level()

    rng = random.Random(42)
    scatter_props(actor_sub, landscape, rng)
    ensure_player_start(actor_sub, landscape, rng)

    unreal.EditorLevelLibrary.save_current_level()
    log("SUCCESS: Height map setup complete! Open Height.umap and press Play to test.")


if __name__ == "__main__":
    setup_height_map_like_demo()
