import unreal,json,math,struct
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource';R='/Game/IsekaiVillage/AdventureWorld';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);A=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert w.get_path_name().startswith(R+'/Maps/Map_AnimeAdventure.')
report={}
def log(stage):report['stage']=stage;(B/'Saved/dish_peak_apply_result.json').write_text(json.dumps(report,indent=2))
def texture(name):
 t=unreal.AssetImportTask();t.filename=str(S/(name+'.png'));t.destination_path=R+'/Textures';t.destination_name=name;t.automated=True;t.save=True;t.replace_existing=True;T.import_asset_tasks([t]);a=unreal.load_asset(t.destination_path+'/'+name)
 for k,v in [('srgb',False),('compression_settings',unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP),('mip_gen_settings',unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS),('filter',unreal.TextureFilter.TF_NEAREST if 'Height' in name else unreal.TextureFilter.TF_BILINEAR)]:a.set_editor_property(k,v)
 A.save_loaded_asset(a);return a
log('Importing low rolling native Landscape lip')
ht=texture('T_IV_DishHeight_RG');biome=texture('T_IV_Biome_Dish_v11');land=next(a for a in E.get_all_level_actors() if isinstance(a,unreal.Landscape));rt=unreal.RenderingLibrary.create_render_target2d(w,1009,1009,unreal.TextureRenderTargetFormat.RTF_RGBA8);rt.set_editor_property('target_gamma',1.);c,_,ctx=unreal.RenderingLibrary.begin_draw_canvas_to_render_target(w,rt);c.draw_texture(ht,unreal.Vector2D(),unreal.Vector2D(1009,1009),unreal.Vector2D(),unreal.Vector2D(1,1),unreal.LinearColor(1,1,1,1),unreal.BlendMode.BLEND_OPAQUE);unreal.RenderingLibrary.end_draw_canvas_to_render_target(w,ctx);assert land.landscape_import_heightmap_from_render_target(rt,True,0);land.force_layers_full_update()
lm=unreal.load_asset(R+'/Materials/M_IV_FloatingLandscape')
for n in M.get_material_expressions(lm):
 if isinstance(n,unreal.MaterialExpressionTextureSample):
  tex=n.get_editor_property('texture')
  if tex and 'Biome' in tex.get_name():n.set_editor_property('texture',biome)
M.recompile_material(lm);A.save_loaded_asset(lm)
log('Importing single inverted mountain')
for a in E.get_all_level_actors():
 if 'IVRockRim10' in [str(t) for t in a.tags]:
  a.set_folder_path('Archived/Rock Rim v10');a.set_actor_hidden_in_game(True);a.set_actor_enable_collision(False);a.static_mesh_component.set_visibility(False,True)
name='SM_IV_InvertedMountain_v11';t=unreal.AssetImportTask();t.filename=str(S/(name+'.obj'));t.destination_path=R+'/Meshes/Refinement';t.destination_name=name;t.automated=True;t.replace_existing=True;t.save=True
op=unreal.FbxImportUI();op.import_materials=False;op.import_textures=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=False;op.static_mesh_import_data.set_editor_property('normal_import_method',unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS);t.options=op;T.import_asset_tasks([t]);mesh=unreal.load_asset(t.destination_path+'/'+name)
sub=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);settings=sub.get_lod_build_settings(mesh,0);settings.recompute_normals=False;settings.recompute_tangents=True;sub.set_lod_build_settings(mesh,0,settings)
mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);A.save_loaded_asset(mesh)
mat=A.duplicate_asset(R+'/Materials/MI_IV_BedrockSurface',R+'/Materials/MI_IV_InvertedMountain_v11')
if not mat:mat=unreal.load_asset(R+'/Materials/MI_IV_InvertedMountain_v11')
M.set_material_instance_scalar_parameter_value(mat,'Normal Flatness',.62)
A.save_loaded_asset(mat)
a=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());a.static_mesh_component.set_static_mesh(mesh);a.static_mesh_component.set_material(0,mat);a.set_actor_label('Single inverted mountain - four converging ridges');a.set_folder_path('Floating Island/Inverted Mountain');a.tags=[unreal.Name('IVDishPeak11')]
# Native foliage updates preserve type ownership even where multiple types share one mesh.
log('Regrounding vegetation on raised rim')
new=struct.unpack('<'+'H'*1009**2,(S/'IV_DishPeak_v11.r16').read_bytes());old=struct.unpack('<'+'H'*1009**2,(S/'IV_RockRim_v10.r16').read_bytes())
def height(raw,x,y):
 i=max(0,min(1008,round((x+600)*.84)));j=max(0,min(1008,round((y+600)*.84)));return (raw[j*1009+i]-32768)/64
moved=0;removed=0
for path in A.list_assets(R+'/Foliage',recursive=False,include_folder=False):
 ft=unreal.load_asset(path)
 if not isinstance(ft,unreal.FoliageType_InstancedStaticMesh):continue
 mesh=ft.get_editor_property('mesh');before=[]
 for actor in E.get_all_level_actors():
  if isinstance(actor,unreal.InstancedFoliageActor):
   for comp in actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent):
    if comp.static_mesh==mesh:before.append((comp,[comp.get_instance_transform(i,world_space=True) for i in range(comp.get_instance_count())]))
 if not before:continue
 unreal.InstancedFoliageActor.remove_all_instances(w,ft);own=[]
 for comp,transforms in before:
  if not unreal.SystemLibrary.is_valid(comp) or comp.get_instance_count()==0:own.extend(transforms)
 kept=[]
 for tf in own:
  p=tf.translation;x=p.x/100;y=p.y/100;delta=height(new,x,y)-height(old,x,y)
  if abs(delta)>.25:
   slope=math.hypot(height(new,x+2,y)-height(new,x-2,y),height(new,x,y+2)-height(new,x,y-2))/4
   if slope>1.15:removed+=1;continue
   tf.translation=unreal.Vector(p.x,p.y,p.z+delta*100);moved+=1
  kept.append(tf)
 if kept:unreal.InstancedFoliageActor.add_instances(w,ft,kept)
report.update(vegetation_regrounded=moved,vegetation_removed_from_steep_scarp=removed)
unreal.SystemLibrary.execute_console_command(w,'RecreateLandscapeCollision');unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level();log('saved')

exec(compile((B/'Scripts/render_dish_peak_v11.py').read_text(),'render','exec'),{'__name__':'__main__'})
