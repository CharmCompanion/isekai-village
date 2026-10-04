import unreal,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');R='/Game/IsekaiVillage/AdventureWorld';M=unreal.MaterialEditingLibrary;A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools()
t=unreal.AssetImportTask();t.filename=str(B/'Saved/AdventureWorldSource/T_IV_ForestFloor_v08.png');t.destination_path=R+'/Textures';t.destination_name='T_IV_ForestFloor_v08';t.automated=True;t.replace_existing=True;t.save=True;T.import_asset_tasks([t]);tex=unreal.load_asset(R+'/Textures/T_IV_ForestFloor_v08');tex.set_editor_property('srgb',False);tex.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP);A.save_loaded_asset(tex)
mat=unreal.load_asset(R+'/Materials/M_IV_FloatingLandscape');nodes=M.get_material_expressions(mat);pos=next(n for n in nodes if isinstance(n,unreal.MaterialExpressionWorldPosition));color=next(n for n in nodes if isinstance(n,unreal.MaterialExpressionCustom) and 'farmSoil' in n.get_editor_property('code'))
code=color.get_editor_property('code')
if 'ForestFloor' not in code:
 uv=M.create_material_expression(mat,unreal.MaterialExpressionCustom);pin=unreal.CustomInput();pin.set_editor_property('input_name','P');uv.set_editor_property('inputs',[pin]);uv.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT2);uv.set_editor_property('code','return (P.xy+60000.0+59.52381)/120119.04762;');M.connect_material_expressions(pos,'',uv,'P')
 sample=M.create_material_expression(mat,unreal.MaterialExpressionTextureSample);sample.set_editor_property('texture',tex);sample.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR);M.connect_material_expressions(uv,'',sample,'UVs')
 pins=list(color.get_editor_property('inputs'));pin=unreal.CustomInput();pin.set_editor_property('input_name','ForestFloor');pins.append(pin);color.set_editor_property('inputs',pins);M.connect_material_expressions(sample,'R',color,'ForestFloor')
 code=code.replace('c=lerp(c,D*float3(1.13,1.05,.90),Mask.r);','c=lerp(c,D*float3(.50,.57,.38),ForestFloor*.65);\nc=lerp(c,D*float3(1.13,1.05,.90),Mask.r);');color.set_editor_property('code',code)
M.recompile_material(mat);A.save_loaded_asset(mat)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(B/'Saved/forest_floor_result.json').write_text(json.dumps({'saved':True}))
