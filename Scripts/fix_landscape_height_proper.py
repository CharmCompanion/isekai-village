"""
Fix Height_DemoCopy properly:
1) Import island heightmap via linear (non-sRGB) RG texture
2) Delete leftover cliff/tree StaticMeshActors
3) Raise landscape so its surface sits above the ocean (Z=0)
4) Save

CLOSE THE EDITOR before running.
"""
import os
import struct
import unreal

MAP = "/Game/SpellCraft/Maps/Height_DemoCopy"
PNG_RG = "F:/DEVELOPMENT/Games/SpellCraft/Content/SpellCraft/Textures/Island_Heightmap_1009_RG.png"
R16 = "F:/DEVELOPMENT/Games/SpellCraft/Content/SpellCraft/Textures/Island_Heightmap_1009.r16"
TEX_PATH = "/Game/SpellCraft/Textures/Island_Heightmap_1009_RG"
SIZE = 1009
RESULT = "F:/DEVELOPMENT/Games/SpellCraft/Saved/Logs/fix_landscape_height_proper_result.txt"

OUT = []


def log(msg):
    OUT.append(str(msg))
    unreal.log(msg)
    print(msg)


def get_landscape():
    for act in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        if isinstance(act, unreal.Landscape):
            return act
    return None


def import_rg_texture_linear():
    if unreal.EditorAssetLibrary.does_asset_exist(TEX_PATH):
        unreal.EditorAssetLibrary.delete_asset(TEX_PATH)

    task = unreal.AssetImportTask()
    task.filename = PNG_RG
    task.destination_path = "/Game/SpellCraft/Textures"
    task.destination_name = "Island_Heightmap_1009_RG"
    task.replace_existing = True
    task.automated = True
    task.save = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

    tex = unreal.EditorAssetLibrary.load_asset(TEX_PATH)
    if not tex:
        log("ERROR: texture import failed")
        return None

    # Critical: do not sRGB-mangle height encoding
    tex.set_editor_property("srgb", False)
    try:
        tex.set_editor_property(
            "compression_settings",
            unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP,
        )
    except Exception:
        pass
    try:
        tex.set_editor_property(
            "mip_gen_settings",
            unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS,
        )
    except Exception:
        pass
    unreal.EditorAssetLibrary.save_asset(TEX_PATH, only_if_is_dirty=False)
    log(f"Imported linear height tex {TEX_PATH}")
    return tex


def apply_height(landscape, tex):
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    rt = unreal.RenderingLibrary.create_render_target2d(
        world, SIZE, SIZE, unreal.TextureRenderTargetFormat.RTF_RGBA8
    )
    canvas, _, ctx = unreal.RenderingLibrary.begin_draw_canvas_to_render_target(world, rt)
    if not canvas:
        log("ERROR: canvas failed — need -AllowCommandletRendering")
        return False
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
    ok = landscape.landscape_import_heightmap_from_render_target(rt, True, 0)
    log(f"height import -> {ok}")
    return ok


def landscape_z_range(landscape):
    origin, extent = landscape.get_actor_bounds(False, False)
    zmin = origin.z - extent.z
    zmax = origin.z + extent.z
    return zmin, zmax, origin, extent


def raise_landscape_above_water(landscape, target_max_z=3500.0):
    zmin, zmax, origin, extent = landscape_z_range(landscape)
    log(f"Landscape Z before raise: {zmin:.1f} .. {zmax:.1f} (actor z={landscape.get_actor_location().z})")
    # Want the high land near target_max_z; keep ocean floor below 0 if possible
    delta = target_max_z - zmax
    loc = landscape.get_actor_location()
    new_z = loc.z + delta
    landscape.set_actor_location(unreal.Vector(loc.x, loc.y, new_z), False, False)
    zmin2, zmax2, _, _ = landscape_z_range(landscape)
    log(f"Raised actor Z by {delta:.1f} -> actor z={new_z:.1f}; surface now {zmin2:.1f} .. {zmax2:.1f}")
    return new_z


def delete_all_static_meshes():
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    removed = 0
    for act in list(sub.get_all_level_actors()):
        if isinstance(act, unreal.StaticMeshActor) or "Foliage" in act.get_class().get_name():
            sub.destroy_actor(act)
            removed += 1
    log(f"Deleted {removed} StaticMesh/Foliage actors (floating cliffs/trees)")


def move_player(landscape_z):
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    # SW beach-ish spawn, above expected land
    loc = unreal.Vector(-22000.0, -24000.0, max(800.0, landscape_z * 0.15 + 500.0))
    for act in sub.get_all_level_actors():
        if isinstance(act, unreal.PlayerStart):
            act.set_actor_location(loc, False, False)
            act.set_actor_rotation(unreal.Rotator(0, 45, 0), False)
            log(f"PlayerStart -> {loc}")
            return


def sample_r16_stats():
    if not os.path.isfile(R16):
        return
    with open(R16, "rb") as f:
        data = f.read()
    n = SIZE * SIZE
    heights = struct.unpack(f"<{n}H", data)
    log(f"Source r16 min={min(heights)} max={max(heights)} avg={sum(heights)/n:.1f}")


def main():
    if not os.path.isfile(PNG_RG):
        log(f"ERROR: missing {PNG_RG} — run create_island_heightmap_v2.py")
        return

    sample_r16_stats()
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
    landscape = get_landscape()
    if not landscape:
        log("ERROR: no landscape")
        return

    zmin, zmax, _, _ = landscape_z_range(landscape)
    log(f"BEFORE: landscape surface Z {zmin:.1f} .. {zmax:.1f}")

    tex = import_rg_texture_linear()
    if not tex:
        return
    apply_height(landscape, tex)

    zmin, zmax, _, _ = landscape_z_range(landscape)
    log(f"AFTER IMPORT: landscape surface Z {zmin:.1f} .. {zmax:.1f}")

    delete_all_static_meshes()
    actor_z = raise_landscape_above_water(landscape, target_max_z=4500.0)
    move_player(actor_z)

    zmin, zmax, _, _ = landscape_z_range(landscape)
    log(f"FINAL: landscape surface Z {zmin:.1f} .. {zmax:.1f}")

    # Keep only ocean water at 0
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    waters = [a for a in sub.get_all_level_actors() if a.get_class().get_name() == "BP_Water_C"]
    waters.sort(key=lambda a: a.get_actor_location().z)
    for i, w in enumerate(waters):
        if i == 0:
            w.set_actor_location(unreal.Vector(0, 0, 0), False, False)
            log(f"Keep ocean {w.get_name()}")
        else:
            sub.destroy_actor(w)
            log(f"Removed extra water {w.get_name()}")

    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    try:
        unreal.EditorAssetLibrary.save_directory("/Game/SpellCraft/Maps", True, True)
    except Exception as e:
        log(f"save_directory: {e}")

    log("SUCCESS — fully close editor if open, then open Height_DemoCopy fresh.")
    with open(RESULT, "w", encoding="utf-8") as f:
        f.write("\n".join(OUT))


if __name__ == "__main__":
    main()
