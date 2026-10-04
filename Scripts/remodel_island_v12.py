"""
Island remodel v12 — fix oaks, mountain height, textures, level satellites.

CRITICAL:
- Oaks are Y-up → pitch -90. NEVER use canopy-bounds "correction" (wide oaks
  look "flat" to that test and get flipped wrong).
- Pines are Z-up → pitch 0.
- Do NOT flood weightmaps to solid grass (that killed ground textures in v11).
  Restore Sand/Grass/Rock/Dirt from generated masks.
- Satellites: pitch 0, roll 0 (no inward tilt).
- Tree clusters like the denser image-3 layout.
- Moderate ScaleZ with capped heightmap peaks.
"""
import math
import os
import random
import struct
import unreal

MAP = "/Game/SpellCraft/Maps/Height_DemoCopy"
PNG_RG = "F:/DEVELOPMENT/Games/SpellCraft/Content/SpellCraft/Textures/Island_Heightmap_1009_RG.png"
R16 = "F:/DEVELOPMENT/Games/SpellCraft/Content/SpellCraft/Textures/Island_Heightmap_1009.r16"
WEIGHT_DIR = "F:/DEVELOPMENT/Games/SpellCraft/Content/SpellCraft/Textures"
SIZE = 1009
SEA = 32768
SCALE_Z = 155.0
RESULT = "F:/DEVELOPMENT/Games/SpellCraft/Saved/Logs/remodel_island_v12.txt"
OUT = []

ASSETS = {
    "landscape_mat": "/Game/SoStylized/Environment/Landscape/Materials/MI_Landscape.MI_Landscape",
    "rvt_landscape": "/Game/SoStylized/Environment/Landscape/Textures/RVT_Landscape.RVT_Landscape",
    "rvt_height": "/Game/SoStylized/Environment/Landscape/Textures/RVT_LandscapeHeight.RVT_LandscapeHeight",
}

OAK_PATHS = [
    "/Game/SoStylized/Environment/Trees/Oak/SM_OakTree1.SM_OakTree1",
    "/Game/SoStylized/Environment/Trees/Oak/SM_OakTree2.SM_OakTree2",
    "/Game/SoStylized/Environment/Trees/Oak/SM_OakTree3.SM_OakTree3",
    "/Game/SoStylized/Environment/Trees/Oak/SM_OakTree4.SM_OakTree4",
    "/Game/SoStylized/Environment/Trees/Oak/SM_OakTreeLarge1.SM_OakTreeLarge1",
]
PINE_PATHS = [
    "/Game/SoStylized/Environment/Trees/Pine/SM_Pine01.SM_Pine01",
    "/Game/SoStylized/Environment/Trees/Pine/SM_Pine02.SM_Pine02",
    "/Game/SoStylized/Environment/Trees/Pine/SM_Pine03.SM_Pine03",
]
CLIFF_PATHS = [
    "/Game/SoStylized/Environment/Rocks/Classic/SM_CliffClassic1.SM_CliffClassic1",
    "/Game/SoStylized/Environment/Rocks/Classic/SM_CliffClassic2.SM_CliffClassic2",
    "/Game/SoStylized/Environment/Rocks/Classic/SM_CliffClassic3.SM_CliffClassic3",
]
ROCK_PATHS = [
    "/Game/SoStylized/Environment/Rocks/Classic/SM_BoulderClassic1.SM_BoulderClassic1",
    "/Game/SoStylized/Environment/Rocks/Classic/SM_BoulderClassic2.SM_BoulderClassic2",
]
HOUSE_BPS = [
    "/Game/AdvancedVillagePack/Blueprints/BP_House_Var01",
    "/Game/AdvancedVillagePack/Blueprints/BP_House_Var02",
]
HOUSE_MESHES = [
    "/Game/AdvancedVillagePack/Meshes/SM_House_Var01.SM_House_Var01",
    "/Game/AdvancedVillagePack/Meshes/SM_House_Var02.SM_House_Var02",
]
WELL_BP = "/Game/AdvancedVillagePack/Blueprints/BP_Well"

LAKE_CX, LAKE_CY, LAKE_R = 0.05, -0.02, 0.12
VILLAGE_CX, VILLAGE_CY, VILLAGE_R = -0.02, -0.20, 0.13
CAVE_CX, CAVE_CY = 0.42, 0.38

# Dense clusters (image-3 style): west forest + foothill wrap. Paths = clearings only.
FOREST_ZONES = [
    # cx, cy, radius, density 0..1
    (-0.28, 0.05, 0.34, 0.98),   # main west/central forest
    (0.18, 0.22, 0.26, 0.95),    # foothill wrap toward mountain
    (-0.10, 0.32, 0.20, 0.88),   # north mid band
    (-0.42, 0.18, 0.18, 0.90),   # NW pack
]

