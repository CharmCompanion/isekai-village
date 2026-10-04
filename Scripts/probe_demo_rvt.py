"""Probe RVT volumes and landscape layers on Demonstration."""
import unreal

DEMO = "/Game/SoStylized/Maps/CompleteVol1/Demonstration"
unreal.EditorLevelLibrary.load_level(DEMO)
actors = unreal.EditorLevelLibrary.get_all_level_actors()

for act in actors:
    if isinstance(act, unreal.RuntimeVirtualTextureVolume):
        comp = act.get_component_by_class(unreal.RuntimeVirtualTextureVolumeComponent)
        print(f"RVT {act.get_name()} scale={act.get_actor_scale3d()}")
        if comp:
            for prop in ["virtual_texture", "hide_actor", "enable_scalability"]:
                try:
                    print(f"  {prop}={comp.get_editor_property(prop)}")
                except Exception as exc:
                    print(f"  {prop} err={exc}")

    if isinstance(act, unreal.Landscape):
        try:
            print(f"Landscape target layers: {act.get_target_layer_names()}")
        except Exception as exc:
            print(f"target layers err: {exc}")
        try:
            print(f"Grass enabled: {act.get_grass_enabled()}")
        except Exception as exc:
            print(f"grass err: {exc}")

    cls = act.get_class().get_name()
    if "StylizedSky" in cls:
        print(f"Sky: {cls} at {act.get_actor_location()}")
