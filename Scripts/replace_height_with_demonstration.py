"""
Replace Height map with a full copy of SoStylized Demonstration.
This is the only reliable way to get grass/rock/sand/dirt/cliffs/trees working.

Run with editor CLOSED:
  T:\\Program Files\\UE_5.8\\Engine\\Binaries\\Win64\\UnrealEditor-Cmd.exe ^
    F:\\DEVELOPMENT\\Games\\SpellCraft\\SpellCraft.uproject ^
    -run=pythonscript ^
    -script="F:\\DEVELOPMENT\\Games\\SpellCraft\\Scripts\\replace_height_with_demonstration.py"
"""
import unreal

SRC = "/Game/SoStylized/Maps/CompleteVol1/Demonstration"
DEST = "/Game/SpellCraft/Maps/Height"


def log(msg):
    unreal.log(msg)
    print(msg)


def replace_map():
    if not unreal.EditorAssetLibrary.does_asset_exist(SRC):
        log(f"ERROR: Source map missing: {SRC}")
        return False

    temp_dest = "/Game/SpellCraft/Maps/Height_DemoCopy"
    for path in (DEST, temp_dest):
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            log(f"Deleting {path} ...")
            unreal.EditorAssetLibrary.delete_asset(path)

    log(f"Duplicating {SRC} -> {temp_dest} ...")
    ok = unreal.EditorAssetLibrary.duplicate_asset(SRC, temp_dest)
    if not ok:
        log("ERROR: duplicate_asset failed")
        return False

    # Rename copy to Height (game default map path)
    if unreal.EditorAssetLibrary.does_asset_exist(DEST):
        unreal.EditorAssetLibrary.delete_asset(DEST)
    renamed = unreal.EditorAssetLibrary.rename_asset(temp_dest, DEST)
    if not renamed:
        log(f"WARNING: rename failed; using {temp_dest} — update DefaultEngine.ini")
        dest_to_load = temp_dest
    else:
        dest_to_load = DEST
        log(f"Renamed copy to {DEST}")

    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(dest_to_load)
    actor_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = actor_sub.get_all_level_actors()

    # Remove duplicate directional lights (sky BP + manual sun conflict)
    suns = [a for a in actors if isinstance(a, unreal.DirectionalLight)]
    if len(suns) > 1:
        for extra in suns[1:]:
            actor_sub.destroy_actor(extra)
        log(f"Removed {len(suns) - 1} extra DirectionalLight(s)")

    has_ps = any(isinstance(a, unreal.PlayerStart) for a in actor_sub.get_all_level_actors())
    if not has_ps:
        actor_sub.spawn_actor_from_class(
            unreal.PlayerStart,
            unreal.Vector(-5028, 33934, 3429),
            unreal.Rotator(0, -53, 0),
        )
        log("Spawned PlayerStart")

    unreal.EditorLevelLibrary.save_current_level()
    log(f"SUCCESS: {dest_to_load} is now a full copy of Demonstration ({len(actor_sub.get_all_level_actors())} actors)")
    return True


if __name__ == "__main__":
    replace_map()
