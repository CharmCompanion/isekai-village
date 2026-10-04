"""
Import Gaea SpellCraft tropical island exports into Height_DemoCopy.

Expects exports in:
  F:/DEVELOPMENT/Games/SpellCraft/Gaea/SpellCraft_TropicalIsland/Export/

Looks for (any match):
  H_*.png / *height*.png / *Island*.png / *.r16
  T_Grass*, T_Sand* or T_Beach*, T_Rock*, T_Dirt*

CLOSE EDITOR. Needs -AllowCommandletRendering.
"""
import glob
import os
import random
import struct
import unreal

MAP = "/Game/SpellCraft/Maps/Height_DemoCopy"
EXPORT = "F:/DEVELOPMENT/Games/SpellCraft/Gaea/SpellCraft_TropicalIsland/Export"
SIZE = 1009
SEA = 32768
SCALE_Z = 155.0
RESULT = "F:/DEVELOPMENT/Games/SpellCraft/Saved/Logs/import_gaea_island_v1.txt"
OUT = []

ASSETS = {
    "landscape_mat": "/Game/SoStylized/Environment/Landscape/Materials/MI_Landscape.MI_Landscape",
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
OAK_PITCH = -90.0
PINE_PITCH = 0.0


def log(msg):
    OUT.append(str(msg))
    unreal.log(msg)


def find_file(patterns):
    for pat in patterns:
        hits = sorted(glob.glob(os.path.join(EXPORT, pat)))
        if hits:
            return hits[0]
    return None


def import_rt(world, path, size=SIZE):
    tex = unreal.RenderingLibrary.import_file_as_texture2d(world, path)
    if not tex:
        return None
    try:
        tex.set_editor_property("srgb", False)
    except Exception:
        pass
    rt = unreal.RenderingLibrary.create_render_target2d(
        world, size, size, unreal.TextureRenderTargetFormat.RTF_RGBA8
    )
    canvas, _, ctx = unreal.RenderingLibrary.begin_draw_canvas_to_render_target(world, rt)
    canvas.draw_texture(
        tex, unreal.Vector2D(0, 0), unreal.Vector2D(size, size),
        unreal.Vector2D(0, 0), unreal.Vector2D(1, 1),
        unreal.LinearColor(1, 1, 1, 1), unreal.BlendMode.BLEND_OPAQUE,
    )
    unreal.RenderingLibrary.end_draw_canvas_to_render_target(world, ctx)
    return rt


def clear_props(sub):
    n = 0
    tags = (
        "ForestTree", "ForestBush", "SatelliteIsle", "SatRock", "SwCliff",
        "DesertCliff", "DesertRock", "CaveMouth", "LakeWater", "Village_", "PlayerHouse",
    )
    kill = ("cliffclassic", "fallen", "boulderclassic", "platform", "shelf")
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


def plant(sub, landscape, rng):
    oaks = [unreal.EditorAssetLibrary.load_asset(p) for p in OAK_PATHS]
    pines = [unreal.EditorAssetLibrary.load_asset(p) for p in PINE_PATHS]
    oaks = [m for m in oaks if m]
    pines = [m for m in pines if m]
    loc = landscape.get_actor_location()
    sc = landscape.get_actor_scale3d()
    # Approximate: plant on a grid; skip deep water by Z heuristic after import
    step = 4
    placed = 0
    for iy in range(4, SIZE - 4, step):
        for ix in range(4, SIZE - 4, step):
            if placed >= 14000:
                break
            jx = max(1, min(SIZE - 2, ix + rng.randint(-1, 1)))
            jy = max(1, min(SIZE - 2, iy + rng.randint(-1, 1)))
            x = loc.x + jx * sc.x
            y = loc.y + jy * sc.y
            # Sample height via line trace if possible; else place slightly above water
            z = 200.0
            hit = unreal.SystemLibrary.line_trace_single(
                unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(),
                unreal.Vector(x, y, 50000),
                unreal.Vector(x, y, -50000),
                unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
                False,
                [],
                unreal.DrawDebugTrace.NONE,
                True,
            )
            if hit and hit.get("blocking_hit", False if isinstance(hit, dict) else False):
                # API varies — try actor hit location
                try:
                    z = hit.to_tuple()[0].location.z if hasattr(hit, "to_tuple") else 200
                except Exception:
                    try:
                        z = hit["location"].z
                    except Exception:
                        z = 200
            else:
                # Fallback: skip edges (likely ocean)
                if jx < 40 or jy < 40 or jx > SIZE - 40 or jy > SIZE - 40:
                    if rng.random() < 0.7:
                        continue
            if z < 80:
                continue
            if rng.random() < 0.12:
                continue
            use_pine = z > 2500 and pines
            mesh = (pines if use_pine else oaks)[rng.randint(0, len(pines if use_pine else oaks) - 1)]
            pitch = PINE_PITCH if use_pine else OAK_PITCH
            act = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z - 18))
            smc = act.get_component_by_class(unreal.StaticMeshComponent)
            smc.set_static_mesh(mesh)
            smc.set_relative_rotation(unreal.Rotator(0, 0, 0), False, False)
            act.set_actor_rotation(unreal.Rotator(pitch, float(rng.uniform(0, 360)), 0), False)
            s = rng.uniform(1.5, 2.5)
            act.set_actor_scale3d(unreal.Vector(s, s, s))
            act.set_actor_label(f"ForestTree_{placed}")
            placed += 1
        if placed >= 14000:
            break
    log(f"Planted {placed} trees")


