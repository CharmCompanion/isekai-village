"""Probe LandscapeEditLayer and component APIs."""
import unreal

out = []
for cls_name in ["LandscapeEditLayer", "LandscapeComponent", "LandscapeEditLayerPersistent"]:
    cls = getattr(unreal, cls_name, None)
    out.append(f"\n=== {cls_name} ===")
    if not cls:
        out.append("  (missing)")
        continue
    for m in sorted(dir(cls)):
        if not m.startswith("_") and any(k in m.lower() for k in ("height", "import", "set", "data", "layer")):
            out.append(f"  {m}")

# instance methods on loaded landscape
sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
landscape = None
for act in sub.get_all_level_actors():
    if isinstance(act, unreal.Landscape):
        landscape = act
        break

out.append(f"\nLandscape instance methods (height/import):")
if landscape:
    for m in sorted(dir(landscape)):
        if not m.startswith("_") and any(k in m.lower() for k in ("height", "import", "edit", "layer")):
            out.append(f"  {m}")

path = "F:/DEVELOPMENT/Games/SpellCraft/Saved/Logs/probe_edit_layer.txt"
with open(path, "w", encoding="utf-8") as f:
    f.write("\n".join(out))
