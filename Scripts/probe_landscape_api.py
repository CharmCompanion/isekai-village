"""Probe landscape/foliage Python APIs available in UE 5.8."""
import unreal

names = [n for n in dir(unreal) if "Landscape" in n or "Foliage" in n]
for n in sorted(names):
    print(n)

print("\n--- LandscapeEditorUtils ---")
utils = getattr(unreal, "LandscapeEditorUtils", None)
print(utils)
if utils:
    for m in sorted(dir(utils)):
        if not m.startswith("_"):
            print(f"  {m}")

print("\n--- LandscapeEditorObject ---")
obj = getattr(unreal, "LandscapeEditorObject", None)
print(obj)
