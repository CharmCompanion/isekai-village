"""Temporary, project-scoped batch runner for this world-building editor session."""
import unreal, json, time, traceback
from pathlib import Path
_iv_root=Path('D:/DEVELOPMENT/Games/IsekaiVillage')
_iv_last=None
_iv_next=0
def _iv_tick(delta):
    global _iv_last,_iv_next
    if time.monotonic()<_iv_next:return
    _iv_next=time.monotonic()+1
    p=_iv_root/'Saved/adventure_request.json'
    if not p.exists():return
    job=json.loads(p.read_text())
    if job['id']==_iv_last:return
    _iv_last=job['id']
    if job.get('stop'):
        unreal.unregister_slate_post_tick_callback(_iv_handle);return
    script=(_iv_root/'Scripts'/job['script']).resolve()
    assert script.parent==(_iv_root/'Scripts').resolve()
    try:exec(compile(script.read_text(encoding='utf-8'),str(script),'exec'),{'__name__':'__main__','__file__':str(script)})
    except:unreal.log_error(traceback.format_exc())
_iv_handle=unreal.register_slate_post_tick_callback(_iv_tick)
unreal.log('Adventure editor session active')
