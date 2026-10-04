"""Inspect Height map and list available landscape/foliage editor subsystems."""
import unreal

MAP_PATH = "/Game/SpellCraft/Maps/Height"
DEMO_PATH = "/Game/SoStylized/Maps/CompleteVol1/Demonstration"


def inspect_map(map_path, label):
    if not unreal.EditorAssetLibrary.does_asset_exist(map_path):
        print(f"[{label}] MISSING: {map_path}")
        return

    unreal.EditorLevelLibrary.load_level(map_path)
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    print(f"\n=== {label}: {map_path} ({len(actors)} actors) ===")

    counts = {}
    for act in actors:
        cls = act.get_class().get_name()
        counts[cls] = counts.get(cls, 0) + 1

        if isinstance(act, unreal.Landscape):
            mat = act.get_editor_property("landscape_material")
            mat_name = mat.get_name() if mat else "None"
            loc = act.get_actor_location()
            scale = act.get_actor_scale3d()
            print(f"  Landscape: {act.get_name()} mat={mat_name} loc={loc} scale={scale}")

        if isinstance(act, unreal.DirectionalLight):
            print(f"  Sun: {act.get_name()} at {act.get_actor_location()}")

        if isinstance(act, unreal.PlayerStart):
            print(f"  PlayerStart: {act.get_actor_location()}")

        if "Water" in cls or "Foliage" in cls or "InstancedFoliage" in cls:
            print(f"  {cls}: {act.get_name()} at {act.get_actor_location()}")

    print("  Actor type counts:")
    for cls, n in sorted(counts.items(), key=lambda x: -x[1])[:20]:
        print(f"    {cls}: {n}")


def inspect_subsystems():
    print("\n=== Editor subsystems ===")
    for name in [
        "LandscapeEditorSubsystem",
        "FoliageEditorSubsystem",
        "EditorActorSubsystem",
        "UnrealEditorSubsystem",
    ]:
        cls = getattr(unreal, name, None)
        if cls:
            try:
                sub = unreal.get_editor_subsystem(cls)
                print(f"  OK {name}: {sub}")
            except Exception as exc:
                print(f"  FAIL {name}: {exc}")
        else:
            print(f"  MISSING class {name}")


if __name__ == "__main__":
    inspect_subsystems()
    inspect_map(DEMO_PATH, "DEMO")
    inspect_map(MAP_PATH, "HEIGHT")
