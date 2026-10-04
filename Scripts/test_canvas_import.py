"""Test canvas blit of height texture to RT then landscape import."""
import unreal

MAP = "/Game/SpellCraft/Maps/Height_DemoCopy"
PNG = "F:/DEVELOPMENT/Games/SpellCraft/Content/SpellCraft/Textures/Island_Heightmap_1009.png"
SIZE = 1009
OUT = []

def p(msg):
    OUT.append(msg)
    unreal.log(msg)

unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
landscape = next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if isinstance(a, unreal.Landscape))

tex = unreal.RenderingLibrary.import_file_as_texture2d(world, PNG)
rt = unreal.RenderingLibrary.create_render_target2d(world, SIZE, SIZE, unreal.TextureRenderTargetFormat.RTF_RGBA8)
p(f"tex={tex}, rt={rt}")

canvas = None
size = None
ctx = None
try:
    canvas, size, ctx = unreal.RenderingLibrary.begin_draw_canvas_to_render_target(world, rt)
    p(f"canvas={canvas}, size={size}")
    if canvas:
        # Full-screen draw
        screen = unreal.Vector2D(SIZE, SIZE)
        pos = unreal.Vector2D(0, 0)
        canvas.k2_draw_texture(
            tex,
            pos,
            screen,
            unreal.Vector2D(0, 0),
            unreal.Vector2D(1, 1),
            unreal.LinearColor(1, 1, 1, 1),
            unreal.BlendMode.BLEND_OPAQUE,
        )
        p("k2_draw_texture ok")
except Exception as e:
    p(f"canvas error: {e}")
finally:
    if ctx is not None:
        unreal.RenderingLibrary.end_draw_canvas_to_render_target(world, ctx)

# Try import with RG channel (16-bit height in R+G)
ok_rg = landscape.landscape_import_heightmap_from_render_target(rt, True, 0)
p(f"import RG -> {ok_rg}")

# Try import R only (16-bit in R as float cast)
rt16 = unreal.RenderingLibrary.create_render_target2d(world, SIZE, SIZE, unreal.TextureRenderTargetFormat.RTF_RGBA16F)
try:
    canvas2, size2, ctx2 = unreal.RenderingLibrary.begin_draw_canvas_to_render_target(world, rt16)
    if canvas2:
        canvas2.k2_draw_texture(tex, unreal.Vector2D(0, 0), unreal.Vector2D(SIZE, SIZE),
                                unreal.Vector2D(0, 0), unreal.Vector2D(1, 1),
                                unreal.LinearColor(1, 1, 1, 1), unreal.BlendMode.BLEND_OPAQUE)
    if ctx2 is not None:
        unreal.RenderingLibrary.end_draw_canvas_to_render_target(world, ctx2)
    ok_r = landscape.landscape_import_heightmap_from_render_target(rt16, False, 0)
    p(f"import R16f -> {ok_r}")
except Exception as e:
    p(f"rgba16 path error: {e}")

unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
path = "F:/DEVELOPMENT/Games/SpellCraft/Saved/Logs/test_canvas_import.txt"
with open(path, "w", encoding="utf-8") as f:
    f.write("\n".join(OUT))
