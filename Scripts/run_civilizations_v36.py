import unreal, time, traceback, runpy
state = {'ready_at': None}
h = {}
MAP = '/Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.'

def tick(dt):
    try:
        w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
        E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    except Exception:
        return
    if not w or not w.get_path_name().startswith(MAP):
        return
    if not any(isinstance(a, unreal.Landscape) for a in E.get_all_level_actors()):
        return
    if state['ready_at'] is None:
        state['ready_at'] = time.monotonic()
        unreal.log('V36_MAP_READY waiting 25s')
        return
    if time.monotonic() < state['ready_at'] + 25:
        return
    unreal.unregister_slate_post_tick_callback(h['h'])
    try:
        runpy.run_path('D:/DEVELOPMENT/Games/IsekaiVillage/Scripts/apply_civilizations_v36.py', run_name='__main__')
        unreal.log('V36_RUN_OK')
    except Exception:
        unreal.log_error('V36_RUN_FAILED\n' + traceback.format_exc())
    unreal.SystemLibrary.execute_console_command(None, 'QUIT_EDITOR')

h['h'] = unreal.register_slate_post_tick_callback(tick)
unreal.log('V36_RUNNER_ARMED')
