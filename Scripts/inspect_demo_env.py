"""Inspect demo environment actors we need to replicate on Height map."""
import unreal

DEMO = "/Game/SoStylized/Maps/CompleteVol1/Demonstration"
HEIGHT = "/Game/SpellCraft/Maps/Height"


def dump_env(map_path):
    unreal.EditorLevelLibrary.load_level(map_path)
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    print(f"\n=== ENV {map_path} ===")
    for act in actors:
        cls = act.get_class().get_name()
        if cls in {
            "RuntimeVirtualTextureVolume",
            "BP_StylizedSky_Lite_C",
            "ExponentialHeightFog",
            "SkyAtmosphere",
            "SkyLight",
            "DirectionalLight",
            "Landscape",
            "PlayerStart",
            "ProceduralFoliageVolume",
            "InstancedFoliageActor",
        } or "Water" in cls:
            loc = act.get_actor_location()
            rot = act.get_actor_rotation()
            scale = act.get_actor_scale3d()
            print(f"{cls} | {act.get_name()} | loc={loc} rot={rot} scale={scale}")
            if isinstance(act, unreal.Landscape):
                print(f"  mat={act.get_editor_property('landscape_material')}")
                print(f"  grass_types={act.get_editor_property('landscape_grass_types')}")
                try:
                    print(f"  target_layers={act.get_target_layer_names()}")
                except Exception as exc:
                    print(f"  target_layers error: {exc}")


if __name__ == "__main__":
    dump_env(DEMO)
    dump_env(HEIGHT)
