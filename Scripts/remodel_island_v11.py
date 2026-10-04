"""
Island remodel v11 — after smoothstep heightmap fix (v8).

- Import soft-coast + real central lake + satellites
- NO desert rock dump (that lower-right mess)
- Pronounced SW coastal cliff only
- RVT volumes (reduces visible 4-way / grid look)
- Upright trees (SMC rot reset + yaw only)
- Wide path clearings (tree gaps only — no height scars)
- Try wipe painted dirt path via weightmap fill
"""
import math
import os
import random
import struct
import unreal

MAP = "/Game/SpellCraft/Maps/Height_DemoCopy"
PNG_RG = "F:/DEVELOPMENT/Games/SpellCraft/Content/SpellCraft/Textures/Island_Heightmap_1009_RG.png"
R16 = "F:/DEVELOPMENT/Games/SpellCraft/Content/SpellCraft/Textures/Island_Heightmap_1009.r16"
SIZE = 1009
SEA = 32768
SCALE_Z = 175.0
RESULT = "F:/DEVELOPMENT/Games/SpellCraft/Saved/Logs/remodel_island_v11.txt"
OUT = []

ASSETS = {
    "landscape_mat": "/Game/SoStylized/Environment/Landscape/Materials/MI_Landscape.MI_Landscape",
    "rvt_landscape": "/Game/SoStylized/Environment/Landscape/Textures/RVT_Landscape.RVT_Landscape",
    "rvt_height": "/Game/SoStylized/Environment/Landscape/Textures/RVT_LandscapeHeight.RVT_LandscapeHeight",
}