def main():
    if not os.path.isdir(EXPORT):
        log(f"Missing export folder: {EXPORT}")
        log("Build the Gaea graph first — see RECIPE.md")
        with open(RESULT, "w", encoding="utf-8") as f:
            f.write("\n".join(OUT))
        return

    height = find_file([
        "H_*.png", "H_*.r16", "*height*.png", "*Height*.png",
        "*Island*.png", "*Final*.png", "*.r16",
    ])
    if not height:
        log("No heightmap found in Export/. Mark height for export in Gaea and Build.")
        with open(RESULT, "w", encoding="utf-8") as f:
            f.write("\n".join(OUT))
        return
    log(f"Height: {height}")

    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    landscape = next(a for a in sub.get_all_level_actors() if isinstance(a, unreal.Landscape))

    rt = import_rt(world, height)
    if not rt:
        log("Failed to load height into RT")
        return
    # Prefer RG for 16-bit style; Gaea PNG-16 often works as R-only
    ok = landscape.landscape_import_heightmap_from_render_target(rt, True, 0)
    if not ok:
        ok = landscape.landscape_import_heightmap_from_render_target(rt, False, 0)
    log(f"height import -> {ok}")

    loc = landscape.get_actor_location()
    sc = landscape.get_actor_scale3d()
    landscape.set_actor_location(unreal.Vector(loc.x, loc.y, 0.0), False, False)
    landscape.set_actor_scale3d(unreal.Vector(sc.x, sc.y, SCALE_Z))

    mat = unreal.EditorAssetLibrary.load_asset(ASSETS["landscape_mat"])
    if mat:
        landscape.set_editor_property("landscape_material", mat)

    # Weight maps
    for layer, pats in (
        ("Grass", ["T_Grass*", "*Grass*", "*ground*", "*slope*"]),
        ("Sand", ["T_Beach*", "T_Sand*", "*Beach*", "*Sand*"]),
        ("Rock", ["T_Rock*", "*Rock*", "*Cliff*"]),
        ("Dirt", ["T_Flow*", "*Flow*", "*Dirt*"]),
    ):
        path = find_file(pats)
        if not path:
            log(f"skip weight {layer}")
            continue
        wrt = import_rt(world, path)
        if not wrt:
            continue
        try:
            wok = landscape.landscape_import_weightmap_from_render_target(wrt, layer)
            log(f"weight {layer} from {os.path.basename(path)} -> {wok}")
        except Exception as e:
            log(f"weight {layer} err: {e}")

    try:
        landscape.force_layers_full_update()
    except Exception:
        pass

    clear_props(sub)
    plant(sub, landscape, random.Random(99))

    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    try:
        unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    except Exception:
        pass
    log("SAVED Gaea import v1")
    with open(RESULT, "w", encoding="utf-8") as f:
        f.write("\n".join(OUT))


if __name__ == "__main__":
    main()
