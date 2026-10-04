"""
Full island pass for Height_DemoCopy (v6):
- v3 heightmap (mountains, lake basin, satellites, smoothed)
- Demo landscape material + RVT + grass streaming (fixes terrain line look)
- Purge bad trees / platforms; forest clusters with upright SoStylized oaks/pines
- 3 satellite rock islets as meshes if height alone is subtle
- One NE pointed cliff

CLOSE EDITOR FIRST. Needs -AllowCommandletRendering.
"""
import math
import os
import random
import struct
import unreal

MAP = "/Game/SpellCraft/Maps/Height_DemoCopy"
DEMO = "/Game/SoStylized/Maps/CompleteVol1/Demonstration"
GRASS_STREAM = "/Game/SoStylized/Maps/CompleteVol1/StreamingLevel_Demo_Grass"
PNG_RG = "F:/DEVELOPMENT/Games/SpellCraft/Content/SpellCraft/Textures/Island_Heightmap_1009_RG.png"
R16 = "F:/DEVELOPMENT/Games/SpellCraft/Content/SpellCraft/Textures/Island_Heightmap_1009.r16"
SIZE = 1009
SEA = 32768
RESULT = "F:/DEVELOPMENT/Games/SpellCraft/Saved/Logs/remodel_island_v6.txt"
OUT = []

ASSETS = {
    "landscape_mat": "/Game/SoStylized/Environment/Landscape/Materials/MI_Landscape.MI_Landscape",
    "rvt_landscape": "/Game/SoStylized/Environment/Landscape/Textures/RVT_Landscape.RVT_Landscape",
    "rvt_height": "/Game/SoStylized/Environment/Landscape/Textures/RVT_LandscapeHeight.RVT_LandscapeHeight",
}

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
    "/Game/SoStylized/Environment/Foliage/SM_Fern1.SM_Fern1",
]

CLIFF_MESHES = [
    "/Game/SoStylized/Environment/Rocks/Classic/SM_CliffClassic1.SM_CliffClassic1",
    "/Game/SoStylized/Environment/Rocks/Classic/SM_CliffClassic2.SM_CliffClassic2",
    "/Game/SoStylized/Environment/Rocks/Classic/SM_CliffClassic3.SM_CliffClassic3",
]

ROCK_MESHES = [
    "/Game/SoStylized/Environment/Rocks/Classic/SM_BoulderClassic1.SM_BoulderClassic1",
    "/Game/SoStylized/Environment/Rocks/Classic/SM_RockClumpClassic2.SM_RockClumpClassic2",
]

# Forest biomes in normalized island space (nx, ny)
FOREST_ZONES = [
    ("NW_highland", -0.45, 0.35, 0.28, 120),  # cx, cy, radius, count
    ("Central_west", -0.15, 0.05, 0.22, 80),
    ("North_mid", 0.05, 0.40, 0.20, 70),
    ("East_foothills", 0.30, 0.10, 0.18, 50),
]

SATellite_MESH_SPOTS = [
    (-0.82, 0.55, 1.8),
    (0.90, -0.15, 1.5),
    (-0.25, -0.86, 1.3),
]

HEIGHT_CACHE = None


def log(msg):
    OUT.append(str(msg))
    unreal.log(msg)


def load_mesh(path):
    return unreal.EditorAssetLibrary.load_asset(path)


def landscape_z(landscape):
    o, e = landscape.get_actor_bounds(False, False)
    return o.z - e.z, o.z + e.z


def load_heights():
    global HEIGHT_CACHE
    if HEIGHT_CACHE is None:
        with open(R16, "rb") as f:
            HEIGHT_CACHE = struct.unpack(f"<{SIZE * SIZE}H", f.read())
    return HEIGHT_CACHE


def height_at(x, y, lo, le, actor_z=0.0):
    u = (x - (lo.x - le.x)) / max(1.0, 2.0 * le.x)
    v = (y - (lo.y - le.y)) / max(1.0, 2.0 * le.y)
    ix = int(max(0, min(SIZE - 1, u * (SIZE - 1))))
    iy = int(max(0, min(SIZE - 1, v * (SIZE - 1))))
    h = load_heights()[iy * SIZE + ix]
    return actor_z + (h - SEA) * 100.0 / 128.0


def apply_height(world, landscape):
    tex = unreal.RenderingLibrary.import_file_as_texture2d(world, PNG_RG)
    if not tex:
        return False
    try:
        tex.set_editor_property("srgb", False)
    except Exception:
        pass
    rt = unreal.RenderingLibrary.create_render_target2d(
        world, SIZE, SIZE, unreal.TextureRenderTargetFormat.RTF_RGBA8
    )
    canvas, _, ctx = unreal.RenderingLibrary.begin_draw_canvas_to_render_target(world, rt)
    canvas.draw_texture(
        tex, unreal.Vector2D(0, 0), unreal.Vector2D(SIZE, SIZE),
        unreal.Vector2D(0, 0), unreal.Vector2D(1, 1),
        unreal.LinearColor(1, 1, 1, 1), unreal.BlendMode.BLEND_OPAQUE,
    )
    unreal.RenderingLibrary.end_draw_canvas_to_render_target(world, ctx)
    ok = landscape.landscape_import_heightmap_from_render_target(rt, True, 0)
    try:
        landscape.force_layers_full_update()
    except Exception:
        pass
    log(f"height import -> {ok}")
    return ok


