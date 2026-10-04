import unreal

def create_spell_emissive_material():
    mat_path = "/Game/SpellCraft/Materials/M_SpellEmissive_Master"
    if unreal.EditorAssetLibrary.does_asset_exist(mat_path):
        unreal.EditorAssetLibrary.delete_asset(mat_path)

    mat_factory = unreal.MaterialFactoryNew()
    mat_tools = unreal.AssetToolsHelpers.get_asset_tools()
    mat = mat_tools.create_asset("M_SpellEmissive_Master", "/Game/SpellCraft/Materials", unreal.Material, mat_factory)

    if not mat:
        print("Failed to create M_SpellEmissive_Master.")
        return

    mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_OPAQUE)
    mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    mat.set_editor_property("two_sided", True)

    # Node 1: Vector Parameter (Color)
    color_param = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -400, 0)
    color_param.set_editor_property("parameter_name", "Color")
    color_param.set_editor_property("default_value", unreal.LinearColor(1.0, 0.25, 0.05, 1.0))

    # Connect to Emissive
    unreal.MaterialEditingLibrary.connect_material_property(color_param, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)

    unreal.MaterialEditingLibrary.recompile_material(mat)
    unreal.EditorAssetLibrary.save_asset(mat_path)
    print("M_SpellEmissive_Master successfully created and saved!")

if __name__ == "__main__":
    create_spell_emissive_material()
