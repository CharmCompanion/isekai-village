"""
Import Gaea/Tropical Island FO.png height + masks into Height_DemoCopy.
Applies SoStylized landscape material. Does NOT change default play map (graybox stays).

Close Unreal first.
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
# FO.png: ocean ~0, peaks ~65535 (normalized Gaea export)
SEA = 800
SCALE_Z = 200.0
MAT = "/Game/SoStylized/Environment/Landscape/Materials/MI_Landscape.MI_Landscape"
RESULT = "F:/DEVELOPMENT/Games/SpellCraft/Saved/Logs/import_tropical_fo.txt"
OUT = []
HEIGHTS = None

OAK_PATHS = [
    "/Game/SoStylized/Environment/Trees/Oak/SM_OakTree1.SM_OakTree1",
    "/Game/SoStylized/Environment/Trees/Oak/SM_OakTree2.SM_OakTree2",
    "/Game/SoStylized/Environment/Trees/Oak/SM_OakTree3.SM_OakTree3",
]


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


def clear_props(sub):
    n = 0
    tags = (
        "ForestTree", "ForestBush", "SatelliteIsle", "SatRock", "SwCliff",
        "DesertCliff", "DesertRock", "Village_", "PlayerHouse",
    )
    for act in list(sub.get_all_level_actors()):
        label = act.get_actor_label()
        if any(label.startswith(t) for t in tags):
            sub.destroy_actor(act)
            n += 1
    log(f"Cleared {n} old props")


def plant_light(sub, landscape, rng):
    oaks = [m for m in (load(p) for p in OAK_PATHS) if m]
    if not oaks:
        log("no oaks")
        return
    placed = 0
    step = 8
    for iy in range(4, SIZE - 4, step):
        for ix in range(4, SIZE - 4, step):
            if placed >= 4000:
                break
            h = heights()[iy * SIZE + ix]
            if h < SEA + 2500 or h > 50000:
                continue
            if rng.random() < 0.35:
                continue
            x, y, z, _ = land_xyz(landscape, ix, iy)
            act = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z - 18))
            smc = act.get_component_by_class(unreal.StaticMeshComponent)
            smc.set_static_mesh(oaks[rng.randint(0, len(oaks) - 1)])
            act.set_actor_rotation(unreal.Rotator(0, rng.uniform(0, 360), 0), False)
            s = rng.uniform(0.85, 1.35)
            act.set_actor_scale3d(unreal.Vector(s, s, s))
            act.set_actor_label(f"ForestTree_{placed}")
            placed += 1
        if placed >= 4000:
            break
    log(f"Trees {placed}")


def main():
    if not os.path.isfile(PNG_RG) or not os.path.isfile(R16):
        log("Missing FO converted textures — run convert first")
        return
    h = heights()
    ocean = sum(1 for v in h if v < SEA) / len(h)
    log(f"FO peak={max(h)} ocean_frac={ocean:.2f}")

    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    les.load_level(MAP)
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    world = unreal.EditorLevelLibrary.get_editor_world()

    landscape = None
    for act in sub.get_all_level_actors():
        if "Landscape" in act.get_class().get_name() and "Streaming" not in act.get_class().get_name():
            landscape = act
            break
    if not landscape:
        log("ERROR no landscape")
        return

    try:
        landscape.set_actor_scale3d(unreal.Vector(100.0, 100.0, SCALE_Z))
    except Exception as e:
        log(f"scale warn {e}")

    mat = load(MAT)
    if mat:
        try:
            landscape.set_landscape_material(mat)
            log(f"SoStylized mat -> {MAT}")
        except Exception as e:
            log(f"mat err {e}")

    apply_height(world, landscape)
    # Weight layers only if landscape already has Layer Infos (SoStylized paint layers)
    for layer, file in (
        ("Sand", "Island_Weight_Sand.png"),
        ("Grass", "Island_Weight_Grass.png"),
        ("Rock", "Island_Weight_Rock.png"),
        ("Dirt", "Island_Weight_Dirt.png"),
    ):
        try:
            import_weight(world, landscape, layer, file)
        except Exception as e:
            log(f"skip weight {layer}: {e}")

    clear_props(sub)
    try:
        plant_light(sub, landscape, random.Random(42))
    except Exception as e:
        log(f"plant err {e}")

    # PlayerStart on land
    for act in list(sub.get_all_level_actors()):
        if act.get_class().get_name() == "PlayerStart":
            # mid-south land sample
            x, y, z, _ = land_xyz(landscape, SIZE // 2, int(SIZE * 0.72))
            act.set_actor_location(unreal.Vector(x, y, z + 120), False, False)
            log("PlayerStart moved")
            break

    les.save_current_level()
    log("IMPORT_FO_OK")
    os.makedirs(os.path.dirname(RESULT), exist_ok=True)
    with open(RESULT, "w", encoding="utf-8") as f:
        f.write("\n".join(OUT))


if __name__ == "__main__":
    main()
