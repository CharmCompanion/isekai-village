import unreal,json,time
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain41';D='/Game/IsekaiVillage/AdventureWorld/Gosain41';R='/Game/IsekaiVillage/AdventureWorld';A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();M=unreal.MaterialEditingLibrary;E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
def node(mat,cls):return M.create_material_expression(mat,cls)
def const(mat,x):n=node(mat,unreal.MaterialExpressionConstant);n.r=x;return n
def custom(mat,code,inputs,typ):
    n=node(mat,unreal.MaterialExpressionCustom);pins=[]
    for k in inputs:p=unreal.CustomInput();p.set_editor_property('input_name',k);pins.append(p)
    n.set_editor_property('inputs',pins);n.set_editor_property('output_type',typ);n.set_editor_property('code',code)
    for k,v in inputs.items():assert M.connect_material_expressions(v,'',n,k)
    return n
def material(name,color,texture=None):
    path=D+'/Materials/M_Gosain41_'+name;m=unreal.load_asset(path) if A.does_asset_exist(path) else T.create_asset('M_Gosain41_'+name,D+'/Materials',unreal.Material,unreal.MaterialFactoryNew());M.delete_all_material_expressions(m)
    if texture:
        p=node(m,unreal.MaterialExpressionWorldPosition);n=node(m,unreal.MaterialExpressionVertexNormalWS);samples=[]
        for axis in ['yz','xz','xy']:
            uv=custom(m,'return P.'+axis+'/350.;',{'P':p},unreal.CustomMaterialOutputType.CMOT_FLOAT2);s=node(m,unreal.MaterialExpressionTextureSample);s.texture=unreal.load_asset(texture);assert s.texture;M.connect_material_expressions(uv,'',s,'UVs');samples.append(s)
        c=custom(m,'float3 w=pow(abs(N),4);w/=max(w.x+w.y+w.z,.0001);return (A*w.x+B*w.y+C*w.z)*float3(%s,%s,%s);'%tuple(color),{'N':n,'A':samples[0],'B':samples[1],'C':samples[2]},unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    else:c=node(m,unreal.MaterialExpressionConstant3Vector);c.constant=unreal.LinearColor(*color,1)
    M.connect_material_property(c,'',unreal.MaterialProperty.MP_BASE_COLOR);M.connect_material_property(const(m,.82),'',unreal.MaterialProperty.MP_ROUGHNESS);M.recompile_material(m);A.save_loaded_asset(m);return m
mats={k:unreal.load_asset(R+'/Gosain37/Materials/M_Gosain37_'+k) for k in ['stone','trim','foundation','paving']}
mats.update(plaster=material('Plaster',(.95,.82,.65),'/Game/Fantastic_Village_Pack/textures/T_wall_02_BC'),wood=material('Wood',(.65,.49,.32),'/Game/Fantastic_Village_Pack/textures/T_wood_05_BC'),window=material('Window',(.018,.038,.045)),awning=material('Awning',(.48,.23,.08)),roof=unreal.load_asset(R+'/Gosain39/Materials/M_Gosain39_Terracotta'))
q=json.loads((O/'urban_block.json').read_text())['mesh'];name=q['name'];task=unreal.AssetImportTask();task.filename=str(O/(name+'.obj'));task.destination_path=D+'/Meshes';task.destination_name=name;task.automated=True;task.replace_existing=True;task.save=True
op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;op.static_mesh_import_data.generate_lightmap_u_vs=False;task.options=op;T.import_asset_tasks([task]);mesh=unreal.load_asset(D+'/Meshes/'+name);assert mesh
for i,s in enumerate(mesh.static_materials):mesh.set_material(i,mats[str(s.material_slot_name)])
A.save_loaded_asset(mesh)
# Isolated, temporary native preview; does not replace or save world actors.
origin=(22173.92809189915,41624.713312447166,-19000)
a=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*[v*100 for v in origin]),transient=True);a.static_mesh_component.set_static_mesh(mesh);a.set_actor_label('TEMP Gosain connected block review')
output=B/'Docs/WorldDesign/Gosain41';output.mkdir(exist_ok=True)
views=[('Block_Aerial',(110,-125,90),(0,0,10)),('Block_Arcade',(0,-60,4),(0,-25,9)),('Block_Courtyard',(0,0,3),(22,28,12)),('Block_Reverse',(-100,110,65),(0,0,10))]
s={'i':0,'phase':0,'next':time.monotonic()+20,'done':[]};h={}
def tick(dt):
    if time.monotonic()<s['next']:return
    if s['i']>=len(views):
        E.destroy_actor(a);unreal.unregister_slate_post_tick_callback(h['h']);(output/'review_complete.json').write_text(json.dumps({'status':'captured','files':s['done'],'mesh':mesh.get_path_name(),'world_placement':'not applied; temporary preview removed'}));return
    name,eye,target=views[s['i']]
    if s['phase']==0:
        p=unreal.Vector(*[(origin[j]+eye[j])*100 for j in range(3)]);q=unreal.Vector(*[(origin[j]+target[j])*100 for j in range(3)]);unreal.EditorLevelLibrary.set_level_viewport_camera_info(p,unreal.MathLibrary.find_look_at_rotation(p,q));s.update(phase=1,next=time.monotonic()+15)
    elif s['phase']==1:
        path=output/(name+'.png');s.update(phase=2,next=time.monotonic()+2,started=time.monotonic(),old=path.stat().st_mtime if path.exists() else 0)
        unreal.AutomationLibrary.take_high_res_screenshot(1600,1000,str(path),delay=.5)
    else:
        path=output/(name+'.png')
        if path.exists() and path.stat().st_mtime>s['old']:
            s['done'].append(str(path));s.update(i=s['i']+1,phase=0,next=time.monotonic()+2)
        elif time.monotonic()-s['started']>60:
            s['done'].append('FAILED '+name);s.update(i=s['i']+1,phase=0,next=time.monotonic()+2)
h['h']=unreal.register_slate_post_tick_callback(tick)
