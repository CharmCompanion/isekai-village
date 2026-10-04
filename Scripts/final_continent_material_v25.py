import unreal
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');R='/Game/IsekaiVillage/AdventureWorld';M=unreal.MaterialEditingLibrary;A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools()
name='M_IV_LivingContinent_Final25';path=R+'/Materials/'+name
mat=unreal.load_asset(path) if A.does_asset_exist(path) else T.create_asset(name,R+'/Materials',unreal.Material,unreal.MaterialFactoryNew());M.delete_all_material_expressions(mat)
def custom(code,typ,inputs):
 node=M.create_material_expression(mat,unreal.MaterialExpressionCustom);pins=[]
 for key in inputs:
  p=unreal.CustomInput();p.set_editor_property('input_name',key);pins.append(p)
 node.set_editor_property('inputs',pins);node.set_editor_property('output_type',typ);node.set_editor_property('code',code)
 for key,(n,out) in inputs.items():assert M.connect_material_expressions(n,out,node,key),key
 return node
pos=M.create_material_expression(mat,unreal.MaterialExpressionWorldPosition);normal=M.create_material_expression(mat,unreal.MaterialExpressionVertexNormalWS)
uv=custom('return (WorldPos.xy/100.+12000.)/24000.;',unreal.CustomMaterialOutputType.CMOT_FLOAT2,{'WorldPos':(pos,'')})
samples=[]
faruv=custom('return float2((-WorldPos.x/8000.+814.174101)/1758.,(638.308916-WorldPos.y/8000.)/1185.);',unreal.CustomMaterialOutputType.CMOT_FLOAT2,{'WorldPos':(pos,'')})
for index,tex in enumerate(['T_IV_ContinentAtlas25','T_IV_WorldBiomes25']):
 n=M.create_material_expression(mat,unreal.MaterialExpressionTextureSample);n.set_editor_property('texture',unreal.load_asset(R+'/Textures/'+tex));n.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR);assert M.connect_material_expressions(uv if index==0 else faruv,'',n,'UVs');samples.append(n)
rock_samples=[]
for plane in ['yz','xz','xy']:
 coord=custom('return (WorldPos+float3(0,0,2000000.)).'+plane+'/18000.;',unreal.CustomMaterialOutputType.CMOT_FLOAT2,{'WorldPos':(pos,'')})
 tex=M.create_material_expression(mat,unreal.MaterialExpressionTextureSample)
 tex.set_editor_property('texture',unreal.load_asset('/Game/SoStylized/Environment/Rocks/Textures/Spire/T_RockSpire_BC'))
 tex.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
 M.connect_material_expressions(coord,'',tex,'UVs');rock_samples.append(tex)
code="""
float3 p=WorldPos/100.;
float3 n=normalize(SurfaceNormal);
float shade=.33+.67*saturate(dot(n,normalize(float3(-.6,-.4,1.))));
float radial=pow(pow(abs(p.x/580.),4.)+pow(abs((p.y-20.)/570.),4.),.25);
float blend=smoothstep(8000.,15000.,length(p.xy));
float3 distant=DistantColor;
float3 ground=lerp(NearColor,distant,blend);
float depth=saturate((-20000.-p.z)/900.);
float3 weights=pow(abs(n),4.);weights/=max(dot(weights,1.),.001);
float3 painted=RockX*weights.x+RockY*weights.y+RockZ*weights.z;
float3 q=(p+float3(0,0,20000.))/145.;float3 cell=floor(q);float3 f=frac(q);f=f*f*(3.-2.*f);float macro=0.;
for(int i=0;i<2;i++)for(int j=0;j<2;j++)for(int k=0;k<2;k++){
 float3 c=float3(i,j,k);float h=frac(sin(dot(cell+c,float3(127.1,311.7,74.7)))*43758.5453);
 float3 w=lerp(1.-f,f,c);macro+=h*w.x*w.y*w.z;
}
float3 stone=lerp(float3(.19,.205,.20),painted*float3(.8,.82,.77),.38);
stone*=lerp(.88,1.08,macro)*lerp(1.,.50,depth);
float exposure=(1.-smoothstep(.99,1.09,radial))*(1.-smoothstep(-20100.,-19980.,p.z));
exposure=max(exposure,(1.-smoothstep(1.0,1.2,radial))*(1.-smoothstep(.45,.8,n.z)));
ground=lerp(ground,stone,exposure);
return ground*lerp(shade,1.,max(exposure,1.-smoothstep(1600.,2400.,length(p.xy))));
"""
col=custom(code,unreal.CustomMaterialOutputType.CMOT_FLOAT3,{'WorldPos':(pos,''),'SurfaceNormal':(normal,''),'NearColor':(samples[0],'RGB'),'DistantColor':(samples[1],'RGB'),'RockX':(rock_samples[0],'RGB'),'RockY':(rock_samples[1],'RGB'),'RockZ':(rock_samples[2],'RGB')})
mask=custom('float2 p=WorldPos.xy/100.;float r=pow(pow(abs(p.x/580.),4.)+pow(abs((p.y-20.)/570.),4.),.25);return max(1.-smoothstep(1.,1.10,r),1.-smoothstep(1600.,2400.,length(p)));',unreal.CustomMaterialOutputType.CMOT_FLOAT1,{'WorldPos':(pos,'')})
base=custom('return C*Mask;',unreal.CustomMaterialOutputType.CMOT_FLOAT3,{'C':(col,''),'Mask':(mask,'')})
emissive=custom('return C*lerp(1.,.075,Mask);',unreal.CustomMaterialOutputType.CMOT_FLOAT3,{'C':(col,''),'Mask':(mask,'')})
M.connect_material_property(base,'',unreal.MaterialProperty.MP_BASE_COLOR)
M.connect_material_property(emissive,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
for prop,val in [(unreal.MaterialProperty.MP_ROUGHNESS,.95),(unreal.MaterialProperty.MP_SPECULAR,0.)]:
 node=M.create_material_expression(mat,unreal.MaterialExpressionConstant);node.set_editor_property('r',val);M.connect_material_property(node,'',prop)
mat.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_DEFAULT_LIT);M.recompile_material(mat);A.save_loaded_asset(mat)
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name()=='SM_IV_PuzzleContinent_v25':a.static_mesh_component.set_material(0,mat)
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if isinstance(a,unreal.ExponentialHeightFog):
  c=a.get_component_by_class(unreal.ExponentialHeightFogComponent)
  a.set_actor_location(unreal.Vector(0,0,-2000000),False,False)
  c.set_editor_property('fog_density',.00018)
  c.set_editor_property('fog_height_falloff',.001)
  c.set_editor_property('fog_max_opacity',.98)
  c.set_editor_property('start_distance',4500000.)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
exec(compile((B/'Scripts/render_puzzle_continent_v25.py').read_text(),'final material review','exec'),{'__name__':'__main__'})


