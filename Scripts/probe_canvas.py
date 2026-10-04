"""Find Canvas draw methods."""
import unreal

methods = [m for m in dir(unreal.Canvas) if "draw" in m.lower() or "texture" in m.lower()]
path = "F:/DEVELOPMENT/Games/SpellCraft/Saved/Logs/probe_canvas.txt"
with open(path, "w", encoding="utf-8") as f:
    f.write("\n".join(sorted(methods)))
