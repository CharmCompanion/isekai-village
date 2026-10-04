import unreal,json,math,struct
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource';R='/Game/IsekaiVillage/AdventureWorld'
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();M=unreal.MaterialEditingLibrary
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_path_name().startswith(R+'/Maps/Map_AnimeAdventure.')
assert not any('IVMountainRoutesV04' in [str(t) for t in a.tags] for a in E.get_all_level_actors()),'Route actors already exist'
plan=json.loads((S/'mountain_routes_v04.json').read_text());raw=struct.unpack('<'+'H'*1009**2,(S/'IV_Adventure_Layered_v05.r16').read_bytes())
def h(x,y):return (raw[round((y+600)*.84)*1009+round((x+600)*.84)]-32768)/64
def tag(a,name,folder):a.set_actor_label(name);a.set_folder_path('Adventure/Routes/'+folder);a.set_editor_property('tags',[unreal.Name('IVMountainRoutesV04')]);return a
def mesh(path,p,scale=(1,1,1),yaw=0,name='Route detail',folder='Details',ground=False):
    m=unreal.load_asset(path);assert m,path
    x,y,z=p
    if ground:z-=m.get_bounding_box().min.z*scale[2]/100
    a=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(x*100,y*100,z*100),unreal.Rotator(yaw=yaw));a.static_mesh_component.set_static_mesh(m);a.set_actor_scale3d(unreal.Vector(*scale));return tag(a,name,folder)
def frame(points,i):
    p=points[i];prev=points[max(0,i-1)];nxt=points[min(len(points)-1,i+1)];dx=nxt[0]-prev[0];dy=nxt[1]-prev[1];length=math.hypot(dx,dy);f=(dx/length,dy/length);right=(f[1],-f[0]);yaw=math.degrees(math.atan2(-f[0],f[1]));return p,f,right,yaw
def offset(p,f,r,x,y,z=0):return [p[0]+r[0]*x+f[0]*y,p[1]+r[1]*x+f[1]*y,p[2]+z]
def light(p,color,folder):
    a=E.spawn_actor_from_class(unreal.PointLight,unreal.Vector(*(v*100 for v in p)));c=a.get_component_by_class(unreal.PointLightComponent)
    c.set_editor_property('intensity',450);c.set_editor_property('attenuation_radius',1000);c.set_editor_property('light_color',unreal.Color(*color,255));c.set_editor_property('cast_shadows',False);tag(a,'Tunnel lantern glow',folder)
