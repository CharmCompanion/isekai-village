import unreal,json
from pathlib import Path
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();land=next(a for a in E.get_all_level_actors() if isinstance(a,unreal.Landscape))
rt=unreal.RenderingLibrary.create_render_target2d(w,1009,1009,unreal.TextureRenderTargetFormat.RTF_RGBA8)
out={'render':land.render_weightmap(unreal.Transform(),unreal.Box2D(), '__LANDSCAPE_VISIBILITY__',rt)}
out['pixels']=[str(unreal.RenderingLibrary.read_render_target_pixel(w,rt,x,y)) for x,y in [(504,504),(10,10),(995,500)]]
layer=land.get_edit_layers_bp()[0];out['edit_methods']=str([p for p in dir(layer) if any(k in p for k in ['alpha','weight','visible','blend'])])
Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/visibility_weight.json').write_text(json.dumps(out,indent=2))
