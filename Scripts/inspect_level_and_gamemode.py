import unreal

def inspect_level():
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    print(f"=== TOTAL ACTORS IN MAP: {len(all_actors)} ===")

    for act in all_actors:
        cls_name = act.get_class().get_name()
        act_name = act.get_name()
        if "Character" in cls_name or "Pawn" in cls_name or "BP_" in act_name or "GameMode" in cls_name:
            print(f" -> {act_name} ({cls_name}) at {act.get_actor_location()}")

    # Check Default GameMode in Maps & Modes
    engine_settings = unreal.get_default_object(unreal.GameMapsSettings)
    if engine_settings:
        gm = engine_settings.get_editor_property("global_default_game_mode")
        print(f"=== Engine Global Default GameMode: {gm} ===")

if __name__ == "__main__":
    inspect_level()
