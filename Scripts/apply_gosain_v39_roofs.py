import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain39';R='/Game/IsekaiVillage/AdventureWorld/Gosain39';A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();M=unreal.MaterialEditingLibrary
mat=T.create_asset('M_Gosain39_Terracotta',R+'/Materials',unreal.Material,unreal.MaterialFactoryNew());assert mat
tex=M.create_material_expression(mat,unreal.MaterialExpressionTextureSample);tex.texture=unreal.load_asset('/Game/Fantastic_Village_Pack/textures/T_rooftiles_01_BC')
des=M.create_material_expression(mat,unreal.MaterialExpressionDesaturation);one=M.create_material_expression(mat,unreal.MaterialExpressionConstant);one.r=1
M.connect_material_expressions(tex,'RGB',des,'Input');M.connect_material_expressions(one,'',des,'Fraction')
color=M.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector);color.constant=unreal.LinearColor(1.65,.55,.23,1)
mul=M.create_material_expression(mat,unreal.MaterialExpressionMultiply);M.connect_material_expressions(des,'',mul,'A');M.connect_material_expressions(color,'',mul,'B');M.connect_material_property(mul,'',unreal.MaterialProperty.MP_BASE_COLOR)
rough=M.create_material_expression(mat,unreal.MaterialExpressionConstant);rough.r=.8;M.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS)
M.recompile_material(mat);A.save_loaded_asset(mat)
changed=[]
for kit in json.loads((O/'merged_house_assets.json').read_text()):
    mesh=unreal.load_asset(kit['path']);assert '/VerifiedMeshes/' in mesh.get_path_name()
    for i,s in enumerate(mesh.static_materials):
        if s.material_interface and 'rooftiles' in s.material_interface.get_path_name():mesh.set_material(i,mat);changed.append([kit['name'],i])
    A.save_loaded_asset(mesh)
(O/'roof_palette.json').write_text(json.dumps({'changed_slots':changed,'material':mat.get_path_name()}))
(O/'nanite_api.txt').write_text(str(unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem).set_nanite_settings.__doc__))
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
