"""
Force-remodel Height_DemoCopy (v5).

CLOSE Unreal Editor before running — if editor stays open it reloads stale data
and saving in-editor overwrites these fixes.

Needs: -AllowCommandletRendering
"""
import os
import struct
import unreal

MAP = "/Game/SpellCraft/Maps/Height_DemoCopy"
DEMO = "/Game/SoStylized/Maps/CompleteVol1/Demonstration"
PNG_RG = "F:/DEVELOPMENT/Games/SpellCraft/Content/SpellCraft/Textures/Island_Heightmap_1009_RG.png"
R16 = "F:/DEVELOPMENT/Games/SpellCraft/Content/SpellCraft/Textures/Island_Heightmap_1009.r16"
SIZE = 1009
SEA = 32768
RESULT = "F:/DEVELOPMENT/Games/SpellCraft/Saved/Logs/remodel_island_v5.txt"
OUT = []

# Mesh name substrings → delete (demo cliff shelves / water rocks)
DELETE_MESH_HINTS = (
    "cliff", "shelf", "platform", "stack", "pillar", "mesa", "spire", "arch",
    "island", "rock_", "_rock", "stonecliff", "bluff", "outcrop", "boulder",
    "sm_ss_", "sm_cliff", "sm_rock", "sm_island", "sm_platform",
)
KEEP_HINTS = (
    "tent", "house", "hut", "camp", "barrel", "crate", "flag", "bridge",
    "sign", "lantern", "islandtree_", "player", "boat", "dock",
)


def log(msg):
    OUT.append(str(msg))
    unreal.log(msg)


def landscape_z(landscape):
    o, e = landscape.get_actor_bounds(False, False)
    return o.z - e.z, o.z + e.z


def export_heights(world, landscape):
    rt = unreal.RenderingLibrary.create_render_target2d(
        world, SIZE, SIZE, unreal.TextureRenderTargetFormat.RTF_RGBA8
    )
    for args in [(rt, True, False), (rt, True, True), (rt, True)]:
        try:
            if landscape.landscape_export_heightmap_to_render_target(*args):
                break
        except TypeError:
            continue
    else:
        return None
    pixels = unreal.RenderingLibrary.read_render_target_raw_pixel_area(
        world, rt, 0, 0, SIZE, SIZE, True
    )
    if not pixels:
        return None
    hs = []
    for c in pixels:
        r = int(round(min(max(c.r, 0.0), 1.0) * 255.0))
        g = int(round(min(max(c.g, 0.0), 1.0) * 255.0))
        if c.r > 1.5:
            r = int(round(c.r))
            g = int(round(c.g))
        hs.append((r << 8) | g)
    return hs


def quadrant_stats(heights):
    mid = SIZE // 2
    sw, ne = [], []
    for j in range(SIZE):
        for i in range(SIZE):
            h = heights[j * SIZE + i]
            if i < mid and j < mid:
                sw.append(h)
            elif i >= mid and j >= mid:
                ne.append(h)
    return min(sw), max(sw), min(ne), max(ne)


def apply_height(world, landscape):
    tex = unreal.RenderingLibrary.import_file_as_texture2d(world, PNG_RG)
    if not tex:
        log("ERROR height texture import failed")
        return False
    try:
        tex.set_editor_property("srgb", False)
    except Exception:
        pass
    rt = unreal.RenderingLibrary.create_render_target2d(
        world, SIZE, SIZE, unreal.TextureRenderTargetFormat.RTF_RGBA8
    )
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


def mesh_key(act):
    parts = [act.get_name().lower(), act.get_actor_label().lower()]
    try:
        sm = act.static_mesh_component.static_mesh
        if sm:
            parts.append(sm.get_name().lower())
            parts.append(sm.get_path_name().lower())
    except Exception:
        pass
    return " ".join(parts)


def should_delete_sma(act, landscape_center, landscape_extent):
    key = mesh_key(act)
    if any(k in key for k in KEEP_HINTS):
        return False
    if any(k in key for k in DELETE_MESH_HINTS):
        return True
    loc = act.get_actor_location()
    # Offshore / floating: far from landscape center in XY
    dx = abs(loc.x - landscape_center.x)
    dy = abs(loc.y - landscape_center.y)
    if dx > landscape_extent.x * 0.92 or dy > landscape_extent.y * 0.92:
        return True
    # Stepping-stone chains in water (low Z, not camp)
    if loc.z < 1200 and (dx > landscape_extent.x * 0.35 or dy > landscape_extent.y * 0.35):
        o, e = act.get_actor_bounds(False, False)
        if e.z < 800:  # flat shelf mesh
            return True
    return False