TREE_PATHS = [
    "/Game/SoStylized/Environment/Trees/Oak/SM_OakTree1.SM_OakTree1",
    "/Game/SoStylized/Environment/Trees/Oak/SM_OakTree2.SM_OakTree2",
    "/Game/SoStylized/Environment/Trees/Oak/SM_OakTree3.SM_OakTree3",
    "/Game/SoStylized/Environment/Trees/Oak/SM_OakTree4.SM_OakTree4",
    "/Game/SoStylized/Environment/Trees/Oak/SM_OakTreeLarge1.SM_OakTreeLarge1",
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

LAKE_CX, LAKE_CY, LAKE_R = 0.05, -0.02, 0.13
VILLAGE_CX, VILLAGE_CY, VILLAGE_R = -0.02, -0.18, 0.14
CAVE_CX, CAVE_CY = 0.42, 0.38

PATHS = [
    [(-0.55, -0.55), (-0.32, -0.40), (-0.12, -0.28), (-0.02, -0.18)],
    [(-0.02, -0.18), (0.02, -0.08), (0.05, -0.02)],
    [(-0.02, -0.18), (0.12, -0.05), (0.28, 0.15), (0.42, 0.38)],
]
PATH_HALF_W = 0.072  # wide clearings, not varicose scars

SAT_SPOTS = [
    (-0.85, 0.52, 2.6),
    (0.92, -0.12, 2.4),
    (-0.22, -0.88, 2.2),
    (0.75, 0.55, 2.0),
]

HEIGHTS = None


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


def forest_ok(nx, ny, h):
    if h < SEA + 900:
        return False
    if nx < -0.18 and ny < -0.18:
        return False
    if math.hypot(nx - LAKE_CX, ny - LAKE_CY) < LAKE_R + 0.02:
        return False
    if math.hypot(nx - VILLAGE_CX, ny - VILLAGE_CY) < VILLAGE_R:
        return False
    if on_path(nx, ny):
        return False
    if nx > 0.30 and ny > 0.20 and h > SEA + 7500:
        return False
    if abs(nx) > 0.74 or abs(ny) > 0.74:
        return False
    return True


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


def verify_lake_file():
    h = heights()
    ix = int((LAKE_CX + 1) * 0.5 * (SIZE - 1))
    iy = int((LAKE_CY + 1) * 0.5 * (SIZE - 1))
    floor = h[iy * SIZE + ix]
    rim = h[iy * SIZE + min(SIZE - 1, ix + 90)]
    log(f"Lake file check: floor={floor} rim={rim} drop={rim - floor} sea_delta={floor - SEA}")
    if floor <= SEA + 100:
        log("ERROR: lake at/below ocean — will flood")
    if floor >= rim - 400:
        log("ERROR: lake too shallow")


def clear_junk(sub):
    n = 0
    tags = (
        "ForestTree", "ForestBush", "IslandTree", "IslandPointed", "SatelliteIsle",
        "Village_", "PlayerHouse", "DesertCliff", "DesertRock", "CaveMouth",
        "SwCliff", "LakeWater", "foresttree", "islandpointed",
    )
    kill_mesh = (
        "cliffclassic", "fallen", "shelf", "platform", "cubiccliff", "oakfallen",
        "boulderclassic", "boulderclump", "rockclump", "cliff",
    )
    for act in list(sub.get_all_level_actors()):
        label = act.get_actor_label()
        ll = label.lower()
        if any(label.startswith(t) or t.lower() in ll for t in tags):
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
    log(f"Cleared {n}")


def ensure_rvt(sub):
    existing = [a for a in sub.get_all_level_actors() if isinstance(a, unreal.RuntimeVirtualTextureVolume)]
    if len(existing) >= 2:
        log(f"RVT volumes ok ({len(existing)})")
        return
    for a in existing:
        sub.destroy_actor(a)
    for path, loc, scale in (
        (ASSETS["rvt_landscape"], unreal.Vector(-50400, -50400, -8000), unreal.Vector(100800, 100908, 40000)),
        (ASSETS["rvt_height"], unreal.Vector(-50400, -50400, -8000), unreal.Vector(100800, 100800, 40000)),
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
        log(f"RVT spawned {path}")


def try_flatten_weight_paint(world, landscape):
    """Kill varicose dirt path — full-size RTs only (engine requires >= landscape size)."""
    rt_full = unreal.RenderingLibrary.create_render_target2d(
        world, SIZE, SIZE, unreal.TextureRenderTargetFormat.RTF_RGBA8
    )
    rt_zero = unreal.RenderingLibrary.create_render_target2d(
        world, SIZE, SIZE, unreal.TextureRenderTargetFormat.RTF_RGBA8
    )
    for rt, val in ((rt_full, 1.0), (rt_zero, 0.0)):
        canvas, _, ctx = unreal.RenderingLibrary.begin_draw_canvas_to_render_target(world, rt)
        canvas.draw_box(
            unreal.Vector2D(0, 0), unreal.Vector2D(SIZE, SIZE), 1.0,
            unreal.LinearColor(val, val, val, 1),
        )
        unreal.RenderingLibrary.end_draw_canvas_to_render_target(world, ctx)

    # Flood grass; zero dirt/path layers if present
    for layer, use_full in (
        ("Grass", True), ("Sand", True), ("Dirt", False), ("Rock", False),
    ):
        rt = rt_full if use_full else rt_zero
        try:
            ok = landscape.landscape_import_weightmap_from_render_target(rt, layer)
            log(f"weightmap {layer} ({'full' if use_full else 'zero'}) -> {ok}")
        except Exception as e:
            log(f"weightmap {layer} skip: {e}")
    try:
        landscape.force_layers_full_update()
    except Exception:
        pass


def plant_forest(sub, landscape, rng):
    trees = [m for m in (load(p) for p in TREE_PATHS) if m]
    if not trees:
        log("ERROR no trees")
        return
    # Calibrate pitch once
    probe = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, -80000))
    smc = probe.get_component_by_class(unreal.StaticMeshComponent)
    smc.set_static_mesh(trees[0])
    smc.set_relative_rotation(unreal.Rotator(0, 0, 0), False, False)
    probe.set_actor_rotation(unreal.Rotator(0, 0, 0), False)
    _, e0 = probe.get_actor_bounds(False, False)
    base_pitch = 0.0
    if e0.z < max(e0.x, e0.y) * 0.55:
        for trial in (-90.0, 90.0, -90.0):
            probe.set_actor_rotation(unreal.Rotator(trial, 0, 0), False)
            _, et = probe.get_actor_bounds(False, False)
            if et.z >= max(et.x, et.y) * 0.55:
                base_pitch = trial
                break
    sub.destroy_actor(probe)
    log(f"Tree base pitch={base_pitch}")

    step = 8
    placed = 0
    max_trees = 7500
    for iy in range(5, SIZE - 5, step):
        for ix in range(5, SIZE - 5, step):
            if placed >= max_trees:
                break
            jx = max(1, min(SIZE - 2, ix + rng.randint(-2, 2)))
            jy = max(1, min(SIZE - 2, iy + rng.randint(-2, 2)))
            nx, ny = nxny(jx, jy)
            x, y, z, h = land_xyz(landscape, jx, jy)
            if not forest_ok(nx, ny, h):
                continue
            if rng.random() < 0.22:
                continue
            mesh = trees[rng.randint(0, len(trees) - 1)]
            if h > SEA + 6500:
                pines = [t for t in trees if "Pine" in t.get_name()]
                if pines:
                    mesh = pines[rng.randint(0, len(pines) - 1)]
            s = rng.uniform(1.45, 2.35)
            yaw = float(rng.uniform(0, 360))
            act = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z - 18))
            c = act.get_component_by_class(unreal.StaticMeshComponent)
            c.set_static_mesh(mesh)
            c.set_relative_rotation(unreal.Rotator(0, 0, 0), False, False)
            act.set_actor_rotation(unreal.Rotator(base_pitch, yaw, 0.0), False)
            act.set_actor_scale3d(unreal.Vector(s, s, s))
            _, be = act.get_actor_bounds(False, False)
            if be.z < max(be.x, be.y) * 0.45:
                act.set_actor_rotation(unreal.Rotator(-90.0, yaw, 0.0), False)
            act.set_actor_label(f"ForestTree_{placed}")
            placed += 1
        if placed >= max_trees:
            break
    log(f"Planted {placed} upright trees")


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
    for i, (nx, ny, yaw, pitch, sc) in enumerate([
        (-0.58, -0.38, 140, -20, (5.0, 3.8, 5.8)),
        (-0.52, -0.44, 155, -14, (4.0, 3.2, 4.6)),
        (-0.64, -0.32, 125, -16, (4.2, 3.4, 5.0)),
    ]):
        x, y, z, _ = uv_xyz(landscape, nx, ny)
        act = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z - 120))
        act.get_component_by_class(unreal.StaticMeshComponent).set_static_mesh(cliffs[i % len(cliffs)])
        act.set_actor_rotation(unreal.Rotator(pitch, yaw, 0), False)
        act.set_actor_scale3d(unreal.Vector(*sc))
        act.set_actor_label(f"SwCliff_{i}")
    log("SW coastal cliff emphasized")


