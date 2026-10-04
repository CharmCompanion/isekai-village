"""Verify graybox map contents."""
import unreal
import traceback

try:
    MAP = "/Game/SpellCraft/Maps/Map_GrayboxArena"
    unreal.log(f"EXISTS {unreal.EditorAssetLibrary.does_asset_exist(MAP)}")
    unreal.EditorLevelLibrary.load_level(MAP)
    world = unreal.EditorLevelLibrary.get_editor_world()
    unreal.log(f"WORLD {world}")
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    unreal.log(f"ACTOR_COUNT {len(actors)}")
    for a in actors:
        unreal.log(f"ACTOR {a.get_actor_label()} {a.get_class().get_name()}")
    if world:
        ws = world.get_world_settings()
        unreal.log(f"GM {ws.get_editor_property('default_game_mode') if ws else None}")
    unreal.log("VERIFY_DONE")
except Exception as e:
    unreal.log_error(f"VERIFY_FAIL {e}")
    unreal.log_error(traceback.format_exc())
