"""Landscape resolution and bounds on Height_DemoCopy."""
import unreal

MAP = "/Game/SpellCraft/Maps/Height_DemoCopy"
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
for act in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if isinstance(act, unreal.Landscape):
        loc = act.get_actor_location()
        scale = act.get_actor_scale3d()
        bounds = act.get_actor_bounds(False)
        print(f"Landscape loc={loc} scale={scale}")
        print(f"  bounds origin={bounds[0]} extent={bounds[1]}")
        try:
            print(f"  layers={act.get_target_layer_names()}")
        except Exception as e:
            print(f"  layers err={e}")
        for prop in ("component_size_quads", "num_subsections", "subdivision_size"):
            try:
                print(f"  {prop}={act.get_editor_property(prop)}")
            except Exception:
                pass
