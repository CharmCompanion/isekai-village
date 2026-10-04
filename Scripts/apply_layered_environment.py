import unreal,json,math,struct
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource';R='/Game/IsekaiVillage/AdventureWorld'
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);A=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;T=unreal.AssetToolsHelpers.get_asset_tools()
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_path_name().startswith(R+'/Maps/Map_AnimeAdventure.')
def tex(filename,name):
    task=unreal.AssetImportTask();task.filename=str(S/filename);task.destination_path=R+'/Textures';task.destination_name=name;task.automated=True;task.save=True;task.replace_existing=True;T.import_asset_tasks([task])
    a=unreal.load_asset(R+'/Textures/'+name)
    for p,v in [('srgb',False),('compression_settings',unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP),('mip_gen_settings',unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS),('filter',unreal.TextureFilter.TF_NEAREST if 'Height' in name else unreal.TextureFilter.TF_BILINEAR)]:a.set_editor_property(p,v)
    A.save_loaded_asset(a);return a
height=tex('T_IV_LayeredHeight_RG.png','T_IV_LayeredHeight_RG');biome=tex('T_IV_Biome_Layered_v05.png','T_IV_Biome_Layered_v05')
land=next(a for a in E.get_all_level_actors() if isinstance(a,unreal.Landscape))
rt=unreal.RenderingLibrary.create_render_target2d(w,1009,1009,unreal.TextureRenderTargetFormat.RTF_RGBA8);rt.set_editor_property('target_gamma',1.)
c,_,ctx=unreal.RenderingLibrary.begin_draw_canvas_to_render_target(w,rt)
c.draw_texture(height,unreal.Vector2D(),unreal.Vector2D(1009,1009),unreal.Vector2D(),unreal.Vector2D(1,1),unreal.LinearColor(1,1,1,1),unreal.BlendMode.BLEND_OPAQUE)
unreal.RenderingLibrary.end_draw_canvas_to_render_target(w,ctx)
assert land.landscape_import_heightmap_from_render_target(rt,True,0);land.force_layers_full_update()
name='M_IV_Landscape_Layered';mat=unreal.load_asset(R+'/Materials/'+name) if A.does_asset_exist(R+'/Materials/'+name) else T.create_asset(name,R+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
M.delete_all_material_expressions(mat)
def node(cls,**props):
    n=M.create_material_expression(mat,cls)
    for k,v in props.items():n.set_editor_property(k,v)
    return n
def custom(code,inputs,kind=unreal.CustomMaterialOutputType.CMOT_FLOAT3):
    pins=[]
    for key in inputs:
        pin=unreal.CustomInput();pin.set_editor_property('input_name',key);pins.append(pin)
    n=node(unreal.MaterialExpressionCustom,code=code,inputs=pins,output_type=kind)
    for key,(src,out) in inputs.items():assert M.connect_material_expressions(src,out,n,key)
    return n
pos=node(unreal.MaterialExpressionWorldPosition);normal=node(unreal.MaterialExpressionVertexNormalWS)
def uv(code):return custom(code,{'P':(pos,'')},unreal.CustomMaterialOutputType.CMOT_FLOAT2)
xy=uv('return P.xy/500.0;');xz=uv('return P.xz/500.0;');yz=uv('return P.yz/500.0;');paveuv=uv('return P.xy/250.0;')
mapuv=uv('return (P.xy+60000.0+59.52381)/120119.04762;')
def sample(path,coord,linear=False,norm=False):
    a=unreal.load_asset(path) if isinstance(path,str) else path;assert a,path
    n=node(unreal.MaterialExpressionTextureSample,texture=a,sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL if norm else unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR if linear else unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
    M.connect_material_expressions(coord,'',n,'UVs');return n
base='/Game/SoStylized/Environment/Landscape/Textures/'
g=sample(base+'T_Grass1_BC',xy);d=sample(base+'T_Dirt1_BC',xy);sand=sample(base+'T_Sand_BC',xy)
rock='/Game/SoStylized/Environment/Rocks/Textures/Classic/T_RockClassic_Rocks_BC'
rxy=sample(rock,xy);rxz=sample(rock,xz);ryz=sample(rock,yz)
mask=sample(biome,mapuv,True);pave=sample('/Game/StylizedIsland/Textures/Tile/T_Stone_Floor_BaseColor',paveuv)
soil=[]
for x,y in [(110,-145),(146,-145),(110,-181),(146,-181)]:soil.append(f'(1-smoothstep(11.3,12.0,abs(P.x/100.0-{x})))*(1-smoothstep(12.3,13.0,abs(P.y/100.0-({y}))))')
code='''float2 p=P.xy/100.0;
float macro=0.86+0.09*sin(p.x/39.0+sin(p.y/71.0))*cos(p.y/46.0)+0.05*sin((p.x+p.y)/11.0);
float grove=saturate(0.5+0.5*sin(p.x/87.0)*cos(p.y/61.0));
float3 c=G*lerp(float3(.68,.87,.69),float3(.78,.92,.60),grove)*macro;
float3 weights=pow(abs(N),4);weights/=max(dot(weights,1),.001);
float3 stone=Ryz*weights.x+Rxz*weights.y+Rxy*weights.z;
float strata=.84+.12*sin(P.z/510.0+sin(p.x/32.0));
stone*=lerp(float3(.64,.72,.80),float3(.86,.85,.81),saturate(P.z/26000.0))*strata;
c=lerp(c,D*float3(1.13,1.05,.90),Mask.r);
c=lerp(c,S*float3(1.06,1.01,.94),Mask.g);
c=lerp(c,stone,Mask.b);
float wet=1-smoothstep(10.0,175.0,P.z);c*=1-wet*.25;
c=lerp(c,float3(.73,.82,.86)*(0.94+0.06*macro),Mask.a);
float plaza=1-smoothstep(17.5,18.0,length(p));c=lerp(c,Pave*float3(1.08,1.05,1.0),plaza);
float farmSoil=saturate('''+'+'.join(soil)+''');c=lerp(c,c*float3(.40,.25,.13),farmSoil);
return c;'''
color=custom(code,{'P':(pos,''),'N':(normal,''),'G':(g,'RGB'),'D':(d,'RGB'),'S':(sand,'RGB'),'Rxy':(rxy,'RGB'),'Rxz':(rxz,'RGB'),'Ryz':(ryz,'RGB'),'Mask':(mask,'RGBA'),'Pave':(pave,'RGB')})
M.connect_material_property(color,'',unreal.MaterialProperty.MP_BASE_COLOR)
dn=sample(base+'T_Dirt1_N',xy,norm=True);sn=sample(base+'T_Sand_N',xy,norm=True);pn=sample('/Game/StylizedIsland/Textures/Tile/T_Stone_Floor_Normal',paveuv,norm=True)
detail=custom('float3 n=lerp(D,S,Mask.g); n=lerp(n,Pave,1-smoothstep(17.5,18.0,length(P.xy/100.0))); return normalize(lerp(float3(0,0,1),n,.52));',{'D':(dn,'RGB'),'S':(sn,'RGB'),'Pave':(pn,'RGB'),'Mask':(mask,'RGBA'),'P':(pos,'')})
M.connect_material_property(detail,'',unreal.MaterialProperty.MP_NORMAL)
rough=custom('return lerp(.86,.34,1-smoothstep(10.0,175.0,P.z));',{'P':(pos,'')},unreal.CustomMaterialOutputType.CMOT_FLOAT1)
M.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS)
M.recompile_material(mat);A.save_loaded_asset(mat);land.set_editor_property('landscape_material',mat)
# The old sea used a foam-overlay material. Replace it with the pack's actual ocean shader.
oceanmat=A.duplicate_asset('/Game/SoStylized/Environment/Water/Materials/MI_Ocean',R+'/Materials/MI_IV_CoastalOcean') if not A.does_asset_exist(R+'/Materials/MI_IV_CoastalOcean') else unreal.load_asset(R+'/Materials/MI_IV_CoastalOcean')
for k,v in {'Roughness':.22,'Specular':.35,'Water Murkiness':.28,'Water Scattering':.24,'Water Speed':.025,'Normal1 Flatness':.87,'Normal2 Flatness':.91,'Caustic Strength':18.,'Distance':180.,'Foam Multiply':1.4,'Distant Normal Start':10000.,'Distant Normal End':120000.}.items():M.set_material_instance_scalar_parameter_value(oceanmat,k,v)
M.set_material_instance_vector_parameter_value(oceanmat,'Scattering Color',unreal.LinearColor(.045,.22,.30,1))
A.save_loaded_asset(oceanmat)
sea=next(a for a in E.get_all_level_actors() if a.get_actor_label()=='Southern Sea')
sea.set_actor_scale3d(unreal.Vector(20000,20000,1));sea.static_mesh_component.set_material(0,oceanmat);sea.set_actor_label('Southern Sea - Coastal Ocean')
raw=struct.unpack('<'+'H'*1009**2,(S/'IV_Adventure_Layered_v05.r16').read_bytes())
def h(x,y):
    u=max(0,min(1007.999,(x+600)*.84));v=max(0,min(1007.999,(y+600)*.84));i=int(u);j=int(v);a=u-i;b=v-j
    value=(raw[j*1009+i]*(1-a)+raw[j*1009+i+1]*a)*(1-b)+(raw[(j+1)*1009+i]*(1-a)+raw[(j+1)*1009+i+1]*a)*b
    return (value-32768)/64
# Reground existing instanced vegetation after sculpting, omitting tunnel interiors.
routes=json.loads((S/'mountain_routes_v04.json').read_text());changes=0
def in_tunnel(x,y):
    for r in routes['routes']:
        if any(math.hypot(x-p[0],y-p[1])<r['halfwidth']+4 for p in r['points']):return True
    return ((x-219)/9)**2+((y-438)/13)**2<1
for path in A.list_assets(R+'/Foliage',recursive=False,include_folder=False):
    ft=unreal.load_asset(path)
    if not isinstance(ft,unreal.FoliageType_InstancedStaticMesh):continue
    kept=[]
    for a in E.get_all_level_actors():
        if not isinstance(a,unreal.InstancedFoliageActor):continue
        for comp in a.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent):
            if comp.static_mesh!=ft.get_editor_property('mesh'):continue
            for i in range(comp.get_instance_count()):
                tf=comp.get_instance_transform(i,world_space=True);p=tf.translation;x=p.x/100;y=p.y/100
                if in_tunnel(x,y):continue
                z=h(x,y)
                if z<2:continue
                tf.translation=unreal.Vector(p.x,p.y,z*100-(0 if 'Farm' in ft.get_name() else 12));kept.append(tf)
    unreal.InstancedFoliageActor.remove_all_instances(w,ft)
    if kept:unreal.InstancedFoliageActor.add_instances(w,ft,kept)
    changes+=len(kept)
for a in E.get_all_level_actors():
    if str(a.get_folder_path())=='Nature/Outcrops':
        p=a.get_actor_location();o,ext=a.get_actor_bounds(False);a.set_actor_location(unreal.Vector(p.x,p.y,p.z+h(p.x/100,p.y/100)*100-(o.z-ext.z)),False,False)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(B/'Saved/layered_environment_result.json').write_text(json.dumps({'saved':True,'vegetation_regrounded':changes,'landscape_material':mat.get_path_name(),'ocean_material':oceanmat.get_path_name()},indent=2))
eye=unreal.Vector(45000,-60000,39000);unreal.EditorLevelLibrary.set_level_viewport_camera_info(eye,unreal.MathLibrary.find_look_at_rotation(eye,unreal.Vector(0,4000,4000)))