def setup_demo_landscape(landscape):
    mat = load_mesh(ASSETS["landscape_mat"])
    if mat:
        landscape.set_editor_property("landscape_material", mat)
        log("Set MI_Landscape material")
    try:
        landscape.set_grass_enabled(True)
    except Exception:
        pass


def ensure_rvt_volumes(sub):
    """RVT volumes drive SoStylized landscape blending — missing = visible grid lines."""
    existing = sum(
        1 for a in sub.get_all_level_actors() if isinstance(a, unreal.RuntimeVirtualTextureVolume)
    )
    if existing >= 2:
        log(f"RVT volumes already present ({existing})")
        return
    specs = [
        (ASSETS["rvt_landscape"], unreal.Vector(-50400, -50400, -4320), unreal.Vector(100800, 100908, 25468)),
        (ASSETS["rvt_height"], unreal.Vector(-50400, -50400, -4320), unreal.Vector(100800, 100800, 25468)),
    ]
    for path, loc, scale in specs:
        rvt = load_mesh(path)
        if not rvt:
            continue
        vol = sub.spawn_actor_from_class(unreal.RuntimeVirtualTextureVolume, loc)
        vol.set_actor_scale3d(scale)
        try:
            comp = vol.get_component_by_class(unreal.RuntimeVirtualTextureComponent)
            if comp:
                comp.set_editor_property("virtual_texture", rvt)
        except Exception:
            pass
        log(f"Spawned RVT volume for {path}")


def add_grass_streaming():
    if not unreal.EditorAssetLibrary.does_asset_exist(GRASS_STREAM):
        log(f"Grass stream missing: {GRASS_STREAM}")
        return
    try:
        unreal.EditorLevelLibrary.add_level_streaming(GRASS_STREAM)
        log("Added StreamingLevel_Demo_Grass")
    except Exception as e:
        log(f"grass stream: {e}")


def clear_old_props(sub):
    n = 0
    for act in list(sub.get_all_level_actors()):
        if not isinstance(act, unreal.StaticMeshActor):
            continue
        label = act.get_actor_label().lower()
        name = act.get_name().lower()
        if "islandtree" in label or "islandtree" in name:
            sub.destroy_actor(act)
            n += 1
            continue
        key = label + name
        if any(h in key for h in (
            "cliff", "shelf", "platform", "stack", "pillar", "island", "rock", "boulder", "mesa"
        )):
            if "islandpointed" not in label and "satellite" not in label:
                sub.destroy_actor(act)
                n += 1
    log(f"Cleared {n} old props/trees")


def spawn_mesh(sub, mesh_path, loc, yaw, uniform_scale):
    mesh = load_mesh(mesh_path)
    if not mesh:
        return None
    act = sub.spawn_actor_from_class(unreal.StaticMeshActor, loc)
    smc = act.get_component_by_class(unreal.StaticMeshComponent)
    smc.set_static_mesh(mesh)
    act.set_actor_rotation(unreal.Rotator(0.0, float(yaw), 0.0), False)
    act.set_actor_scale3d(unreal.Vector(uniform_scale, uniform_scale, uniform_scale))
    return act


def plant_forests(sub, landscape, rng):
    lo, le = landscape.get_actor_bounds(False, False)
    trees = [m for m in (load_mesh(p) for p in TREE_MESHES) if m]
    bushes = [m for m in (load_mesh(p) for p in BUSH_MESHES) if m]
    if not trees:
        log("No tree meshes")
        return
    placed = 0
    for _zone, cx, cy, rad, count in FOREST_ZONES:
        for _ in range(count):
            ang = rng.uniform(0, math.pi * 2)
            r = rng.uniform(0, rad)
            nx = cx + math.cos(ang) * r
            ny = cy + math.sin(ang) * r
            if nx > 0.38 and ny > 0.38:
                continue  # skip NE peak
            if nx < -0.22 and ny < -0.22:
                continue  # SW beach
            x = lo.x + nx * le.x
            y = lo.y + ny * le.y
            z = height_at(x, y, lo, le)
            if z < 350:
                continue
            mesh = trees[rng.randint(0, len(trees) - 1)]
            s = rng.uniform(1.2, 2.4)
            act = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z - 15))
            smc = act.get_component_by_class(unreal.StaticMeshComponent)
            smc.set_static_mesh(mesh)
            act.set_actor_rotation(unreal.Rotator(0.0, rng.uniform(0, 360), 0.0), False)
            act.set_actor_scale3d(unreal.Vector(s, s, s))
            act.set_actor_label(f"ForestTree_{placed}")
            placed += 1
            if bushes and rng.random() < 0.35:
                bm = bushes[rng.randint(0, len(bushes) - 1)]
                bs = rng.uniform(0.8, 1.3)
                bact = sub.spawn_actor_from_class(
                    unreal.StaticMeshActor,
                    unreal.Vector(x + rng.uniform(-120, 120), y + rng.uniform(-120, 120), z),
                )
                bsmc = bact.get_component_by_class(unreal.StaticMeshComponent)
                bsmc.set_static_mesh(bm)
                bact.set_actor_rotation(unreal.Rotator(0.0, rng.uniform(0, 360), 0.0), False)
                bact.set_actor_scale3d(unreal.Vector(bs, bs, bs))
    log(f"Planted {placed} forest trees (+ bushes)")


