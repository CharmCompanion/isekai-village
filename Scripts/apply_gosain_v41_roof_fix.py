import unreal
M=unreal.MaterialEditingLibrary;A=unreal.EditorAssetLibrary
mat=unreal.load_asset('/Game/IsekaiVillage/AdventureWorld/Gosain39/Materials/M_Gosain39_Terracotta');assert mat;M.delete_all_material_expressions(mat)
t=M.create_material_expression(mat,unreal.MaterialExpressionTextureSample);t.texture=unreal.load_asset('/Game/Fantastic_Village_Pack/textures/T_rooftiles_01_BC')
c=M.create_material_expression(mat,unreal.MaterialExpressionCustom);pin=unreal.CustomInput();pin.set_editor_property('input_name','T');c.set_editor_property('inputs',[pin]);c.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3);c.set_editor_property('code','float l=dot(T.rgb,float3(.3,.59,.11));return l*float3(1.65,.55,.23);')
assert M.connect_material_expressions(t,'',c,'T');assert M.connect_material_property(c,'',unreal.MaterialProperty.MP_BASE_COLOR)
r=M.create_material_expression(mat,unreal.MaterialExpressionConstant);r.r=.82;assert M.connect_material_property(r,'',unreal.MaterialProperty.MP_ROUGHNESS);M.recompile_material(mat);A.save_loaded_asset(mat)
