"""
Remodel Height_DemoCopy:
- Re-import stronger NE-mountain island heightmap (SEA @ mid → actor Z=0)
- Delete leftover floating rock platforms / satellite islands
- Keep ONE pointed cliff, snapped to NE shore
- Scatter a light SoStylized foliage pass so the island is not barren

CLOSE Unreal Editor first. Needs -AllowCommandletRendering.
"""
import os
import struct
import unreal

MAP = "/Game/SpellCraft/Maps/Height_DemoCopy"
PNG_RG = "F:/DEVELOPMENT/Games/SpellCraft/Content/SpellCraft/Textures/Island_Heightmap_1009_RG.png"
R16 = "F:/DEVELOPMENT/Games/SpellCraft/Content/SpellCraft/Textures/Island_Heightmap_1009.r16"
SIZE = 1009
SEA = 32768
RESULT = "F:/DEVELOPMENT/Games/SpellCraft/Saved/Logs/remodel_island_v4.txt"
OUT = []

CLIFF_NAME_HINTS = (
    "cliff", "rock", "island", "platform", "pillar", "mesa", "shelf", "stack", "arch", "spire"
)
KEEP_NAME_HINTS = ("tent", "house", "building", "camp", "player", "water", "sky", "light", "post")


def log(msg):
    OUT.append(str(msg))
    unreal.log(msg)


def landscape_z(landscape):
    o, e = landscape.get_actor_bounds(False, False)
    return o.z - e.z, o.z + e.z


def apply_height(world, landscape):
    rt = unreal.RenderingLibrary.create_render_target2d(
        world, SIZE, SIZE, unreal.TextureRenderTargetFormat.RTF_RGBA8
    )
    tex = unreal.RenderingLibrary.import_file_as_texture2d(world, PNG_RG)
    if not tex:
        log("ERROR: import_file_as_texture2d failed")
        return False
    try:
        tex.set_editor_property("srgb", False)
    except Exception:
        pass
    canvas, _, ctx = unreal.RenderingLibrary.begin_draw_canvas_to_render_target(world, rt)
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
    try:
        landscape.force_layers_full_update()
    except Exception:
        pass
    log(f"height import -> {ok}")
    return ok


def align_sea_level(landscape):
    """Actor Z ≈ world Z of height SEA when ScaleZ=100: world = Z + (H-SEA)*ScaleZ/128."""
    loc = landscape.get_actor_location()
    scale = landscape.get_actor_scale3d()
    # Prefer Z=0 so mid-height sits at water plane BP_Water Z=0
    landscape.set_actor_location(unreal.Vector(loc.x, loc.y, 0.0), False, False)
    zmin, zmax = landscape_z(landscape)
    log(f"Aligned actor Z=0 (scale={scale}); surface {zmin:.1f}..{zmax:.1f}")


def mesh_name_of(act):
    try:
        smc = act.static_mesh_component
        if smc and smc.static_mesh:
            return smc.static_mesh.get_name().lower()
    except Exception:
        pass
    return act.get_name().lower()


def is_keep_prop(act):
    n = mesh_name_of(act) + " " + act.get_name().lower()
    return any(h in n for h in KEEP_NAME_HINTS)


def is_rock_platform(act):
    n = mesh_name_of(act)
    return any(h in n for h in CLIFF_NAME_HINTS)


def purge_platforms_keep_one_cliff(sub, landscape):
    candidates = []
    deleted = 0
    for act in list(sub.get_all_level_actors()):
        if not isinstance(act, unreal.StaticMeshActor):
            continue
        if is_keep_prop(act):
            continue
        if not is_rock_platform(act):
            # orphan floating demo props that aren't named but sit high / offshore
            loc = act.get_actor_location()
            o, e = act.get_actor_bounds(False, False)
            tall = e.z * 2.0
            # delete thin high props that look like leftover shelves
            if loc.z > 800 and tall > 200:
                sub.destroy_actor(act)
                deleted += 1
            continue

        o, e = act.get_actor_bounds(False, False)
        tall = e.z * 2.0
        width = max(e.x, e.y) * 2.0
        aspect = tall / max(1.0, width)
        loc = act.get_actor_location()
        candidates.append((aspect, tall, loc, act))

    candidates.sort(key=lambda t: (t[0], t[1]), reverse=True)
    keep = candidates[0][3] if candidates else None
    for _, _, _, act in candidates:
        if act is keep:
            continue
        sub.destroy_actor(act)
        deleted += 1

    if keep:
        # NE tip of island — roughly +X +Y in landscape space
        lo, le = landscape.get_actor_bounds(False, False)
        ne = unreal.Vector(lo.x + le.x * 0.55, lo.y + le.y * 0.55, lo.z + le.z * 0.35)
        keep.set_actor_location(ne, False, False)
        # Point the long axis out to sea (NE)
        keep.set_actor_rotation(unreal.Rotator(0, 45, 0), False)
        log(f"Kept pointed cliff {keep.get_name()} at {ne}")
    else:
        log("No cliff candidate found to keep")

    log(f"Deleted {deleted} rock platform / floating SMAs")


