"""Explicit request runner for regional world repair. Does not replay legacy jobs."""
import unreal, time, json, traceback
from pathlib import Path
ROOT = Path('D:/DEVELOPMENT/Games/IsekaiVillage')
unreal.load_object(None,'/Script/UnrealEd.Default__EditorPerformanceSettings').set_editor_property('bThrottleCPUWhenNotForeground', False)
unreal.SystemLibrary.execute_console_command(None, 't.IdleWhenNotForeground 0')
STATE = {'last': None, 'next': time.monotonic() + 35, 'busy':False}
H = {}
previous = ROOT / 'Saved/world_rebuild_response.json'
if previous.exists():
    try:
        finished = json.loads(previous.read_text(encoding='utf-8-sig'))
        if finished.get('status') == 'script_returned': STATE['last'] = finished.get('id')
    except (ValueError, OSError): pass
def tick(dt):
    if STATE['busy'] or time.monotonic() < STATE['next']: return
    STATE['next'] = time.monotonic() + 1
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    if not w or not w.get_path_name().startswith('/Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.'): return
    p = ROOT / 'Saved/world_rebuild_request.json'
    if not p.exists(): return
    job = json.loads(p.read_text(encoding='utf-8-sig'))
    if job['id'] == STATE['last']: return
    STATE['last'] = job['id']
    if job.get('stop'):
        unreal.unregister_slate_post_tick_callback(H['h']); return
    script = (ROOT / 'Scripts' / job['script']).resolve()
    assert script.parent == (ROOT / 'Scripts').resolve() and script.name.startswith(('audit_gosain_', 'render_gosain_', 'apply_gosain_', 'verify_gosain_'))
    STATE['busy']=True
    try:
        exec(compile(script.read_text(encoding='utf-8'), str(script), 'exec'), {'__name__':'__main__', '__file__':str(script)})
        result = {'id': job['id'], 'script':script.name, 'status':'script_returned'}
    except Exception:
        result = {'id':job['id'], 'status':'error', 'error':traceback.format_exc()}
        unreal.log_error(result['error'])
    finally:
        STATE['busy']=False
    (ROOT/'Saved/world_rebuild_response.json').write_text(json.dumps(result, indent=2))
H['h'] = unreal.register_slate_post_tick_callback(tick)
unreal.log('REGIONAL_WORLD_REBUILD_SESSION_READY')
