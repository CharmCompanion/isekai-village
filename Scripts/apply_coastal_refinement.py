import unreal,struct,math,random,json
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource';R='/Game/IsekaiVillage/AdventureWorld';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);A=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
textures=[]
for filename,name in [('T_IV_CoastalHeight_RG.png','T_IV_CoastalHeight_RG'),('T_IV_Biome_Coastal_v06.png','T_IV_Biome_Coastal_v06')]:
    t=unreal.AssetImportTask();t.filename=str(S/filename);t.destination_path=R+'/Textures';t.destination_name=name;t.automated=True;t.save=True;T.import_asset_tasks([t]);tex=unreal.load_asset(R+'/Textures/'+name)
    for k,v in [('srgb',False),('compression_settings',unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP),('mip_gen_settings',unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS),('filter',unreal.TextureFilter.TF_NEAREST if 'Height' in name else unreal.TextureFilter.TF_BILINEAR)]:tex.set_editor_property(k,v)
    A.save_loaded_asset(tex);textures.append(tex)
land=next(a for a in E.get_all_level_actors() if isinstance(a,unreal.Landscape));rt=unreal.RenderingLibrary.create_render_target2d(w,1009,1009,unreal.TextureRenderTargetFormat.RTF_RGBA8);rt.set_editor_property('target_gamma',1.)
c,_,ctx=unreal.RenderingLibrary.begin_draw_canvas_to_render_target(w,rt);c.draw_texture(textures[0],unreal.Vector2D(),unreal.Vector2D(1009,1009),unreal.Vector2D(),unreal.Vector2D(1,1),unreal.LinearColor(1,1,1,1),unreal.BlendMode.BLEND_OPAQUE);unreal.RenderingLibrary.end_draw_canvas_to_render_target(w,ctx);assert land.landscape_import_heightmap_from_render_target(rt,True,0);land.force_layers_full_update()
mat=unreal.load_asset(R+'/Materials/M_IV_Landscape_Layered')
for n in M.get_material_expressions(mat):
    if isinstance(n,unreal.MaterialExpressionTextureSample) and n.get_editor_property('texture')==unreal.load_asset(R+'/Textures/T_IV_Biome_Layered_v05'):n.set_editor_property('texture',textures[1])
M.recompile_material(mat);A.save_loaded_asset(mat)
raw=struct.unpack('<'+'H'*1009**2,(S/'IV_Adventure_Coastal_v06.r16').read_bytes())
def h(x,y):return (raw[round((y+600)*.84)*1009+round((x+600)*.84)]-32768)/64
# Only the eastern strip moved. Keep all other foliage transforms byte-for-byte.
for path in A.list_assets(R+'/Foliage',recursive=False,include_folder=False):
    ft=unreal.load_asset(path)
    if not isinstance(ft,unreal.FoliageType_InstancedStaticMesh):continue
    kept=[];changed=0
    for a in E.get_all_level_actors():
        if not isinstance(a,unreal.InstancedFoliageActor):continue
        for c in a.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent):
            if c.static_mesh!=ft.get_editor_property('mesh'):continue
            for i in range(c.get_instance_count()):
                tf=c.get_instance_transform(i,world_space=True);p=tf.translation
                if p.x>34000:
                    z=h(p.x/100,p.y/100);changed+=1
                    if z<3:continue
                    tf.translation=unreal.Vector(p.x,p.y,z*100-12)
                kept.append(tf)
    if changed:
        unreal.InstancedFoliageActor.remove_all_instances(w,ft)
        if kept:unreal.InstancedFoliageActor.add_instances(w,ft,kept)
for a in E.get_all_level_actors():
    if str(a.get_folder_path())=='Nature/Outcrops' and a.get_actor_location().x>34000:
        p=a.get_actor_location();o,ext=a.get_actor_bounds(False);a.set_actor_location(unreal.Vector(p.x,p.y,p.z+h(p.x/100,p.y/100)*100-(o.z-ext.z)),False,False)
rock=unreal.load_asset('/Game/SoStylized/Environment/Rocks/Classic/SM_BoulderClassic1');box=rock.get_bounding_box();rng=random.Random(926);count=0
def place(x,y,width,name):
    global count
    z=h(x,y);s=width*100/max(box.max.x-box.min.x,box.max.y-box.min.y)
    a=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(x*100,y*100,z*100-box.min.z*s-45),unreal.Rotator(yaw=rng.uniform(0,360)));a.static_mesh_component.set_static_mesh(rock);a.set_actor_scale3d(unreal.Vector(s,s*.8,s*.8));a.set_actor_label(name);a.set_folder_path('Coast/Rock Shelves');a.set_editor_property('tags',[unreal.Name('IVCoastalV06')]);count+=1
for x in [-335,-245,-175,85,175,290,380]:
    y=min(range(-570,-300,2),key=lambda y:abs(h(x,y)-.7))
    place(x,y,rng.uniform(5,8),'Tidal shore outcrop')
    for i in range(3):place(x+rng.uniform(-7,7),y+rng.uniform(-5,5),rng.uniform(1,2.8),'Tidal shore stones')
for y in range(-320,331,65):
    x=min(range(435,535,2),key=lambda x:abs(h(x,y)-4));place(x,y,rng.uniform(8,13),'Eastern cliff buttress')
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(B/'Saved/coastal_refinement_result.json').write_text(json.dumps({'saved':True,'coastal_rock_clusters':count,'ocean_span_m':200000,'native_landscape':True},indent=2))
