import unreal
MAP = "/Game/SpellCraft/Maps/Height_DemoCopy"
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
land = None
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if isinstance(a, unreal.Landscape):
        land = a
        break
print("Landscape methods with import/height:")
for m in sorted(dir(land)):
    if "height" in m.lower() or "import" in m.lower():
        print(f"  {m}")
