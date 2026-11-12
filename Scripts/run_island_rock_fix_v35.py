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
    has_land = False
    has_found = False
    has_collar = False
    for a in E.get_all_level_actors():
        if isinstance(a, unreal.Landscape):
            has_land = True
        if isinstance(a, unreal.StaticMeshActor) and a.static_mesh_component.static_mesh:
            n = a.static_mesh_component.static_mesh.get_name()
            if n == 'SM_IV_JoinedMountain_v28':
                has_found = True
            if n == 'SM_IV_RimCollar_v31':
                has_collar = True
    if not (has_land and has_found):
        return
    if state['ready_at'] is None:
        state['ready_at'] = time.monotonic()
        unreal.log('V35_ACTORS_READY collar=%s waiting 20s' % has_collar)
        return
    if time.monotonic() < state['ready_at'] + 20:
        return
    unreal.unregister_slate_post_tick_callback(h['h'])
    try:
        runpy.run_path('D:/DEVELOPMENT/Games/IsekaiVillage/Scripts/apply_island_rock_fix_v35.py', run_name='__main__')
        unreal.log('V35_RUN_OK')
    except Exception:
        unreal.log_error('V35_RUN_FAILED\n' + traceback.format_exc())
    unreal.SystemLibrary.execute_console_command(None, 'QUIT_EDITOR')

h['h'] = unreal.register_slate_post_tick_callback(tick)
unreal.log('V35_RUNNER_ARMED')
