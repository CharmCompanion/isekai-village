"""Scoped request runner for the dedicated El Ruhn map; no legacy job replay."""
import unreal,json,time,traceback
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');S={'last':None,'next':time.monotonic()+2};H={}
p=B/'Saved/elruhn_sky_response.json'
if p.exists():
 try:S['last']=json.loads(p.read_text()).get('id')
 except Exception:pass
def tick(dt):
 if time.monotonic()<S['next']:return
 S['next']=time.monotonic()+1;p=B/'Saved/elruhn_sky_request.json'
 if not p.exists():return
 q=json.loads(p.read_text(encoding='utf-8-sig'))
 if q['id']==S['last']:return
 S['last']=q['id'];script=(B/'Scripts'/q['script']).resolve()
 assert script.parent==(B/'Scripts').resolve() and script.name.startswith(('apply_elruhn_sky','audit_elruhn_sky','render_elruhn_sky','verify_elruhn_sky'))
 try:
  exec(compile(script.read_text(encoding='utf-8'),str(script),'exec'),{'__name__':'__main__','__file__':str(script)});r={'id':q['id'],'status':'script_returned'}
 except Exception:r={'id':q['id'],'status':'error','error':traceback.format_exc()};unreal.log_error(r['error'])
 (B/'Saved/elruhn_sky_response.json').write_text(json.dumps(r,indent=2))
H['h']=unreal.register_slate_post_tick_callback(tick)
