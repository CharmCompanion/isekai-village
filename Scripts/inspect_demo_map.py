import unreal

def inspect_demo_map():
    map_path = "/Game/SoStylized/Maps/CompleteVol1/Demonstration"
    if not unreal.EditorAssetLibrary.does_asset_exist(map_path):
        print(f"Map {map_path} does not exist!")
        return

    unreal.EditorLevelLibrary.load_level(map_path)
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    print(f"=== INSPECTING {map_path} ===")
    print(f"Total Actors: {len(all_actors)}")

    for act in all_actors:
        cls_name = act.get_class().get_name()
        act_name = act.get_name()
        if "Landscape" in cls_name or "Water" in cls_name or "Light" in cls_name or "Sky" in cls_name or "Fog" in cls_name:
            print(f" -> {act_name} ({cls_name}) at {act.get_actor_location()} scale {act.get_actor_scale3d()}")

if __name__ == "__main__":
    inspect_demo_map()