arch='/Game/StylizedIsland/Mesh/Props/SM_Arch/SM_Stylized_Arch_Mesh/SM_Stylized_Arch'
gate='/Game/Fantastic_Village_Pack/meshes/props/construction/SM_PROP_wall_wood_gate_frame_01'
lamp='/Game/Fantastic_Village_Pack/meshes/props/light/SM_PROP_lantern_01'
stone=unreal.load_asset('/Game/SoStylized/Environment/Rocks/Materials/Classic/MI_RockClassic_Cliff')
counts={}
for route in plan['routes']:
    name=route['name'];points=route['points'];task=unreal.AssetImportTask();task.filename=str(S/(route['mesh']+'.obj'));task.destination_path=R+'/Meshes/Routes';task.destination_name=route['mesh'];task.automated=True;task.replace_existing=True;task.save=True
    options=unreal.FbxImportUI();options.set_editor_property('import_materials',False);options.set_editor_property('import_textures',False);options.static_mesh_import_data.set_editor_property('combine_meshes',True);options.static_mesh_import_data.set_editor_property('auto_generate_collision',False);task.options=options;T.import_asset_tasks([task])
    path=R+'/Meshes/Routes/'+route['mesh'];m=unreal.load_asset(path);assert m,path
    body=m.get_editor_property('body_setup');body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);A.save_loaded_asset(m)
    a=mesh(path,[0,0,0],name=name+' - continuous walkable tunnel',folder=name);a.static_mesh_component.set_material(0,stone)
    p,f,right,yaw=frame(points,0)
    if name=='Mine':mesh(gate,p,(.8,.95,.75),yaw+90,'Mine timber entrance',name,True)
    else:mesh(arch,p,(2.1,2.1,2.1) if name=='TradePass' else (2.3,2.3,2.3),yaw,name+' stone portal',name,True)
    if name=='TradePass':
        ep,ef,er,ey=frame(points,len(points)-1);mesh(arch,ep,(2.1,2.1,2.1),ey+180,'Trade tunnel - far-side exit',name,True)
    # Lit, repeated support bays show depth and scale from the entrance.
    for i in range(3,len(points)-2,5 if name=='TradePass' else 4):
        q,qf,qr,qy=frame(points,i);side=route['halfwidth']-.65
        if name=='Mine':mesh(gate,q,(.55,.88,.72),qy+90,'Mine support bay',name,True)
        lp=offset(q,qf,qr,side,0,3.15);mesh(lamp,lp,(.8,.8,.8),qy,'Passage lantern',name);light(lp,(255,191,104) if name!='Dungeon' else (100,162,255),name)
    # Cargo at the trade mouth, tools/supplies at the mine, stone markers at the dungeon.
    for sx,sy in [(-7,-7),(-7,-4),(7,-5)]:
        q=offset(p,f,right,sx,sy);q[2]=h(q[0],q[1]);mesh('/Game/AdvancedVillagePack/Meshes/SM_Crate_Closed',q,(1,1,1),yaw+15,name+' supply crate',name,True)
    for side in [-1,1]:
        q=offset(p,f,right,side*(route['halfwidth']+2.5),2);q[2]=h(q[0],q[1]);mesh('/Game/SoStylized/Environment/Rocks/Classic/SM_BoulderClassic1',q,(2.4,2.1,2.7),yaw+side*20,'Entrance shoulder rock',name,True)
    if name=='Mine':
        for i in [8,13,18,22]:
            q,qf,qr,qy=frame(points,i);v=offset(q,qf,qr,-2.4,0,.2);mesh('/Game/StylizedIsland/Mesh/Props/SM_Crystals/SM_Stylized_Crystals_Mesh/SM_Stylized_Crystal_03_CrystalC',v,(1.2,1.2,1.2),qy,'Mine crystal seam',name,True)
    counts[name]=len(points)
# Move the existing magical barrier into the right-hand dungeon, behind its real entrance.
dun=next(r for r in plan['routes'] if r['name']=='Dungeon');p,f,right,yaw=frame(dun['points'],6)
seal=next(a for a in E.get_all_level_actors() if a.get_actor_label()=='Ancient Magical Seal')
seal.set_actor_scale3d(unreal.Vector(3.4,3.4,3.4));o,ext=seal.get_actor_bounds(False)
seal.set_actor_rotation(unreal.Rotator(yaw=yaw),False);seal.set_actor_location(unreal.Vector(p[0]*100,p[1]*100,(p[2]+4.1)*100),False,False);seal.set_folder_path('Adventure/Routes/Dungeon')
# The earlier northwest waterfall stays as a mine-side spring; this cascade screens the dungeon.
fall=mesh('/Game/SoStylized/Environment/Water/Waterfalls/SM_Waterfall1',[222,447,113.8],(1.25,1.3,7),yaw,'Dungeon waterfall curtain','Dungeon')
fall.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
pool=mesh('/Engine/BasicShapes/Cylinder',[219,438,113.8],(11,16,.001),0,'Dungeon spring pool','Dungeon');pool.static_mesh_component.set_material(0,unreal.load_asset('/Game/SoStylized/Environment/Water/Materials/MI_Water'));pool.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
for x,y,s in [(218,450,.6),(220,457,.65)]:
    mesh('/Game/SoStylized/Environment/Rocks/Classic/SM_CliffClassic1',[x,y,h(x,y)],(s,s,s),25,'Waterfall ledge','Dungeon',True)
# Clear semantic wayfinding on the original branches.
labels={'West Ridge':'Western Trade Pass','Whisperwood Trail':'Whisperwood Mine Road','Crown Pass':'Sealed Dungeon Expedition Trail'}
for a in E.get_all_level_actors():
    if a.get_actor_label() in labels:a.set_actor_label(labels[a.get_actor_label()])
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(B/'Saved/mountain_entrances_result.json').write_text(json.dumps({'saved':True,'routes':counts,'collision':'ComplexAsSimple open tunnel shells','trade_exit':plan['trade_exit'][-1]},indent=2))
eye=unreal.Vector(-32600,-6000,7300);unreal.EditorLevelLibrary.set_level_viewport_camera_info(eye,unreal.MathLibrary.find_look_at_rotation(eye,unreal.Vector(-36600,-8700,5950)))
