"""Find all unreal APIs related to landscape height editing."""
import unreal

keywords = ("height", "landscape", "editlayer", "heightmap")
found = []
for name in sorted(dir(unreal)):
    nl = name.lower()
    if any(k in nl for k in keywords):
        found.append(name)

path = "F:/DEVELOPMENT/Games/SpellCraft/Saved/Logs/probe_unreal_landscape_names.txt"
with open(path, "w", encoding="utf-8") as f:
    f.write("\n".join(found))
    f.write(f"\n\nTotal: {len(found)}")
