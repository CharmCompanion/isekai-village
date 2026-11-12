"""Small local authoring session, limited to scripts in this project's Scripts directory."""
import unreal,json,time,traceback
from pathlib import Path
root=Path(__file__).resolve().parents[1];last=None;next_poll=0;running=False
def tick(delta):
 global last,next_poll,running
 if running or time.monotonic()<next_poll:return
 next_poll=time.monotonic()+1
 p=root/'Saved/slime_magic_request.json'
 if not p.exists():return
 job=json.loads(p.read_text())
 if job['id']==last:return
 last=job['id'];running=True
 report={'id':last,'script':job['script'],'status':'running'}
 try:
  script=(root/'Scripts'/job['script']).resolve();assert script.parent==(root/'Scripts').resolve()
  exec(compile(script.read_text(encoding='utf-8'),str(script),'exec'),{'__name__':'__main__','__file__':str(script)})
  report['status']='complete'
 except Exception:
  report['status']='failed';report['error']=traceback.format_exc();unreal.log_error(report['error'])
 finally:
  (root/'Saved/slime_magic_job.json').write_text(json.dumps(report,indent=2));running=False
handle=unreal.register_slate_post_tick_callback(tick)
(root/'Saved/slime_magic_session.json').write_text(json.dumps({'ready':True,'time':time.time()}))
