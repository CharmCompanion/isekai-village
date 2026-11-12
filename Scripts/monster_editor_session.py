"""Project-local request runner for monster authoring only."""
import unreal,json,time,traceback
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/IsekaiVillage')
last=None
next_poll=0
running=False
def run_file(name):
    p=(root/'Scripts'/name).resolve()
    assert p.parent==(root/'Scripts').resolve()
    exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),{'__name__':'__main__','__file__':str(p)})
try:run_file('export_monster_player_sources.py')
except:unreal.log_error(traceback.format_exc())
def tick(delta):
    global last,next_poll,running
    if running:return
    if time.monotonic()<next_poll:return
    next_poll=time.monotonic()+1
    p=root/'Saved/monster_request.json'
    if not p.exists():return
    job=json.loads(p.read_text())
    if job['id']==last:return
    last=job['id']
    running=True
    try:run_file(job['script'])
    except:unreal.log_error(traceback.format_exc())
    finally:running=False
handle=unreal.register_slate_post_tick_callback(tick)
(root/'Saved/monster_session_ready.json').write_text(json.dumps({'ready':True}))
