import unreal

def verify_demo_map():
    map_path = "/Game/SoStylized/Maps/CompleteVol1/Demonstration"
    unreal.EditorLevelLibrary.load_level(map_path)
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    print(f"Loaded {map_path}, actors: {len(all_actors)}")

    has_ps = False
    for act in all_actors:
        if isinstance(act, unreal.PlayerStart):
            has_ps = True
            print(f"Found PlayerStart at {act.get_actor_location()}")
            break

    if not has_ps:
        ps = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(0, 0, 300), unreal.Rotator(0, 0, 0))
        unreal.EditorLevelLibrary.save_current_level()
        print("Spawned and saved PlayerStart!")

if __name__ == "__main__":
    verify_demo_map()
