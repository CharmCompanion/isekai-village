"""
Fix Height_DemoCopy look only:
- Apply SoStylized MI_Landscape (does NOT change height)
- Re-apply weight masks to Sand/Grass/Rock/Dirt if layers exist
- Upright trees + kill wind WPO (wind-tunnel lean)

Close Unreal first.
"""
import os
import random
import unreal

MAP = "/Game/SpellCraft/Maps/Height_DemoCopy"
MAT = "/Game/SoStylized/Environment/Landscape/Materials/MI_Landscape"
WEIGHT_DIR = "F:/DEVELOPMENT/Games/SpellCraft/Content/SpellCraft/Textures"
SIZE = 1009
RESULT = "F:/DEVELOPMENT/Games/SpellCraft/Saved/Logs/fix_island_look_v1.txt"
OUT = []

WEIGHTS = (
    ("Sand", "Island_Weight_Sand.png"),
    ("Grass", "Island_Weight_Grass.png"),
    ("Rock", "Island_Weight_Rock.png"),
    ("Dirt", "Island_Weight_Dirt.png"),
)


def log(msg):
    OUT.append(str(msg))
    unreal.log(msg)


def import_weight(world, landscape, layer, filename):
    path = os.path.join(WEIGHT_DIR, filename)
    if not os.path.isfile(path):
        log(f"missing {filename}")
        return
    tex = unreal.RenderingLibrary.import_file_as_texture2d(world, path)
    if not tex:
        return
    try:
        tex.set_editor_property("srgb", False)
    except Exception:
        pass
    rt = unreal.RenderingLibrary.create_render_target2d(
        world, SIZE, SIZE, unreal.TextureRenderTargetFormat.RTF_RGBA8
    )
    canvas, size, ctx = unreal.RenderingLibrary.begin_draw_canvas_to_render_target(world, rt)
    if not canvas:
        log("canvas None — need -AllowCommandletRendering")
        return
    canvas.draw_texture(
        tex, unreal.Vector2D(0, 0), unreal.Vector2D(SIZE, SIZE),
        unreal.Vector2D(0, 0), unreal.Vector2D(1, 1),
        unreal.LinearColor(1, 1, 1, 1), unreal.BlendMode.BLEND_OPAQUE,
    )
    unreal.RenderingLibrary.end_draw_canvas_to_render_target(world, ctx)
    try:
        ok = landscape.landscape_import_weightmap_from_render_target(rt, layer)
        log(f"weight {layer} -> {ok}")
    except Exception as e:
        log(f"weight {layer} err: {e}")


def fix_trees(sub, rng):
    fixed = 0
    for act in list(sub.get_all_level_actors()):
        label = act.get_actor_label()
        if not (label.startswith("ForestTree") or label.startswith("ForestBush")):
            continue
        # Upright only — yaw random so nothing looks wind-aligned
        act.set_actor_rotation(unreal.Rotator(0.0, rng.uniform(0.0, 360.0), 0.0), False)
        smc = act.get_component_by_class(unreal.StaticMeshComponent)
        if smc:
            smc.set_relative_rotation(unreal.Rotator(0, 0, 0), False, False)
            # Kill SimpleWind / WPO lean (SoStylized "wind tunnel")
            for prop in (
                "evaluate_world_position_offset",
                "b_evaluate_world_position_offset",
                "world_position_offset_disable_distance",
            ):
                try:
                    if "disable" in prop:
                        smc.set_editor_property(prop, 1)
                    else:
                        smc.set_editor_property(prop, False)
                except Exception:
                    pass
            try:
                smc.set_editor_property("cast_shadow", True)
            except Exception:
                pass
        fixed += 1
    log(f"Trees fixed upright + no WPO wind: {fixed}")


def main():
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    les.load_level(MAP)
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    world = unreal.UnrealEditorSubsystem().get_editor_world()

    landscape = None
    for act in sub.get_all_level_actors():
        cn = act.get_class().get_name()
        if "Landscape" in cn and "Streaming" not in cn and "Proxy" not in cn:
            landscape = act
            break
    if not landscape:
        # proxies ok as fallback
        for act in sub.get_all_level_actors():
            if isinstance(act, unreal.Landscape):
                landscape = act
                break
    if not landscape:
        log("ERROR no landscape")
        return

    mat = unreal.EditorAssetLibrary.load_asset(MAT)
    if mat:
        landscape.set_editor_property("landscape_material", mat)
        log(f"landscape_material -> {MAT}")
    else:
        log("ERROR missing MI_Landscape")

    try:
        landscape.set_grass_enabled(True)
        log("grass enabled")
    except Exception as e:
        log(f"grass: {e}")

    try:
        names = [str(n) for n in landscape.get_target_layer_names()]
        log(f"target layers: {names}")
    except Exception as e:
        names = []
        log(f"target layers err: {e}")

    # Import weights for layers that exist (case-insensitive match)
    lower = {n.lower(): n for n in names}
    for want, file in WEIGHTS:
        real = lower.get(want.lower())
        if real:
            import_weight(world, landscape, real, file)
        else:
            # try anyway — some builds accept name even if query empty
            import_weight(world, landscape, want, file)

    try:
        landscape.force_layers_full_update()
    except Exception:
        pass

    fix_trees(sub, random.Random(77))

    les.save_current_level()
    log("FIX_LOOK_OK")
    os.makedirs(os.path.dirname(RESULT), exist_ok=True)
    with open(RESULT, "w", encoding="utf-8") as f:
        f.write("\n".join(OUT))


if __name__ == "__main__":
    main()