PATHS = [
    [(-0.55, -0.55), (-0.30, -0.38), (-0.10, -0.26), (-0.02, -0.20)],
    [(-0.02, -0.20), (0.02, -0.08), (0.05, -0.02)],
    [(-0.02, -0.20), (0.15, 0.00), (0.30, 0.18), (0.42, 0.38)],
]
PATH_HALF_W = 0.065

SAT_SPOTS = [
    (-0.85, 0.52, 1.8),
    (0.92, -0.12, 1.7),
    (-0.22, -0.88, 1.6),
    (0.75, 0.55, 1.5),
]

HEIGHTS = None
OAK_PITCH = -90.0  # SoStylized oaks are sideways-authored
PINE_PITCH = 0.0


def log(msg):
    OUT.append(str(msg))
    unreal.log(msg)


def load(path):
    return unreal.EditorAssetLibrary.load_asset(path)


def heights():
    global HEIGHTS
    if HEIGHTS is None:
        with open(R16, "rb") as f:
            HEIGHTS = struct.unpack(f"<{SIZE * SIZE}H", f.read())
    return HEIGHTS


def land_xyz(landscape, ix, iy):
    loc = landscape.get_actor_location()
    sc = landscape.get_actor_scale3d()
    h = heights()[iy * SIZE + ix]
    return loc.x + ix * sc.x, loc.y + iy * sc.y, loc.z + (h - SEA) * sc.z / 128.0, h


def nxny(ix, iy):
    return ix / (SIZE - 1) * 2.0 - 1.0, iy / (SIZE - 1) * 2.0 - 1.0


def uv_xyz(landscape, nx, ny):
    ix = int(max(0, min(SIZE - 1, (nx + 1) * 0.5 * (SIZE - 1))))
    iy = int(max(0, min(SIZE - 1, (ny + 1) * 0.5 * (SIZE - 1))))
    return land_xyz(landscape, ix, iy)


def dist_seg(px, py, ax, ay, bx, by):
    abx, aby = bx - ax, by - ay
    t = ((px - ax) * abx + (py - ay) * aby) / max(1e-8, abx * abx + aby * aby)
    t = max(0.0, min(1.0, t))
    return math.hypot(px - (ax + t * abx), py - (ay + t * aby))


def on_path(nx, ny):
    for poly in PATHS:
        for i in range(len(poly) - 1):
            if dist_seg(nx, ny, poly[i][0], poly[i][1], poly[i + 1][0], poly[i + 1][1]) < PATH_HALF_W:
                return True
    return False


def in_forest_zone(nx, ny):
    best = 0.0
    for cx, cy, rad, dens in FOREST_ZONES:
        d = math.hypot(nx - cx, ny - cy)
        if d < rad:
            best = max(best, dens * (1.0 - d / rad))
    return best


def forest_ok(nx, ny, h):
    if h < SEA + 1000:
        return False
    if nx < -0.20 and ny < -0.22:
        return False  # beach
    if math.hypot(nx - LAKE_CX, ny - LAKE_CY) < LAKE_R + 0.03:
        return False
    if math.hypot(nx - VILLAGE_CX, ny - VILLAGE_CY) < VILLAGE_R:
        return False
    if on_path(nx, ny):
        return False
    if h > SEA + 8500:
        return False  # bare rock peak
    if abs(nx) > 0.72 or abs(ny) > 0.72:
        return False
    return in_forest_zone(nx, ny) > 0.08


def apply_height(world, landscape):
    tex = unreal.RenderingLibrary.import_file_as_texture2d(world, PNG_RG)
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


def restore_weightmaps(world, landscape):
    """Rebuild sand/grass/rock variation (undo v11 solid-grass wipe)."""
    for layer in ("Grass", "Sand", "Rock", "Dirt"):
        path = f"{WEIGHT_DIR}/Island_Weight_{layer}.png"
        if not os.path.isfile(path):
            log(f"missing weight mask {path}")
            continue
        tex = unreal.RenderingLibrary.import_file_as_texture2d(world, path)
        if not tex:
            log(f"failed import weight tex {layer}")
            continue
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
        try:
            ok = landscape.landscape_import_weightmap_from_render_target(rt, layer)
            log(f"restore weight {layer} -> {ok}")
        except Exception as e:
            log(f"restore weight {layer} err: {e}")
    try:
        landscape.force_layers_full_update()
    except Exception:
        pass