def place_satellites(sub, landscape, rng):
    cliffs = [m for m in (load(p) for p in CLIFF_PATHS) if m]
    rocks = [m for m in (load(p) for p in ROCK_PATHS) if m]
    mesh_list = cliffs if cliffs else rocks
    if not mesh_list:
        return
    for i, (nx, ny, sc) in enumerate(SAT_SPOTS):
        x, y, z, h = uv_xyz(landscape, nx, ny)
        if h < SEA - 200:
            z = 280
        act = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z - 30))
        act.get_component_by_class(unreal.StaticMeshComponent).set_static_mesh(mesh_list[i % len(mesh_list)])
        act.set_actor_rotation(unreal.Rotator(-4, rng.uniform(0, 360), 0), False)
        act.set_actor_scale3d(unreal.Vector(sc, sc, sc * 1.2))
        act.set_actor_label(f"SatelliteIsle_{i}")
    log(f"Restored {len(SAT_SPOTS)} satellite islets")


def place_cave(sub, landscape):
    cliffs = [m for m in (load(p) for p in CLIFF_PATHS) if m]
    if not cliffs:
        return
    x, y, z, _ = uv_xyz(landscape, CAVE_CX, CAVE_CY)
    for i, (ox, oy, yaw, pitch, sc) in enumerate([
        (-160, -70, 210, -14, (2.4, 2.0, 2.6)),
        (160, -50, 150, -12, (2.4, 2.0, 2.6)),
        (0, 50, 180, -22, (3.2, 1.8, 2.0)),
    ]):
        act = sub.spawn_actor_from_class(
            unreal.StaticMeshActor, unreal.Vector(x + ox, y + oy, z - 30 + (40 if i == 2 else 0))
        )
        act.get_component_by_class(unreal.StaticMeshComponent).set_static_mesh(cliffs[i % len(cliffs)])
        act.set_actor_rotation(unreal.Rotator(pitch, yaw, 0), False)
        act.set_actor_scale3d(unreal.Vector(*sc))
        act.set_actor_label(f"CaveMouth_{i}")
    log("Cave mouth placed")