def purge_props(sub, landscape):
    lo, le = landscape.get_actor_bounds(False, False)
    deleted = 0
    keep_act = None
    best_score = -1.0
    all_smas = [a for a in sub.get_all_level_actors() if isinstance(a, unreal.StaticMeshActor)]
    for act in all_smas:
        key = mesh_key(act)
        if "islandtree_" in key:
            continue
        if any(h in key for h in ("cliff", "rock", "spire", "pillar")):
            o, e = act.get_actor_bounds(False, False)
            score = e.z * 2.0
            if score > best_score:
                best_score = score
                keep_act = act
    for act in all_smas:
        key = mesh_key(act)
        if "islandtree_" in key or act is keep_act:
            continue
        if should_delete_sma(act, lo, le):
            sub.destroy_actor(act)
            deleted += 1
    log(f"Deleted {deleted} static meshes (platforms / offshore rocks)")
    return keep_act


HEIGHT_CACHE = None


def load_height_cache():
    global HEIGHT_CACHE
    if HEIGHT_CACHE is not None:
        return HEIGHT_CACHE
    with open(R16, "rb") as f:
        HEIGHT_CACHE = struct.unpack(f"<{SIZE * SIZE}H", f.read())
    return HEIGHT_CACHE


def world_to_height_uv(x, y, lo, le):
    """Map world XY to heightmap texel (0..SIZE-1)."""
    u = (x - (lo.x - le.x)) / max(1.0, 2.0 * le.x)
    v = (y - (lo.y - le.y)) / max(1.0, 2.0 * le.y)
    ix = int(max(0, min(SIZE - 1, u * (SIZE - 1))))
    iy = int(max(0, min(SIZE - 1, v * (SIZE - 1))))
    return ix, iy


def height_at_world(x, y, lo, le, actor_z=0.0, scale_z=100.0):
    hs = load_height_cache()
    ix, iy = world_to_height_uv(x, y, lo, le)
    h = hs[iy * SIZE + ix]
    return actor_z + (h - SEA) * scale_z / 128.0


def line_landscape_z(world, x, y, lo, le, fallback=800.0):
    try:
        return height_at_world(x, y, lo, le) + 30.0
    except Exception:
        return fallback


def place_kept_cliff(sub, landscape, kept_cliff, world):
    lo, le = landscape.get_actor_bounds(False, False)
    # NE shore
    x = lo.x + le.x * 0.62
    y = lo.y + le.y * 0.62
    z = line_landscape_z(world, x, y, lo, le, lo.z + le.z * 0.4)
    if kept_cliff:
        kept_cliff.set_actor_location(unreal.Vector(x, y, z), False, False)
        kept_cliff.set_actor_rotation(unreal.Rotator(-8, 35, 0), False)
        kept_cliff.set_actor_label("IslandPointedCliff_NE")
        log(f"Repositioned kept cliff at ({x:.0f},{y:.0f},{z:.0f})")
        return
    # spawn one from registry if purge removed everything
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    cliff_mesh = None
    for a in ar.get_assets_by_path("/Game/SoStylized", recursive=True):
        n = str(a.asset_name).lower()
        if "cliff" in n and a.asset_class_path.asset_name == "StaticMesh":
            cliff_mesh = unreal.EditorAssetLibrary.load_asset(f"{a.package_name}.{a.asset_name}")
            if cliff_mesh:
                break
    if cliff_mesh:
        act = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z))
        act.static_mesh_component.set_static_mesh(cliff_mesh)
        act.set_actor_label("IslandPointedCliff_NE")
        act.set_actor_rotation(unreal.Rotator(-8, 35, 0), False)
        log(f"Spawned NE cliff mesh {cliff_mesh.get_name()}")


def copy_demo_foliage_settings(landscape):
    """Copy grass types from Demonstration landscape if present."""
    try:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(DEMO)
        demo_land = next(
            a
            for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
            if isinstance(a, unreal.Landscape)
        )
        grass = demo_land.get_editor_property("landscape_grass_types")
        mat = demo_land.get_editor_property("landscape_material")
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
        if grass:
            landscape.set_editor_property("landscape_grass_types", grass)
            log(f"Copied {len(grass)} grass types from Demonstration")
        if mat:
            landscape.set_editor_property("landscape_material", mat)
            log("Copied landscape material from Demonstration")
    except Exception as e:
        log(f"foliage settings copy err: {e} — reload map")
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)


