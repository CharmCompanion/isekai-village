import unreal,json
from pathlib import Path
M=unreal.MaterialEditingLibrary;A=unreal.EditorAssetLibrary
mat=unreal.load_asset('/Game/IsekaiVillage/AdventureWorld/Gosain37/Materials/M_Gosain37_RegionalTerrain')
fixed=[]
for n in M.get_material_expressions(mat):
    if isinstance(n,unreal.MaterialExpressionTextureSample) and n.texture and n.texture.get_name()=='T_Gosain37_Region':
        n.sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_GRAYSCALE;fixed.append(n.get_name())
# Proper three-axis rock projection avoids stretched texture on the sea cliffs.
nodes=M.get_material_expressions(mat)
if not any(isinstance(n,unreal.MaterialExpressionCustom) and 'GosainRock37' in n.get_editor_property('code') for n in nodes):
    p=next(n for n in nodes if isinstance(n,unreal.MaterialExpressionWorldPosition))
    normal=next(n for n in nodes if isinstance(n,unreal.MaterialExpressionVertexNormalWS))
    samples=[]
    for plane in ('yz','xz','xy'):
        uv=M.create_material_expression(mat,unreal.MaterialExpressionCustom);pin=unreal.CustomInput();pin.set_editor_property('input_name','P');uv.set_editor_property('inputs',[pin]);uv.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT2);uv.set_editor_property('code','return P.'+plane+'/900.;');M.connect_material_expressions(p,'',uv,'P')
        t=M.create_material_expression(mat,unreal.MaterialExpressionTextureSample);t.texture=unreal.load_asset('/Game/SoStylized/Environment/Rocks/Textures/Spire/T_RockSpire_BC');t.sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_COLOR;M.connect_material_expressions(uv,'',t,'UVs');samples.append(t)
    tri=M.create_material_expression(mat,unreal.MaterialExpressionCustom);pins=[]
    for key in ('N','A','B','C'):pin=unreal.CustomInput();pin.set_editor_property('input_name',key);pins.append(pin)
    tri.set_editor_property('inputs',pins);tri.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3);tri.set_editor_property('code','/*GosainRock37*/ float3 w=pow(abs(N),4);w/=max(dot(w,1),.001);return A*w.x+B*w.y+C*w.z;')
    for key,n in zip(('N','A','B','C'),[normal]+samples):M.connect_material_expressions(n,'',tri,key)
    for n in nodes:
        if isinstance(n,unreal.MaterialExpressionCustom) and 'float3 meadow=' in n.get_editor_property('code'):M.connect_material_expressions(tri,'',n,'R')
M.recompile_material(mat);A.save_loaded_asset(mat)
Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/Gosain37/material_fix.json').write_text(json.dumps({'sampler_fixed':fixed,'tangent_space_normal':mat.get_editor_property('tangent_space_normal')}))
