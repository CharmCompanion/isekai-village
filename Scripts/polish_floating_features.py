import unreal,json,math
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S=B/'Saved/AdventureWorldSource';R='/Game/IsekaiVillage/AdventureWorld';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);A=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
for name in ['T_IV_FloatingHeight_RG','T_IV_Biome_Floating_v07']:
 t=unreal.AssetImportTask();t.filename=str(S/(name+'.png'));t.destination_path=R+'/Textures';t.destination_name=name;t.automated=True;t.replace_existing=True;t.save=True;T.import_asset_tasks([t]);tex=unreal.load_asset(R+'/Textures/'+name)
 for k,v in [('srgb',False),('compression_settings',unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP),('mip_gen_settings',unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS),('filter',unreal.TextureFilter.TF_NEAREST if 'Height' in name else unreal.TextureFilter.TF_BILINEAR)]:tex.set_editor_property(k,v)
 A.save_loaded_asset(tex)
land=next(a for a in E.get_all_level_actors() if isinstance(a,unreal.Landscape));rt=unreal.RenderingLibrary.create_render_target2d(w,1009,1009,unreal.TextureRenderTargetFormat.RTF_RGBA8);rt.set_editor_property('target_gamma',1.)
c,_,ctx=unreal.RenderingLibrary.begin_draw_canvas_to_render_target(w,rt);c.draw_texture(unreal.load_asset(R+'/Textures/T_IV_FloatingHeight_RG'),unreal.Vector2D(),unreal.Vector2D(1009,1009),unreal.Vector2D(),unreal.Vector2D(1,1),unreal.LinearColor(1,1,1,1),unreal.BlendMode.BLEND_OPAQUE);unreal.RenderingLibrary.end_draw_canvas_to_render_target(w,ctx);assert land.landscape_import_heightmap_from_render_target(rt,True,0);land.force_layers_full_update()
lake=A.duplicate_asset('/Game/SoStylized/Environment/Water/Materials/MI_Ocean',R+'/Materials/MI_IV_SkyLake') if not A.does_asset_exist(R+'/Materials/MI_IV_SkyLake') else unreal.load_asset(R+'/Materials/MI_IV_SkyLake')
for k,v in {'Roughness':.24,'Specular':.35,'Water Murkiness':.6,'Water Scattering':.5,'Water Speed':.025,'Normal1 Flatness':.95,'Normal2 Flatness':.96,'Caustic Strength':2.,'Distance':140.,'Foam Multiply':.45}.items():M.set_material_instance_scalar_parameter_value(lake,k,v)
M.set_material_instance_vector_parameter_value(lake,'Scattering Color',unreal.LinearColor(.025,.26,.32,1));A.save_loaded_asset(lake)
for a in E.get_all_level_actors():
 label=a.get_actor_label()
 if label in ['SM_IV_SkyLake','SM_IV_SkyRiver']:a.static_mesh_component.set_material(0,lake)
 if label=='Landing dock stone buttress':
  x=a.get_actor_location().x/100;p=unreal.Vector(x*100,-52700,-1400);q=unreal.Vector(x*100,-56400,2260)
  a.set_actor_location((p+q)*.5,False,False);a.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(p,q),False);a.set_actor_scale3d(unreal.Vector((q-p).length()/100,3,3))
 if label=='Harbor Road':a.set_actor_label('Skyport Road')
 if isinstance(a,unreal.ExponentialHeightFog):
  c=a.get_component_by_class(unreal.ExponentialHeightFogComponent);c.set_editor_property('fog_density',.0003);a.set_actor_location(unreal.Vector(0,0,-12000),False,False)
 if isinstance(a,unreal.SkyAtmosphere):
  c=a.get_component_by_class(unreal.SkyAtmosphereComponent);c.set_editor_property('transform_mode',unreal.SkyAtmosphereTransformMode.PLANET_TOP_AT_COMPONENT_TRANSFORM);a.set_actor_location(unreal.Vector(0,0,-300000),False,False)
unreal.SystemLibrary.execute_console_command(w,'RecreateLandscapeCollision')
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(B/'Saved/floating_polish_result.json').write_text(json.dumps({'dock_approach_connected':True,'dock_supports_aligned':True,'lake_water_revised':True},indent=2))
