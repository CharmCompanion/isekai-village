import unreal

def inspect_demo():
    map_path = "/Game/SoStylized/Maps/CompleteVol1/Demonstration"
    unreal.EditorLevelLibrary.load_level(map_path)
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    print(f"=== ACTORS IN {map_path} (Total: {len(all_actors)}) ===")

    ps_count = 0
    landscape_count = 0
    water_count = 0

    for act in all_actors:
        cls_name = act.get_class().get_name()
        if isinstance(act, unreal.PlayerStart):
            ps_count += 1
            print(f"PlayerStart at: {act.get_actor_location()}")
        elif isinstance(act, unreal.Landscape):
            landscape_count += 1
            print(f"Landscape at: {act.get_actor_location()}")
        elif "Water" in cls_name:
            water_count += 1
            print(f"Water actor: {act.get_name()} ({cls_name}) at {act.get_actor_location()}")

    print(f"Summary: Landscapes={landscape_count}, Water={water_count}, PlayerStarts={ps_count}")

if __name__ == "__main__":
    inspect_demo()
