import unreal,json,struct,math
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource';R='/Game/IsekaiVillage/AdventureWorld'
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);A=unreal.EditorAssetLibrary
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert w.get_path_name().startswith(R+'/Maps/Map_AnimeAdventure.')
assert not any('IVWaterfallV03' in [str(t) for t in a.tags] for a in E.get_all_level_actors()),'Waterfall exists; use targeted refinement'
raw=struct.unpack('<'+'H'*1009**2,(S/'IV_Adventure_Waterfall_v03.r16').read_bytes())
def h(x,y):return (raw[round((y+600)*.84)*1009+round((x+600)*.84)]-32768)/64
task=unreal.AssetImportTask();task.filename=str(S/'T_IV_WaterfallHeight_RG.png');task.destination_path=R+'/Textures';task.destination_name='T_IV_WaterfallHeight_RG';task.automated=True;task.save=True
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task]);tex=unreal.load_asset(R+'/Textures/T_IV_WaterfallHeight_RG')
for p,v in [('srgb',False),('compression_settings',unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP),('mip_gen_settings',unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS),('filter',unreal.TextureFilter.TF_NEAREST)]:tex.set_editor_property(p,v)
A.save_loaded_asset(tex)
rt=unreal.RenderingLibrary.create_render_target2d(w,1009,1009,unreal.TextureRenderTargetFormat.RTF_RGBA8);rt.set_editor_property('target_gamma',1.)
canvas,_,ctx=unreal.RenderingLibrary.begin_draw_canvas_to_render_target(w,rt)
canvas.draw_texture(tex,unreal.Vector2D(),unreal.Vector2D(1009,1009),unreal.Vector2D(),unreal.Vector2D(1,1),unreal.LinearColor(1,1,1,1),unreal.BlendMode.BLEND_OPAQUE)
unreal.RenderingLibrary.end_draw_canvas_to_render_target(w,ctx)
land=next(a for a in E.get_all_level_actors() if isinstance(a,unreal.Landscape))
assert land.landscape_import_heightmap_from_render_target(rt,True,0);land.force_layers_full_update()
def mark(a,name):
    a.set_actor_label(name);a.set_folder_path('Adventure/Waterfall');a.set_editor_property('tags',[unreal.Name('IVWaterfallV03')]);return a
def mesh(path,name,x,y,z,scale,yaw=0):
    a=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(x*100,y*100,z*100),unreal.Rotator(yaw=yaw))
    a.static_mesh_component.set_static_mesh(unreal.load_asset(path));a.set_actor_scale3d(unreal.Vector(*scale));return mark(a,name)
fall=mesh('/Game/SoStylized/Environment/Water/Waterfalls/SM_Waterfall1','Veil Falls - Hidden Dungeon Approach',-349,269.8,78.8,(1.15,1.2,5.6))
fall.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
pool=mesh('/Engine/BasicShapes/Cylinder','Veil Falls - Spring Pool',-349,263,78.8,(16,22,.001))
pool.static_mesh_component.set_material(0,unreal.load_asset('/Game/SoStylized/Environment/Water/Materials/MI_Water'))
pool.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
for x,y,s in [(-356,256,.085),(-341,256,.09),(-339,265,.075),(-354,253,.06),(-357,264,.085)]:
    m=unreal.load_asset('/Game/SoStylized/Environment/Rocks/Classic/SM_BoulderClassic1');z=h(x,y)-m.get_bounding_box().min.z*s/100
    mesh(m.get_path_name(),'Spring bank stone',x,y,z,(s,s,s),(x*17+y*11)%360)
seal=next(a for a in E.get_all_level_actors() if a.get_actor_label()=='Ancient Magical Seal')
seal.set_actor_location(unreal.Vector(-34900,27600,(h(-349,276)+2.2)*100),False,False)
# Remove foliage only within the pool/bank grading footprint.
removed=0
for path in A.list_assets(R+'/Foliage',recursive=False,include_folder=False):
    ft=unreal.load_asset(path)
    if not isinstance(ft,unreal.FoliageType_InstancedStaticMesh):continue
    kept=[];cut=0
    for a in E.get_all_level_actors():
        if not isinstance(a,unreal.InstancedFoliageActor):continue
        for c in a.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent):
            if c.static_mesh!=ft.get_editor_property('mesh'):continue
            for i in range(c.get_instance_count()):
                tf=c.get_instance_transform(i,world_space=True);p=tf.translation
                r=math.sqrt(((p.x/100+349)/8)**2+((p.y/100-263)/11)**2)
                if r<1.7:cut+=1
                else:kept.append(tf)
    if cut:
        unreal.InstancedFoliageActor.remove_all_instances(w,ft)
        if kept:unreal.InstancedFoliageActor.add_instances(w,ft,kept)
        removed+=cut
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
eye=unreal.Vector(-32000,23500,12500)
unreal.EditorLevelLibrary.set_level_viewport_camera_info(eye,unreal.MathLibrary.find_look_at_rotation(eye,unreal.Vector(-34900,27200,8800)))
(B/'Saved/waterfall_build.json').write_text(json.dumps({'saved':True,'foliage_cleared':removed,'water_elevation_m':78.8,'fall_height_m':21.39,'pool_center':[-349,263]},indent=2))
