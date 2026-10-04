"""
Island remodel v8:
- Import blended heightmap (no center cross seams)
- Raise landscape ScaleZ so mountains actually read
- Delete floating cliff/rock on mountain
- Scatter trees from HEIGHTMAP UV (covers whole island, not one clump)
- Keep beach / lake / village clear
- More trees (~ denser step)

CLOSE EDITOR FIRST.
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
SCALE_Z = 220.0  # strong vertical — mountains must read as mountains
RESULT = "F:/DEVELOPMENT/Games/SpellCraft/Saved/Logs/remodel_island_v8.txt"
OUT = []

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
    "/Game/AdvancedVillagePack/Blueprints/BP_House_Var01",
    "/Game/AdvancedVillagePack/Blueprints/BP_House_Var02",
]
HOUSE_MESHES = [
    "/Game/AdvancedVillagePack/Meshes/SM_House_Var01.SM_House_Var01",
    "/Game/AdvancedVillagePack/Meshes/SM_House_Var02.SM_House_Var02",
]
FANTASTIC = [
    "/Game/Fantastic_Village_Pack/blueprints/buildings/BP_BLD_house_1",
    "/Game/Fantastic_Village_Pack/blueprints/buildings/BP_BLD_house_2",
    "/Game/Fantastic_Village_Pack/blueprints/buildings/BP_BLD_house_3",
]
WELL_BP = "/Game/AdvancedVillagePack/Blueprints/BP_Well"
LAMP_BP = "/Game/AdvancedVillagePack/Blueprints/BP_Street_Lamp"

LAKE_CX, LAKE_CY, LAKE_R = 0.10, 0.12, 0.14
VILLAGE_CX, VILLAGE_CY, VILLAGE_R = 0.02, -0.08, 0.17

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
    """Correct UE landscape texel → world (actor origin = SW corner of heightmap)."""
    loc = landscape.get_actor_location()
    sc = landscape.get_actor_scale3d()
    h = heights()[iy * SIZE + ix]
    x = loc.x + ix * sc.x
    y = loc.y + iy * sc.y
    z = loc.z + (h - SEA) * sc.z / 128.0
    return x, y, z, h


def nxny(ix, iy):
    return ix / (SIZE - 1) * 2.0 - 1.0, iy / (SIZE - 1) * 2.0 - 1.0


def forest_ok(nx, ny, h):
    if h < SEA + 600:
        return False
    if nx < -0.12 and ny < -0.12:
        return False  # beach
    if math.hypot(nx - LAKE_CX, ny - LAKE_CY) < LAKE_R:
        return False
    if math.hypot(nx - VILLAGE_CX, ny - VILLAGE_CY) < VILLAGE_R:
        return False
    if nx > 0.38 and ny > 0.38 and h > SEA + 12000:
        return False  # high rock alpine — sparse/none
    if abs(nx) > 0.80 or abs(ny) > 0.80:
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
                "SatelliteIsle", "Village_", "PlayerHouse", "foresttree", "islandpointed"
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
            # floating cliff/rock props anywhere
            if any(k in mn for k in ("cliffclassic", "fallen", "shelf", "platform", "mesa", "spire")):
                sub.destroy_actor(act)
                n += 1
                continue
            loc = act.get_actor_location()
            # any rock mesh stuck high on NE mountain
            if loc.z > 4000 and any(k in mn for k in ("rock", "boulder", "cliff", "stone")):
                sub.destroy_actor(act)
                n += 1
    log(f"Cleared {n} trees/rocks/cliffs")


def make_upright(act, yaw):
    smc = act.get_component_by_class(unreal.StaticMeshComponent)
    if smc:
        smc.set_relative_rotation(unreal.Rotator(0, 0, 0), False, False)
    act.set_actor_rotation(unreal.Rotator(0.0, float(yaw), 0.0), False)
    o, e = act.get_actor_bounds(False, False)
    if e.z < max(e.x, e.y) * 0.45:
        act.set_actor_rotation(unreal.Rotator(-90.0, float(yaw), 0.0), False)
        o2, e2 = act.get_actor_bounds(False, False)
        if e2.z <= e.z:
            act.set_actor_rotation(unreal.Rotator(90.0, float(yaw), 0.0), False)


def plant_forest(sub, landscape, rng):
    trees = [m for m in (load(p) for p in TREE_PATHS) if m]
    bushes = [m for m in (load(p) for p in BUSH_PATHS) if m]
    if not trees:
        log("ERROR no trees")
        return
    log(f"Trees: {[t.get_name() for t in trees]}")

    # ~500 uu spacing (scale 100) — dense but finishes in minutes
    step = 5
    placed = 0
    max_trees = 18000
    for iy in range(2, SIZE - 2, step):
        for ix in range(2, SIZE - 2, step):
            if placed >= max_trees:
                break
            jx = ix + rng.randint(-1, 1)
            jy = iy + rng.randint(-1, 1)
            jx = max(1, min(SIZE - 2, jx))
            jy = max(1, min(SIZE - 2, jy))
            nx, ny = nxny(jx, jy)
            x, y, z, h = land_xyz(landscape, jx, jy)
            if not forest_ok(nx, ny, h):
                continue
            if rng.random() < 0.05:
                continue
            mesh = trees[rng.randint(0, len(trees) - 1)]
            if h > SEA + 8000:
                pines = [t for t in trees if "Pine" in t.get_name()]
                if pines:
                    mesh = pines[rng.randint(0, len(pines) - 1)]
            s = rng.uniform(1.5, 2.9)
            act = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z - 30))
            smc = act.get_component_by_class(unreal.StaticMeshComponent)
            smc.set_static_mesh(mesh)
            act.set_actor_scale3d(unreal.Vector(s, s, s))
            # Fast upright — SoStylized oaks/pines are Z-up
            act.set_actor_rotation(unreal.Rotator(0.0, float(rng.uniform(0, 360)), 0.0), False)
            act.set_actor_label(f"ForestTree_{placed}")
            placed += 1
            if bushes and rng.random() < 0.12:
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
    log(f"Planted {placed} trees across whole island (UV scatter)")


def spawn_bp(sub, path, loc, yaw=0.0, scale=1.0, label=""):
    cls = unreal.EditorAssetLibrary.load_blueprint_class(path)
    if not cls:
        try:
            cls = unreal.load_class(None, path + "_C")
        except Exception:
            cls = None
    if not cls:
        log(f"BP miss {path}")
        return None
    act = sub.spawn_actor_from_class(cls, loc)
    if act:
        act.set_actor_rotation(unreal.Rotator(0, yaw, 0), False)
        if scale != 1.0:
            act.set_actor_scale3d(unreal.Vector(scale, scale, scale))
        if label:
            act.set_actor_label(label)
    return act


def spawn_mesh(sub, path, loc, yaw, scale, label):
    mesh = load(path)
    if not mesh:
        return None
    act = sub.spawn_actor_from_class(unreal.StaticMeshActor, loc)
    act.get_component_by_class(unreal.StaticMeshComponent).set_static_mesh(mesh)
    act.set_actor_rotation(unreal.Rotator(0, yaw, 0), False)
    act.set_actor_scale3d(unreal.Vector(scale, scale, scale))
    act.set_actor_label(label)
    return act


def place_village(sub, landscape):
    # village UV → texel
    ix = int((VILLAGE_CX + 1) * 0.5 * (SIZE - 1))
    iy = int((VILLAGE_CY + 1) * 0.5 * (SIZE - 1))
    cx, cy, cz, _ = land_xyz(landscape, ix, iy)

    if not spawn_bp(sub, HOUSE_BPS[0], unreal.Vector(cx, cy + 350, cz), 180, 1.2, "PlayerHouse"):
        spawn_mesh(sub, HOUSE_MESHES[0], unreal.Vector(cx, cy + 350, cz), 180, 1.2, "PlayerHouse")
    log("PlayerHouse placed")

    spots = [
        (-850, -150, 35), (900, -120, -40), (-550, -850, 95),
        (700, -800, -70), (-150, -1150, 5), (250, 180, 210),
        (-1000, -550, 130), (1050, -480, -100),
    ]
    for i, (ox, oy, yaw) in enumerate(spots):
        # approximate offset in world (scale ~ SCALE XY 100)
        sc = landscape.get_actor_scale3d().x
        tx = max(1, min(SIZE - 2, ix + int(ox / sc)))
        ty = max(1, min(SIZE - 2, iy + int(oy / sc)))
        x, y, z, _ = land_xyz(landscape, tx, ty)
        if not spawn_bp(sub, HOUSE_BPS[i % 2], unreal.Vector(x, y, z), yaw, 1.0, f"Village_House_{i}"):
            spawn_mesh(sub, HOUSE_MESHES[i % 2], unreal.Vector(x, y, z), yaw, 1.0, f"Village_House_{i}")
        if i < 3:
            spawn_bp(sub, FANTASTIC[i], unreal.Vector(x - 200, y - 300, z), yaw + 40, 1.0, f"Village_Fan_{i}")

    spawn_bp(sub, WELL_BP, unreal.Vector(cx + 120, cy - 180, cz), label="Village_Well")
    for i, (ox, oy) in enumerate([(-400, -350), (450, -300), (0, -950), (-750, 80)]):
        sc = landscape.get_actor_scale3d().x
        tx = max(1, min(SIZE - 2, ix + int(ox / sc)))
        ty = max(1, min(SIZE - 2, iy + int(oy / sc)))
        x, y, z, _ = land_xyz(landscape, tx, ty)
        spawn_bp(sub, LAMP_BP, unreal.Vector(x, y, z), label=f"Village_Lamp_{i}")
    log("Village placed (lake clearing)")


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
        log("Run create_island_heightmap_v5.py first")
        return
    rng = random.Random(11)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    landscape = next(a for a in sub.get_all_level_actors() if isinstance(a, unreal.Landscape))

    apply_height(world, landscape)

    # Landscape origin at SW of map, Z=0 so SEA≈water; boost Z scale for mountain
    loc = landscape.get_actor_location()
    sc = landscape.get_actor_scale3d()
    landscape.set_actor_location(unreal.Vector(loc.x, loc.y, 0.0), False, False)
    landscape.set_actor_scale3d(unreal.Vector(sc.x, sc.y, SCALE_Z))
    log(f"Landscape scale Z -> {SCALE_Z}")

    try:
        mat = load("/Game/SoStylized/Environment/Landscape/Materials/MI_Landscape.MI_Landscape")
        if mat:
            landscape.set_editor_property("landscape_material", mat)
    except Exception:
        pass

    clear_junk(sub)
    plant_forest(sub, landscape, rng)
    place_village(sub, landscape)
    fix_water(sub)

    # PlayerStart at village
    ix = int((VILLAGE_CX + 1) * 0.5 * (SIZE - 1))
    iy = int((VILLAGE_CY + 1) * 0.5 * (SIZE - 1))
    px, py, pz, _ = land_xyz(landscape, ix, iy)
    for act in sub.get_all_level_actors():
        if isinstance(act, unreal.PlayerStart):
            act.set_actor_location(unreal.Vector(px, py - 600, pz + 150), False, False)

    o, e = landscape.get_actor_bounds(False, False)
    ntrees = sum(1 for a in sub.get_all_level_actors() if a.get_actor_label().startswith("ForestTree"))
    log(f"FINAL Z {o.z - e.z:.0f}..{o.z + e.z:.0f} trees={ntrees}")
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    try:
        unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    except Exception:
        pass
    log("SAVED v8 — reopen + Reload from disk.")
    with open(RESULT, "w", encoding="utf-8") as f:
        f.write("\n".join(OUT))


if __name__ == "__main__":
    main()
