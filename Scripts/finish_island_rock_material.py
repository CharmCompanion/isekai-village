import unreal
R='/Game/IsekaiVillage/AdventureWorld';A=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;mat=unreal.load_asset(R+'/Materials/M_IV_IslandRock')
for n in M.get_material_expressions(mat):
 if isinstance(n,unreal.MaterialExpressionCustom):
  code=n.get_editor_property('code')
  if '/400.' in code:n.set_editor_property('code',code.replace('/400.','/2200.'))
old=M.get_material_property_input_node(mat,unreal.MaterialProperty.MP_BASE_COLOR);pos=next(n for n in M.get_material_expressions(mat) if isinstance(n,unreal.MaterialExpressionWorldPosition))
pins=[]
for key in ['C','P']:
 p=unreal.CustomInput();p.set_editor_property('input_name',key);pins.append(p)
n=M.create_material_expression(mat,unreal.MaterialExpressionCustom);n.set_editor_property('inputs',pins);n.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3);n.set_editor_property('code','float strata=.84+.12*sin(P.z/1200.+sin(P.x/4300.))+.06*sin((P.x+P.y)/3500.); return C*strata*float3(1.1,1.0,.85);');M.connect_material_expressions(old,'',n,'C');M.connect_material_expressions(pos,'',n,'P');M.connect_material_property(n,'',unreal.MaterialProperty.MP_BASE_COLOR);M.recompile_material(mat);A.save_loaded_asset(mat)
