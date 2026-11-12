from pathlib import Path
import json,traceback,unreal as u
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
try:
 for name in ['apply_native_clearance_poses.py','export_native_clipping_poses.py']:
  p=r/'Scripts'/name;exec(compile(p.read_text(),str(p),'exec'),{'__name__':'__main__'})
 (r/'Saved/native_clipping_final_export_ready.json').write_text(json.dumps({'success':True},indent=2))
 p=r/'Scripts/playtest_native_clipping_fixes.py';exec(compile(p.read_text(),str(p),'exec'),{'__name__':'__main__'})
except Exception:(r/'Saved/native_clipping_final_start_error.txt').write_text(traceback.format_exc());raise
