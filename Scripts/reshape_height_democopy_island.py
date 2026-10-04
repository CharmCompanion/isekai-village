"""
Apply island heightmap to Height_DemoCopy landscape.
SW crescent beach, NE mountains, demo-style interior.

Generate heightmap first (system Python):
  python F:\\DEVELOPMENT\\Games\\SpellCraft\\Scripts\\create_island_heightmap_v2.py

Run with editor CLOSED (needs GPU — pass -AllowCommandletRendering):
  T:\\Program Files\\UE_5.8\\Engine\\Binaries\\Win64\\UnrealEditor-Cmd.exe ^
    F:\\DEVELOPMENT\\Games\\SpellCraft\\SpellCraft.uproject ^
    -run=pythonscript ^
    -script="F:\\DEVELOPMENT\\Games\\SpellCraft\\Scripts\\reshape_height_democopy_island.py" ^
    -AllowCommandletRendering -stdout -unattended -nosplash
"""
import os
import unreal

MAP = "/Game/SpellCraft/Maps/Height_DemoCopy"
PNG_RG_PATH = "F:/DEVELOPMENT/Games/SpellCraft/Content/SpellCraft/Textures/Island_Heightmap_1009_RG.png"
HEIGHTMAP_SIZE = 1009

# SW crescent beach spawn (world coords; landscape center ~ 0,0)
PLAYER_LOC = unreal.Vector(-22000.0, -24000.0, 450.0)
PLAYER_ROT = unreal.Rotator(0, 45, 0)  # face NE toward mountains

# Cull props outside this radius (centered on the landscape bounds, not world origin)
ISLAND_RADIUS = 38500.0


def log(msg):
    unreal.log(msg)
    print(msg)


def load_map():
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)


def get_landscape():
    for act in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        if isinstance(act, unreal.Landscape):
            return act
    return None


def apply_heightmap_to_landscape(landscape, png_path):
    if not os.path.isfile(png_path):
        log(f"ERROR: Missing {png_path} — run create_island_heightmap_v2.py first")
        return False

    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    if not world:
        log("ERROR: No editor world")
        return False

    tex = unreal.RenderingLibrary.import_file_as_texture2d(world, png_path)
    if not tex:
        log("ERROR: Could not import heightmap PNG")
        return False
    log(f"Imported height texture from {png_path}")

    rt = unreal.RenderingLibrary.create_render_target2d(
        world,
        HEIGHTMAP_SIZE,
        HEIGHTMAP_SIZE,
        unreal.TextureRenderTargetFormat.RTF_RGBA8,
    )
    if not rt:
        log("ERROR: Could not create render target — run with -AllowCommandletRendering")
        return False

    canvas, _, ctx = unreal.RenderingLibrary.begin_draw_canvas_to_render_target(world, rt)
    if not canvas:
        log("ERROR: Canvas draw failed — run with -AllowCommandletRendering (GPU required)")
        return False

    canvas.draw_texture(
        tex,
        unreal.Vector2D(0, 0),
        unreal.Vector2D(HEIGHTMAP_SIZE, HEIGHTMAP_SIZE),
        unreal.Vector2D(0, 0),
        unreal.Vector2D(1, 1),
        unreal.LinearColor(1, 1, 1, 1),
        unreal.BlendMode.BLEND_OPAQUE,
    )
    unreal.RenderingLibrary.end_draw_canvas_to_render_target(world, ctx)

    ok = landscape.landscape_import_heightmap_from_render_target(rt, True, 0)
    log(f"landscape_import_heightmap_from_render_target -> {ok}")
    return ok


def move_player_start():
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for act in sub.get_all_level_actors():
        if isinstance(act, unreal.PlayerStart):
            act.set_actor_location(PLAYER_LOC, False, False)
            act.set_actor_rotation(PLAYER_ROT, False)
            log(f"PlayerStart -> {PLAYER_LOC}")
            return
    sub.spawn_actor_from_class(unreal.PlayerStart, PLAYER_LOC, PLAYER_ROT)
    log(f"Spawned PlayerStart at {PLAYER_LOC}")


def get_landscape_center(landscape):
    # The landscape actor location isn't guaranteed to be the center; use bounds center when possible.
    try:
        bb = landscape.get_components_bounding_box()
        return bb.get_center()
    except Exception:
        return landscape.get_actor_location()


def cull_off_island_props(landscape, island_center):
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    removed = 0
    for act in list(sub.get_all_level_actors()):
        if not isinstance(act, unreal.StaticMeshActor):
            continue
        loc = act.get_actor_location()
        dx = loc.x - island_center.x
        dy = loc.y - island_center.y
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist > ISLAND_RADIUS or loc.z < -500.0:
            sub.destroy_actor(act)
            removed += 1
    log(f"Removed {removed} StaticMeshActors outside island or underwater")


def fix_duplicate_suns():
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    suns = [a for a in sub.get_all_level_actors() if isinstance(a, unreal.DirectionalLight)]
    if len(suns) > 1:
        for extra in suns[1:]:
            sub.destroy_actor(extra)
        log(f"Removed {len(suns) - 1} extra DirectionalLight(s)")


def reshape():
    if not os.path.isfile(PNG_RG_PATH):
        log("Run: python Scripts/create_island_heightmap_v2.py")
        return

    load_map()
    landscape = get_landscape()
    if not landscape:
        log("ERROR: No landscape in map")
        return

    if not apply_heightmap_to_landscape(landscape, PNG_RG_PATH):
        log("Manual fallback: Landscape mode -> Import from File -> Island_Heightmap_1009_RG.png")

    fix_duplicate_suns()
    island_center = get_landscape_center(landscape)
    cull_off_island_props(landscape, island_center)
    move_player_start()

    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    log("SUCCESS: Island reshape saved. Open Height_DemoCopy — SW beach, NE mountains.")


if __name__ == "__main__":
    reshape()
