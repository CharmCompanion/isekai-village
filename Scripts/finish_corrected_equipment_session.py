import unreal as u,json,traceback
from pathlib import Path
u.EditorPythonScripting.set_keep_python_script_alive(True)
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
try:
 for filename,result in [('setup_corrected_equipment.py','golem_corrected_setup.json'),('verify_corrected_equipment.py','golem_corrected_verify.json')]:
  script=root/'Scripts'/filename;exec(compile(script.read_text(),str(script),'exec'),{'__name__':'__main__'})
  report=json.loads((root/'Saved'/result).read_text());assert report['success'],report.get('error',report)
 (root/'Saved/golem_corrected_session_error.txt').write_text('')
except Exception:(root/'Saved/golem_corrected_session_error.txt').write_text(traceback.format_exc())
finally:
 script=root/'Scripts/review_corrected_equipment.py';exec(compile(script.read_text(),str(script),'exec'),{'__name__':'__main__'})
