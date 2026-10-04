"""Test MID texture blit to RT for height import."""
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
p(f"tex={tex}")

# Try several engine materials with texture params
candidates = [
    "/Engine/EngineMaterials/DefaultMaterial.DefaultMaterial",
    "/Engine/EngineMaterials/M_TechChecker.M_TechChecker",
    "/Engine/EngineMaterials/DefaultDiffuse.DefaultDiffuse",
    "/Engine/EditorMaterials/WidgetMaterial.WidgetMaterial",
    "/Engine/EditorLandscapeResources/Landscape_Heightmap_To_RenderTarget2D.Landscape_Heightmap_To_RenderTarget2D",
]

for path in candidates:
    mat = unreal.load_asset(path)
    p(f"\nTry {path}: {mat}")
    if not mat:
        continue
    try:
        mid = unreal.MaterialInstanceDynamic.create(mat, landscape)
        # common param names
        for pname in ["Texture", "BaseColor", "DiffuseTexture", "Heightmap", "InputTexture", "SourceTexture"]:
            try:
                mid.set_texture_parameter_value(pname, tex)
                p(f"  set_texture_parameter_value({pname}) ok")
            except Exception:
                pass
        unreal.RenderingLibrary.draw_material_to_render_target(world, rt, mid)
        p("  draw_material ok")
        ok = landscape.landscape_import_heightmap_from_render_target(rt, True, 0)
        p(f"  landscape_import -> {ok}")
        if ok:
            break
    except Exception as e:
        p(f"  failed: {e}")

unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
with open("F:/DEVELOPMENT/Games/SpellCraft/Saved/Logs/test_mid_import.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(OUT))
