"""
Fix Height_DemoCopy: make island heightmap actually stick, raise above water,
purge floating cliff SMAs.

CLOSE Unreal Editor before running.
Needs: -AllowCommandletRendering
"""
import os
import struct
import unreal

MAP = "/Game/SpellCraft/Maps/Height_DemoCopy"
PNG_RG = "F:/DEVELOPMENT/Games/SpellCraft/Content/SpellCraft/Textures/Island_Heightmap_1009_RG.png"
R16 = "F:/DEVELOPMENT/Games/SpellCraft/Content/SpellCraft/Textures/Island_Heightmap_1009.r16"
SIZE = 1009
RESULT = "F:/DEVELOPMENT/Games/SpellCraft/Saved/Logs/fix_height_import_v3.txt"
OUT = []


def log(msg):
    OUT.append(str(msg))
    unreal.log(msg)


def landscape_z(landscape):
    o, e = landscape.get_actor_bounds(False, False)
    return o.z - e.z, o.z + e.z


def export_heights(world, landscape, rt):
    for args in [(rt, True, False), (rt, True, True), (rt, True), (rt, False)]:
        try:
            if landscape.landscape_export_heightmap_to_render_target(*args):
                break
        except TypeError:
            continue
    else:
        return None
    pixels = unreal.RenderingLibrary.read_render_target_raw_pixel_area(
        world, rt, 0, 0, SIZE, SIZE, True
    )
    if not pixels:
        return None
    heights = []
    for c in pixels:
        # LinearColor 0..1 for RTF_RGBA8 export path
        r = int(round(min(max(c.r, 0.0), 1.0) * 255.0))
        g = int(round(min(max(c.g, 0.0), 1.0) * 255.0))
        # Also handle 0..255 mistaken linear reads
        if c.r > 1.5 or c.g > 1.5:
            r = int(round(min(max(c.r, 0.0), 255.0)))
            g = int(round(min(max(c.g, 0.0), 255.0)))
        heights.append((r << 8) | g)
    return heights


def quadrant_summary(heights, label):
    if not heights:
        return f"{label}: none"
    mid = SIZE // 2
    sw, ne = [], []
    for j in range(SIZE):
        for i in range(SIZE):
            h = heights[j * SIZE + i]
            if i < mid and j < mid:
                sw.append(h)
            elif i >= mid and j >= mid:
                ne.append(h)
    return (
        f"{label}: all[{min(heights)}..{max(heights)} avg={sum(heights)/len(heights):.0f}] "
        f"SW[{min(sw)}..{max(sw)}] NE[{min(ne)}..{max(ne)}]"
    )


def sample_rt(world, rt, tag):
    for x, y, name in [(10, 10, "corner"), (504, 504, "center"), (800, 800, "NE")]:
        c = unreal.RenderingLibrary.read_render_target_pixel(world, rt, x, y)
        raw = unreal.RenderingLibrary.read_render_target_raw_pixel(world, rt, x, y, True)
        log(f"  {tag} {name}: Color={c} Raw={raw}")


def fill_rt_from_r16(world, rt):
    """Paint heightmap into RT via canvas colored rects in strips (RG encoded)."""
    with open(R16, "rb") as f:
        data = f.read()
    n = SIZE * SIZE
    heights = struct.unpack(f"<{n}H", data)

    # Clear
    canvas, _, ctx = unreal.RenderingLibrary.begin_draw_canvas_to_render_target(world, rt)
    canvas.draw_box(
        unreal.Vector2D(0, 0),
        unreal.Vector2D(SIZE, SIZE),
        1.0,
        unreal.LinearColor(0, 0, 0, 1),
    )
    unreal.RenderingLibrary.end_draw_canvas_to_render_target(world, ctx)

    # Draw row-by-row as 1px-tall boxes — too slow for 1009 rows with per-pixel.
    # Instead: pack into a transient Texture2D via import_file_as_texture2d (PNG).
    tex = unreal.RenderingLibrary.import_file_as_texture2d(world, PNG_RG)
    log(f"import_file_as_texture2d -> {tex}")
    if not tex:
        return False
    try:
        tex.set_editor_property("srgb", False)
    except Exception:
        pass

    canvas, _, ctx = unreal.RenderingLibrary.begin_draw_canvas_to_render_target(world, rt)
    canvas.draw_texture(
        tex,
        unreal.Vector2D(0, 0),
        unreal.Vector2D(SIZE, SIZE),
        unreal.Vector2D(0, 0),
        unreal.Vector2D(1, 1),
        unreal.LinearColor(1, 1, 1, 1),
        unreal.BlendMode.BLEND_OPAQUE,
    )
    unreal.RenderingLibrary.end_draw_canvas_to_render_target(world, ctx)
    sample_rt(world, rt, "after_draw_png")

    # If still white/black, fall back to strip painting every N pixels (coarse test)
    c = unreal.RenderingLibrary.read_render_target_pixel(world, rt, 504, 504)
    # Color struct uses 0-255 channels
    looks_blank = False
    try:
        looks_blank = (c.r > 250 and c.g > 250) or (c.r < 5 and c.g < 5)
    except Exception:
        pass

    if looks_blank:
        log("draw_texture looks blank — painting coarse RG strips from r16")
        canvas, _, ctx = unreal.RenderingLibrary.begin_draw_canvas_to_render_target(world, rt)
        step = 4  # 4x4 blocks for speed
        for j in range(0, SIZE, step):
            for i in range(0, SIZE, step):
                h = heights[j * SIZE + i]
                r = (h >> 8) / 255.0
                g = (h & 0xFF) / 255.0
                canvas.draw_box(
                    unreal.Vector2D(float(i), float(j)),
                    unreal.Vector2D(float(min(step, SIZE - i)), float(min(step, SIZE - j))),
                    1.0,
                    unreal.LinearColor(r, g, 0.0, 1.0),
                )
        unreal.RenderingLibrary.end_draw_canvas_to_render_target(world, ctx)
        sample_rt(world, rt, "after_strip_paint")
    return True


