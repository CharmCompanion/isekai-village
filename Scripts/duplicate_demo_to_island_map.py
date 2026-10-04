import unreal

def setup_full_stylized_map():
    src_map = "/Game/SoStylized/Maps/CompleteVol1/Demonstration"
    dest_map = "/Game/SpellCraft/Maps/Map_IslandSanctum"

    if not unreal.EditorAssetLibrary.does_asset_exist(src_map):
        print(f"Error: Source map {src_map} does not exist!")
        return

    # Delete existing placeholder Map_IslandSanctum
    if unreal.EditorAssetLibrary.does_asset_exist(dest_map):
        unreal.EditorAssetLibrary.delete_asset(dest_map)
        print(f"Deleted old placeholder at {dest_map}")

    # Duplicate the full professional demonstration map to Map_IslandSanctum
    success = unreal.EditorAssetLibrary.duplicate_asset(src_map, dest_map)
    print(f"Duplicated {src_map} to {dest_map}: {success}")

    # Also duplicate the streaming grass level if needed
    src_grass = "/Game/SoStylized/Maps/CompleteVol1/StreamingLevel_Demo_Grass"
    dest_grass = "/Game/SpellCraft/Maps/StreamingLevel_Demo_Grass"
    if unreal.EditorAssetLibrary.does_asset_exist(src_grass) and not unreal.EditorAssetLibrary.does_asset_exist(dest_grass):
        unreal.EditorAssetLibrary.duplicate_asset(src_grass, dest_grass)

    # Load and customize the map
    unreal.EditorLevelLibrary.load_level(dest_map)

    # Ensure PlayerStart exists
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    has_player_start = False
    for act in all_actors:
        if isinstance(act, unreal.PlayerStart):
            has_player_start = True
            break

    if not has_player_start:
        unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(0, 0, 500), unreal.Rotator(0, 0, 0))

    unreal.EditorLevelLibrary.save_current_level()
    print("Map_IslandSanctum successfully configured with full SoStylized environment!")

if __name__ == "__main__":
    setup_full_stylized_map()
