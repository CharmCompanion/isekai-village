import unreal,json,math,traceback
from pathlib import Path
ROOT='/Game/IsekaiVillage/AdventureWorld';BASE=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=BASE/'Saved/AdventureWorldSource'
plan=json.loads((BASE/'Content/IsekaiVillage/AdventureWorld/Design/SettlementGrid.json').read_text())
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();M=unreal.MaterialEditingLibrary
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert w.get_path_name().startswith(ROOT+'/Maps/Map_AnimeAdventure.')
report={'stage':'start'}
def checkpoint(stage):
    report['stage']=stage;(BASE/'Saved/farm_grid_result.json').write_text(json.dumps(report,indent=2));unreal.log('IV FARM/GRID: '+stage)
def load(path):
    a=unreal.load_asset(path);assert a,path;return a
def import_tex(filename,name):
    task=unreal.AssetImportTask();task.filename=str(S/filename);task.destination_path=ROOT+'/Textures';task.destination_name=name;task.automated=True;task.replace_existing=True;task.save=True
    T.import_asset_tasks([task]);tex=load(ROOT+'/Textures/'+name)
    for p,v in [('srgb',False),('compression_settings',unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP),('mip_gen_settings',unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS),('filter',unreal.TextureFilter.TF_BILINEAR if 'Biome' in name else unreal.TextureFilter.TF_NEAREST)]:tex.set_editor_property(p,v)
    A.save_loaded_asset(tex);return tex
def traceheight(x,y):
    ignored=[a for a in E.get_all_level_actors() if not isinstance(a,unreal.LandscapeProxy)]
    hit=unreal.SystemLibrary.line_trace_single(w,unreal.Vector(x*100,y*100,60000),unreal.Vector(x*100,y*100,-6000),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,ignored,unreal.DrawDebugTrace.NONE,True)
    assert hit,'No Landscape collision at '+str((x,y))
    return hit.to_tuple()[4].z/100
def mat(name,color):
    path=ROOT+'/Materials/'+name
    if A.does_asset_exist(path):return load(path)
    m=T.create_asset(name,ROOT+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
    n=M.create_material_expression(m,unreal.MaterialExpressionConstant3Vector);n.set_editor_property('constant',unreal.LinearColor(*color,1))
    M.connect_material_property(n,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR);m.set_editor_property('two_sided',True)
    M.recompile_material(m);A.save_loaded_asset(m);return m
def tag(a,name,folder):
    a.set_actor_label(name);a.set_folder_path(folder);a.set_editor_property('tags',[unreal.Name('IVFarmGridV02')]);return a
def mesh(path,x,y,z=None,yaw=0,scale=(1,1,1),name='Farm detail',folder='Farms/Organized'):
    m=load(path);ground=traceheight(x,y) if z is None else z
    a=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(x*100,y*100,ground*100),unreal.Rotator(yaw=yaw))
    a.static_mesh_component.set_static_mesh(m);a.set_actor_scale3d(unreal.Vector(*scale))
    a.set_actor_location(unreal.Vector(x*100,y*100,ground*100-m.get_bounding_box().min.z*scale[2]),False,False)
    return tag(a,name,folder)
