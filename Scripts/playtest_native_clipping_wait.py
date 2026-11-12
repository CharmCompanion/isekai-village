import unreal as u,json,time,traceback
from pathlib import Path
u.EditorPythonScripting.set_keep_python_script_alive(True)
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');started=time.monotonic()
def poll(delta):
 try:
  path=r/'ArtSource/Golems/NativeClipping/geometry_audit_final.json'
  if path.exists():
   try:report=json.loads(path.read_text())
   except json.JSONDecodeError:return
   if report.get('success'):
    u.unregister_slate_post_tick_callback(handle);(r/'ArtSource/Golems/NativeClipping/geometry_audit.json').write_text(json.dumps(report,indent=2));script=r/'Scripts/playtest_native_clipping_fixes.py';exec(compile(script.read_text(),str(script),'exec'),{'__name__':'__main__'});return
  if time.monotonic()-started>480:raise RuntimeError('Geometry audit did not finish before the live-check deadline')
 except Exception:
  u.unregister_slate_post_tick_callback(handle);(r/'Saved/native_clipping_live_start_error.txt').write_text(traceback.format_exc());u.EditorPythonScripting.set_keep_python_script_alive(False)
handle=u.register_slate_post_tick_callback(poll)
