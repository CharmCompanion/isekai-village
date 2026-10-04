import unreal,json
from pathlib import Path
R='/Game/IsekaiVillage/AdventureWorld';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);land=next(a for a in E.get_all_level_actors() if isinstance(a,unreal.Landscape));w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
settings=unreal.LandscapeTargetLayerSettings();settings.set_editor_property('layer_info_obj',unreal.load_asset('/Engine/EngineResources/LandscapeVisibilityLayerInfo'))
layers=land.get_editor_property('target_layers');layers['__LANDSCAPE_VISIBILITY__']=settings;land.set_editor_property('target_layers',layers)
rt=unreal.RenderingLibrary.create_render_target2d(w,1009,1009,unreal.TextureRenderTargetFormat.RTF_RGBA8);rt.set_editor_property('target_gamma',1.)
c,_,ctx=unreal.RenderingLibrary.begin_draw_canvas_to_render_target(w,rt);c.draw_texture(unreal.load_asset(R+'/Textures/T_IV_FloatingVisibility'),unreal.Vector2D(),unreal.Vector2D(1009,1009),unreal.Vector2D(),unreal.Vector2D(1,1),unreal.LinearColor(1,1,1,1),unreal.BlendMode.BLEND_OPAQUE);unreal.RenderingLibrary.end_draw_canvas_to_render_target(w,ctx)
assert land.landscape_import_weightmap_from_render_target(rt,'__LANDSCAPE_VISIBILITY__',0);land.force_layers_full_update()
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
