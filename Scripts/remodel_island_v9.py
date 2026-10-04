"""
Island remodel v9:
- Import curved back-edge mountain heightmap
- Slightly thinner forests
- Wide clear paths: beach↔village, village↔mountain/cave, village↔lake
- Desert cliff cluster SE of range
- Cave mouth props at carved tunnel
- No floating butte rock on summit

CLOSE EDITOR FIRST. Needs -AllowCommandletRendering.
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
SCALE_Z = 180.0
RESULT = "F:/DEVELOPMENT/Games/SpellCraft/Saved/Logs/remodel_island_v9.txt"
OUT = []

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
BUSH_PATHS = [
    "/Game/SoStylized/Environment/Foliage/SM_Bush1.SM_Bush1",
    "/Game/SoStylized/Environment/Foliage/SM_Bush2.SM_Bush2",
    "/Game/SoStylized/Environment/Foliage/SM_Fern1.SM_Fern1",
]
CLIFF_PATHS = [
    "/Game/SoStylized/Environment/Rocks/Classic/SM_CliffClassic1.SM_CliffClassic1",
    "/Game/SoStylized/Environment/Rocks/Classic/SM_CliffClassic2.SM_CliffClassic2",
    "/Game/SoStylized/Environment/Rocks/Classic/SM_CliffClassic3.SM_CliffClassic3",
    "/Game/SoStylized/Environment/Rocks/Classic/SM_CliffClassic4.SM_CliffClassic4",
    "/Game/SoStylized/Environment/Rocks/Classic/SM_CliffClassic5.SM_CliffClassic5",
]
ROCK_PATHS = [
    "/Game/SoStylized/Environment/Rocks/Classic/SM_BoulderClassic1.SM_BoulderClassic1",
    "/Game/SoStylized/Environment/Rocks/Classic/SM_BoulderClassic2.SM_BoulderClassic2",
    "/Game/SoStylized/Environment/Rocks/Classic/SM_BoulderClumpClassic1.SM_BoulderClumpClassic1",
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
LAMP_BP = "/Game/AdvancedVillagePack/Blueprints/BP_Street_Lamp"

LAKE_CX, LAKE_CY, LAKE_R = 0.08, 0.08, 0.13
VILLAGE_CX, VILLAGE_CY, VILLAGE_R = 0.0, -0.12, 0.15
BEACH_CX, BEACH_CY = -0.45, -0.45
CAVE_CX, CAVE_CY = 0.42, 0.38
DESERT_CX, DESERT_CY = 0.55, 0.25

# Wide path polylines in nx,ny (normalized). Half-width ~0.055 ≈ wide road.
PATHS = [
    # beach → village
    [(-0.55, -0.55), (-0.35, -0.40), (-0.18, -0.28), (-0.05, -0.18), (0.0, -0.12)],
    # village → lake shore
    [(0.0, -0.12), (0.03, -0.02), (0.06, 0.04)],
    # village → mountain trail / cave
    [(0.0, -0.12), (0.12, -0.02), (0.25, 0.12), (0.35, 0.28), (0.42, 0.38)],
    # village east loop toward desert cliff overlook
    [(0.0, -0.12), (0.18, -0.15), (0.35, 0.0), (0.50, 0.18)],
]
PATH_HALF_W = 0.052

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


def dist_point_seg(px, py, ax, ay, bx, by):
    abx, aby = bx - ax, by - ay
    t = ((px - ax) * abx + (py - ay) * aby) / max(1e-8, abx * abx + aby * aby)
    t = max(0.0, min(1.0, t))
    cx, cy = ax + t * abx, ay + t * aby
    return math.hypot(px - cx, py - cy)


def on_path(nx, ny):
    for poly in PATHS:
        for i in range(len(poly) - 1):
            ax, ay = poly[i]
            bx, by = poly[i + 1]
            if dist_point_seg(nx, ny, ax, ay, bx, by) < PATH_HALF_W:
                return True
    return False


def forest_ok(nx, ny, h):
    if h < SEA + 700:
        return False
    if nx < -0.15 and ny < -0.15:
        return False
    if math.hypot(nx - LAKE_CX, ny - LAKE_CY) < LAKE_R:
        return False
    if math.hypot(nx - VILLAGE_CX, ny - VILLAGE_CY) < VILLAGE_R:
        return False
    if on_path(nx, ny):
        return False
    # alpine / desert rock — no dense forest
    if nx > 0.35 and ny > 0.25 and h > SEA + 9000:
        return False
    if math.hypot(nx - DESERT_CX, ny - DESERT_CY) < 0.14:
        return False
    if abs(nx) > 0.78 or abs(ny) > 0.78:
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


def clear_junk(sub):
    n = 0
    for act in list(sub.get_all_level_actors()):
        label = act.get_actor_label()
        ll = label.lower()
        if any(
            label.startswith(p) or p in ll
            for p in (
                "ForestTree", "ForestBush", "IslandTree", "IslandPointed",
                "SatelliteIsle", "Village_", "PlayerHouse", "DesertCliff",
                "CaveMouth", "PathMarker", "foresttree", "islandpointed"
            )
        ):
            sub.destroy_actor(act)
            n += 1
            continue
        if isinstance(act, unreal.StaticMeshActor):
            try:
                mesh = act.static_mesh_component.static_mesh
                mn = mesh.get_name().lower() if mesh else ""
            except Exception:
                mn = ""
            if any(k in mn for k in ("cliffclassic", "fallen", "shelf", "platform", "cubiccliff")):
                sub.destroy_actor(act)
                n += 1
                continue
            loc = act.get_actor_location()
            if loc.z > 5000 and any(k in mn for k in ("rock", "boulder", "cliff")):
                sub.destroy_actor(act)
                n += 1
    log(f"Cleared {n}")


def plant_forest(sub, landscape, rng):
    trees = [m for m in (load(p) for p in TREE_PATHS) if m]
    bushes = [m for m in (load(p) for p in BUSH_PATHS) if m]
    if not trees:
        log("ERROR no trees")
        return
    # Slightly less dense than v8 (step 5 → 7)
    step = 7
    placed = 0
    max_trees = 12000
    for iy in range(3, SIZE - 3, step):
        for ix in range(3, SIZE - 3, step):
            if placed >= max_trees:
                break
            jx = max(1, min(SIZE - 2, ix + rng.randint(-2, 2)))
            jy = max(1, min(SIZE - 2, iy + rng.randint(-2, 2)))
            nx, ny = nxny(jx, jy)
            x, y, z, h = land_xyz(landscape, jx, jy)
            if not forest_ok(nx, ny, h):
                continue
            if rng.random() < 0.12:
                continue
            mesh = trees[rng.randint(0, len(trees) - 1)]
            if h > SEA + 7000:
                pines = [t for t in trees if "Pine" in t.get_name()]
                if pines:
                    mesh = pines[rng.randint(0, len(pines) - 1)]
            s = rng.uniform(1.4, 2.6)
            act = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z - 25))
            act.get_component_by_class(unreal.StaticMeshComponent).set_static_mesh(mesh)
            act.set_actor_scale3d(unreal.Vector(s, s, s))
            act.set_actor_rotation(unreal.Rotator(0.0, float(rng.uniform(0, 360)), 0.0), False)
            act.set_actor_label(f"ForestTree_{placed}")
            placed += 1
            if bushes and rng.random() < 0.10:
                bx, by, bz, _ = land_xyz(
                    landscape,
                    max(1, min(SIZE - 2, jx + rng.randint(-2, 2))),
                    max(1, min(SIZE - 2, jy + rng.randint(-2, 2))),
                )
                bact = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(bx, by, bz))
                bact.get_component_by_class(unreal.StaticMeshComponent).set_static_mesh(
                    bushes[rng.randint(0, len(bushes) - 1)]
                )
                bact.set_actor_rotation(unreal.Rotator(0, rng.uniform(0, 360), 0), False)
                bact.set_actor_label(f"ForestBush_{placed}")
        if placed >= max_trees:
            break
    log(f"Planted {placed} trees (thinner + path clearings)")


def uv_to_xy(landscape, nx, ny):
    ix = int(max(0, min(SIZE - 1, (nx + 1) * 0.5 * (SIZE - 1))))
    iy = int(max(0, min(SIZE - 1, (ny + 1) * 0.5 * (SIZE - 1))))
    return land_xyz(landscape, ix, iy)


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
    if act:
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
    cx, cy, cz, _ = uv_to_xy(landscape, VILLAGE_CX, VILLAGE_CY)
    if not spawn_bp(sub, HOUSE_BPS[0], unreal.Vector(cx, cy + 300, cz), 180, 1.15, "PlayerHouse"):
        spawn_mesh(sub, HOUSE_MESHES[0], unreal.Vector(cx, cy + 300, cz), 180, 0, 1.15, "PlayerHouse")
    spots = [(-800, -100, 40), (850, -80, -35), (-500, -800, 100), (650, -750, -70),
             (-100, -1100, 5), (200, 150, 200), (-950, -500, 120), (1000, -450, -90)]
    sc = landscape.get_actor_scale3d().x
    ix = int((VILLAGE_CX + 1) * 0.5 * (SIZE - 1))
    iy = int((VILLAGE_CY + 1) * 0.5 * (SIZE - 1))
    for i, (ox, oy, yaw) in enumerate(spots):
        tx = max(1, min(SIZE - 2, ix + int(ox / sc)))
        ty = max(1, min(SIZE - 2, iy + int(oy / sc)))
        x, y, z, _ = land_xyz(landscape, tx, ty)
        if not spawn_bp(sub, HOUSE_BPS[i % 2], unreal.Vector(x, y, z), yaw, 1.0, f"Village_House_{i}"):
            spawn_mesh(sub, HOUSE_MESHES[i % 2], unreal.Vector(x, y, z), yaw, 0, 1.0, f"Village_House_{i}")
    spawn_bp(sub, WELL_BP, unreal.Vector(cx + 100, cy - 150, cz), label="Village_Well")
    log("Village placed")


def place_desert_cliffs(sub, landscape, rng):
    cliffs = [m for m in (load(p) for p in CLIFF_PATHS) if m]
    rocks = [m for m in (load(p) for p in ROCK_PATHS) if m]
    if not cliffs:
        log("No cliff meshes")
        return
    # Arc of desert cliffs along SE mountain face
    for i, (nx, ny, yaw, sc) in enumerate([
        (0.48, 0.22, 200, (3.2, 3.2, 2.8)),
        (0.55, 0.28, 220, (4.0, 3.5, 3.5)),
        (0.62, 0.32, 240, (3.5, 3.5, 4.0)),
        (0.58, 0.18, 180, (2.8, 2.8, 2.5)),
        (0.68, 0.25, 250, (3.0, 3.0, 3.2)),
    ]):
        x, y, z, _ = uv_to_xy(landscape, nx, ny)
        mesh = cliffs[i % len(cliffs)]
        act = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z - 80))
        act.get_component_by_class(unreal.StaticMeshComponent).set_static_mesh(mesh)
        act.set_actor_rotation(unreal.Rotator(-6, yaw, 0), False)
        act.set_actor_scale3d(unreal.Vector(*sc))
        act.set_actor_label(f"DesertCliff_{i}")
        if rocks:
            for j in range(3):
                rx, ry, rz, _ = uv_to_xy(
                    landscape, nx + rng.uniform(-0.04, 0.04), ny + rng.uniform(-0.04, 0.04)
                )
                ract = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(rx, ry, rz - 20))
                ract.get_component_by_class(unreal.StaticMeshComponent).set_static_mesh(
                    rocks[rng.randint(0, len(rocks) - 1)]
                )
                ract.set_actor_rotation(unreal.Rotator(0, rng.uniform(0, 360), 0), False)
                ract.set_actor_scale3d(unreal.Vector(rng.uniform(0.8, 1.6)))
                ract.set_actor_label(f"DesertRock_{i}_{j}")
    log("Desert cliff cluster placed SE of range")


def place_cave_mouth(sub, landscape):
    cliffs = [m for m in (load(p) for p in CLIFF_PATHS) if m]
    x, y, z, _ = uv_to_xy(landscape, CAVE_CX, CAVE_CY)
    # Frame cave with two leaning cliffs + overhang
    if cliffs:
        for i, (ox, oy, yaw, pitch, sc) in enumerate([
            (-180, -80, 210, -15, (2.5, 2.2, 2.8)),
            (180, -60, 150, -12, (2.5, 2.2, 2.8)),
            (0, 40, 180, -25, (3.5, 2.0, 2.2)),  # overhang
        ]):
            act = sub.spawn_actor_from_class(
                unreal.StaticMeshActor, unreal.Vector(x + ox, y + oy, z - 40 + (30 if i == 2 else 0))
            )
            act.get_component_by_class(unreal.StaticMeshComponent).set_static_mesh(cliffs[i % len(cliffs)])
            act.set_actor_rotation(unreal.Rotator(pitch, yaw, 0), False)
            act.set_actor_scale3d(unreal.Vector(*sc))
            act.set_actor_label(f"CaveMouth_{i}")
    log("Cave mouth framed at mountain trail end")


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
        log("Run create_island_heightmap_v6.py first")
        return
    rng = random.Random(19)
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

    try:
        mat = load("/Game/SoStylized/Environment/Landscape/Materials/MI_Landscape.MI_Landscape")
        if mat:
            landscape.set_editor_property("landscape_material", mat)
    except Exception:
        pass

    clear_junk(sub)
    plant_forest(sub, landscape, rng)
    place_village(sub, landscape)
    place_desert_cliffs(sub, landscape, rng)
    place_cave_mouth(sub, landscape)
    fix_water(sub)

    px, py, pz, _ = uv_to_xy(landscape, VILLAGE_CX, VILLAGE_CY - 0.06)
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
    log("SAVED v9 — reopen + Reload from disk.")
    with open(RESULT, "w", encoding="utf-8") as f:
        f.write("\n".join(OUT))


if __name__ == "__main__":
    main()
