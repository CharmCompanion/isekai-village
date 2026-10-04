"""
Keep only the main ocean BP_Water (lowest Z near 0); delete elevated water planes.
Also ensure landscape stays above that ocean.

Close editor first, then:
  UnrealEditor-Cmd.exe <uproject> -run=pythonscript -script=...\\fix_water_planes.py -AllowCommandletRendering -stdout -unattended -nosplash
"""
import unreal

MAP = "/Game/SpellCraft/Maps/Height_DemoCopy"
RESULT = "F:/DEVELOPMENT/Games/SpellCraft/Saved/Logs/fix_water_planes_result.txt"
OUT = []


def log(msg):
    OUT.append(msg)
    unreal.log(msg)
    print(msg)


def main():
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    waters = []
    landscape = None
    for act in sub.get_all_level_actors():
        cls = act.get_class().get_name()
        if cls == "BP_Water_C" or "BP_Water" in act.get_name():
            waters.append(act)
        if isinstance(act, unreal.Landscape):
            landscape = act

    waters.sort(key=lambda a: a.get_actor_location().z)
    for w in waters:
        log(f"water {w.get_name()} Z={w.get_actor_location().z}")

    if not waters:
        log("ERROR: no BP_Water")
        return

    # Keep the lowest water as ocean; delete the rest (demo lake/river pieces at high Z)
    keep = waters[0]
    keep.set_actor_location(unreal.Vector(0.0, 0.0, 0.0), False, False)
    log(f"KEEP ocean {keep.get_name()} at Z=0")

    removed = 0
    for w in waters[1:]:
        log(f"DELETE elevated water {w.get_name()} Z={w.get_actor_location().z}")
        sub.destroy_actor(w)
        removed += 1
    log(f"Removed {removed} elevated water planes")

    if landscape:
        loc = landscape.get_actor_location()
        # Ensure landscape base is clearly above ocean
        if loc.z < 1500.0:
            landscape.set_actor_location(unreal.Vector(loc.x, loc.y, 2500.0), False, False)
            log(f"Landscape Z forced to 2500 (was {loc.z})")
        else:
            log(f"Landscape Z ok at {loc.z}")

    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    log("SUCCESS: reopen Height_DemoCopy")
    with open(RESULT, "w", encoding="utf-8") as f:
        f.write("\n".join(OUT))


if __name__ == "__main__":
    main()
