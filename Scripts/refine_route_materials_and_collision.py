import unreal,json,math
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');R='/Game/IsekaiVillage/AdventureWorld';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);A=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;T=unreal.AssetToolsHelpers.get_asset_tools()
def material(name,texture,tint):
    path=R+'/Materials/'+name
    mat=unreal.load_asset(path) if A.does_asset_exist(path) else T.create_asset(name,R+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
    M.delete_all_material_expressions(mat)
    def node(cls,**props):
        n=M.create_material_expression(mat,cls)
        for k,v in props.items():n.set_editor_property(k,v)
        return n
    pos=node(unreal.MaterialExpressionWorldPosition);normal=node(unreal.MaterialExpressionVertexNormalWS)
    def custom(code,inputs,kind):
        pins=[]
        for key in inputs:
            pin=unreal.CustomInput();pin.set_editor_property('input_name',key);pins.append(pin)
        n=node(unreal.MaterialExpressionCustom,code=code,inputs=pins,output_type=kind)
        for key,(src,out) in inputs.items():M.connect_material_expressions(src,out,n,key)
        return n
    samples=[]
    for axes in ['xy','xz','yz']:
        uv=custom('return P.'+axes+'/400.;',{'P':(pos,'')},unreal.CustomMaterialOutputType.CMOT_FLOAT2)
        tex=node(unreal.MaterialExpressionTextureSample,texture=unreal.load_asset(texture),sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_COLOR);M.connect_material_expressions(uv,'',tex,'UVs');samples.append(tex)
    c=custom('float3 w=pow(abs(N),4);w/=max(dot(w,1),.001); return (A*w.z+B*w.y+C*w.x)*float3('+','.join(map(str,tint))+');',{'N':(normal,''),'A':(samples[0],'RGB'),'B':(samples[1],'RGB'),'C':(samples[2],'RGB')},unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    M.connect_material_property(c,'',unreal.MaterialProperty.MP_BASE_COLOR)
    glow=custom('return C*.09;',{'C':(c,'')},unreal.CustomMaterialOutputType.CMOT_FLOAT3);M.connect_material_property(glow,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    rough=node(unreal.MaterialExpressionConstant,r=.87);M.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS);mat.set_editor_property('two_sided',True);M.recompile_material(mat);A.save_loaded_asset(mat);return mat
stone=material('M_IV_CaveStone','/Game/SoStylized/Environment/Rocks/Textures/Classic/T_RockClassic_Rocks_BC',(.72,.78,.83))
wood=material('M_IV_MineTimber','/Game/Fantastic_Village_Pack/textures/T_wood_03_BC',(.95,.82,.67))
clones={}
for a in E.get_all_level_actors():
    if not isinstance(a,unreal.StaticMeshActor):continue
    folder=str(a.get_folder_path());label=a.get_actor_label()
    if folder.startswith('Adventure/Routes/'):
        if 'continuous walkable tunnel' in label or 'stone portal' in label or 'far-side exit' in label:a.static_mesh_component.set_material(0,stone)
        if label in ['Mine timber entrance','Mine support bay']:a.static_mesh_component.set_material(0,wood)
        if 'stone portal' in label or 'far-side exit' in label or label in ['Mine timber entrance','Mine support bay']:
            original=a.static_mesh_component.static_mesh;key=original.get_name()
            if key not in clones:
                dest=R+'/Meshes/Routes/'+key+'_OpenCollision';m=unreal.load_asset(dest) if A.does_asset_exist(dest) else A.duplicate_asset(original.get_path_name(),dest)
                m.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);A.save_loaded_asset(m);clones[key]=m
            a.static_mesh_component.set_static_mesh(clones[key])
        if label=='Waterfall ledge':
            p=a.get_actor_location();o,ext=a.get_actor_bounds(False);bottom=o.z-ext.z;a.set_actor_scale3d(unreal.Vector(.27,.27,.65));box=a.static_mesh_component.static_mesh.get_bounding_box();a.set_actor_location(unreal.Vector(p.x,p.y,bottom-box.min.z*.65),False,False)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
plan=json.loads((B/'Saved/AdventureWorldSource/mountain_routes_v04.json').read_text());world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
ignored=[a for a in E.get_all_level_actors() if a.get_actor_label()=='Ancient Magical Seal'];out={}
for route in plan['routes']:
    points=route['points'];checks=[]
    for i,(p,q) in enumerate(zip(points[:-2],points[1:-1])):
        hit=unreal.SystemLibrary.capsule_trace_single(world,unreal.Vector(p[0]*100,p[1]*100,p[2]*100+120),unreal.Vector(q[0]*100,q[1]*100,q[2]*100+120),35,90,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,ignored,unreal.DrawDebugTrace.NONE,True)
        if hit and hit.to_tuple()[0]:checks.append({'segment':i,'hit':str(hit.to_tuple())})
    out[route['name']]={'segments_checked':len(points)-2,'blocked':checks}
(B/'Saved/tunnel_clearance_review.json').write_text(json.dumps(out,indent=2))
eye=unreal.Vector(-32800,-6100,6750);unreal.EditorLevelLibrary.set_level_viewport_camera_info(eye,unreal.MathLibrary.find_look_at_rotation(eye,unreal.Vector(-36400,-8500,5950)))
