"""Read-only capability check for creating/importing a Landscape in UE 5.8."""
import unreal

for name in sorted(n for n in dir(unreal) if "Landscape" in n):
    print("TYPE", name)

for name in ("LandscapeEditorSubsystem", "LandscapeEditorUtils", "Landscape", "EditorLevelLibrary"):
    value = getattr(unreal, name, None)
    print("\nAPI", name, value)
    if value:
        for method in sorted(m for m in dir(value) if not m.startswith("_") and any(word in m.lower() for word in ("create", "import", "height", "landscape", "spawn", "level"))):
            print(" ", method)
