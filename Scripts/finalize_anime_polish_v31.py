"""v31 step 5 - tunnel readability, Veil Falls pool re-seat, and the documented render set.

Tunnel interiors (M_IV_CaveStone) had 9% emissive and no lights, so the dungeon/mine/trade-pass approaches read as
pitch-black holes in the mountainside; raise the stone's self-illumination so they read as dim rock. The Veil Falls
spring pool is lowered by the same amount its bank stones were dropped in step 4 so the arrangement is preserved.
Then renders the full review set to Docs/WorldDesign/AnimePolish31_*.png.
"""
import unreal, json, os
from pathlib import Path

B = Path('D:/DEVELOPMENT/Games/IsekaiVillage')
R = '/Game/IsekaiVillage/AdventureWorld'
MAP = R + '/Maps/Map_AnimeAdventure'
A = unreal.EditorAssetLibrary
M = unreal.MaterialEditingLibrary
E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert w.get_path_name().startswith(MAP + '.'), w.get_path_name()
report = {}

cave = unreal.load_asset(R + '/Materials/M_IV_CaveStone')
for n in M.get_material_expressions(cave):
    if isinstance(n, unreal.MaterialExpressionCustom) and n.get_editor_property('code').strip() == 'return C*.09;':
        n.set_editor_property('code', 'return C*.30;'); report['cave_emissive'] = '.09 -> .30'
M.recompile_material(cave); A.save_loaded_asset(cave)

ground = json.loads((B / 'Saved/anime_ground_v31.json').read_text())
bank = [d['gap_m'] for d in ground['props_dropped'] if d['actor'] == 'Spring bank stone']
if bank:
    drop = sum(bank) / len(bank)
    for a in E.get_all_level_actors():
        if a.get_actor_label() == 'Veil Falls - Spring Pool':
            loc = a.get_actor_location(); a.set_actor_location(unreal.Vector(loc.x, loc.y, loc.z - drop * 100.0), False, False)
            report['veil_falls_pool_dropped_m'] = round(drop, 2)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
report['saved'] = True
(B / 'Saved/anime_finalize_v31.json').write_text(json.dumps(report, indent=1))
unreal.log('FINAL_V31 ' + json.dumps(report))

if os.environ.get('IV_RENDER_AFTER') == '1':
    import importlib.util
    spec = importlib.util.spec_from_file_location('render_anime_polish_v31', str(B / 'Scripts/render_anime_polish_v31.py'))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    views = list(mod.VIEWS) + [
        ('EdgeSouth', (-100, -500), None, (120, -560, None)),
        ('VeilFalls', (-330, 240), None, (-349, 263, None)),
        ('DungeonSpring', (205, 425), None, (219, 438, None)),
        ('TunnelInside', (238, 452), None, (241, 475, None)),
        ('TradePassMouth', (-310, -100), None, (-355, -85, None)),
    ]
    mod.start_render(prefix='AnimePolish31_', out_dir=Path(os.environ.get('IV_RENDER_DIR', str(B / 'Docs/WorldDesign'))), views=views, warmup=90.0, quit_when_done=True)
