"""v31 step 1 - daylight for the floating island.

The SkyAtmosphere planet top had been moved to mainland sea level (20.6 km below El Ruhn), so the playable island sat in
near-vacuum: black zenith, a sky light capturing darkness, and pitch-black shade. This puts the atmosphere back at island
altitude, softens the sun, and stops the painted cloud meshes from casting hole-like shadow blobs on the ground.
Backs up the map to Saved/WorldBackups/BeforeAnimePolish_v31/ before saving.
"""
import unreal, json, shutil, os
from pathlib import Path

B = Path('D:/DEVELOPMENT/Games/IsekaiVillage')
MAP = '/Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure'
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert w.get_path_name().startswith(MAP + '.'), w.get_path_name()

backup = B / 'Saved/WorldBackups/BeforeAnimePolish_v31'
backup.mkdir(parents=True, exist_ok=True)
src = B / 'Content/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.umap'
if not (backup / 'Map_AnimeAdventure.umap').exists():
    shutil.copy2(src, backup / 'Map_AnimeAdventure.umap')

report = {'cloud_shadow_actors': 0}
for a in E.get_all_level_actors():
    if isinstance(a, unreal.SkyAtmosphere):
        # Planet surface 250 m under the village: the island reads as low-altitude countryside, the mainland 20 km below stays hazy.
        a.set_actor_location(unreal.Vector(0, 0, -25000), False, False)
        c = a.get_component_by_class(unreal.SkyAtmosphereComponent)
        c.set_editor_property('aerial_pespective_view_distance_scale', 0.6)
        report['sky_atmosphere_z_cm'] = -25000
    elif isinstance(a, unreal.DirectionalLight):
        c = a.get_component_by_class(unreal.DirectionalLightComponent)
        c.set_editor_property('light_source_angle', 1.6)
        c.set_editor_property('light_source_soft_angle', 1.0)
        c.set_editor_property('shadow_amount', 0.9)
        report['sun'] = {'source_angle': 1.6, 'shadow_amount': 0.9}
    elif isinstance(a, unreal.SkyLight):
        c = a.get_component_by_class(unreal.SkyLightComponent)
        c.set_editor_property('lower_hemisphere_color', unreal.LinearColor(0.32, 0.36, 0.30, 1.0))
        c.set_editor_property('cubemap_resolution', 256)
        c.recapture_sky()
    elif isinstance(a, unreal.StaticMeshActor):
        smc = a.static_mesh_component
        m = smc.static_mesh
        if not m:
            continue
        mats = [x.get_path_name() if x else '' for x in smc.get_materials()]
        if 'Cloud' in m.get_name() or any('CloudBank' in p or 'PaintedSky' in p for p in mats):
            if smc.get_editor_property('cast_shadow'):
                smc.set_editor_property('cast_shadow', False)
                report['cloud_shadow_actors'] += 1

assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
report['saved'] = True
(B / 'Saved/anime_lighting_v31.json').write_text(json.dumps(report, indent=1))
unreal.log('LIGHTING_V31 ' + json.dumps(report))

if os.environ.get('IV_RENDER_AFTER') == '1':
    import importlib.util
    spec = importlib.util.spec_from_file_location('render_anime_polish_v31', str(B / 'Scripts/render_anime_polish_v31.py'))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    mod.start_render(prefix='AnimePolish31_step1_', out_dir=Path(os.environ.get('IV_RENDER_DIR', str(B / 'Saved/AnimePolish31'))), quit_when_done=True)