def scatter_foliage(sub, landscape):
    """Place a modest ring of trees/rocks from SoStylized if assets exist."""
    tree_paths = [
        "/Game/SoStylized/Environment/Meshes/Trees/SM_Tree_01",
        "/Game/SoStylized/Environment/Meshes/Trees/SM_Tree_02",
        "/Game/SoStylized/Environment/Meshes/SM_SS_Tree_01",
        "/Game/SoStylized/Nature/Meshes/SM_Tree_A",
        "/Game/SoStylized/Nature/Meshes/SM_Pine_01",
    ]
    meshes = []
    for p in tree_paths:
        # try common extensions
        for path in (p, p + "." + p.rsplit("/", 1)[-1]):
            asset = unreal.EditorAssetLibrary.load_asset(path)
            if asset:
                meshes.append(asset)
                break
    # Fallback: search asset registry for a few tree static meshes
    if not meshes:
        try:
            ar = unreal.AssetRegistryHelpers.get_asset_registry()
            assets = ar.get_assets_by_path("/Game/SoStylized", recursive=True)
            for a in assets:
                name = str(a.asset_name).lower()
                if "tree" in name and a.asset_class_path.asset_name == "StaticMesh":
                    obj = unreal.EditorAssetLibrary.load_asset(str(a.package_name) + "." + str(a.asset_name))
                    if obj:
                        meshes.append(obj)
                    if len(meshes) >= 4:
                        break
        except Exception as e:
            log(f"foliage search err: {e}")

    if not meshes:
        log("No tree meshes found — skip foliage scatter (map still needs manual foliage paint)")
        return

    lo, le = landscape.get_actor_bounds(False, False)
    placed = 0
    # Interior / mid ring — avoid SW beach and deep NE peak center
    spots = [
        (-0.25, -0.10), (-0.15, 0.15), (0.05, -0.20), (0.20, 0.05),
        (-0.35, 0.05), (0.10, 0.25), (-0.05, 0.30), (0.30, -0.05),
        (-0.20, 0.35), (0.15, -0.30), (0.0, 0.0), (-0.40, -0.15),
        (0.25, 0.20), (-0.10, -0.25), (0.35, 0.10), (-0.30, 0.25),
    ]
    for i, (nx, ny) in enumerate(spots):
        x = lo.x + nx * le.x
        y = lo.y + ny * le.y
        z = lo.z + le.z * 0.15  # approximate surface; artist can snap later
        act = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z))
        if not act:
            continue
        smc = act.static_mesh_component
        smc.set_static_mesh(meshes[i % len(meshes)])
        scale = 0.8 + (i % 5) * 0.15
        act.set_actor_scale3d(unreal.Vector(scale, scale, scale))
        act.set_actor_rotation(unreal.Rotator(0, i * 37.0, 0), False)
        # Tag so we don't purge them as cliffs
        act.set_actor_label(f"IslandTree_{i}")
        placed += 1
    log(f"Scattered {placed} trees from {len(meshes)} mesh type(s)")


def fix_water(sub):
    waters = [a for a in sub.get_all_level_actors() if "Water" in a.get_class().get_name()]
    waters.sort(key=lambda a: a.get_actor_location().z)
    for i, w in enumerate(waters):
        if i == 0:
            w.set_actor_location(unreal.Vector(0, 0, 0), False, False)
            log(f"Ocean kept {w.get_name()} Z=0")
        else:
            sub.destroy_actor(w)
            log(f"Removed extra water {w.get_name()}")


def main():
    if not os.path.isfile(PNG_RG):
        log(f"ERROR missing {PNG_RG} — run create_island_heightmap_v2.py")
        return

    with open(R16, "rb") as f:
        data = f.read()
    n = SIZE * SIZE
    heights = struct.unpack(f"<{n}H", data)
    log(f"r16 min={min(heights)} max={max(heights)} avg={sum(heights)/n:.0f}")

    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    landscape = next(a for a in sub.get_all_level_actors() if isinstance(a, unreal.Landscape))

    z0, z1 = landscape_z(landscape)
    log(f"BEFORE surface {z0:.1f}..{z1:.1f}")

    apply_height(world, landscape)
    align_sea_level(landscape)
    purge_platforms_keep_one_cliff(sub, landscape)
    scatter_foliage(sub, landscape)
    fix_water(sub)

    for act in sub.get_all_level_actors():
        if isinstance(act, unreal.PlayerStart):
            act.set_actor_location(unreal.Vector(-18000, -20000, 800), False, False)
            break

    z0, z1 = landscape_z(landscape)
    log(f"FINAL surface {z0:.1f}..{z1:.1f}")
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    try:
        unreal.EditorAssetLibrary.save_directory("/Game/SpellCraft/Maps", True, True)
    except Exception as e:
        log(f"save_directory: {e}")
    log("DONE — reopen Height_DemoCopy (editor must have been closed).")
    with open(RESULT, "w", encoding="utf-8") as f:
        f.write("\n".join(OUT))


if __name__ == "__main__":
    main()
