"""
Assign SKM_Manny_Simple and ABP_Unarmed to BP_MageCharacter and configure child actor scales.
"""
import unreal

BEL = unreal.BlueprintEditorLibrary
EAL = unreal.EditorAssetLibrary

bp_path = "/Game/SpellCraft/Blueprints/Character/BP_MageCharacter"
bp = unreal.load_asset(bp_path)

if bp:
    mesh_asset = unreal.load_asset("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple")
    anim_asset = unreal.load_asset("/Game/Characters/Mannequins/Anims/Unarmed/ABP_Unarmed")
    
    gen_class = bp.generated_class()
    cdo = unreal.get_default_object(gen_class)
    
    if cdo:
        mesh_comp = cdo.get_editor_property("mesh")
        if mesh_comp and mesh_asset:
            mesh_comp.set_editor_property("skeletal_mesh_asset", mesh_asset)
            mesh_comp.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, -88.0))
            mesh_comp.set_editor_property("relative_rotation", unreal.Rotator(0.0, -90.0, 0.0))
            if anim_asset:
                mesh_comp.set_editor_property("anim_class", anim_asset.generated_class())
            unreal.log("Successfully assigned SKM_Manny_Simple and ABP_Unarmed to BP_MageCharacter!")
            
    BEL.compile_blueprint(bp)
    EAL.save_loaded_asset(bp)

unreal.log("=== Mage Mannequin Setup Finished ===")
