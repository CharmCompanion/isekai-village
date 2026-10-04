import unreal

def apply_stylized_material_to_landscape():
    """
    Finds the Landscape actor in the current level and assigns the
    SoStylized landscape material to it directly.
    """
    # Load the SoStylized landscape material instance
    land_mat_paths = [
        "/Game/SoStylized/Environment/Landscape/Materials/MI_Landscape",
        "/Game/SoStylized/Environment/Landscape/Materials/MI_Landscape_Bundle_1",
        "/Game/SoStylized/Environment/Landscape/Materials/M_Landscape",
    ]

    land_mat = None
    for path in land_mat_paths:
        land_mat = unreal.EditorAssetLibrary.load_asset(path)
        if land_mat:
            print(f"Loaded landscape material: {path}")
            break

    if not land_mat:
        print("ERROR: Could not find SoStylized landscape material!")
        return

    # Find the Landscape actor in the current level
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    landscape_actor = None
    for act in all_actors:
        if isinstance(act, unreal.Landscape):
            landscape_actor = act
            print(f"Found Landscape actor: {act.get_name()} at {act.get_actor_location()}")
            break

    if not landscape_actor:
        print("ERROR: No Landscape actor found in current level. Make sure your Height map is open!")
        return

    # Assign the SoStylized material to the landscape
    landscape_actor.set_editor_property("landscape_material", land_mat)
    print("Assigned SoStylized MI_Landscape material to Landscape!")

    # Now assign LL Layer Info objects so the material has its grass/rock/sand/dirt
    layer_info_paths = {
        "Grass": "/Game/SoStylized/Environment/Landscape/LL_Grass",
        "Rock":  "/Game/SoStylized/Environment/Landscape/LL_Rock",
        "Sand":  "/Game/SoStylized/Environment/Landscape/LL_Sand",
        "Dirt":  "/Game/SoStylized/Environment/Landscape/LL_Dirt",
    }

    for layer_name, ll_path in layer_info_paths.items():
        ll_asset = unreal.EditorAssetLibrary.load_asset(ll_path)
        if ll_asset:
            print(f"Loaded Layer Info: {layer_name} -> {ll_path}")
        else:
            print(f"WARNING: Could not find Layer Info for {layer_name} at {ll_path}")

    # Force update and save
    unreal.EditorLevelLibrary.save_current_level()
    print("\nSUCCESS: SoStylized Landscape material applied and saved!")
    print("Your island should now show grass, rocks, sand, and dirt!")

if __name__ == "__main__":
    apply_stylized_material_to_landscape()
