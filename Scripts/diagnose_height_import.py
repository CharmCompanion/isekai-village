"""Diagnose why landscape height import doesn't change bounds."""
import unreal

MAP = "/Game/SpellCraft/Maps/Height_DemoCopy"
TEX_PATH = "/Game/SpellCraft/Textures/Island_Heightmap_1009_RG"
SIZE = 1009
OUT = []


def log(msg):
    OUT.append(str(msg))
    unreal.log(msg)


def main():
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    landscape = next(
        a
        for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
        if isinstance(a, unreal.Landscape)
    )

    # Probe edit-layer related props/methods
    for name in sorted(dir(landscape)):
        if "layer" in name.lower() or "edit" in name.lower():
            OUT.append(f"landscape.{name}")

    # Try reading editor properties that might exist
    for prop in [
        "landscape_layers",
        "landscape_edit_layers",
        "edit_layers",
        "can_have_layers_content",
        "b_can_have_layers_content",
    ]:
        try:
            val = landscape.get_editor_property(prop)
            log(f"prop {prop}={val}")
        except Exception as e:
            log(f"prop {prop} err: {e}")

    tex = unreal.EditorAssetLibrary.load_asset(TEX_PATH)
    log(f"tex={tex} srgb={tex.get_editor_property('srgb') if tex else None}")

    rt = unreal.RenderingLibrary.create_render_target2d(
        world, SIZE, SIZE, unreal.TextureRenderTargetFormat.RTF_RGBA8
    )
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

    # Sample a few pixels from RT
    for x, y, label in [(10, 10, "corner"), (504, 504, "center"), (800, 800, "NE-ish")]:
        c = unreal.RenderingLibrary.read_render_target_pixel(world, rt, x, y)
        # Color is BGRA 0-255
        log(f"RT {label} ({x},{y}) = {c}")
        raw = unreal.RenderingLibrary.read_render_target_raw_pixel(world, rt, x, y, True)
        log(f"RT raw {label} = {raw}")

    # Try import on several edit layer indices
    origin, extent = landscape.get_actor_bounds(False, False)
    log(f"bounds before any import: z={origin.z - extent.z}..{origin.z + extent.z}")

    for layer_i in range(0, 5):
        try:
            ok = landscape.landscape_import_heightmap_from_render_target(rt, True, layer_i)
            origin, extent = landscape.get_actor_bounds(False, False)
            log(
                f"import layer={layer_i} -> {ok}; z={origin.z - extent.z:.1f}..{origin.z + extent.z:.1f}"
            )
        except Exception as e:
            log(f"import layer={layer_i} err: {e}")

    # Also try RG=False
    ok = landscape.landscape_import_heightmap_from_render_target(rt, False, 0)
    origin, extent = landscape.get_actor_bounds(False, False)
    log(f"import RG=False -> {ok}; z={origin.z - extent.z:.1f}..{origin.z + extent.z:.1f}")

    path = "F:/DEVELOPMENT/Games/SpellCraft/Saved/Logs/diagnose_height_import.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(OUT))


if __name__ == "__main__":
    main()
