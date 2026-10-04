import unreal
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
print("RenderingLibrary", hasattr(unreal, "RenderingLibrary"))
print("KismetRenderingLibrary", hasattr(unreal, "KismetRenderingLibrary"))
rt = unreal.TextureRenderTarget2D()
for prop in ("size_x", "size_y", "render_target_format"):
    try:
        print(prop, "ok")
    except Exception as e:
        print(prop, e)
rt.set_editor_property("size_x", 1009)
rt.set_editor_property("size_y", 1009)
rt.set_editor_property("render_target_format", unreal.TextureRenderTargetFormat.RTF_R16f)
print("RT created", rt)
