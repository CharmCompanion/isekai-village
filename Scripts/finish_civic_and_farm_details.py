import unreal,json,math
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource';R='/Game/IsekaiVillage/AdventureWorld'
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);A=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert not any('IVCivicV05' in [str(t) for t in a.tags] for a in E.get_all_level_actors()),'Civic details already exist'
def mesh(path,p,scale=(1,1,1),yaw=0,name='Civic detail',future=False):
    m=unreal.load_asset(path);x,y,z=p;z-=m.get_bounding_box().min.z*scale[2]/100
    a=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(x*100,y*100,z*100),unreal.Rotator(yaw=yaw));a.static_mesh_component.set_static_mesh(m);a.set_actor_scale3d(unreal.Vector(*scale));a.set_actor_label(name);a.set_folder_path('EraPreviews/LargeTown' if future else 'Village/Civic Gardens');a.set_editor_property('tags',[unreal.Name('IVCivicV05')]+([unreal.Name('IVFutureLargeTown')] if future else []))
    if future:a.static_mesh_component.set_visibility(False);a.set_actor_hidden_in_game(True);a.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    return a
# Existing wood gate frames flank a new continuous stone rampart mesh.
task=unreal.AssetImportTask();task.filename=str(S/'SM_LargeTown_Ramparts.obj');task.destination_path=R+'/Meshes/Civic';task.destination_name='SM_LargeTown_Ramparts';task.automated=True;task.save=True
options=unreal.FbxImportUI();options.set_editor_property('import_materials',False);options.set_editor_property('import_textures',False);options.static_mesh_import_data.set_editor_property('combine_meshes',True);options.static_mesh_import_data.set_editor_property('auto_generate_collision',False);task.options=options;T.import_asset_tasks([task])
sm=unreal.load_asset(R+'/Meshes/Civic/SM_LargeTown_Ramparts');sm.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);A.save_loaded_asset(sm)
name='M_IV_RampartStone';mat=T.create_asset(name,R+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
for path,prop,kind in [('/Game/StylizedIsland/Textures/Tile/T_Brick_Wall_C',unreal.MaterialProperty.MP_BASE_COLOR,unreal.MaterialSamplerType.SAMPLERTYPE_COLOR),('/Game/StylizedIsland/Textures/Tile/T_Brick_Wall_N',unreal.MaterialProperty.MP_NORMAL,unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)]:
    n=M.create_material_expression(mat,unreal.MaterialExpressionTextureSample);n.set_editor_property('texture',unreal.load_asset(path));n.set_editor_property('sampler_type',kind);M.connect_material_property(n,'RGB',prop)
rough=M.create_material_expression(mat,unreal.MaterialExpressionConstant);rough.set_editor_property('r',.82);M.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS);M.recompile_material(mat);A.save_loaded_asset(mat)
a=mesh(sm.get_path_name(),[0,0,0],name='Large Town - Ramparts and Gate Towers',future=True);a.set_actor_location(unreal.Vector(),False,False);a.static_mesh_component.set_material(0,mat)
import struct
raw=struct.unpack('<'+'H'*1009**2,(S/'IV_Adventure_Layered_v05.r16').read_bytes())
def h(x,y):return (raw[round((y+600)*.84)*1009+round((x+600)*.84)]-32768)/64
gates=json.loads((S/'civic_defenses.json').read_text())['gates']
for gate in gates:
    x,y=gate['xy'];mesh('/Game/Fantastic_Village_Pack/meshes/props/construction/SM_PROP_wall_wood_gate_frame_01',[x,y,h(x,y)],(1.4,2.,1.),gate['yaw'],gate['name']+' - Large Town',True)
# Four low stone flower beds leave radial road approaches clear.
flower='/Game/SoStylized/Environment/Foliage/SM_Flower_Allium'
stone='/Game/Fantastic_Village_Pack/meshes/props/construction/SM_PROP_wall_stone_small_01'
for angle in [55,145,235,325]:
    cx=22*math.cos(math.radians(angle));cy=22*math.sin(math.radians(angle))
    for dx in [-2,2]:mesh(stone,[cx+dx,cy,h(cx+dx,cy)],(.8,1.,.35),0,'Garden bed edging')
    for dy in [-1.5,1.5]:mesh(stone,[cx,cy+dy,h(cx,cy+dy)],(.8,1.33,.35),90,'Garden bed edging')
    for ix in range(5):
        for iy in range(3):
            x=cx-1.5+ix*.75;y=cy-.85+iy*.85;mesh(flower,[x,y,h(x,y)],(.9,.9,.9),ix*40+iy*55,'Plaza garden flowers')
# Replace the vegetable field's short-wheat stand-in with an existing cauliflower plant mesh.
ft=unreal.load_asset(R+'/Foliage/FT_FarmWheat');kept=[];removed=0
for a in E.get_all_level_actors():
    if isinstance(a,unreal.InstancedFoliageActor):
        for c in a.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent):
            if c.static_mesh!=ft.get_editor_property('mesh'):continue
            for i in range(c.get_instance_count()):
                tf=c.get_instance_transform(i,world_space=True);p=tf.translation
                if 13400<p.x<15800 and -15800<p.y<-13200:removed+=1
                else:kept.append(tf)
unreal.InstancedFoliageActor.remove_all_instances(w,ft);unreal.InstancedFoliageActor.add_instances(w,ft,kept)
veg=unreal.load_asset('/Game/Fantastic_Village_Pack/meshes/props/food/SM_PROP_food_cauliflower');box=veg.get_bounding_box();scale=65/max(box.max.x-box.min.x,box.max.y-box.min.y)
vf=T.create_asset('FT_FarmVegetables',R+'/Foliage',unreal.FoliageType_InstancedStaticMesh,unreal.FoliageType_InstancedStaticMeshFactory());vf.set_editor_property('mesh',veg);A.save_loaded_asset(vf)
trans=[]
for ix in range(13):
    for iy in range(15):
        x=146-10+ix*1.6;y=-145-11.2+iy*1.6
        trans.append(unreal.Transform(location=unreal.Vector(x*100,y*100,2450-box.min.z*scale),rotation=unreal.Rotator(yaw=(ix*37+iy*13)%360),scale=unreal.Vector(scale,scale,scale)))
unreal.InstancedFoliageActor.add_instances(w,vf,trans)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(B/'Saved/civic_completion_result.json').write_text(json.dumps({'saved':True,'future_gate_count':len(gates),'future_ramparts':'built and hidden in Village era','garden_beds':4,'vegetable_standins_replaced':removed,'vegetables':len(trans)},indent=2))