def main():
    # Refresh only this task's farm/grid objects after a design revision.
    for a in list(E.get_all_level_actors()):
        if 'IVFarmGridV02' in [str(t) for t in a.tags]:E.destroy_actor(a)
    land=next(a for a in E.get_all_level_actors() if isinstance(a,unreal.Landscape))
    checkpoint('Updating farm soil and road texture')
    import_tex('T_IV_Biome_Farm_v02.png','T_IV_Biome')
    # Four small field terraces only; outside samples are identical to the saved source.
    tex=import_tex('T_IV_FarmHeight_RG.png','T_IV_FarmHeight_RG')
    rt=unreal.RenderingLibrary.create_render_target2d(w,1009,1009,unreal.TextureRenderTargetFormat.RTF_RGBA8)
    rt.set_editor_property('target_gamma',1.0)
    canvas,_,ctx=unreal.RenderingLibrary.begin_draw_canvas_to_render_target(w,rt)
    canvas.draw_texture(tex,unreal.Vector2D(0,0),unreal.Vector2D(1009,1009),unreal.Vector2D(0,0),unreal.Vector2D(1,1),unreal.LinearColor(1,1,1,1),unreal.BlendMode.BLEND_OPAQUE)
    unreal.RenderingLibrary.end_draw_canvas_to_render_target(w,ctx)
    assert land.landscape_import_heightmap_from_render_target(rt,True,0),'Height import rejected'
    land.force_layers_full_update()
    farmhouse=next(a for a in E.get_all_level_actors() if a.get_actor_label()=='Farmhouse')
    oldpos=farmhouse.get_actor_location();o,b=farmhouse.get_actor_bounds(False)
    bottom=o.z-b.z
    fx,fy=plan['farm']['farmhouse'];fz=plan['farm']['terrace_height']*100
    farmhouse.set_actor_location(unreal.Vector(fx*100,fy*100,oldpos.z+fz-bottom),False,False)
    for a in E.get_all_level_actors():
        if str(a.get_folder_path())=='Village/Props':
            p=a.get_actor_location()
            if math.hypot(p.x-oldpos.x,p.y-oldpos.y)<1900:
                a.set_actor_location(unreal.Vector(p.x+fx*100-oldpos.x,p.y+fy*100-oldpos.y,p.z+fz-bottom),False,False)
    L.save_current_level()
    checkpoint('Replacing farm fences and organizing four crop fields')
    # Only the old generated farm fence set is replaced; all village objects remain.
    old=[a for a in E.get_all_level_actors() if str(a.get_folder_path())=='Farms/Fences' and 'IVAdventureGenerated' in [str(t) for t in a.tags]]
    for a in old:E.destroy_actor(a)
    report['old_fences_replaced']=len(old)
    # Remove meadow foliage from cultivated soil and the service courtyard only.
    removed=0
    for ftpath in A.list_assets(ROOT+'/Foliage',recursive=False,include_folder=False):
        ft=load(ftpath)
        if not isinstance(ft,unreal.FoliageType_InstancedStaticMesh):continue
        if ft.get_name() in ['FT_FarmWheat','FT_FarmPumpkins']:
            unreal.InstancedFoliageActor.remove_all_instances(w,ft);continue
        kept=[];cut=0
        for a in E.get_all_level_actors():
            if not isinstance(a,unreal.InstancedFoliageActor):continue
            for c in a.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent):
                if c.static_mesh!=ft.get_editor_property('mesh'):continue
                for i in range(c.get_instance_count()):
                    tf=c.get_instance_transform(i,world_space=True);p=tf.translation;x=p.x/100;y=p.y/100
                    if 90<x<167 and -207<y<-85:cut+=1
                    else:kept.append(tf)
        if cut:
            unreal.InstancedFoliageActor.remove_all_instances(w,ft)
            unreal.InstancedFoliageActor.add_instances(w,ft,kept);removed+=cut
    report['farm_meadow_instances_removed']=removed
    fencepath='/Game/AdvancedVillagePack/Meshes/SM_Fence_Var01';fb=load(fencepath).get_bounding_box()
    along_x=(fb.max.x-fb.min.x)>=(fb.max.y-fb.min.y);length=max(fb.max.x-fb.min.x,fb.max.y-fb.min.y)
    wheat=[];pumpkins=[]
    # Source heights are used for newly terraced crop placement while collision refreshes.
    import struct
    raw=struct.unpack('<'+'H'*(1009*1009),(S/'IV_Adventure_Farm_v02.r16').read_bytes())
    def height(x,y):return (raw[round((y+600)/1200*1008)*1009+round((x+600)/1200*1008)]-32768)/64
    for f in plan['farm']['fields']:
        x,y=f['center'];inner=1 if x<128 else -1
        for dx in [-14,14]:
            for j in range(11):
                py=y-15+j*3
                if dx==inner*14 and abs(py-y)<4:continue
                scale=300/length
                mesh(fencepath,x+dx,py,z=height(x+dx,py),yaw=90 if along_x else 0,scale=(scale,scale,scale),name=f['id']+' Fence')
        for dy in [-15,15]:
            for j in range(10):
                px=x-13.5+j*3;scale=300/length
                mesh(fencepath,px,y+dy,z=height(px,y+dy),yaw=0 if along_x else 90,scale=(scale,scale,scale),name=f['id']+' Fence')
        if f['crop']=='Pumpkins':
            for ix in range(7):
                for iy in range(9):
                    px=x-9+ix*3;py=y-11.2+iy*2.8;pumpkins.append((px,py,height(px,py),.8,(ix*37+iy*17)%360))
        else:
            for ix in range(13):
                for iy in range(15):
                    px=x-10+ix*1.6;py=y-11.2+iy*1.6;wheat.append((px,py,height(px,py),.85 if f['crop']=='Wheat' else .55,0))
    for name,path,items in [('FarmWheat','/Game/StylizedIsland/Mesh/Foliage/SM_Wheat',wheat),('FarmPumpkins','/Game/AdvancedVillagePack/Meshes/SM_Pumpkin_Var01',pumpkins)]:
        ft=load(ROOT+'/Foliage/FT_'+name) if A.does_asset_exist(ROOT+'/Foliage/FT_'+name) else T.create_asset('FT_'+name,ROOT+'/Foliage',unreal.FoliageType_InstancedStaticMesh,unreal.FoliageType_InstancedStaticMeshFactory())
        ft.set_editor_property('mesh',load(path));A.save_loaded_asset(ft)
        transforms=[unreal.Transform(location=unreal.Vector(x*100,y*100,z*100),rotation=unreal.Rotator(yaw=yaw),scale=unreal.Vector(s,s,s)) for x,y,z,s,yaw in items]
        unreal.InstancedFoliageActor.add_instances(w,ft,transforms)
    report['crop_instances']=len(wheat)+len(pumpkins)
    L.save_current_level()
    checkpoint('Importing the hidden construction-grid overlay')
    for category,color in [('Available',(.03,.7,.45)),('Reserved',(1,.55,.025)),('Protected',(.75,.07,.1))]:
        task=unreal.AssetImportTask();task.filename=str(S/('SM_Grid_'+category+'.obj'));task.destination_path=ROOT+'/Design/Debug';task.destination_name='SM_Grid_'+category;task.automated=True;task.save=True;task.replace_existing=True
        options=unreal.FbxImportUI();options.set_editor_property('import_materials',False);options.set_editor_property('import_textures',False)
        options.static_mesh_import_data.set_editor_property('combine_meshes',True);options.static_mesh_import_data.set_editor_property('auto_generate_collision',False)
        task.options=options;T.import_asset_tasks([task])
        a=mesh(ROOT+'/Design/Debug/SM_Grid_'+category,0,0,z=0,name='Grid '+category+' - toggle with script',folder='BuildGrid/Debug')
        # OBJ vertices are already world-space; disable grounding offset.
        a.set_actor_location(unreal.Vector(),False,False)
        a.static_mesh_component.set_material(0,mat('M_Grid_'+category,color))
        a.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        a.static_mesh_component.set_visibility(False)
        a.set_actor_hidden_in_game(True);a.set_editor_property('is_editor_only_actor',True)
    for p in plan['reservations']:
        x,y,z=p['center'];a=E.spawn_actor_from_class(unreal.TargetPoint,unreal.Vector(x*100,y*100,z*100))
        tag(a,p['id']+' | '+p['era'],'BuildGrid/Reserved Plots/'+p['district'])
        a.set_editor_property('tags',[unreal.Name('IVFarmGridV02'),unreal.Name(p['id']),unreal.Name(p['type']),unreal.Name(p['era'])])
        a.set_editor_property('is_editor_only_actor',True)
    for g in plan['gates']:
        x,y=g['center'];a=E.spawn_actor_from_class(unreal.TargetPoint,unreal.Vector(x*100,y*100,height(x,y)*100))
        tag(a,g['name']+' | '+str(g['width'])+'m approach','BuildGrid/Defense Reservations');a.set_editor_property('is_editor_only_actor',True)
    L.save_current_level()
    eye=unreal.Vector(20000,-25500,11500);target=unreal.Vector(12800,-15000,2450)
    unreal.EditorLevelLibrary.set_level_viewport_camera_info(eye,unreal.MathLibrary.find_look_at_rotation(eye,target))
    checkpoint('Saved farm and grid; visual and collision review pending')
try:main()
except Exception:
    report['error']=traceback.format_exc();checkpoint('error');unreal.log_error(report['error'])
