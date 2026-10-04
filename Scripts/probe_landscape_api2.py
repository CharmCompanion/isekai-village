"""Probe landscape height import APIs in UE 5.8 commandlet."""
import unreal

out = []

def p(msg):
    out.append(msg)
    unreal.log(msg)

# Landscape actor methods
landscape_methods = [m for m in dir(unreal.Landscape) if "height" in m.lower() or "import" in m.lower()]
p("Landscape height/import methods:")
for m in sorted(landscape_methods):
    p(f"  {m}")

# Rendering libs
for name in ["RenderingLibrary", "KismetRenderingLibrary", "LandscapeEditorUtils", "LandscapeEditorSubsystem"]:
    obj = getattr(unreal, name, None)
    p(f"\n{name}: {obj}")
    if obj:
        methods = [m for m in dir(obj) if not m.startswith("_")]
        for m in sorted(methods):
            if any(k in m.lower() for k in ("height", "import", "texture", "render", "landscape", "convert")):
                p(f"  {m}")

# Check if landscape_import_heightmap_from_render_target exists on Landscape
p(f"\nhas landscape_import_heightmap_from_render_target: {hasattr(unreal.Landscape, 'landscape_import_heightmap_from_render_target')}")

# Write to file
path = "F:/DEVELOPMENT/Games/SpellCraft/Saved/Logs/probe_landscape_api2.txt"
with open(path, "w", encoding="utf-8") as f:
    f.write("\n".join(out))
p(f"Wrote {path}")
