import unreal
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');R='/Game/IsekaiVillage/AdventureWorld';M=unreal.MaterialEditingLibrary;A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools()
name='M_IV_LivingContinent_Final17';path=R+'/Materials/'+name
mat=unreal.load_asset(path) if A.does_asset_exist(path) else T.create_asset(name,R+'/Materials',unreal.Material,unreal.MaterialFactoryNew());M.delete_all_material_expressions(mat)
def custom(code,typ,inputs):
 node=M.create_material_expression(mat,unreal.MaterialExpressionCustom);pins=[]
 for key in inputs:
  p=unreal.CustomInput();p.set_editor_property('input_name',key);pins.append(p)
 node.set_editor_property('inputs',pins);node.set_editor_property('output_type',typ);node.set_editor_property('code',code)
 for key,(n,out) in inputs.items():assert M.connect_material_expressions(n,out,node,key),key
 return node
pos=M.create_material_expression(mat,unreal.MaterialExpressionWorldPosition);normal=M.create_material_expression(mat,unreal.MaterialExpressionVertexNormalWS)
uv=custom('return (WorldPos.xy/100.+8000.)/16000.;',unreal.CustomMaterialOutputType.CMOT_FLOAT2,{'WorldPos':(pos,'')})
samples=[]
faruv=custom('return abs(frac((WorldPos.xy/100.+8000.)/32000.)*2.-1.)*.9+.05;',unreal.CustomMaterialOutputType.CMOT_FLOAT2,{'WorldPos':(pos,'')})
for index,tex in enumerate(['T_IV_ContinentAtlas17','T_IV_ContinentAtlas17']):
 n=M.create_material_expression(mat,unreal.MaterialExpressionTextureSample);n.set_editor_property('texture',unreal.load_asset(R+'/Textures/'+tex));n.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR);assert M.connect_material_expressions(uv if index==0 else faruv,'',n,'UVs');samples.append(n)
col=custom('float shade=.48+.52*saturate(dot(normalize(SurfaceNormal),normalize(float3(-.6,-.4,1.))));float blend=smoothstep(5500.,7500.,length(WorldPos.xy/100.));float wet=saturate((DistantColor.b-DistantColor.r)*14.);float3 distant=lerp(DistantColor,float3(.12,.24,.075),wet);distant=lerp(distant,float3(.10,.18,.085),.45);return lerp(NearColor,distant,blend)*shade;',unreal.CustomMaterialOutputType.CMOT_FLOAT3,{'WorldPos':(pos,''),'SurfaceNormal':(normal,''),'NearColor':(samples[0],'RGB'),'DistantColor':(samples[1],'RGB')})
assert M.connect_material_property(col,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR);mat.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT);M.recompile_material(mat);A.save_loaded_asset(mat)
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name()=='SM_IV_LivingContinent_v17':a.static_mesh_component.set_material(0,mat)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
exec(compile((B/'Scripts/render_living_continent_v17.py').read_text(),'final material review','exec'),{'__name__':'__main__'})