def clear_junk(sub):
    n = 0
    tags = (
        "ForestTree", "ForestBush", "IslandTree", "IslandPointed", "SatelliteIsle",
        "Village_", "PlayerHouse", "DesertCliff", "DesertRock", "CaveMouth",
        "SwCliff", "LakeWater",
    )
    kill_mesh = (
        "cliffclassic", "fallen", "shelf", "platform", "cubiccliff", "oakfallen",
        "boulderclassic", "boulderclump", "rockclump",
    )
    for act in list(sub.get_all_level_actors()):
        label = act.get_actor_label()
        if any(label.startswith(t) for t in tags):
            sub.destroy_actor(act)
            n += 1
            continue
        if isinstance(act, unreal.StaticMeshActor):
            try:
                mesh = act.static_mesh_component.static_mesh
                mn = mesh.get_name().lower() if mesh else ""
            except Exception:
                mn = ""
            if any(k in mn for k in kill_mesh):
                sub.destroy_actor(act)
                n += 1
                continue
            # Engine plane used as fake lake crater
            if mn == "plane" and "lake" in label.lower():
                sub.destroy_actor(act)
                n += 1
    log(f"Cleared {n}")


def ensure_rvt(sub):
    existing = [a for a in sub.get_all_level_actors() if isinstance(a, unreal.RuntimeVirtualTextureVolume)]
    if len(existing) >= 2:
        log(f"RVT ok ({len(existing)})")
        return
    for a in existing:
        sub.destroy_actor(a)
    for path, loc, scale in (
        (ASSETS["rvt_landscape"], unreal.Vector(-50400, -50400, -8000), unreal.Vector(100800, 100908, 35000)),
        (ASSETS["rvt_height"], unreal.Vector(-50400, -50400, -8000), unreal.Vector(100800, 100800, 35000)),
    ):
        rvt = load(path)
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
        log(f"RVT {path}")


def plant_tree(sub, mesh, x, y, z, yaw, is_oak, scale):
    act = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z - 20))
    smc = act.get_component_by_class(unreal.StaticMeshComponent)
    smc.set_static_mesh(mesh)
    smc.set_relative_rotation(unreal.Rotator(0, 0, 0), False, False)
    pitch = OAK_PITCH if is_oak else PINE_PITCH
    # World upright: pitch only for mesh authoring axis, yaw for variety, roll always 0
    act.set_actor_rotation(unreal.Rotator(pitch, float(yaw), 0.0), False)
    act.set_actor_scale3d(unreal.Vector(scale, scale, scale))
    return act


def plant_forest(sub, landscape, rng):
    oaks = [m for m in (load(p) for p in OAK_PATHS) if m]
    pines = [m for m in (load(p) for p in PINE_PATHS) if m]
    if not oaks and not pines:
        log("ERROR no trees")
        return
    log(f"Oaks={len(oaks)} Pines={len(pines)} oak_pitch={OAK_PITCH} pine_pitch={PINE_PITCH}")

    step = 5
    placed = 0
    oak_n = pine_n = 0
    max_trees = 12000
    for iy in range(4, SIZE - 4, step):
        for ix in range(4, SIZE - 4, step):
            if placed >= max_trees:
                break
            jx = max(1, min(SIZE - 2, ix + rng.randint(-2, 2)))
            jy = max(1, min(SIZE - 2, iy + rng.randint(-2, 2)))
            nx, ny = nxny(jx, jy)
            x, y, z, h = land_xyz(landscape, jx, jy)
            if not forest_ok(nx, ny, h):
                continue
            zone = in_forest_zone(nx, ny)
            if rng.random() > zone:
                continue
            # Highlands / foothills → pine; lowland clusters → oak
            use_pine = (h > SEA + 4500) or (nx > 0.05 and ny > 0.10 and rng.random() < 0.55)
            if use_pine and pines:
                mesh = pines[rng.randint(0, len(pines) - 1)]
                is_oak = False
                pine_n += 1
            elif oaks:
                mesh = oaks[rng.randint(0, len(oaks) - 1)]
                is_oak = True
                oak_n += 1
            else:
                mesh = pines[rng.randint(0, len(pines) - 1)]
                is_oak = False
                pine_n += 1
            s = rng.uniform(1.5, 2.4)
            act = plant_tree(sub, mesh, x, y, z, rng.uniform(0, 360), is_oak, s)
            act.set_actor_label(f"ForestTree_{placed}")
            placed += 1
        if placed >= max_trees:
            break
    log(f"Planted {placed} trees (oaks={oak_n} pines={pine_n})")


