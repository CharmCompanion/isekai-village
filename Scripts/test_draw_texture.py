"""Test canvas.draw_texture with RG heightmap."""
import unreal

MAP = "/Game/SpellCraft/Maps/Height_DemoCopy"
PNG_RG = "F:/DEVELOPMENT/Games/SpellCraft/Content/SpellCraft/Textures/Island_Heightmap_1009_RG.png"
SIZE = 1009
OUT = []

def p(msg):
    OUT.append(msg)
    unreal.log(msg)

unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
landscape = next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if isinstance(a, unreal.Landscape))

tex = unreal.RenderingLibrary.import_file_as_texture2d(world, PNG_RG)
rt = unreal.RenderingLibrary.create_render_target2d(world, SIZE, SIZE, unreal.TextureRenderTargetFormat.RTF_RGBA8)

canvas, size, ctx = unreal.RenderingLibrary.begin_draw_canvas_to_render_target(world, rt)
p(f"canvas={canvas}, size={size}")
if canvas:
    canvas.draw_texture(
        tex,
        unreal.Vector2D(0, 0),
        unreal.Vector2D(SIZE, SIZE),
        unreal.Vector2D(0, 0),
        unreal.Vector2D(1, 1),
        unreal.LinearColor(1, 1, 1, 1),
        unreal.BlendMode.BLEND_OPAQUE,
    )
    p("draw_texture ok")
unreal.RenderingLibrary.end_draw_canvas_to_render_target(world, ctx)

ok = landscape.landscape_import_heightmap_from_render_target(rt, True, 0)
p(f"landscape_import -> {ok}")

unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
with open("F:/DEVELOPMENT/Games/SpellCraft/Saved/Logs/test_draw_texture.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(OUT))
