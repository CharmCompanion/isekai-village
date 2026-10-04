"""
Export current landscape heightmap to a render target and print quadrant stats.

Used to diagnose "island is below water / mountains appear wrong" after the
procedural reshape.

Run:
  UnrealEditor-Cmd.exe <uproject> -run=pythonscript -script="...\\debug_landscape_height_quadrants.py" -AllowCommandletRendering -stdout -unattended -nosplash
"""

import struct
import unreal

MAP = "/Game/SpellCraft/Maps/Height_DemoCopy"
HEIGHT_RT_FORMAT = unreal.TextureRenderTargetFormat.RTF_RGBA8


def get_landscape():
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for act in sub.get_all_level_actors():
        if isinstance(act, unreal.Landscape):
            return act
    return None


def decode_rgba8_height_bytes_to_u16(r, g):
    # Mirror the engine packing used by LandscapeImportHeightmapFromRenderTarget
    # when InImportHeightFromRGChannel == True:
    #   Height = ((Color.R << 8) | Color.G)
    return (int(round(r * 255)) << 8) | int(round(g * 255))


def quadrant_stats(values, label):
    if not values:
        return f"{label}: empty"
    mn = min(values)
    mx = max(values)
    avg = sum(values) / len(values)
    return f"{label}: count={len(values)} min={mn} max={mx} avg={avg:.1f}"


def main():
    out_lines = []
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    landscape = get_landscape()
    out_lines.append(f"Landscape: {landscape}")

    if not landscape:
        return

    # Hardcode expected heightmap dimension for this project.
    SIZE = 1009
    rt = unreal.RenderingLibrary.create_render_target2d(world, SIZE, SIZE, HEIGHT_RT_FORMAT)
    if not rt:
        out_lines.append("Failed to create render target.")
        return

    export_fn = unreal.Landscape.landscape_export_heightmap_to_render_target
    out_lines.append(f"export fn: {export_fn}")
    try:
        out_lines.append(f"export text signature: {getattr(export_fn, '__text_signature__', '')}")
        out_lines.append(f"export doc: {getattr(export_fn, '__doc__', '')}")
    except Exception:
        pass

    exported = False
    # Try the most likely argument ordering variants.
    for args in [
        (rt, True, True),
        (rt, True, False),
        (rt, False, True),
        (rt, False, False),
        (rt, True),
        (rt, False),
        (rt,),
    ]:
        try:
            exported = landscape.landscape_export_heightmap_to_render_target(*args)
            print(f"export call {args} -> {exported}")
            if exported:
                break
        except TypeError:
            continue

    if not exported:
        out_lines.append("Export failed (couldn't match signature).")
        return

    # Read all pixels from render target and compute quadrant stats.
    # RTF_RGBA8 export should pack height into R/G.
    size_x = rt.get_editor_property("size_x")
    size_y = rt.get_editor_property("size_y")
    # read_render_target_raw_pixel_area uses a half-open interval:
    #   output size ~= (max_x - min_x) * (max_y - min_y)
    # so we want a full SIZE x SIZE read => max_* should be SIZE (not SIZE-1).
    max_x = int(size_x)
    max_y = int(size_y)
    pixels = unreal.RenderingLibrary.read_render_target_raw_pixel_area(
        world, rt, 0, 0, max_x, max_y, True
    )
    out_lines.append(f"Read pixels: len={len(pixels)} size={size_x}x{size_y}")

    # Quadrants in heightmap tex coords:
    # SW: x<0.5, y<0.5  (front-left)
    # NE: x>=0.5, y>=0.5
    mid_x = int(size_x) // 2
    mid_y = int(size_y) // 2
    sw = []
    ne = []
    se = []
    nw = []

    for j in range(int(size_y)):
        for i in range(int(size_x)):
            idx = j * int(size_x) + i
            c = pixels[idx]
            h = decode_rgba8_height_bytes_to_u16(c.r, c.g)
            if i < mid_x and j < mid_y:
                sw.append(h)
            elif i >= mid_x and j >= mid_y:
                ne.append(h)
            elif i >= mid_x and j < mid_y:
                se.append(h)
            else:
                nw.append(h)

    out_lines.append(quadrant_stats(sw, "SW (front-left)"))
    out_lines.append(quadrant_stats(ne, "NE (back-right)"))
    out_lines.append(quadrant_stats(se, "SE"))
    out_lines.append(quadrant_stats(nw, "NW"))

    with open("F:/DEVELOPMENT/Games/SpellCraft/Saved/Logs/debug_landscape_height_quadrants_result.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines))
    unreal.log("Wrote quadrant stats result file")


if __name__ == "__main__":
    main()

