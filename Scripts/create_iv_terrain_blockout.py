"""Create a separate terrain-only Unreal map. Existing maps are never changed.

Run with UnrealEditor-Cmd and -AllowCommandletRendering. The generated map is
/Game/IsekaiVillage/WorldBlockout/Maps/Map_IV_TerrainBlockout_v01.
"""
import unreal

MAP = '/Game/IsekaiVillage/WorldBlockout/Maps/Map_IV_TerrainBlockout_v01'
HEIGHT_PNG = r'D:\DEVELOPMENT\Games\IsekaiVillage\Content\IsekaiVillage\WorldBlockout\TerrainSource\IV_Terrain_Blockout_1009_RG.png'
SIZE = 1009

def log(message):
    unreal.log(message)
    print(message)

level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if unreal.EditorAssetLibrary.does_asset_exist(MAP):
    # The only existing version is the empty map produced by the failed commandlet attempt.
    # Refuse to touch a map that already contains actors.
    level.load_level(MAP)
    existing = actors.get_all_level_actors()
    if existing:
        raise RuntimeError('Refusing to modify non-empty map: ' + MAP)
else:
    level.new_level(MAP)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()

# Terrain only: one Landscape plus daylight so its landform can be reviewed.
landscape = actors.spawn_actor_from_class(
    unreal.Landscape, unreal.Vector(-60000, -60000, 0), unreal.Rotator(0, 0, 0)
)
if not landscape:
    raise RuntimeError('Landscape actor could not be spawned')
landscape.set_actor_scale3d(unreal.Vector(119.047619, 119.047619, 100.0))

texture = unreal.RenderingLibrary.import_file_as_texture2d(world, HEIGHT_PNG)
if not texture:
    raise RuntimeError('Could not read terrain source: ' + HEIGHT_PNG)
texture.set_editor_property('srgb', False)
target = unreal.RenderingLibrary.create_render_target2d(
    world, SIZE, SIZE, unreal.TextureRenderTargetFormat.RTF_RGBA8
)
canvas, _, context = unreal.RenderingLibrary.begin_draw_canvas_to_render_target(world, target)
canvas.draw_texture(
    texture, unreal.Vector2D(0, 0), unreal.Vector2D(SIZE, SIZE),
    unreal.Vector2D(0, 0), unreal.Vector2D(1, 1),
    unreal.LinearColor(1, 1, 1, 1), unreal.BlendMode.BLEND_OPAQUE,
)
unreal.RenderingLibrary.end_draw_canvas_to_render_target(world, context)

ok = landscape.landscape_import_heightmap_from_render_target(target, True, 0)
if not ok:
    raise RuntimeError('Landscape heightmap import failed; map was not saved')

# One sun and atmosphere are part of the terrain review, not environment dressing.
sun = actors.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 30000), unreal.Rotator(-42, -35, 0))
sun_component = sun.get_component_by_class(unreal.DirectionalLightComponent)
sun_component.set_editor_property('intensity', 6.0)
sun_component.set_editor_property('atmosphere_sun_light', True)
actors.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
sky = actors.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 12000), unreal.Rotator(0, 0, 0))
sky.get_component_by_class(unreal.SkyLightComponent).set_editor_property('real_time_capture', True)

mat = unreal.EditorAssetLibrary.load_asset('/Game/SoStylized/Environment/Landscape/Materials/MI_Landscape.MI_Landscape')
if mat:
    landscape.set_editor_property('landscape_material', mat)

unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
log('SUCCESS: created ' + MAP)
log('Landscape scale: 119.047619, 119.047619, 100.0')
log('Terrain source: ' + HEIGHT_PNG)
