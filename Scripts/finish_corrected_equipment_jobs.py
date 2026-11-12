import unreal as u,json,traceback
from pathlib import Path
root=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
try:
 for filename,result in [('setup_corrected_equipment.py','golem_corrected_setup.json'),('import_equipment_pose_check.py','golem_fit_pose_import.json'),('verify_corrected_equipment.py','golem_corrected_verify.json')]:
  p=root/'Scripts'/filename;exec(compile(p.read_text(),str(p),'exec'),{'__name__':'__main__'})
  report=json.loads((root/'Saved'/result).read_text());assert report['success'],report.get('error',report)
 (root/'Saved/golem_corrected_session_error.txt').write_text('')
except Exception:(root/'Saved/golem_corrected_session_error.txt').write_text(traceback.format_exc())
