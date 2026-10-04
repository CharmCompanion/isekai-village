"""
Probe read-back render target signatures for UnrealEditor Python.
"""

import unreal

OUT_PATH = "F:/DEVELOPMENT/Games/SpellCraft/Saved/Logs/probe_read_render_target_sig_out.txt"

def show(name):
    fn = getattr(unreal.RenderingLibrary, name, None)
    if not fn:
        line = f"{name}: missing"
        print(line)
        out_lines.append(line)
        return
    line1 = f"{name}: {fn}"
    line2 = f"  text_signature: {getattr(fn, '__text_signature__', '')}"
    line3 = f"  doc: {getattr(fn, '__doc__', '')}"
    print(line1)
    print(line2)
    print(line3)
    out_lines.extend([line1, line2, line3])


def main():
    global out_lines
    out_lines = []
    for name in [
        "read_render_target_raw_pixel_area",
        "read_render_target_raw_pixel",
        "read_render_target_uv",
        "read_render_target_raw_uv_area",
        "read_render_target_pixel",
        "read_render_target",
    ]:
        show(name)

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines))
    unreal.log(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()

