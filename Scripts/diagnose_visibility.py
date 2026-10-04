import unreal,json
from pathlib import Path
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();land=next(a for a in E.get_all_level_actors() if isinstance(a,unreal.Landscape));R='/Game/IsekaiVillage/AdventureWorld';out={}
rt=unreal.RenderingLibrary.create_render_target2d(w,1009,1009,unreal.TextureRenderTargetFormat.RTF_RGBA8);rt.set_editor_property('target_gamma',1.)
c,_,ctx=unreal.RenderingLibrary.begin_draw_canvas_to_render_target(w,rt);c.draw_texture(unreal.load_asset(R+'/Textures/T_IV_FloatingVisibility'),unreal.Vector2D(),unreal.Vector2D(1009,1009),unreal.Vector2D(),unreal.Vector2D(1,1),unreal.LinearColor(1,1,1,1),unreal.BlendMode.BLEND_OPAQUE);unreal.RenderingLibrary.end_draw_canvas_to_render_target(w,ctx)
out['source']=[str(unreal.RenderingLibrary.read_render_target_pixel(w,rt,x,y)) for x,y in [(504,504),(10,10),(995,500)]]
for a in E.get_all_level_actors():
 if a.get_actor_label()=='SM_IV_FloatingUnderside':out['underside']={'bounds':str(a.get_actor_bounds(False)),'mat':str(a.static_mesh_component.get_material(0))}
Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/visibility_diagnostic.json').write_text(json.dumps(out,indent=2))
land.set_editor_property('landscape_material',unreal.load_asset(R+'/Materials/M_IV_Landscape_Layered'))
land.set_editor_property('landscape_hole_material',unreal.load_asset(R+'/Materials/M_IV_Landscape_Layered'))