def place_satellite_rocks(sub, landscape, rng):
    lo, le = landscape.get_actor_bounds(False, False)
    cliffs = [m for m in (load_mesh(p) for p in CLIFF_MESHES) if m]
    rocks = [m for m in (load_mesh(p) for p in ROCK_MESHES) if m]
    for i, (nx, ny, sc) in enumerate(SATellite_MESH_SPOTS):
        x = lo.x + nx * le.x
        y = lo.y + ny * le.y
        z = height_at(x, y, lo, le)
        mesh_list = cliffs if cliffs else rocks
        if not mesh_list:
            break
        m = mesh_list[i % len(mesh_list)]
        act = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z - 80))
        smc = act.get_component_by_class(unreal.StaticMeshComponent)
        smc.set_static_mesh(m)
        act.set_actor_rotation(unreal.Rotator(rng.uniform(-5, 5), rng.uniform(0, 360), 0.0), False)
        act.set_actor_scale3d(unreal.Vector(sc, sc, sc * 1.1))
        act.set_actor_label(f"SatelliteIsle_{i}")
        for j in range(4):
            rx = x + rng.uniform(-400, 400)
            ry = y + rng.uniform(-400, 400)
            rz = height_at(rx, ry, lo, le)
            if rocks:
                rm = rocks[rng.randint(0, len(rocks) - 1)]
                rs = rng.uniform(0.6, 1.2)
                ract = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(rx, ry, rz - 20))
                rsmc = ract.get_component_by_class(unreal.StaticMeshComponent)
                rsmc.set_static_mesh(rm)
                ract.set_actor_rotation(unreal.Rotator(0, rng.uniform(0, 360), 0), False)
                ract.set_actor_scale3d(unreal.Vector(rs, rs, rs))
    log("Placed satellite islet rock clusters")


def place_ne_cliff(sub, landscape):
    lo, le = landscape.get_actor_bounds(False, False)
    x = lo.x + le.x * 0.62
    y = lo.y + le.y * 0.62
    z = height_at(x, y, lo, le)
    cliff = load_mesh(CLIFF_MESHES[1]) or load_mesh(CLIFF_MESHES[0])
    if cliff:
        act = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z - 100))
        smc = act.get_component_by_class(unreal.StaticMeshComponent)
        smc.set_static_mesh(cliff)
        act.set_actor_rotation(unreal.Rotator(-10, 40, 0), False)
        act.set_actor_scale3d(unreal.Vector(2.5, 2.5, 3.0))
        act.set_actor_label("IslandPointedCliff_NE")


def fix_water(sub):
    waters = [a for a in sub.get_all_level_actors() if "Water" in a.get_class().get_name()]
    waters.sort(key=lambda a: a.get_actor_location().z)
    for i, w in enumerate(waters):
        if i == 0:
            w.set_actor_location(unreal.Vector(0, 0, 0), False, False)
            log("Ocean Z=0")
        else:
            sub.destroy_actor(w)


def main():
    if not os.path.isfile(PNG_RG):
        log("Run create_island_heightmap_v3.py first")
        return

    rng = random.Random(42)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    landscape = next(a for a in sub.get_all_level_actors() if isinstance(a, unreal.Landscape))

    apply_height(world, landscape)
    landscape.set_actor_location(unreal.Vector(0, 0, 0), False, False)
    setup_demo_landscape(landscape)
    ensure_rvt_volumes(sub)
    add_grass_streaming()

    clear_old_props(sub)
    plant_forests(sub, landscape, rng)
    place_satellite_rocks(sub, landscape, rng)
    place_ne_cliff(sub, landscape)
    fix_water(sub)

    for act in sub.get_all_level_actors():
        if isinstance(act, unreal.PlayerStart):
            act.set_actor_location(unreal.Vector(-18000, -20000, 700), False, False)
            act.set_actor_rotation(unreal.Rotator(0, 45, 0), False)

    z0, z1 = landscape_z(landscape)
    sma = sum(1 for a in sub.get_all_level_actors() if isinstance(a, unreal.StaticMeshActor))
    log(f"FINAL surface Z {z0:.0f}..{z1:.0f}  SMA={sma}")

    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    try:
        unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    except Exception:
        pass
    log("SAVED v6 — reopen Height_DemoCopy, reload from disk.")
    with open(RESULT, "w", encoding="utf-8") as f:
        f.write("\n".join(OUT))


if __name__ == "__main__":
    main()
