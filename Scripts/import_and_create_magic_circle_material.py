import unreal
import os

def create_magic_circle_assets():
    png_path = "F:/DEVELOPMENT/Games/SpellCraft/Content/SpellCraft/Textures/T_MagicCircle_Master.png"
    if not os.path.exists(png_path):
        print(f"Error: {png_path} not found!")
        return

    # 1. Re-import Texture
    task = unreal.AssetImportTask()
    task.filename = png_path
    task.destination_path = "/Game/SpellCraft/Textures"
    task.destination_name = "T_MagicCircle_Master"
    task.replace_existing = True
    task.automated = True
    task.save = True

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    print("Texture re-imported successfully!")

    texture_asset = unreal.EditorAssetLibrary.load_asset("/Game/SpellCraft/Textures/T_MagicCircle_Master")
    if not texture_asset:
        print("Failed to load imported texture asset.")
        return

    # 2. Re-create Material M_MagicCircle_Master with UV Rotator Node (Prevents ANY 3D barrel rolls!)
    mat_path = "/Game/SpellCraft/Materials/M_MagicCircle_Master"
    if unreal.EditorAssetLibrary.does_asset_exist(mat_path):
        unreal.EditorAssetLibrary.delete_asset(mat_path)

    mat_factory = unreal.MaterialFactoryNew()
    mat_tools = unreal.AssetToolsHelpers.get_asset_tools()
    mat = mat_tools.create_asset("M_MagicCircle_Master", "/Game/SpellCraft/Materials", unreal.Material, mat_factory)

    if not mat:
        print("Failed to create material asset.")
        return

    mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_ADDITIVE)
    mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    mat.set_editor_property("two_sided", True)

    # Node 1: Texture Coordinate
    tex_coord = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionTextureCoordinate, -800, 100)

    # Node 2: Scalar Parameter (RotationAngle: 0.0 to 1.0 UV turns)
    rot_param = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -800, 250)
    rot_param.set_editor_property("parameter_name", "RotationAngle")
    rot_param.set_editor_property("default_value", 0.0)

    # Node 3: CustomRotator (Rotates UV around center 0.5, 0.5)
    custom_rot = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionCustomRotator, -600, 150)
    unreal.MaterialEditingLibrary.connect_material_expressions(tex_coord, "", custom_rot, "UVs")
    unreal.MaterialEditingLibrary.connect_material_expressions(rot_param, "", custom_rot, "RotationSpeed") # In CustomRotator this is Time/Angle input

    # Node 4: Texture Sample Parameter
    tex_sample = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionTextureSampleParameter2D, -380, 100)
    tex_sample.set_editor_property("parameter_name", "CircleTexture")
    tex_sample.set_editor_property("texture", texture_asset)
    unreal.MaterialEditingLibrary.connect_material_expressions(custom_rot, "", tex_sample, "UVs")

    # Node 5: Vector Parameter (EmissiveColor)
    color_param = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -400, -200)
    color_param.set_editor_property("parameter_name", "EmissiveColor")
    color_param.set_editor_property("default_value", unreal.LinearColor(0.08, 0.72, 1.0, 1.0)) # Electric Cyan

    # Node 6: Scalar Parameter (GlowIntensity)
    glow_param = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -400, -50)
    glow_param.set_editor_property("parameter_name", "GlowIntensity")
    glow_param.set_editor_property("default_value", 20.0)

    # Node 7: Multiply (Color * GlowIntensity)
    mul_glow = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionMultiply, -180, -150)
    unreal.MaterialEditingLibrary.connect_material_expressions(color_param, "", mul_glow, "A")
    unreal.MaterialEditingLibrary.connect_material_expressions(glow_param, "", mul_glow, "B")

    # Node 8: Multiply ((Color * Glow) * Texture RGB)
    mul_tex = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionMultiply, -20, -50)
    unreal.MaterialEditingLibrary.connect_material_expressions(mul_glow, "", mul_tex, "A")
    unreal.MaterialEditingLibrary.connect_material_expressions(tex_sample, "RGB", mul_tex, "B")

    # Node 9: Multiply (Result * Texture Alpha)
    mul_alpha = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionMultiply, 140, 0)
    unreal.MaterialEditingLibrary.connect_material_expressions(mul_tex, "", mul_alpha, "A")
    unreal.MaterialEditingLibrary.connect_material_expressions(tex_sample, "A", mul_alpha, "B")

    # Connect to Material Emissive Output
    unreal.MaterialEditingLibrary.connect_material_property(mul_alpha, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)

    unreal.MaterialEditingLibrary.recompile_material(mat)
    unreal.EditorAssetLibrary.save_loaded_asset(mat)

    print("Master UV-Rotated Material M_MagicCircle_Master created and saved successfully!")

if __name__ == "__main__":
    create_magic_circle_assets()