def place_lake_water(sub, landscape):
    """Plane in the carved basin, above ocean, below rim."""
    x, y, floor_z, _ = uv_xyz(landscape, LAKE_CX, LAKE_CY)
    _, _, rim_z, _ = uv_xyz(landscape, LAKE_CX + LAKE_R * 0.8, LAKE_CY)
    water_z = max(80.0, floor_z + (rim_z - floor_z) * 0.55)
    plane = load("/Engine/BasicShapes/Plane.Plane")
    if not plane:
        log("No plane mesh for lake water")
        return
    act = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, water_z))
    act.get_component_by_class(unreal.StaticMeshComponent).set_static_mesh(plane)
    act.set_actor_scale3d(unreal.Vector(48.0, 48.0, 1.0))
    act.set_actor_label("LakeWater")
    log(f"Lake water plane at Z={water_z:.0f} (floor={floor_z:.0f} rim={rim_z:.0f})")


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
        log("Run create_island_heightmap_v8.py first")
        return
    verify_lake_file()
    rng = random.Random(31)
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

    try_flatten_weight_paint(world, landscape)
    ensure_rvt(sub)
    clear_junk(sub)
    plant_forest(sub, landscape, rng)
    place_village(sub, landscape)
    place_sw_cliff(sub, landscape)
    place_satellites(sub, landscape, rng)
    place_cave(sub, landscape)
    place_lake_water(sub, landscape)
    fix_water(sub)

    px, py, pz, _ = uv_xyz(landscape, VILLAGE_CX, VILLAGE_CY - 0.05)
    for act in sub.get_all_level_actors():
        if isinstance(act, unreal.PlayerStart):
            act.set_actor_location(unreal.Vector(px, py, pz + 120), False, False)

    # Post-check lake world Z
    _, _, lake_z, lake_h = uv_xyz(landscape, LAKE_CX, LAKE_CY)
    _, _, rim_z, rim_h = uv_xyz(landscape, LAKE_CX + 0.12, LAKE_CY)
    log(f"Lake world Z={lake_z:.0f} h={lake_h}; rim Z={rim_z:.0f} h={rim_h}; dropZ={rim_z - lake_z:.0f}")

    o, e = landscape.get_actor_bounds(False, False)
    ntrees = sum(1 for a in sub.get_all_level_actors() if a.get_actor_label().startswith("ForestTree"))
    log(f"FINAL Z {o.z - e.z:.0f}..{o.z + e.z:.0f} trees={ntrees}")
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    try:
        unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    except Exception:
        pass
    log("SAVED v11")
    with open(RESULT, "w", encoding="utf-8") as f:
        f.write("\n".join(OUT))


if __name__ == "__main__":
    main()