def try_import(landscape, rt):
    # Probe edit layers
    try:
        layers = landscape.get_edit_layers_bp()
        log(f"get_edit_layers_bp -> {layers}")
    except Exception as e:
        log(f"get_edit_layers_bp err: {e}")

    results = []
    for layer_i in [0, 1]:
        for rg in [True, False]:
            try:
                ok = landscape.landscape_import_heightmap_from_render_target(rt, rg, layer_i)
                results.append((layer_i, rg, ok))
                log(f"import layer={layer_i} rg={rg} -> {ok}")
            except Exception as e:
                log(f"import layer={layer_i} rg={rg} err: {e}")
    try:
        landscape.force_layers_full_update()
        log("force_layers_full_update ok")
    except Exception as e:
        log(f"force_layers_full_update err: {e}")
    return results


def delete_floating_props():
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    removed = 0
    for act in list(sub.get_all_level_actors()):
        cls = act.get_class().get_name()
        if isinstance(act, unreal.StaticMeshActor) or "Foliage" in cls:
            sub.destroy_actor(act)
            removed += 1
    log(f"Deleted {removed} StaticMesh/Foliage actors")


def raise_above_water(landscape, target_max_z=4500.0):
    zmin, zmax = landscape_z(landscape)
    loc = landscape.get_actor_location()
    delta = target_max_z - zmax
    new_z = loc.z + delta
    landscape.set_actor_location(unreal.Vector(loc.x, loc.y, new_z), False, False)
    zmin2, zmax2 = landscape_z(landscape)
    log(f"Raised actor {loc.z:.1f}->{new_z:.1f}; surface {zmin2:.1f}..{zmax2:.1f}")


def fix_water():
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    waters = [a for a in sub.get_all_level_actors() if "Water" in a.get_class().get_name()]
    waters.sort(key=lambda a: a.get_actor_location().z)
    for i, w in enumerate(waters):
        if i == 0:
            w.set_actor_location(unreal.Vector(0, 0, 0), False, False)
            try:
                w.set_editor_property("water_depth", 2000.0)
            except Exception:
                pass
            log(f"Keep water {w.get_name()} at Z=0")
        else:
            sub.destroy_actor(w)
            log(f"Removed extra water {w.get_name()}")


def main():
    if not os.path.isfile(PNG_RG) or not os.path.isfile(R16):
        log("ERROR: missing heightmap files")
        return

    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    landscape = next(
        a
        for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
        if isinstance(a, unreal.Landscape)
    )

    zmin, zmax = landscape_z(landscape)
    log(f"BEFORE bounds Z {zmin:.1f}..{zmax:.1f} actorZ={landscape.get_actor_location().z}")

    rt_export = unreal.RenderingLibrary.create_render_target2d(
        world, SIZE, SIZE, unreal.TextureRenderTargetFormat.RTF_RGBA8
    )
    before = export_heights(world, landscape, rt_export)
    if before:
        log(quadrant_summary(before, "BEFORE export"))
    else:
        log("BEFORE export failed")

    rt = unreal.RenderingLibrary.create_render_target2d(
        world, SIZE, SIZE, unreal.TextureRenderTargetFormat.RTF_RGBA8
    )
    fill_rt_from_r16(world, rt)
    try_import(landscape, rt)

    after = export_heights(world, landscape, rt_export)
    if after:
        log(quadrant_summary(after, "AFTER export"))
        changed = before and after and (before != after)
        log(f"Height data changed after import: {changed}")
        if before and after:
            diffs = sum(1 for a, b in zip(before, after) if a != b)
            log(f"Pixels different: {diffs}/{len(after)}")
    else:
        log("AFTER export failed")

    zmin, zmax = landscape_z(landscape)
    log(f"AFTER IMPORT bounds Z {zmin:.1f}..{zmax:.1f}")

    delete_floating_props()
    raise_above_water(landscape, 4500.0)
    fix_water()

    # PlayerStart on SW beach
    for act in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        if isinstance(act, unreal.PlayerStart):
            act.set_actor_location(unreal.Vector(-22000, -24000, 1200), False, False)
            break

    zmin, zmax = landscape_z(landscape)
    log(f"FINAL bounds Z {zmin:.1f}..{zmax:.1f}")

    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    try:
        unreal.EditorAssetLibrary.save_directory("/Game/SpellCraft/Maps", True, True)
    except Exception as e:
        log(f"save_directory: {e}")

    log("DONE — close editor fully, reopen Height_DemoCopy.")
    with open(RESULT, "w", encoding="utf-8") as f:
        f.write("\n".join(OUT))


if __name__ == "__main__":
    main()
