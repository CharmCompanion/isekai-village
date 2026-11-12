import unreal as u,time,json,gc,traceback
from pathlib import Path
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');attempt=0;last_retry=None
while attempt<5:
 attempt+=1;scope={'__name__':'__main__'}
 try:
  p=r/'Scripts/native_wardrobe_import_impl.py';exec(compile(p.read_text(),str(p),'exec'),scope);break
 except Exception:
  (r/'Saved/native_wardrobe_session_error.txt').write_text(traceback.format_exc())
 finally:
  scope=None;gc.collect()
 deadline=time.monotonic()+600
 while time.monotonic()<deadline:
  p=r/'Saved/native_wardrobe_retry.json'
  if p.exists():
   request=json.loads(p.read_text())
   if request['id']!=last_retry:last_retry=request['id'];break
  time.sleep(1)
 else:raise RuntimeError('Wardrobe session expired while waiting for a correction')
