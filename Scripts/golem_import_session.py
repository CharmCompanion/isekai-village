import unreal,time,json,traceback
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
request=root/'Saved/golem_editor_job.json'
response=root/'Saved/golem_editor_job_result.json'
last=None;deadline=time.monotonic()+1800
while time.monotonic()<deadline:
 if request.exists():
  job=json.loads(request.read_text())
  if job['id']!=last:
   last=job['id']
   if job.get('stop'):break
   try:
    script=root/'Scripts'/job['script']
    exec(compile(script.read_text(),str(script),'exec'),{'__name__':'__main__'})
    response.write_text(json.dumps({'id':last,'executed':True}))
   except Exception:response.write_text(json.dumps({'id':last,'error':traceback.format_exc()}))
 time.sleep(.5)
