"""
Import UCreate Tropical Island heightmap into Height_DemoCopy.
No Gaea graph required — uses prebuilt Island_01_Height (+ splats).
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
SCALE_Z = 175.0
RESULT = "F:/DEVELOPMENT/Games/SpellCraft/Saved/Logs/import_ucreate_island.txt"
OUT = []

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
HOUSE_BPS = [
    "/Game/AdvancedVillagePack/Blueprints/BP_House_Var01",
    "/Game/AdvancedVillagePack/Blueprints/BP_House_Var02",
]
HOUSE_MESHES = [
    "/Game/AdvancedVillagePack/Meshes/SM_House_Var01.SM_House_Var01",
    "/Game/AdvancedVillagePack/Meshes/SM_House_Var02.SM_House_Var02",
]
WELL_BP = "/Game/AdvancedVillagePack/Blueprints/BP_Well"
MAT = "/Game/SoStylized/Environment/Landscape/Materials/MI_Landscape.MI_Landscape"

HEIGHTS = None
# SoStylized oaks are Z-up. -90 was laying the whole forest flat (green carpet).
OAK_PITCH = 0.0
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


def import_weight(world, landscape, layer, filename):
    path = os.path.join(WEIGHT_DIR, filename)
    if not os.path.isfile(path):
        log(f"missing {filename}")
        return
    tex = unreal.RenderingLibrary.import_file_as_texture2d(world, path)
    if not tex:
        return
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
        log(f"weight {layer} -> {ok}")
    except Exception as e:
        log(f"weight {layer} err: {e}")


def clear_junk(sub):
    n = 0
    tags = (
        "ForestTree", "ForestBush", "SatelliteIsle", "SatRock", "SwCliff",
        "DesertCliff", "DesertRock", "CaveMouth", "LakeWater", "Village_", "PlayerHouse",
    )
    kill = ("cliffclassic", "fallen", "boulderclassic", "platform", "shelf", "cubiccliff")
    for act in list(sub.get_all_level_actors()):
        label = act.get_actor_label()
        if any(label.startswith(t) for t in tags):
            sub.destroy_actor(act)
            n += 1
            continue
        if isinstance(act, unreal.StaticMeshActor):
            try:
                mn = act.static_mesh_component.static_mesh.get_name().lower()
            except Exception:
                mn = ""
            if any(k in mn for k in kill):
                sub.destroy_actor(act)
                n += 1
    log(f"Cleared {n}")


def plant_forest(sub, landscape, rng):
    oaks = [m for m in (load(p) for p in OAK_PATHS) if m]
    pines = [m for m in (load(p) for p in PINE_PATHS) if m]
    if not oaks and not pines:
        log("ERROR no trees")
        return
    step = 4
    placed = 0
    for iy in range(3, SIZE - 3, step):
        for ix in range(3, SIZE - 3, step):
            if placed >= 15000:
                break
            jx = max(1, min(SIZE - 2, ix + rng.randint(-1, 1)))
            jy = max(1, min(SIZE - 2, iy + rng.randint(-1, 1)))
            x, y, z, h = land_xyz(landscape, jx, jy)
            if h < SEA + 900:
                continue
            if h > SEA + 8500:
                continue
            # keep beach / low rim thinner
            if h < SEA + 1600 and rng.random() < 0.55:
                continue
            if rng.random() < 0.1:
                continue
            use_pine = h > SEA + 4800 and pines
            mesh = (pines if use_pine else oaks)[rng.randint(0, len(pines if use_pine else oaks) - 1)]
            pitch = PINE_PITCH if use_pine else OAK_PITCH
            act = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z - 18))
            smc = act.get_component_by_class(unreal.StaticMeshComponent)
            smc.set_static_mesh(mesh)
            smc.set_relative_rotation(unreal.Rotator(0, 0, 0), False, False)
            act.set_actor_rotation(unreal.Rotator(pitch, float(rng.uniform(0, 360)), 0.0), False)
            s = rng.uniform(1.5, 2.5)
            act.set_actor_scale3d(unreal.Vector(s, s, s))
            act.set_actor_label(f"ForestTree_{placed}")
            placed += 1
        if placed >= 15000:
            break
    log(f"Planted {placed} upright trees")


def place_village(sub, landscape):
    # Find a mid-low grassy spot near center-south
    best = None
    for iy in range(SIZE // 2, int(SIZE * 0.75), 8):
        for ix in range(int(SIZE * 0.35), int(SIZE * 0.65), 8):
            x, y, z, h = land_xyz(landscape, ix, iy)
            if SEA + 1400 < h < SEA + 3500:
                best = (x, y, z, h)
                break
        if best:
            break
    if not best:
        best = land_xyz(landscape, SIZE // 2, int(SIZE * 0.62))
    cx, cy, cz, _ = best
    cls = unreal.EditorAssetLibrary.load_blueprint_class(HOUSE_BPS[0])
    if cls:
        act = sub.spawn_actor_from_class(cls, unreal.Vector(cx, cy, cz))
        act.set_actor_rotation(unreal.Rotator(0, 180, 0), False)
        act.set_actor_label("PlayerHouse")
    else:
        mesh = load(HOUSE_MESHES[0])
        if mesh:
            act = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(cx, cy, cz))
            act.get_component_by_class(unreal.StaticMeshComponent).set_static_mesh(mesh)
            act.set_actor_label("PlayerHouse")
    for i, (ox, oy, yaw) in enumerate([(-600, -200, 40), (650, -150, -35), (-400, -700, 90), (500, -650, -80)]):
        sc = landscape.get_actor_scale3d().x
        # approx neighbor
        act = None
        ix = int(SIZE * 0.5 + ox / max(1.0, sc))
        iy = int(SIZE * 0.62 + oy / max(1.0, sc))
        ix = max(1, min(SIZE - 2, ix))
        iy = max(1, min(SIZE - 2, iy))
        x, y, z, _ = land_xyz(landscape, ix, iy)
        bp = unreal.EditorAssetLibrary.load_blueprint_class(HOUSE_BPS[i % 2])
        if bp:
            act = sub.spawn_actor_from_class(bp, unreal.Vector(x, y, z))
            act.set_actor_rotation(unreal.Rotator(0, yaw, 0), False)
            act.set_actor_label(f"Village_House_{i}")
    log("Village placed")


def fix_water(sub):
    waters = [a for a in sub.get_all_level_actors() if "Water" in a.get_class().get_name()]
    waters.sort(key=lambda a: a.get_actor_location().z)
    for i, w in enumerate(waters):
        if i == 0:
            w.set_actor_location(unreal.Vector(0, 0, 0), False, False)
        else:
            sub.destroy_actor(w)


CLIFF_PATHS = [
    "/Game/SoStylized/Environment/Rocks/Classic/SM_CliffClassic2.SM_CliffClassic2",
    "/Game/SoStylized/Environment/Rocks/Classic/SM_CliffClassic3.SM_CliffClassic3",
]


def place_coastal_cliffs(sub, landscape, rng):
    """A few upright cliff meshes on steep coastal samples — yaw only."""
    cliffs = [m for m in (load(p) for p in CLIFF_PATHS) if m]
    if not cliffs:
        return
    placed = 0
    step = 28
    for iy in range(8, SIZE - 8, step):
        for ix in range(8, SIZE - 8, step):
            if placed >= 18:
                break
            h0 = heights()[iy * SIZE + ix]
            if h0 < SEA + 1200 or h0 > SEA + 7000:
                continue
            # near water?
            near = False
            for dy in (-6, 0, 6):
                for dx in (-6, 0, 6):
                    if heights()[(iy + dy) * SIZE + (ix + dx)] < SEA + 200:
                        near = True
            if not near:
                continue
            if rng.random() < 0.55:
                continue
            x, y, z, _ = land_xyz(landscape, ix, iy)
            act = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z - 80))
            smc = act.get_component_by_class(unreal.StaticMeshComponent)
            smc.set_static_mesh(cliffs[placed % len(cliffs)])
            smc.set_relative_rotation(unreal.Rotator(0, 0, 0), False, False)
            # face roughly outward from island center
            yaw = math.degrees(math.atan2(y, x)) + 180.0
            act.set_actor_rotation(unreal.Rotator(0.0, yaw, 0.0), False)
            s = rng.uniform(2.2, 3.6)
            act.set_actor_scale3d(unreal.Vector(s, s * 0.85, s * 1.1))
            act.set_actor_label(f"SwCliff_{placed}")
            placed += 1
        if placed >= 18:
            break
    log(f"Coastal cliffs upright x{placed}")


def main():
    if not os.path.isfile(PNG_RG):
        log("Missing converted heightmap RG")
        return
    h = heights()
    log(f"UCreate import peakΔ={max(h)-SEA} oceanish={sum(1 for v in h if v < SEA)/len(h):.2f}")

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

    mat = load(MAT)
    if mat:
        landscape.set_editor_property("landscape_material", mat)

    for layer, fn in (
        ("Grass", "Island_Weight_Grass.png"),
        ("Sand", "Island_Weight_Sand.png"),
        ("Rock", "Island_Weight_Rock.png"),
        ("Dirt", "Island_Weight_Dirt.png"),
    ):
        import_weight(world, landscape, layer, fn)
    try:
        landscape.force_layers_full_update()
    except Exception:
        pass

    clear_junk(sub)
    plant_forest(sub, landscape, random.Random(11))
    place_coastal_cliffs(sub, landscape, random.Random(11))
    place_village(sub, landscape)
    fix_water(sub)

    # PlayerStart on village-ish area
    x, y, z, _ = land_xyz(landscape, SIZE // 2, int(SIZE * 0.65))
    for act in sub.get_all_level_actors():
        if isinstance(act, unreal.PlayerStart):
            act.set_actor_location(unreal.Vector(x, y, z + 120), False, False)

    ntrees = sum(1 for a in sub.get_all_level_actors() if a.get_actor_label().startswith("ForestTree"))
    o, e = landscape.get_actor_bounds(False, False)
    log(f"FINAL Z {o.z-e.z:.0f}..{o.z+e.z:.0f} trees={ntrees}")
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    try:
        unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    except Exception:
        pass
    log("SAVED UCreate tropical island import")
    with open(RESULT, "w", encoding="utf-8") as f:
        f.write("\n".join(OUT))


if __name__ == "__main__":
    main()
