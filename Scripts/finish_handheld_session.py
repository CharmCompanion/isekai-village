import unreal as u,json,traceback
from pathlib import Path
u.EditorPythonScripting.set_keep_python_script_alive(True)
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
try:
 for filename,result in [('import_handheld_equipment.py','golem_handheld_import.json'),('import_handheld_idle.py','golem_handheld_idle_import.json'),('import_equipment_pose_check.py','golem_fit_pose_import.json'),('setup_corrected_equipment.py','golem_corrected_setup.json'),('verify_corrected_equipment.py','golem_corrected_verify.json')]:
  p=root/'Scripts'/filename;exec(compile(p.read_text(),str(p),'exec'),{'__name__':'__main__'})
  report=json.loads((root/'Saved'/result).read_text());assert report['success'],report.get('error',report)
 (root/'Saved/golem_handheld_session_error.txt').write_text('')
except Exception:(root/'Saved/golem_handheld_session_error.txt').write_text(traceback.format_exc())
finally:
 p=root/'Scripts/review_corrected_equipment.py';exec(compile(p.read_text(),str(p),'exec'),{'__name__':'__main__'})
