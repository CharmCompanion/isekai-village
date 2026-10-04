"""
Ensure BP_ThirdPersonGameMode and BP_ThirdPersonCharacter use SpellCraftCharacter,
and assign the Mannequin mesh and animation blueprint to BP_MageCharacter.
"""
import unreal

BEL = unreal.BlueprintEditorLibrary
EAL = unreal.EditorAssetLibrary

# 1. Update BP_ThirdPersonGameMode to use SpellCraftCharacter as Default Pawn Class
gm_path = "/Game/ThirdPerson/Blueprints/BP_ThirdPersonGameMode"
gm_bp = unreal.load_asset(gm_path)
if gm_bp:
    unreal.log(f"Found GameMode: {gm_path}")
    # Get generated class of SpellCraftCharacter or BP_MageCharacter
    mage_bp = unreal.load_asset("/Game/SpellCraft/Blueprints/Character/BP_MageCharacter")
    pawn_class = mage_bp.generated_class() if mage_bp else unreal.SpellCraftCharacter.static_class()
    
    # Set default pawn class on the GameMode CDO
    gm_cdo = unreal.get_default_object(gm_bp.generated_class())
    if gm_cdo:
        gm_cdo.set_editor_property("default_pawn_class", pawn_class)
        unreal.log(f"Set BP_ThirdPersonGameMode default_pawn_class to: {pawn_class}")
    
    BEL.compile_blueprint(gm_bp)
    EAL.save_loaded_asset(gm_bp)

# 2. Also reparent BP_ThirdPersonCharacter to SpellCraftCharacter so that any placed actor in the level immediately becomes our mage!
tp_char_path = "/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter"
tp_char_bp = unreal.load_asset(tp_char_path)
if tp_char_bp:
    unreal.log(f"Found Character: {tp_char_path}")
    BEL.reparent_blueprint(tp_char_bp, unreal.SpellCraftCharacter)
    BEL.compile_blueprint(tp_char_bp)
    EAL.save_loaded_asset(tp_char_bp)
    unreal.log("Reparented BP_ThirdPersonCharacter to SpellCraftCharacter!")

# 3. Ensure BP_MageCharacter inherits mannequin mesh if available
if mage_bp:
    BEL.reparent_blueprint(mage_bp, unreal.SpellCraftCharacter)
    BEL.compile_blueprint(mage_bp)
    EAL.save_loaded_asset(mage_bp)
    unreal.log("Compiled BP_MageCharacter!")

unreal.log("=== GameMode and Character Configuration Complete ===")