def spawn_bp(sub, path, loc, yaw=0.0, scale=1.0, label=""):
    cls = unreal.EditorAssetLibrary.load_blueprint_class(path)
    if not cls:
        try:
            cls = unreal.load_class(None, path + "_C")
        except Exception:
            cls = None
    if not cls:
        return None
    act = sub.spawn_actor_from_class(cls, loc)
    act.set_actor_rotation(unreal.Rotator(0, yaw, 0), False)
    if scale != 1.0:
        act.set_actor_scale3d(unreal.Vector(scale, scale, scale))
    if label:
        act.set_actor_label(label)
    return act


def spawn_mesh(sub, path, loc, yaw, pitch, scale, label):
    mesh = load(path)
    if not mesh:
        return None
    act = sub.spawn_actor_from_class(unreal.StaticMeshActor, loc)
    act.get_component_by_class(unreal.StaticMeshComponent).set_static_mesh(mesh)
    act.set_actor_rotation(unreal.Rotator(pitch, yaw, 0), False)
    if isinstance(scale, (int, float)):
        act.set_actor_scale3d(unreal.Vector(scale, scale, scale))
    else:
        act.set_actor_scale3d(unreal.Vector(*scale))
    act.set_actor_label(label)
    return act


def place_village(sub, landscape):
    cx, cy, cz, _ = uv_xyz(landscape, VILLAGE_CX, VILLAGE_CY)
    if not spawn_bp(sub, HOUSE_BPS[0], unreal.Vector(cx, cy + 280, cz), 180, 1.15, "PlayerHouse"):
        spawn_mesh(sub, HOUSE_MESHES[0], unreal.Vector(cx, cy + 280, cz), 180, 0, 1.15, "PlayerHouse")
    sc = landscape.get_actor_scale3d().x
    ix = int((VILLAGE_CX + 1) * 0.5 * (SIZE - 1))
    iy = int((VILLAGE_CY + 1) * 0.5 * (SIZE - 1))
    for i, (ox, oy, yaw) in enumerate([
        (-750, -80, 35), (800, -60, -40), (-480, -750, 95), (620, -700, -75),
        (-80, -1000, 10), (180, 120, 190), (-900, -480, 115), (950, -420, -100),
    ]):
        tx = max(1, min(SIZE - 2, ix + int(ox / sc)))
        ty = max(1, min(SIZE - 2, iy + int(oy / sc)))
        x, y, z, _ = land_xyz(landscape, tx, ty)
        if not spawn_bp(sub, HOUSE_BPS[i % 2], unreal.Vector(x, y, z), yaw, 1.0, f"Village_House_{i}"):
            spawn_mesh(sub, HOUSE_MESHES[i % 2], unreal.Vector(x, y, z), yaw, 0, 1.0, f"Village_House_{i}")
    spawn_bp(sub, WELL_BP, unreal.Vector(cx + 80, cy - 120, cz), label="Village_Well")
    log("Village placed")


def place_sw_cliff(sub, landscape):
    cliffs = [m for m in (load(p) for p in CLIFF_PATHS) if m]
    if not cliffs:
        return
    for i, (nx, ny, yaw, sc) in enumerate([
        (-0.58, -0.38, 140, (4.2, 3.2, 4.5)),
        (-0.52, -0.44, 155, (3.4, 2.8, 3.8)),
    ]):
        x, y, z, _ = uv_xyz(landscape, nx, ny)
        act = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z - 80))
        act.get_component_by_class(unreal.StaticMeshComponent).set_static_mesh(cliffs[i % len(cliffs)])
        # Level — no lean into map
        act.set_actor_rotation(unreal.Rotator(-8.0, yaw, 0.0), False)
        act.set_actor_scale3d(unreal.Vector(*sc))
        act.set_actor_label(f"SwCliff_{i}")
    log("SW cliff placed")


def place_satellites(sub, landscape, rng):
    """Level rock islets — pitch 0, roll 0."""
    rocks = [m for m in (load(p) for p in ROCK_PATHS) if m]
    cliffs = [m for m in (load(p) for p in CLIFF_PATHS) if m]
    mesh_list = rocks if rocks else cliffs
    if not mesh_list:
        return
    for i, (nx, ny, sc) in enumerate(SAT_SPOTS):
        x, y, z, h = uv_xyz(landscape, nx, ny)
        if h < SEA + 50:
            z = 220
        act = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z - 10))
        act.get_component_by_class(unreal.StaticMeshComponent).set_static_mesh(mesh_list[i % len(mesh_list)])
        act.set_actor_rotation(unreal.Rotator(0.0, float(rng.uniform(0, 360)), 0.0), False)
        act.set_actor_scale3d(unreal.Vector(sc, sc, sc * 0.85))
        act.set_actor_label(f"SatelliteIsle_{i}")
    log(f"Level satellites x{len(SAT_SPOTS)}")