def scatter_trees(sub, landscape, world):
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    meshes = []
    for a in ar.get_assets_by_path("/Game/SoStylized", recursive=True):
        n = str(a.asset_name).lower()
        if a.asset_class_path.asset_name != "StaticMesh":
            continue
        if any(t in n for t in ("tree", "pine", "bush", "shrub")) and "billboard" not in n:
            m = unreal.EditorAssetLibrary.load_asset(f"{a.package_name}.{a.asset_name}")
            if m:
                meshes.append(m)
        if len(meshes) >= 8:
            break
    if not meshes:
        log("No tree meshes found")
        return
    lo, le = landscape.get_actor_bounds(False, False)
    placed = 0
    # grid across interior — skip deep NE peak and SW beach
    for row in range(7):
        for col in range(8):
            nx = -0.55 + col * 0.16
            ny = -0.55 + row * 0.16
            if nx > 0.35 and ny > 0.35:  # leave NE peak clearer
                continue
            if nx < -0.25 and ny < -0.25:  # SW beach open
                continue
            x = lo.x + nx * le.x
            y = lo.y + ny * le.y
            z = line_landscape_z(world, x, y, lo, le, lo.z)
            if z < 200:
                continue
            act = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z))
            smc = act.static_mesh_component
            smc.set_static_mesh(meshes[(row + col) % len(meshes)])
            s = 0.7 + (row % 4) * 0.12
            act.set_actor_scale3d(unreal.Vector(s, s, s))
            act.set_actor_rotation(unreal.Rotator(0, (row * 53 + col * 29) % 360, 0), False)
            act.set_actor_label(f"IslandTree_{row}_{col}")
            placed += 1
    log(f"Scattered {placed} trees/bushes")


def fix_water(sub):
    waters = [a for a in sub.get_all_level_actors() if "Water" in a.get_class().get_name()]
    waters.sort(key=lambda a: a.get_actor_location().z)
    for i, w in enumerate(waters):
        if i == 0:
            w.set_actor_location(unreal.Vector(0, 0, 0), False, False)
            log(f"Ocean {w.get_name()} at Z=0")
        else:
            sub.destroy_actor(w)


def main():
    if not os.path.isfile(PNG_RG):
        log("ERROR missing heightmap PNG")
        return

    with open(R16, "rb") as f:
        hs = struct.unpack(f"<{SIZE * SIZE}H", f.read())
    log(f"file r16 min={min(hs)} max={max(hs)}")

    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    landscape = next(a for a in sub.get_all_level_actors() if isinstance(a, unreal.Landscape))

    z0, z1 = landscape_z(landscape)
    log(f"BEFORE Z {z0:.0f}..{z1:.0f} actorZ={landscape.get_actor_location().z}")

    apply_height(world, landscape)
    landscape.set_actor_location(unreal.Vector(0, 0, 0), False, False)

    exported = export_heights(world, landscape)
    if exported:
        sw_min, sw_max, ne_min, ne_max = quadrant_stats(exported)
        log(f"EXPORT SW {sw_min}..{sw_max}  NE {ne_min}..{ne_max}  delta={ne_max - sw_max}")
        if ne_max - sw_max < 3000:
            log("WARNING: landscape heights may not have applied — NE should be much higher than SW")

    copy_demo_foliage_settings(landscape)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    landscape = next(a for a in sub.get_all_level_actors() if isinstance(a, unreal.Landscape))

    kept = purge_props(sub, landscape)
    place_kept_cliff(sub, landscape, kept, world)
    scatter_trees(sub, landscape, world)
    fix_water(sub)

    for act in sub.get_all_level_actors():
        if isinstance(act, unreal.PlayerStart):
            act.set_actor_location(unreal.Vector(-18000, -20000, 900), False, False)
            act.set_actor_rotation(unreal.Rotator(0, 45, 0), False)

    z0, z1 = landscape_z(landscape)
    sma = sum(1 for a in sub.get_all_level_actors() if isinstance(a, unreal.StaticMeshActor))
    log(f"FINAL Z {z0:.0f}..{z1:.0f}  StaticMeshActors={sma}")

    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    log("SAVED — reopen editor and load Height_DemoCopy (do not save over without checking).")
    with open(RESULT, "w", encoding="utf-8") as f:
        f.write("\n".join(OUT))


if __name__ == "__main__":
    main()
