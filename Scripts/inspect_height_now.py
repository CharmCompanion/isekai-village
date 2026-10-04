"""
Inspect Height_DemoCopy: landscape Z/bounds, mesh count, water, streaming.
Writes Saved/Logs/inspect_height_now.txt
"""
import unreal

MAP = "/Game/SpellCraft/Maps/Height_DemoCopy"
OUT = []


def log(msg):
    OUT.append(str(msg))
    unreal.log(msg)


def main():
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    counts = {}
    landscape = None
    for act in sub.get_all_level_actors():
        cls = act.get_class().get_name()
        counts[cls] = counts.get(cls, 0) + 1
        if isinstance(act, unreal.Landscape):
            landscape = act
            loc = act.get_actor_location()
            scale = act.get_actor_scale3d()
            log(f"Landscape loc={loc} scale={scale}")
            try:
                bb = act.get_actor_bounds(False)
                # get_actor_bounds returns (origin, extent) in some bindings
                log(f"Landscape bounds raw={bb}")
            except Exception as e:
                log(f"bounds err: {e}")
            try:
                origin, extent = act.get_actor_bounds(False, False)
                log(f"origin={origin} extent={extent}")
                log(f"Z range approx {origin.z - extent.z} .. {origin.z + extent.z}")
            except Exception as e:
                log(f"bounds2 err: {e}")
        if "Water" in cls or "Water" in act.get_name():
            log(f"Water {act.get_name()} loc={act.get_actor_location()} scale={act.get_actor_scale3d()}")
        if isinstance(act, unreal.StaticMeshActor):
            loc = act.get_actor_location()
            mesh = act.static_mesh_component.static_mesh if act.static_mesh_component else None
            mname = mesh.get_name() if mesh else "?"
            if abs(loc.z) > 500 or "Cliff" in mname or "Rock" in mname:
                log(f"  SMA {act.get_name()} mesh={mname} loc={loc}")

    log("COUNTS: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items(), key=lambda kv: -kv[1])[:25]))

    # Streaming levels
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    try:
        streaming = world.get_streaming_levels()
        log(f"Streaming levels: {len(streaming)}")
        for s in streaming:
            log(f"  stream {s}")
    except Exception as e:
        log(f"streaming err: {e}")

    path = "F:/DEVELOPMENT/Games/SpellCraft/Saved/Logs/inspect_height_now.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(OUT))
    log(f"Wrote {path}")


if __name__ == "__main__":
    main()
