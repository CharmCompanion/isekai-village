"""
Hard fix for Height_DemoCopy: island above water + remove floating leftover props.

Close the Unreal Editor before running — if the editor has the map open it will
overwrite the commandlet save when you quit.

  T:\\Program Files\\UE_5.8\\Engine\\Binaries\\Win64\\UnrealEditor-Cmd.exe ^
    F:\\DEVELOPMENT\\Games\\SpellCraft\\SpellCraft.uproject ^
    -run=pythonscript ^
    -script="F:\\DEVELOPMENT\\Games\\SpellCraft\\Scripts\\fix_island_visible.py" ^
    -AllowCommandletRendering -stdout -unattended -nosplash
"""
import os
import unreal

MAP = "/Game/SpellCraft/Maps/Height_DemoCopy"
PNG_RG = "F:/DEVELOPMENT/Games/SpellCraft/Content/SpellCraft/Textures/Island_Heightmap_1009_RG.png"
SIZE = 1009
RESULT = "F:/DEVELOPMENT/Games/SpellCraft/Saved/Logs/fix_island_visible_result.txt"

# Keep these actor class / name fragments
KEEP_CLASS = {
    "Landscape",
    "LandscapeStreamingProxy",
    "PlayerStart",
    "DirectionalLight",
    "SkyLight",
    "ExponentialHeightFog",
    "SkyAtmosphere",
    "VolumetricCloud",
    "PostProcessVolume",
    "WorldSettings",
    "DefaultPhysicsVolume",
    "Brush",
    "RuntimeVirtualTextureVolume",
    "LevelBounds",
}
KEEP_NAME_FRAG = (
    "BP_Water",
    "BP_StylizedSky",
    "RVT",
    "PlayerStart",
    "Landscape",
)

# Raise whole landscape actor so sculpt sits clearly above ocean plane
LANDSCAPE_Z_BOOST = 2500.0
PLAYER_LOC = unreal.Vector(-22000.0, -24000.0, 800.0)
PLAYER_ROT = unreal.Rotator(0, 45, 0)

OUT = []


def log(msg):
    OUT.append(msg)
    unreal.log(msg)
    print(msg)


def keep_actor(act):
    cls = act.get_class().get_name()
    name = act.get_name()
    if cls in KEEP_CLASS:
        return True
    if any(f in cls or f in name for f in KEEP_NAME_FRAG):
        return True
    # Keep Blueprint water / sky by parent class name
    if "Water" in cls or "Sky" in cls:
        return True
    return False


def get_landscape():
    for act in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        if isinstance(act, unreal.Landscape):
            return act
    return None


def import_height(landscape):
    if not os.path.isfile(PNG_RG):
        log(f"ERROR missing {PNG_RG}")
        return False
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    tex = unreal.RenderingLibrary.import_file_as_texture2d(world, PNG_RG)
    rt = unreal.RenderingLibrary.create_render_target2d(
        world, SIZE, SIZE, unreal.TextureRenderTargetFormat.RTF_RGBA8
    )
    canvas, _, ctx = unreal.RenderingLibrary.begin_draw_canvas_to_render_target(world, rt)
    if not canvas:
        log("ERROR: no canvas (need -AllowCommandletRendering)")
        return False
    canvas.draw_texture(
        tex,
        unreal.Vector2D(0, 0),
        unreal.Vector2D(SIZE, SIZE),
        unreal.Vector2D(0, 0),
        unreal.Vector2D(1, 1),
        unreal.LinearColor(1, 1, 1, 1),
        unreal.BlendMode.BLEND_OPAQUE,
    )
    unreal.RenderingLibrary.end_draw_canvas_to_render_target(world, ctx)
    ok = landscape.landscape_import_heightmap_from_render_target(rt, True, 0)
    log(f"height import -> {ok}")
    return ok


def raise_landscape(landscape):
    loc = landscape.get_actor_location()
    new_loc = unreal.Vector(loc.x, loc.y, loc.z + LANDSCAPE_Z_BOOST)
    landscape.set_actor_location(new_loc, False, False)
    log(f"Landscape Z {loc.z} -> {new_loc.z}")


def purge_leftover_props():
    """Remove floating demo cliffs/trees/rocks left at old heights."""
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    removed = 0
    for act in list(sub.get_all_level_actors()):
        if keep_actor(act):
            continue
        cls = act.get_class().get_name()
        if isinstance(act, unreal.StaticMeshActor) or "Foliage" in cls:
            sub.destroy_actor(act)
            removed += 1
    log(f"Purged {removed} StaticMesh/Foliage leftovers")


def move_player():
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for act in sub.get_all_level_actors():
        if isinstance(act, unreal.PlayerStart):
            # Spawn above raised beach
            z = PLAYER_LOC.z + LANDSCAPE_Z_BOOST
            loc = unreal.Vector(PLAYER_LOC.x, PLAYER_LOC.y, z)
            act.set_actor_location(loc, False, False)
            act.set_actor_rotation(PLAYER_ROT, False)
            log(f"PlayerStart -> {loc}")
            return


def report_actors():
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    counts = {}
    water_z = []
    for act in sub.get_all_level_actors():
        cls = act.get_class().get_name()
        counts[cls] = counts.get(cls, 0) + 1
        if "Water" in cls or "Water" in act.get_name():
            water_z.append(f"{act.get_name()} Z={act.get_actor_location().z}")
    top = sorted(counts.items(), key=lambda kv: -kv[1])[:15]
    log("Actor counts (top): " + ", ".join(f"{k}={v}" for k, v in top))
    for w in water_z:
        log(f"  {w}")


def main():
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
    landscape = get_landscape()
    if not landscape:
        log("ERROR: no landscape")
        return

    loc = landscape.get_actor_location()
    scale = landscape.get_actor_scale3d()
    log(f"Before: landscape loc={loc} scale={scale}")
    report_actors()

    import_height(landscape)
    raise_landscape(landscape)
    purge_leftover_props()
    move_player()

    loc2 = landscape.get_actor_location()
    log(f"After: landscape loc={loc2}")
    report_actors()

    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    # Also save dirty packages so landscape height data sticks
    try:
        unreal.EditorAssetLibrary.save_directory("/Game/SpellCraft/Maps", True, True)
    except Exception as exc:
        log(f"save_directory note: {exc}")

    log("SUCCESS: Close any open editor copy of this map, then reopen Height_DemoCopy.")
    with open(RESULT, "w", encoding="utf-8") as f:
        f.write("\n".join(OUT))


if __name__ == "__main__":
    main()
