import json, time, traceback, runpy
import unreal

state = {'ready_at': None, 'done': False}
h = {}
MAP = '/Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.'
HEART = 'D:/DEVELOPMENT/Games/IsekaiVillage/Saved/hub_dungeon_heartbeat_v37.txt'


def tick(dt):
    if state['done']:
        return
    try:
        w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
        E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    except Exception:
        return
    if not w or not w.get_path_name().startswith(MAP):
        return
    if not any(isinstance(a, unreal.Landscape) for a in E.get_all_level_actors()):
        return
    if not hasattr(unreal, 'AdventurerHub') and not unreal.load_class(None, '/Script/IsekaiVillage.AdventurerHub'):
        return
    now = time.monotonic()
    if state['ready_at'] is None:
        state['ready_at'] = now
        open(HEART, 'w').write('ready %s\n' % now)
        unreal.log('V37_MAP_READY waiting 25s')
        return
    elapsed = now - state['ready_at']
    if elapsed < 25.0:
        return
    state['done'] = True
    unreal.unregister_slate_post_tick_callback(h['h'])
    open(HEART, 'a').write('apply %s\n' % elapsed)
    try:
        runpy.run_path('D:/DEVELOPMENT/Games/IsekaiVillage/Scripts/apply_hub_and_dungeon_v37.py', run_name='__main__')
        unreal.log('V37_RUN_OK')
    except Exception:
        unreal.log_error('V37_RUN_FAILED\n' + traceback.format_exc())
        open('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/hub_dungeon_applied_v37.json', 'w', encoding='utf-8').write(
            json.dumps({'stage': 'failed', 'error': traceback.format_exc()}, indent=2)
        )
    unreal.SystemLibrary.execute_console_command(None, 'QUIT_EDITOR')


h['h'] = unreal.register_slate_post_tick_callback(tick)
unreal.log('V37_RUNNER_ARMED')
