"""Inspect Python signatures for landscape height import."""
import inspect
import unreal

m = unreal.Landscape.landscape_import_heightmap_from_render_target
out = [f"landscape_import_heightmap_from_render_target: {m}"]

# Try to get doc
try:
    out.append(f"doc: {m.__doc__}")
except Exception:
    pass

# List all Landscape static/editor methods with height
for name in sorted(dir(unreal.Landscape)):
    if "height" in name.lower() or "import" in name.lower():
        out.append(f"  {name}")

# RenderingLibrary create_render_target2d signature
for fn_name in ["create_render_target2d", "draw_material_to_render_target", "import_file_as_texture2d", "export_texture2d"]:
    fn = getattr(unreal.RenderingLibrary, fn_name, None)
    if fn:
        out.append(f"\nRenderingLibrary.{fn_name}: {fn}")

# Check LandscapeStreamingProxy
for cls_name in ["LandscapeStreamingProxy", "LandscapeEditorObject"]:
    cls = getattr(unreal, cls_name, None)
    out.append(f"\n{cls_name}: {cls}")

path = "F:/DEVELOPMENT/Games/SpellCraft/Saved/Logs/probe_landscape_sig.txt"
with open(path, "w", encoding="utf-8") as f:
    f.write("\n".join(out))
