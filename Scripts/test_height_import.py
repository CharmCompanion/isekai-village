"""Test direct landscape height import paths."""
import os
import struct
import unreal

MAP = "/Game/SpellCraft/Maps/Height_DemoCopy"
R16 = "F:/DEVELOPMENT/Games/SpellCraft/Content/SpellCraft/Textures/Island_Heightmap_1009.r16"
SIZE = 1009
OUT = []

def p(msg):
    OUT.append(msg)
    unreal.log(msg)

unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()

landscape = None
for act in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if isinstance(act, unreal.Landscape):
        landscape = act
        break

p(f"Landscape: {landscape}")
p(f"has import: {hasattr(landscape, 'import')}")
p(f"CanEverRender-ish RenderingLibrary.create_render_target2d available: {hasattr(unreal.RenderingLibrary, 'create_render_target2d')}")

# Read r16 heights
with open(R16, "rb") as f:
    raw = f.read()
heights = struct.unpack(f"<{SIZE*SIZE}H", raw)
p(f"Read {len(heights)} heights, min={min(heights)} max={max(heights)}")

# Try create RT with AllowCommandletRendering (caller must pass flag)
rt = unreal.RenderingLibrary.create_render_target2d(world, SIZE, SIZE, unreal.TextureRenderTargetFormat.RTF_RGBA8)
p(f"RT: {rt}, resource={rt.get_editor_property('size_x') if rt else None}")

# Import PNG as texture
png = "F:/DEVELOPMENT/Games/SpellCraft/Content/SpellCraft/Textures/Island_Heightmap_1009.png"
tex = unreal.RenderingLibrary.import_file_as_texture2d(world, png)
p(f"Imported tex: {tex}")

# Try draw material - use engine default material
mat = unreal.load_asset("/Engine/EngineMaterials/DefaultMaterial.DefaultMaterial")
p(f"Material: {mat}")

if rt and tex and mat:
    try:
        unreal.RenderingLibrary.draw_material_to_render_target(world, rt, mat)
        p("draw_material_to_render_target: ok")
    except Exception as e:
        p(f"draw_material failed: {e}")

    try:
        ok = landscape.landscape_import_heightmap_from_render_target(rt, True, 0)
        p(f"landscape_import -> {ok}")
    except Exception as e:
        p(f"landscape_import failed: {e}")

path = "F:/DEVELOPMENT/Games/SpellCraft/Saved/Logs/test_height_import.txt"
with open(path, "w", encoding="utf-8") as f:
    f.write("\n".join(OUT))
