import unreal
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');R='/Game/IsekaiVillage/AdventureWorld';M=unreal.MaterialEditingLibrary;A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools()
name='M_IV_LivingContinent_Final19';path=R+'/Materials/'+name
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
for index,tex in enumerate(['T_IV_ContinentAtlas19','T_IV_ContinentAtlas19']):
 n=M.create_material_expression(mat,unreal.MaterialExpressionTextureSample);n.set_editor_property('texture',unreal.load_asset(R+'/Textures/'+tex));n.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR);assert M.connect_material_expressions(uv if index==0 else faruv,'',n,'UVs');samples.append(n)
code="""
float3 p=WorldPos/100.;
float3 n=normalize(SurfaceNormal);
float shade=.33+.67*saturate(dot(n,normalize(float3(-.6,-.4,1.))));
float radial=pow(pow(abs(p.x/580.),4.)+pow(abs((p.y-20.)/570.),4.),.25);
float blend=smoothstep(5500.,9500.,length(p.xy));
float wet=saturate((DistantColor.b-DistantColor.r)*14.);
float3 distant=lerp(DistantColor,float3(.12,.24,.075),wet);
distant=lerp(distant,float3(.10,.18,.085),.55);
float3 ground=lerp(NearColor,distant,blend);
float depth=saturate((-20000.-p.z)/900.);
float warp=12.*sin(p.x*.008)+8.*sin(p.y*.011)+5.*sin((p.x+p.y)*.033);
float beds=.5+.5*sin((p.z+warp)*.055);
float seam=1.-smoothstep(.025,.12,abs(frac((p.z+warp)/48.)-.5));
float grain=.5+.25*sin(p.x*.12+p.z*.07)*sin(p.y*.15-p.z*.17)+.25*sin(p.x*.029+p.y*.035+p.z*.041);
float3 stone=lerp(float3(.15,.125,.095),float3(.29,.265,.215),beds*.22+grain*.55);
stone*=1.-seam*.08;
stone*=lerp(1.,.48,depth);
float exposure=(1.-smoothstep(.99,1.09,radial))*(1.-smoothstep(-20100.,-19980.,p.z));
exposure=max(exposure,(1.-smoothstep(1.0,1.2,radial))*(1.-smoothstep(.45,.8,n.z)));
ground=lerp(ground,stone,exposure);
return ground*shade;
"""
col=custom(code,unreal.CustomMaterialOutputType.CMOT_FLOAT3,{'WorldPos':(pos,''),'SurfaceNormal':(normal,''),'NearColor':(samples[0],'RGB'),'DistantColor':(samples[1],'RGB')})
assert M.connect_material_property(col,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR);mat.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT);M.recompile_material(mat);A.save_loaded_asset(mat)
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name()=='SM_IV_PuzzleContinent_v19':a.static_mesh_component.set_material(0,mat)
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if isinstance(a,unreal.ExponentialHeightFog):
  c=a.get_component_by_class(unreal.ExponentialHeightFogComponent)
  a.set_actor_location(unreal.Vector(0,0,-2000000),False,False)
  c.set_editor_property('fog_density',.00035)
  c.set_editor_property('fog_height_falloff',.001)
  c.set_editor_property('fog_max_opacity',.98)
  c.set_editor_property('start_distance',3000000.)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
exec(compile((B/'Scripts/render_puzzle_continent_v19.py').read_text(),'final material review','exec'),{'__name__':'__main__'})


