"""
Synchronizes BP_MageCharacter properties (Camera, Mesh, Visuals) for AAA Third-Person gameplay.
"""
import unreal

BEL = unreal.BlueprintEditorLibrary
EAL = unreal.EditorAssetLibrary

bp_path = "/Game/SpellCraft/Blueprints/Character/BP_MageCharacter"
bp = unreal.load_asset(bp_path)

if bp:
    gen_class = bp.generated_class()
    cdo = unreal.get_default_object(gen_class)
    
    if cdo:
        # Mesh Alignment (Standard upright facing forward)
        mesh_comp = cdo.get_editor_property("mesh")
        if mesh_comp:
            mesh_comp.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, -88.0))
            mesh_comp.set_editor_property("relative_rotation", unreal.Rotator(0.0, -90.0, 0.0))
            unreal.log("Mesh transform set to Location(0, 0, -88), Rotation(0, -90, 0)")

        # AAA Camera Boom Setup
        try:
            boom = cdo.get_editor_property("camera_boom")
            if boom:
                boom.set_editor_property("target_arm_length", 400.0)
                boom.set_editor_property("socket_offset", unreal.Vector(0.0, 40.0, 50.0))
                boom.set_editor_property("b_inherit_pitch", True)
                boom.set_editor_property("b_inherit_yaw", True)
                boom.set_editor_property("b_inherit_roll", False)
                boom.set_editor_property("b_use_pawn_control_rotation", True)
                boom.set_editor_property("b_do_collision_test", True)
                boom.set_editor_property("b_enable_camera_lag", True)
                boom.set_editor_property("camera_lag_speed", 12.0)
                unreal.log("CameraBoom setup for AAA Over-The-Shoulder free orbit!")
        except Exception as e:
            unreal.log(f"CameraBoom property setup notice: {e}")

    BEL.compile_blueprint(bp)
    EAL.save_loaded_asset(bp)

unreal.log("=== AAA Character Setup Complete ===")
