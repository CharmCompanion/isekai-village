"""
Force set the GameMode and Default Pawn in Lvl_ThirdPerson and BP_ThirdPersonGameMode.
"""
import unreal

BEL = unreal.BlueprintEditorLibrary
EAL = unreal.EditorAssetLibrary

# 1. Load BP_MageCharacter and get its generated class
mage_bp = unreal.load_asset("/Game/SpellCraft/Blueprints/Character/BP_MageCharacter")
if not mage_bp:
    unreal.log_error("Could not load BP_MageCharacter!")
mage_class = mage_bp.generated_class() if mage_bp else unreal.SpellCraftCharacter.static_class()

# 2. Update BP_ThirdPersonGameMode so even if World Settings uses it, it spawns BP_MageCharacter
tp_gm_bp = unreal.load_asset("/Game/ThirdPerson/Blueprints/BP_ThirdPersonGameMode")
if tp_gm_bp:
    gm_cdo = unreal.get_default_object(tp_gm_bp.generated_class())
    if gm_cdo:
        gm_cdo.set_editor_property("default_pawn_class", mage_class)
        unreal.log(f"Set BP_ThirdPersonGameMode DefaultPawnClass to: {mage_class.get_name()}")
    BEL.compile_blueprint(tp_gm_bp)
    EAL.save_loaded_asset(tp_gm_bp)

# 3. Load the map and change World Settings GameMode Override directly
map_path = "/Game/ThirdPerson/Lvl_ThirdPerson"
world = unreal.EditorLevelLibrary.get_editor_world()
if not world or world.get_name() != "Lvl_ThirdPerson":
    unreal.EditorLevelLibrary.load_level(map_path)
    world = unreal.EditorLevelLibrary.get_editor_world()

if world:
    world_settings = world.get_world_settings()
    if world_settings:
        world_settings.set_editor_property("game_mode_override_class", unreal.SpellCraftGameMode.static_class())
        unreal.log("Set WorldSettings GameModeOverride to SpellCraftGameMode!")
    unreal.EditorLevelLibrary.save_current_level()
    unreal.log(f"Saved level: {map_path}")

unreal.log("=== Setup Complete! ===")
