import unreal as u,json,time,traceback
from pathlib import Path
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
try:
 manifest=r/'ArtSource/Golems/NativeWeapons/manifest.json'
 if not manifest.exists() or not json.loads(manifest.read_text()).get('success'):
  p=r/'Scripts/prepare_native_weapon_clips.py';exec(compile(p.read_text(),str(p),'exec'),{'__name__':'__main__'})
except Exception:(r/'Saved/native_weapon_prepare_error.txt').write_text(traceback.format_exc())
last=None;deadline=time.monotonic()+1500
while time.monotonic()<deadline:
 p=r/'Saved/native_weapon_job.json'
 if p.exists():
  job=json.loads(p.read_text())
  if job.get('id')!=last:
   last=job.get('id')
   if job.get('stop'):break
   try:
    script=Path(job['script']);exec(compile(script.read_text(),str(script),'exec'),{'__name__':'__main__'});value={'id':last,'success':True}
   except Exception:value={'id':last,'success':False,'error':traceback.format_exc()}
   (r/'Saved/native_weapon_job_result.json').write_text(json.dumps(value,indent=2))
 time.sleep(1)
