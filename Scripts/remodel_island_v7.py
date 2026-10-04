"""
Island remodel v7 — dense upright forests, village, tall mountains.

CLOSE Unreal Editor first. Needs -AllowCommandletRendering.
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
RESULT = "F:/DEVELOPMENT/Games/SpellCraft/Saved/Logs/remodel_island_v7.txt"
OUT = []

# Upright trees ONLY — never Fallen / Branch / Sapling / Roots / Stump
TREE_PATHS = [
    "/Game/SoStylized/Environment/Trees/Oak/SM_OakTree1.SM_OakTree1",
    "/Game/SoStylized/Environment/Trees/Oak/SM_OakTree2.SM_OakTree2",
    "/Game/SoStylized/Environment/Trees/Oak/SM_OakTree3.SM_OakTree3",
    "/Game/SoStylized/Environment/Trees/Oak/SM_OakTree4.SM_OakTree4",
    "/Game/SoStylized/Environment/Trees/Oak/SM_OakTreeLarge1.SM_OakTreeLarge1",
    "/Game/SoStylized/Environment/Trees/Oak/SM_OakTreeLarge2.SM_OakTreeLarge2",
    "/Game/SoStylized/Environment/Trees/Pine/SM_Pine01.SM_Pine01",
    "/Game/SoStylized/Environment/Trees/Pine/SM_Pine02.SM_Pine02",
    "/Game/SoStylized/Environment/Trees/Pine/SM_Pine03.SM_Pine03",
]

BUSH_PATHS = [
    "/Game/SoStylized/Environment/Foliage/SM_Bush1.SM_Bush1",
    "/Game/SoStylized/Environment/Foliage/SM_Bush2.SM_Bush2",
    "/Game/SoStylized/Environment/Foliage/SM_Fern1.SM_Fern1",
]

HOUSE_BPS = [
    "/Game/AdvancedVillagePack/Blueprints/BP_House_Var01.BP_House_Var01_C",
    "/Game/AdvancedVillagePack/Blueprints/BP_House_Var02.BP_House_Var02_C",
]
HOUSE_MESHES = [
    "/Game/AdvancedVillagePack/Meshes/SM_House_Var01.SM_House_Var01",
    "/Game/AdvancedVillagePack/Meshes/SM_House_Var02.SM_House_Var02",
]
FANTASTIC_HOUSES = [
    "/Game/Fantastic_Village_Pack/blueprints/buildings/BP_BLD_house_1.BP_BLD_house_1_C",
    "/Game/Fantastic_Village_Pack/blueprints/buildings/BP_BLD_house_2.BP_BLD_house_2_C",
    "/Game/Fantastic_Village_Pack/blueprints/buildings/BP_BLD_house_3.BP_BLD_house_3_C",
    "/Game/Fantastic_Village_Pack/blueprints/buildings/BP_BLD_house_4.BP_BLD_house_4_C",
    "/Game/Fantastic_Village_Pack/blueprints/buildings/BP_BLD_house_5.BP_BLD_house_5_C",
]
WELL_BP = "/Game/AdvancedVillagePack/Blueprints/BP_Well.BP_Well_C"
LAMP_BP = "/Game/AdvancedVillagePack/Blueprints/BP_Street_Lamp.BP_Street_Lamp_C"
CLIFF = "/Game/SoStylized/Environment/Rocks/Classic/SM_CliffClassic2.SM_CliffClassic2"

# Exclusion zones in normalized map space [-1,1]
LAKE_CX, LAKE_CY, LAKE_R = 0.10, 0.12, 0.13
VILLAGE_CX, VILLAGE_CY, VILLAGE_R = 0.02, -0.08, 0.16
BEACH_NX, BEACH_NY = -0.15, -0.15  # SW beach if both below these

HEIGHT_CACHE = None


def log(msg):
    OUT.append(str(msg))
    unreal.log(msg)


def load(path):
    return unreal.EditorAssetLibrary.load_asset(path)


def load_heights():
    global HEIGHT_CACHE
    if HEIGHT_CACHE is None:
        with open(R16, "rb") as f:
            HEIGHT_CACHE = struct.unpack(f"<{SIZE * SIZE}H", f.read())
    return HEIGHT_CACHE


def height_at(x, y, lo, le):
    u = (x - (lo.x - le.x)) / max(1.0, 2.0 * le.x)
    v = (y - (lo.y - le.y)) / max(1.0, 2.0 * le.y)
    ix = int(max(0, min(SIZE - 1, u * (SIZE - 1))))
    iy = int(max(0, min(SIZE - 1, v * (SIZE - 1))))
    h = load_heights()[iy * SIZE + ix]
    return (h - SEA) * 100.0 / 128.0


def world_to_nxny(x, y, lo, le):
    nx = (x - lo.x) / max(1.0, le.x)
    ny = (y - lo.y) / max(1.0, le.y)
    return nx, ny


def is_forest_ok(nx, ny):
    if nx < BEACH_NX and ny < BEACH_NY:
        return False  # beach
    if math.hypot(nx - LAKE_CX, ny - LAKE_CY) < LAKE_R:
        return False  # lake + shore
    if math.hypot(nx - VILLAGE_CX, ny - VILLAGE_CY) < VILLAGE_R:
        return False  # village clearing
    if nx > 0.42 and ny > 0.42:
        return False  # rocky mountain peak
    if abs(nx) > 0.78 or abs(ny) > 0.78:
        return False  # ocean
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


def clear_props(sub):
    n = 0
    for act in list(sub.get_all_level_actors()):
        if not isinstance(act, unreal.StaticMeshActor):
            # also remove previously spawned village BP actors we tagged
            label = act.get_actor_label()
            if label.startswith("Village_") or label.startswith("PlayerHouse"):
                sub.destroy_actor(act)
                n += 1
            continue
        label = act.get_actor_label().lower()
        name = act.get_name().lower()
        if any(
            t in label or t in name
            for t in (
                "foresttree", "islandtree", "bush", "satelliteisle",
                "islandpointed", "village_", "playerhouse"
            )
        ):
            sub.destroy_actor(act)
            n += 1
            continue
        # kill leftover cliff platforms / fallen trees
        try:
            mesh = act.static_mesh_component.static_mesh
            mn = mesh.get_name().lower() if mesh else ""
        except Exception:
            mn = ""
        if any(k in mn for k in ("fallen", "shelf", "platform", "cliffclassic", "oakfallen", "pinefallen")):
            if "islandpointed" not in label:
                sub.destroy_actor(act)
                n += 1
    log(f"Cleared {n} old props")


def make_upright(act, yaw):
    """SoStylized trees are Z-up; force world upright (pitch=0,roll=0) + yaw only."""
    smc = act.get_component_by_class(unreal.StaticMeshComponent)
    if smc:
        smc.set_relative_rotation(unreal.Rotator(0.0, 0.0, 0.0), False, False)
        smc.set_relative_location(unreal.Vector(0, 0, 0), False, False)
    act.set_actor_rotation(unreal.Rotator(0.0, float(yaw), 0.0), False)
    # If still flat (Z extent tiny vs XY), pitch -90 to stand mesh up
    o, e = act.get_actor_bounds(False, False)
    if e.z < max(e.x, e.y) * 0.45:
        act.set_actor_rotation(unreal.Rotator(-90.0, float(yaw), 0.0), False)
        o2, e2 = act.get_actor_bounds(False, False)
        if e2.z < e.z:
            # worse — try +90
            act.set_actor_rotation(unreal.Rotator(90.0, float(yaw), 0.0), False)


def plant_dense_forest(sub, landscape, rng):
    trees = [m for m in (load(p) for p in TREE_PATHS) if m]
    bushes = [m for m in (load(p) for p in BUSH_PATHS) if m]
    if not trees:
        log("ERROR: no tree meshes loaded")
        return
    log(f"Tree meshes OK: {[t.get_name() for t in trees]}")

    lo, le = landscape.get_actor_bounds(False, False)
    placed = 0
    # Dense grid ~550uu spacing across island
    step = 550.0
    x0, x1 = lo.x - le.x * 0.72, lo.x + le.x * 0.72
    y0, y1 = lo.y - le.y * 0.72, lo.y + le.y * 0.72
    x = x0
    while x < x1:
        y = y0
        while y < y1:
            jx = x + rng.uniform(-180, 180)
            jy = y + rng.uniform(-180, 180)
            nx, ny = world_to_nxny(jx, jy, lo, le)
            if is_forest_ok(nx, ny):
                z = height_at(jx, jy, lo, le)
                if z > 400:
                    mesh = trees[rng.randint(0, len(trees) - 1)]
                    s = rng.uniform(1.4, 2.8)
                    # pines on higher ground
                    if z > 3500 and any("Pine" in t.get_name() for t in trees):
                        pines = [t for t in trees if "Pine" in t.get_name()]
                        if pines:
                            mesh = pines[rng.randint(0, len(pines) - 1)]
                    act = sub.spawn_actor_from_class(
                        unreal.StaticMeshActor, unreal.Vector(jx, jy, z - 25.0)
                    )
                    smc = act.get_component_by_class(unreal.StaticMeshComponent)
                    smc.set_static_mesh(mesh)
                    act.set_actor_scale3d(unreal.Vector(s, s, s))
                    make_upright(act, rng.uniform(0, 360))
                    act.set_actor_label(f"ForestTree_{placed}")
                    placed += 1
                    if bushes and rng.random() < 0.22:
                        bx = jx + rng.uniform(-200, 200)
                        by = jy + rng.uniform(-200, 200)
                        bz = height_at(bx, by, lo, le)
                        bact = sub.spawn_actor_from_class(
                            unreal.StaticMeshActor, unreal.Vector(bx, by, bz)
                        )
                        bsmc = bact.get_component_by_class(unreal.StaticMeshComponent)
                        bsmc.set_static_mesh(bushes[rng.randint(0, len(bushes) - 1)])
                        bact.set_actor_rotation(unreal.Rotator(0, rng.uniform(0, 360), 0), False)
                        bact.set_actor_scale3d(unreal.Vector(1.0, 1.0, 1.0))
                        bact.set_actor_label(f"ForestBush_{placed}")
            y += step
        x += step
    log(f"Planted {placed} upright forest trees")


def spawn_bp(sub, class_path, loc, yaw=0.0, scale=1.0, label=""):
    cls = unreal.EditorAssetLibrary.load_blueprint_class(class_path.replace("_C", "").rsplit(".", 1)[0])
    if not cls:
        # try full path as generated class
        asset = load(class_path.replace("_C", ""))
        if asset:
            try:
                cls = asset.generated_class()
            except Exception:
                cls = None
    if not cls:
        # fallback: load soft class
        try:
            cls = unreal.load_class(None, class_path)
        except Exception:
            cls = None
    if not cls:
        log(f"Could not load BP {class_path}")
        return None
    act = sub.spawn_actor_from_class(cls, loc)
    if act:
        act.set_actor_rotation(unreal.Rotator(0, yaw, 0), False)
        if scale != 1.0:
            act.set_actor_scale3d(unreal.Vector(scale, scale, scale))
        if label:
            act.set_actor_label(label)
    return act


def spawn_house_mesh(sub, mesh_path, loc, yaw, scale, label):
    mesh = load(mesh_path)
    if not mesh:
        return None
    act = sub.spawn_actor_from_class(unreal.StaticMeshActor, loc)
    smc = act.get_component_by_class(unreal.StaticMeshComponent)
    smc.set_static_mesh(mesh)
    act.set_actor_rotation(unreal.Rotator(0, yaw, 0), False)
    act.set_actor_scale3d(unreal.Vector(scale, scale, scale))
    act.set_actor_label(label)
    return act


def place_village(sub, landscape, rng):
    lo, le = landscape.get_actor_bounds(False, False)
    # Village center south of lake
    cx = lo.x + VILLAGE_CX * le.x
    cy = lo.y + VILLAGE_CY * le.y
    cz = height_at(cx, cy, lo, le)

    # Player house — slightly larger, labeled
    ph = spawn_bp(
        sub, HOUSE_BPS[0],
        unreal.Vector(cx, cy + 400, cz),
        yaw=180, scale=1.15, label="PlayerHouse",
    )
    if not ph:
        spawn_house_mesh(
            sub, HOUSE_MESHES[0],
            unreal.Vector(cx, cy + 400, cz),
            180, 1.15, "PlayerHouse",
        )
        log("PlayerHouse via mesh fallback")
    else:
        log("PlayerHouse BP placed")

    # Ring of village houses
    offsets = [
        (-900, -200, 40), (900, -150, -30), (-600, -900, 90),
        (700, -850, -80), (-200, -1200, 10), (300, 200, 200),
        (-1100, -600, 120), (1100, -500, -110),
    ]
    for i, (ox, oy, yaw) in enumerate(offsets):
        loc = unreal.Vector(cx + ox, cy + oy, height_at(cx + ox, cy + oy, lo, le))
        ok = spawn_bp(sub, HOUSE_BPS[i % 2], loc, yaw=yaw, scale=1.0, label=f"Village_House_{i}")
        if not ok:
            spawn_house_mesh(
                sub, HOUSE_MESHES[i % 2], loc, yaw, 1.0, f"Village_House_{i}"
            )
        # Try a couple Fantastic houses too
        if i < 3:
            spawn_bp(
                sub, FANTASTIC_HOUSES[i],
                unreal.Vector(cx + ox * 0.55, cy + oy * 0.55 - 400, height_at(cx, cy, lo, le)),
                yaw=yaw + 45, scale=1.0, label=f"Village_FanHouse_{i}",
            )

    spawn_bp(sub, WELL_BP, unreal.Vector(cx + 150, cy - 200, cz), label="Village_Well")
    for i, (lx, ly) in enumerate([(-500, -400), (500, -350), (0, -1000), (-800, 100)]):
        spawn_bp(
            sub, LAMP_BP,
            unreal.Vector(cx + lx, cy + ly, height_at(cx + lx, cy + ly, lo, le)),
            label=f"Village_Lamp_{i}",
        )
    log("Village placed near lake (clearing kept tree-free)")


def place_ne_cliff(sub, landscape):
    lo, le = landscape.get_actor_bounds(False, False)
    x = lo.x + le.x * 0.68
    y = lo.y + le.y * 0.58
    z = height_at(x, y, lo, le)
    mesh = load(CLIFF)
    if not mesh:
        return
    act = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z - 200))
    smc = act.get_component_by_class(unreal.StaticMeshComponent)
    smc.set_static_mesh(mesh)
    act.set_actor_rotation(unreal.Rotator(-12, 35, 0), False)
    act.set_actor_scale3d(unreal.Vector(3.5, 3.5, 4.5))
    act.set_actor_label("IslandPointedCliff_NE")
    log("NE pointed cliff placed")


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
        log("Missing heightmap — run create_island_heightmap_v4.py")
        return
    rng = random.Random(7)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    landscape = next(a for a in sub.get_all_level_actors() if isinstance(a, unreal.Landscape))

    apply_height(world, landscape)
    landscape.set_actor_location(unreal.Vector(0, 0, 0), False, False)
    try:
        mat = load("/Game/SoStylized/Environment/Landscape/Materials/MI_Landscape.MI_Landscape")
        if mat:
            landscape.set_editor_property("landscape_material", mat)
    except Exception:
        pass

    clear_props(sub)
    plant_dense_forest(sub, landscape, rng)
    place_village(sub, landscape, rng)
    place_ne_cliff(sub, landscape)
    fix_water(sub)

    # PlayerStart near player house / SW approach
    lo, le = landscape.get_actor_bounds(False, False)
    px = lo.x + VILLAGE_CX * le.x
    py = lo.y + (VILLAGE_CY - 0.08) * le.y
    pz = height_at(px, py, lo, le) + 120
    for act in sub.get_all_level_actors():
        if isinstance(act, unreal.PlayerStart):
            act.set_actor_location(unreal.Vector(px, py, pz), False, False)
            act.set_actor_rotation(unreal.Rotator(0, 45, 0), False)

    o, e = landscape.get_actor_bounds(False, False)
    trees = sum(1 for a in sub.get_all_level_actors() if "ForestTree" in a.get_actor_label())
    log(f"FINAL Z {o.z - e.z:.0f}..{o.z + e.z:.0f}  ForestTree={trees}")
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    try:
        unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    except Exception:
        pass
    log("SAVED v7 — CLOSE/REOPEN editor, Reload Height_DemoCopy from disk.")
    with open(RESULT, "w", encoding="utf-8") as f:
        f.write("\n".join(OUT))


if __name__ == "__main__":
    main()