def place_cave(sub, landscape):
    cliffs = [m for m in (load(p) for p in CLIFF_PATHS) if m]
    if not cliffs:
        return
    x, y, z, _ = uv_xyz(landscape, CAVE_CX, CAVE_CY)
    for i, (ox, oy, yaw, pitch, sc) in enumerate([
        (-140, -60, 210, -10, (2.2, 1.8, 2.4)),
        (140, -40, 150, -10, (2.2, 1.8, 2.4)),
        (0, 40, 180, -18, (2.8, 1.6, 1.8)),
    ]):
        act = sub.spawn_actor_from_class(
            unreal.StaticMeshActor, unreal.Vector(x + ox, y + oy, z - 20 + (30 if i == 2 else 0))
        )
        act.get_component_by_class(unreal.StaticMeshComponent).set_static_mesh(cliffs[i % len(cliffs)])
        act.set_actor_rotation(unreal.Rotator(pitch, yaw, 0), False)
        act.set_actor_scale3d(unreal.Vector(*sc))
        act.set_actor_label(f"CaveMouth_{i}")
    log("Cave mouth placed")


def fix_water(sub):
    waters = [a for a in sub.get_all_level_actors() if "Water" in a.get_class().get_name()]
    waters.sort(key=lambda a: a.get_actor_location().z)
    for i, w in enumerate(waters):
        if i == 0:
            w.set_actor_location(unreal.Vector(0, 0, 0), False, False)
        else:
            sub.destroy_actor(w)


def main():
    if not os.path.isfile(PNG_RG):
        log("Run create_island_heightmap_v9.py first")
        return
    h = heights()
    peak = max(h)
    ix = int((LAKE_CX + 1) * 0.5 * (SIZE - 1))
    iy = int((LAKE_CY + 1) * 0.5 * (SIZE - 1))
    log(f"Height file peak={peak} sea_delta={peak - SEA} lake={h[iy * SIZE + ix]}")

    rng = random.Random(42)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    landscape = next(a for a in sub.get_all_level_actors() if isinstance(a, unreal.Landscape))

    apply_height(world, landscape)
    loc = landscape.get_actor_location()
    sc = landscape.get_actor_scale3d()
    landscape.set_actor_location(unreal.Vector(loc.x, loc.y, 0.0), False, False)
    landscape.set_actor_scale3d(unreal.Vector(sc.x, sc.y, SCALE_Z))
    log(f"ScaleZ -> {SCALE_Z}")

    mat = load(ASSETS["landscape_mat"])
    if mat:
        landscape.set_editor_property("landscape_material", mat)
        log("MI_Landscape set")

    restore_weightmaps(world, landscape)
    ensure_rvt(sub)
    clear_junk(sub)
    plant_forest(sub, landscape, rng)
    place_village(sub, landscape)
    place_sw_cliff(sub, landscape)
    place_satellites(sub, landscape, rng)
    place_cave(sub, landscape)
    fix_water(sub)

    _, _, lake_z, lake_h = uv_xyz(landscape, LAKE_CX, LAKE_CY)
    _, _, rim_z, rim_h = uv_xyz(landscape, LAKE_CX + 0.11, LAKE_CY)
    _, _, peak_z, peak_h = uv_xyz(landscape, 0.35, 0.45)
    log(f"Lake Z={lake_z:.0f} drop={rim_z - lake_z:.0f} | Peak Z≈{peak_z:.0f} h={peak_h}")

    px, py, pz, _ = uv_xyz(landscape, VILLAGE_CX, VILLAGE_CY - 0.04)
    for act in sub.get_all_level_actors():
        if isinstance(act, unreal.PlayerStart):
            act.set_actor_location(unreal.Vector(px, py, pz + 120), False, False)

    o, e = landscape.get_actor_bounds(False, False)
    ntrees = sum(1 for a in sub.get_all_level_actors() if a.get_actor_label().startswith("ForestTree"))
    log(f"FINAL Z {o.z - e.z:.0f}..{o.z + e.z:.0f} trees={ntrees}")
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    try:
        unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    except Exception:
        pass
    log("SAVED v12")
    with open(RESULT, "w", encoding="utf-8") as f:
        f.write("\n".join(OUT))


if __name__ == "__main__":
    main()
