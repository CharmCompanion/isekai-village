"""Private masonry materials, original district mesh, temporary native review."""
import unreal,json,time
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain42';D='/Game/IsekaiVillage/AdventureWorld/Gosain42';R='/Game/IsekaiVillage/AdventureWorld'
A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();M=unreal.MaterialEditingLibrary;E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
def node(m,cls):return M.create_material_expression(m,cls)
def custom(m,code,inputs,typ):
    n=node(m,unreal.MaterialExpressionCustom);pins=[]
    for k in inputs:p=unreal.CustomInput();p.set_editor_property('input_name',k);pins.append(p)
    n.set_editor_property('inputs',pins);n.set_editor_property('output_type',typ);n.set_editor_property('code',code)
    for k,v in inputs.items():assert M.connect_material_expressions(v,'',n,k)
    return n
def material(name,color,texture=None):
    path=D+'/Materials/M_Gosain42_'+name;m=unreal.load_asset(path) if A.does_asset_exist(path) else T.create_asset('M_Gosain42_'+name,D+'/Materials',unreal.Material,unreal.MaterialFactoryNew());M.delete_all_material_expressions(m)
    if texture:
        p=node(m,unreal.MaterialExpressionWorldPosition);n=node(m,unreal.MaterialExpressionVertexNormalWS);samples=[]
        for axis in ['yz','xz','xy']:
            uv=custom(m,'return P.'+axis+'/260.;',{'P':p},unreal.CustomMaterialOutputType.CMOT_FLOAT2);s=node(m,unreal.MaterialExpressionTextureSample);s.texture=unreal.load_asset(texture);assert s.texture;assert M.connect_material_expressions(uv,'',s,'UVs');samples.append(s)
        c=custom(m,'float3 w=pow(abs(N),4);w/=max(w.x+w.y+w.z,.0001);float3 t=A*w.x+B*w.y+C*w.z;float l=dot(t,float3(.2126,.7152,.0722));return float3(%s,%s,%s)*(.66+l*.65);'%tuple(color),{'N':n,'A':samples[0],'B':samples[1],'C':samples[2]},unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    else:c=node(m,unreal.MaterialExpressionConstant3Vector);c.constant=unreal.LinearColor(*color,1)
    assert M.connect_material_property(c,'',unreal.MaterialProperty.MP_BASE_COLOR)
    rough=node(m,unreal.MaterialExpressionConstant);rough.r=.88;assert M.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS);M.recompile_material(m);A.save_loaded_asset(m);return m
tex='/Game/Fantastic_Village_Pack/textures/T_wall_02_BC'
mats={k:material(k,c,tex) for k,c in {'limestone':(.54,.49,.39),'ivory':(.66,.62,.50),'aged':(.39,.37,.30),'warmstone':(.55,.45,.33),'trim':(.7,.65,.53),'roofstone':(.35,.33,.28),'foundation':(.38,.36,.3)}.items()}
mats.update(recess=material('recess',(.018,.026,.027)),mullion=material('mullion',(.15,.16,.14)),joint=material('joint',(.27,.25,.21)),paving=unreal.load_asset(R+'/Gosain37/Materials/M_Gosain37_paving'))
q=json.loads((O/'district.json').read_text())['mesh'];name=q['name'];task=unreal.AssetImportTask();task.filename=str(O/(name+'.obj'));task.destination_path=D+'/Meshes';task.destination_name=name;task.automated=True;task.replace_existing=True;task.save=True
op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;op.static_mesh_import_data.generate_lightmap_u_vs=False;op.static_mesh_import_data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS;task.options=op
T.import_asset_tasks([task]);mesh=unreal.load_asset(D+'/Meshes/'+name);assert mesh
for i,s in enumerate(mesh.static_materials):mesh.set_material(i,mats[str(s.material_slot_name)])
A.save_loaded_asset(mesh)
# Preview above the same region, leaving the live world unchanged until checked.
origin=[q['origin_m'][0],q['origin_m'][1],-19000]
a=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*[v*100 for v in origin]),transient=True);a.static_mesh_component.set_static_mesh(mesh);a.set_actor_label('TEMP Gosain42 road-grown district review')
output=B/'Docs/WorldDesign/Gosain42';output.mkdir(exist_ok=True)
views=[('District_Aerial',(-150,-350,140),(-350,-100,16)),('District_Reverse',(-550,110,110),(-350,-90,16)),('District_Street',(-414,-185,5),(-385,-155,13))]
s={'i':0,'phase':0,'next':time.monotonic()+25,'done':[]};h={}
def tick(dt):
    if time.monotonic()<s['next']:return
    if s['i']>=len(views):
        E.destroy_actor(a);unreal.unregister_slate_post_tick_callback(h['h']);(output/'review_complete.json').write_text(json.dumps({'status':'captured','files':s['done'],'mesh':mesh.get_path_name(),'temporary_actor_removed':True}));return
    name,eye,target=views[s['i']]
    if s['phase']==0:
        p=unreal.Vector(*[(origin[j]+eye[j])*100 for j in range(3)]);q=unreal.Vector(*[(origin[j]+target[j])*100 for j in range(3)]);unreal.EditorLevelLibrary.set_level_viewport_camera_info(p,unreal.MathLibrary.find_look_at_rotation(p,q));s.update(phase=1,next=time.monotonic()+10)
    elif s['phase']==1:
        path=output/(name+'.png');s.update(phase=2,next=time.monotonic()+2,started=time.monotonic(),old=path.stat().st_mtime if path.exists() else 0);unreal.AutomationLibrary.take_high_res_screenshot(1600,1000,str(path),delay=.5)
    else:
        path=output/(name+'.png')
        if path.exists() and path.stat().st_mtime>s['old']:s['done'].append(str(path));s.update(i=s['i']+1,phase=0,next=time.monotonic()+2)
        elif time.monotonic()-s['started']>60:s['done'].append('FAILED '+name);s.update(i=s['i']+1,phase=0,next=time.monotonic()+2)
h['h']=unreal.register_slate_post_tick_callback(tick)
